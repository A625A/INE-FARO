"""Mapa, perfiles departamentales y contexto de hogares."""
import json

import altair as alt
import pandas as pd
import streamlit as st

from dashboard_data import CAMPO_PIB, DEPARTAMENTOS, GROUPS, NOMBRES_ENCOVI, PERFILES, PIB
from dashboard_precision import ETIQUETAS_PRECISION
from dashboard_ui import (AZUL, AZUL_CLARO, SECCIONES, cifras, descargar_csv, grafico, mostrar_tabla,
                          navegar, selector, titulo)
from dashboard_utils import RESTRINGIDA
from scripts.radar_rules.inputs import sector_fields

PREVALENTE = 'actividad_predominante_2023'
ESTRUCTURA = 'participacion_predominante_pct_2023'
INDICADORES_MAPA = {**NOMBRES_ENCOVI, CAMPO_PIB: PIB,
                   ESTRUCTURA: 'Peso de la actividad predominante', PREVALENTE: 'Actividad predominante'}
ACTIVIDADES = dict(zip(GROUPS, (
    'Agricultura', 'Minas y canteras', 'Manufacturas', 'Electricidad, gas y agua',
    'Construcción', 'Comercio', 'Transporte', 'Alojamiento y comidas', 'Información',
    'Finanzas y seguros', 'Inmobiliarias', 'Servicios profesionales', 'Servicios de apoyo',
    'Administración pública', 'Enseñanza', 'Salud y asistencia social', 'Otros servicios',
)))
GRUPOS_HOGARES = {
    'remesas_personas': 'Remesas',
    'negocios_hogares': 'Negocios familiares',
    'consumo_per_capita': 'Consumo per cápita',
}
HORIZONTES = {'ultimos_3_meses': 'Últimos tres meses', 'promedio_ultimos_3_meses': 'Promedio de tres meses',
              'actual': 'Situación declarada', 'mensual': 'Mensual', 'octubre_2023': 'Octubre de 2023'}
DENOMINADORES = {
    'ocupacion_sector_informal': 'Personas ocupadas de 15 años o más',
    'pobreza_total': 'Personas representadas por hogares con clasificación de consumo válida',
    'pobreza_extrema': 'Personas representadas por hogares con clasificación de consumo válida',
}
UNIDAD_PIB = 'Q corrientes por habitante'
RESTRICCION = 'N/D · precisión insuficiente'


def datos_mapa(matriz, encovi, indicador):
    if indicador in NOMBRES_ENCOVI:
        datos = encovi[encovi.indicador.eq(indicador)].copy()
        datos['calidad'] = datos.clasificacion.map(
            {**ETIQUETAS_PRECISION, RESTRINGIDA: RESTRICCION})
        datos['valor_visible'] = datos.valor.map(lambda v: RESTRICCION if pd.isna(v) else f'{v:.1f} %')
        datos['denominador'] = DENOMINADORES[indicador]
        return datos
    columnas = ['depto_id', 'departamento', 'anio', indicador]
    datos = matriz[columnas].rename(columns={indicador: 'valor'})
    datos['indicador'] = indicador
    datos['calidad'] = 'Preliminar'
    datos['fuente'] = 'Banco de Guatemala · cuadro 8' if indicador == CAMPO_PIB else 'Banco de Guatemala · cuadro 7'
    datos['denominador'] = ('Población departamental proyectada' if indicador == CAMPO_PIB
                            else 'VAB departamental corriente de 17 grupos')
    if indicador == CAMPO_PIB:
        datos['unidad'] = UNIDAD_PIB
        datos['valor_visible'] = datos.valor.map(lambda v: f'Q {v:,.0f} por habitante')
    elif indicador == PREVALENTE:
        datos['unidad'] = 'Grupo CIIU'
        datos['valor_visible'] = datos.valor.map(ACTIVIDADES)
    else:
        datos['unidad'] = 'Porcentaje del VAB territorial'
        datos['valor_visible'] = datos.valor.map(lambda v: f'{v:.1f} % del VAB')
    return datos


@st.cache_data(show_spinner=False)
def cargar_geometrias(ruta):
    entrada = json.loads(ruta.read_text(encoding='utf-8'))
    geometrias = {f['properties']['shapeName']: f['geometry'] for f in entrada['features']}
    if set(geometrias) != set(DEPARTAMENTOS.values()) or len(entrada['features']) != 22:
        raise ValueError('La geometría debe corresponder a los 22 departamentos.')
    for geometria in geometrias.values():
        if geometria['type'] not in ('Polygon', 'MultiPolygon'):
            raise ValueError('Geometría departamental incompatible.')
        # Vega y GeoJSON usan orientaciones opuestas para polígonos esféricos.
        poligonos = ([geometria['coordinates']] if geometria['type'] == 'Polygon'
                     else geometria['coordinates'])
        for poligono in poligonos:
            for anillo in poligono:
                anillo.reverse()
    return geometrias


def mapa_departamental(geometrias, datos, indicador, seleccionado):
    campos = ['depto_id', 'departamento', 'valor', 'valor_visible', 'calidad']
    valores = json.loads(datos[campos].to_json(orient='records', force_ascii=False))
    features = [dict(fila, type='Feature', geometry=geometrias[fila['departamento']]) for fila in valores]
    eje = alt.Color('valor:Q', title='Q por habitante' if indicador == CAMPO_PIB else '%',
                    scale=alt.Scale(scheme='blues', zero=True),
                    legend=alt.Legend(orient='bottom', direction='horizontal', gradientLength=140))
    if indicador == PREVALENTE:
        eje = alt.Color('valor_visible:N', title='Actividad', scale=alt.Scale(scheme='tableau20'),
                        legend=alt.Legend(orient='bottom', direction='horizontal', columns=2,
                                          labelLimit=125))
    seleccion = alt.selection_point(name='departamento_mapa', fields=['depto_id'],
                                    toggle=False, clear=False)
    return alt.Chart(alt.Data(values=features)).mark_geoshape().project(type='mercator').encode(
        color=alt.condition('isValid(datum.valor)', eje, alt.value('#a4a9af')),
        stroke=alt.condition(alt.datum.depto_id == seleccionado, alt.value('#172841'), alt.value('#ffffff')),
        strokeWidth=alt.condition(alt.datum.depto_id == seleccionado, alt.value(3.1), alt.value(1.1)),
        tooltip=[
            alt.Tooltip('departamento:N', title='Departamento'),
            alt.Tooltip('valor_visible:N', title=INDICADORES_MAPA[indicador]),
            alt.Tooltip('calidad:N', title='Calidad'),
        ],
    ).add_params(seleccion).properties(height=370, usermeta={'embedOptions': {'renderer': 'svg'}})


def seleccionar_mapa(clave):
    seleccion = st.session_state[clave].selection.get('departamento_mapa', [])
    if seleccion:
        codigo = seleccion[0].get('depto_id')
        if codigo in DEPARTAMENTOS:
            st.session_state.depto = codigo


def mostrar_territorio(matriz, encovi, ruta_mapa, radar, hogares):
    titulo('Territorio', '¿Cómo difieren las condiciones de vida y la producción entre departamentos?',
           '22 departamentos · 2023 · INE, ENCOVI y Banco de Guatemala')
    a, b, c = st.columns(3)
    indicador = selector('Indicador del mapa', list(INDICADORES_MAPA), 'indicador_mapa',
                          formato=INDICADORES_MAPA.get, contenedor=a)
    depto = selector('Departamento', list(DEPARTAMENTOS), 'depto',
                      formato=DEPARTAMENTOS.get, contenedor=b)
    comparar = selector('Comparar con', ['', *(d for d in DEPARTAMENTOS if d != depto)], 'comparar',
                         default='16', formato=lambda d: DEPARTAMENTOS.get(d, 'Sin comparación'),
                         contenedor=c)
    datos = datos_mapa(matriz, encovi, indicador)
    mapa, ficha = st.columns([1.15, 1])
    with mapa:
        st.subheader(INDICADORES_MAPA[indicador])
        try:
            geometrias = cargar_geometrias(ruta_mapa)
        except (OSError, ValueError, KeyError, TypeError):
            st.error('No se pudo cargar la geometría local. Usa el selector de departamento para explorar los perfiles.')
        else:
            clave = f'mapa_{indicador}'
            grafico(mapa_departamental(geometrias, datos, indicador, depto), key=clave,
                    on_select=lambda: seleccionar_mapa(clave), selection_mode='departamento_mapa')
            st.caption('Gris · estimación restringida. Límites de referencia: geoBoundaries / © colaboradores de OpenStreetMap (ODbL 1.0).')
        with st.expander('Valores y calidad de los 22 departamentos'):
            mostrar_tabla(datos[['departamento', 'valor_visible', 'calidad']].rename(columns={
                'departamento': 'Departamento', 'valor_visible': 'Valor', 'calidad': 'Calidad',
            }))
            descargar_csv(datos.drop(columns='valor_visible'), 'Descargar indicador del mapa',
                           f'mapa-{indicador}-2023.csv')
    with ficha:
        mostrar_perfil(matriz, encovi, radar, depto)
    st.divider()
    codigos = [depto] + ([comparar] if comparar else [])
    comparar_territorios(matriz, encovi, codigos)
    st.divider()
    dispersion(matriz, encovi, codigos)
    if hogares is not None:
        st.divider()
        mostrar_hogares(hogares, depto)


def mostrar_perfil(matriz, encovi, radar, depto):
    detalle = encovi[encovi.depto_id.eq(depto)].assign(
        denominador=lambda d: d.indicador.map(DENOMINADORES))
    fila = matriz[matriz.depto_id.eq(depto)].iloc[0]
    st.subheader(DEPARTAMENTOS[depto])
    cifras([
        (NOMBRES_ENCOVI[r.indicador], RESTRICCION if pd.isna(r.valor) else f'{r.valor:.1f} %',
         'Publicable con reserva' if pd.notna(r.valor) else '')
        for r in detalle.itertuples()
    ] + [(PIB, f'Q {fila[CAMPO_PIB]:,.0f}', 'Por habitante · preliminar')])
    st.write(f'**Actividad predominante** · {ACTIVIDADES[fila[PREVALENTE]]} ({fila[ESTRUCTURA]:.1f} % del VAB departamental).')
    st.caption('El PIB por habitante mide producción por persona. Las tasas ENCOVI de 2023 tienen precisión aproximada por DEPTO/UPM.')
    with st.expander('Muestra y precisión de las tasas'):
        tabla = detalle.assign(indicador=detalle.indicador.map(NOMBRES_ENCOVI))
        campos = {'indicador': 'Indicador', 'n': 'Muestra (n)', 'denominador': 'Universo',
                  'cv': 'CV (%)', 'ic95_inf': 'IC95 inferior (%)', 'ic95_sup': 'IC95 superior (%)',
                  'ponderador': 'Ponderador'}
        mostrar_tabla(tabla[list(campos)].rename(columns=campos))
        descargar_csv(detalle, 'Descargar tasas del perfil', f'perfil-encovi-{depto}.csv')
    if radar is not None:
        n = sum(depto in f['territorios'] for f in radar['hallazgos'])
        st.button(f'Consultar hallazgos relacionados ({n})', on_click=navegar,
                  args=(SECCIONES[3],), kwargs={'depto_radar': depto, 'regla_radar': 'Todas', 'ficha_radar': ''})


def comparar_territorios(matriz, encovi, codigos):
    st.subheader('Perfil productivo comparado' if len(codigos) == 2 else 'Perfil productivo')
    filas = matriz.set_index('depto_id').loc[codigos]
    if len(codigos) == 2:
        union = encovi[encovi.depto_id.isin(codigos)].pivot(index='indicador', columns='depto_id', values='valor')
        union = union.reindex(NOMBRES_ENCOVI).rename(index=NOMBRES_ENCOVI)
        union.loc[PIB] = filas[CAMPO_PIB]
        union['unidad'] = ['%', '%', '%', UNIDAD_PIB]
        union.columns = [DEPARTAMENTOS.get(c, 'Unidad') for c in union.columns]
        union = union.reset_index(names='Indicador')
        mostrar_tabla(union)
        st.caption('Tasas · INE, ENCOVI 2023, publicables con reserva. Las celdas vacías indican precisión insuficiente. PIB · Banguat 2023, preliminar.')
        descargar_csv(union, 'Descargar comparación de indicadores', 'comparacion-departamental.csv')
    estructura = pd.DataFrame([
        {'depto_id': codigo, 'departamento': fila.departamento, 'anio': fila.anio, 'ciiu': g,
         'actividad': ACTIVIDADES[g], 'participacion': fila[sector_fields(g)[1]],
         'denominador_millones_q': fila.vab_total_millones_q_2023, 'fuente': 'Banguat, cuadro 7',
         'revision': 'preliminar'}
        for codigo, fila in filas.iterrows() for g in GROUPS
    ])
    chart = alt.Chart(estructura).mark_bar(height=9 if len(codigos) > 1 else 15).encode(
        y=alt.Y('actividad:N', title=None, sort=list(ACTIVIDADES.values()), axis=alt.Axis(labelLimit=145)),
        x=alt.X('participacion:Q', title='Participación en el VAB departamental (%)',
                scale=alt.Scale(zero=True)),
        yOffset=alt.YOffset('departamento:N', sort=[DEPARTAMENTOS[d] for d in codigos]),
        color=alt.Color('departamento:N', title=None,
                        scale=alt.Scale(range=[AZUL, AZUL_CLARO][:len(codigos)]),
                        legend=alt.Legend(orient='top')),
        tooltip=[alt.Tooltip('departamento:N', title='Departamento'),
                 alt.Tooltip('ciiu:N', title='Grupo CIIU'),
                 alt.Tooltip('actividad:N', title='Actividad'),
                 alt.Tooltip('participacion:Q', title='Participación (%)', format='.2f'),
                 alt.Tooltip('denominador_millones_q:Q', title='VAB departamental (millones de Q)', format=',.2f')],
    ).properties(height=25 * len(GROUPS))
    grafico(chart)
    st.caption('Banco de Guatemala · Cuadro 7 · 17 grupos de actividad, precios corrientes de 2023, preliminar.')
    descargar_csv(estructura, 'Descargar estructura de los departamentos seleccionados', 'estructura-departamental.csv')


def dispersion(matriz, encovi, codigos):
    st.subheader('PIB por habitante y ocupación en el sector informal')
    tasa = encovi[encovi.indicador.eq('ocupacion_sector_informal')].dropna(subset=['valor'])
    puntos = tasa[['depto_id', 'departamento', 'valor', 'clasificacion']].merge(
        matriz[['depto_id', CAMPO_PIB]], on='depto_id', validate='one_to_one')
    puntos['seleccion'] = puntos.depto_id.isin(codigos)
    grafico(alt.Chart(puntos).mark_circle(size=85, opacity=.9).encode(
        x=alt.X(f'{CAMPO_PIB}:Q', title=UNIDAD_PIB, scale=alt.Scale(zero=True)),
        y=alt.Y('valor:Q', title='Ocupados en el sector informal (%)', scale=alt.Scale(domain=[0, 100])),
        color=alt.condition(alt.datum.seleccion, alt.value(AZUL), alt.value('#7299c0')),
        tooltip=[alt.Tooltip('departamento:N', title='Departamento'),
                 alt.Tooltip(f'{CAMPO_PIB}:Q', title=UNIDAD_PIB, format=',.0f'),
                 alt.Tooltip('valor:Q', title='Ocupados en el sector informal (%)', format='.1f')],
    ).properties(height=295))
    st.caption('ENCOVI y Banguat · 2023. El azul oscuro identifica la selección. El contraste es descriptivo y no permite inferir causalidad.')


def mostrar_hogares(hogares, depto):
    st.subheader('Perfiles de hogares y negocios')
    territorio = selector('Ámbito de hogares', ['nacional', 'departamental'], 'ambito_hogares',
                           default='departamental',
                           formato=lambda a: 'Guatemala · nacional' if a == 'nacional' else DEPARTAMENTOS[depto])
    codigo = '' if territorio == 'nacional' else depto
    corte = hogares[hogares.depto_id.eq(codigo)].copy()
    corte['horizonte_etiqueta'] = corte.horizonte.map(HORIZONTES)
    indicadores = {k: v for tabla in PERFILES.values() for k, v in tabla.items()}
    corte['indicador_etiqueta'] = corte.indicador.map(lambda k: indicadores[k][0])
    corte['denominador'] = corte.indicador.map(lambda k: indicadores[k][1])
    corte['advertencia'] = corte.n.map(lambda n: 'Muestra inferior a 100' if n < 100 else '')
    corte['valor_visible'] = [RESTRICCION if pd.isna(v) else f'{v:,.3f}' if u == 'negocios por hogar'
                             else f'{v:,.2f}' for v, u in zip(corte.valor, corte.unidad)]
    st.caption('INE, ENCOVI 2023 · Precisión aproximada. Las medidas conservan sus horizontes y universos.')
    if corte.n.lt(100).any():
        st.warning('La selección incluye estimaciones con muestra inferior a 100. Consulta el tamaño de muestra por indicador.')
    for clave, nombre in GRUPOS_HOGARES.items():
        st.markdown(f'**{nombre}**')
        campos = {'indicador_etiqueta': 'Indicador', 'valor_visible': 'Valor',
                  'unidad': 'Unidad', 'horizonte_etiqueta': 'Horizonte',
                  'n': 'Muestra (n)', 'denominador': 'Universo', 'advertencia': 'Advertencia'}
        mostrar_tabla(corte.loc[corte.tabla.eq(clave), list(campos)].rename(columns=campos))
    st.caption('Cobertura de negocios · 73 hogares muestran discrepancias entre negocios declarados y detallados. Ventas y ganancias usan el detalle disponible. Los cruces de pobreza por hogares formales, informales y mixtos siguen pendientes.')
    descargar_csv(corte.drop(columns='valor_visible'), 'Descargar perfil de hogares visible',
                   f'hogares-{codigo or "nacional"}-2023.csv')
