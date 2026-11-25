"""Contratos de lectura para los agregados públicos de M-05."""
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from dashboard_utils import INDICADORES, aplicar_precision
from dashboard_utils import MIN_MUESTRA, UMBRAL_PUBLICACION
from scripts.comun import DEPARTAMENTOS as CATALOGO_INE
from scripts.radar_rules.inputs import DIAGNOSTICS, GROUPS, PRECISION, matrix_columns, sector_fields

DEPARTAMENTOS = {f"{codigo:02}": nombre for codigo, nombre in CATALOGO_INE.items()}

NOMBRES_ENCOVI = dict(zip(INDICADORES, (
    'Ocupación en el sector informal', 'Pobreza total', 'Pobreza extrema',
)))
PIB = 'PIB por habitante'
CAMPO_PIB = 'pib_por_habitante_q_2023'
DOMINIOS = ('Urbano Metropolitano', 'Resto Urbano', 'Rural Nacional')
RAMAS_ENEIC = {
    '1': 'Agricultura, ganadería, silvicultura y pesca',
    '2': 'Industrias manufactureras, explotación de minas y canteras y otras actividades industriales',
    '3': 'Construcción',
    '4': 'Comercio al por mayor y al por menor, transporte y almacenamiento, actividades de alojamiento y de servicio de comidas',
    '5': 'Información y comunicación',
    '6': 'Actividades financieras y de seguros',
    '7': 'Actividades inmobiliarias',
    '8': 'Actividades profesionales, científicas, técnicas, y de servicios administrativos y de apoyo',
    '9': 'Actividades de administración pública y defensa, enseñanza, actividades de atención de la salud y asistencia social',
    '10': 'Otras actividades de servicios',
}
MEDIDAS_ENEIC = {
    'tasa_sector_informal': ('Ocupación en el sector informal', 'porcentaje'),
    'media_ingreso': ('Ingreso laboral medio', 'Q/mes'),
    'peso_ocupados': ('Población ocupada', 'personas'),
    'peso_informal': ('Volumen estimado informal', 'personas'),
    'peso_formal': ('Volumen estimado formal', 'personas'),
    'composicion_ocupados_pct': ('Composición de ocupados', 'porcentaje'),
}
PERFILES = {
    'remesas_personas': {
        'recibio_remesas_pct': ('Personas que recibieron remesas', 'Personas con respuesta válida'),
        'monto_remesas_mensual_entre_receptores_q': ('Remesas mensuales por receptor', 'Receptores con tres montos válidos'),
    },
    'negocios_hogares': {
        'hogares_con_negocio_pct': ('Hogares con negocio', 'Hogares con respuesta válida'),
        'negocios_por_hogar_promedio': ('Negocios por hogar', 'Hogares, incluidos los que no declararon negocio'),
        'venta_mensual_por_hogar_con_negocio_q': ('Venta mensual por hogar con negocio', 'Hogares declarantes con detalle disponible'),
        'ganancia_neta_mensual_por_hogar_con_negocio_q': ('Ganancia neta mensual por hogar con negocio', 'Hogares declarantes con detalle disponible'),
    },
    'consumo_per_capita': {
        'consumo_per_capita_mensual_q': ('Agregado de consumo por persona', 'Personas en hogares con agregado de consumo'),
        'gasto_per_capita_mensual_q': ('Gasto por persona', 'Personas en hogares con agregado de consumo'),
        'ayudas_servicios_per_capita_mensual_q': ('Ayudas y servicios por persona', 'Personas en hogares con agregado de consumo'),
    },
}
PRECIOS = {
    'corrientes': 'Precios corrientes',
    'volumen_encadenado_2013': 'Volúmenes encadenados · referencia 2013',
}
ANIOS_VAB = tuple(y for y in range(2013, 2025) if y != 2020)
RESERVA = 'publicable_con_reserva'
RESTRINGIDO = 'no_publicable'


def leer_csv(ruta, columnas, **dtype):
    datos = pd.read_csv(ruta, dtype=dtype)
    faltantes = set(columnas) - set(datos)
    if faltantes:
        raise ValueError(f'{ruta.name}: faltan {", ".join(sorted(faltantes))}.')
    if set(datos) - set(columnas):
        raise ValueError(f'{ruta.name}: el archivo contiene columnas ajenas al contrato público.')
    return datos[list(columnas)].copy()


def comprobar_claves(datos, campos, esperado, fuente):
    claves = list(datos[list(campos)].itertuples(index=False, name=None))
    if len(claves) != len(esperado) or set(claves) != esperado:
        raise ValueError(f'{fuente}: grano o cobertura incompatibles.')


def numericos(datos, campos):
    return datos[list(campos)].apply(pd.to_numeric, errors='coerce')


def cargar_eneic(procesados: Path):
    columnas = ('periodo dimension categoria indicador valor valor_oficial unidad denominador n '
                'n_ocupados cobertura_pct ponderador fuente referencia estado tipo_validacion precision '
                'ic95_inf ic95_sup').split()
    datos = leer_csv(procesados / 'eneic_iv_2025/agregados_publicos.csv', columnas, categoria=str)
    esperado = {('nacional', 'GT', clave) for clave in (
        'tasa_sector_informal', 'media_ingreso', 'peso_ocupados', 'peso_informal', 'peso_formal')}
    esperado.update(('dominio', d, k) for d, k in product(DOMINIOS, ('tasa_sector_informal', 'media_ingreso')))
    esperado.update(('rama_ine', rama, 'composicion_ocupados_pct') for rama in RAMAS_ENEIC)
    comprobar_claves(datos, ('dimension', 'categoria', 'indicador'), esperado, 'ENEIC')
    campos = ['valor', 'valor_oficial', 'denominador', 'n', 'n_ocupados', 'cobertura_pct']
    datos[campos] = numericos(datos, campos)
    montos = datos[datos.unidad.eq('porcentaje')]
    unidades = datos.indicador.map({k: v[1] for k, v in MEDIDAS_ENEIC.items()})
    indirecto = datos.indicador.isin(['peso_informal', 'peso_formal'])
    validacion = datos.tipo_validacion
    if (not datos.periodo.eq('IV-2025').all() or not datos.estado.eq('oficial_conciliado').all()
            or not datos.ponderador.eq('FACTOR').all() or not datos.unidad.eq(unidades).all()
            or not np.isfinite(datos[campos]).all().all() or not montos.valor.between(0, 100).all()
            or not montos.valor_oficial.between(0, 100).all()
            or not datos.denominador.gt(0).all() or not datos.n.gt(0).all()
            or not datos.n.le(datos.n_ocupados).all() or not datos.cobertura_pct.between(0, 100).all()
            or not validacion[indirecto].eq('derivado_conciliacion_indirecta').all()
            or not validacion[~indirecto].eq('contraste_directo_boletin').all()):
        raise ValueError('ENEIC: período, calidad, unidades o valores incompatibles.')
    ic = datos[['ic95_inf', 'ic95_sup']]
    con_ic = ic.notna().any(axis=1)
    limites = numericos(datos.loc[con_ic], ic.columns)
    if (not np.isfinite(limites).all().all()
            or not limites.ic95_inf.le(datos.loc[con_ic, 'valor_oficial']).all()
            or not limites.ic95_sup.ge(datos.loc[con_ic, 'valor_oficial']).all()):
        raise ValueError('ENEIC: intervalos oficiales incoherentes.')
    datos[list(ic)] = numericos(datos, ic.columns)
    return datos


def cargar_matriz(procesados: Path):
    columnas = matrix_columns()
    matriz = leer_csv(procesados / 'matriz_departamental.csv', columnas, depto_id=str)
    comprobar_claves(matriz, ('depto_id', 'anio'), {(d, 2023) for d in DEPARTAMENTOS}, 'M-03')
    if not matriz.departamento.eq(matriz.depto_id.map(DEPARTAMENTOS)).all():
        raise ValueError('M-03: nombres del catálogo departamental incompatibles.')
    bases = ['depto_id', 'departamento', 'anio']
    partes = []
    for indicador in INDICADORES:
        campos = {f'{indicador}_{c}_2023': c for c in DIAGNOSTICS}
        parte = matriz[bases + list(campos)].rename(columns=campos)
        parte = aplicar_precision(parte.assign(
            indicador=indicador, fuente='INE, ENCOVI 2023', unidad='porcentaje', precision=PRECISION,
        ))
        matriz[list(campos)] = parte[list(campos.values())].to_numpy()
        partes.append(parte)
    encovi = pd.concat(partes, ignore_index=True)
    participaciones = [sector_fields(grupo)[1] for grupo in GROUPS]
    importes = [sector_fields(grupo)[0] for grupo in GROUPS]
    campos = [CAMPO_PIB, 'pib_total_millones_q_2023', 'vab_total_millones_q_2023',
              'ipns_millones_q_2023', 'participacion_predominante_pct_2023', *participaciones, *importes]
    matriz[campos] = numericos(matriz, campos)
    if (not np.isfinite(matriz[campos]).all().all() or not matriz[CAMPO_PIB].gt(0).all()
            or not matriz.vab_total_millones_q_2023.gt(0).all()
            or not matriz.actividad_predominante_2023.isin(GROUPS).all()
            or not (matriz[participaciones].ge(0) & matriz[participaciones].le(100)).all().all()):
        raise ValueError('M-03: el perfil productivo contiene valores incompatibles.')
    return matriz, encovi


def cargar_hogares(procesados: Path):
    columnas = ('tabla ambito depto_id departamento anio indicador valor unidad horizonte '
                'ponderador n upm_n cv fuente limite precision estado').split()
    datos = leer_csv(procesados / 'perfiles_hogares.csv', columnas, depto_id=str)
    datos['depto_id'] = datos.depto_id.fillna('')
    territorios = [('nacional', ''), *(('departamental', d) for d in DEPARTAMENTOS)]
    esperado = {(tabla, k, ambito, depto) for tabla, indicadores in PERFILES.items()
                for k in indicadores for ambito, depto in territorios}
    comprobar_claves(datos, ('tabla', 'indicador', 'ambito', 'depto_id'), esperado, 'M-02')
    if not datos.anio.eq(2023).all() or not datos.estado.isin([RESERVA, RESTRINGIDO]).all():
        raise ValueError('M-02: año o estado incompatible.')
    campos = ['valor', 'cv', 'n', 'upm_n']
    datos[campos] = numericos(datos, campos)
    apto = (datos.estado.eq(RESERVA) & datos.n.ge(MIN_MUESTRA)
            & datos.cv.between(0, UMBRAL_PUBLICACION))
    datos.loc[~apto, 'estado'] = RESTRINGIDO
    datos.loc[~apto, ['valor', 'cv']] = pd.NA
    if not np.isfinite(datos.loc[apto, 'valor']).all():
        raise ValueError('M-02: estimación publicable inválida.')
    return datos


def cargar_vab(procesados: Path):
    base = 'anio tipo_precio unidad preliminar revision vab_informal'.split()
    medidas = ('vab_total participacion_informal_pct'.split(),
               'vab_total_grupo composicion_pct participacion_informal_grupo_pct'.split())
    esperadas = set(product(ANIOS_VAB, PRECIOS))
    resultados = []
    for nivel, extras, indicadores in zip(
        ('nacional', 'grupo'), ([], ['grupo_ciiu', 'grupo_nombre']), medidas,
    ):
        datos = leer_csv(procesados / f'vab_informal_{nivel}.csv', base + extras + indicadores)
        claves = ['anio', 'tipo_precio']
        esperadas_nivel = esperadas
        if extras:
            claves.append('grupo_ciiu')
            esperadas_nivel = {(*par, g) for par, g in product(esperadas, GROUPS)}
        comprobar_claves(datos, claves, esperadas_nivel, 'Banguat, VAB informal')
        corrientes = datos.tipo_precio.eq('corrientes')
        medidas_corrientes = numericos(datos.loc[corrientes], indicadores)
        informal = pd.to_numeric(datos.vab_informal, errors='coerce')
        if (not datos.preliminar.eq(datos.anio.isin([2023, 2024])).all()
                or not datos.unidad.eq('millones_de_quetzales').all() or datos.revision.isna().any()
                or datos.loc[~corrientes, indicadores].notna().any().any()
                or not (np.isfinite(informal) & informal.ge(0)).all()
                or not np.isfinite(medidas_corrientes).all().all()
                or not medidas_corrientes[indicadores[0]].gt(0).all()
                or not all(medidas_corrientes[c].between(0, 100).all() for c in indicadores[1:])):
            raise ValueError('Banguat: unidades, cobertura o medidas incompatibles con el tipo de precio.')
        datos['vab_informal'] = informal
        datos[indicadores] = numericos(datos, indicadores)
        resultados.append(datos)
    return tuple(resultados)
