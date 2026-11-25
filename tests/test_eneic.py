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
