"""Lectura y comprobación de las tablas agregadas que consume M-05."""
from pathlib import Path

import pandas as pd

INDICADORES = ('ocupacion_sector_informal', 'pobreza_total', 'pobreza_extrema')


COLUMNAS_ENCOVI = (
    'depto_id', 'departamento', 'anio', 'indicador', 'valor', 'unidad', 'fuente',
    'n', 'upm_n', 'ponderador', 'cv', 'ic95_inf', 'ic95_sup', 'precision', 'estado',
)


def cargar_pib(procesados: Path) -> pd.DataFrame:
    """Carga el PIB por habitante de los 22 departamentos."""
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
    return pib.sort_values('depto_id').reset_index(drop=True)


def cargar_encovi(procesados: Path, pib: pd.DataFrame) -> pd.DataFrame | None:
    """Devuelve solo estimaciones publicables, con sus metadatos de precisión."""
    ruta = procesados / 'indicadores_encovi_2023.csv'
    if not ruta.exists():
        return None
    encovi = pd.read_csv(ruta, dtype={'depto_id': str})
    faltantes = set(COLUMNAS_ENCOVI) - set(encovi)
    if faltantes:
        raise ValueError(f'ENCOVI sin columnas: {sorted(faltantes)}')
    claves = ['depto_id', 'indicador']
    esperadas = {(depto, indicador) for depto in pib.depto_id for indicador in INDICADORES}
    if (not encovi.anio.eq(2023).all() or encovi.duplicated(claves).any()
            or set(encovi[claves].itertuples(index=False, name=None)) != esperadas):
        raise ValueError('ENCOVI debe tener 22 departamentos por tres indicadores únicos de 2023')
    if not encovi.estado.isin(['publicable_con_reserva', 'no_publicable']).all():
        raise ValueError('ENCOVI contiene estados de publicación desconocidos')
    publicables = encovi.loc[encovi.estado.eq('publicable_con_reserva'), list(COLUMNAS_ENCOVI)]
    if (not publicables.unidad.eq('porcentaje').all()
            or not pd.to_numeric(publicables.valor, errors='coerce').between(0, 100).all()):
        raise ValueError('ENCOVI contiene unidades o tasas inválidas en filas publicables')
    return publicables
