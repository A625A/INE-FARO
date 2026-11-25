import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from xlsx_fixture import xlsx_minimo

ROOT = Path(__file__).resolve().parents[1]


def test_dinese_reconcilia_controles_oficiales_y_excluye_crecimiento(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/auditar_dinese.py'),
         '--output-dir', str(tmp_path / 'datos'),
         '--evidence-dir', str(tmp_path / 'evidencia')],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    with (tmp_path / 'datos/dinese_resumen.csv').open() as file:
        rows = list(csv.DictReader(file))
    assert {r['depto_id'] for r in rows} == {f'{n:02}' for n in range(1, 23)}
    # Cuadros oficiales nacionales 2023 y 2024; no derivados del código del auditor.
    for year, registered, sales in [('2023', 425464, 220903), ('2024', 645431, 338415)]:
        assert sum(int(r['empresas']) for r in rows if r['anio'] == year) == registered
        assert sum(int(r['empresas']) for r in rows if r['anio'] == year
                   and r['movimiento_ventas'] == 'con_movimiento') == sales
    evidence = json.loads((tmp_path / 'evidencia/I-05.json').read_text())
    assert evidence['viabilidad_transversal_2023'] is True
    assert evidence['habilitar_crecimiento_radar'] is False
    assert evidence['codigo_longitudinal_validado'] is False
    assert evidence['controles_oficiales'] == 'validados'
    assert all(y['duplicados_codigo'] == 0 for y in evidence['anios'])
    assert {r['seccion_codigo'] for r in rows} == set('ABCDEFGHIJKLMNOPQRSTU')
    assert {r['sector_banguat'] for r in rows if r['seccion_codigo'] in 'DE'} == {'D-E'}


@pytest.mark.parametrize('cambio,error', [
    ({'sector': 'Sector inventado'}, 'Sección CIIU desconocida'),
    ({'depto': 'Territorio inventado'}, 'Departamento desconocido'),
    ({'year': 2022}, 'AÑO inconsistente'),
    ({'movimiento': None}, 'Movimiento de ventas desconocido'),
    ({'codigo': None}, 'CÓDIGO vacío'),
])
def test_dinese_rechaza_categorias_invalidas_sin_publicar(cambio, error, tmp_path):
    entrada = tmp_path / 'entrada'
    entrada.mkdir()
    row = {'codigo': 1, 'year': 2023, 'sector': 'Agricultura, ganadería, silvicultura y pesca',
           'personeria': 'Individual', 'rango': 'Micro', 'movimiento': 'Con movimiento',
           'depto': 'Guatemala', 'municipio': 'Guatemala'}
    row.update(cambio)
    headers = ['CÓDIGO', 'AÑO', 'SECCION_CIIU_4', 'TIPO_PERSONERIA', 'CLA_RANGO_VENTAS',
               'MOVIMIENTO_DE_VENTAS', 'NOMBRE_DEPARTAMENTO', 'NOMBRE_MUNICIPIO']
    xlsx_minimo(entrada / 'dinese-2023.xlsx', [headers, list(row.values())])
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/auditar_dinese.py'),
        '--input-dir', str(entrada), '--output-dir', str(tmp_path / 'salida'),
        '--evidence-dir', str(tmp_path / 'evidencia')], capture_output=True, text=True)
    assert result.returncode != 0
    assert error in result.stderr
    assert not (tmp_path / 'salida').exists()


@pytest.mark.parametrize('modo,error', [
    ('duplicado', 'CÓDIGO vacío, inválido o duplicado'),
    ('columnas', 'Columnas inesperadas'),
    ('conteos', 'Controles oficiales no concilian'),
])
def test_dinese_rechaza_duplicados_esquema_y_conteos(modo, error, tmp_path):
    entrada = tmp_path / 'entrada'
    entrada.mkdir()
    headers = ['CÓDIGO', 'AÑO', 'SECCION_CIIU_4', 'TIPO_PERSONERIA', 'CLA_RANGO_VENTAS',
               'MOVIMIENTO_DE_VENTAS', 'NOMBRE_DEPARTAMENTO', 'NOMBRE_MUNICIPIO']
    # Datos sintéticos de prueba. No se entregan como resultados económicos.
    departamentos = ['Guatemala', 'El Progreso', 'Sacatepéquez', 'Chimaltenango', 'Escuintla',
        'Santa Rosa', 'Sololá', 'Totonicapán', 'Quetzaltenango', 'Suchitepéquez',
        'Retalhuleu', 'San Marcos', 'Huehuetenango', 'Quiché', 'Baja Verapaz',
        'Alta Verapaz', 'Petén', 'Izabal', 'Zacapa', 'Chiquimula', 'Jalapa', 'Jutiapa']
    rows = [[i, 2023, 'Agricultura, ganadería, silvicultura y pesca', 'Individual',
             'Micro', 'Con movimiento', d, 'Municipio de prueba'] for i, d in enumerate(departamentos, 1)]
    if modo == 'duplicado':
        rows.insert(1, rows[0])
    if modo == 'columnas':
        headers[0] = 'IDENTIFICADOR_NO_DOCUMENTADO'
    xlsx_minimo(entrada / 'dinese-2023.xlsx', [headers, *rows])
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/auditar_dinese.py'),
        '--input-dir', str(entrada), '--output-dir', str(tmp_path / 'salida'),
        '--evidence-dir', str(tmp_path / 'evidencia')], capture_output=True, text=True)
    assert result.returncode != 0
    assert error in result.stderr
    assert not (tmp_path / 'salida').exists()
