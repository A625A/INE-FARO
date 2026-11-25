"""Pruebas de M-02: sintéticas para reglas y una ejecución real del contrato."""
import csv
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from procesar_hogares import (COLUMNAS, estimar_media, preparar_negocios,
                              validar_negocios_dos, validar_remesas)

ROOT = Path(__file__).resolve().parents[1]


def test_estimar_media_ponderada_y_precision():
    df = pd.DataFrame({
        'DEPTO': [1, 1, 1, 1],
        'UPM': [10, 10, 11, 11],
        'FACTOR': [2, 2, 1, 1],
        'x': [10, 20, 30, 40],
    })
    resultado = estimar_media(df, df.x, 'FACTOR')
    assert resultado['valor'] == pytest.approx(130 / 6, abs=1e-5)
    assert resultado['n'] == 4
    assert resultado['upm_n'] == 2
    assert resultado['cv'] > 0
    assert resultado['precision'].startswith('aproximada')


def test_estimar_media_rechaza_peso_invalido():
    df = pd.DataFrame({'DEPTO': [1, 1], 'UPM': [10, 10],
                       'FACTOR': [1, 0], 'x': [10, 20]})
    with pytest.raises(ValueError, match='Ponderador'):
        estimar_media(df, df.x, 'FACTOR')


def test_preparar_negocios_agrega_antes_de_cruzar():
    hogares = pd.DataFrame({'NO_HOGAR': [1, 2, 3], 'DEPTO': [1, 1, 2],
                            'UPM': [10, 11, 20], 'FACTOR': [1, 2, 3]})
    uno = pd.DataFrame({'NO_HOGAR': [1, 2, 3], 'P14A01': [1, 2, 2],
                        'P14A02A': [2, 1, None]})
    dos = pd.DataFrame({'NO_HOGAR': [1, 1], 'ID_NEGOCIO': [1, 2],
                        'P14A13': [100, 200], 'P14A16': [50, -10]})
    resultado = preparar_negocios(hogares, uno, dos)
    assert resultado.tiene_negocio.tolist() == [True, False, False]
    assert resultado.n_negocios.tolist() == [2, 0, 0]
    assert resultado.venta_mensual.tolist() == [300, 0, 0]
    assert resultado.ganancia_mensual.tolist() == [40, 0, 0]


def test_negocios_dos_rechaza_clave_duplicada():
    dos = pd.DataFrame({'NO_HOGAR': [1, 1], 'ID_NEGOCIO': [1, 1],
                        'P14A13': [100, 200], 'P14A16': [50, 60]})
    with pytest.raises(ValueError, match='Clave NO_HOGAR/ID_NEGOCIO'):
        validar_negocios_dos(dos)


def test_remesas_exige_tres_montos_en_receptores():
    base = pd.DataFrame({'DEPTO': [1, 1], 'UPM': [10, 10], 'FACTOR': [1, 1],
                         'P11C01': [1, 2], 'P11C02B': [10, None],
                         'P11C03B': [20, None], 'P11C04B': [0, None]})
    validado = validar_remesas(base)
    assert validado.recibio_remesas.tolist() == [True, False]
    assert validado.monto_mensual.iloc[0] == pytest.approx(10)
    base.loc[0, 'P11C04B'] = None
    with pytest.raises(ValueError, match='tres montos'):
        validar_remesas(base)


def test_cli_genera_contrato_y_claves_unicas(tmp_path):
    resultado = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/procesar_hogares.py'),
         '--output-dir', str(tmp_path / 'salida')],
        capture_output=True, text=True)
    assert resultado.returncode == 0, resultado.stderr
    with (tmp_path / 'salida/perfiles_hogares.csv').open(encoding='utf-8') as file:
        lector = csv.DictReader(file)
        assert tuple(lector.fieldnames) == COLUMNAS
        filas = list(lector)
    assert len(filas) == 207
    assert {f['tabla'] for f in filas} == {
        'remesas_personas', 'negocios_hogares', 'consumo_per_capita'}
    assert {f['anio'] for f in filas} == {'2023'}
    assert sum(f['ambito'] == 'nacional' for f in filas) == 9
    departamentales = [f for f in filas if f['ambito'] == 'departamental']
    assert {f['depto_id'] for f in departamentales} == {
        f'{n:02}' for n in range(1, 23)}
    assert all(f['departamento'] for f in departamentales)
    assert all(not f['depto_id'] for f in filas if f['ambito'] == 'nacional')
    assert len({(f['tabla'], f['ambito'], f['depto_id'], f['indicador'])
                for f in filas}) == 207
