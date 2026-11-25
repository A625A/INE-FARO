"""Lectura y comprobación de las tablas agregadas que consume M-05."""
from pathlib import Path

import pandas as pd

INDICADORES = ('ocupacion_sector_informal', 'pobreza_total', 'pobreza_extrema')


def cargar_tablero(procesados: Path) -> tuple[pd.DataFrame, bool]:
    """Devuelve 22 departamentos. Sin M-01, muestra sólo el PIB real disponible."""
    pib_path = procesados / 'pib_per_capita.csv'
    if not pib_path.exists():
        raise FileNotFoundError('Falta data/processed/pib_per_capita.csv (I-04).')
    pib = pd.read_csv(pib_path, dtype={'depto_id': str})
    necesarias = {'depto_id', 'departamento', 'anio', 'pib_per_capita', 'tipo_precio', 'unidad'}
    if not necesarias.issubset(pib):
        raise ValueError(f'PIB sin columnas: {sorted(necesarias - set(pib))}')
    pib = pib.loc[pib.anio.eq(2023) & pib.tipo_precio.eq('corrientes')].copy()
    if (len(pib) != 22 or pib.depto_id.nunique() != 22 or pib.depto_id.duplicated().any()
            or set(pib.depto_id) != {f'{i:02}' for i in range(1, 23)}):
        raise ValueError('PIB per cápita debe tener exactamente los 22 departamentos de 2023')
    if not pib.unidad.eq('quetzales_por_habitante').all():
        raise ValueError('PIB per cápita tiene unidades inesperadas')
    if pib.pib_per_capita.isna().any() or not pib.pib_per_capita.gt(0).all():
        raise ValueError('PIB contiene valores faltantes o no positivos')
    columnas = ['depto_id', 'departamento', 'pib_per_capita']
    tabla = pib[columnas].copy()
    encovi_path = procesados / 'indicadores_encovi_2023.csv'
    if not encovi_path.exists():
        return tabla.sort_values('depto_id').reset_index(drop=True), False
    encovi = pd.read_csv(encovi_path, dtype={'depto_id': str})
    requeridas = {'depto_id', 'anio', 'indicador', 'valor', 'unidad', 'estado', 'cv'}
    if not requeridas.issubset(encovi):
        raise ValueError(f'ENCOVI sin columnas: {sorted(requeridas - set(encovi))}')
    encovi = encovi[encovi.anio.eq(2023) & encovi.indicador.isin(INDICADORES)].copy()
    claves = set(zip(encovi.depto_id, encovi.indicador))
    if len(encovi) != 66 or len(claves) != 66 or {x[0] for x in claves} != set(tabla.depto_id):
        raise ValueError('ENCOVI debe tener 22 departamentos por tres indicadores únicos')
    if not encovi.unidad.eq('porcentaje').all() or encovi.valor.isna().any() or not encovi.valor.between(0, 100).all():
        raise ValueError('ENCOVI contiene unidades o tasas inválidas')
    if not encovi.estado.eq('publicable_con_reserva').all():
        raise ValueError('ENCOVI contiene indicadores no publicables; revisar la precisión')
    valores = encovi.pivot(index='depto_id', columns='indicador', values='valor').reset_index()
    tabla = tabla.merge(valores, on='depto_id', how='left', validate='one_to_one')
    if tabla[list(INDICADORES)].isna().any().any():
        raise ValueError('Faltan valores ENCOVI en algún departamento')
    return tabla.sort_values('depto_id').reset_index(drop=True), True