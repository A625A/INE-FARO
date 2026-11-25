"""Presentación del diagnóstico de precisión departamental de ENCOVI."""
import altair as alt
import streamlit as st

from dashboard_utils import MAYOR, MODERADA, RESTRINGIDA, UMBRAL_PUBLICACION

COLORES = {MAYOR: '#175943', MODERADA: '#8a6000', RESTRINGIDA: '#575e62'}
ETIQUETAS_ESTADO = {
    'publicable_con_reserva': 'Publicable con reserva', 'no_publicable': RESTRINGIDA,
}
METODO = (
    'El coeficiente de variación (CV) expresa el error estándar como porcentaje de la '
    'estimación. Un CV mayor indica menor precisión relativa. El intervalo de confianza '
    'del 95 % resume la incertidumbre muestral alrededor de la estimación. '
    'La aproximación usa el departamento (DEPTO) como estrato y la unidad primaria de '
    'muestreo (UPM) como conglomerado. Al faltar los estratos originales y la corrección '
    'por población finita, los CV e intervalos pueden diferir de los oficiales del INE.'
)


def marca(clase):
    return (f'<span class="marca" style="--tinta:{COLORES[clase]}">'
            f'<span aria-hidden="true"></span>{clase}</span>')


def leyenda():
    st.caption('Precisión ENCOVI · Las estimaciones en verde y amarillo son publicables con reserva.')
    st.html('<div class="leyenda" aria-label="Leyenda de precisión">'
            f'<span>{marca(MAYOR)} · CV ≤ 20 %</span>'
            f'<span>{marca(MODERADA)} · 20 % &lt; CV ≤ 30 %</span>'
            f'<span>{marca(RESTRINGIDA)} · CV &gt; 30 %, n &lt; 30 o precisión indeterminada</span>'
            '</div>')


def grafica_cv(filas):
    # Vega recibe únicamente campos de diagnóstico, incluso en la descarga del gráfico.
    datos = filas[['departamento', 'indicador', 'cv', 'exceso_pp', 'n']].copy()
    datos['fila'] = datos.departamento
    if datos.indicador.nunique() > 1:
        datos['fila'] += ' · ' + datos.indicador
    orden = datos.sort_values('cv', ascending=False).fila.tolist()
    base = alt.Chart(datos).encode(
        y=alt.Y('fila:N', sort=orden, title=None, axis=alt.Axis(labelLimit=250)),
        x=alt.X('cv:Q', title='Coeficiente de variación (%)', scale=alt.Scale(zero=True),
                axis=alt.Axis(tickCount=5)),
    )
    barras = base.mark_bar(color='#63747a', size=16).encode(tooltip=[
        alt.Tooltip('departamento:N', title='Departamento'),
        alt.Tooltip('indicador:N', title='Indicador'),
        alt.Tooltip('cv:Q', title='CV (%)', format='.5f'),
        alt.Tooltip('exceso_pp:Q', title='Exceso (pp)', format='.5f'),
        alt.Tooltip('n:Q', title='Muestra (n)', format='d'),
    ])
    etiquetas = base.mark_text(align='left', dx=6, color='white', fontSize=12).encode(
        x=alt.datum(0), text=alt.Text('cv:Q', format='.2f'),
    )
    linea = alt.Chart(alt.Data(values=[{'umbral': UMBRAL_PUBLICACION}])).mark_rule(
        color='#173f4a', strokeDash=[4, 3], size=2,
    ).encode(x='umbral:Q')
    return (barras + etiquetas + linea).properties(height=alt.Step(32))


def mostrar_calidad(encovi, nombres):
    st.header('Calidad estadística')
    st.write('Precisión de las estimaciones departamentales de la ENCOVI 2023')
    if encovi is None:
        st.info('El diagnóstico requiere el archivo departamental de ENCOVI 2023.')
        return

    datos = encovi.assign(indicador=encovi.indicador.map(nombres))
    filtros = st.columns(3)
    for columna, campo, titulo, opciones in zip(
        filtros, ('departamento', 'indicador', 'clasificacion'),
        ('Departamento', 'Indicador', 'Clasificación'),
        (sorted(datos.departamento.unique()), nombres.values(), COLORES),
    ):
        elegido = columna.selectbox(titulo, ['Todos', *opciones], key=f'calidad_{campo}')
        if elegido != 'Todos':
            datos = datos.loc[datos[campo].eq(elegido)]

    calculadas, publicables, restringidas = st.columns(3)
    cantidad = int(datos.estado.eq('no_publicable').sum())
    calculadas.metric('Estimaciones calculadas', len(datos))
    publicables.metric('Publicables con reserva', len(datos) - cantidad)
    restringidas.metric('No publicables', cantidad)
    if datos.empty:
        st.info('Ninguna estimación coincide con los filtros seleccionados.')
        return

    st.subheader('Estimaciones con CV superior al 30 %')
    altas = datos.loc[datos.cv.gt(UMBRAL_PUBLICACION)]
    if altas.empty:
        st.caption('Ninguna estimación de esta selección supera el umbral.')
    else:
        indicadores = ', '.join(altas.indicador.unique())
        st.caption(f'{indicadores} · La línea discontinua marca el umbral de publicación del 30 %.')
        st.altair_chart(grafica_cv(altas), use_container_width=True)

    st.subheader('Diagnóstico por estimación')
    st.caption('El exceso se expresa en puntos porcentuales por encima del 30 %. '
               'Por debajo del umbral, o en él, vale cero. Si falta el CV, el exceso es indeterminado.')
    campos = {'departamento': 'Departamento', 'indicador': 'Indicador', 'clasificacion': 'Clasificación',
              'cv': 'CV (%)', 'n': 'Muestra (n)', 'estado': 'Estado', 'exceso_pp': 'Exceso (pp)'}
    tabla = datos.sort_values(['departamento', 'indicador'])[list(campos)].copy()
    tabla['estado'] = tabla.estado.map(ETIQUETAS_ESTADO)
    st.dataframe(tabla.rename(columns=campos), hide_index=True, use_container_width=True,
                 column_config={campo: st.column_config.NumberColumn(format='%.5f')
                                for campo in ('CV (%)', 'Exceso (pp)')})
    with st.expander('Cómo interpretar la precisión'):
        leyenda()
        st.write(METODO)
