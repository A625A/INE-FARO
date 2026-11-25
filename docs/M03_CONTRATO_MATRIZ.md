# M-03 · Matriz departamental integrada de Guatemala, 2023

`data/processed/matriz_departamental.csv` es la entrada departamental de M-04 y de la integración posterior de M-05. Cada fila describe un departamento en 2023. La clave es `(depto_id, anio)`. El archivo contiene 22 filas y 67 columnas, en orden de código INE, con cabecera, codificación UTF-8, separador coma, punto decimal y fin de línea LF. Un campo vacío representa un dato ausente. Al cargarlo con pandas, usar `dtype={'depto_id': 'string'}` para conservar los ceros iniciales.

## Origen y granularidad

| Archivo bajo `data/` | Grano y filas del corte | Uso |
|---|---|---|
| `processed/indicadores_encovi_2023.csv` | Departamento × indicador, 66 | Tasas y diagnóstico de M-01, INE ENCOVI 2023. |
| `processed/indicadores_encovi_nacional_2023.csv` | Ámbito × área × indicador, 5 | Referencia de control. Se verifican las tres muestras nacionales frente a la suma de las departamentales y se reconoce la informalidad urbana y rural. |
| `processed/pib_departamental.csv` | Departamento × sector × tipo de precio, 836 | Los 418 registros corrientes aportan 17 VAB, IPNS y PIB total por departamento. |
| `processed/pib_per_capita.csv` | Departamento, 22 | PIB por habitante oficial a precios corrientes. |
| `reference/sectores_ciiu.csv` | Sección CIIU, 21 | Catálogo sin dimensión temporal. Relaciona A–U con 17 grupos Banguat. |

El constructor exige 2023 en cada registro fechado. Comprueba las claves antes de pivotar y coteja código y nombre con el catálogo departamental de `scripts/comun.py`. Cada bloque ancho aporta una sola observación por clave. Los agregados nacionales, por área y extrarregionales quedan fuera de las filas departamentales.

## Identificación

| Columna | Tipo y significado |
|---|---|
| `depto_id` | Texto de dos dígitos, de `01` a `22` según el INE. |
| `departamento` | Nombre canónico del departamento, con acentos. |
| `anio` | Año de referencia común, entero 2023. |

## Indicadores ENCOVI

La ocupación en el sector informal es el porcentaje de ocupados de 15 años o más que trabajan en ese sector. M-01 usa Personas, `PPA03 >= 15`, `OCUPADOS = 1`, `FORMAL_INFORMAL = 1` en el numerador y `FACTOR` para expandir el universo de ocupados. El indicador describe el sector de la unidad económica.

La pobreza mide incidencia poblacional según consumo anual por persona. El denominador comprende personas representadas por hogares con información de consumo y clasificación 1–3 en Agregado.Consumo. M-01 usa `Factor3` para expandir esos hogares a personas. Las categorías 1 y 2 forman el numerador de pobreza total y la categoría 1 el de pobreza extrema.

| Campo M-01 y unidad | Ocupación en el sector informal | Pobreza total | Pobreza extrema |
|---|---|---|---|
| `valor` · estimación, % | `ocupacion_sector_informal_valor_2023` | `pobreza_total_valor_2023` | `pobreza_extrema_valor_2023` |
| `ic95_inf` · límite inferior, % | `ocupacion_sector_informal_ic95_inf_2023` | `pobreza_total_ic95_inf_2023` | `pobreza_extrema_ic95_inf_2023` |
| `ic95_sup` · límite superior, % | `ocupacion_sector_informal_ic95_sup_2023` | `pobreza_total_ic95_sup_2023` | `pobreza_extrema_ic95_sup_2023` |
| `cv` · coeficiente de variación, % | `ocupacion_sector_informal_cv_2023` | `pobreza_total_cv_2023` | `pobreza_extrema_cv_2023` |
| `n` · observaciones sin ponderar | `ocupacion_sector_informal_n_2023` | `pobreza_total_n_2023` | `pobreza_extrema_n_2023` |
| `upm_n` · UPM observadas | `ocupacion_sector_informal_upm_n_2023` | `pobreza_total_upm_n_2023` | `pobreza_extrema_upm_n_2023` |
| `ponderador` · nombre del factor | `ocupacion_sector_informal_ponderador_2023` | `pobreza_total_ponderador_2023` | `pobreza_extrema_ponderador_2023` |
| `estado` · categoría de publicación | `ocupacion_sector_informal_estado_2023` | `pobreza_total_estado_2023` | `pobreza_extrema_estado_2023` |

`n` cuenta personas en ocupación y hogares con consumo en pobreza. `upm_n` cuenta unidades primarias de muestreo. El campo de ponderación conserva el nombre del factor aplicado por M-01. Las tasas y los límites se expresan en escala 0–100. El CV expresa el error estándar relativo en porcentaje de la estimación.

M-03 copia los resultados de M-01 a su precisión publicada. El estado `publicable_con_reserva` permite mostrar el valor y el IC95. Un `n < 30`, un CV superior al 30 % o un CV indefinido implica `no_publicable`. En ese caso el valor y ambos límites quedan vacíos. El estado, la muestra, las UPM, el ponderador y el CV disponible se conservan. En este corte hay cinco restricciones, todas de pobreza extrema, en Guatemala (01), Sacatepéquez (03), Escuintla (05), Quetzaltenango (09) y Retalhuleu (11). Son 15 celdas vacías. Un consumidor debe respetar el estado al mostrar, comparar o clasificar departamentos. El detalle diagnóstico original permanece en M-01.

La precisión común es `aproximada_depto_upm_sin_estratos_originales`. M-01 aproxima la varianza con DEPTO como estrato y UPM como conglomerado, sin estratos originales ni corrección por población finita. Los CV y los IC95 son aproximaciones. La referencia operativa para los tres indicadores y sus estados es el resultado validado de M-01. [Metodología](metodologia.md) · [Implementación y controles de M-01](M01_IMPLEMENTACION.md)

## Producción departamental

| Columna | Unidad y regla |
|---|---|
| `pib_total_millones_q_2023` | Millones de quetzales corrientes. Se copia el registro TOTAL, medida `pib_total`, cuadro Banguat 5. |
| `pib_por_habitante_q_2023` | Quetzales corrientes por habitante. Se copia el cuadro 8, cuyo denominador son las proyecciones de población INE 2010–2050. |
| `vab_total_millones_q_2023` | Millones de quetzales corrientes. Suma de los 17 grupos con medida `valor_agregado` del cuadro 7. Es el denominador de todas las participaciones. |
| `ipns_millones_q_2023` | Millones de quetzales corrientes. Impuestos netos de subvenciones sobre productos, registro IPNS del cuadro 7. |
| `actividad_predominante_2023` | Código del grupo con mayor VAB nominal. En empate exacto se elige el primero en el orden CIIU de la tabla siguiente. |
| `participacion_predominante_pct_2023` | Porcentaje del VAB total correspondiente al grupo predominante, con la misma precisión que su participación sectorial. |

Por departamento y grupo, la participación es `100 × VAB del grupo / VAB total`. El constructor exige un denominador positivo y usa los importes nominales sin redondeo previo. TOTAL e IPNS intervienen en la conciliación contable. Solo los 17 grupos de la tabla participan en la clasificación. Los registros `volumen_encadenado_2013` se descartan antes de cualquier operación sectorial.

| Grupo | Actividad (etiqueta breve) | VAB en millones de Q corrientes | Participación en el VAB total (%) |
|---|---|---|---|
| A | Agricultura, ganadería, silvicultura y pesca | `vab_a_millones_q_2023` | `participacion_a_pct_2023` |
| B | Minas y canteras | `vab_b_millones_q_2023` | `participacion_b_pct_2023` |
| C | Manufacturas | `vab_c_millones_q_2023` | `participacion_c_pct_2023` |
| D-E | Electricidad, gas, agua y saneamiento | `vab_d_e_millones_q_2023` | `participacion_d_e_pct_2023` |
| F | Construcción | `vab_f_millones_q_2023` | `participacion_f_pct_2023` |
| G | Comercio y reparación de vehículos | `vab_g_millones_q_2023` | `participacion_g_pct_2023` |
| H | Transporte y almacenamiento | `vab_h_millones_q_2023` | `participacion_h_pct_2023` |
| I | Alojamiento y servicios de comidas | `vab_i_millones_q_2023` | `participacion_i_pct_2023` |
| J | Información y comunicaciones | `vab_j_millones_q_2023` | `participacion_j_pct_2023` |
| K | Actividades financieras y de seguros | `vab_k_millones_q_2023` | `participacion_k_pct_2023` |
| L | Actividades inmobiliarias | `vab_l_millones_q_2023` | `participacion_l_pct_2023` |
| M | Actividades profesionales, científicas y técnicas | `vab_m_millones_q_2023` | `participacion_m_pct_2023` |
| N | Servicios administrativos y de apoyo | `vab_n_millones_q_2023` | `participacion_n_pct_2023` |
| O | Administración pública, defensa y seguridad social obligatoria | `vab_o_millones_q_2023` | `participacion_o_pct_2023` |
| P | Enseñanza | `vab_p_millones_q_2023` | `participacion_p_pct_2023` |
| Q | Salud humana y asistencia social | `vab_q_millones_q_2023` | `participacion_q_pct_2023` |
| R-S-T-U | Artes y recreación, otros servicios, hogares y organizaciones extraterritoriales | `vab_r_s_t_u_millones_q_2023` | `participacion_r_s_t_u_pct_2023` |

Los cuadros Banguat contienen cifras preliminares sujetas a revisión. El PIB mide producción territorial y el PIB por habitante expresa esa producción por persona de referencia. La distribución del ingreso o del consumo entre hogares requiere otras medidas. Las asociaciones entre estos agregados y ENCOVI solo admiten interpretación descriptiva a escala departamental. [Metadatos y procedencia del PIB](metadata_pib.md) · [Contratos de I-04 e I-05](CONTRATOS_DE_DATOS.md)

DINESE puede incorporarse como capa descriptiva independiente de empresas registradas, con su propio año y cobertura. La matriz se limita a hogares, ocupación y producción agregados por departamento.

## Reproducción y controles

Desde la raíz del repositorio, con el entorno de pruebas del proyecto instalado:

```sh
python scripts/build_matriz.py
python -m pytest -q tests/test_matriz_m03.py
python -m pytest -q
```

El constructor solo requiere la biblioteca estándar de Python y los cinco CSV locales. `--data-dir` selecciona un directorio con las carpetas `processed/` y `reference/`. `--output` selecciona otro archivo de salida. La validación precede al reemplazo atómico del CSV. Cualquier error conserva la salida anterior.

Las pruebas contrastan todos los importes y diagnósticos con los originales, recalculan cada participación con aritmética decimal y comprueban la actividad predominante. La conciliación exige `|PIB − VAB − IPNS| ≤ 0.000001` millones de Q. La suma de participaciones debe diferir de 100 en como máximo `0.000000001` puntos porcentuales. Se prueban entradas alteradas, ausencia de nulos críticos, publicación restringida y regeneración idéntica en bytes con acceso de red bloqueado y con los insumos en orden inverso. Los controles de cinco restricciones y sus departamentos corresponden al corte de 2023 y deben revisarse ante una nueva versión de las fuentes.
