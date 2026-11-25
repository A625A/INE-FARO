# M-05 — Interfaz Streamlit

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

El tablero usa archivos locales. Presenta PIB por habitante de Banguat (2023,
precios corrientes) para 22 departamentos, con ficha, comparación, gráficas y mapa.

Cuando M-01 entregue `data/processed/indicadores_encovi_2023.csv`, se mostrarán
informalidad y pobreza con fuente, año, unidad, CV e IC de precisión aproximada.
Las filas `no_publicable` muestran «N/D — precisión insuficiente» y conservan
su CV. El valor y el intervalo se ocultan, y las gráficas y comparaciones omiten
la estimación. Si falta el CSV o no cumple el contrato, se muestra el PIB con un aviso.

La pestaña de radar espera `data/processed/hallazgos.csv` de M-04. La presentación
final se verificará con sus reglas, evidencia y limitaciones cuando se entregue.

El mapa usa la [capa simplificada GTM ADM1 de geoBoundaries](https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/GTM/ADM1/geoBoundaries-GTM-ADM1_simplified.geojson).
[Metadatos](https://www.geoboundaries.org/api/current/gbOpen/GTM/ADM1/):
límites de referencia de 2017, © [colaboradores de OpenStreetMap](https://www.openstreetmap.org/copyright),
licencia [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). Se distribuye
la capa original, con sus 22 nombres comprobados frente al PIB. El mapa funciona
sin teselas ni servicios externos.
