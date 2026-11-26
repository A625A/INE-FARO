"""Recalcula el caso M-06 desde las fuentes y comprueba su ficha pública."""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/encovi_2023'
PROCESADOS = ROOT / 'data/processed'


def tasa_puntual_por_departamento(base, evento, ponderador):
    estados = base.assign(positivo=base[ponderador].where(evento, 0))
    sumas = estados.groupby('DEPTO')[[ponderador, 'positivo']].sum()
    return {
        int(depto): Decimal(str(fila.positivo)) * 100 / Decimal(str(fila[ponderador]))
        for depto, fila in sumas.iterrows()
    }


def redondear(valor):
    return valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def test_caso_m06_reproduce_las_cuatro_tasas_y_las_dos_brechas():
    personas, _ = pyreadstat.read_sav(RAW / 'encovi_2023_personas.sav', usecols=[
        'DEPTO', 'PPA03', 'OCUPADOS', 'FORMAL_INFORMAL', 'FACTOR',
    ])
    ocupados = personas[personas.PPA03.ge(15) & personas.OCUPADOS.eq(1)]
    consumo, _ = pyreadstat.read_sav(RAW / 'encovi_2023_agregado_consumo.sav',
                                     usecols=['DEPTO', 'pobreza', 'Factor3'])
    consumo = consumo[consumo.pobreza.isin([1, 2, 3])]
    tasas = {
        'ocupacion_sector_informal': tasa_puntual_por_departamento(
            ocupados, ocupados.FORMAL_INFORMAL.eq(1), 'FACTOR'),
        'pobreza_total': tasa_puntual_por_departamento(
            consumo, consumo.pobreza.isin([1, 2]), 'Factor3'),
    }
    esperado = {
        'ocupacion_sector_informal': ('80.08', '81.06', '0.98', 'brecha_informalidad_pp'),
        'pobreza_total': ('47.75', '90.30', '42.55', 'brecha_pobreza_pp'),
    }

    salida = json.loads((PROCESADOS / 'hallazgos.json').read_text(encoding='utf-8'))
    caso, = [f for f in salida['hallazgos'] if f['id'] == 'R1:2023:04-16']
    evidencia = {(int(f['territorio']), f['indicador']): f for f in caso['evidencias']}
    for indicador, (valor_04, valor_16, diferencia, magnitud) in esperado.items():
        tasa_04, tasa_16 = tasas[indicador][4], tasas[indicador][16]
        assert redondear(tasa_04) == Decimal(valor_04)
        assert redondear(tasa_16) == Decimal(valor_16)
        assert redondear(abs(tasa_16 - tasa_04)) == Decimal(diferencia)
        assert redondear(Decimal(str(caso['magnitudes'][magnitud]))) == Decimal(diferencia)

        for depto, tasa in ((4, tasa_04), (16, tasa_16)):
            ficha = evidencia[depto, indicador]
            assert abs(Decimal(str(ficha['valor'])) - tasa) <= Decimal('0.0000005')
            assert ficha['diagnostico']['estado'] == 'publicable_con_reserva'

    assert caso['robustez']['presentes'] == caso['robustez']['escenarios'] == 7
