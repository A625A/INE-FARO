"""I-02: inventario y controles estructurales, sin estimar tasas poblacionales."""

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
from openpyxl import load_workbook

BASES = {
    'personas': ('encovi_2023_personas', 'persona', ['NO_HOGAR', 'CP']),
    'hogares': ('encovi_2023_hogares', 'hogar', ['NO_HOGAR']),
    'consumo': ('encovi_2023_agregado_consumo', 'hogar con consumo', ['NO_HOGAR']),
    'negocios_1': ('encovi_2023_c14sa_negocios_1', 'hogar', ['NO_HOGAR']),
    'negocios_2': ('encovi_2023_c14sa_negocios_2', 'negocio del hogar', ['NO_HOGAR', 'ID_NEGOCIO']),
}
PESOS = ['FACTOR', 'Factor2', 'Factor3']
PROPUESTAS = ['ingreso_hogar', 'ingreso_per_capita', 'informalidad', 'tipo_ocupacion',
              'sector_actividad', 'consumo_total', 'n_hogar']
RESUMEN_INE = {'PET', 'PEA', 'OCUPADOS', 'DESOCUPADOS', 'FORMAL_INFORMAL',
               'POBREZA', 'pobreza', 'pob_gen', 'pob_ext', 'pob_no', 'FACTOR', 'Factor2', 'Factor3'}


def json_texto(valor):
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, allow_nan=False)


def cargar_bases(directorio, precargadas=None):
    precargadas = precargadas or {}
    return {nombre: precargadas[nombre] if nombre in precargadas else pyreadstat.read_sav(directorio / f'{archivo}.sav', user_missing=True,
                                       disable_datetime_conversion=True)
            for nombre, (archivo, _, _) in BASES.items()}


def variables_xlsx(path):
    libro = load_workbook(path, read_only=True, data_only=True)
    variables = {}
    activo = False
    try:
        for fila in libro.active.values:
            if fila[0] == 'Variable' and fila[1] == 'Posición':
                activo = True
                continue
            if activo and fila[0] in ('Variables en el archivo de trabajo', 'Valores de variable'):
                break
            if activo and isinstance(fila[0], str) and isinstance(fila[1], (int, float)):
                variables[fila[0].casefold()] = {'nombre': fila[0], 'etiqueta': fila[2]}
    finally:
        libro.close()
    return variables


def validar_clave(frame, columnas):
    if frame[columnas].isna().any(axis=None):
        raise ValueError(f'Clave con faltantes: {columnas}')
    if frame.duplicated(columnas).any():
        raise ValueError(f'Clave duplicada: {columnas}')


def unir_a_hogares(frame, hogares, many=False, upm='UPM'):
    """Unión de comprobación; valida cardinalidad y conserva todas las filas hijas."""
    hijo = frame[['NO_HOGAR', 'DEPTO', upm]].rename(columns={upm: 'upm_hijo'})
    padre = hogares[['NO_HOGAR', 'DEPTO', 'UPM']]
    unido = hijo.merge(padre, on='NO_HOGAR', how='left', indicator=True,
                       suffixes=('_hijo', '_hogar'),
                       validate='many_to_one' if many else 'one_to_one')
    assert len(unido) == len(frame)
    ambos = unido['_merge'].eq('both')
    return {
        'cardinalidad': 'muchos_a_uno' if many else 'uno_a_uno',
        'filas_antes': len(frame), 'filas_despues': len(unido),
        'filas_sin_hogar': int((~ambos).sum()),
        'hogares_sin_registro_hijo': int((~hogares.NO_HOGAR.isin(frame.NO_HOGAR)).sum()),
        'departamento_discordante': int((ambos & unido.DEPTO_hijo.ne(unido.DEPTO_hogar)).sum()),
        'upm_discordante': int((ambos & unido.upm_hijo.ne(unido.UPM)).sum()),
    }


def crear_diccionario(bases, directorio):
    filas, contraste = [], {}
    especiales = re.compile(r'no sabe|no responde|no respondió|no especificado|sin información', re.I)
    for base, (frame, meta) in bases.items():
        archivo, unidad, _ = BASES[base]
        xlsx = variables_xlsx(directorio / f'dd_{archivo}.xlsx')
        nombres_sav = {v.casefold() for v in frame}
        contraste[base] = {
            'variables_sav': len(frame.columns), 'variables_xlsx': len(xlsx),
            'solo_sav': [v for v in frame if v.casefold() not in xlsx],
            'solo_xlsx': [v['nombre'] for k, v in xlsx.items() if k not in nombres_sav],
        }
        for variable in frame:
            serie = frame[variable]
            etiquetas = meta.variable_value_labels.get(variable, {})
            rangos = meta.missing_ranges.get(variable, [])
            mascara = pd.Series(False, index=serie.index)
            for rango in rangos:
                mascara |= serie.between(rango['lo'], rango['hi'])
            codigos_especiales = {k: v for k, v in etiquetas.items() if especiales.search(v)}
            sin_etiqueta = serie.notna() & ~serie.isin(etiquetas) if etiquetas else pd.Series(False, index=serie.index)
            no_etiquetados = sorted(float(v) for v in serie[sin_etiqueta].unique()) if etiquetas and pd.api.types.is_numeric_dtype(serie) else []
            original = xlsx.get(variable.casefold(), {})
            filas.append({
                'base': base, 'archivo_origen': f'{archivo}.sav',
                'diccionario_origen': f'dd_{archivo}.xlsx', 'unidad_observacion': unidad,
                'variable': variable, 'naturaleza': 'original_publicada',
                'calculada_por_ine': 'si' if variable in RESUMEN_INE else 'no_determinado',
                'tipo_sav': meta.readstat_variable_types[variable],
                'etiqueta_sav': meta.column_names_to_labels.get(variable) or '',
                'etiqueta_xlsx': original.get('etiqueta') or '',
                'presente_xlsx': 'si' if original else 'no',
                'codigos_etiquetas': json_texto(etiquetas),
                'n_registros': len(frame), 'valores_distintos_no_nulos': int(serie.nunique()),
                'faltantes_sistema': int(serie.isna().sum()),
                'cadenas_vacias': int(serie.str.strip().eq('').sum()) if pd.api.types.is_string_dtype(serie) else 0,
                'faltantes_declarados_sav': json_texto(rangos),
                'n_faltantes_declarados': int(mascara.sum()),
                'codigos_especiales_etiquetados': json_texto(codigos_especiales),
                'n_codigos_especiales': int(serie.isin(codigos_especiales).sum()),
                'codigos_observados_sin_etiqueta': json_texto(no_etiquetados),
                'n_codigos_sin_etiqueta': int(sin_etiqueta.sum()),
                'formula': 'Factor2 * personas (etiqueta INE; no recalculada como ponderador)' if variable == 'Factor3' else
                    'No proporcionada por el diccionario; no recalculada; consultar docs/metodologia.md' if variable in RESUMEN_INE else '',
                'nota_metodologica': 'Uso definido en docs/metodologia.md; no intercambiar' if variable in PESOS else
                    'Consultar universo y códigos de docs/metodologia.md' if variable in RESUMEN_INE else '',
            })
    columnas = list(filas[0])
    for nombre in PROPUESTAS:
        assert not any(nombre in frame.columns for frame, _ in bases.values())
        fila = dict.fromkeys(columnas, '')
        fila.update(base='propuestas_previas', variable=nombre,
                    naturaleza='derivada_propuesta_no_implementada',
                    archivo_origen='No es columna original de las cinco bases inspeccionadas',
                    unidad_observacion='Pendiente de definición',
                    formula='Sin fórmula aprobada ni transformación implementada',
                    pendiente_I03='Sin transformación acreditada; no utilizar como columna original')
        filas.append(fila)
    return pd.DataFrame(filas), contraste


def auditar_bases(bases):
    auditoria, categorias, pesos, cobertura = {}, [], [], []
    for base, (frame, meta) in bases.items():
        _, unidad, clave = BASES[base]
        validar_clave(frame, clave)
        assert frame.DEPTO.isin(range(1, 23)).all()
        auditoria[base] = {'filas': len(frame), 'columnas': len(frame.columns),
            'unidad': unidad, 'clave': clave, 'duplicados_clave': 0, 'faltantes_clave': 0,
            'hogares_distintos': int(frame.NO_HOGAR.nunique()),
            'celdas_faltantes_sistema': int(frame.isna().sum().sum())}
        for depto, n in frame.DEPTO.value_counts().sort_index().items():
            cobertura.append({'base': base, 'depto_id': f'{int(depto):02}', 'n_registros': int(n)})
        for variable in ['POBREZA', 'pobreza', 'FORMAL_INFORMAL', 'PET', 'PEA', 'OCUPADOS', 'DOMINIO', 'AREA', 'P14A01']:
            if variable not in frame:
                continue
            for codigo, n in frame[variable].value_counts().sort_index().items():
                categorias.append({'base': base, 'variable': variable, 'codigo': float(codigo),
                    'etiqueta': meta.variable_value_labels.get(variable, {}).get(codigo, 'Sin etiqueta SAV'),
                    'n_no_ponderado': int(n)})
        for variable in PESOS:
            if variable in frame:
                serie = frame[variable]
                pesos.append({'base': base, 'variable': variable,
                    'etiqueta': meta.column_names_to_labels[variable],
                    'faltantes': int(serie.isna().sum()), 'ceros': int(serie.eq(0).sum()),
                    'negativos': int(serie.lt(0).sum()), 'no_finitos': int((~np.isfinite(serie)).sum())})
    p, h, c, n1, n2 = [bases[k][0] for k in BASES]
    uniones = {base: unir_a_hogares(bases[base][0], h,
               many=base in ('personas', 'negocios_2'), upm='SECTOR' if base == 'consumo' else 'UPM')
               for base in ('personas', 'consumo', 'negocios_1', 'negocios_2')}
    for resultado in uniones.values():
        assert resultado['filas_sin_hogar'] == 0
        assert resultado['departamento_discordante'] == resultado['upm_discordante'] == 0
    sin_consumo = h.loc[~h.NO_HOGAR.isin(c.NO_HOGAR)]
    pc = p[['NO_HOGAR', 'FACTOR', 'Factor2']].groupby('NO_HOGAR').first().reset_index()
    repeticion = p.groupby('NO_HOGAR')[['FACTOR', 'Factor2']].nunique(dropna=False)
    chequear = c[['NO_HOGAR', 'FACTOR', 'Factor3', 'personas']].merge(pc, on='NO_HOGAR',
                           validate='one_to_one', suffixes=('_consumo', '_personas'))
    tamaños = p.groupby('NO_HOGAR').size().reindex(c.NO_HOGAR).to_numpy()
    def coinciden(a, b):
        return int(np.isclose(a, b, rtol=1e-10, atol=1e-8).sum())
    ch = c[['NO_HOGAR', 'Factor3']].merge(h[['NO_HOGAR', 'Factor3']], on='NO_HOGAR', validate='one_to_one', suffixes=('_c', '_h'))
    ph = pc.merge(h[['NO_HOGAR', 'FACTOR']], on='NO_HOGAR', validate='one_to_one', suffixes=('_p', '_h'))
    relaciones_pesos = {
        'hogares_con_pesos_personas_no_constantes': int(repeticion.gt(1).any(axis=1).sum()),
        'n_comparados': len(chequear),
        'consumo_FACTOR_igual_personas_Factor2': coinciden(chequear.FACTOR_consumo, chequear.Factor2),
        'consumo_FACTOR_vs_personas_Factor2_max_diferencia_absoluta': float(np.abs(chequear.FACTOR_consumo-chequear.Factor2).max()),
        'consumo_FACTOR_vs_personas_Factor2_discordancias_rtol_1e5': int((~np.isclose(chequear.FACTOR_consumo, chequear.Factor2, rtol=1e-5, atol=1e-8)).sum()),
        'consumo_Factor3_igual_personas_Factor2_por_personas': coinciden(chequear.Factor3, chequear.Factor2 * chequear.personas),
        'consumo_Factor3_igual_consumo_FACTOR_por_personas': coinciden(chequear.Factor3, chequear.FACTOR_consumo * chequear.personas),
        'consumo_Factor3_igual_hogares_Factor3': coinciden(ch.Factor3_c, ch.Factor3_h),
        'consumo_Factor3_vs_hogares_Factor3_max_diferencia_absoluta': float(np.abs(ch.Factor3_c-ch.Factor3_h).max()),
        'consumo_Factor3_vs_hogares_Factor3_discordancias_rtol_1e5': int((~np.isclose(ch.Factor3_c, ch.Factor3_h, rtol=1e-5, atol=1e-8)).sum()),
        'personas_FACTOR_igual_hogares_FACTOR': coinciden(ph.FACTOR_p, ph.FACTOR_h),
        'tamano_consumo_igual_conteo_personas': coinciden(c.personas, tamaños),
        'tolerancia_numpy': {'rtol': 1e-10, 'atol': 1e-8},
    }
    consumo = {'guia_hogares_con_consumo': 10930, 'observados': len(c),
        'diferencia_con_guia': len(c)-10930, 'hogares_sin_consumo': len(sin_consumo),
        'personas_en_hogares_sin_consumo': int((~p.NO_HOGAR.isin(c.NO_HOGAR)).sum()),
        'clasificacion_pobreza_sin_consumo': {str(int(k)): int(v) for k, v in sin_consumo.POBREZA.value_counts().items()},
        'Factor3_cero_sin_consumo': int(sin_consumo.Factor3.eq(0).sum())}
    assert consumo['diferencia_con_guia'] == 0
    declaran = n1.loc[n1.P14A01.eq(1), 'NO_HOGAR']
    cantidades = n1.loc[n1.P14A01.eq(1), ['NO_HOGAR', 'P14A02A']].merge(
        n2.groupby('NO_HOGAR').size().rename('detalles'), on='NO_HOGAR', validate='one_to_one', how='left')
    negocios = {'hogares_declaran_negocio': len(declaran), 'hogares_con_detalle': int(n2.NO_HOGAR.nunique()),
        'declaran_sin_detalle': int((~declaran.isin(n2.NO_HOGAR)).sum()),
        'filas_detalle_fuera_hogares_declaran': int((~n2.NO_HOGAR.isin(declaran)).sum()),
        'suma_P14A02A_todos_hogares': float(n1.P14A02A.sum()),
        'suma_P14A02A_hogares_declarantes': float(cantidades.P14A02A.sum()), 'filas_detalle': len(n2),
        'hogares_no_declarantes_con_cantidad': int((n1.P14A01.ne(1) & n1.P14A02A.notna()).sum()),
        'hogares_no_declarantes_con_cantidad_positiva': int((n1.P14A01.ne(1) & n1.P14A02A.gt(0)).sum()),
        'saldo_detalle_menos_declarado_en_declarantes': float(cantidades.detalles.sum() - cantidades.P14A02A.sum()),
        'hogares_discrepantes_tambien_sin_consumo': int(cantidades.loc[cantidades.P14A02A.ne(cantidades.detalles), 'NO_HOGAR'].isin(sin_consumo.NO_HOGAR).sum()),
        'hogares_cantidad_declarada_distinta_del_detalle': int(cantidades.P14A02A.ne(cantidades.detalles).sum()),
        'hogares_declaran_con_cantidad_faltante': int(cantidades.P14A02A.isna().sum())}
    return {'bases': auditoria, 'categorias': categorias, 'pesos': pesos,
            'cobertura': cobertura, 'uniones_a_hogares': uniones, 'consumo': consumo,
            'relaciones_pesos': relaciones_pesos, 'negocios': negocios,
            'tasas_poblacionales_calculadas': False, 'I03': 'Publicada en main; se conserva docs/metodologia.md sin recalcular indicadores'}


def guardar_resultados(root, diccionario, informe, contraste):
    destino = root / 'docs/evidencia/I-02'
    destino.mkdir(parents=True, exist_ok=True)
    raw = root / 'data/raw/encovi_2023'
    archivos = [raw / f'{archivo}{extension}' for archivo, _, _ in BASES.values()
                for extension in ['.sav']]
    archivos += [raw / f'dd_{archivo}.xlsx' for archivo, _, _ in BASES.values()]
    archivos.append(raw / 'Guia-para-el-uso-de-bases-de-datos_v_final.pdf')
    fuentes = [{'archivo': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                'bytes': p.stat().st_size} for p in archivos]
    informe = {**informe, 'contraste_xlsx': contraste, 'insumos': fuentes,
        'privacidad': 'Sólo metadatos y conteos agregados; sin filas individuales ni identificadores.',
        'referencia_metodologica': 'docs/metodologia.md',
        'decisiones_I03_conservadas': {'informalidad': 'FACTOR en ocupados de 15 años o más',
                                      'pobreza': 'Factor3 en Agregado de Consumo',
                                      'precision': 'aproximado_depto_upm'},
        'limitacion_negocios': 'Cantidades no conciliadas; no se imputan ni se atribuye una causa no demostrada'}
    diccionario.to_csv(destino / 'diccionario_detallado.csv', sep=';', index=False)
    (destino / 'validacion.json').write_text(json.dumps(informe, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    pd.DataFrame(informe['cobertura']).to_csv(destino / 'cobertura_departamental.csv', index=False)
    return informe
