"""Productor laboral ENEIC IV-2025, con márgenes fijos y publicación autorizada."""
import argparse
import hashlib
import json
import os
import tempfile
from operator import itemgetter
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from comun import ROOT, descargar_fuentes, procedencia

PERIODO = 'IV-2025'
MANIFIESTO = ROOT / 'data/reference/fuentes_eneic_iv_2025.json'
CLAVE = ['ANIO', 'TRIMESTRE', 'DOMINIO', 'NUM_HOGAR', 'NUM_PERSONA']
COLUMNAS = CLAVE + ['P02A02', 'P02A03', 'OCUPADOS', 'FORMAL_INFORMAL', 'FACTOR',
                   'P05C04_2D', 'P05C04_1D', 'P05C13', 'YLAB_PUBLI']
DOMINIOS = {1: 'Urbano Metropolitano', 2: 'Resto Urbano', 3: 'Rural Nacional'}
TAMANOS = dict(enumerate(['1 persona', '2 personas', '3 personas', '4 personas', '5 personas',
                         'De 6 a 10', 'De 11 a 50', 'De 51 a 100', 'De 101 a 200',
                         'De 201 a 500', 'De 501 o más'], 1))
SECCIONES = [('A',1,3,1), ('B',5,9,2), ('C',10,33,2), ('D',35,35,2), ('E',36,39,2),
             ('F',41,43,3), ('G',45,47,4), ('H',49,53,4), ('I',55,56,4), ('J',58,63,5),
             ('K',64,66,6), ('L',68,68,7), ('M',69,75,8), ('N',77,82,8), ('O',84,84,9),
             ('P',85,85,9), ('Q',86,88,9), ('R',90,93,10), ('S',94,96,10),
             ('T',97,98,10), ('U',99,99,10)]


def leer_diccionario(path):
    libro = load_workbook(path, read_only=True, data_only=True)
    catalogos = {}
    actual = None
    try:
        for variable, codigo, etiqueta, *_ in libro.active.values:
            if variable:
                actual = variable
            if isinstance(codigo, str) and codigo.strip().isdigit():
                catalogos.setdefault(actual, {})[int(codigo)] = etiqueta
    finally:
        libro.close()
    return catalogos


def mapa_divisiones(catalogos):
    sectores = pd.read_csv(ROOT / 'data/reference/sectores_ciiu.csv').set_index(
        'seccion_codigo', verify_integrity=True).sector_banguat
    mapa = {d: (s, sectores[s], r) for s, a, b, r in SECCIONES for d in range(a, b+1)}
    if set(catalogos['P05C04_2D']) != set(mapa) | {999}:
        raise ValueError('P05C04_2D: catálogo distinto de CIIU Rev.4')
    for campo, esperado in [('DOMINIO', DOMINIOS), ('P05C13', TAMANOS),
                            ('FORMAL_INFORMAL', {1: 'Informal', 2: 'Formal'})]:
        if catalogos[campo] != esperado:
            raise ValueError(f'{campo}: diccionario cambió')
    return mapa


def leer_personas(path):
    libro = load_workbook(path, read_only=True, data_only=True)
    try:
        filas = iter(libro.active.values)
        cabecera = next(filas)
        if any(cabecera.count(c) != 1 for c in COLUMNAS):
            raise ValueError('Cabecera incompleta o ambigua')
        extraer = itemgetter(*(cabecera.index(c) for c in COLUMNAS))
        return pd.DataFrame.from_records((extraer(f) for f in filas), columns=COLUMNAS)
    finally:
        libro.close()


def preparar(personas, divisiones):
    df = personas[COLUMNAS].copy()
    for c in COLUMNAS:
        original = df[c].replace(r'^\s*$', np.nan, regex=True)
        numero = pd.to_numeric(original, errors='coerce')
        presentes = numero.dropna()
        if ((original.notna() & numero.isna()).any() or not np.isfinite(presentes).all()
                or (c not in ('FACTOR', 'YLAB_PUBLI') and (presentes % 1 != 0).any())):
            raise ValueError(f'{c}: dato numérico inválido')
        df[c] = numero
    for c in CLAVE + ['FACTOR', 'P02A03']:
        if df[c].isna().any():
            raise ValueError(f'{c}: falta dato obligatorio')
    if df.duplicated(CLAVE).any():
        raise ValueError('Clave de persona duplicada')
    for c, codigos in [('ANIO', [2025]), ('TRIMESTRE', [5]), ('DOMINIO', DOMINIOS),
                       ('OCUPADOS', [1]), ('P02A02', [1, 2]), ('FORMAL_INFORMAL', [1, 2]),
                       ('P05C13', TAMANOS)]:
        if not df[c].dropna().isin(codigos).all():
            raise ValueError(f'{c}: categoría inválida')
    if (df.FACTOR <= 0).any():
        raise ValueError('FACTOR debe ser positivo')
    if (df.P02A03 < 0).any():
        raise ValueError('P02A03 negativa')
    oc = df.loc[df.P02A03.ge(15) & df.OCUPADOS.eq(1)].copy()
    oc['nacional'] = 'GT'
    oc['dominio'] = oc.DOMINIO.map(DOMINIOS)
    oc['sexo'] = oc.P02A02.map({1: 'Hombre', 2: 'Mujer'}).fillna('Sin clasificar')
    oc['edad'] = pd.cut(oc.P02A03, [15,25,45,65,np.inf], right=False,
                        labels=['15–24','25–44','45–64','65+'])
    oc['tamano'] = oc.P05C13.map(TAMANOS).fillna('Sin clasificar')
    oc['condicion'] = oc.FORMAL_INFORMAL.map({1:'Informal', 2:'Formal'}).fillna('Sin clasificar')
    oc['grupo_ciiu'] = oc.P05C04_2D.map({d:g for d, (_,g,_) in divisiones.items()}).fillna('Sin clasificar')
    rama = oc.P05C04_2D.map({d:r for d, (_,_,r) in divisiones.items()})
    if (rama.notna() & rama.ne(oc.P05C04_1D)).any():
        raise ValueError('P05C04_1D incompatible con CIIU')
    oc['rama_ine'] = rama.astype('Int64').astype('string').fillna('Sin clasificar')
    return oc


def porcentaje(n, d):
    return 100 * n / d if d else None


def resumir(ocupados):
    total_informal = ocupados.loc[ocupados.FORMAL_INFORMAL.eq(1), 'FACTOR'].sum()
    filas = []
    for dim in ['nacional','dominio','sexo','edad','tamano','grupo_ciiu','rama_ine','condicion']:
        for categoria, g in ocupados.groupby(dim, observed=True, sort=True):
            total = g.FACTOR.sum()
            c = g[g.FORMAL_INFORMAL.isin([1,2])]
            i = g[g.FORMAL_INFORMAL.eq(1)]
            y = g.loc[g.YLAB_PUBLI.notna()].sort_values('YLAB_PUBLI')
            py = y.FACTOR.sum()
            media = mediana = None
            if py:
                media = (y.YLAB_PUBLI * y.FACTOR).sum() / py
                mediana = y.loc[y.FACTOR.cumsum().ge(py / 2), 'YLAB_PUBLI'].iloc[0]
            filas.append(dict(periodo=PERIODO, dimension=dim, categoria=str(categoria),
                n_ocupados=len(g), peso_ocupados=total, n_clasificados=len(c), peso_clasificados=c.FACTOR.sum(),
                cobertura_condicion_pct=porcentaje(c.FACTOR.sum(),total), n_informal=len(i),
                peso_informal=i.FACTOR.sum(), peso_formal=c.loc[c.FORMAL_INFORMAL.eq(2),'FACTOR'].sum(),
                tasa_sector_informal=porcentaje(i.FACTOR.sum(),c.FACTOR.sum()),
                composicion_informal_pct=porcentaje(i.FACTOR.sum(),total_informal) if dim=='grupo_ciiu' else None,
                n_ingreso=len(y), n_ingreso_cero=int(y.YLAB_PUBLI.eq(0).sum()), peso_ingreso=py,
                cobertura_ingreso_pct=porcentaje(py,total), media_ingreso=media, mediana_ingreso=mediana,
                estado='solo_revision_interna'))
    return pd.DataFrame(filas)
