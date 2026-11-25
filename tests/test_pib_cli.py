import csv
import subprocess
import sys
from pathlib import Path

import pytest

from xlsx_fixture import copiar_pib_alterado

ROOT = Path(__file__).resolve().parents[1]


def test_pib_2023_conserva_departamentos_medidas_y_conciliacion(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/procesar_pib.py'),
         '--output-dir', str(tmp_path / 'datos'),
         '--evidence-dir', str(tmp_path / 'evidencia')],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    with (tmp_path / 'datos/pib_departamental.csv').open() as file:
        rows = list(csv.DictReader(file))
    assert len(rows) == 836  # 22 departamentos × (17 VAB + IPNS + PIB) × 2 precios
    assert {r['depto_id'] for r in rows} == {f'{n:02}' for n in range(1, 23)}
    assert {r['anio'] for r in rows} == {'2023'}
    assert {r['medida'] for r in rows} == {'pib_total', 'valor_agregado', 'impuestos_netos'}
    guatemala = next(r for r in rows if r['depto_id'] == '01'
                     and r['sector'] == 'TOTAL' and r['tipo_precio'] == 'corrientes')
    assert float(guatemala['pib_valor']) == 354106.0518568182  # XLSX oficial, N9
    with (tmp_path / 'datos/pib_per_capita.csv').open() as file:
        per_capita = list(csv.DictReader(file))
    assert len(per_capita) == 22
    assert per_capita[0]['unidad'] == 'quetzales_por_habitante'
    assert float(per_capita[0]['pib_per_capita']) == 97289.2325263085
    with (tmp_path / 'datos/pib_conciliacion.csv').open() as file:
        controls = list(csv.DictReader(file))
    assert len(controls) == 38
    total = next(r for r in controls if r['sector'] == 'TOTAL'
                 and r['tipo_precio'] == 'corrientes')
    assert float(total['extrarregional']) == 223.09231393999994
    assert total['estado'] == 'validado'
    assert {r['estado'] for r in controls if r['tipo_precio'] == 'volumen_encadenado_2013'} == {'no_aditivo'}


@pytest.mark.parametrize('cambios,error', [
    ({'N9': None}, 'Valor numérico faltante'),
    ({'B10': 1, 'C10': 'Guatemala'}, 'Territorio duplicado'),
    ({'N7': 2022}, 'Cobertura anual inesperada'),
    ({'N9': 1}, 'Conciliación nacional fallida'),
    ({'C5': 'Miles de quetzales'}, 'Unidad inesperada'),
])
def test_pib_rechaza_insumos_invalidos_sin_publicar(cambios, error, tmp_path):
    copiar_pib_alterado(ROOT / 'data/raw/banguat', tmp_path / 'entrada', cambios)
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/procesar_pib.py'),
         '--input-dir', str(tmp_path / 'entrada'), '--output-dir', str(tmp_path / 'salida'),
         '--evidence-dir', str(tmp_path / 'evidencia')], capture_output=True, text=True)
    assert result.returncode != 0
    assert error in result.stderr
    assert not (tmp_path / 'salida').exists()


def test_pib_selecciona_2024_y_es_reproducible_fuera_del_repositorio(tmp_path):
    command = [sys.executable, str(ROOT / 'scripts/procesar_pib.py'), '--year', '2024',
               '--output-dir', str(tmp_path / 'salida'), '--evidence-dir', str(tmp_path / 'evidencia')]
    first = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    before = {p.name: p.read_bytes() for p in (tmp_path / 'salida').glob('*.csv')}
    second = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    assert before == {p.name: p.read_bytes() for p in (tmp_path / 'salida').glob('*.csv')}
    with (tmp_path / 'salida/pib_departamental.csv').open() as file:
        assert {r['anio'] for r in csv.DictReader(file)} == {'2024'}


def test_pib_descarga_no_sobrescribe_un_snapshot_distinto(tmp_path):
    copiar_pib_alterado(ROOT / 'data/raw/banguat', tmp_path / 'entrada', {'N9': 1})
    original = (tmp_path / 'entrada/5_PIB_total_por_departamento.xlsx').read_bytes()
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/procesar_pib.py'),
        '--download', '--input-dir', str(tmp_path / 'entrada'),
        '--output-dir', str(tmp_path / 'salida')], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'SHA-256' in result.stderr
    assert (tmp_path / 'entrada/5_PIB_total_por_departamento.xlsx').read_bytes() == original
    assert not (tmp_path / 'salida').exists()
