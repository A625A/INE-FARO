# M-05 — Interfaz Streamlit

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

El tablero usa archivos locales. Presenta PIB por habitante de Banguat (2023,
precios corrientes) para 22 departamentos, con ficha, comparación, gráficas y mapa.

Las fichas usan el CSV departamental de ENCOVI 2023 integrado en M-01. Las
estimaciones con al menos 30 observaciones y CV determinado son publicables
con reserva si M-01 permite su publicación y el CV no supera el 30 %.
Verde indica mayor precisión (CV ≤ 20 %) y amarillo precisión moderada
(20 % < CV ≤ 30 %). Gris indica una estimación no publicable. Cada color lleva
una etiqueta textual. La aplicación oculta el valor y ambos límites del IC
antes de construir fichas, tablas y gráficas. Si falta el CSV o su estructura
es inválida, se puede seguir consultando el PIB.

En **Calidad estadística**, los filtros de departamento, indicador y clasificación
se aplican a los conteos, al gráfico y al diagnóstico. El exceso se calcula en
puntos porcentuales como `max(CV − 30, 0)`; queda vacío si el CV es indeterminado.
El CSV integrado contiene 66 estimaciones, de las cuales 61 son publicables con
reserva. Los cinco casos restringidos corresponden a pobreza extrema. Los CV e
intervalos son aproximados por departamento y UPM, sin los estratos originales
ni la corrección de población finita.

La pestaña de radar espera `data/processed/hallazgos.csv` de M-04. La presentación
final se verificará con sus reglas, evidencia y limitaciones cuando se entregue.

El mapa usa la [capa simplificada GTM ADM1 de geoBoundaries](https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/GTM/ADM1/geoBoundaries-GTM-ADM1_simplified.geojson).
[Metadatos](https://www.geoboundaries.org/api/current/gbOpen/GTM/ADM1/):
límites de referencia de 2017, © [colaboradores de OpenStreetMap](https://www.openstreetmap.org/copyright),
licencia [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Se distribuye
la capa original, con sus 22 nombres comprobados frente al PIB. El mapa funciona
sin teselas ni servicios externos.
