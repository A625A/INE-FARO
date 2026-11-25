"""Regla R1 del radar departamental para la matriz M-03 de 2023."""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path


def detectar(filas, tolerancia, umbral_pobreza, umbral_pib):
    resultados = []
    for a, b in itertools.combinations(sorted(filas, key=lambda x: x['depto_id']), 2):
        if a['informal'] is None or b['informal'] is None:
            continue
        diferencia_i = abs(a['informal'] - b['informal'])
        if diferencia_i > tolerancia:
            continue
        diferencia_p = (abs(a['pobreza'] - b['pobreza'])
                        if a['pobreza'] is not None and b['pobreza'] is not None else None)
        razon = (max(a['pib'], b['pib']) / min(a['pib'], b['pib'])
                 if a['pib'] and b['pib'] and min(a['pib'], b['pib']) > 0 else None)
        motivos = []
        if diferencia_p is not None and diferencia_p >= umbral_pobreza:
            motivos.append('pobreza')
        if razon is not None and razon >= umbral_pib:
            motivos.append('pib')
        if motivos:
            resultados.append({'id': f"R1:2023:{a['depto_id']}-{b['depto_id']}",
                               'regla': 'R1', 'anio': 2023,
                               'territorios': [a['depto_id'], b['depto_id']],
                               'departamentos': [a['departamento'], b['departamento']],
                               'motivo': motivos, 'diferencia_informal_pp': diferencia_i,
                               'diferencia_pobreza_pp': diferencia_p, 'razon_pib': razon})
    resultados.sort(key=lambda r: (0 if len(r['motivo']) == 2 else 1 if 'pobreza' in r['motivo'] else 2,
                                    -r['diferencia_pobreza_pp'] if r['diferencia_pobreza_pp'] is not None else math.inf,
                                    -r['razon_pib'] if r['razon_pib'] is not None else math.inf,
                                    r['diferencia_informal_pp'], r['territorios']))
    return resultados


def numero(texto):
    if texto == '':
        return None
    valor = float(texto)
    if not math.isfinite(valor):
        raise ValueError('Valor no finito')
    return valor


def leer_matriz(path):
    with path.open(encoding='utf-8', newline='') as archivo:
        originales = list(csv.DictReader(archivo))
    if len(originales) != 22 or {r['depto_id'] for r in originales} != {f'{i:02}' for i in range(1, 23)}:
        raise ValueError('La matriz debe contener 22 departamentos únicos')
    filas = []
    for r in originales:
        if r['anio'] != '2023':
            raise ValueError('Año incompatible')
        valores = {}
        for nombre, clave in [('ocupacion_sector_informal', 'informal'), ('pobreza_total', 'pobreza')]:
            valor = numero(r[f'{nombre}_valor_2023'])
            cv = numero(r[f'{nombre}_cv_2023'])
            n = numero(r[f'{nombre}_n_2023'])
            estado = r[f'{nombre}_estado_2023']
            if estado not in ('publicable', 'publicable_con_reserva', 'no_publicable'):
                raise ValueError('Estado inválido')
            if valor is not None and not 0 <= valor <= 100:
                raise ValueError('Tasa fuera de rango')
            valores[clave] = valor if estado != 'no_publicable' and n is not None and n >= 30 and cv is not None and 0 <= cv <= 30 else None
        pib = numero(r['pib_por_habitante_q_2023'])
        filas.append(dict(depto_id=r['depto_id'], departamento=r['departamento'], pib=pib, **valores))
    return filas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matriz', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    filas = leer_matriz(args.matriz)
    resultados = detectar(filas, 3, 15, 1.5)
    canon = json.dumps(sorted(filas, key=lambda r: r['depto_id']), ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    contenido = {'schema_version': 'r1-1.0', 'reglas_version': '1.1', 'modo': 'standard',
                 'hash_filas_sha256': hashlib.sha256(canon.encode()).hexdigest(),
                 'parametros': {'tolerancia_informal_pp': 3, 'brecha_pobreza_pp': 15, 'razon_pib': 1.5},
                 'conteos': {'R1': len(resultados)}, 'hallazgos': resultados}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'r1.json').write_text(json.dumps(contenido, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    columnas = ['id', 'regla', 'anio', 'territorios', 'departamentos', 'motivo', 'diferencia_informal_pp', 'diferencia_pobreza_pp', 'razon_pib']
    with (args.output_dir / 'r1.csv').open('w', encoding='utf-8', newline='') as archivo:
        writer = csv.DictWriter(archivo, fieldnames=columnas, lineterminator='\n')
        writer.writeheader()
        for r in resultados:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v for k, v in r.items()})
    print(f"R1: {len(resultados)} parejas")


if __name__ == '__main__':
    main()
