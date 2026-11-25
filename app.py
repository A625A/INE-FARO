"""M-05: interfaz local de INE FARO."""
import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from dashboard_precision import METODO, leyenda, marca, mostrar_calidad
from dashboard_utils import INDICADORES, cargar_encovi, cargar_pib

ROOT = Path(__file__).resolve().parent
PROCESADOS = ROOT / 'data/processed'
PIB = 'PIB por habitante'
UNIDAD_PIB = 'Quetzales por habitante'
NO_DISPONIBLE = 'N/D — precisión insuficiente'
NOMBRES_ENCOVI = dict(zip(INDICADORES, (
    'Ocupación en el sector informal', 'Pobreza total', 'Pobreza extrema',
)))
ERROR_CSV = (OSError, ValueError, pd.errors.ParserError)


def grafica_pib(tabla, seleccionado):
    return alt.Chart(tabla).mark_bar().encode(
        y=alt.Y('departamento:N', sort='-x', title=None, axis=alt.Axis(labelOverlap=False)),
        x=alt.X('pib_per_capita:Q', title=UNIDAD_PIB, axis=alt.Axis(format=',.0f')),
        color=alt.condition(alt.datum.departamento == seleccionado,
                            alt.value('#174e61'), alt.value('#829ba5')),
        tooltip=[alt.Tooltip('departamento:N', title='Departamento'),
                 alt.Tooltip('pib_per_capita:Q', title=UNIDAD_PIB, format=',.0f')],
    ).properties(height=max(120, 23 * len(tabla)))


def mapa_pib(tabla, seleccionado):
    ruta = ROOT / 'data/reference/departamentos_m05.geojson'
    geometrias = json.loads(ruta.read_text(encoding='utf-8'))['features']
    # Vega usa la orientación esférica opuesta a la del GeoJSON original.
    for figura in geometrias:
        geometria = figura['geometry']
        poligonos = ([geometria['coordinates']] if geometria['type'] == 'Polygon'
                     else geometria['coordinates'])
        for poligono in poligonos:
            for anillo in poligono:
                anillo.reverse()
    return alt.Chart(alt.Data(values=geometrias)).mark_geoshape(stroke='white').transform_lookup(
        lookup='properties.shapeName',
        from_=alt.LookupData(tabla, 'departamento', ['departamento', 'pib_per_capita']),
    ).project(type='mercator').encode(
        color=alt.Color('pib_per_capita:Q', title=UNIDAD_PIB, scale=alt.Scale(scheme='blues'),
                        legend=alt.Legend(orient='bottom', format=',.0f')),
        strokeWidth=alt.condition(alt.datum.departamento == seleccionado,
                                  alt.value(2.5), alt.value(0.8)),
        tooltip=[alt.Tooltip('departamento:N', title='Departamento'),
                 alt.Tooltip('pib_per_capita:Q', title=UNIDAD_PIB, format=',.0f')],
    ).properties(height=440)


st.set_page_config(page_title='INE FARO | Radar territorial', layout='wide')
st.html('''<style>
    [data-testid="stMainBlockContainer"] {max-width: 1520px; padding-top: 3.5rem;}
    [data-testid="stMain"] :is(h1, h2) {font-family: Georgia, "Times New Roman", serif; font-weight: 500; color: #173f4a;}
    [data-testid="stMetricValue"] {font-variant-numeric: tabular-nums;}
    .marca {display: inline-flex; align-items: center; gap: 8px; color: var(--tinta);
            font-weight: 600; font-size: 0.9375rem;}
    [data-testid="stCaptionContainer"] p {color: #52636a;}
    .marca > span {width: 12px; height: 12px; border-radius: 50%; background: var(--tinta);}
    .leyenda {display: flex; flex-wrap: wrap; gap: 8px 24px; padding: 12px 0;
              border-block: 1px solid #cbd3d4; font-size: 0.9375rem;}
    </style>''')
st.title('INE FARO')
st.caption('Radar territorial de Guatemala · 22 departamentos')

try:
    tabla = cargar_pib(PROCESADOS)
except ERROR_CSV as exc:
    st.error(f'No se pudo cargar el PIB: {exc}')
    st.stop()

try:
    encovi = cargar_encovi(PROCESADOS, tabla)
    if encovi is None:
        st.warning('El archivo de ENCOVI 2023 aún no está disponible. Se muestra únicamente el PIB.')
except ERROR_CSV as exc:
    encovi = None
    st.warning(f'Se muestra únicamente el PIB. Revisá el archivo de ENCOVI 2023: {exc}')

territorio, comparacion, radar, calidad = st.tabs([
    'Departamento', 'Comparar departamentos', 'Hallazgos del radar', 'Calidad estadística',
])
departamentos = tabla.departamento.tolist()

with territorio:
    seleccionado = st.selectbox('Departamento', departamentos)
    fila = tabla.loc[tabla.departamento.eq(seleccionado)].iloc[0]
    st.header(seleccionado)
    ficha = st.columns(4) if encovi is not None else [st.container()]
    ficha[0].metric(f'{PIB} · 2023', f'Q {fila.pib_per_capita:,.0f}')

    if len(ficha) > 1:
        detalle = encovi.loc[encovi.depto_id.eq(fila.depto_id)].set_index('indicador')
        for tarjeta, (clave, nombre) in zip(ficha[1:], NOMBRES_ENCOVI.items()):
            valor = detalle.at[clave, 'valor']
            if pd.isna(valor):
                tarjeta.metric(nombre, 'N/D', help=NO_DISPONIBLE)
            else:
                tarjeta.metric(nombre, f'{valor:.1f} %')
            tarjeta.html(marca(detalle.at[clave, 'clasificacion']))
        leyenda()
        with st.expander('Fuente y precisión de ENCOVI'):
            campos = {
                'indicador': 'Indicador', 'valor': 'Valor (%)', 'fuente': 'Fuente', 'anio': 'Año',
                'n': 'Observaciones', 'cv': 'CV (%)', 'ic95_inf': 'IC 95 % inferior',
                'ic95_sup': 'IC 95 % superior', 'estado': 'Estado',
            }
            detalle = detalle.reset_index()
            detalle['indicador'] = detalle.indicador.map(NOMBRES_ENCOVI)
            detalle['estado'] = detalle.estado.map({
                'publicable_con_reserva': 'Publicable con reserva', 'no_publicable': NO_DISPONIBLE,
            })
            st.dataframe(detalle[list(campos)].rename(columns=campos), hide_index=True)
            st.write(METODO)

    st.caption('Fuente del PIB: Banco de Guatemala · 2023 · Precios corrientes · Quetzales por habitante. '
               'Cifras preliminares y revisables. Mide producción por persona, no ingreso familiar.')
    mapa, barras = st.columns([1.1, 1])
    with barras:
        st.subheader('PIB por habitante por departamento')
        st.altair_chart(grafica_pib(tabla, seleccionado))
    with mapa:
        st.subheader('Mapa del PIB por habitante')
        st.altair_chart(mapa_pib(tabla, seleccionado))
        st.caption('Límites de referencia: geoBoundaries / © colaboradores de OpenStreetMap (ODbL 1.0).')

with comparacion:
    st.header('Comparación departamental')
    seleccion = st.multiselect('Departamentos a comparar', departamentos,
                               default=['Guatemala', 'Quiché', 'Alta Verapaz'])
    if not seleccion:
        st.info('Seleccioná al menos un departamento.')
    else:
        elegidos = tabla.loc[tabla.departamento.isin(seleccion)]
        st.altair_chart(grafica_pib(elegidos, seleccionado))
        resumen = elegidos.set_index('depto_id')[['departamento', 'pib_per_capita']]
        if encovi is not None:
            valores = encovi.pivot(index='depto_id', columns='indicador', values='valor')
            resumen = resumen.join(valores)
        etiquetas = {'pib_per_capita': 'PIB por habitante (Q)', 'departamento': 'Departamento'}
        etiquetas.update({clave: f'{nombre} (%)' for clave, nombre in NOMBRES_ENCOVI.items()})
        st.dataframe(resumen.rename(columns=etiquetas).round(2), hide_index=True)
        st.caption('PIB: Banco de Guatemala, 2023, precios corrientes. Cifras preliminares y revisables.')
        if len(resumen.columns) > 2:
            st.caption('Tasas: INE, ENCOVI 2023. Estimaciones de precisión aproximada, publicables con reserva. '
                       f'Las celdas vacías indican «{NO_DISPONIBLE}».')
        if INDICADORES[0] in resumen:
            puntos = resumen.dropna(subset=[INDICADORES[0]])
            if len(puntos) >= 2:
                st.subheader('PIB por habitante y ocupación en el sector informal')
                st.altair_chart(alt.Chart(puntos).mark_circle(size=95, color='#174e61').encode(
                    x=alt.X('pib_per_capita:Q', title=UNIDAD_PIB),
                    y=alt.Y(f'{INDICADORES[0]}:Q', title='Ocupación en el sector informal (%)'),
                    tooltip=[alt.Tooltip('departamento:N', title='Departamento')],
                ))
                st.caption('El gráfico describe una asociación entre departamentos. No permite inferir causalidad.')

with radar:
    st.header('Hallazgos del radar')
    hallazgos = PROCESADOS / 'hallazgos.csv'
    if not hallazgos.exists():
        st.info('Los hallazgos de M-04 se mostrarán aquí con su regla, evidencia y limitaciones.')
    else:
        try:
            tabla_hallazgos = pd.read_csv(hallazgos)
            if 'estado' in tabla_hallazgos:
                tabla_hallazgos = tabla_hallazgos.loc[~tabla_hallazgos.estado.eq('no_publicable')]
            if tabla_hallazgos.empty:
                st.info('No hay hallazgos publicables para presentar.')
            else:
                st.dataframe(tabla_hallazgos, hide_index=True)
        except ERROR_CSV as exc:
            st.warning(f'No se pudo leer hallazgos.csv: {exc}')

with calidad:
    mostrar_calidad(encovi, NOMBRES_ENCOVI)
