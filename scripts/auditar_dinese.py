"""I-05: audita DINESE 2023–2024 y genera agregados descriptivos separados."""

import argparse
import sys
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

from comun import (ROOT, DEPARTAMENTOS, SECCIONES_CIIU, codigo_departamento, escribir_csv,
                   escribir_json, procedencia, descargar_fuentes)

COLUMNAS = ('CÓDIGO', 'AÑO', 'SECCION_CIIU_4', 'TIPO_PERSONERIA',
            'CLA_RANGO_VENTAS', 'MOVIMIENTO_DE_VENTAS',
            'NOMBRE_DEPARTAMENTO', 'NOMBRE_MUNICIPIO')
CONTROLES = {
    2023: {'total': 425464, 'con_movimiento': 220903,
           'guatemala_total': 209804, 'guatemala_con_movimiento': 108182},
    2024: {'total': 645431, 'con_movimiento': 338415,
           'guatemala_total': 235807, 'guatemala_con_movimiento': 120141},
}
PUBLICACIONES = {
    2023: 'https://www.ine.gob.gt/wp-content/uploads/2024/12/Resumen-Base-de-datos-DINESE.pdf',
    2024: 'https://www.ine.gob.gt/wp-content/uploads/2026/03/RESUMEN-ESTADISTICO-FORMATO-DINESE.pdf',
}


def auditar(input_dir):
    resumen, evidencia = [], []
    codigos_seccion = {nombre: codigo for codigo, nombre in SECCIONES_CIIU.items()}
    for anio in (2023, 2024):
        path = input_dir / f'dinese-{anio}.xlsx'
        fuente = procedencia(path)
        libro = load_workbook(path, read_only=True, data_only=True)
        conteos, codigos, departamentos, secciones = Counter(), set(), set(), set()
        faltantes = Counter()
        try:
            if libro.sheetnames != [f'Empresas {anio}']:
                raise ValueError(f'Hojas inesperadas en DINESE {anio}')
            filas = libro.active.iter_rows(values_only=True)
            if tuple(next(filas)) != COLUMNAS:
                raise ValueError(f'Columnas inesperadas en DINESE {anio}')
            for numero_fila, fila in enumerate(filas, 2):
                if len(fila) != len(COLUMNAS):
                    raise ValueError(f'Número de columnas inválido en {anio}:{numero_fila}')
                codigo, year, sector, personeria, rango, movimiento, depto, municipio = fila
                if type(codigo) is not int or codigo <= 0 or codigo in codigos:
                    raise ValueError(f'CÓDIGO vacío, inválido o duplicado en {anio}:{numero_fila}')
                codigos.add(codigo)
                if year != anio:
                    raise ValueError(f'AÑO inconsistente en {anio}:{numero_fila}')
                if not isinstance(sector, str) or not sector.strip():
                    raise ValueError(f'Sección CIIU faltante en {anio}:{numero_fila}')
                if sector.strip() not in codigos_seccion:
                    raise ValueError(f'Sección CIIU desconocida en {anio}:{numero_fila}')
                if movimiento not in ('Con movimiento', 'Sin movimiento'):
                    raise ValueError(f'Movimiento de ventas desconocido en {anio}:{numero_fila}')
                clave = codigo_departamento(depto)
                departamentos.add(clave)
                sector = sector.strip()
                secciones.add(sector)
                estado = 'con_movimiento' if movimiento == 'Con movimiento' else 'sin_movimiento'
                conteos[(clave, sector, estado)] += 1
                for campo, valor in [('personeria', personeria), ('rango_ventas', rango), ('municipio', municipio)]:
                    if valor is None or not str(valor).strip():
                        faltantes[campo] += 1
            if departamentos != {f'{n:02}' for n in DEPARTAMENTOS}:
                raise ValueError(f'Cobertura departamental incompleta en {anio}')
            control = {
                'total': len(codigos),
                'con_movimiento': sum(v for (d, s, m), v in conteos.items() if m == 'con_movimiento'),
                'guatemala_total': sum(v for (d, s, m), v in conteos.items() if d == '01'),
                'guatemala_con_movimiento': sum(v for (d, s, m), v in conteos.items()
                                                if d == '01' and m == 'con_movimiento'),
            }
            if control != CONTROLES[anio]:
                raise ValueError(f'Controles oficiales no concilian en {anio}: {control}')
            for (depto, sector, movimiento), cantidad in sorted(conteos.items()):
                seccion_codigo = codigos_seccion[sector]
                sector_banguat = ('D-E' if seccion_codigo in 'DE' else
                                  'R-S-T-U' if seccion_codigo in 'RSTU' else seccion_codigo)
                resumen.append({'depto_id': depto, 'departamento': DEPARTAMENTOS[int(depto)],
                    'anio': anio, 'seccion_ciiu_4': sector, 'seccion_codigo': seccion_codigo,
                    'sector_banguat': sector_banguat,
                    'movimiento_ventas': movimiento, 'empresas': cantidad,
                    'unidad': 'registros_empresas_activas', 'fuente': fuente['url'],
                    'uso': 'descriptivo_transversal', 'crecimiento_habilitado': 'no'})
            evidencia.append({'anio': anio, 'controles': control,
                'sin_movimiento': control['total'] - control['con_movimiento'],
                'duplicados_codigo': 0, 'departamentos': len(departamentos),
                'secciones': sorted(secciones), 'faltantes_no_criticos': dict(faltantes),
                'filas_descartadas': 0, 'insumo': fuente, 'publicacion_control': PUBLICACIONES[anio]})
        finally:
            libro.close()
    return resumen, {'anios': evidencia, 'controles_oficiales': 'validados',
        'viabilidad_transversal_2023': True, 'habilitar_crecimiento_radar': False,
        'codigo_longitudinal_validado': False,
        'comparabilidad_temporal': 'no_acreditada',
        'advertencia': 'Variación de registros no demuestra creación de empresas ni formalización laboral.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=ROOT / 'data/raw/dinese')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'docs/evidencia')
    parser.add_argument('--download', action='store_true', help='Descargar snapshot oficial si falta; verificar SHA-256')
    args = parser.parse_args()
    try:
        if args.download:
            descargar_fuentes('dinese', args.input_dir)
        filas, evidencia = auditar(args.input_dir)
        escribir_csv(args.output_dir / 'dinese_resumen.csv', filas, list(filas[0]))
        escribir_json(args.evidence_dir / 'I-05.json', evidencia)
    except (ValueError, OSError, KeyError, StopIteration) as error:
        print(f'I-05: {error}. No se generaron salidas nuevas; revise las anteriores.', file=sys.stderr)
        return 1
    print(f'I-05 auditado: {len(filas)} agregados; crecimiento excluido del radar.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
