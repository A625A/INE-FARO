# I-03 — Metodología y definiciones

Estado: documentación preparada a partir de las fuentes descargadas, 24/11/2026
(Guatemala). No acredita indicadores calculados ni sustituye la validación de I-02.
Los valores oficiales se usan como referencia de validación, no como resultado
producido por este prototipo.

## Alcance

El prototipo contrasta, para los 22 departamentos de Guatemala y el año 2023,
ocupación en el sector informal y pobreza según ENCOVI 2023 con producción
departamental según Banguat. DINESE queda como capa descriptiva opcional y
separada. No se busca demostrar causalidad.

Reglas de integración:

- Está prohibido enlazar registros individuales entre ENCOVI, Banguat y DINESE.
  Solo se comparan agregados por departamento, sector y año.
- `depto_id` es texto `01`–`22`. Nacional y Extrarregional no tienen código
  departamental; Extrarregional no entra al mapa.
- Un hallazgo es un contraste calculado y trazable entre indicadores compatibles,
  con evidencia y límites. No se redacta como relación causal.

## Fuentes consultadas

| Fuente | Archivo local | Uso en esta metodología |
|---|---|---|
| F2, Guía para el uso de bases de datos | `data/raw/encovi_2023/Guia-para-el-uso-de-bases-de-datos_v_final.pdf` | factores de expansión, precisión, diseño, contenido de bases |
| ENCOVI 2023, Empleo, población y vivienda | `data/raw/encovi_2023/encovi_2023_empleo_poblacion_vivienda.pdf` | definición de sector informal, universo ocupado, 70.3% nacional, glosario |
| ENCOVI 2023, Pobreza y desigualdad | `data/raw/encovi_2023/encovi_2023_pobreza_desigualdad.pdf` | líneas de pobreza, 56.0% y 16.2%, tablas departamentales, ODS 8.3.1 |
| Microdatos y diccionarios | `data/raw/encovi_2023/*.sav`, `dd_encovi_2023_*.xlsx` | códigos y etiquetas oficiales de variables |
| Decisiones acordadas | `CONTEXT.md`, `docs/ESTADO_PROYECTO.md` | elección del indicador principal y precauciones |

No se dispone localmente de F8 (Perfiles Departamentales INE) ni de un informe
de levantamiento con tasas de respuesta. La ruta de F2 en `docs/fuentes.csv` aún
apunta a `docs/guia_encovi_2023.pdf`; la ruta real es la indicada arriba.

## Definiciones

### Sector informal, empleo informal y economía informal

La definición oficial de **población ocupada en el sector informal** comprende a
la población ocupada que labora como empleadores, empleados y obreros de empresas
de menos de seis personas; por cuenta propia o autónoma, excluyendo profesionales
y técnicos; como familiares no remunerados; o en servicio doméstico. El sector
formal es su contraparte: ocupados que no están en el sector informal.

**Empleo informal** alude a la naturaleza y protección de la relación laboral y
puede aparecer dentro de distintas clases de unidades económicas. Su medición no
es intercambiable con la del sector informal. **Economía informal** es un concepto
más amplio, ligado a unidades y actividades no registradas; no equivale a la tasa
de ocupación en el sector informal.

El informe de ODS rotula un gráfico como "proporción de empleo informal en el
empleo total", pero el texto inmediatamente lo define como porcentaje de
población ocupada de 15 años o más **en el sector informal**. Se adopta esa
segunda definición y se documenta la discrepancia de etiqueta. En la base de
personas, `FORMAL_INFORMAL` usa `1=Informal` y `2=Formal`; la correspondencia
entre ese indicador y los criterios del párrafo anterior debe verificarse con
I-02 antes de publicar cualquier tasa.

### Pobreza

`POBREZA` es una clasificación categórica del hogar: `1=Pobre extremo`,
`2=Pobre no extremo`, `3=No pobre`. No es una variable binaria. La pobreza total
reúne las categorías 1 y 2; la extrema corresponde a la categoría 1. La línea de
pobreza extrema para 2023 es Q6,095.7 anuales y la de pobreza total Q14,382.7
anuales, estimada esta última a partir de líneas por área de residencia. El
indicador se refiere a consumo anual por persona, no a ingreso.

Hay registros sin clasificación de pobreza porque el hogar no reportó consumo.
Esos vacíos no se imputan ni se cuentan como no pobres.

### Producción y registro empresarial

PIB total es valor agregado más impuestos netos sobre productos; no es ingreso,
consumo ni riqueza de los hogares. El valor agregado sectorial es anterior a esos
impuestos. PIB por habitante es producción por persona de la población de
referencia, no ingreso recibido. El volumen encadenado con referencia 2013 no es
aditivo: `TOTAL` no se suma con sus componentes. Extrarregional pertenece a la
conciliación nacional, no a un departamento.

Empresa activa DINESE es una unidad registrada SAT/INE, con o sin movimiento de
ventas. Solo el subconjunto con movimiento se denomina económicamente activa en
las publicaciones del INE. DINESE no mide personas ocupadas, ni todas las
empresas existentes, ni formalización laboral; no habilita crecimiento, altas o
bajas netas en el radar sin nueva evidencia de comparabilidad.

## Universo, periodo y denominador

- **Ocupación en el sector informal:** personas de 15 años o más que durante la
  semana de referencia realizaron al menos una hora o un día de actividad
  económica, o que estaban ausentes temporalmente sin romper el vínculo laboral.
  El denominador es el total de ocupados de 15 años o más en esa misma semana.
  `PET` y `PEA` son variables auxiliares; no se usa PET como denominador de la
  tasa de informalidad. La definición nacional de PET empieza a los 10 años,
  mientras que la comparabilidad internacional y este indicador usan 15 años.
- **Pobreza:** unidad de análisis hogar con información de consumo, expandida a
  personas cuando se requiere incidencia poblacional. El periodo es el consumo
  anual por persona.
- **Otros ingresos:** la guía documenta ventanas de 3 y 12 meses; no se mezclan
  con ingreso laboral mensual ni con consumo anual.
- **Vínculos:** `NO_HOGAR` identifica al hogar y permite cruces entre bases de
  ENCOVI. Su cardinalidad y la existencia de identificadores de persona deben
  verificarse en I-02. Los cruces entre fuentes institucionales siguen prohibidos.

## Dominios geográficos y diseño muestral

La ENCOVI 2023 usa un diseño probabilístico, bietápico, estratificado y por
conglomerados. La guía señala como dominios de estudio los 22 departamentos e
identifica `DEPTO` y `UPM` como variables de diseño, junto con `FACTOR`. Los SAV
no contienen una variable de estrato explícita.

Conviene distinguir tres geografías que no son intercambiables:

| Variable | Categorías | Uso |
|---|---|---|
| `DEPTO` | 1–22, con nombres oficiales | dominio departamental y contraste con Banguat |
| `DOMINIO` | 1 Urbano Metropolitano, 2 Resto Urbano, 3 Rural Nacional | dominios de estudio del informe laboral |
| `AREA` | 1 Urbana, 2 Rural | desagregación de pobreza e indicador ODS |

El gráfico departamental de pobreza incluye la categoría "Diferendo Territorial,
Insular y Marítimo pendiente de resolver", que no es departamento y se excluye
de los 22 `depto_id`.

## Ponderación

| Base | Variable | Etiqueta observada | Uso previsto | Precaución |
|---|---|---|---|---|
| Todas | `FACTOR` | Factor de expansión | ponderación general; la guía ejemplifica `WEIGHT BY FACTOR` | no asumir que sirve para todo indicador |
| Personas | `Factor2` | Factor de expansión de hogares con agregado de consumo | posible puente hacia pobreza | no es `Factor3` ni un genérico por dominio |
| Hogares | `Factor3` | `Factor2 * personas (con consumo)` | posible agregación per cápita de hogares | no sustituye a `FACTOR` ni a `Factor2` |
| Agregado.Consumo | `Factor3` | `Factor2 * personas` | indicadores per cápita de consumo y pobreza | no aparece en la base Personas |

La guía resume que `FACTOR` pondera hogares y `Factor3` ajusta por número de
personas para cálculos per cápita, y describe `Factor3` como disponible solo en
Agregado.Consumo; su ejemplo en R calcula pobreza por área con `Factor3` y filtra
`POBREZA` en 1 o 2. Los metadatos de los SAV muestran además `Factor3` en Hogares,
con la etiqueta `Factor2 * personas (con consumo)`, y `Factor2` en Personas. Esa
diferencia entre guía y bases debe resolverse en I-02. La elección efectiva del
ponderador para la tasa de ocupación en el sector informal y para la incidencia
de pobreza queda pendiente de reproducir con microdatos en I-02/M-01.

## Precisión y publicación

La guía define `CV = se(theta) / theta * 100` e `IC 95% = theta +/- 1.96 * se(theta)`
y propone: CV ≤ 20% preciso, 21–30% poco preciso, > 30% impreciso. También advierte
sobre efecto de diseño, tamaño de UPM, correlación intraclase, muestras inferiores
a 100 unidades y recuentos no ponderados menores a 30, que clasifica como no
fiables.

Regla operativa del prototipo:

1. Todo indicador departamental debe informar `n` no ponderado, ponderador usado
   y, cuando sea calculable, CV e IC al 95%.
2. Si `n < 30` o `CV > 30%`, la etiqueta es `no_publicable` y el valor puede
   conservarse solo como insumo interno, nunca como hallazgo.
3. El cálculo de error estándar con diseño bietápico, estratificado y por
   conglomerados aún no está especificado en las fuentes descargadas; debe
   definirse antes de reportar CV departamentales.

## Indicadores objetivo

Los valores de referencia y sus definiciones operativas están en
`docs/indicadores_objetivo.csv`. No se han reproducido con los microdatos.

| Indicador | Valor oficial 2023 | Fuente |
|---|---:|---|
| Ocupación en el sector informal, nacional, 15 años o más | 70.3% | Informe de empleo, §4.1 |
| Sector formal, nacional | 29.7% | Informe de empleo, §4.1 |
| Ocupación en el sector informal, urbano / rural | 61.3% / 83.0% | Informe de pobreza, §4.24 |
| Pobreza total, nacional | 56.0% | Informe de pobreza, §2.3 |
| Pobreza extrema, nacional | 16.2% | Informe de pobreza, §2.7 |
| Coeficiente de Gini, nacional | 0.42 | Informe de pobreza, §3.1 |

Pobreza total por departamento, en porcentaje, según el informe §2.5:

| depto_id | Departamento | Valor | depto_id | Departamento | Valor |
|---|---|---:|---|---|---:|
| 01 | Guatemala | 21.6 | 12 | San Marcos | 53.7 |
| 02 | El Progreso | 46.4 | 13 | Huehuetenango | 81.3 |
| 03 | Sacatepéquez | 38.7 | 14 | Quiché | 86.4 |
| 04 | Chimaltenango | 47.8 | 15 | Baja Verapaz | 80.1 |
| 05 | Escuintla | 39.2 | 16 | Alta Verapaz | 90.3 |
| 06 | Santa Rosa | 74.0 | 17 | Petén | 50.6 |
| 07 | Sololá | 61.9 | 18 | Izabal | 50.5 |
| 08 | Totonicapán | 62.1 | 19 | Zacapa | 52.6 |
| 09 | Quetzaltenango | 44.1 | 20 | Chiquimula | 59.6 |
| 10 | Suchitepéquez | 53.7 | 21 | Jalapa | 79.9 |
| 11 | Retalhuleu | 50.9 | 22 | Jutiapa | 74.0 |

No hay tabla departamental publicada de ocupación en el sector informal en los
archivos descargados. El informe de empleo publica desgloses por sexo, dominio de
estudio, edad, pueblo y actividad económica, pero no por los 22 departamentos.
F8 podría cubrir esa comparación; no está descargado.

## Reglas de contraste

Los contrastes permitidos son agregados por departamento, sector y año. Ejemplos
de reglas a diseñar en M-04: alta ocupación en el sector informal frente a PIB por
habitante, sector productivo destacado frente a perfil laboral, y territorios con
características similares y diferencia económica. Cada hallazgo debe incluir id,
indicadores, departamento o grupo, valor y unidad, fuente y año, umbral o regla,
explicación y limitación.

Se excluyen del radar: crecimiento DINESE, altas y bajas netas, formalización
laboral inferida de DINESE, suma de `TOTAL` con componentes del PIB, mezcla de
corrientes con volumen encadenado y cualquier comparación individual entre
fuentes. Coincidir en departamento y año no convierte PIB en ingreso de los
hogares ni establece una relación causal.

## Pendiente antes de publicar tasas

1. Ejecutar y guardar `notebooks/01_exploracion_encovi.ipynb` con resultados.
2. Reconciliar `docs/diccionario_encovi.csv` con los SAV y diccionarios oficiales;
   las columnas derivadas `pobreza`, `informalidad`, `ingreso_hogar` y
   `consumo_total` no están acreditadas.
3. Confirmar códigos de `FORMAL_INFORMAL` y `POBREZA`, universo de ocupados,
   edad, denominador, cardinalidad de `NO_HOGAR` y ponderador por indicador.
4. Reproducir el 70.3% nacional o documentar la discrepancia.
5. Declarar dominio, diseño, `n`, CV e IC; obtener tasas de respuesta de una
   fuente metodológica no descargada todavía.
6. Contrastar agregados con F8 si se descarga y se revisa su procedencia.

El incumplimiento de cualquiera de estos puntos mantiene el estado
`referencia_oficial_no_reproducida` en `docs/indicadores_objetivo.csv`.
