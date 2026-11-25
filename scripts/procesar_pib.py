"""I-04: normaliza los cuadros Banguat y valida sus conciliaciones."""

import argparse
import math
import sys
from pathlib import Path

from openpyxl import load_workbook

from comun import (ROOT, DEPARTAMENTOS, codigo_departamento, escribir_csv,
                   escribir_json, procedencia, descargar_fuentes)

ARCHIVOS = {
    'total': '5_PIB_total_por_departamento.xlsx',
    'actividad': '7_Resultados_por_actividad_economica_en_departamentos.xlsx',
    'per_capita': '8_PIB_Per_Capita_por_departamento.xlsx',
}
ACTIVIDADES = ['A', 'B', 'C', 'D - E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
               'M', 'N', 'O', 'P', 'Q', 'R-S-T-U', 'IPNS']


def numero(valor, contexto):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
        raise ValueError(f'Valor numérico faltante o inválido en {contexto}: {valor!r}')
    if valor < 0:
        raise ValueError(f'Valor negativo inesperado en {contexto}')
    return valor


def bloques(hoja, anio, per_capita=False, precio_unico=None):
    filas = list(hoja.values)
    encontrados = []
    for indice, fila in enumerate(filas):
        if 'No.' not in fila or 'Departamento' not in fila:
            continue
        id_col = fila.index('No.')
        depto_col = fila.index('Departamento')
        columnas = {v: i for i, v in enumerate(fila) if type(v) is int and 2013 <= v <= 2024}
        if set(columnas) != set(range(2013, 2025)):
            raise ValueError(f'Cobertura anual inesperada en {hoja.title}')
        anteriores = ' '.join(str(v) for r in filas[max(0, indice-5):indice]
                              for v in r if v is not None)
        if per_capita:
            if 'Cifras en quetzales' not in anteriores:
                raise ValueError('Unidad per cápita inesperada')
            precio = 'corrientes'
        else:
            if 'Millones de quetzales' not in anteriores:
                raise ValueError(f'Unidad inesperada en {hoja.title}')
            precio = 'volumen_encadenado_2013' if 'encadenadas' in anteriores else 'corrientes'
            if precio != 'corrientes' and 'referencia 2013' not in anteriores:
                raise ValueError('Año de referencia de volumen inesperado')
        valores = {}
        for i in range(indice + 1, len(filas)):
            r = filas[i]
            nombre = r[depto_col]
            identificador = r[id_col]
            if nombre == 'Nacional' or identificador == 'Nacional':
                clave = 'Nacional'
            elif nombre == 'Extrarregional':
                clave = 'Extrarregional'
            elif identificador is None and nombre is None:
                continue
            else:
                if type(identificador) is not int or identificador not in DEPARTAMENTOS:
                    raise ValueError(f'Fila territorial inesperada: {hoja.title}:{i+1}')
                clave = codigo_departamento(nombre)
                if int(clave) != identificador:
                    raise ValueError('Código Banguat no coincide con catálogo INE')
            if clave in valores:
                raise ValueError(f'Territorio duplicado: {hoja.title}:{clave}')
            valores[clave] = numero(r[columnas[anio]], f'{hoja.title}:{i+1}')
            if clave == 'Nacional':
                break
        if not {f'{n:02}' for n in DEPARTAMENTOS}.issubset(valores) or 'Nacional' not in valores:
            raise ValueError(f'Cobertura territorial incompleta en {hoja.title}')
        encontrados.append((precio, valores, {'hoja': hoja.title,
                           'fila_encabezado': indice + 1,
                           'columna_anio': columnas[anio] + 1}))
    precios = [b[0] for b in encontrados]
    esperado = [precio_unico] if precio_unico else (
        ['corrientes'] if per_capita else ['corrientes', 'volumen_encadenado_2013'])
    if sorted(precios) != sorted(esperado):
        raise ValueError(f'Bloques de valoración inesperados en {hoja.title}: {precios}')
    return encontrados


def procesar(input_dir, anio, manifiesto=None):
    tablas, per_capita, controles, origenes, trazas = [], [], [], [], []
    for tipo, nombre in ARCHIVOS.items():
        path = input_dir / nombre
        fuente = procedencia(path, manifiesto)
        origenes.append(fuente)
        libro = load_workbook(path, read_only=True, data_only=True)
        try:
            if tipo == 'actividad':
                if set(libro.sheetnames) != {'Índice', *ACTIVIDADES}:
                    raise ValueError('Secciones de actividad inesperadas')
                hojas = [(libro[s], s.replace(' ', ''),
                          'impuestos_netos' if s == 'IPNS' else 'valor_agregado') for s in ACTIVIDADES]
            elif tipo == 'total':
                hojas = [(libro['PIB Corriente'], 'TOTAL', 'pib_total'),
                         (libro['PIB Constante'], 'TOTAL', 'pib_total')]
            else:
                hojas = [(libro['PIB Per Cápita'], 'TOTAL', 'pib_per_capita')]
            for hoja, sector, medida in hojas:
                if tipo == 'total':
                    precio = 'corrientes' if hoja.title == 'PIB Corriente' else 'volumen_encadenado_2013'
                    datos = bloques(hoja, anio, precio_unico=precio)
                else:
                    datos = bloques(hoja, anio, tipo == 'per_capita')
                for precio, valores, traza in datos:
                    trazas.append({'archivo': nombre, 'tipo_precio': precio, **traza})
                    for n, departamento in DEPARTAMENTOS.items():
                        clave = f'{n:02}'
                        base = {'depto_id': clave, 'departamento': departamento,
                                'anio': anio, 'tipo_precio': precio, 'fuente': fuente['url']}
                        if tipo == 'per_capita':
                            per_capita.append({**base, 'pib_per_capita': valores[clave],
                                               'unidad': 'quetzales_por_habitante'})
                        else:
                            tablas.append({**base, 'sector': sector, 'pib_valor': valores[clave],
                                           'unidad': 'millones_de_quetzales', 'medida': medida})
                    if tipo == 'per_capita':
                        continue
                    if sector != 'IPNS' and 'Extrarregional' not in valores:
                        raise ValueError(f'Falta Extrarregional en {hoja.title}')
                    suma = math.fsum(valores[f'{n:02}'] for n in DEPARTAMENTOS)
                    extra = valores.get('Extrarregional')
                    diferencia = valores['Nacional'] - suma - (extra if extra is not None else 0)
                    if precio == 'corrientes' and not math.isclose(diferencia, 0, abs_tol=1e-6):
                        raise ValueError(f'Conciliación nacional fallida en {hoja.title}: {diferencia}')
                    controles.append({'anio': anio, 'sector': sector, 'medida': medida,
                        'tipo_precio': precio, 'unidad': 'millones_de_quetzales',
                        'suma_departamentos': suma, 'extrarregional': extra,
                        'nacional': valores['Nacional'], 'diferencia': diferencia,
                        'estado': 'validado' if precio == 'corrientes' else 'no_aditivo',
                        'nota': 'Sin componente extrarregional publicado' if extra is None else '',
                        'fuente': fuente['url']})
        finally:
            libro.close()
    for codigo in DEPARTAMENTOS:
        clave = f'{codigo:02}'
        datos = [r for r in tablas if r['depto_id'] == clave and r['tipo_precio'] == 'corrientes']
        total = next(r['pib_valor'] for r in datos if r['medida'] == 'pib_total')
        componentes = math.fsum(r['pib_valor'] for r in datos if r['medida'] != 'pib_total')
        if not math.isclose(total, componentes, abs_tol=1e-6, rel_tol=0):
            raise ValueError(f'VAB + impuestos no concilia con PIB: {clave}')
    return tablas, per_capita, controles, {'anio': anio, 'cobertura_original': [2013, 2024],
        'departamentos': 22, 'filas_pib': len(tablas), 'filas_per_capita': len(per_capita),
        'insumos': origenes, 'bloques': trazas, 'conciliacion_corriente': 'validada',
        'volumen_encadenado': 'No se exige aditividad; referencia 2013',
        'advertencia': 'Producción económica; no es ingreso ni consumo de hogares.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=ROOT / 'data/raw/banguat')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'docs/evidencia')
    parser.add_argument('--download', action='store_true', help='Descargar snapshot oficial si falta; verificar SHA-256')
    parser.add_argument('--manifest', type=Path, help='Manifiesto alternativo de snapshots previamente revisados')
    parser.add_argument('--year', type=int, choices=range(2013, 2025), default=2023)
    args = parser.parse_args()
    try:
        if args.download:
            descargar_fuentes('banguat', args.input_dir, args.manifest)
        filas, per_capita, controles, evidencia = procesar(args.input_dir, args.year, args.manifest)
        escribir_csv(args.output_dir / 'pib_departamental.csv', filas,
                     ['depto_id', 'departamento', 'anio', 'sector', 'pib_valor',
                      'unidad', 'tipo_precio', 'fuente', 'medida'])
        escribir_csv(args.output_dir / 'pib_per_capita.csv', per_capita,
                     ['depto_id', 'departamento', 'anio', 'pib_per_capita', 'unidad', 'tipo_precio', 'fuente'])
        escribir_csv(args.output_dir / 'pib_conciliacion.csv', controles, list(controles[0]))
        escribir_json(args.evidence_dir / 'I-04.json', evidencia)
    except (ValueError, OSError, KeyError, StopIteration) as error:
        print(f'I-04 falló: {error}. No use salidas previas o parciales como resultado de esta ejecución.', file=sys.stderr)
        return 1
    print(f'I-04 validado: {len(filas)} filas y 22 departamentos, año {args.year}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
