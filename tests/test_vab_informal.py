"""Pruebas de estructura y precisión de los snapshots de Banguat."""
import sys
from functools import lru_cache
from pathlib import Path

import pytest
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import procesar_vab_informal as vab


@lru_cache
def filas(nombre, hoja):
    libro = load_workbook(next((ROOT / "data/raw/banguat_nacional").glob(nombre)),
                          read_only=True, data_only=True)
    try:
        return tuple(libro[hoja].values)
    finally:
        libro.close()


def alteradas(original, fila, columna, valor):
    copia = [list(r) for r in original]
    copia[fila - 1][columna - 1] = valor
    return copia


@pytest.mark.parametrize("fila,columna,valor", [
    (5, 2, "Miles de quetzales"), (7, 13, 2020), (7, 13, 2019),
    (9, 3, "B"), (14, 15, None), (14, 15, -1), (14, 15, True),
    (14, 15, float("nan")), (26, 15, 900000), (42, 15, 39),
])
def test_rechaza_cuadro_12_invalido(fila, columna, valor):
    datos = alteradas(filas("12_*.xlsx", "12.1"), fila, columna, valor)
    with pytest.raises(ValueError):
        vab.leer_informal(datos, "12.1")


def test_total_encadenado_se_lee_directamente():
    datos = alteradas(filas("12_*.xlsx", "12.2"), 14, 15, 1)
    periodos = vab.leer_informal(datos, "12.2")
    assert 2020 not in periodos
    assert periodos[2023]["total"] == 117009.886658
    assert periodos[2023]["grupos"]["G"][1] == 1


@pytest.mark.parametrize("fila,columna,valor", [
    (4, 2, "P1 Producción"), (5, 2, "Porcentajes"), (6, 2, "Año 2022 p/"),
    (10, 9, "S14 Hogares"), (12, 2, "AE002"), (12, 9, None),
    (126, 9, 0), (126, 9, 800000),
])
def test_rechaza_ccis_incompatible(fila, columna, valor):
    datos = alteradas(filas("5_*.xlsx", "5.103"), fila, columna, valor)
    with pytest.raises(ValueError):
        vab.leer_ccis(datos, "5.103", 2023)


def test_mapeo_oficial_incluye_todas_las_actividades():
    original = filas("Nomenclaturas*.xlsx", "NAEG-CIIU")
    mapa = vab.leer_mapeo(original)
    assert len(mapa) == 105
    assert mapa["AE062"] == "G" and mapa["AE096"] == "R-S-T-U"


@pytest.mark.parametrize("fila,columna,valor", [
    (11, 4, "0111, 4510"), (11, 4, "0410"), (11, 4, None),
    (11, 2, "AE002"), (11, 2, None), (9, 4, "CIIU revisión 3"),
])
def test_mapeo_incompleto_o_incompatible(fila, columna, valor):
    original = filas("Nomenclaturas*.xlsx", "NAEG-CIIU")
    with pytest.raises(ValueError):
        vab.leer_mapeo(alteradas(original, fila, columna, valor))


def test_reproduccion_y_hash_invalido(tmp_path):
    import shutil
    import subprocess
    comando = [sys.executable, str(ROOT / 'scripts/procesar_vab_informal.py'),
               '--output-dir', str(tmp_path / 'salida'), '--evidence-dir', str(tmp_path / 'evidencia')]
    primero = subprocess.run(comando, capture_output=True, text=True)
    assert primero.returncode == 0, primero.stderr
    salida = tmp_path / 'salida/vab_informal_nacional.csv'
    original = salida.read_bytes()
    segundo = subprocess.run(comando, capture_output=True, text=True)
    assert segundo.returncode == 0, segundo.stderr
    assert salida.read_bytes() == original
    insumos = tmp_path / 'insumos'
    shutil.copytree(ROOT / 'data/raw/banguat_nacional', insumos)
    with (insumos / vab.INFORMAL).open('ab') as archivo:
        archivo.write(b'alterado')
    fallido = subprocess.run(comando + ['--input-dir', str(insumos)], capture_output=True, text=True)
    assert fallido.returncode != 0
    assert salida.read_bytes() == original
