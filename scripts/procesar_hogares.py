"""M-02: perfiles descriptivos de remesas, negocios y consumo ENCOVI 2023."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from calcular_indicadores_encovi import estimar_tasa
from comun import DEPARTAMENTOS, escribir_csv

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/encovi_2023'
OUT = ROOT / 'data/processed'
PRECISION = 'aproximada_depto_upm_sin_estratos_originales'
COLUMNAS = ('tabla', 'ambito', 'depto_id', 'departamento', 'anio', 'indicador',
            'valor', 'unidad', 'horizonte', 'ponderador', 'n', 'upm_n', 'cv',
            'fuente', 'limite', 'precision', 'estado')


def leer(raw: Path, nombre: str, columnas: tuple[str, ...]) -> pd.DataFrame:
    import pyreadstat
    frame, _ = pyreadstat.read_sav(str(raw / nombre), usecols=list(columnas))
    return frame


def validar_hogares(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.NO_HOGAR.isna().any() or frame.NO_HOGAR.duplicated().any():
        raise ValueError('NO_HOGAR duplicado o nulo en Hogares')
    if not frame.DEPTO.isin(range(1, 23)).all():
        raise ValueError('DEPTO fuera de 01-22 en Hogares')
    if frame.UPM.isna().any() or not frame.FACTOR.gt(0).all():
        raise ValueError('UPM o FACTOR inválido en Hogares')
    return frame


def validar_remesas(frame: pd.DataFrame) -> pd.DataFrame:
    necesarios = {'DEPTO', 'UPM', 'P11C01', 'P11C02B', 'P11C03B', 'P11C04B', 'FACTOR'}
    if not necesarios.issubset(frame.columns):
        raise ValueError(f'Faltan columnas de remesas: {sorted(necesarios - set(frame.columns))}')
    respuesta = frame.loc[frame.P11C01.notna()].copy()
    if not respuesta.P11C01.isin([1, 2]).all():
        raise ValueError('P11C01 contiene códigos ajenos a 1/2')
    receptores = respuesta.loc[respuesta.P11C01.eq(1)]
    columnas_monto = ['P11C02B', 'P11C03B', 'P11C04B']
    if not receptores[columnas_monto].notna().all().all():
        raise ValueError('Receptor de remesas sin los tres montos mensuales')
    if not receptores[columnas_monto].ge(0).all().all():
        raise ValueError('Monto de remesas negativo')
    if not respuesta.FACTOR.gt(0).all():
        raise ValueError('FACTOR inválido en personas')
    respuesta['recibio_remesas'] = respuesta.P11C01.eq(1)
    respuesta['monto_mensual'] = respuesta[columnas_monto].sum(axis=1) / 3
    return respuesta


def validar_negocios_uno(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.NO_HOGAR.isna().any() or frame.NO_HOGAR.duplicated().any():
        raise ValueError('NO_HOGAR duplicado o nulo en Negocios.1')
    if not frame.P14A01.isin([1, 2]).all():
        raise ValueError('P14A01 contiene códigos ajenos a 1/2')
    con_negocio = frame.loc[frame.P14A01.eq(1)]
    if not con_negocio.P14A02A.notna().all() or not con_negocio.P14A02A.ge(1).all():
        raise ValueError('Hogar con negocio sin P14A02A válido')
    return frame


def validar_negocios_dos(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.duplicated(['NO_HOGAR', 'ID_NEGOCIO']).any():
        raise ValueError('Clave NO_HOGAR/ID_NEGOCIO duplicada en Negocios.2')
    if frame[['NO_HOGAR', 'ID_NEGOCIO', 'P14A13', 'P14A16']].isna().any().any():
        raise ValueError('Datos incompletos en Negocios.2')
    if not frame.P14A13.ge(0).all():
        raise ValueError('Venta mensual negativa en Negocios.2')
    return frame


def preparar_negocios(hogares: pd.DataFrame, uno: pd.DataFrame,
                      dos: pd.DataFrame) -> pd.DataFrame:
    uno = validar_negocios_uno(uno)
    dos = validar_negocios_dos(dos)
    base = hogares.merge(uno, on='NO_HOGAR', how='left', validate='one_to_one',
                         indicator=True)
    if not base['_merge'].eq('both').all():
        raise ValueError('Negocios.1 no concilia uno a uno con Hogares')
    base = base.drop(columns='_merge')
    base['tiene_negocio'] = base.P14A01.eq(1)
    base['n_negocios'] = base.P14A02A.where(base.tiene_negocio).fillna(0)
    agregado = dos.groupby('NO_HOGAR', as_index=False).agg(
        venta_mensual=('P14A13', 'sum'), ganancia_mensual=('P14A16', 'sum'))
    if not agregado.NO_HOGAR.isin(base.NO_HOGAR).all():
        raise ValueError('Negocios.2 contiene NO_HOGAR huérfano')
    base = base.merge(agregado, on='NO_HOGAR', how='left', validate='one_to_one')
    if (base.tiene_negocio & base.venta_mensual.isna()).any():
        raise ValueError('Hogar con negocio sin detalle en Negocios.2')
    if (~base.tiene_negocio & base.venta_mensual.notna()).any():
        raise ValueError('Negocios.2 contiene hogar sin P14A01=1')
    base.loc[~base.tiene_negocio, ['venta_mensual', 'ganancia_mensual']] = 0.0
    return base


def preparar_consumo(hogares: pd.DataFrame, consumo: pd.DataFrame) -> pd.DataFrame:
    columnas = ['NO_HOGAR', 'DEPTO', 'Factor3', 'agreg3', 'gasto3', 'ayuda3']
    if consumo.NO_HOGAR.isna().any() or consumo.NO_HOGAR.duplicated().any():
        raise ValueError('NO_HOGAR duplicado o nulo en Agregado.Consumo')
    if not consumo.Factor3.gt(0).all():
        raise ValueError('Factor3 inválido en Agregado.Consumo')
    if not consumo[['agreg3', 'gasto3', 'ayuda3']].notna().all().all():
        raise ValueError('Agregado de consumo incompleto')
    if not consumo[['agreg3', 'gasto3', 'ayuda3']].ge(0).all().all():
        raise ValueError('Agregado de consumo con valores negativos')
    base = consumo.merge(hogares.rename(columns={'DEPTO': 'DEPTO_hogar'}),
                         on='NO_HOGAR', how='left', validate='one_to_one',
                         indicator=True)
    if not base['_merge'].eq('both').all() or not base.DEPTO.eq(base.DEPTO_hogar).all():
        raise ValueError('Consumo no concilia uno a uno con Hogares')
    return base.drop(columns=['DEPTO_hogar', '_merge'])


def estimar_media(frame: pd.DataFrame, valores: pd.Series, peso: str) -> dict:
    necesarios = {'DEPTO', 'UPM', peso}
    if not necesarios.issubset(frame.columns):
        raise ValueError(f'Faltan columnas: {sorted(necesarios - set(frame.columns))}')
    y = pd.to_numeric(valores.reindex(frame.index), errors='raise')
    valido = y.notna()
    base = frame.loc[valido]
    y = y.loc[valido]
    if base.empty:
        raise ValueError('Muestra vacía para estimar media')
    w = pd.to_numeric(base[peso], errors='raise').to_numpy(dtype=float)
    if not np.isfinite(w).all() or not (w > 0).all():
        raise ValueError(f'Ponderador inválido: {peso}')
    if base[['DEPTO', 'UPM']].isna().any().any():
        raise ValueError('Identificadores de diseño incompletos')
    media = float(np.sum(w * y.to_numpy(dtype=float)) / np.sum(w))
    z = w * (y.to_numpy(dtype=float) - media)
    disenio = pd.DataFrame({'DEPTO': base.DEPTO.to_numpy(),
                            'UPM': base.UPM.to_numpy(), 'z': z})
    psu = disenio.groupby(['DEPTO', 'UPM'], observed=True, sort=False)['z'].sum()
    suficiente = True
    var_numerador = 0.0
    for _, grupo in psu.groupby(level=0, sort=False):
        valores_grupo = grupo.to_numpy(dtype=float)
        if len(valores_grupo) < 2:
            suficiente = False
            continue
        m = len(valores_grupo)
        var_numerador += m / (m - 1) * float(np.square(valores_grupo - valores_grupo.mean()).sum())
    se = float(np.sqrt(var_numerador) / np.sum(w)) if suficiente else float('nan')
    cv = 100 * se / media if media > 0 and np.isfinite(se) else float('nan')
    n = int(len(y))
    upm_n = int(base[['DEPTO', 'UPM']].drop_duplicates().shape[0])
    publicable = n >= 30 and np.isfinite(cv) and cv <= 30
    return {'valor': round(media, 6), 'n': n, 'upm_n': upm_n,
            'cv': round(cv, 5) if np.isfinite(cv) else '',
            'precision': PRECISION,
            'estado': 'publicable_con_reserva' if publicable else 'no_publicable'}


def fila(ambito: str, depto_id: str, departamento: str,
         estimacion: dict, indicador: str, unidad: str, horizonte: str,
         ponderador: str, fuente: str, limite: str, tabla: str) -> dict:
    return {'tabla': tabla, 'ambito': ambito, 'depto_id': depto_id,
            'departamento': departamento, 'anio': 2023, 'indicador': indicador,
            'valor': estimacion['valor'], 'unidad': unidad, 'horizonte': horizonte,
            'ponderador': ponderador, 'n': estimacion['n'],
            'upm_n': estimacion['upm_n'], 'cv': estimacion['cv'],
            'fuente': fuente, 'limite': limite,
            'precision': estimacion['precision'], 'estado': estimacion['estado']}


def generar(base: pd.DataFrame, estimador, meta: dict) -> list[dict]:
    filas = [fila('nacional', '', '', estimador(base), **meta)]
    for codigo, nombre in DEPARTAMENTOS.items():
        sub = base.loc[base.DEPTO.eq(codigo)]
        if sub.empty:
            raise ValueError(f'Sin observaciones para {nombre}')
        filas.append(fila('departamental', f'{codigo:02}', nombre,
                          estimador(sub), **meta))
    return filas


def construir_filas(personas: pd.DataFrame, negocios: pd.DataFrame,
                    consumo: pd.DataFrame) -> list[dict]:
    receptores = personas.loc[personas.recibio_remesas]
    con_negocio = negocios.loc[negocios.tiene_negocio]
    especificaciones = [
        (personas,
         lambda b: estimar_tasa(b, b.recibio_remesas, 'FACTOR'),
         {'tabla': 'remesas_personas', 'indicador': 'recibio_remesas_pct',
          'unidad': 'porcentaje', 'horizonte': 'ultimos_3_meses',
          'ponderador': 'FACTOR',
          'fuente': 'ENCOVI 2023 - personas P11C01',
          'limite': 'Universo observado con respuesta; no anualizado.'}),
        (receptores,
         lambda b: estimar_media(b, b.monto_mensual, 'FACTOR'),
         {'tabla': 'remesas_personas',
          'indicador': 'monto_remesas_mensual_entre_receptores_q',
          'unidad': 'quetzales por persona al mes', 'horizonte': 'promedio_ultimos_3_meses',
          'ponderador': 'FACTOR',
          'fuente': 'ENCOVI 2023 - personas P11C01/P11C02B-P11C04B',
          'limite': 'Solo receptores con tres montos; no explica PIB ni consumo.'}),
        (negocios,
         lambda b: estimar_tasa(b, b.tiene_negocio, 'FACTOR'),
         {'tabla': 'negocios_hogares', 'indicador': 'hogares_con_negocio_pct',
          'unidad': 'porcentaje', 'horizonte': 'actual',
          'ponderador': 'FACTOR',
          'fuente': 'ENCOVI 2023 - hogares P14A01',
          'limite': 'Negocio familiar del hogar; no equivale a DINESE.'}),
        (negocios,
         lambda b: estimar_media(b, b.n_negocios, 'FACTOR'),
         {'tabla': 'negocios_hogares', 'indicador': 'negocios_por_hogar_promedio',
          'unidad': 'negocios por hogar', 'horizonte': 'actual',
          'ponderador': 'FACTOR',
          'fuente': 'ENCOVI 2023 - hogares P14A01/P14A02A',
          'limite': 'P14A02A vacío se trata como 0 cuando P14A01=2.'}),
        (con_negocio,
         lambda b: estimar_media(b, b.venta_mensual, 'FACTOR'),
         {'tabla': 'negocios_hogares', 'indicador': 'venta_mensual_por_hogar_con_negocio_q',
          'unidad': 'quetzales por hogar al mes', 'horizonte': 'mensual',
          'ponderador': 'FACTOR',
          'fuente': 'ENCOVI 2023 - negocios P14A13',
          'limite': 'Suma de negocios del hogar; no es PIB ni venta DINESE.'}),
        (con_negocio,
         lambda b: estimar_media(b, b.ganancia_mensual, 'FACTOR'),
         {'tabla': 'negocios_hogares',
          'indicador': 'ganancia_neta_mensual_por_hogar_con_negocio_q',
          'unidad': 'quetzales por hogar al mes', 'horizonte': 'mensual',
          'ponderador': 'FACTOR',
          'fuente': 'ENCOVI 2023 - negocios P14A16',
          'limite': 'Puede ser negativa; no se recorta ni se anualiza.'}),
        (consumo,
         lambda b: estimar_media(b, b.agreg3, 'Factor3'),
         {'tabla': 'consumo_per_capita',
          'indicador': 'consumo_per_capita_mensual_q',
          'unidad': 'quetzales por persona al mes', 'horizonte': 'octubre_2023',
          'ponderador': 'Factor3',
          'fuente': 'ENCOVI 2023 - agregado de consumo agreg3',
          'limite': 'Consumo per cápita; no es ingreso ni PIB.'}),
        (consumo,
         lambda b: estimar_media(b, b.gasto3, 'Factor3'),
         {'tabla': 'consumo_per_capita', 'indicador': 'gasto_per_capita_mensual_q',
          'unidad': 'quetzales por persona al mes', 'horizonte': 'octubre_2023',
          'ponderador': 'Factor3',
          'fuente': 'ENCOVI 2023 - agregado de consumo gasto3',
          'limite': 'Componente de gasto; no se suma con otras medidas.'}),
        (consumo,
         lambda b: estimar_media(b, b.ayuda3, 'Factor3'),
         {'tabla': 'consumo_per_capita',
          'indicador': 'ayudas_servicios_per_capita_mensual_q',
          'unidad': 'quetzales por persona al mes', 'horizonte': 'octubre_2023',
          'ponderador': 'Factor3',
          'fuente': 'ENCOVI 2023 - agregado de consumo ayuda3',
          'limite': 'Servicios legales y otros; no es remesa ni ingreso laboral.'}),
    ]
    filas = []
    for base, estimador, meta in especificaciones:
        filas.extend(generar(base, estimador, meta))
    if len(filas) != 207:
        raise ValueError(f'Se esperaban 207 filas; se generaron {len(filas)}')
    claves = {(f['tabla'], f['ambito'], f['depto_id'], f['indicador']) for f in filas}
    if len(claves) != len(filas):
        raise ValueError('Claves duplicadas en perfiles_hogares')
    return filas


def main(raw: Path = RAW, out: Path = OUT) -> None:
    hogares = validar_hogares(leer(raw, 'encovi_2023_hogares.sav',
                                   ('NO_HOGAR', 'DEPTO', 'UPM', 'FACTOR')))
    personas = validar_remesas(leer(raw, 'encovi_2023_personas.sav',
                                    ('DEPTO', 'UPM', 'P11C01', 'P11C02B',
                                     'P11C03B', 'P11C04B', 'FACTOR')))
    negocios = preparar_negocios(
        hogares,
        leer(raw, 'encovi_2023_c14sa_negocios_1.sav',
             ('NO_HOGAR', 'P14A01', 'P14A02A')),
        leer(raw, 'encovi_2023_c14sa_negocios_2.sav',
             ('NO_HOGAR', 'ID_NEGOCIO', 'P14A13', 'P14A16')))
    consumo = preparar_consumo(hogares, leer(raw, 'encovi_2023_agregado_consumo.sav',
                                             ('NO_HOGAR', 'DEPTO', 'Factor3',
                                              'agreg3', 'gasto3', 'ayuda3')))
    filas = construir_filas(personas, negocios, consumo)
    escribir_csv(out / 'perfiles_hogares.csv', filas, COLUMNAS)
    print('M-02: 3 tablas, 9 indicadores, 23 ambitos, 207 filas.')
    for fila_nacional in filas:
        if fila_nacional['ambito'] == 'nacional':
            print(f"{fila_nacional['indicador']}: {fila_nacional['valor']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='M-02 hogares, negocios y remesas ENCOVI 2023')
    parser.add_argument('--input-dir', type=Path, default=RAW)
    parser.add_argument('--output-dir', type=Path, default=OUT)
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
