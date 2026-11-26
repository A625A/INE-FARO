# Atribuciones y condiciones de uso de terceros

INE FARO · Datatón INE 2026

Este documento identifica la procedencia y las condiciones de los recursos ajenos al código propio del equipo. No concede permisos de reutilización adicionales ni sustituye las condiciones del titular de cada recurso.

| Recurso | Fuente y condiciones |
|---|---|
| ENCOVI 2023 (microdatos, guía y documentación) | [INE](https://www.ine.gob.gt/encovi-2023). Condiciones de reutilización y redistribución de los originales por confirmar con INE. |
| ENEIC IV-2025 (microdatos y boletín) | [INE](https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/). Condiciones de reutilización de los originales por confirmar con INE. |
| DINESE 2023–2024 | [Catálogo INE](https://datos.ine.gob.gt/dataset/directorio-nacional-estadistico-de-empresas-dinese). El catálogo declara Creative Commons Attribution; consultar la versión y condiciones en la fuente. |
| PIB territorial y VAB informal nacional | [Banco de Guatemala](https://banguat.gob.gt/page/cuadros-estadisticos-detallados). Conservar la atribución y las condiciones del proveedor; la redistribución de los archivos originales no se presume autorizada. |
| Límites departamentales (ADM1, referencia 2017) | [geoBoundaries](https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/GTM/ADM1/geoBoundaries-GTM-ADM1_simplified.geojson). © [Colaboradores de OpenStreetMap](https://www.openstreetmap.org/copyright), [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). |
| Ubuntu Sans | Ubuntu Font Licence 1.0; [texto de licencia incluido](static/UbuntuSans-LICENSE.txt). |
| Identidad gráfica del Datatón/INE | Recursos institucionales utilizados para identificar el evento; no se otorga licencia sobre marcas o logotipos. |

## Software y herramientas de terceros

Las dependencias directas declaradas en [requirements.txt](requirements.txt) y las herramientas de desarrollo y prueba conservan sus licencias originales. La tabla identifica sus licencias principales; las distribuciones pueden contener componentes con avisos adicionales.

| Componente | Versión declarada o uso | Licencia principal y referencia |
|---|---|---|
| openpyxl | 3.1.5 | [MIT](https://pypi.org/project/openpyxl/3.1.5/) |
| pytest | 8.3.5 | [MIT](https://pypi.org/project/pytest/8.3.5/) |
| NumPy | 2.5.4 | [BSD-3-Clause](https://pypi.org/project/numpy/2.5.4/) |
| pandas | 3.1.1 | [BSD-3-Clause](https://pypi.org/project/pandas/3.1.1/) |
| pyreadstat | 1.3.8 | [Apache-2.0](https://pypi.org/project/pyreadstat/1.3.8/); incluye ReadStat, MIT, y otros componentes según sus avisos |
| jupyter | 1.1.1 | [BSD-3-Clause](https://pypi.org/project/jupyter/1.1.1/) |
| nbconvert | 7.17.2 | [BSD-3-Clause](https://pypi.org/project/nbconvert/7.17.2/) |
| pypdf | 7.1.1 | [BSD-3-Clause](https://pypi.org/project/pypdf/7.1.1/) |
| nbformat | 5.11.1 | [BSD-3-Clause](https://pypi.org/project/nbformat/5.11.1/) |
| nbclient | 0.11.0 | [BSD-3-Clause](https://pypi.org/project/nbclient/0.11.0/) |
| ipykernel | 7.4.0 | [BSD-3-Clause](https://pypi.org/project/ipykernel/7.4.0/) |
| Streamlit | 1.67.0 | [Apache-2.0](https://pypi.org/project/streamlit/1.67.0/) |
| Altair | 6.3.0 | [BSD-3-Clause](https://pypi.org/project/altair/6.3.0/) |
| Python | 3.14 | [PSF License y avisos incluidos](https://docs.python.org/3/license.html) |
| Playwright | Pruebas de navegador | [Apache-2.0](https://github.com/microsoft/playwright/blob/main/LICENSE) |
| Chromium | Navegador de pruebas | [Licencia BSD y avisos de terceros](https://chromium.googlesource.com/chromium/src/+/main/LICENSE) |

Las dependencias transitivas y los componentes incluidos en las distribuciones conservan sus propios avisos y condiciones. Este inventario no equivale a un SBOM exhaustivo ni sustituye los textos de licencia distribuidos por cada proveedor. Para las fuentes estadísticas y la procedencia visual, consultar [docs/fuentes.csv](docs/fuentes.csv) y [M-05](docs/M05_IMPLEMENTACION.md).

## Alcance de la licencia del proyecto

La [licencia MIT](LICENSE) se aplica únicamente al software original y su documentación de software elaborada por los titulares del proyecto INE FARO. No se aplica a los datos originales o derivados sujetos a derechos de terceros, documentos externos, marcas, logotipos, tipografías, cartografía ni otros materiales ajenos al equipo. La disponibilidad pública no constituye por sí sola una autorización de redistribución de esos recursos.

La licencia institucional no exclusiva, gratuita, perpetua e irrevocable concedida al Instituto Nacional de Estadística para fines institucionales conforme a los términos del Datatón se mantiene intacta. El reconocimiento de la autoría se conserva. El ZIP histórico del corte validado se mantiene sin cambios para preservar su integridad.
