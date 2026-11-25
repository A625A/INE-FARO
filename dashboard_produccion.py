"""Vista nacional de producción informal a partir del contrato Banguat."""
import altair as alt
import streamlit as st

from dashboard_data import ANIOS_VAB, PRECIOS
from dashboard_ui import AZUL, barras, cifras, descargar_csv, grafico, mostrar_tabla, selector, titulo

MILLONES = 'Millones de quetzales'
CAPTION = 'Banco de Guatemala · Cuadros 12 y 5.103 · 2023 y 2024 preliminares'


def serie_historica(datos, medida, unidad):
    # Vega recibe dos series separadas. Ninguna línea cruza el año ausente.
    serie = datos.assign(tramo=datos.anio.gt(2020), revision_visible=datos.preliminar.map(
        {True: 'Preliminar', False: 'Histórico'}))
    return alt.Chart(serie).mark_line(color=AZUL, point=True, strokeWidth=2).encode(
        x=alt.X('anio:Q', title='Año', scale=alt.Scale(domain=[2013, 2024], nice=False),
                axis=alt.Axis(format='d', tickMinStep=1)),
        y=alt.Y(f'{medida}:Q', title=unidad, scale=alt.Scale(zero=True)),
        detail='tramo:N',
        tooltip=[alt.Tooltip('anio:Q', title='Año', format='d'),
                 alt.Tooltip(f'{medida}:Q', title=unidad, format=',.2f'),
                 alt.Tooltip('revision_visible:N', title='Estado de revisión')],
    ).properties(height=240)


def mostrar_produccion(nacional, grupos):
    titulo('Producción', '¿Cuánto valor agregado genera el sector informal y en qué actividades se concentra?',
           'Guatemala · 2013–2024 · Banco de Guatemala')
    izquierda, derecha = st.columns(2)
    anio = selector('Año del perfil productivo', list(reversed(ANIOS_VAB)), 'anio_vab',
                    default=2023, contenedor=izquierda)
    precio = selector('Tipo de precio', list(PRECIOS), 'precio_vab', formato=PRECIOS.get,
                      contenedor=derecha)
    nominal = precio == 'corrientes'
    serie = nacional[nacional.tipo_precio.eq(precio)]
    corte = serie[serie.anio.eq(anio)].iloc[0]
    sectores = grupos[grupos.anio.eq(anio) & grupos.tipo_precio.eq(precio)]
    comercio = sectores.loc[sectores.grupo_ciiu.eq('G'), 'composicion_pct'].item()
    medidas = [('VAB informal nacional', f'Q {corte.vab_informal:,.2f}', MILLONES)]
    if nominal:
        medidas.extend([
            ('VAB total nacional', f'Q {corte.vab_total:,.2f}', MILLONES),
            ('Participación informal', f'{corte.participacion_informal_pct:.2f} %', 'Del VAB total'),
            ('Comercio y reparación', f'{comercio:.2f} %', 'Del VAB del sector informal'),
        ])
    cifras(medidas)
    st.caption(f'{anio} · {"Cifras preliminares y revisables" if corte.preliminar else "Serie histórica"} · {PRECIOS[precio]} · Revisión {corte.revision}.')
    st.divider()
    if nominal:
        st.subheader('Evolución de la participación informal')
        grafico(serie_historica(serie, 'participacion_informal_pct', 'Participación en el VAB total (%)'))
        with st.expander('Serie de importes corrientes'):
            grafico(serie_historica(serie, 'vab_informal', MILLONES))
    else:
        st.subheader('Evolución en volumen encadenado')
        grafico(serie_historica(serie, 'vab_informal', f'{MILLONES} · referencia 2013'))
        st.caption('Los componentes encadenados pueden ser no aditivos. Las participaciones se publican para precios corrientes.')
    st.caption(f'{CAPTION}. En 2020 no se desagregó la producción informal, porque no se realizó la ENEI.')
    descargar_csv(serie, 'Descargar serie nacional visible', 'vab-informal-serie.csv')
    st.divider()
    if nominal:
        dos_barras(sectores)
    else:
        st.subheader(f'VAB del sector informal por actividad · {anio}')
        grafico(barras(sectores, 'grupo_nombre', 'vab_informal', MILLONES, [
            alt.Tooltip('grupo_nombre:N', title='Actividad'),
            alt.Tooltip('vab_informal:Q', title=MILLONES, format=',.2f'),
        ]))
    st.caption(f'{CAPTION}. Las estimaciones tienen alcance nacional.')
    with st.expander('Tabla y denominadores del perfil productivo'):
        legibles = {'grupo_ciiu': 'CIIU', 'grupo_nombre': 'Actividad', 'vab_informal': 'VAB informal (millones de Q)'}
        if nominal:
            legibles.update(vab_total_grupo='VAB total de la rama (millones de Q)',
                            composicion_pct='Del VAB informal (%)',
                            participacion_informal_grupo_pct='Dentro de la actividad (%)')
        mostrar_tabla(sectores[list(legibles)].rename(columns=legibles))
    descargar_csv(sectores, f'Descargar actividades de {anio}', f'vab-informal-actividades-{anio}.csv')


def dos_barras(sectores):
    for campo, encabezado, unidad, denominador in (
        ('composicion_pct', 'Composición del VAB informal',
         'Participación en el VAB informal nacional (%)', 'VAB informal nacional'),
        ('participacion_informal_grupo_pct', 'Participación informal dentro de cada actividad',
         'Participación en el VAB de la actividad (%)', 'VAB total de cada actividad'),
    ):
        st.subheader(encabezado)
        grafico(barras(sectores, 'grupo_nombre', campo, unidad, [
            alt.Tooltip('grupo_nombre:N', title='Actividad'),
            alt.Tooltip(f'{campo}:Q', title=unidad, format='.2f'),
            alt.Tooltip('vab_informal:Q', title='VAB informal (millones de Q)', format=',.2f'),
        ], dominio=[0, 100] if campo == 'participacion_informal_grupo_pct' else None))
        st.caption(f'Denominador · {denominador}.')
