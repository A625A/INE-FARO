# INE FARO

Observatorio de contrastes económicos territoriales de Guatemala basado en
estadísticas oficiales de hogares y producción.

## Lenguaje

**Ocupación en el sector informal**: clasificación oficial del INE de la población
ocupada según las características de su unidad económica y categoría ocupacional.
Es el indicador principal acordado para ENCOVI 2023.
_Evitar_: llamarlo automáticamente empleo informal o economía informal total.

**Empleo informal**: concepto referido a la naturaleza y protección del empleo,
que puede existir en distintas clases de unidades económicas. Su medición no se
considera intercambiable con ocupación en el sector informal.

**PIB total**: producción económica medida por valor agregado más impuestos netos
de subvenciones a los productos en un territorio y período.
_Evitar_: ingreso o consumo de los hogares.

**Valor agregado sectorial**: contribución de una actividad a la producción,
antes de incorporar los impuestos netos sobre los productos al PIB total.

**PIB por habitante**: cociente del PIB y la población de referencia. Es una medida
de producción por habitante, no el ingreso recibido por cada persona.

**Volumen encadenado**: medida de volumen con ponderaciones móviles y año de
referencia; sus componentes no son necesariamente aditivos.

**Extrarregional**: componente de unidades residentes generado fuera del territorio
económico, no atribuible a un departamento.

**Empresa activa DINESE**: unidad registrada incluida en el directorio SAT/INE,
con o sin movimiento de ventas. No equivale a toda empresa existente en Guatemala.

**Empresa con movimiento de ventas**: subconjunto de DINESE con movimiento
reportado; se denomina económicamente activa en las publicaciones del INE.

**Hallazgo**: contraste calculado y trazable entre indicadores compatibles, con
evidencia y límites de interpretación. No demuestra una relación causal.

## Continuidad del prototipo (handoff 24/11/2026)

Objetivo: 22 departamentos; ocupación en el sector informal y pobreza ENCOVI 2023;
producción Banguat; DINESE solo capa descriptiva opcional. Entrega: app local con
indicadores, matriz departamental, reglas de hallazgos, demo reproducible con 2–3
hallazgos trazables (año, fuente, unidad, límites). Sin causalidad.

Reglas operativas: prohibido join individual entre ENCOVI, Banguat y DINESE; solo
contrastes agregados por departamento, sector y año. Volumen encadenado 2013 no
aditivo (`TOTAL` no se suma con componentes). Extrarregional queda fuera del mapa.
DINESE solo transversal por año: excluidos crecimiento, altas/bajas netas y
formalización laboral. Cada hallazgo lleva id, indicadores, departamento/grupo,
valor y unidad, fuente y año, umbral/regla, explicación y limitación.

Completado y validado:
- I-04: `scripts/procesar_pib.py`, `scripts/comun.py`, `docs/metadata_pib.md`,
  `docs/evidencia/I-04.json`; `pib_departamental.csv` (836), `pib_per_capita.csv`
  (22), `pib_conciliacion.csv` (38); `tests/test_pib_cli.py` (9). Valida 22
  departamentos, claves únicas, 2013–2024, unidades, reconciliación con
  Extrarregional, separación corrientes/volumen y descarte de escrituras si falla.
- I-05: `scripts/auditar_dinese.py`, `docs/viabilidad_dinese.md`,
  `docs/evidencia/investigacion_dinese.md`, `docs/evidencia/I-05.json`;
  `dinese_resumen.csv` (1,750 = 876/2023 + 874/2024); `tests/test_dinese_cli.py`
  (10). Marcadores: `viabilidad_transversal_2023=true`,
  `habilitar_crecimiento_radar=false`, `codigo_longitudinal_validado=false`,
  `comparabilidad_temporal=no_acreditada`.
- Registro: 19 pruebas en verde, `compileall` y `git diff --check` sin errores.

Estado de validación científica (actualizado 25/11/2026):
- I-01: corregido; F2 apunta a
  `data/raw/encovi_2023/Guia-para-el-uso-de-bases-de-datos_v_final.pdf`.
- I-02: notebook ejecutado; diccionario reconciliado; `POBREZA` es categórica;
  `FORMAL_INFORMAL` = 1 informal, 2 formal; la edad en años es `PPA03`, no
  `Edad`; `FACTOR`, `Factor2` y `Factor3` no son intercambiables. Universo
  `PPA03 >= 15 & OCUPADOS == 1` con n=17,523, `NO_HOGAR` verificado y 70.305%
  reproducido con `FACTOR`. Precisión aproximada `DEPTO`/`UPM` declarada.
- I-03: `docs/metodologia.md` e `docs/indicadores_objetivo.csv` actualizados con
  los resultados I-02; commit `585f674` pusheado y actualización posterior sin
  commitear. I-06 opcional: Gini e ingresos derivados siguen sin acreditar.
- Pendiente menor: descargar F8 localmente, recuperar tasa de respuesta y guardar
  localmente la nota conceptual de la OIT. El 49.4% del perfil nacional corresponde
  al departamento `01 Guatemala`, no al total nacional.
- M-01 indicadores ENCOVI; M-02 agregados hogares/negocios; M-03 matriz; M-04
  radar/hallazgos; M-05 Streamlit; M-06 demo y pruebas; F-01..F-05 integración.

Datos: microdatos y diccionarios en `data/raw/encovi_2023/`; XLSX de Banguat y
DINESE en `data/raw/`; URLs/tamaños/SHA-256 en
`data/reference/fuentes_I04_I05.json`. Claves en `docs/CONTRATOS_DE_DATOS.md`:
`pib_departamental` = depto_id,anio,sector,tipo_precio; `pib_per_capita` =
depto_id,anio; `pib_conciliacion` = anio,sector,tipo_precio; `dinese_resumen` =
depto_id,anio,seccion_codigo,movimiento_ventas. `depto_id` texto `01`–`22`;
vacíos no son ceros. Matriz: filtrar 2023, `TOTAL`, corrientes; unir por
depto_id; per cápita como medida separada; no mezclar con volumen encadenado.

Reproducción: `python -m pip install -r requirements.txt`,
`python scripts/procesar_pib.py`, `python scripts/auditar_dinese.py`,
`python -m pytest -q`, `python -m compileall -q scripts tests`. Opciones comunes:
`--input-dir`, `--output-dir`, `--evidence-dir`, `--download`, `--manifest`;
PIB `--year` 2013–2024 (default 2023). Sin red si los XLSX ya están en `raw`.
`requirements.txt` incluye openpyxl, pytest, numpy, pandas, pyreadstat, Jupyter,
nbconvert y pypdf; streamlit se agregará con M-05.

Checklist de cierre: notebook I-02 ejecutado; diccionario reconciliado; 70.3%
reproducido; metodología e indicadores objetivo actualizados; dependencias
agregadas; indicadores con precisión aproximada declarada; pendiente matriz desde
PIB 2023 corrientes `TOTAL`, radar con reglas trazables, app con un comando, suite
y compileall limpios, ningún hallazgo causal y DINESE fuera del radar salvo
evidencia documentada.
