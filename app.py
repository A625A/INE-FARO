"""Entrada de Streamlit para el prototipo INE FARO."""
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard_data import cargar_eneic, cargar_hogares, cargar_matriz, cargar_vab
from dashboard_empleo import mostrar_empleo
from dashboard_radar import cargar_radar
from dashboard_ui import SECCIONES, cabecera

ROOT = Path(__file__).resolve().parent
PROCESADOS = ROOT / 'data/processed'
ERRORES_DE_DATOS = (OSError, ValueError, pd.errors.ParserError)


def cargar(lector, componente):
    try:
        return lector(PROCESADOS)
    except ERRORES_DE_DATOS as exc:
        st.error(f'{componente} · No se pudo validar el archivo público. {exc}')
        return None


def principal():
    st.set_page_config(page_title='INE FARO | Datatón INE 2026', layout='wide')
    cabecera()
    seccion = st.radio('Secciones de INE FARO', SECCIONES, horizontal=True,
                       label_visibility='collapsed', key='seccion')
    if seccion == SECCIONES[0]:
        datos = cargar(cargar_eneic, 'Empleo e ingresos')
        if datos is not None:
            mostrar_empleo(datos)
    elif seccion == SECCIONES[1]:
        from dashboard_territorio import mostrar_territorio
        datos = cargar(cargar_matriz, 'Territorio')
        if datos is not None:
            radar = cargar(cargar_radar, 'Hallazgos relacionados')
            mostrar_territorio(*datos, ROOT / 'data/reference/departamentos_m05.geojson', radar,
                               cargar(cargar_hogares, 'Perfiles de hogares'))
    elif seccion == SECCIONES[2]:
        from dashboard_produccion import mostrar_produccion
        datos = cargar(cargar_vab, 'Producción')
        if datos is not None:
            mostrar_produccion(*datos)
    elif seccion == SECCIONES[3]:
        from dashboard_radar_ui import mostrar_radar
        radar = cargar(cargar_radar, 'Radar de inteligencia')
        if radar is not None:
            mostrar_radar(radar)
    else:
        from dashboard_metodologia import mostrar_metodologia
        datos = cargar(cargar_matriz, 'Calidad ENCOVI')
        mostrar_metodologia(datos[1] if datos is not None else None)


principal()
