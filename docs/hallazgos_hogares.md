# M-02 — Hogares, negocios y remesas en ENCOVI 2023

Genera `data/processed/perfiles_hogares.csv`: 207 filas, tres tablas descriptivas, nueve indicadores y 23 ámbitos (nacional + 22 departamentos). No guarda registros individuales ni mezcla ENCOVI con Banguat o DINESE.

```bash
python scripts/procesar_hogares.py
python scripts/auditar_hogares_m02.py
python -m pytest tests/test_hogares_m02.py -q
```

## Variables y reglas acreditadas

| Tabla | Base ENCOVI | Variables | Unidad | Horizonte | Ponderador |
|---|---|---|---|---|---|
| `remesas_personas` | Personas | `P11C01`, `P11C02B`, `P11C03B`, `P11C04B` | persona | últimos 3 meses | `FACTOR` |
| `negocios_hogares` | Hogares, Negocios.1 y Negocios.2 | `P14A01`, `P14A02A`, `P14A13`, `P14A16` | hogar / negocio | actual y mensual | `FACTOR` |
| `consumo_per_capita` | Agregado.Consumo | `agreg3`, `gasto3`, `ayuda3` | persona | octubre 2023 | `Factor3` |

Variables comprobadas en los SAV y en los diccionarios oficiales. No se usan `ingreso_hogar`, `ingreso_per_capita`, `consumo_total` ni Gini: siguen sin acreditar en `docs/diccionario_encovi.csv:20-23`. ENIGH queda descartada y DINESE no interviene.

## Control de uniones

- `Hogares → Negocios.1` por `NO_HOGAR`: `one_to_one`, 10,964 hogares; sin nulos ni duplicados.
- `Hogares → Agregado.Consumo` por `NO_HOGAR`: `one_to_one`, 10,930 hogares; `DEPTO` concuerda en todos los casos.
- `Negocios.2`: 2,490 filas y 2,142 hogares. La clave es `NO_HOGAR` + `ID_NEGOCIO`; se agregó a un registro por hogar antes de cruzarla. No hay joins muchos-a-muchos.
- `P14A01` manda sobre `P14A02A`: 23 hogares con `P14A01=2` tenían un conteo distinto de cero; se trataron como sin negocio por el salto del cuestionario y no aparecen en Negocios.2.
- El universo de remesas es la respuesta válida no nula a `P11C01` (39,046 personas). No se imputó a quienes no respondieron.
- Los 2,477 receptores tienen los tres montos mensuales completos. El promedio mensual por receptor es la suma de esos tres montos dividida por tres; no se anualiza.

## Tabla 1. Remesas

| Indicador | Nacional | n | Departamento más bajo | Departamento más alto |
|---|---:|---:|---|---|
| Recibió remesas (%) | 5.820915 | 39,046 | Sacatepéquez 2.049961 | Petén 10.791668 |
| Monto mensual entre receptores (Q) | 1365.332855 | 2,477 | Escuintla 960.319684 | Sololá 2326.722230 |

Comparación ponderada con `FACTOR`, precisión aproximada por `DEPTO`/`UPM`. CV nacional: 3.11549% y 3.04571%. Solo describe recepción y monto declarado en un horizonte de tres meses; no demuestra que las remesas expliquen el PIB, el consumo ni la pobreza.

## Tabla 2. Negocios del hogar

| Indicador | Nacional | n | Departamento más bajo | Departamento más alto |
|---|---:|---:|---|---|
| Hogares con negocio (%) | 20.760921 | 10,964 | Alta Verapaz 12.710317 | Sololá 31.420503 |
| Negocios por hogar | 0.238152 | 10,964 | Alta Verapaz 0.140350 | Sololá 0.365044 |
| Venta mensual por hogar con negocio (Q) | 9669.723279 | 2,142 | El Progreso 4574.297170 | Guatemala 12863.413353 |
| Ganancia neta mensual por hogar con negocio (Q) | 4384.247588 | 2,142 | Jalapa 2233.384135 | Guatemala 6061.328685 |

La ganancia conserva valores negativos: no se recorta. Catorce estimaciones departamentales de venta o ganancia quedan `no_publicable` por CV aproximado superior a 30%; la salida pública deja vacíos valor y CV de esas filas. La evidencia completa se conserva en `data/processed/auditoria_interna/`. Los extremos de estas tablas usan únicamente estimaciones elegibles. Estas cifras son unidades económicas declaradas por el hogar, no registros DINESE ni producción territorial.

## Tabla 3. Consumo per cápita

| Indicador | Nacional | n | Departamento más bajo | Departamento más alto |
|---|---:|---:|---|---|
| Agregado de consumo (Q/persona/mes) | 1440.048589 | 10,930 | Alta Verapaz 574.392762 | Guatemala 2604.809041 |
| Gasto (Q/persona/mes) | 126.799197 | 10,930 | Alta Verapaz 56.877065 | Guatemala 219.697559 |
| Ayudas y servicios (Q/persona/mes) | 21.110229 | 10,930 | Alta Verapaz 4.793326 | Guatemala 59.394301 |

Medidas en quetzales de octubre de 2023. `agreg3` es consumo, no ingreso; `ayuda3` no es remesa. No deben sumarse entre sí ni compararse directamente con el PIB departamental.

## Contrato de `perfiles_hogares.csv`

Clave: `tabla`, `ambito`, `depto_id`, `indicador`. Columnas: `tabla`, `ambito`, `depto_id`, `departamento`, `anio`, `indicador`, `valor`, `unidad`, `horizonte`, `ponderador`, `n`, `upm_n`, `cv`, `fuente`, `limite`, `precision`, `estado`.

`depto_id` es texto `01`–`22` solo cuando `ambito=departamental`; en `ambito=nacional` queda vacío, sin códigos `00` ni `Nacional`. `anio=2023`. Precisión: `aproximada_depto_upm_sin_estratos_originales`, no oficial. Estado: `publicable_con_reserva` cuando `n>=30`, frecuencia del evento >=30 para proporciones y `CV<=30%`, si no `no_publicable`. Vacíos no se sustituyen por ceros; la excepción documentada es el conteo de negocios cuando el filtro `P14A01=2`.

## Límites

- Son estimaciones descriptivas con diseño muestral aproximado; no reemplazan publicaciones oficiales ni permiten inferencia municipal.
- Los horizontes difieren: remesas a tres meses, negocios mensuales/actuales y consumo de octubre de 2023. No se convierten a una misma unidad temporal.
- No hay prueba de causalidad entre remesas, negocios, consumo, pobreza o PIB.
- I-06 permanece como trabajo opcional pendiente; este entregable solo usa variables directas verificadas en los SAV.


## Correcciones de auditoría sobre 9ad12c9

Las tres medias condicionadas conservan ahora todas las UPM de la base de respuesta para remesas y de Hogares para negocios. Las observaciones fuera del dominio aportan cero al total linealizado. El denominador ponderado, `n` y `upm_n` describen el dominio. La estructura completa se utiliza para la varianza. Se conserva la aproximación DEPTO/UPM de M-01.

Se recalcularon 69 CV. Los valores puntuales permanecen iguales. Los CV nacionales de remesas, ventas y ganancias pasan respectivamente de 3.02896 a 3.04571%, de 10.23575 a 10.23650% y de 12.13660 a 12.14287%. Los estados conservan 193 estimaciones elegibles con reserva y 14 restringidas, sin transiciones. `auditoria_interna/comparacion_precision.csv` registra el antes y después de las 207 filas. La salida pública conserva columnas y claves, con valor y CV vacíos para las restringidas.

## Cobertura de negocios declarados y detallados

En los 2,142 hogares con negocio se declaran 2,440 negocios y se detallan 2,490. Hay 2,069 hogares con conteos coincidentes. En 11 hogares se declaran 28 negocios y se detallan 11, una diferencia de 17. En otros 62 hogares se declaran 64 y se detallan 131, un exceso de 67 detalles. La diferencia neta de 50 oculta ambas direcciones. Los conteos ponderados son 969,006 declarados y 993,834 detallados. La razón agregada de 102.56% representa conciliación de conteos y requiere cautela como medida de cobertura.

Los 2,142 hogares tienen al menos un detalle. Ventas y ganancias suman los registros disponibles y usan como denominador todos los hogares declarantes. El promedio de negocios por hogar usa el conteo declarado, por lo que su cobertura difiere de la de los montos. Las discrepancias afectan 73 hogares y una expansión de 32,967 hogares. En los 11 hogares con menos detalles, la diferencia ponderada es de 6,168 negocios. En los otros 62, el exceso ponderado es de 30,996 detalles. Los montos de los negocios ausentes y la explicación de los detalles excedentes quedan indeterminados. Se conserva el detalle observado sin imputación ni eliminación automática. `auditoria_interna/cobertura_negocios.csv` cuantifica por departamento y grupo los conteos y la contribución observada a ventas y ganancias. Estas contribuciones permiten localizar exposición a discrepancias, pero no medir el monto omitido.

## Recuentos y restricciones de la guía

La guía oficial local `data/raw/encovi_2023/Guia-para-el-uso-de-bases-de-datos_v_final.pdf`, página impresa 9 (página 14 del PDF), advierte sobre muestras inferiores a 100 unidades, recuentos no ponderados inferiores a 30, efecto de diseño y grados de libertad. Se conserva el umbral operativo de 30 y se añade advertencia explícita en `limite` cuando `n<100`. Esta decisión conserva la elegibilidad con reserva de los casos que superan 30 y cumplen CV, exponiendo la limitación adicional de la guía.

`n` es el tamaño no ponderado del denominador. En proporciones, la frecuencia del evento es distinta y queda registrada como `n_evento` en `auditoria_interna/casos_evento.csv`, junto con `n_muestra`. Se exige también un mínimo de 30 casos del evento. En las dos proporciones actuales todos los ámbitos superan ambos mínimos. En medias condicionadas, `n` cuenta receptores u hogares con negocio. Hay 33 estimaciones de medias con menos de 100 unidades, de las cuales cinco corresponden a remesas y 28 a ventas o ganancias. Los ceros en variables continuas son observaciones válidas y no se interpretan como ausencia de muestra. Los CV siguen siendo aproximados, sin grados de libertad ajustados ni estratos originales acreditados. Los extremos elegibles también deben leerse con estas reservas.

## Cruce de pobreza de la especificación v1.1

Pendiente de implementación y validación el cruce de pobreza por hogares formales, informales, mixtos y sin ocupados. El código M-02 revisado produce remesas, negocios y consumo. La implementación de M-01 calcula pobreza e informalidad por separado. Este cruce requiere definir la clasificación del hogar, unir por NO_HOGAR y validar denominadores y ponderadores antes de publicar resultados.

Los hogares con menos detalles aportan 0.6231% de las ventas y 1.0055% de las ganancias observadas ponderadas. Los hogares con más detalles aportan 3.5214% y 4.0377%, respectivamente. En conjunto, los hogares discrepantes representan 4.1445% de ventas y 5.0432% de ganancias observadas. Estos porcentajes cuantifican la exposición del agregado al problema de conciliación.

## Verificación de las correcciones

Se observaron fallos con el código original en las regresiones de contribuciones cero y separación de salidas. Tras corregir, las pruebas específicas pasan con 9 casos y la suite completa con 42 casos. Se reutilizó `/private/tmp/ine-faro-m05-venv/bin/python` para la suite, dado que el entorno del checkout original carecía de Streamlit. Los microdatos locales y las dependencias existentes permitieron completar la ejecución. Se verificaron además la supresión de las 14 filas restringidas, los 69 cambios de CV, la ausencia de cambios de estado y las 33 advertencias de muestra. `git diff --check` pasó.

La carpeta `data/processed/auditoria_interna/` se conserva localmente y queda excluida de Git porque contiene estimaciones restringidas. Para reproducir esta evidencia se ejecutan los dos scripts indicados al inicio con los microdatos locales. El commit de revisión incluye la salida pública y los cálculos reproducibles.
