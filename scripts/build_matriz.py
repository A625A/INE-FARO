"""Construye el contrato departamental M-03 a partir de agregados locales de 2023."""
import argparse
import csv
from itertools import product
from math import fsum, isfinite
from pathlib import Path
from tempfile import TemporaryDirectory

from comun import DEPARTAMENTOS, ROOT, SECCIONES_CIIU, escribir_csv

ANIO = '2023'
DEPTOS = {f'{i:02}': nombre for i, nombre in DEPARTAMENTOS.items()}
PESOS = {'ocupacion_sector_informal': 'FACTOR', 'pobreza_total': 'Factor3',
         'pobreza_extrema': 'Factor3'}
CAMPOS = ('valor', 'ic95_inf', 'ic95_sup', 'cv', 'n', 'upm_n', 'ponderador', 'estado')
PUBLICABLE = 'publicable_con_reserva'
PRECISION = 'aproximada_depto_upm_sin_estratos_originales'
BANGUAT = 'https://banguat.gob.gt/sites/default/files/banguat/Publica/PIB_Regional/'
TOTAL = BANGUAT + '5_PIB_total_por_departamento.xlsx'
ACTIVIDADES = BANGUAT + '7_Resultados_por_actividad_economica_en_departamentos.xlsx'
PER_CAPITA = BANGUAT + '8_PIB_Per_Capita_por_departamento.xlsx'


def exigir(fila, campo, esperado):
    if fila[campo] != esperado:
        raise ValueError(f"{campo}={fila[campo]!r}, se esperaba {esperado!r}")


def indice(ruta, clave, campos):
    """Carga sin inferencia de tipos y rechaza claves ambiguas antes del cruce."""
    resultado = {}
    with ruta.open(encoding='utf-8', newline='') as archivo:
        lector = csv.DictReader(archivo)
        cabecera = lector.fieldnames or []
        faltantes = set((*clave, *campos)) - set(cabecera)
        if faltantes or len(set(cabecera)) != len(cabecera):
            raise ValueError(f'{ruta.name}: cabecera inválida, faltan {sorted(faltantes)}')
        for fila in lector:
            if None in fila or None in fila.values():
                raise ValueError(f'{ruta.name}:{lector.line_num}: fila incompleta o con campos extra')
            if 'anio' in campos:
                exigir(fila, 'anio', ANIO)
            if 'depto_id' in clave:
                codigo = fila['depto_id']
                if codigo not in DEPTOS:
                    raise ValueError(f'{ruta.name}: depto_id inválido {codigo!r}')
                exigir(fila, 'departamento', DEPTOS[codigo])
            llave = tuple(fila[c] for c in clave)
            if llave in resultado:
                raise ValueError(f'{ruta.name}: clave duplicada {llave}')
            resultado[llave] = fila
    return resultado


def cobertura(indice_filas, esperadas, nombre):
    esperadas = set(esperadas)
    if indice_filas.keys() != esperadas:
        raise ValueError(f'{nombre}: cobertura incorrecta, faltan {sorted(esperadas - indice_filas.keys())}, '
                         f'sobran {sorted(indice_filas.keys() - esperadas)}')


def numero(fila, campo):
    try:
        valor = float(fila[campo])
    except ValueError as exc:
        raise ValueError(f'{campo} inválido: {fila[campo]!r}') from exc
    if not isfinite(valor) or valor < 0:
        raise ValueError(f'{campo} fuera de rango: {valor}')
    return valor


def validar_estimacion(fila, peso):
    exigir(fila, 'ponderador', peso)
    exigir(fila, 'precision', PRECISION)
    n, upm = int(fila['n']), int(fila['upm_n'])
    valor = numero(fila, 'valor')
    if not numero(fila, 'ic95_inf') <= valor <= numero(fila, 'ic95_sup') <= 100:
        raise ValueError('ic95 incompatible con el valor o el rango porcentual')
    # M-01 deja el CV vacío cuando la estimación es cero.
    cv = None if fila['cv'] == '' and valor == 0 else numero(fila, 'cv')
    publicable = n >= 30 and cv is not None and cv <= 30
    exigir(fila, 'estado', PUBLICABLE if publicable else 'no_publicable')
    if not 1 <= upm <= n:
        raise ValueError(f'Muestra incoherente: n={n}, upm_n={upm}')


def cargar_encovi(procesados):
    diagnostico = (*CAMPOS, 'precision', 'anio')
    enc = indice(procesados / 'indicadores_encovi_2023.csv', ('depto_id', 'indicador'),
                 (*diagnostico, 'departamento', 'unidad', 'fuente'))
    cobertura(enc, product(DEPTOS, PESOS), 'ENCOVI departamental')
    restringidas = 0
    for (_, indicador), fila in enc.items():
        exigir(fila, 'unidad', 'porcentaje')
        exigir(fila, 'fuente', 'ENCOVI 2023 - INE')
        validar_estimacion(fila, PESOS[indicador])
        if fila['estado'] != PUBLICABLE:
            if indicador != 'pobreza_extrema':
                raise ValueError(f'{indicador}: falta un valor crítico publicable')
            restringidas += 1
    if restringidas != 5:
        raise ValueError(f'Se esperaban cinco restricciones de pobreza extrema, hay {restringidas}')

    nacional = indice(procesados / 'indicadores_encovi_nacional_2023.csv',
                      ('ambito', 'area', 'indicador'), diagnostico)
    pesos_control = {('nacional', '', ind): peso for ind, peso in PESOS.items()}
    for area in ('urbana', 'rural'):
        pesos_control['area', area, 'ocupacion_sector_informal_' + area] = 'FACTOR'
    cobertura(nacional, pesos_control, 'ENCOVI nacional y por área')
    for llave, fila in nacional.items():
        validar_estimacion(fila, pesos_control[llave])
        ambito, _, indicador = llave
        if ambito == 'nacional':
            muestra = sum(int(enc[d, indicador]['n']) for d in DEPTOS)
            if muestra != int(fila['n']):
                raise ValueError(f'Muestra departamental y nacional difieren para {indicador}')
    return enc


def cargar_grupos(ruta):
    catalogo = indice(ruta, ('seccion_codigo',), ('seccion', 'sector_banguat'))
    cobertura(catalogo, ((s,) for s in SECCIONES_CIIU), 'catálogo CIIU')
    grupos = []
    for seccion, etiqueta in SECCIONES_CIIU.items():
        fila = catalogo[seccion,]
        exigir(fila, 'seccion', etiqueta)
        grupo = fila['sector_banguat']
        esperado = 'D-E' if seccion in 'DE' else 'R-S-T-U' if seccion in 'RSTU' else seccion
        exigir(fila, 'sector_banguat', esperado)
        if grupo not in grupos:
            grupos.append(grupo)
    return grupos


def cargar_banguat(procesados, grupos):
    comunes = ('anio', 'departamento', 'unidad', 'fuente')
    pib = indice(procesados / 'pib_departamental.csv', ('depto_id', 'sector', 'tipo_precio'),
                 (*comunes, 'medida', 'pib_valor'))
    nominal = {}
    for (d, sector, precio), fila in pib.items():
        if precio == 'volumen_encadenado_2013':
            continue
        exigir(fila, 'tipo_precio', 'corrientes')
        exigir(fila, 'unidad', 'millones_de_quetzales')
        medida = {'TOTAL': 'pib_total', 'IPNS': 'impuestos_netos'}.get(sector, 'valor_agregado')
        exigir(fila, 'medida', medida)
        exigir(fila, 'fuente', TOTAL if sector == 'TOTAL' else ACTIVIDADES)
        numero(fila, 'pib_valor')
        nominal[d, sector] = fila['pib_valor']
    cobertura(nominal, product(DEPTOS, (*grupos, 'IPNS', 'TOTAL')), 'PIB corriente')
    pc = indice(procesados / 'pib_per_capita.csv', ('depto_id',),
                (*comunes, 'tipo_precio', 'pib_per_capita'))
    cobertura(pc, ((d,) for d in DEPTOS), 'PIB por habitante')
    for fila in pc.values():
        exigir(fila, 'tipo_precio', 'corrientes')
        exigir(fila, 'unidad', 'quetzales_por_habitante')
        exigir(fila, 'fuente', PER_CAPITA)
        numero(fila, 'pib_per_capita')
    return nominal, pc


def perfil_productivo(d, grupos, nominal, per_capita):
    valores = {g: float(nominal[d, g]) for g in grupos}
    vab = fsum(valores.values())
    if vab <= 0:
        raise ValueError(f'{d}: denominador VAB total nulo')
    if abs(float(nominal[d, 'TOTAL']) - vab - float(nominal[d, 'IPNS'])) > 1e-6:
        raise ValueError(f'{d}: falla la conciliación nominal PIB = VAB + IPNS')
    perfil = {'pib_total_millones_q_2023': nominal[d, 'TOTAL'],
              'pib_por_habitante_q_2023': per_capita,
              'vab_total_millones_q_2023': vab, 'ipns_millones_q_2023': nominal[d, 'IPNS']}
    cuotas = {g: 100 * (valor / vab) for g, valor in valores.items()}
    if abs(fsum(cuotas.values()) - 100) > 1e-9:
        raise ValueError(f'{d}: las participaciones sectoriales no suman 100')
    for g in grupos:
        slug = g.lower().replace('-', '_')
        perfil[f'vab_{slug}_millones_q_2023'] = nominal[d, g]
        perfil[f'participacion_{slug}_pct_2023'] = cuotas[g]
    lider = max(grupos, key=valores.get)
    perfil['actividad_predominante_2023'] = lider
    perfil['participacion_predominante_pct_2023'] = cuotas[lider]
    return perfil


def construir(datos):
    procesados = datos / 'processed'
    enc = cargar_encovi(procesados)
    grupos = cargar_grupos(datos / 'reference/sectores_ciiu.csv')
    nominal, pc = cargar_banguat(procesados, grupos)
    matriz = []
    for d, nombre in DEPTOS.items():
        fila = {'depto_id': d, 'departamento': nombre, 'anio': ANIO}
        for indicador in PESOS:
            original = enc[d, indicador]
            for campo in CAMPOS:
                ocultar = original['estado'] != PUBLICABLE and campo in ('valor', 'ic95_inf', 'ic95_sup')
                fila[f'{indicador}_{campo}_2023'] = '' if ocultar else original[campo]
        fila.update(perfil_productivo(d, grupos, nominal, pc[d,]['pib_per_capita']))
        matriz.append(fila)
    return matriz


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--output', type=Path, help='Por defecto, processed/matriz_departamental.csv bajo data-dir')
    args = parser.parse_args()
    salida = args.output or args.data_dir / 'processed/matriz_departamental.csv'
    try:
        filas = construir(args.data_dir)
        salida.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=salida.parent) as temporal:
            validada = Path(temporal) / 'matriz.csv'
            escribir_csv(validada, filas, filas[0].keys())
            validada.replace(salida)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'M-03: {exc}\n')
    print(f'{salida}: {len(filas)} departamentos, {len(filas[0])} columnas')


if __name__ == '__main__':
    main()
