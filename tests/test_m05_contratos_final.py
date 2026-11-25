"""Regresiones del consumidor público; usa los agregados versionados."""
from copy import deepcopy
import json
from pathlib import Path

import pandas as pd
import pytest

from dashboard_data import cargar_eneic, cargar_hogares, cargar_matriz, cargar_vab
from dashboard_radar import cargar_radar, exportar_radar, validar_radar

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed'


def test_eneic_publica_solo_celdas_autorizadas():
    datos = cargar_eneic(DATA)
    nacional = datos[datos.dimension.eq('nacional')].set_index('indicador')
    assert len(datos) == 21
    assert nacional.loc['peso_ocupados', 'valor_oficial'] == 7944838
    assert nacional.loc['tasa_sector_informal', 'valor_oficial'] == 65.6
    assert nacional.loc['peso_informal', 'valor_oficial'] == 5214094
    assert nacional.loc['media_ingreso', 'valor_oficial'] == 2842
    assert nacional.loc['media_ingreso', 'cobertura_pct'] == pytest.approx(94.28, abs=.005)


@pytest.mark.parametrize('campo,valor', [('estado', 'solo_revision_interna'), ('categoria', 'sexo')])
def test_eneic_rechaza_celdas_fuera_del_contrato(tmp_path, campo, valor):
    archivo = 'eneic_iv_2025/agregados_publicos.csv'
    (tmp_path / archivo).parent.mkdir()
    datos = pd.read_csv(DATA / archivo)
    datos.loc[0, campo] = valor
    datos.to_csv(tmp_path / archivo, index=False)
    with pytest.raises(ValueError, match='ENEIC'):
        cargar_eneic(tmp_path)


def test_matriz_y_perfiles_suprimen_valores(tmp_path):
    matriz, encovi = cargar_matriz(DATA)
    assert matriz.shape == (22, 67)
    assert len(encovi) == 66
    ocultas = encovi[encovi.estado.eq('no_publicable')]
    assert set(ocultas.depto_id) == {'01', '03', '05', '09', '11'}
    assert ocultas[['valor', 'ic95_inf', 'ic95_sup']].isna().all().all()
    for campo in ('valor', 'ic95_inf', 'ic95_sup'):
        matriz.loc[0, f'pobreza_extrema_{campo}_2023'] = 99.99
    matriz.to_csv(tmp_path / 'matriz_departamental.csv', index=False)
    limpia, _ = cargar_matriz(tmp_path)
    assert pd.isna(limpia.loc[0, 'pobreza_extrema_valor_2023'])
    hogares = pd.read_csv(DATA / 'perfiles_hogares.csv', dtype={'depto_id': str})
    restringidas = hogares.estado.eq('no_publicable')
    hogares.loc[restringidas, ['valor', 'cv']] = [999999, 80]
    hogares.to_csv(tmp_path / 'perfiles_hogares.csv', index=False)
    publico = cargar_hogares(tmp_path)
    assert len(publico) == 207 and restringidas.sum() == 14
    assert publico.loc[restringidas, ['valor', 'cv']].isna().all().all()


def test_vab_preserva_granos_y_tipo_de_precio():
    nacional, grupo = cargar_vab(DATA)
    assert len(nacional) == 22 and len(grupo) == 374
    assert 2020 not in set(nacional.anio)
    assert grupo.loc[grupo.tipo_precio.ne('corrientes'), 'composicion_pct'].isna().all()
    corte = nacional[nacional.anio.eq(2023) & nacional.tipo_precio.eq('corrientes')].iloc[0]
    assert round(corte.vab_informal, 2) == 172538.68
    assert round(corte.vab_total, 2) == 762881.36
    assert round(corte.participacion_informal_pct, 2) == 22.62


def test_radar_tres_esquemas_reales_y_descarga_vacia():
    radar = cargar_radar(DATA)
    assert radar['conteos'] == {'R1': 26, 'R2a': 0, 'R2b': 1, 'R3': 7, 'R4': 10}
    assert len(radar['hallazgos']) == 44 and len(radar['sensibilidad']) == 21
    assert json.loads(exportar_radar(radar, []))['hallazgos'] == []
    assert len(exportar_radar(radar, [], 'csv').splitlines()) == 1


@pytest.mark.parametrize('fuente,cambio', [
    ('INE, ENCOVI 2023', {'diagnostico': {'estado': 'no_publicable', 'elegible': False}}),
    ('INE, ENCOVI 2023', {'diagnostico': {'ic95_inf': 101}}),
    ('INE, ENCOVI 2023', {'diagnostico': {'cv': 30.00001}}),
    ('INE, ENCOVI 2023', {'diagnostico': {'n': 29}}),
    ('INE, ENCOVI 2023', {'fuente': 'fuente desconocida'}),
    ('Banguat, cuadro 8, 2023', {'valor': 0}),
    ('Banguat, cuadro 8, 2023', {'diagnostico': {'revision': ''}}),
    ('Banguat, cuadro 7, VAB a precios corrientes 2023', {'valor': float('inf')}),
    ('Banguat, cuadro 7, VAB a precios corrientes 2023', {'unidad': 'Q'}),
    ('Banguat, cuadro 7, VAB a precios corrientes 2023', {'diagnostico': {'estado': 'no_publicable'}}),
])
def test_radar_rechaza_ficha_y_protege_exportacion(fuente, cambio):
    radar = json.loads((DATA / 'hallazgos.json').read_text())
    ficha, evidencia = next((f, e) for f in radar['hallazgos'] for e in f['evidencias']
                             if e['fuente'] == fuente)
    cambio = deepcopy(cambio)
    evidencia['diagnostico'].update(cambio.pop('diagnostico', {}))
    evidencia.update(cambio)
    publico = validar_radar(radar)
    assert publico['rechazados'] == 1
    assert len(publico['hallazgos']) == 43
    assert ficha['id'] not in exportar_radar(publico, [ficha['id']]).decode()
