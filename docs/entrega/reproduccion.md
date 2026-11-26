# Guía de ejecución y verificación · INE FARO v1.1

Esta guía permite presentar el ZIP del jurado, verificar sus huellas y reconstruir la entrega desde el repositorio. El corte de referencia es `63af665b30b567c662b8098946595e2df4ab0c9e`. La ruta de demostración requiere el ZIP y un entorno Python. El recálculo requiere el checkout y los insumos originales. [Dossier](README.md) · [commit de entrega](https://github.com/A625A/INE-FARO/commit/63af665b30b567c662b8098946595e2df4ab0c9e)

## 1. Comprobar y presentar el ZIP

**Con el ZIP descargado.** Abrir una terminal en la carpeta de descarga y ejecutar `shasum -a 256 INE-FARO-Dataton.zip` en macOS o Linux. La huella esperada es `7788385aa8396c28f9d39788cdcb8fbc9db18195bf768d7e4f303f6b51136c31`. Extraer el ZIP en una carpeta nueva y abrir allí una terminal para preparar Python. En PowerShell se puede consultar la huella con `Get-FileHash -Algorithm SHA256 INE-FARO-Dataton.zip` y extraer desde el Explorador. La ruta Windows queda pendiente de ejecución en ese sistema. [Descargar ZIP del corte](https://raw.githubusercontent.com/A625A/INE-FARO/63af665b30b567c662b8098946595e2df4ab0c9e/docs/evidencia/entrega/INE-FARO-Dataton.zip) · [Registro de huellas](../evidencia/entrega/SHA256SUMS)

**Con el repositorio.** Ejecutar los siguientes comandos desde su raíz en macOS o Linux. Usar una carpeta de destino nueva.

```sh
shasum -a 256 -c docs/evidencia/entrega/SHA256SUMS
unzip -tq docs/evidencia/entrega/INE-FARO-Dataton.zip
unzip -q docs/evidencia/entrega/INE-FARO-Dataton.zip -d ../faro-demo
cd ../faro-demo
```

El primer control comprueba el ZIP y `presentacion.pdf`. Ambos deben indicar `OK`. El segundo comprueba la integridad de las entradas comprimidas.

Con Python 3.14 instalado, preparar el entorno desde la carpeta que contiene `app.py`. Se usó Python 3.14.3 en macOS con Apple Silicon. Instalar las dependencias antes del ensayo sin conexión.

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8516 --server.headless true
```

Abrir [la aplicación local](http://127.0.0.1:8516). Debe iniciar en **Empleo e ingresos**. Seguir el [guion](../guion_demo.md) y comprobar estos pasos en el equipo de presentación.

1. Abrir **Ver contraste Chimaltenango–Alta Verapaz** y confirmar la brecha de pobreza de **42.55 pp**.
2. Pulsar **Abrir comparación en Territorio** y verificar que ambos departamentos estén seleccionados.
3. En **Indicador del mapa**, elegir **Pobreza extrema**. Deben verse en gris Guatemala, Sacatepéquez, Escuintla, Quetzaltenango y Retalhuleu.
4. Abrir **Valores y calidad de los 22 departamentos** y pulsar **Descargar indicador del mapa**.
5. Abrir `mapa-pobreza_extrema-2023.csv`. Debe tener 22 filas de datos y cinco estados `no_publicable`, con `valor`, `ic95_inf` e `ic95_sup` vacíos.
6. Dejar abiertos `presentacion.pdf` y `docs/guion_demo.md`. Las cuatro capturas se encuentran en `docs/evidencia/M-05/final/` dentro del ZIP.

PowerShell en Windows, desde la raíz del ZIP extraído. Esta secuencia proviene del README y queda pendiente de ejecución en Windows nativo. [README del repositorio](../../README.md#ejecutar-la-demostración)

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

La secuencia PowerShell usa el puerto predeterminado. Abrir [Streamlit local](http://localhost:8501) y repetir el caso de dos clics.

## 2. Reconstruir y comprobar los datos

1. Abrir una copia de trabajo limpia del repositorio con el commit de entrega disponible.
2. Seleccionar el corte con `git checkout --detach 63af665b30b567c662b8098946595e2df4ab0c9e`.
3. Preparar y activar el entorno desde la raíz del checkout con los cuatro comandos de instalación de la sección anterior.
4. Colocar en `data/raw/` los archivos que exige cada productor. Conservar nombres y huellas del corte.

| Directorio bajo `data/raw/` | Archivos requeridos | Dónde obtenerlos |
| --- | --- | --- |
| `encovi_2023/` | SAV de Personas, Hogares, Agregado.Consumo y Negocios.1/.2. Para I-02, usar también los diccionarios XLSX y la guía local. | Versionados en el commit. [Inventario y huellas de I-02](../evidencia/I-02/validacion.json) |
| `banguat/` | Cuadros 5, 7 y 8 de PIB departamental. El cuadro 7 alimenta también el cotejo del VAB informal. | Versionados en el commit. [Nombres y huellas](../../data/reference/fuentes_I04_I05.json) |
| `dinese/` | XLSX 2023 y 2024. | Versionados en el commit. [Nombres y huellas](../../data/reference/fuentes_I04_I05.json) |
| `eneic_iv_2025/` | `Base-de-datos-Personas-ENEIC-IV-2025.xlsx`, `Diccionario-Personas-ENEIC-IV-2025.xlsx` y `Boletin-Estadistico-Edicion-No.3-ENEIC-2025-1.pdf`. | Aportar los tres desde una copia original o ejecutar `python scripts/procesar_eneic.py --download`. [Contrato de descarga](../ENEIC_CONTRATO_M05.md#reproducción) · [Manifiesto](../../data/reference/fuentes_eneic_iv_2025.json) |
| `banguat_nacional/` | `12_Valor_agregado_bruto_del_sector_informal.xlsx`, `5_Clasificacion_cruzada_de_industrias_y_sectores_institucionales.xlsx` y `Nomenclaturas_2013.xlsx`. | Aportar los tres desde una copia original o descargar los XLSX desde el contrato. [Enlaces y huellas](../VAB_CONTRATO_M05.md#fuentes-y-reproducción) |

El checkout trae 20 archivos de insumo. Para ejecutar todo el recálculo hay que añadir los seis archivos de ENEIC y VAB nacional. Si una huella difiere, recuperar el archivo del corte o revisar la nueva edición como actualización independiente. El recálculo de referencia se completó con entradas locales. [Inventario de fuentes](../fuentes.csv) · [README de insumos](../../README.md#reproducir-i-04-e-i-05)

Ejecutar el bloque desde la raíz en macOS o Linux. La subshell se detiene ante el primer comando que falle. Tomar el recálculo como válido solo si la secuencia termina con código 0, ya que el checkout conserva agregados versionados.

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

El cotejo de consumo debe confirmar la matriz de 22 × 67, las 21 celdas ENEIC y el radar de 44 fichas y 21 escenarios. La suite de 17 archivos Python incluye la prueba M-06 que recalcula las cuatro tasas y las dos brechas desde los SAV. El publicador del radar requiere permisos para crear enlaces simbólicos. El ZIP incorpora archivos regulares y puede ejecutarse de forma independiente. [Control de consumo](../evaluation/m05_final/validar_consumo.py) · [Prueba M-06](../../tests/test_indicadores.py) · [Reglas del radar](../reglas_radar.md)

Para auditar M-02 con `python scripts/auditar_hogares_m02.py`, ejecutar primero el productor y disponer de `9ad12c9:data/processed/perfiles_hogares.csv`. En un clon parcial, Git debe poder recuperar ese objeto. Las salidas de la auditoría quedan en `data/processed/auditoria_interna/`. Para repetir la exploración inicial, ejecutar `python scripts/ejecutar_exploracion_encovi.py` en una copia de trabajo. Esta tarea actualiza el cuaderno y su evidencia y queda fuera de la ruta para reconstruir el ZIP. [Auditoría de hogares](../hallazgos_hogares.md) · [Exploración I-02](../exploracion_encovi_resumen.md)

## 3. Reconstruir el archivo de entrega

Con el entorno activo y el checkout de referencia, ejecutar desde la raíz. Elegir un nombre nuevo para la salida. Con los agregados versionados se puede empaquetar directamente. Con los agregados recalculados se comprueba también la reproducción desde los insumos originales.

```sh
python -m scripts.empacar_m05 --output ../faro-recalculado.zip
cmp docs/evidencia/entrega/INE-FARO-Dataton.zip ../faro-recalculado.zip
```

`cmp` debe terminar sin salida y con código 0. La igualdad se comprobó con los insumos del corte, Python 3.14.3 y zlib 1.2.12. El empaquetador exige una generación estándar íntegra del radar y un destino nuevo. El PDF se incorpora como artefacto versionado. [Empaquetador](../../scripts/empacar_m05.py) · [Validación de entrega](../evidencia/entrega/VALIDACION.md)

Si se usa otro entorno de compresión y difiere el SHA-256, extraer ambos ZIP en carpetas nuevas y comparar su contenido. Usar la huella publicada para comprobar siempre la distribución oficial.

```sh
unzip -q docs/evidencia/entrega/INE-FARO-Dataton.zip -d ../comparar-original
unzip -q ../faro-recalculado.zip -d ../comparar-recalculado
diff -qr ../comparar-original ../comparar-recalculado
```

## 4. Repetir la prueba Chromium

Mantener levantada la app del ZIP extraído en el puerto 8516. En otra terminal, desde la raíz del checkout, preparar Playwright en una carpeta temporal con Node.js y npm. El recorrido de prueba conserva las nuevas capturas fuera del repositorio.

```sh
FARO_QA=$(mktemp -d)
npm install --prefix "$FARO_QA" playwright@1.64.1
export PLAYWRIGHT_BROWSERS_PATH="$FARO_QA/browsers"
npm exec --prefix "$FARO_QA" -- playwright install chromium
NODE_PATH="$FARO_QA/node_modules" BASE_URL=http://127.0.0.1:8516 \
  FARO_EVIDENCE="$FARO_QA/evidencia" node tests/browser/m05.cjs
```

Si ya hay un binario Chromium disponible, se puede indicar su ruta con `FARO_CHROME` y usarlo en lugar del que descarga Playwright. El script intercepta tráfico externo y requiere cero errores de consola y cero solicitudes externas. Prueba dos tamaños, escritorio y móvil emulado, y conserva las capturas y el registro `chromium.txt` en `FARO_EVIDENCE`. [Prueba de navegador](../../tests/browser/m05.cjs) · [Registro del corte de entrega](../evidencia/entrega/chromium.txt)

## Si falla un control

| Síntoma | Qué revisar |
| --- | --- |
| Falla el SHA-256 o la integridad del ZIP | Recuperar el archivo de la referencia fijada y repetir ambas comprobaciones antes de usarlo. |
| Streamlit falla al iniciar | Confirmar que se ejecuta en la carpeta que contiene `app.py` y que `python -m pip check` pasa en el entorno activo. Si el puerto está ocupado, elegir otro y actualizar `BASE_URL` al probar con Chromium. |
| Una vista muestra error de datos | Comparar sus CSV con el contrato y el corte. Si se alteraron los archivos de la demo, volver a extraer el ZIP verificado. |
| El empaquetador rechaza el radar | Revisar que JSON, CSV y manifiesto pertenezcan a la misma generación estándar. Regenerarlos juntos con la secuencia de la sección 2. |
| La demo falla en el ensayo | Abrir el PDF y seguir las cuatro capturas enlazadas en el guion. Registrar el problema en el ensayo del equipo final. [Guion](../guion_demo.md) · [checklist](../checklist_entrega.md) |

## Verificación de esta documentación

El 25 de noviembre de 2026 se verificaron la descarga pública del ZIP y las huellas del paquete y del PDF. Se instaló un entorno para la demo extraída y se pasó el recorrido de Chromium 156 en escritorio y móvil emulado con la red externa bloqueada, cero solicitudes externas y cero errores de consola. Se descargaron los seis insumos adicionales de ENEIC y VAB nacional desde las fuentes oficiales y coincidieron las huellas fijadas. El recálculo en una copia del corte reprodujo los agregados, las **231 pruebas** pasaron y los ZIP reconstruidos coincidieron byte por byte con el artefacto del jurado. El ensayo en el equipo final y la recepción siguen en el checklist. [Evidencia original de cierre](../evidencia/entrega/VALIDACION.md) · [Checklist](../checklist_entrega.md)
