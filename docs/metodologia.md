# I-03 — Metodología y definiciones

Estado: validación local de I-02 ejecutada 25/11/2026 (Guatemala). El notebook
`notebooks/01_exploracion_encovi.ipynb` quedó ejecutado con salidas reales y el
diccionario `docs/diccionario_encovi.csv` quedó reconciliado con los SAV y sus
etiquetas oficiales. Los valores calculados se presentan con ponderador, `n`,
precisión aproximada y límites; no sustituyen a una publicación oficial.

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

| Fuente | Archivo o enlace | Uso en esta metodología |
|---|---|---|
| F2, Guía para el uso de bases de datos | `data/raw/encovi_2023/Guia-para-el-uso-de-bases-de-datos_v_final.pdf` | factores de expansión, precisión, diseño, contenido de bases |
| ENCOVI 2023, Empleo, población y vivienda | `data/raw/encovi_2023/encovi_2023_empleo_poblacion_vivienda.pdf` | definición de sector informal, universo ocupado, 70.3% nacional, glosario |
| ENCOVI 2023, Pobreza y desigualdad | `data/raw/encovi_2023/encovi_2023_pobreza_desigualdad.pdf` | líneas de pobreza, 56.0% y 16.2%, tablas departamentales, ODS 8.3.1 |
| Microdatos y diccionarios | `data/raw/encovi_2023/*.sav`, `dd_encovi_2023_*.xlsx` | códigos, etiquetas y validación de indicadores |
| OIT, diferenciación conceptual | https://www.ilo.org/es/resource/45-trabajadores-de-la-economia-informal | distinción entre sector informal, empleo informal y economía informal |
| F8, Perfiles Departamentales INE | https://www.ine.gob.gt/perfiles | verificación externa de tasas departamentales de informalidad |
| Decisión de cobertura de campo INE | https://www.ine.gob.gt/2024/01/30/el-ine-concluyo-con-la-cobertura-de-campo-de-la-encovi-2023 | contexto de levantamiento; 14,682 hogares y 97.4% de cobertura de campo |

La ruta F2 en `docs/fuentes.csv` quedó corregida. Los PDF de F8 no se descargaron
localmente: se localizaron enlaces oficiales por departamento, por ejemplo
`https://www.ine.gob.gt/wp-content/uploads/2025/11/22.-JUTIAPA-PERFIL-ESTADISTICO.pdf`,
y los fragmentos indexados reproducen las tasas departamentales calculadas abajo.
El perfil nacional
(`https://www.ine.gob.gt/wp-content/uploads/2025/11/01.-GUATEMALA-PERFIL-ESTADISTICO.pdf`)
reporta 49.4%, valor que coincide con el departamento `01 Guatemala` calculado
(49.42%), no con el total nacional (70.305%). Por eso no se adopta como cifra
nacional. La página de cobertura de campo devolvió una pantalla CAPTCHA al
intentar descargarla; por eso se registra, pero no se usa como tasa de respuesta.

## Definiciones

### Sector informal, empleo informal y economía informal

La definición oficial de **población ocupada en el sector informal** comprende a
la población ocupada que labora como empleadores, empleados y obreros de empresas
de menos de seis personas; por cuenta propia o autónoma, excluyendo profesionales
y técnicos; como familiares no remunerados; o en servicio doméstico. El sector
formal es su contraparte: ocupados que no están en el sector informal.

La OIT distingue tres conceptos que no son intercambiables: el **sector informal**
se refiere a unidades económicas no registradas o no reconocidas formalmente; el
**empleo informal** se refiere al puesto de trabajo y a la ausencia de registro,
regulación o protección; y la **economía informal** abarca ambas perspectivas.
Se adopta esa distinción para evitar que el indicador principal se lea como
empleo informal o economía informal total.

El informe de ODS rotula un gráfico como "proporción de empleo informal en el
empleo total", pero el texto inmediatamente lo define como porcentaje de
población ocupada de 15 años o más **en el sector informal**. Se adopta esa
segunda definición y se documenta la discrepancia de etiqueta.

La validación I-02 confirmó que `FORMAL_INFORMAL` usa `1=Informal` y `2=Formal`,
que el universo de ocupados de 15 años o más tiene `n=17,523`, y que la tasa
ponderada con `FACTOR` es `70.305%`, redondeable a `70.3%`. `Factor2` produce
`70.2919%`, también redondeable a `70.3%`. Se usa `FACTOR` como ponderador
principal por ser el factor de expansión general en la base de personas.

### Pobreza

`POBREZA` es una clasificación categórica del hogar: `1=Pobre extremo`,
`2=Pobre no extremo`, `3=No pobre`, con `0` para registros sin clasificación en
las bases de personas y hogares. No es una variable binaria. La pobreza total
reúne las categorías 1 y 2; la extrema corresponde a la categoría 1. La línea de
pobreza extrema para 2023 es Q6,095.7 anuales y la de pobreza total Q14,382.7
anuales, estimada esta última a partir de líneas por área de residencia. El
indicador se refiere a consumo anual por persona, no a ingreso.

Hay registros sin clasificación de pobreza porque el hogar no reportó consumo.
Esos vacíos no se imputan ni se cuentan como no pobres. Con `Factor3` en
`Agregado.Consumo`, la incidencia calculada es `56.0413%` para pobreza total y
`16.2366%` para pobreza extrema.

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
- La edad en años es `PPA03` (rango observado 0–97, sin nulos). `Edad` es un
  grupo etario de 1 a 18 categorías y no debe usarse como edad continua. Con
  `PPA03 >= 15 & OCUPADOS == 1` se obtienen 17,523 registros; los 18,036
  ocupados totales incluyen 513 personas menores de 15 años. Los 17,523
  ocupados de 15 años o más también tienen `PEA == 1`.
- **Pobreza:** unidad de análisis hogar con información de consumo, expandida a
  personas cuando se requiere incidencia poblacional. El periodo es el consumo
  anual por persona. La base de consumo tiene 10,930 hogares; los 34 hogares con
  `POBREZA == 0` quedan fuera del denominador.
- **Otros ingresos:** la guía documenta ventanas de 3 y 12 meses; no se mezclan
  con ingreso laboral mensual ni con consumo anual. Las variables derivadas
  `ingreso_hogar` e `ingreso_per_capita` no están acreditadas en I-02.
- **Vínculos:** `NO_HOGAR` identifica al hogar y permite cruces entre bases de
  ENCOVI. Hay 10,964 hogares únicos en personas y hogares, y 10,930 en consumo;
  el conjunto de consumo es subconjunto de hogares, sin ids huérfanos, y la unión
  Hogares→Agregado.Consumo por `NO_HOGAR` es `one_to_one` sin nulos. El promedio
  observado es 4.197 personas por hogar, con máximo 27. Los cruces entre fuentes
  institucionales siguen prohibidos.

## Dominios geográficos y diseño muestral

La ENCOVI 2023 usa un diseño probabilístico, bietápico, estratificado y por
conglomerados. La guía señala como dominios de estudio los 22 departamentos e
identifica `DEPTO` y `UPM` como variables de diseño, junto con `FACTOR`. Los SAV
no contienen una variable de estrato explícita. Hay entre 48 y 124 UPM por
departamento.

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

| Base | Variable | Etiqueta observada | Uso confirmado | Suma observada |
|---|---|---|---|---:|
| Personas | `FACTOR` | Factor de Expansión | informalidad nacional, por área y departamental | 17,237,068.00 |
| Personas | `Factor2` | Factor de expansión de hogares con agregado de consumo | control alternativo de informalidad, no intercambiable | 17,237,068.79 |
| Hogares | `Factor3` | `Factor2 * personas (con consumo)` | puente per cápita, no usado como peso principal de informalidad | 17,237,067.97 |
| Agregado.Consumo | `Factor3` | `Factor2 * personas` | pobreza total y extrema | 17,237,068.00 |
| Hogares y Agregado.Consumo | `FACTOR` | Factor de expansión / factor de hogares con consumo | control de hogares, no peso de pobreza per cápita | 4,068,856.00 / 4,064,261.13 |

La guía ejemplifica `WEIGHT BY FACTOR` y calcula pobreza con `Factor3` en
`Agregado.Consumo`. Los metadatos de los SAV también muestran `Factor2` en
Personas y `Factor3` en Hogares. La elección efectiva quedó resuelta con la
reproducción de los valores oficiales: `FACTOR` para informalidad y `Factor3`
para pobreza.

## Precisión y publicación

La guía define `CV = se(theta) / theta * 100` e `IC 95% = theta +/- 1.96 * se(theta)`
y propone: CV ≤ 20% preciso, 21–30% poco preciso, > 30% impreciso. También advierte
sobre efecto de diseño, tamaño de UPM, correlación intraclase, muestras inferiores
a 100 unidades y recuentos no ponderados menores a 30, que clasifica como no
fiables.

Regla operativa del prototipo:

1. Todo indicador departamental informa `n` no ponderado, ponderador usado, CV e
   IC al 95%.
2. Si `n < 30` o `CV > 30%`, la etiqueta es `no_publicable`. Todos los
   departamentos calculados cumplen `n >= 357` y `CV <= 9.96%`, por lo que son
   `publicable` bajo esta regla.
3. El cálculo implementado es una aproximación con `DEPTO` como estrato y `UPM`
   como PSU, sin factor de corrección por población finita. La varianza de una
   razón se linealiza con `z_i = w_i * (y_i - r * x_i)` y se suma, por estrato,
   `n_h / (n_h - 1) * Σ(z_hj - z_h)^2`, dividiendo después por el denominador
   ponderado al cuadrado. `UPM` no existe en `Agregado.Consumo`; se incorporó desde
   Hogares por `NO_HOGAR`, con 0 nulos. Al no existir variable de estrato
   explícita, los CV/IC se etiquetan como `aproximado_depto_upm`, no como
   precisión oficial.

Precisión nacional calculada:

| Indicador | Valor | `n` | `se` (pp) | CV | IC 95% (pp) |
|---|---:|---:|---:|---:|---|
| Informalidad | 70.305% | 17,523 | 0.6835 | 0.97% | 68.965–71.645 |
| Pobreza total | 56.0413% | 10,930 | 0.8121 | 1.45% | 54.450–57.633 |
| Pobreza extrema | 16.2366% | 10,930 | 0.6849 | 4.22% | 14.894–17.579 |
| Informalidad urbana | 61.3329% | 9,764 | — | 1.51% | — |
| Informalidad rural | 83.0248% | 7,759 | — | 0.81% | — |

## Indicadores objetivo

Los valores de referencia y sus definiciones operativas están en
`docs/indicadores_objetivo.csv`. Los cinco valores nacionales y el desglose
departamental de pobreza se reprodujeron con los microdatos.

| Indicador | Valor oficial 2023 | Valor calculado | Código |
|---|---:|---:|---|
| Ocupación en el sector informal, nacional, 15 años o más | 70.3% | 70.305% | IND-INF-01 |
| Sector formal, nacional | 29.7% | 29.695% | IND-INF-02 |
| Ocupación en el sector informal, urbano / rural | 61.3% / 83.0% | 61.3329% / 83.0248% | IND-INF-03/04 |
| Pobreza total, nacional | 56.0% | 56.0413% | IND-POB-01 |
| Pobreza extrema, nacional | 16.2% | 16.2366% | IND-POB-02 |
| Coeficiente de Gini, nacional | 0.42 | no reproducido en I-02 | — |

Resultados departamentales. La columna `Informal` se calculó con `FACTOR`; la
columna `Pobreza calc.` con `Factor3`. La diferencia máxima frente a la tabla
oficial de pobreza es 0.05 puntos porcentuales.

| depto_id | Departamento | n inf | Informal | CV inf | n pob | Pobreza oficial | Pobreza calc. | CV pob |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 01 | Guatemala | 1,523 | 49.42 | 3.91 | 887 | 21.6 | 21.61 | 9.96 |
| 02 | El Progreso | 782 | 64.75 | 3.45 | 530 | 46.4 | 46.40 | 7.37 |
| 03 | Sacatepéquez | 1,200 | 62.73 | 3.09 | 656 | 38.7 | 38.75 | 7.80 |
| 04 | Chimaltenango | 896 | 80.08 | 3.02 | 514 | 47.8 | 47.75 | 7.14 |
| 05 | Escuintla | 1,137 | 60.04 | 3.60 | 679 | 39.2 | 39.18 | 7.74 |
| 06 | Santa Rosa | 613 | 71.63 | 3.48 | 423 | 74.0 | 73.98 | 3.78 |
| 07 | Sololá | 711 | 84.34 | 2.15 | 382 | 61.9 | 61.94 | 6.32 |
| 08 | Totonicapán | 645 | 85.87 | 2.53 | 357 | 62.1 | 62.12 | 6.54 |
| 09 | Quetzaltenango | 794 | 77.95 | 3.21 | 505 | 44.1 | 44.12 | 7.15 |
| 10 | Suchitepéquez | 816 | 66.63 | 3.58 | 540 | 53.7 | 53.66 | 5.72 |
| 11 | Retalhuleu | 614 | 68.76 | 2.72 | 403 | 50.9 | 50.87 | 6.15 |
| 12 | San Marcos | 619 | 81.59 | 3.12 | 416 | 53.7 | 53.75 | 5.49 |
| 13 | Huehuetenango | 626 | 84.54 | 3.35 | 409 | 81.3 | 81.27 | 3.37 |
| 14 | Quiché | 685 | 86.46 | 2.49 | 447 | 86.4 | 86.40 | 2.03 |
| 15 | Baja Verapaz | 730 | 77.96 | 3.69 | 440 | 80.1 | 80.14 | 4.20 |
| 16 | Alta Verapaz | 822 | 81.06 | 2.56 | 500 | 90.3 | 90.30 | 2.17 |
| 17 | Petén | 724 | 76.64 | 3.11 | 484 | 50.6 | 50.56 | 7.27 |
| 18 | Izabal | 814 | 64.00 | 5.24 | 494 | 50.5 | 50.54 | 8.98 |
| 19 | Zacapa | 770 | 68.55 | 3.38 | 483 | 52.6 | 52.56 | 8.61 |
| 20 | Chiquimula | 579 | 81.62 | 3.49 | 394 | 59.6 | 59.56 | 8.70 |
| 21 | Jalapa | 656 | 81.57 | 3.40 | 440 | 79.9 | 79.94 | 3.53 |
| 22 | Jutiapa | 767 | 78.63 | 2.61 | 547 | 74.0 | 73.97 | 3.36 |

Los fragmentos indexados de F8 coinciden con estas tasas departamentales de
informalidad, por ejemplo El Progreso 64.8%, Chimaltenango 80.1%, Santa Rosa
71.6%, Quiché 86.5%, Izabal 64.0%, Chiquimula 81.6% y Jutiapa 78.6%. La
comparación es indirecta porque los PDF no están descargados localmente.

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

## Estado de cierre y límites

1. I-01 quedó corregido en `docs/fuentes.csv`: F2 apunta al PDF real en `raw`.
2. I-02 quedó ejecutado y validado: notebook con salidas, diccionario
   reconciliado, códigos y universo confirmados, `NO_HOGAR` verificado,
   ponderadores asignados y 70.3% reproducido.
3. I-03 quedó documentado con precisión aproximada por `DEPTO`/`UPM` y todos los
   departamentos son `publicable` según la regla local.
4. Queda pendiente descargar los PDF de F8 al repositorio, obtener una tasa de
   respuesta documental y agregar la distinción OIT como archivo local si se
   requiere cita offline. Ninguno de esos pendientes cambia los valores calculados.
5. El coeficiente de Gini y los ingresos derivados siguen sin acreditar en I-02;
   DINESE sigue fuera del radar salvo evidencia documentada.
