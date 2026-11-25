"""Contratos laborales del productor ENEIC, con personas sintéticas."""
from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import procesar_eneic as e


def personas():
    base = dict(ANIO=2025, TRIMESTRE=5, DOMINIO=1, NUM_HOGAR=1,
                P02A02=2, P05C13=1, P05C04_2D=1, P05C04_1D=1, OCUPADOS=1)
    # PESO, EDAD, CONDICIÓN, INGRESO
    valores = [(2, 15, 1, 0), (2, 24, 2, 100), (4, 65, None, None),
               (9, 14, 1, 900), (8, 33, None, None)]
    df = pd.DataFrame([dict(base, NUM_PERSONA=i+1, FACTOR=p, P02A03=a,
                            FORMAL_INFORMAL=c, YLAB_PUBLI=y)
                       for i, (p, a, c, y) in enumerate(valores)])
    df.loc[4, "OCUPADOS"] = None
    return df


@pytest.fixture
def mapa():
    return {1: ("A", "A", 1), 99: ("U", "R-S-T-U", 10)}


@pytest.mark.parametrize("col,x", [("FACTOR", 0), ("FACTOR", float("inf")),
                                   ("FACTOR", -1), ("FACTOR", None),
                                   ("ANIO", 2024), ("TRIMESTRE", 4),
                                   ("OCUPADOS", 7), ("P02A02", 9), ("DOMINIO", 4),
                                   ("FORMAL_INFORMAL", 3), ("P05C13", 12),
                                   ("YLAB_PUBLI", "err"), ("NUM_PERSONA", None)])
def test_dato_invalido(col, x, mapa):
    df = personas().astype(object)
    df.loc[0, col] = x
    with pytest.raises(ValueError, match=col):
        e.preparar(df, mapa)


def test_duplicado_fuera_del_universo(mapa):
    df = personas()
    with pytest.raises(ValueError, match="duplicada"):
        e.preparar(pd.concat([df, df.iloc[[-1]]]), mapa)


def test_ponderacion_cobertura_mediana_y_edad(mapa):
    t = e.resumir(e.preparar(personas(), mapa)).set_index(["dimension", "categoria"])
    n = t.loc[("nacional", "GT")]
    assert (n.n_ocupados, n.peso_ocupados, n.n_clasificados, n.peso_clasificados) == (3, 8, 2, 4)
    assert (n.peso_informal, n.tasa_sector_informal, n.cobertura_condicion_pct) == (2, 50, 50)
    assert (n.n_ingreso, n.peso_ingreso, n.cobertura_ingreso_pct, n.n_ingreso_cero) == (2, 4, 50, 1)
    assert (n.media_ingreso, n.mediana_ingreso) == (50, 0)
    assert t.loc[("edad", "15–24")].n_ocupados == 2
    assert pd.isna(t.loc[("edad", "65+")].media_ingreso)
    assert t.loc[("condicion", "Informal")].media_ingreso == 0


@pytest.mark.parametrize("codigo", [999, 4, None])
def test_rama_residual_conserva_peso(codigo, mapa):
    df = personas()
    df.loc[0, ["P05C04_2D", "P05C04_1D"]] = [codigo, 99]
    t = e.resumir(e.preparar(df, mapa))
    ramas = t[t.dimension == "grupo_ciiu"].set_index("categoria")
    assert ramas.loc["Sin clasificar", "peso_informal"] == 2
    assert ramas.loc["Sin clasificar", "composicion_informal_pct"] == 100
    assert ramas.peso_ocupados.sum() == 8
    assert ramas.composicion_informal_pct.sum() == 100


def test_codigos_dos_digitos_y_conciliacion(mapa):
    df = personas()
    df.loc[0, "P05C04_2D"] = 99
    with pytest.raises(ValueError, match="P05C04_1D"):
        e.preparar(df, mapa)
    df.loc[0, "P05C04_1D"] = 10
    t = e.resumir(e.preparar(df, mapa))
    assert "R-S-T-U" in t.categoria.values


def test_publicacion_solo_celdas_conciliadas(mapa):
    t = e.resumir(e.preparar(personas(), mapa))
    ref = [dict(dimension='nacional', categoria='GT', indicador='tasa_sector_informal',
                valor=50, decimales=1, unidad='porcentaje', referencia='prueba sintética')]
    p = e.publicar(t, ref)
    assert len(p) == 1
    assert p.iloc[0].valor == 50
    assert p.iloc[0].denominador == 4
    assert p.iloc[0].estado == 'oficial_conciliado'
    assert 'mediana_ingreso' not in p.indicador.values
    t.loc[t.dimension.eq('nacional'), 'tasa_sector_informal'] = 49
    with pytest.raises(ValueError, match='Conciliación'):
        e.publicar(t, ref)


def test_control_independiente_detecta_diferencia(mapa):
    t = e.resumir(e.preparar(personas(), mapa))
    with pytest.raises(ValueError, match='independiente'):
        e.validar_replica(t, {'nacional': {'volumenes': {'ocupados': {'n': 8}}}})


def test_particiones_y_mediana_con_pesos_desiguales(mapa):
    df = personas()
    df.loc[1, 'FACTOR'] = 3
    df['YLAB_PUBLI'] = df.YLAB_PUBLI.astype(object)
    df.loc[2, 'YLAB_PUBLI'] = ' '
    t = e.resumir(e.preparar(df, mapa))
    nacional = t[t.dimension.eq('nacional')].iloc[0]
    assert nacional.mediana_ingreso == 100
    for dim, g in t.groupby('dimension'):
        assert g.n_ocupados.sum() == nacional.n_ocupados
        assert g.peso_ocupados.sum() == nacional.peso_ocupados


def test_cli_fallo_hash_conserva_salida(tmp_path):
    publico = tmp_path/'data/processed/eneic_iv_2025/agregados_publicos.csv'
    publico.parent.mkdir(parents=True)
    publico.write_text('previo\n')
    raw = tmp_path/'raw'
    raw.mkdir()
    (raw/'Base-de-datos-Personas-ENEIC-IV-2025.xlsx').write_bytes(b'alterado')
    assert e.main(['--input-dir', str(raw), '--output-root', str(tmp_path)]) == 1
    assert publico.read_text() == 'previo\n'


def test_datos_reales_publicacion_y_replica():
    """Verifica las salidas ya generadas, sin repetir lectura del XLSX completo."""
    root = Path(__file__).resolve().parents[1]
    tabla = pd.read_csv(root/'docs/evidencia/eneic_iv_2025/diagnosticos_internos.csv',
                        dtype={'categoria':str})
    import json
    replica = json.loads((root/'docs/evaluation/eneic_iv_2025/eneic_resultado_independiente.json').read_text())
    e.validar_replica(tabla,replica)
    publicos = pd.read_csv(root/'data/processed/eneic_iv_2025/agregados_publicos.csv')
    assert len(publicos) == 21
    assert set(publicos.dimension) == {'nacional','dominio','rama_ine'}
    assert publicos.estado.eq('oficial_conciliado').all()
    assert not publicos.indicador.isin(['mediana_ingreso','composicion_informal_pct']).any()
    for _, grupo in tabla.groupby('dimension'):
        assert grupo.n_ocupados.sum() == 21233
        assert grupo.peso_ocupados.sum() == 7944838
    assert tabla.loc[tabla.dimension.eq('grupo_ciiu'),'composicion_informal_pct'].sum() == pytest.approx(100)


def test_volumen_nacional_derivado_y_numerador(mapa):
    t = e.resumir(e.preparar(personas(), mapa))
    ref = [dict(dimension='nacional',categoria='GT',indicador='peso_informal',valor=2,
                decimales=0,unidad='personas',referencia='control derivado')]
    p = e.publicar(t,ref)
    assert p.iloc[0].valor == 2
    assert p.iloc[0].denominador == 4
    assert p.iloc[0].n == 2


def test_orden_de_personas_no_cambia_agregados(mapa):
    df = personas()
    a = e.resumir(e.preparar(df,mapa)).to_csv(index=False)
    b = e.resumir(e.preparar(df.iloc[::-1],mapa)).to_csv(index=False)
    assert a == b


def test_clave_agregada_duplicada_se_rechaza(mapa):
    t = e.resumir(e.preparar(personas(),mapa))
    with pytest.raises(ValueError,match='duplicada'):
        e.publicar(pd.concat([t,t]),[])
