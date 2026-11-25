"""Reproduce evidencia agregada de M-02 frente al commit auditado 9ad12c9.

Ejecutar después de procesar_hogares.py desde cualquier directorio.
Las salidas contienen estimaciones restringidas para revisión interna.
"""
from io import StringIO
from pathlib import Path
import subprocess

import pandas as pd

import procesar_hogares as m

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/auditoria_interna'


def main():
    original = subprocess.check_output(
        ['git', 'show', '9ad12c9:data/processed/perfiles_hogares.csv'],
        cwd=ROOT, text=True)
    antes = pd.read_csv(StringIO(original), keep_default_na=False)
    despues = pd.read_csv(OUT / 'perfiles_hogares.csv', keep_default_na=False)
    claves = ['tabla', 'ambito', 'depto_id', 'indicador']
    comparacion = antes.merge(despues, on=claves,
                             suffixes=('_antes', '_despues'), validate='one_to_one')
    columnas = claves + ['cv_antes', 'cv_despues', 'estado_antes', 'estado_despues']
    comparacion[columnas].to_csv(OUT / 'comparacion_precision.csv', index=False)

    hogares = m.validar_hogares(m.leer(
        m.RAW, 'encovi_2023_hogares.sav', ('NO_HOGAR', 'DEPTO', 'UPM', 'FACTOR')))
    negocios = m.preparar_negocios(
        hogares,
        m.leer(m.RAW, 'encovi_2023_c14sa_negocios_1.sav',
               ('NO_HOGAR', 'P14A01', 'P14A02A')),
        m.leer(m.RAW, 'encovi_2023_c14sa_negocios_2.sav',
               ('NO_HOGAR', 'ID_NEGOCIO', 'P14A13', 'P14A16')))
    ambitos = [('', negocios)] + [
        (f'{d:02}', negocios.loc[negocios.DEPTO.eq(d)]) for d in m.DEPARTAMENTOS]
    filas = []
    for codigo, base in ambitos:
        base = base.loc[base.tiene_negocio]
        diferencia = base.n_negocios - base.n_detallados
        grupos = [('todos', base.tiene_negocio),
                  ('faltan_detalles', diferencia.gt(0)),
                  ('sobran_detalles', diferencia.lt(0)),
                  ('coinciden', diferencia.eq(0))]
        for grupo, mascara in grupos:
            sub = base.loc[mascara]
            filas.append({
                'depto_id': codigo, 'grupo': grupo, 'hogares': len(sub),
                'declarados': sub.n_negocios.sum(),
                'detallados': sub.n_detallados.sum(),
                'declarados_ponderados': (sub.n_negocios * sub.FACTOR).sum(),
                'detallados_ponderados': (sub.n_detallados * sub.FACTOR).sum(),
                'hogares_ponderados': sub.FACTOR.sum(),
                'ventas_observadas': (sub.venta_mensual * sub.FACTOR).sum(),
                'ganancias_observadas': (sub.ganancia_mensual * sub.FACTOR).sum(),
            })
    pd.DataFrame(filas).to_csv(OUT / 'cobertura_negocios.csv', index=False)
    print('Evidencia interna de precisión y cobertura M-02 actualizada.')


if __name__ == '__main__':
    main()
