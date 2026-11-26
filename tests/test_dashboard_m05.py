"""Pruebas del contrato de datos y la navegación en M-05."""
import json
import shutil
from pathlib import Path
import sys

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dashboard_utils import INDICADORES, cargar_encovi, cargar_pib


def escribir_encovi(tmp_path, pib):
    filas = [
        dict(depto_id=fila.depto_id, departamento=fila.departamento, anio=2023,
             indicador=indicador, valor=50.0, unidad='porcentaje', fuente='ENCOVI 2023 - INE',
             n=100, upm_n=20, ponderador='FACTOR', cv=5.0, ic95_inf=45, ic95_sup=55,
             precision='aproximada_depto_upm_sin_estratos_originales',
             estado='publicable_con_reserva')
        for fila in pib.itertuples() for indicador in INDICADORES
    ]
    ruta = tmp_path / 'indicadores_encovi_2023.csv'
    pd.DataFrame(filas).to_csv(ruta, index=False)
    return ruta


@pytest.fixture
def pib():
    return cargar_pib(ROOT / 'data/processed')


def test_sin_m01_solo_pib_real(tmp_path, pib):
    assert len(pib) == 22
    assert cargar_encovi(tmp_path, pib) is None


def test_con_m01_cruce_uno_a_uno(tmp_path, pib):
    escribir_encovi(tmp_path, pib)
    detalle = cargar_encovi(tmp_path, pib)
    assert len(detalle) == 66
    assert detalle.pivot(index='depto_id', columns='indicador', values='valor').pobreza_total.eq(50).all()


def test_rechaza_encovi_incompleto(tmp_path, pib):
    ruta = escribir_encovi(tmp_path, pib)
    pd.read_csv(ruta).iloc[:-1].to_csv(ruta, index=False)
    with pytest.raises(ValueError, match='22 departamentos'):
        cargar_encovi(tmp_path, pib)


def test_rechaza_depto_duplicado_pib(tmp_path, pib):
    pib.loc[1, 'depto_id'] = '01'
    pib.to_csv(tmp_path / 'pib_per_capita.csv', index=False)
    with pytest.raises(ValueError, match='22 departamentos'):
        cargar_pib(tmp_path)


def test_conserva_cinco_filas_sin_publicar_sus_estimaciones(tmp_path, pib):
    ruta = escribir_encovi(tmp_path, pib)
    df = pd.read_csv(ruta, dtype={'depto_id': str})
    restringidas = df.depto_id.isin(['01', '03', '05', '09', '11']) & df.indicador.eq('pobreza_extrema')
    df.loc[restringidas, ['estado', 'valor', 'cv']] = ['no_publicable', 99.9, 35]
    df.to_csv(ruta, index=False)
    detalle = cargar_encovi(tmp_path, pib)
    assert len(detalle) == 66 and detalle.depto_id.nunique() == 22
    assert detalle.valor.notna().sum() == 61
    no_publicables = detalle.loc[detalle.estado.eq('no_publicable')]
    assert len(no_publicables) == 5
    assert no_publicables[['valor', 'ic95_inf', 'ic95_sup']].isna().all().all()
    assert no_publicables.cv.eq(35).all()


def test_app_local_y_cobertura_del_mapa(tmp_path, pib):
    mapa = json.loads((ROOT / 'data/reference/departamentos_m05.geojson').read_text())
    nombres = [f['properties']['shapeName'] for f in mapa['features']]
    assert len(nombres) == 22 and set(nombres) == set(pib.departamento)
    datos = tmp_path / 'data'
    procesados = datos / 'processed'
    procesados.mkdir(parents=True)
    shutil.copytree(ROOT / 'data/reference', datos / 'reference')
    pib.to_csv(procesados / 'pib_per_capita.csv', index=False)
    assert cargar_pib(procesados).equals(pib)
    assert cargar_encovi(procesados, pib) is None
    app = tmp_path / 'app.py'
    app.write_text((ROOT / 'app.py').read_text())
    vista = AppTest.from_file(str(app), default_timeout=20).run()
    vista.radio(key='seccion').set_value('Territorio').run()
    assert not vista.exception and 'matriz_departamental.csv' in vista.error[0].value

    # El contrato territorial vigente concentra PIB y tasas en la matriz M-03.
    matriz = pd.read_csv(ROOT / 'data/processed/matriz_departamental.csv', dtype={'depto_id': str})
    matriz.to_csv(procesados / 'matriz_departamental.csv', index=False)
    vista.run()
    assert any('Hallazgos relacionados' in aviso.value for aviso in vista.error)
    assert set(vista.selectbox(key='filtro_depto').options) == set(nombres)
    tabla = vista.dataframe[0].value
    assert set(tabla.Departamento) == set(nombres)
    for codigo in ('01', '14', '16'):
        vista.selectbox(key='filtro_depto').select(codigo).run()
        fila = pib.loc[pib.depto_id.eq(codigo)].iloc[0]
        assert any(h.value == fila.departamento for h in vista.subheader)
        assert any(f'Q {fila.pib_per_capita:,.0f}' in h.proto.body for h in vista.get('html'))
        assert not vista.exception

    for archivo in ('hallazgos.json', 'perfiles_hogares.csv'):
        shutil.copyfile(ROOT / 'data/processed' / archivo, procesados / archivo)

    # Una cifra restringida introducida en el archivo jamás debe llegar a la vista.
    for indicador in INDICADORES:
        for campo, valor in dict(valor=50.0, n=100, cv=5, ic95_inf=45, ic95_sup=55,
                                 estado='publicable_con_reserva').items():
            matriz.loc[matriz.depto_id.eq('01'), f'{indicador}_{campo}_2023'] = valor
    matriz.loc[matriz.depto_id.eq('01'), ['ocupacion_sector_informal_valor_2023',
              'ocupacion_sector_informal_estado_2023']] = [99.9, 'no_publicable']
    matriz.to_csv(procesados / 'matriz_departamental.csv', index=False)
    vista.selectbox(key='filtro_depto').select('01').run()
    assert not vista.exception and not vista.error and not vista.warning
    ficha = next(h.proto.body for h in vista.get('html') if 'faro-cifras' in h.proto.body and '<strong>' in h.proto.body)
    assert ficha.count('50.0 %') == 2 and 'N/D · precisión insuficiente' in ficha and '99.9' not in ficha
    resumen = vista.dataframe[0].value.set_index('Departamento')
    assert resumen.at['Guatemala', 'Valor'] == 'N/D · precisión insuficiente'
    detalle = vista.dataframe[1].value.set_index('Indicador').loc['Ocupación en el sector informal']
    assert detalle['CV (%)'] == 5 and pd.isna(detalle['IC95 inferior (%)']) and pd.isna(detalle['IC95 superior (%)'])
    vista.selectbox(key='filtro_comparar').select('16').run()
    comparacion = vista.dataframe[2].value.set_index('Indicador')
    assert pd.isna(comparacion.at['Ocupación en el sector informal', 'Guatemala'])
    assert comparacion.Guatemala.iloc[:3].count() == 2


def test_precision_csv_integrado(pib):
    detalle = cargar_encovi(ROOT / 'data/processed', pib)
    assert detalle.clasificacion.value_counts().to_dict() == {
        'Mayor precisión': 51, 'Precisión moderada': 10, 'No publicable': 5,
    }
    restringidas = detalle.loc[detalle.estado.eq('no_publicable')].set_index('departamento')
    assert restringidas.indicador.eq('pobreza_extrema').all()
    assert restringidas[['valor', 'ic95_inf', 'ic95_sup']].isna().all().all()
    esperado = {
        'Guatemala': (38.60323, 8.60323), 'Sacatepéquez': (31.46913, 1.46913),
        'Escuintla': (31.78476, 1.78476), 'Quetzaltenango': (33.41783, 3.41783),
        'Retalhuleu': (35.84744, 5.84744),
    }
    for depto, (cv, exceso) in esperado.items():
        assert restringidas.at[depto, 'cv'] == cv
        assert restringidas.at[depto, 'exceso_pp'] == pytest.approx(exceso)
    assert detalle.loc[detalle.estado.ne('no_publicable'), 'exceso_pp'].eq(0).all()


@pytest.mark.parametrize('cv,n,clasificacion', [
    (20, 30, 'Mayor precisión'), (20.00001, 30, 'Precisión moderada'),
    (30, 30, 'Precisión moderada'), (30.00001, 30, 'No publicable'),
    (0, 29, 'No publicable'), (None, 30, 'No publicable'),
    ('indeterminado', 30, 'No publicable'), ('inf', 30, 'No publicable'),
    (-1, 30, 'No publicable'), (2, None, 'No publicable'),
])
def test_umbral_independiente_del_estado_de_origen(tmp_path, pib, cv, n, clasificacion):
    ruta = ROOT / 'data/processed/indicadores_encovi_2023.csv'
    filas = pd.read_csv(ruta, dtype=str)
    filas.loc[0, ['cv', 'n']] = [str(cv), str(n)]
    filas.to_csv(tmp_path / ruta.name, index=False)
    fila = cargar_encovi(tmp_path, pib).iloc[0]
    assert fila.clasificacion == clasificacion
    if clasificacion == 'No publicable':
        assert fila.estado == 'no_publicable'
        assert fila[['valor', 'ic95_inf', 'ic95_sup']].isna().all()
        if cv in (None, 'indeterminado', 'inf', -1):
            assert pd.isna(fila.exceso_pp)
    else:
        assert fila.valor == float(filas.at[0, 'valor'])


def test_calidad_interactiva_con_csv_integrado():
    vista = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20).run()
    vista.radio(key='seccion').set_value('Metodología y calidad').run()
    assert any(h.value == 'Calidad estadística' for h in vista.header)
    assert [m.value for m in vista.metric] == ['66', '61', '5']
    vista.selectbox(key='calidad_clasificacion').select('No publicable').run()
    assert [m.value for m in vista.metric] == ['5', '0', '5']
    vista.selectbox(key='calidad_departamento').select('Guatemala').run()
    diagnostico = vista.dataframe[0].value
    assert list(diagnostico.Departamento) == ['Guatemala']
    assert set(diagnostico) == {'Departamento', 'Indicador', 'Clasificación', 'CV (%)',
                                'Muestra (n)', 'Estado', 'Exceso (pp)'}
    assert diagnostico.iloc[0]['Exceso (pp)'] == pytest.approx(8.60323)
    vista.selectbox(key='calidad_indicador').select('Pobreza total').run()
    assert [m.value for m in vista.metric] == ['0', '0', '0']
    assert vista.info and not vista.exception
