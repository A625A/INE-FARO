"""Contrato de entrada del radar y detección del contraste R1."""

import csv
import json
import shutil
from decimal import Decimal
from pathlib import Path

import pytest


DATOS = Path(__file__).resolve().parents[1] / 'data'
MATRIZ = 'processed/matriz_departamental.csv'
NACIONAL = 'processed/indicadores_encovi_nacional_2023.csv'
INFORMALIDAD = 'ocupacion_sector_informal'
POBREZA = 'pobreza_total'
PIB_HAB = 'pib_por_habitante'


@pytest.fixture
def copia(tmp_path):
    (tmp_path / 'processed').mkdir()
    for archivo in (MATRIZ, NACIONAL):
        shutil.copyfile(DATOS / archivo, tmp_path / archivo)
    return tmp_path


def editar(ruta, transformar):
    with ruta.open(encoding='utf-8', newline='') as archivo:
        lector = csv.DictReader(archivo)
        campos = lector.fieldnames
        filas = list(lector)
    with ruta.open('w', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, campos, lineterminator='\n')
        escritor.writeheader()
        escritor.writerows(transformar(filas))


def cargar(datos):
    from scripts.radar_rules.inputs import load_inputs

    return load_inputs(datos)


def test_referencias_ponderadas_y_mediana_departamental():
    universo = cargar(DATOS)
    assert [d.code for d in universo.territories] == [f'{d:02}' for d in range(1, 23)]
    assert universo.national_informality.value == Decimal('70.304975')
    assert universo.medians == {
        INFORMALIDAD: Decimal('77.9530445'),
        POBREZA: Decimal('53.7034785'),
        PIB_HAB: Decimal('33062.518856997196'),
    }
    assert universo.coverage['encovi_departamental']['pobreza_extrema']['elegibles'] == 17
    json.dumps(universo.coverage, allow_nan=False)


def test_hashes_locales_distinguen_filas_reordenadas_solo_en_bruto(copia):
    original = cargar(copia)
    for archivo in (MATRIZ, NACIONAL):
        editar(copia / archivo, reversed)
    invertido = cargar(copia)
    assert original.canonical_hashes == invertido.canonical_hashes
    assert original.raw_hashes.keys() == invertido.raw_hashes.keys()
    assert all(invertido.raw_hashes[k] != v for k, v in original.raw_hashes.items())
    assert original.coverage == invertido.coverage


@pytest.mark.parametrize(('campo', 'valor'), [
    ('estado', 'no_publicable'),
    ('n', '29'),
    ('cv', '30.00001'),
    ('cv', ''),
])
def test_resguarda_estimacion_con_cualquier_restriccion(copia, campo, valor):
    def cambiar(filas):
        # Conserva la barra de calidad de las UPM y simula estimaciones rehechas.
        filas[0][f'{POBREZA}_upm_n_2023'] = '1'
        filas[0][f'{POBREZA}_{campo}_2023'] = valor
        for medida in ('valor', 'ic95_inf', 'ic95_sup'):
            filas[0][f'{POBREZA}_{medida}_2023'] = '51.123456789'
        return filas

    editar(copia / MATRIZ, cambiar)
    universo = cargar(copia)
    lectura = universo.territories[0].encovi[POBREZA]
    assert (lectura.value, lectura.lower, lectura.upper) == (None, None, None)
    assert lectura.diagnostic['elegible'] is False
    if campo == 'cv':
        assert lectura.diagnostic[campo] == (float(valor) if valor else None)
    elif campo == 'n':
        assert lectura.diagnostic[campo] == 29
    else:
        assert lectura.diagnostic[campo] == valor
    assert universo.coverage['encovi_departamental'][POBREZA]['elegibles'] == 21
    assert '51.123456789' not in json.dumps(universo.coverage)


def test_resguarda_encovi_nacional_sin_cv(copia):
    def cambiar(filas):
        filas[0]['cv'] = ''
        return filas

    editar(copia / NACIONAL, cambiar)
    universo = cargar(copia)
    lectura = universo.national_informality
    assert (lectura.value, lectura.lower, lectura.upper) == (None, None, None)
    assert lectura.diagnostic['ponderador'] == 'FACTOR'
    assert lectura.diagnostic['cv'] is None


@pytest.mark.parametrize(('archivo', 'campo', 'valor'), [
    (MATRIZ, 'depto_id', '1'),
    (MATRIZ, 'depto_id', '02'),
    (MATRIZ, 'anio', '2024'),
    (MATRIZ, f'{POBREZA}_valor_2023', '100.01'),
    (MATRIZ, f'{POBREZA}_ic95_inf_2023', '30'),
    (MATRIZ, f'{POBREZA}_estado_2023', 'desconocido'),
    (MATRIZ, 'pib_por_habitante_q_2023', 'NaN'),
    (MATRIZ, 'vab_total_millones_q_2023', '0'),
    (MATRIZ, 'participacion_a_pct_2023', '1.5'),
    (MATRIZ, 'pib_total_millones_q_2023', '1'),
    (MATRIZ, 'actividad_predominante_2023', 'A'),
    (NACIONAL, 'anio', '2024'),
    (NACIONAL, 'ponderador', 'Factor3'),
    (NACIONAL, 'ic95_sup', '65'),
    (NACIONAL, 'ambito', 'area'),
])
def test_rechaza_incoherencias_del_contrato(copia, archivo, campo, valor):
    def cambiar(filas):
        filas[0][campo] = valor
        return filas

    editar(copia / archivo, cambiar)
    with pytest.raises(ValueError):
        cargar(copia)


def test_rechaza_columnas_incompletas(copia):
    ruta = copia / MATRIZ
    cabecera, *filas = ruta.read_text().splitlines()
    ruta.write_text('\n'.join([cabecera.replace('pib_por_habitante_q_2023,', ''), *filas]))
    with pytest.raises(ValueError, match='cabecera'):
        cargar(copia)


def test_matriz_incompleta_no_publica_universo(copia):
    editar(copia / MATRIZ, lambda filas: filas[:-1])
    with pytest.raises(ValueError, match='cobertura'):
        cargar(copia)


def test_pib_por_habitante_nulo_no_interviene_en_mediana(copia):
    def cambiar(filas):
        filas[0]['pib_por_habitante_q_2023'] = '0'
        return filas

    editar(copia / MATRIZ, cambiar)
    universo = cargar(copia)
    assert universo.territories[0].pib_per_capita is None
    assert universo.coverage['pib_por_habitante']['elegibles'] == 21


@pytest.mark.parametrize("gap_i,gap_p,y,reason", [
    ("3", "15", "150", "ambos"),
    ("3.00000001", "15", "150", None),
    ("3", "14.99999999", "149.99999999", None),
    ("3", "15", None, "solo_pobreza"),
    ("3", None, "150", "solo_pib"),
    ("3", None, None, None),
])
def test_r1_fronteras_y_clausulas_independientes(gap_i, gap_p, y, reason):
    from dataclasses import replace
    from scripts.radar_rules.r1 import evaluate

    u = cargar(DATOS)
    a, b = u.territories[:2]

    def artificial(d, i, p, prod):
        measures = dict(d.encovi)
        for key, val in ((INFORMALIDAD, i), (POBREZA, p)):
            measures[key] = replace(measures[key], value=val, lower=val, upper=val)
        return replace(d, encovi=measures, pib_per_capita=prod)

    a = artificial(a, Decimal(50), Decimal(40), Decimal(100))
    b = artificial(b, 50 + Decimal(gap_i), 40 + Decimal(gap_p) if gap_p else None,
                   Decimal(y) if y else None)
    result = evaluate(replace(u, territories=(a, b)), {"r1_i": 3, "r1_p": 15, "r1_y": Decimal("1.5")})
    assert [f["motivo"] for f in result] == ([reason] if reason else [])
