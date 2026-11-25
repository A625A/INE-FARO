"""Componentes de presentación y navegación de INE FARO."""
from html import escape
from pathlib import Path

import altair as alt
import streamlit as st

ROOT = Path(__file__).resolve().parent
AZUL = '#004080'
AZUL_CLARO = '#0080FF'
TINTA = '#10243B'
FUENTE = 'Ubuntu Sans'
SECCIONES = ('Empleo e ingresos', 'Territorio', 'Producción',
             'Radar de inteligencia', 'Metodología y calidad')


def cabecera():
    st.html(ROOT / 'static/faro.css')
    st.html('''
      <div class="faro-cabecera">
        <div><span class="faro-marca">INE FARO</span>
        <span class="faro-dataton">Prototipo del Datatón INE 2026</span></div>
        <img class="faro-ine" src="app/static/ine-horizontal-rgb.png" alt="Instituto Nacional de Estadística">
      </div>
    ''')


def titulo(seccion, pregunta, fuente):
    st.caption(fuente)
    st.title(seccion)
    st.markdown(f'<p class="faro-pregunta">{escape(pregunta)}</p>', unsafe_allow_html=True)


def navegar(seccion, **seleccion):
    st.session_state.update(seccion=seccion, **seleccion)


def conservar(campo, clave):
    st.session_state[campo] = st.session_state[clave]


def selector(label, opciones, campo, default=None, formato=str, contenedor=st):
    clave = f'filtro_{campo}'
    valor = st.session_state.get(campo, default)
    if valor not in opciones:
        valor = opciones[0]
    st.session_state[campo] = valor
    if st.session_state.get(clave) != valor:
        st.session_state[clave] = valor
    return contenedor.selectbox(label, opciones, format_func=formato, key=clave,
                                on_change=conservar, args=(campo, clave))


def cifras(items):
    st.html('<div class="faro-cifras">' + ''.join(
        '<div><p>' + escape(etiqueta) + '</p><strong>' + escape(valor) + '</strong>'
        + (f'<small>{escape(nota)}</small>' if nota else '') + '</div>'
        for etiqueta, valor, nota in items
    ) + '</div>')


def grafico(chart, **kwargs):
    return st.altair_chart(
        chart.configure(font=FUENTE).configure_view(stroke=None)
        .configure_axis(labelFontSize=12, titleFontSize=13, titleColor=TINTA,
                        labelColor=TINTA, gridColor='#DFE8F1', domainColor='#B8C8D9')
        .configure_legend(labelFontSize=12, titleFontSize=13, labelColor=TINTA),
        theme=None, width='stretch', **kwargs,
    )


def barras(datos, nombre, medida, unidad, tooltips, *, ordenar='-x', dominio=None):
    return alt.Chart(datos).mark_bar(color=AZUL, height=16).encode(
        y=alt.Y(f'{nombre}:N', title=None, sort=ordenar, axis=alt.Axis(labelLimit=146)),
        x=alt.X(f'{medida}:Q', title=unidad, scale=alt.Scale(zero=True, domain=dominio or alt.Undefined)),
        tooltip=tooltips,
    ).properties(height=max(100, 28 * len(datos)))


def descargar_csv(datos, label, nombre):
    st.download_button(label, datos.to_csv(index=False, lineterminator='\n').encode('utf-8'),
                       nombre, 'text/csv', on_click='ignore')


def mostrar_tabla(datos, **kwargs):
    st.dataframe(datos, hide_index=True, width='stretch', **kwargs)
