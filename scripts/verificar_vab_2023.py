"""Cotejo independiente de controles 2023 contra celdas oficiales."""
import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/banguat_nacional'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--datos', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    a = load_workbook(RAW / '12_Valor_agregado_bruto_del_sector_informal.xlsx', read_only=True, data_only=True)
    b = load_workbook(RAW / '5_Clasificacion_cruzada_de_industrias_y_sectores_institucionales.xlsx', read_only=True, data_only=True)
    try:
        informal = Decimal(str(a['12.1']['O26'].value))
        comercio = Decimal(str(a['12.1']['O14'].value))
        estructura = Decimal(str(a['12.1']['O42'].value))
        total = Decimal(str(b['5.103']['I126'].value))
    finally:
        a.close(); b.close()
    valores = {'vab_informal': informal, 'vab_total': total, 'participacion_informal_pct': 100*informal/total, 'composicion_comercio_pct': 100*comercio/informal}
    errores = []
    with (args.datos / 'vab_informal_nacional.csv').open(encoding='utf-8', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['anio'] == '2023' and r['tipo_precio'] == 'corrientes']
    with (args.datos / 'vab_informal_grupo.csv').open(encoding='utf-8', newline='') as f:
        ramas = [r for r in csv.DictReader(f) if r['anio'] == '2023' and r['tipo_precio'] == 'corrientes' and r['grupo_ciiu'] == 'G']
    if len(filas) != 1 or len(ramas) != 1:
        errores.append('Claves 2023 incompletas o duplicadas')
    else:
        for clave in ('vab_informal', 'vab_total', 'participacion_informal_pct'):
            if abs(Decimal(filas[0][clave]) - valores[clave]) > Decimal('0.000000001'):
                errores.append(clave)
        if abs(Decimal(ramas[0]['vab_informal']) - comercio) > Decimal('0.000001') or abs(Decimal(ramas[0]['composicion_pct']) - valores['composicion_comercio_pct']) > Decimal('0.000000001'):
            errores.append('comercio')
    if abs(estructura-valores['composicion_comercio_pct']) > Decimal('0.00000051'):
        errores.append('estructura publicada')
    resultado = {'celdas': {'vab_informal': '12.1!O26', 'vab_total': '5.103!I126', 'comercio': '12.1!O14', 'composicion_publicada_comercio_pct': '12.1!O42'}, 'valores': {k: str(v) for k,v in valores.items()}, 'controles_redondeados': {k: str(v.quantize(Decimal('0.01'))) for k,v in valores.items()}, 'errores': errores}
    texto = json.dumps(resultado, ensure_ascii=False, indent=2) + '\n'
    if args.salida:
        args.salida.write_text(texto, encoding='utf-8')
    else:
        print(texto, end='')
    return bool(errores)


if __name__ == '__main__':
    raise SystemExit(main())
