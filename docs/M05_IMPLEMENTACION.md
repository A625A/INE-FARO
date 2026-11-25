# M-05 — Interfaz Streamlit

```bash
python -m pip install -r requirements.txt
python -m pip install 'streamlit>=1.40,<2'
streamlit run app.py
```

El tablero usa `data/processed/pib_per_capita.csv` de I-04. Si existe `data/processed/indicadores_encovi_2023.csv` de M-01, muestra informalidad, pobreza total y extrema, con año, cifras e información de precisión. Si aún no existe M-01, la aplicación sigue mostrando PIB y advierte que faltan indicadores, **sin inventarlos**. Si algún indicador no es publicable, bloquea la visualización de ese archivo hasta su revisión.

Hay selector departamental, comparación de departamentos, gráficos y sección de hallazgos que carga `data/processed/hallazgos.csv` cuando M-04 esté integrado. La cartografía oficial y la ficha de reglas de hallazgos siguen pendientes; no se presentan como implementadas. No usa Internet para funcionar.

**Estado:** se verificaron pruebas sintéticas de los contratos CSV; ejecución visual del servidor Streamlit pendiente en el entorno del equipo.