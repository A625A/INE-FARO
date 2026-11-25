"""Procesa las cuentas nacionales Banguat de producción informal."""
import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from openpyxl import load_workbook
from comun import ROOT, escribir_csv, escribir_json, normalizar
from procesar_pib import numero

RAW = ROOT / 'data/raw/banguat_nacional'
ARCHIVOS = {'informal': '12_Valor_agregado_bruto_del_sector_informal.xlsx', 'ccis': '5_Clasificacion_cruzada_de_industrias_y_sectores_institucionales.xlsx', 'nomenclatura': 'Nomenclaturas_2013.xlsx'}
INFORMAL = ARCHIVOS['informal']
HASHES = {'informal': 'cc653433a922db3e6f7222eee6cab7394e7ed193390cb640ae2f5072caa290d3', 'ccis': '154fa12f69d11fd6c187cccf237af9f3fcc80b6f61f4aa6dfeaa29a60d151618', 'nomenclatura': '3c4ccbf16be5d4a04828ed26a5535218aaa70219f13a06ce7d6b0bf559c1c355'}
GRUPOS = 'A B C D-E F G H I J K L M N O P Q R-S-T-U'.split()
ANIOS = set(range(2013, 2025)) - {2020}


def exigir(condicion, mensaje):
    if not condicion:
        raise ValueError(mensaje)


def leer_informal(filas, hoja):
    unidad = normalizar(filas[4][1])
    exigir(unidad == ('millones de quetzales' if hoja == '12.1' else 'millones de quetzales en medidas encadenadas de volumen con ano de referencia 2013 a/'), 'Unidad incompatible')
    cab = filas[6]
    fin = cab.index('Variación porcentual (%)')
    anos = []
    for valor in cab[5:fin]:
        match = re.fullmatch(r'(\d{4})( p/)?', str(valor))
        exigir(match is not None, 'Año inválido')
        anos.append((int(match[1]), bool(match[2])))
    exigir(len(anos) == len(ANIOS) and {a for a, _ in anos} == ANIOS, 'Cobertura anual inválida')
    grupos = filas[8:25]
    exigir([r[2] for r in grupos] == GRUPOS and filas[25][1] == 'Valor agregado bruto', 'Grupos inválidos')
    resultado = {}
    for col, (anio, preliminar) in enumerate(anos, 5):
        total = numero(filas[25][col], f'{hoja} total')
        exigir(total > 0, 'Total inválido')
        valores = {r[2]: (r[3], numero(r[col], f'{hoja} {r[2]}')) for r in grupos}
        if hoja == '12.1':
            exigir(abs(math.fsum(v[1] for v in valores.values()) - total) <= 0.000009, 'Total informal no concilia')
            for j, r in enumerate(grupos):
                estructura = numero(filas[36+j][col], 'composición')
                exigir(filas[36+j][2] == r[2] and abs(estructura - 100 * valores[r[2]][1] / total) <= 0.00000051, 'Composición incompatible')
        resultado[anio] = {'total': total, 'grupos': valores, 'preliminar': preliminar}
    return resultado


def leer_ccis(filas, hoja, anio):
    exigir(filas[1][1] == f'Cuadro {hoja}' and normalizar(filas[3][1]) == 'b1b valor agregado' and normalizar(filas[4][1]) == 'millones de quetzales', 'CCIS incompatible')
    exigir(str(filas[5][1]) in (f'Año {anio}', f'Año {anio} p/') and normalizar(filas[9][8]) == 's1 economia total', 'Periodo o S1 incompatible')
    datos = {}
    totales = []
    for r in filas[10:]:
        codigo = r[1]
        if str(codigo).startswith('AE'):
            exigir(codigo not in datos, 'NAEG duplicado')
            datos[codigo] = numero(r[8], str(codigo))
        elif codigo == 'Valor agregado':
            totales.append(numero(r[8], 'S1'))
    exigir(set(datos) == {f'AE{i:03d}' for i in range(1, 106)} and len(totales) == 1 and totales[0] > 0, 'Cobertura CCIS inválida')
    exigir(abs(math.fsum(datos.values()) - totales[0]) <= 0.000053, 'CCIS no concilia')
    return {'total': totales[0], 'actividades': datos, 'preliminar': str(filas[5][1]).endswith('p/')}


def leer_mapeo(filas):
    exigir(normalizar(filas[8][3]).endswith('(ciiu) revision 4'), 'Nomenclatura incompatible')
    rangos = [(1,3,'A'), (5,9,'B'), (10,33,'C'), (35,39,'D-E'), (41,43,'F'), (45,47,'G'), (49,53,'H'), (55,56,'I'), (58,63,'J'), (64,66,'K'), (68,68,'L'), (69,75,'M'), (77,82,'N'), (84,84,'O'), (85,85,'P'), (86,88,'Q'), (90,99,'R-S-T-U')]
    divisiones = {i: grupo for inicio, fin, grupo in rangos for i in range(inicio, fin+1)}
    mapa = {}
    for r in filas[9:]:
        codigo = r[1]
        if not str(codigo).startswith('AE'):
            continue
        clases = str(r[3]).split(', ')
        exigir(all(re.fullmatch(r'\d{4}', c) for c in clases), 'Clase inválida')
        destinos = {divisiones.get(int(c[:2])) for c in clases}
        exigir(len(destinos) == 1 and None not in destinos and codigo not in mapa, 'Mapa incompatible')
        mapa[codigo] = destinos.pop()
    exigir(set(mapa) == {f'AE{i:03d}' for i in range(1,106)}, 'Mapa incompleto')
    return mapa


def procesar(input_dir, regional):
    fuentes = {}
    for tipo, nombre in ARCHIVOS.items():
        path = input_dir / nombre
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        exigir(digest == HASHES[tipo], f'Hash diferente: {nombre}')
        fuentes[tipo] = digest
    regional_hash = hashlib.sha256(regional.read_bytes()).hexdigest()
    exigir(regional_hash == '7acce7a4f90c92245fe481e3c853e2b48659c8e84c9176c064bad4e09db6951a', 'Hash del contraste regional diferente')
    informal = load_workbook(input_dir / ARCHIVOS['informal'], read_only=True, data_only=True)
    ccis = load_workbook(input_dir / ARCHIVOS['ccis'], read_only=True, data_only=True)
    nom = load_workbook(input_dir / ARCHIVOS['nomenclatura'], read_only=True, data_only=True)
    referencia = load_workbook(regional, read_only=True, data_only=True)
    try:
        cuadros = {h: leer_informal(list(informal[h].values), h) for h in ('12.1', '12.2')}
        mapa = leer_mapeo(list(nom['NAEG-CIIU'].values))
        nacional, grupos, conciliaciones = [], [], []
        for anio in sorted(ANIOS):
            hoja = f'5.{3 + 10 * (anio - 2013)}'
            total = leer_ccis(list(ccis[hoja].values), hoja, anio)
            denominadores = {g: math.fsum(v for ae, v in total['actividades'].items() if mapa[ae] == g) for g in GRUPOS}
            for g in GRUPOS:
                s = referencia[g.replace('-', ' - ') if g == 'D-E' else g]
                columnas = {v: i for i, v in enumerate(list(s.values)[7]) if isinstance(v, int)}
                valor_referencia = list(s.values)[32][columnas[anio]]
                diferencia = denominadores[g] - valor_referencia
                exigir(abs(diferencia) < 0.000053, f'No concilia rama {anio} {g}: {diferencia}')
                conciliaciones.append({'anio': anio, 'grupo': g, 'ccis': denominadores[g], 'referencia': valor_referencia, 'diferencia': diferencia})
            for hoja_12, precio in [('12.1', 'corrientes'), ('12.2', 'volumen_encadenado_2013')]:
                fila = cuadros[hoja_12][anio]
                corriente = precio == 'corrientes'
                base = {'anio': anio, 'tipo_precio': precio, 'unidad': 'millones_de_quetzales', 'preliminar': fila['preliminar'], 'revision': 'referencia_2013_snapshot_2026-11-25'}
                nacional.append({**base, 'vab_informal': fila['total'], 'vab_total': total['total'] if corriente else '', 'participacion_informal_pct': round(100*fila['total']/total['total'], 9) if corriente else ''})
                for g in GRUPOS:
                    nombre, valor = fila['grupos'][g]
                    denominador = denominadores[g]
                    grupos.append({**base, 'grupo_ciiu': g, 'grupo_nombre': nombre, 'vab_informal': valor, 'vab_total_grupo': denominador if corriente else '', 'composicion_pct': round(100*valor/fila['total'], 9) if corriente else '', 'participacion_informal_grupo_pct': round(100*valor/denominador, 9) if corriente and denominador > 0 else ''})
        return nacional, grupos, {'sha256': fuentes, 'sha256_contraste': regional_hash, 'conciliacion_grupos': conciliaciones, 'ausencia_2020': 'INE no realizó ENEI en 2020', 'mapeo': 'NAEG-CIIU revisión 4, contraste con VAB nacional del cuadro departamental'}
    finally:
        informal.close(); ccis.close(); nom.close(); referencia.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=RAW)
    parser.add_argument('--regional', type=Path, default=ROOT / 'data/raw/banguat/7_Resultados_por_actividad_economica_en_departamentos.xlsx')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'docs/evidencia')
    args = parser.parse_args()
    nacional, grupos, evidencia = procesar(args.input_dir, args.regional)
    escribir_csv(args.output_dir / 'vab_informal_nacional.csv', nacional, list(nacional[0]))
    escribir_csv(args.output_dir / 'vab_informal_grupo.csv', grupos, list(grupos[0]))
    escribir_json(args.evidence_dir / 'vab_informal_conciliacion.json', evidencia)
    print(f'{len(nacional)} registros nacionales y {len(grupos)} por grupo')


if __name__ == '__main__':
    main()
