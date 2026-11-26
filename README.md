<h1 align="center">INE FARO</h1>
<p align="center"><strong>Inteligencia estadística y territorial para Guatemala</strong><br>Datatón INE 2026 · Prototipo v1.1</p>
<p align="center"><a href="https://ine-faro.streamlit.app/"><strong>Abrir demo principal</strong></a> · <a href="https://ine-faro.onrender.com/">Demo de respaldo</a> · <a href="presentacion.pdf">Presentación</a> · <a href="docs/entrega/README.md">Expediente técnico</a></p>

> ¿Qué no sabemos todavía sobre Guatemala? Los datos ya están ahí. Solo falta hacerles las preguntas correctas.

<p align="center"><a href="https://ine-faro.streamlit.app/"><img src="docs/evidencia/M-05/final/01-empleo.png" alt="INE FARO: vista de empleo e ingresos, indicadores nacionales y navegación del tablero" width="100%"></a></p>

> [!NOTE]
> **Para el jurado:** comenzar por la [demo principal en Streamlit](https://ine-faro.streamlit.app/). Si no responde, intentar el [respaldo en Render](https://ine-faro.onrender.com/) o descargar el [ZIP autónomo del corte validado](https://raw.githubusercontent.com/A625A/INE-FARO/63af665b30b567c662b8098946595e2df4ab0c9e/docs/evidencia/entrega/INE-FARO-Dataton.zip). Los servicios alojados pueden requerir tiempo de arranque. El ZIP funciona sin internet después de instalar dependencias. El [guion](docs/guion_demo.md), la [presentación](presentacion.pdf) y la [guía local](docs/entrega/reproduccion.md) permiten seguir el caso incluso sin acceso a los servicios web.

## Contenido

[El problema](#el-problema) · [Caso de uso](#caso-de-uso) · [Funcionalidades](#funcionalidades) · [Arquitectura](#arquitectura) · [Validación](#validación) · [Ejecutar localmente](#ejecutar-la-demostración) · [Reproducir datos](#reproducir-el-corte-completo) · [Limitaciones](#cautelas-científicas) · [Entrega](#entrega-y-documentación)

## El problema

Guatemala cuenta con fuentes oficiales que describen la ocupación, las condiciones de vida y la producción. Sin embargo, comparar sus resultados requiere respetar períodos, universos, ponderadores, denominadores y precisión estadística. Una tasa aislada no necesariamente permite entender los contrastes entre territorios.

INE FARO reúne estos indicadores y propone preguntas de investigación mediante un radar de reglas transparentes. El tablero es la interfaz; el radar es el mecanismo de descubrimiento. Su propósito es complementar el trabajo de los analistas del INE, no reemplazar su juicio ni producir nuevas estadísticas oficiales.

## Caso de uso

**¿Por qué dos departamentos con tasas cercanas de ocupación en el sector informal presentan brechas tan diferentes de pobreza?**

| ENCOVI 2023 | Chimaltenango | Alta Verapaz | Brecha absoluta |
|---|---:|---:|---:|
| Ocupación en el sector informal, población ocupada de 15 años o más | 80.08 % | 81.06 % | 0.98 pp |
| Pobreza total de personas | 47.75 % | 90.30 % | 42.55 pp |

Las cuatro estimaciones se publican con reserva e intervalos aproximados. pp = puntos porcentuales.

1. En **Empleo e ingresos**, seleccionar **Ver contraste Chimaltenango–Alta Verapaz**.
2. Examinar la ficha R1:2023:04-16, sus magnitudes, evidencia, precisión y sensibilidad.
3. Seleccionar **Abrir comparación en Territorio** para inspeccionar ambos departamentos.
4. Formular una nueva investigación: ¿cuánto de la brecha de pobreza persiste al comparar por separado áreas urbanas y rurales con suficiente soporte muestral?

<p align="center"><img src="docs/evidencia/M-05/final/08-contraste-r1.png" alt="Ficha del contraste Chimaltenango y Alta Verapaz, con comparación de indicadores" width="100%"></p>

El contraste aparece en los siete escenarios R1 evaluados. Esta persistencia se refiere únicamente a los umbrales explorados; no demuestra causalidad ni equivalencia estadística. [Caso completo](docs/caso_demostracion.md) · [Reglas del radar](docs/reglas_radar.md).

## Funcionalidades

| Vista | Qué permite hacer |
|---|---|
| **Empleo e ingresos** | Explorar ENEIC IV-2025: ocupación, sector informal, ingreso laboral medio y dominios geográficos. La composición por rama describe a todos los ocupados. |
| **Territorio** | Explorar 22 departamentos, cambiar indicadores en el mapa, comparar territorios y consultar perfiles de hogares, remesas, negocios y consumo. |
| **Producción** | Consultar VAB informal nacional, evolución temporal, composición y participaciones por actividad económica. |
| **Radar de inteligencia** | Filtrar 44 hallazgos por regla o departamento, inspeccionar evidencia y sensibilidad, consultar preguntas de investigación y descargar resultados. |
| **Metodología y calidad** | Revisar fuentes, denominadores, precisión, intervalos disponibles y restricciones de publicación. |

<details open>
<summary><strong>Territorio · mapa y comparación departamental</strong></summary>
<p align="center"><img src="docs/evidencia/M-05/final/02-territorio.png" alt="Mapa interactivo y vista territorial de INE FARO" width="100%"></p>
</details>
<details>
<summary><strong>Producción · evolución y estructura económica</strong></summary>
<p align="center"><img src="docs/evidencia/M-05/final/03-produccion.png" alt="Vista de producción y VAB informal" width="100%"></p>
</details>
<details>
<summary><strong>Radar · hallazgos y preguntas</strong></summary>
<p align="center"><img src="docs/evidencia/M-05/final/04-radar.png" alt="Radar de inteligencia con hallazgos y filtros" width="100%"></p>
<p align="center"><img src="docs/evidencia/M-05/final/10-que-investigar.png" alt="Ficha de investigación del radar" width="100%"></p>
</details>
<details>
<summary><strong>Metodología y calidad · precisión y restricciones</strong></summary>
<p align="center"><img src="docs/evidencia/M-05/final/05-metodologia.png" alt="Vista de metodología y calidad" width="100%"></p>
<p align="center"><img src="docs/evidencia/M-05/final/07-calidad.png" alt="Diagnóstico de calidad estadística" width="100%"></p>
</details>
<details>
<summary><strong>Vista móvil</strong></summary>
<p align="center"><img src="docs/evidencia/M-05/final/06-movil.png" alt="INE FARO en un navegador móvil emulado" width="300"></p>
</details>

Capturas del recorrido de validación del corte v1.1; no son interfaces simuladas. [Evidencia visual](docs/evidencia/M-05/final/) · [Implementación](docs/M05_IMPLEMENTACION.md).

## Arquitectura

El procesamiento se ejecuta por fuente y la aplicación consume los agregados versionados. El radar usa reglas deterministas, no un LLM ni un modelo predictivo.

```mermaid
flowchart LR
    E["INE · ENCOVI 2023"] --> C["Indicadores y precisión"]
    E --> H["Perfiles de hogares"]
    B["Banguat · PIB departamental 2023"] --> M["Matriz 22 × 67"]
    C --> M
    M --> R["Radar R1–R4"]
    C --> R
    L["INE · ENEIC IV-2025"] --> A["Agregados laborales"]
    V["Banguat · VAB informal nacional"] --> P["Agregados de producción"]
    D["INE · DINESE 2023–2024"] --> Q["Auditoría descriptiva"]
    M --> S["Streamlit · cinco vistas"]
    H --> S
    R --> S
    A --> S
    P --> S
    S --> Z["Demo local y ZIP"]
```

| Fuente | Uso en el proyecto |
|---|---|
| ENCOVI 2023 | Ocupación en el sector informal, pobreza, precisión y perfiles de hogares. |
| ENEIC IV-2025 | Indicadores laborales nacionales y por dominio; 21 celdas públicas. |
| Banguat | PIB departamental 2023 y VAB informal nacional 2013–2019, 2021–2024. |
| DINESE 2023–2024 | Auditoría descriptiva de registros empresariales, fuera de las reglas de crecimiento del radar. |

**Stack:** Python, Pandas, NumPy, Streamlit, Altair, CSV, JSON, GeoJSON, Pytest y Playwright. No requiere credenciales ni servicios externos para la demo local. [Arquitectura y contratos](docs/entrega/arquitectura.md) · [Inventario de fuentes](docs/fuentes.csv) · [Contratos de datos](docs/CONTRATOS_DE_DATOS.md).

## Validación

La evidencia corresponde al [corte técnico validado 63af665](https://github.com/A625A/INE-FARO/commit/63af665b30b567c662b8098946595e2df4ab0c9e), no a una medición en producción ni a una calificación oficial del jurado.

| Control | Resultado registrado |
|---|---|
| Matriz territorial | 22 departamentos × 67 columnas |
| Radar | 44 fichas en cuatro familias de reglas; 21 escenarios de sensibilidad |
| Precisión ENCOVI departamental | 66 estimaciones; 61 publicables según el criterio del proyecto, cinco restringidas |
| Perfiles de hogares | 207 celdas; 14 restringidas |
| Pruebas de software | 231 aprobadas |
| Recorrido Chromium | Escritorio y móvil emulado; cero errores de consola y cero solicitudes externas durante el ensayo local |
| Paquete de entrega | 58 archivos regulares; dos empaquetados idénticos en el entorno de referencia |

Se suprimen los valores e intervalos de las estimaciones restringidas en las vistas y exportaciones públicas correspondientes. Las pruebas de software verifican comportamiento, contratos y conciliaciones; no sustituyen la validación estadística. [Registro de validación](docs/evidencia/entrega/VALIDACION.md) · [Informe de navegador](docs/evidencia/entrega/chromium.txt) · [Evaluación del radar](docs/evaluation/radar_evaluation.md) · [Revisión de aceptación](docs/revision_final.md).

## Ejecutar la demostración

**Requisitos:** Git si se usa el repositorio; Python 3.12 o posterior según el README original (el corte se verificó con Python 3.14.3; se recomienda 3.14). Internet para descargar el paquete e instalar dependencias la primera vez. No se necesita descargar los microdatos originales para abrir el ZIP.

### Opción A · ZIP autónomo (recomendada para el jurado)

[Descargar INE-FARO-Dataton.zip](https://raw.githubusercontent.com/A625A/INE-FARO/63af665b30b567c662b8098946595e2df4ab0c9e/docs/evidencia/entrega/INE-FARO-Dataton.zip). Extraerlo en una carpeta nueva y abrir la terminal donde se encuentra `app.py`.

### Opción B · Clonar el repositorio

```sh
git clone https://github.com/A625A/INE-FARO.git
cd INE-FARO
```

Si se necesita una referencia técnica inmutable, usar `git checkout --detach 63af665b30b567c662b8098946595e2df4ab0c9e` en una copia de trabajo.

### macOS / Linux

Desde la carpeta de la opción A o B, con Python 3.14 instalado:

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py
```

### Windows (PowerShell)

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abrir [http://localhost:8501](http://localhost:8501). La aplicación inicia en **Empleo e ingresos**. Para detenerla, presionar Ctrl+C. La secuencia Windows está documentada; su ejecución en Windows nativo queda pendiente.

Si el puerto está ocupado, añadir `--server.port 8516` y abrir el nuevo puerto. Si la aplicación falla, comprobar que la terminal esté en la carpeta de `app.py` y que `pip check` termine sin errores. Consultar la [guía de reproducción y solución de problemas](docs/entrega/reproduccion.md).

## Reproducir el corte completo

La demostración consume agregados. Para recalcularlos y repetir la suite completa, trabajar en un checkout del repositorio con el entorno anterior y los insumos del corte.

- Los SAV de ENCOVI, XLSX departamentales y DINESE versionados se complementan con los seis archivos originales de ENEIC y VAB nacional indicados en la [guía de reproducción](docs/entrega/reproduccion.md#2-reconstruir-y-comprobar-los-datos).
- Para ENEIC, `python scripts/procesar_eneic.py --download` recupera los insumos autorizados y valida sus huellas. Para VAB, obtener los tres XLSX nacionales siguiendo el [contrato VAB](docs/VAB_CONTRATO_M05.md).
- Verificar nombres, rutas y SHA-256 antes de recalcular. Una descarga revisada requiere una actualización independiente del manifiesto.

Con todos los insumos disponibles, ejecutar desde la raíz (macOS/Linux):

```sh
(
  set -e
  python scripts/calcular_indicadores_encovi.py
  python scripts/procesar_hogares.py
  python scripts/procesar_pib.py
  python scripts/auditar_dinese.py
  python scripts/procesar_eneic.py
  python scripts/procesar_vab_informal.py
  python scripts/verificar_vab_2023.py
  python scripts/build_matriz.py
  python scripts/radar.py --mode standard --output-dir data/processed
  python scripts/evaluar_radar.py
  python docs/evaluation/m05_final/validar_consumo.py
  python -m pytest -p no:cacheprovider -q
)
```

El recálculo solo es válido si todos los comandos terminan correctamente. Para verificar el ZIP y PDF versionados, desde la raíz:

```sh
shasum -a 256 -c docs/evidencia/entrega/SHA256SUMS
unzip -tq docs/evidencia/entrega/INE-FARO-Dataton.zip
```

En PowerShell, usar `Get-FileHash -Algorithm SHA256` para cada archivo y comparar con [SHA256SUMS](docs/evidencia/entrega/SHA256SUMS).

Para reconstruir el ZIP, utilizar el checkout del corte de referencia y un destino nuevo:

```sh
python -m scripts.empacar_m05 --output ../faro-recalculado.zip
cmp docs/evidencia/entrega/INE-FARO-Dataton.zip ../faro-recalculado.zip
```

La igualdad binaria fue comprobada en el entorno de referencia (Python 3.14.3, zlib 1.2.12). Si cambia la versión de compresión, comparar el contenido extraído. La [guía completa](docs/entrega/reproduccion.md) incluye la prueba de navegador, los requisitos del publicador del radar y la recuperación de insumos.

### Reproducir I-04 e I-05

```sh
python scripts/procesar_pib.py
python scripts/auditar_dinese.py
```

Sin `--download` funcionan con los XLSX originales en `data/raw/banguat/` y `data/raw/dinese/`. Si faltan, añadir `--download`; se utilizan las URL y huellas fijadas en [el manifiesto](data/reference/fuentes_I04_I05.json). Los comandos admiten `--input-dir`, `--output-dir` y `--evidence-dir`; el SHA-256 también se exige sin descarga. PIB admite `--year` entre 2013 y 2024 (por defecto 2023); para otros años usar un directorio de salida distinto. [Metadatos PIB](docs/metadata_pib.md) · [Dictamen DINESE](docs/viabilidad_dinese.md) · [Especificación](docs/specs/I-04-I-05.md).

## Cautelas científicas

- El indicador territorial corresponde a ocupación en el **sector informal**, no a toda forma de empleo informal. ENCOVI 2023 y ENEIC IV-2025 tienen períodos y universos distintos.
- La pobreza de ENCOVI se mide a partir del consumo; PIB por habitante no equivale a ingreso de los hogares. VAB no equivale a PIB.
- Los volúmenes encadenados no son necesariamente aditivos. La serie nacional de VAB informal conserva la ausencia de 2020.
- Los intervalos ENCOVI son aproximados por las limitaciones del diseño muestral disponible. Los valores restringidos no deben interpretarse como cero.
- El radar formula preguntas descriptivas; su sensibilidad no implica causalidad, significancia estadística ni equivalencia entre territorios.
- DINESE describe registros de empresas; no permite concluir creación empresarial o formalización laboral. No se implementan tasas municipales ni el cruce de pobreza por condición laboral del hogar.

[Metodología](docs/metodologia.md) · [Diagnósticos y precisión](docs/M01_IMPLEMENTACION.md) · [Alcance y trabajo posterior](docs/entrega/README.md).

## Entrega y documentación

| Recurso | Enlace |
|---|---|
| Demo principal | [Streamlit](https://ine-faro.streamlit.app/) |
| Demo de respaldo | [Render](https://ine-faro.onrender.com/) |
| Paquete local | [ZIP validado](docs/evidencia/entrega/INE-FARO-Dataton.zip) |
| Presentación | [PDF de cinco diapositivas](presentacion.pdf) |
| Guion | [Guion de demostración y respuestas](docs/guion_demo.md) |
| Dossier | [Expediente técnico](docs/entrega/README.md) |
| Arquitectura | [Datos, reglas y contratos](docs/entrega/arquitectura.md) |
| Reproducción | [Instalación y pruebas](docs/entrega/reproduccion.md) |
| Auditoría de cierre | [Verificación de entrega](docs/entrega/auditoria_entrega.md) |
| Checklist | [Controles y recepción](docs/checklist_entrega.md) |
| Huellas | [SHA-256](docs/evidencia/entrega/SHA256SUMS) |

### Fuentes y condiciones de uso

[INE](https://www.ine.gob.gt/) · [Banco de Guatemala: cuadros departamentales](https://banguat.gob.gt/page/cuadros-estadisticos-por-departamento-2013-2024) · [DINESE](https://datos.ine.gob.gt/dataset/directorio-nacional-estadistico-de-empresas-dinese).

Se emplean tecnologías de código abierto. El código del prototipo está disponible públicamente; este repositorio no declara una licencia general en el corte revisado. Las licencias y condiciones de los datos y recursos pertenecen a cada fuente; DINESE declara Creative Commons Attribution. Consultar el [inventario](docs/fuentes.csv) y las atribuciones antes de redistribuir materiales. No se presume una licencia común.

### Contribución

Seguir [la guía de colaboración](CONTRIBUTING_AGENTS.md): cambios acotados en ramas dedicadas, commits descriptivos y revisión antes de integrar. No hacer push, PR, merges ni cambiar la rama predeterminada sin autorización. El estado de desarrollo y las evidencias se conservan en [docs](docs/).
