"""Contrato de M-03 comprobado desde el CLI y los CSV de origen."""
import csv
import os
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATOS = ROOT / 'data'
ENC = 'processed/indicadores_encovi_2023.csv'
NAC = 'processed/indicadores_encovi_nacional_2023.csv'
PIB = 'processed/pib_departamental.csv'
PC = 'processed/pib_per_capita.csv'
CAT = 'reference/sectores_ciiu.csv'
PUBLICADA = DATOS / 'processed/matriz_departamental.csv'
GRUPOS = 'A B C D-E F G H I J K L M N O P Q R-S-T-U'.split()


def leer(ruta):
    with ruta.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def guardar(ruta, filas):
    with ruta.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=filas[0])
        writer.writeheader()
        writer.writerows(filas)


def ejecutar(datos, salida, env=None):
    return subprocess.run([sys.executable, str(ROOT / 'scripts/build_matriz.py'),
                           '--data-dir', str(datos), '--output', str(salida)],
                          cwd=salida.parent, env=env, capture_output=True, text=True)


@pytest.fixture
def copia(tmp_path):
    for nombre in [ENC, NAC, PIB, PC, CAT]:
        destino = tmp_path / nombre
        destino.parent.mkdir(exist_ok=True)
        shutil.copyfile(DATOS / nombre, destino)
    return tmp_path


def test_contraste_independiente_con_originales():
    assert PUBLICADA.exists(), 'Falta el CSV del contrato M-03'
    filas = leer(PUBLICADA)
    assert [f['depto_id'] for f in filas] == [f'{i:02}' for i in range(1, 23)]
    matriz = {f['depto_id']: f for f in filas}
    restringidos = set()
    for original in leer(DATOS / ENC):
        f = matriz[original['depto_id']]
        indicador = original['indicador']
        assert (f['departamento'], f['anio']) == (original['departamento'], '2023')
        restringido = original['estado'] == 'no_publicable'
        if restringido:
            restringidos.add((original['depto_id'], indicador))
        for campo in ('valor', 'ic95_inf', 'ic95_sup', 'cv', 'n', 'upm_n', 'ponderador', 'estado'):
            esperado = original[campo]
            if restringido and campo in ('valor', 'ic95_inf', 'ic95_sup'):
                esperado = ''
            assert f[f'{indicador}_{campo}_2023'] == esperado
    assert restringidos == {(d, 'pobreza_extrema') for d in ['01', '03', '05', '09', '11']}
    assert sum(v == '' for f in filas for v in f.values()) == 15

    corrientes = [r for r in leer(DATOS / PIB) if r['tipo_precio'] == 'corrientes']
    for original in leer(DATOS / PC):
        d = original['depto_id']
        f = matriz[d]
        assert f['departamento'] == original['departamento']
        assert Decimal(f['pib_por_habitante_q_2023']) == Decimal(original['pib_per_capita'])
        importes = {r['sector']: Decimal(r['pib_valor']) for r in corrientes if r['depto_id'] == d}
        vab = sum(importes[g] for g in GRUPOS)
        assert Decimal(f['pib_total_millones_q_2023']) == importes['TOTAL']
        assert Decimal(f['ipns_millones_q_2023']) == importes['IPNS']
        assert abs(Decimal(f['vab_total_millones_q_2023']) - vab) < Decimal('1e-8')
        assert abs(importes['TOTAL'] - importes['IPNS'] - vab) <= Decimal('1e-6')
        porcentajes = []
        for g in GRUPOS:
            slug = g.lower().replace('-', '_')
            assert Decimal(f[f'vab_{slug}_millones_q_2023']) == importes[g]
            pct = Decimal(f[f'participacion_{slug}_pct_2023'])
            assert abs(pct - 100 * importes[g] / vab) < Decimal('1e-10')
            porcentajes.append(pct)
        assert abs(sum(porcentajes) - 100) <= Decimal('1e-9')
        assert f['actividad_predominante_2023'] == GRUPOS[porcentajes.index(max(porcentajes))]
        assert Decimal(f['participacion_predominante_pct_2023']) == max(porcentajes)


def test_regeneracion_offline_e_independiente_del_orden(copia, tmp_path):
    # El intérprete hijo aborta ante cualquier intento de resolver o conectar a la red.
    (tmp_path / 'sitecustomize.py').write_text(
        "import sys\ndef offline(event, args):\n"
        "    if event.startswith('socket.'): raise RuntimeError(event)\n"
        "sys.addaudithook(offline)\n")
    env = {**os.environ, 'PYTHONPATH': str(tmp_path)}
    salida = tmp_path / 'matriz.csv'
    for invertir in (False, True):
        if invertir:
            for nombre in (ENC, NAC, PC, PIB, CAT):
                guardar(copia / nombre, list(reversed(leer(copia / nombre))))
        proceso = ejecutar(copia, salida, env)
        assert proceso.returncode == 0, proceso.stderr
        assert salida.read_bytes() == PUBLICADA.read_bytes()


@pytest.mark.parametrize('nombre,campo,valor,error', [
    (ENC, None, 'duplicar', 'duplicad'), (NAC, None, 'duplicar', 'duplicad'),
    (PIB, None, 'duplicar', 'duplicad'), (PC, None, 'duplicar', 'duplicad'),
    (CAT, None, 'duplicar', 'duplicad'), (PIB, None, 'quitar', 'cobertura'),
    (ENC, 'depto_id', '1', 'depto_id'), (PC, 'departamento', 'Petén', 'departamento'),
    (ENC, 'anio', '2022', 'anio'), (PIB, 'anio', '2024', 'anio'), (NAC, 'anio', '2022', 'anio'),
    (PC, 'anio', '2024', 'anio'), (ENC, 'unidad', 'fraccion', 'unidad'),
    (PIB, 'unidad', 'quetzales', 'unidad'), (PC, 'unidad', 'millones_de_quetzales', 'unidad'),
    (PIB, 'tipo_precio', 'constantes', 'tipo_precio'),
    (PC, 'tipo_precio', 'volumen_encadenado_2013', 'tipo_precio'),
    (PIB, 'medida', 'valor_agregado', 'medida'), (PIB, 'pib_valor', '1', 'concili'),
    (PC, 'pib_per_capita', 'NaN', 'pib_per_capita'), (ENC, 'valor', '', 'valor'),
    (ENC, 'estado', 'publicable', 'estado'), (ENC, 'estado', 'no_publicable', 'estado'),
    (ENC, 'cv', '31', 'estado'), (ENC, 'n', '29', 'estado'),
    (ENC, 'ic95_inf', '99', 'ic95'), (ENC, 'ponderador', 'Factor2', 'ponderador'),
    (CAT, 'sector_banguat', 'TOTAL', 'sector_banguat'),
    (NAC, 'n', '17522', 'muestra'),
])
def test_rechaza_insumo_invalido_y_preserva_salida(copia, nombre, campo, valor, error):
    filas = leer(copia / nombre)
    if campo:
        filas[0][campo] = valor
    elif valor == 'duplicar':
        filas.append(filas[0])
    else:
        filas.pop(0)
    guardar(copia / nombre, filas)
    salida = copia / 'matriz.csv'
    salida.write_text('salida anterior')
    proceso = ejecutar(copia, salida)
    assert proceso.returncode != 0
    assert error in proceso.stderr.lower()
    assert salida.read_text() == 'salida anterior'


def test_rechaza_cambio_en_el_numero_de_restricciones(copia):
    filas = leer(copia / ENC)
    fila = next(r for r in filas if r['estado'] == 'no_publicable')
    fila.update(cv='20', estado='publicable_con_reserva')
    guardar(copia / ENC, filas)
    resultado = ejecutar(copia, copia / 'matriz.csv')
    assert resultado.returncode != 0 and 'restricciones' in resultado.stderr.lower()


def test_volumen_encadenado_no_afecta_la_matriz(copia):
    filas = leer(copia / PIB)
    for r in filas:
        if r['tipo_precio'] == 'volumen_encadenado_2013':
            r['pib_valor'] = '123456'
    guardar(copia / PIB, filas)
    salida = copia / 'matriz.csv'
    proceso = ejecutar(copia, salida)
    assert proceso.returncode == 0, proceso.stderr
    assert salida.read_bytes() == PUBLICADA.read_bytes()
