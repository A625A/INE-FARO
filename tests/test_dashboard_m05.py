"""Pruebas del contrato de datos y la navegación en M-05."""
import json
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


def test_filtra_solo_la_fila_no_publicable(tmp_path, pib):
    ruta = escribir_encovi(tmp_path, pib)
    df = pd.read_csv(ruta, dtype={'depto_id': str})
    df.loc[0, ['estado', 'valor', 'cv']] = ['no_publicable', None, None]
    df.to_csv(ruta, index=False)
    detalle = cargar_encovi(tmp_path, pib)
    assert len(detalle) == 65
    assert set(detalle.loc[detalle.depto_id.eq('01'), 'indicador']) == {'pobreza_total', 'pobreza_extrema'}
    assert detalle.estado.eq('publicable_con_reserva').all()


def test_app_local_y_cobertura_del_mapa(tmp_path, pib):
    mapa = json.loads((ROOT / 'data/reference/departamentos_m05.geojson').read_text())
    nombres = [f['properties']['shapeName'] for f in mapa['features']]
    assert len(nombres) == 22 and set(nombres) == set(pib.departamento)
    # Una copia aislada asegura que la prueba use exclusivamente el PIB local.
    datos = tmp_path / 'data'
    (datos / 'processed').mkdir(parents=True)
    (datos / 'reference').symlink_to(ROOT / 'data/reference')
    pib.to_csv(datos / 'processed/pib_per_capita.csv', index=False)
    app = tmp_path / 'app.py'
    app.write_text((ROOT / 'app.py').read_text())
    vista = AppTest.from_file(str(app), default_timeout=15).run()
    assert not vista.exception and len(vista.warning) == 1
    assert len(vista.selectbox[0].options) == 22
    for nombre in ('Guatemala', 'Quiché', 'Alta Verapaz'):
        vista.selectbox[0].select(nombre).run()
        valor = pib.loc[pib.departamento.eq(nombre), 'pib_per_capita'].item()
        assert not vista.exception and vista.metric[0].value == f'Q {valor:,.0f}'
    assert set(vista.dataframe[0].value.Departamento) == {'Guatemala', 'Quiché', 'Alta Verapaz'}
    assert any('M-04' in aviso.value for aviso in vista.info)

    ruta = escribir_encovi(datos / 'processed', pib)
    filas = pd.read_csv(ruta, dtype={'depto_id': str})
    filas.loc[0, ['valor', 'estado']] = [99.9, 'no_publicable']
    filas.to_csv(ruta, index=False)
    vista.selectbox[0].select('Guatemala').run()
    assert not vista.exception and not vista.warning
    assert [m.value for m in vista.metric[1:]] == ['—', '50.0 %', '50.0 %']
    assert vista.dataframe[0].value['Valor (%)'].tolist() == [50.0, 50.0]
    resumen = vista.dataframe[1].value.set_index('Departamento')
    assert pd.isna(resumen.at['Guatemala', 'Ocupación en el sector informal (%)'])
