"""M-01: indicadores ENCOVI 2023 con ponderación y precisión aproximada.

El diseño disponible permite una aproximación DEPARTAMENTO/UPM, no un error
muestral oficial. No modificar los archivos SAV originales.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from comun import DEPARTAMENTOS, escribir_csv

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/encovi_2023'
OUT = ROOT / 'data/processed'
INDICADORES = ('ocupacion_sector_informal', 'pobreza_total', 'pobreza_extrema')
COLUMNAS = ('depto_id', 'departamento', 'anio', 'indicador', 'valor', 'unidad',
            'fuente', 'n', 'upm_n', 'ponderador', 'cv', 'ic95_inf', 'ic95_sup',
            'precision', 'estado')
PRECISION = 'aproximada_depto_upm_sin_estratos_originales'
OFICIALES = {'ocupacion_sector_informal': 70.3, 'pobreza_total': 56.0,
             'pobreza_extrema': 16.2}
POBREZA_OFICIAL_DEPTO = dict(enumerate([
    21.6, 46.4, 38.7, 47.8, 39.2, 74.0, 61.9, 62.1, 44.1, 53.7, 50.9,
    53.7, 81.3, 86.4, 80.1, 90.3, 50.6, 50.5, 52.6, 59.6, 79.9, 74.0,
], start=1))


def estimar_tasa(frame: pd.DataFrame, evento: pd.Series, peso: str,
                 dominio: pd.Series | None = None) -> dict:
    """Razón ponderada con varianza linealizada por UPM dentro de DEPTO.

    El dominio se calcula sobre la muestra completa: las UPM sin casos en el
    dominio contribuyen cero a la varianza, en lugar de desaparecer.
    """
    necesarios = {'DEPTO', 'UPM', peso}
    if not necesarios.issubset(frame.columns):
        raise ValueError(f'Faltan columnas: {sorted(necesarios - set(frame.columns))}')
    if frame.empty or evento.isna().any():
        raise ValueError('Muestra vacía o evento con valores faltantes')
    w = pd.to_numeric(frame[peso], errors='raise').to_numpy(dtype=float)
    if not np.isfinite(w).all() or (w <= 0).any():
        raise ValueError(f'Ponderador inválido: {peso}')
    if frame[['DEPTO', 'UPM']].isna().any().any():
        raise ValueError('Identificadores de diseño incompletos')
    x = (pd.Series(True, index=frame.index) if dominio is None else
         dominio.reindex(frame.index)).to_numpy(dtype=bool)
    y = evento.reindex(frame.index).to_numpy(dtype=bool)
    denominador = float(np.sum(w * x))
    if denominador <= 0:
        raise ValueError('Dominio sin denominador ponderado')
    estimacion = float(np.sum(w * x * y) / denominador)
    z = w * x * (y.astype(float) - estimacion)
    disenio = pd.DataFrame({'DEPTO': frame['DEPTO'].to_numpy(),
                            'UPM': frame['UPM'].to_numpy(), 'z': z})
    psu = disenio.groupby(['DEPTO', 'UPM'], observed=True, sort=False)['z'].sum()
    var_numerador = 0.0
    for _, grupo in psu.groupby(level=0, sort=False):
        valores = grupo.to_numpy(dtype=float)
        m = len(valores)
        if m < 2:
            raise ValueError('No se puede estimar precisión: estrato con una UPM')
        var_numerador += m / (m - 1) * float(np.square(valores - valores.mean()).sum())
    se = float(np.sqrt(var_numerador) / denominador)
    valor = estimacion * 100
    cv = 100 * se / estimacion if estimacion > 0 else float('nan')
    n = int(x.sum())
    upm_n = int(frame.loc[x, ['DEPTO', 'UPM']].drop_duplicates().shape[0])
    publicable = n >= 30 and np.isfinite(cv) and cv <= 30
    return {'valor': round(valor, 6), 'n': n, 'upm_n': upm_n,
            'cv': round(cv, 5) if np.isfinite(cv) else '',
            'ic95_inf': round(max(0, (estimacion - 1.96 * se) * 100), 6),
            'ic95_sup': round(min(100, (estimacion + 1.96 * se) * 100), 6),
            'precision': PRECISION,
            'estado': 'publicable_con_reserva' if publicable else 'no_publicable'}


def cargar_datos(raw: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    import pyreadstat
    p, _ = pyreadstat.read_sav(str(raw / 'encovi_2023_personas.sav'),
          usecols=['DEPTO', 'UPM', 'PPA03', 'OCUPADOS', 'FORMAL_INFORMAL', 'FACTOR', 'AREA'])
    c, _ = pyreadstat.read_sav(str(raw / 'encovi_2023_agregado_consumo.sav'),
          usecols=['NO_HOGAR', 'DEPTO', 'pobreza', 'Factor3'])
    h, _ = pyreadstat.read_sav(str(raw / 'encovi_2023_hogares.sav'),
          usecols=['NO_HOGAR', 'DEPTO', 'UPM'])
    if h.NO_HOGAR.isna().any() or h.NO_HOGAR.duplicated().any():
        raise ValueError('NO_HOGAR duplicado o nulo en Hogares')
    if c.NO_HOGAR.isna().any() or c.NO_HOGAR.duplicated().any():
        raise ValueError('NO_HOGAR duplicado o nulo en Consumo')
    if len(c) != 10930:
        raise ValueError(f'Consumo distinto a la guía ENCOVI: {len(c)}')
    c = c.merge(h.rename(columns={'DEPTO': 'DEPTO_hogar'}), on='NO_HOGAR',
                validate='one_to_one', how='left', indicator=True)
    if not c['_merge'].eq('both').all() or not c.DEPTO.eq(c.DEPTO_hogar).all():
        raise ValueError('Consumo no concilia con Hogares')
    c = c.drop(columns=['DEPTO_hogar', '_merge'])
    ocupados = p.loc[p.PPA03.ge(15) & p.OCUPADOS.eq(1)].copy()
    if not ocupados.FORMAL_INFORMAL.isin([1, 2]).all():
        raise ValueError('Ocupados sin clasificación formal/informal válida')
    if not c.pobreza.isin([1, 2, 3]).all():
        raise ValueError('Pobreza contiene códigos ajenos a 1/2/3')
    for nombre, base in [('ocupados', ocupados), ('consumo', c)]:
        if not base.DEPTO.isin(range(1, 23)).all():
            raise ValueError(f'Departamentos inválidos en {nombre}')
    return ocupados, c


def crear_indicadores(ocupados: pd.DataFrame,
                      consumo: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    poblaciones = {
        'ocupacion_sector_informal': (ocupados, ocupados.FORMAL_INFORMAL.eq(1), 'FACTOR'),
        'pobreza_total': (consumo, consumo.pobreza.isin([1, 2]), 'Factor3'),
        'pobreza_extrema': (consumo, consumo.pobreza.eq(1), 'Factor3'),
    }
    departamentales, nacionales = [], []
    for nombre, (base, evento, peso) in poblaciones.items():
        nacional = estimar_tasa(base, evento, peso)
        if abs(nacional['valor'] - OFICIALES[nombre]) > 0.11:
            raise ValueError(f'{nombre} no reproduce la referencia oficial: {nacional["valor"]}')
        nacionales.append({'ambito': 'nacional', 'anio': 2023, 'indicador': nombre,
                           'ponderador': peso, **nacional})
        for depto, etiqueta in DEPARTAMENTOS.items():
            mask = base.DEPTO.eq(depto)
            resultado = estimar_tasa(base.loc[mask], evento.loc[mask], peso)
            if nombre == 'pobreza_total' and abs(resultado['valor'] - POBREZA_OFICIAL_DEPTO[depto]) > 0.15:
                raise ValueError(f'Pobreza de {etiqueta} no coincide con tabla oficial')
            departamentales.append({
                'depto_id': f'{depto:02}', 'departamento': etiqueta, 'anio': 2023,
                'indicador': nombre, 'unidad': 'porcentaje', 'fuente': 'ENCOVI 2023 - INE',
                'ponderador': peso, **resultado,
            })
    for area, nombre in [(1, 'ocupacion_sector_informal_urbana'),
                         (2, 'ocupacion_sector_informal_rural')]:
        tasa_area = estimar_tasa(ocupados, ocupados.FORMAL_INFORMAL.eq(1),
                                'FACTOR', ocupados.AREA.eq(area))
        referencia = 61.3 if area == 1 else 83.0
        if abs(tasa_area['valor'] - referencia) > 0.11:
            raise ValueError(f'{nombre} no reproduce referencia: {tasa_area["valor"]}')
        nacionales.append({'ambito': 'area', 'area': 'urbana' if area == 1 else 'rural',
                           'anio': 2023, 'indicador': nombre, 'ponderador': 'FACTOR',
                           **tasa_area})
    if len(departamentales) != 66 or len({(x['depto_id'], x['indicador']) for x in departamentales}) != 66:
        raise ValueError('La tabla departamental no tiene 22 x 3 claves únicas')
    return departamentales, nacionales


def main(raw: Path = RAW, out: Path = OUT) -> None:
    ocupados, consumo = cargar_datos(raw)
    departamentales, nacionales = crear_indicadores(ocupados, consumo)
    escribir_csv(out / 'indicadores_encovi_2023.csv', departamentales, COLUMNAS)
    escribir_csv(out / 'indicadores_encovi_nacional_2023.csv', nacionales,
                 ('ambito', 'area', 'anio', 'indicador', 'ponderador', 'valor', 'n',
                  'upm_n', 'cv', 'ic95_inf', 'ic95_sup', 'precision', 'estado'))
    print('M-01: 66 filas departamentales + 5 referencias nacionales/de área.')
    for fila in nacionales:
        print(f"{fila['indicador']}: {fila['valor']:.3f}% (CV aprox. {fila['cv']}%)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='M-01 ENCOVI 2023')
    parser.add_argument('--input-dir', type=Path, default=RAW)
    parser.add_argument('--output-dir', type=Path, default=OUT)
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)