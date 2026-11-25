"""M-05: interfaz local de INE FARO, sin datos simulados ni inferencias causales."""
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard_utils import cargar_tablero

ROOT = Path(__file__).resolve().parent
PROCESADOS = ROOT / 'data/processed'

st.set_page_config(page_title='INE FARO | Radar territorial', page_icon='📊', layout='wide')
st.title('INE FARO')
st.caption('Radiografía territorial de Guatemala · ENCOVI 2023 (INE) + PIB 2023 (Banguat)')


@st.cache_data(show_spinner=False)
def datos():
    return cargar_tablero(PROCESADOS)


try:
    tabla, tiene_encovi = datos()
except (ValueError, FileNotFoundError, pd.errors.ParserError) as exc:
    st.error(f'No se pudo cargar una tabla verificada: {exc}')
    st.stop()

if not tiene_encovi:
    st.warning('M-01 todavía no ha generado indicadores ENCOVI. Se muestra únicamente el PIB oficial; no se usan cifras simuladas.')

pestaña_territorio, pestaña_comparacion, pestaña_radar = st.tabs(
    ['Departamento', 'Comparar departamentos', 'Hallazgos del radar'])

with pestaña_territorio:
    nombres = tabla.departamento.tolist()
    seleccionado = st.selectbox('Departamento', nombres, index=0)
    fila = tabla.loc[tabla.departamento.eq(seleccionado)].iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('PIB por habitante · 2023', f"Q{fila.pib_per_capita:,.0f}")
    if tiene_encovi:
        col2.metric('Ocupación en sector informal', f"{fila.ocupacion_sector_informal:.1f}%")
        col3.metric('Pobreza total', f"{fila.pobreza_total:.1f}%")
        col4.metric('Pobreza extrema', f"{fila.pobreza_extrema:.1f}%")
    else:
        col2.info('Informalidad: pendiente de M-01')
        col3.info('Pobreza: pendiente de M-01')
    st.subheader('PIB por habitante entre departamentos')
    st.bar_chart(tabla.set_index('departamento')['pib_per_capita'].sort_values(),
                 x_label='Departamento', y_label='Quetzales por habitante')
    if tiene_encovi:
        detalle = pd.read_csv(PROCESADOS / 'indicadores_encovi_2023.csv', dtype={'depto_id': str})
        detalle = detalle.loc[detalle.depto_id.eq(fila.depto_id),
                   ['indicador', 'valor', 'n', 'cv', 'ic95_inf', 'ic95_sup', 'estado']]
        st.subheader('Precisión de las estimaciones ENCOVI')
        st.dataframe(detalle, use_container_width=True, hide_index=True)
        st.caption('CV e intervalos estimados con aproximación DEPTO/UPM; no son errores muestrales oficiales del INE.')
    st.caption('El PIB por habitante mide producción por persona, no ingreso familiar.')

with pestaña_comparacion:
    departamentos = st.multiselect('Seleccioná departamentos', tabla.departamento.tolist(),
                                   default=tabla.departamento.tolist()[:3])
    if not departamentos:
        st.info('Seleccioná al menos un departamento.')
    else:
        comparacion = tabla.loc[tabla.departamento.isin(departamentos)]
        campos = ['departamento', 'pib_per_capita']
        if tiene_encovi:
            campos += ['ocupacion_sector_informal', 'pobreza_total', 'pobreza_extrema']
        st.dataframe(comparacion[campos], hide_index=True, use_container_width=True)
        if tiene_encovi:
            st.subheader('Contraste descriptivo: PIB e informalidad')
            st.scatter_chart(comparacion, x='pib_per_capita', y='ocupacion_sector_informal',
                             x_label='PIB por habitante (Q, 2023)',
                             y_label='Ocupación en sector informal (%)')
            st.caption('La asociación visual no demuestra que una variable cause la otra.')

with pestaña_radar:
    hallazgos = PROCESADOS / 'hallazgos.csv'
    if not hallazgos.exists():
        st.info('M-04 aún no genera hallazgos. Este apartado mostrará solo resultados reales, con regla, evidencia y advertencia.')
    else:
        try:
            tabla_hallazgos = pd.read_csv(hallazgos)
            if tabla_hallazgos.empty:
                st.info('No hay hallazgos verificables para presentar.')
            else:
                st.dataframe(tabla_hallazgos, hide_index=True, use_container_width=True)
        except (ValueError, pd.errors.ParserError) as exc:
            st.error(f'No se pudo leer hallazgos.csv: {exc}')

st.divider()
st.caption('Fuentes: INE, ENCOVI 2023; Banco de Guatemala, PIB departamental 2023. El radar compara agregados, no cruza personas con empresas ni infiere causalidad.')