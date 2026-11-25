# M-02 — Hogares, negocios y remesas en ENCOVI 2023

Genera `data/processed/perfiles_hogares.csv`: 207 filas, tres tablas descriptivas, nueve indicadores y 23 ámbitos (nacional + 22 departamentos). No guarda registros individuales ni mezcla ENCOVI con Banguat o DINESE.

```bash
python scripts/procesar_hogares.py
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

Comparación ponderada con `FACTOR`, precisión aproximada por `DEPTO`/`UPM`. CV nacional: 3.11549% y 3.02896%. Solo describe recepción y monto declarado en un horizonte de tres meses; no demuestra que las remesas expliquen el PIB, el consumo ni la pobreza.

## Tabla 2. Negocios del hogar

| Indicador | Nacional | n | Departamento más bajo | Departamento más alto |
|---|---:|---:|---|---|
| Hogares con negocio (%) | 20.760921 | 10,964 | Alta Verapaz 12.710317 | Sololá 31.420503 |
| Negocios por hogar | 0.238152 | 10,964 | Alta Verapaz 0.140350 | Sololá 0.365044 |
| Venta mensual por hogar con negocio (Q) | 9669.723279 | 2,142 | El Progreso 4574.297170 | Petén 16303.830786 |
| Ganancia neta mensual por hogar con negocio (Q) | 4384.247588 | 2,142 | Jalapa 2233.384135 | Huehuetenango 7832.201123 |

La ganancia conserva valores negativos: no se recorta. Catorce estimaciones departamentales de venta o ganancia quedan `no_publicable` por CV aproximado superior a 30%; el CSV conserva el valor con su estado. Estas cifras son unidades económicas declaradas por el hogar, no registros DINESE ni producción territorial.

## Tabla 3. Consumo per cápita

| Indicador | Nacional | n | Departamento más bajo | Departamento más alto |
|---|---:|---:|---|---|
| Agregado de consumo (Q/persona/mes) | 1440.048589 | 10,930 | Alta Verapaz 574.392762 | Guatemala 2604.809041 |
| Gasto (Q/persona/mes) | 126.799197 | 10,930 | Alta Verapaz 56.877065 | Guatemala 219.697559 |
| Ayudas y servicios (Q/persona/mes) | 21.110229 | 10,930 | Alta Verapaz 4.793326 | Guatemala 59.394301 |

Medidas en quetzales de octubre de 2023. `agreg3` es consumo, no ingreso; `ayuda3` no es remesa. No deben sumarse entre sí ni compararse directamente con el PIB departamental.

## Contrato de `perfiles_hogares.csv`

Clave: `tabla`, `ambito`, `depto_id`, `indicador`. Columnas: `tabla`, `ambito`, `depto_id`, `departamento`, `anio`, `indicador`, `valor`, `unidad`, `horizonte`, `ponderador`, `n`, `upm_n`, `cv`, `fuente`, `limite`, `precision`, `estado`.

`depto_id` es texto `01`–`22` solo cuando `ambito=departamental`; en `ambito=nacional` queda vacío, sin códigos `00` ni `Nacional`. `anio=2023`. Precisión: `aproximada_depto_upm_sin_estratos_originales`, no oficial. Estado: `publicable_con_reserva` cuando `n>=30` y `CV<=30%`, si no `no_publicable`. Vacíos no se sustituyen por ceros; la excepción documentada es el conteo de negocios cuando el filtro `P14A01=2`.

## Límites

- Son estimaciones descriptivas con diseño muestral aproximado; no reemplazan publicaciones oficiales ni permiten inferencia municipal.
- Los horizontes difieren: remesas a tres meses, negocios mensuales/actuales y consumo de octubre de 2023. No se convierten a una misma unidad temporal.
- No hay prueba de causalidad entre remesas, negocios, consumo, pobreza o PIB.
- I-06 permanece como trabajo opcional pendiente; este entregable solo usa variables directas verificadas en los SAV.
