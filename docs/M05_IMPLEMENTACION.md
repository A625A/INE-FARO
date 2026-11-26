# M-05 · Integración final de INE FARO

## Ejecución

Usar Python 3.12 o posterior. Desde la raíz, instalar `requirements.txt` y
ejecutar `python -m streamlit run app.py`. La navegación comienza en Empleo e
ingresos. La aplicación usa los agregados versionados para las cinco vistas. La
única comunicación de la demo es entre el navegador y Streamlit en el equipo.

| Vista | Insumos y recorrido |
| --- | --- |
| Empleo e ingresos | 21 celdas públicas ENEIC IV-2025. Incorpora tasa, volumen, media, cobertura, dominios y ramas oficiales. Las ramas describen todos los ocupados. |
| Territorio | Matriz M-03. Cambiar indicador, hacer clic en el mapa o elegir departamento y compararlo con otro. El contexto M-02 tiene nueve indicadores agrupados. |
| Producción | Tablas de VAB nacional y por actividad. Elegir año y valoración. Hay dos tramos históricos por la ausencia de 2020. Las participaciones se muestran en precios corrientes. |
| Radar de inteligencia | Generación estándar de M-04, con 44 hallazgos y 21 escenarios. Filtrar regla y departamento, abrir perfiles y descargar fichas o selección. |
| Metodología y calidad | Fuentes, períodos, universos, ponderadores, glosario y diagnóstico de 66 estimaciones ENCOVI. |

## Contratos y protección estadística

El lector ENEIC se limita al agregado del [contrato público](ENEIC_CONTRATO_M05.md).
El [contrato M-03](M03_CONTRATO_MATRIZ.md) y el [contrato M-02](hallazgos_hogares.md)
conservan los universos y los denominadores de cada insumo. El consumidor
enmascara valores antes de construir gráficos, tooltips, tablas o descargas.
ENCOVI tiene 61 estimaciones publicables con reserva y cinco restringidas de
pobreza extrema. La aproximación DEPTO/UPM carece de los estratos originales
y de la corrección por población finita. M-02 deja 14 estimaciones sin valor.
Los 73 hogares con discrepancias de negocios limitan los montos observados.

El [VAB informal](VAB_CONTRATO_M05.md) tiene alcance nacional. Los valores
productivos departamentales provienen de los cuadros 7 y 8 de Banguat.
El PIB por habitante mide producción por persona. La comparación con las tasas
sociales es descriptiva. Se difiere DINESE por su carácter contextual y para evitar
confundir registros con crecimiento empresarial o formalización.

El [radar](reglas_radar.md) lee selectivamente el JSON y valida cada evidencia de
acuerdo con su fuente. El CSV carece de un estado global. Si una ficha contiene
evidencia inválida o restringida, se excluye de la pantalla y de las descargas.
Los filtros limitan la vista. Las medianas, el P25 y la referencia nacional
siguen siendo las calculadas por el productor. Se presentan escenarios
precalculados. Cuando hay fichas excluidas se omite la sensibilidad del corte.

## ZIP de demostración para Windows

Desde el checkout, ejecutar:

```sh
python -m scripts.empacar_m05 --output faro-m05.zip
```

El comando resuelve `data/processed/.radar_m04/actual` una vez, verifica la
huella de la generación y la concordancia entre JSON, CSV y manifiesto,
y agrega sus bytes al ZIP como archivos regulares. Los agregados y recursos de
la aplicación se incluyen mediante una lista de archivos permitidos. El proceso
verifica los mismos bytes que agrega y rechaza valores indebidamente presentes
en filas restringidas. El ZIP excluye microdatos, XLSX, evidencia interna,
enlaces simbólicos y generaciones históricas. El ZIP reúne también el caso M-06,
la presentación, el guion, el checklist y las capturas de respaldo. El orden,
la fecha de entradas, los permisos y el nivel de compresión son fijos. Dos
ejecuciones en el mismo entorno con los mismos insumos generan los mismos bytes.
Un ZIP existente se conserva. Se admite el puntero de 64 caracteres de un
checkout de Git para Windows con enlaces desactivados.

Extraer en una carpeta, instalar las dependencias antes de desconectar la red y
ejecutar `python -m streamlit run app.py` desde esa carpeta. La instalación del
entorno es un paso independiente de la demostración. Los comandos de PowerShell para crear el entorno, instalar dependencias y arrancar el ZIP están en el [README](../README.md#ejecutar-la-demostración).

## Procedencia visual

El sistema de diseño y el inventario del kit están en
[.superdesign/design-system.md](../.superdesign/design-system.md).
El imagotipo adjunto se usa para identificar el Datatón y Ubuntu Sans se
distribuye con su [Ubuntu Font Licence 1.0](../static/UbuntuSans-LICENSE.txt).

El mapa usa la [capa simplificada GTM ADM1 de geoBoundaries](https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/GTM/ADM1/geoBoundaries-GTM-ADM1_simplified.geojson).
Límites de referencia de 2017, © [colaboradores de OpenStreetMap](https://www.openstreetmap.org/copyright),
licencia [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
