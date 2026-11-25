# ENEIC IV-2025 para M-05

## Reproducción

Desde la raíz, con las dependencias de requirements.txt instaladas.

```sh
python scripts/procesar_eneic.py
python scripts/procesar_eneic.py --input-dir data/raw/eneic_iv_2025 --output-root /tmp/eneic-reproduccion
python -m pytest -q
```

La ejecución normal utiliza los archivos locales. `--download` permite recuperar únicamente los snapshots fijados por SHA-256 cuando falten. Un cambio de hash requiere revisión explícita del manifiesto. Se verifican también el diccionario y el boletín antes de procesar. Los XLSX y PDF permanecen en raw ignorado por Git. La base contiene 49,338 personas y la clave ANIO, TRIMESTRE, DOMINIO, NUM_HOGAR, NUM_PERSONA es única incluso fuera del universo laboral.

## Entrada pública

M-05 debe leer exclusivamente `data/processed/eneic_iv_2025/agregados_publicos.csv`. Clave única `(periodo, dimension, categoria, indicador)`. CSV UTF-8, coma, punto decimal, LF y blancos para ausentes. Schema 1.0. El productor publica 21 celdas mediante lista cerrada en `data/reference/controles_eneic_iv_2025.json`.

- Nacional y tres dominios, tasa de ocupación en el sector informal y media laboral.
- Nacional, población ocupada y volúmenes informal y formal.
- Diez ramas oficiales, composición de toda la población ocupada.

Cada fila incluye `valor`, `valor_oficial`, `unidad`, `denominador`, `n`, `n_ocupados`, `cobertura_pct`, `ponderador`, `fuente`, `referencia`, `estado`, `precision`, `tipo_validacion`, `ic95_inf`, `ic95_sup`. `estado=oficial_conciliado` identifica las filas habilitadas. `valor` conserva precisión calculada y `valor_oficial` la precisión publicada. Los intervalos disponibles se transcriben del boletín a su precisión original. No se estiman CV ni intervalos nuevos.

Para tasas, el denominador es el peso de ocupados con condición válida y n su muestra. Para ingreso, es el peso de ocupados con ingreso numérico y n su muestra. Para volumen ocupado, `denominador` expresa la población de referencia ocupada. Para los volúmenes por condición, expresa el conjunto de ocupados clasificados. Para composición por rama, es el total nacional de ocupados y n la muestra de la rama. La cobertura de clasificación e ingreso se calcula respecto al peso de todos los ocupados del corte.

Los volúmenes informal y formal nacionales tienen `tipo_validacion=derivado_conciliacion_indirecta`. Son sumas de FACTOR conciliadas con la réplica independiente y con la tasa y población ocupada oficiales. El boletín no aporta una tabla explícita de esos dos volúmenes. Las restantes filas tienen contraste directo. La composición oficial por rama describe todos los ocupados. La composición del sector informal por rama se conserva en diagnóstico interno.

M-05 selecciona filas existentes por sus claves, muestra período, unidad, denominador y calidad, y descarga la misma selección. No recalcula medias sumando celdas, ni crea cruces de filtros, ni genera departamentos a partir de dominios. El campo `rama_ine` identifica grupos 1–10 del boletín. La correspondencia a los 17 grupos existentes de CIIU/Banguat permanece en diagnóstico, con clave `periodo, grupo_ciiu`. Su uso conjunto requiere homologar período, cobertura y valoración.

## Diagnósticos y precisión

`docs/evidencia/eneic_iv_2025/diagnosticos_internos.csv` está separado físicamente del directorio público. Todas sus filas tienen `estado=solo_revision_interna`. Contiene márgenes simples de dominio, sexo, edades 15–24, 25–44, 45–64 y 65+, tamaño, grupo CIIU, rama INE y condición, además del nacional. Incluye cobertura, n, sumas de peso, ingreso medio y mediana. Los ceros observados se mantienen. Los blancos quedan fuera del ingreso válido. La mediana es el primer ingreso cuyo peso acumulado alcanza 50% del peso válido.

El tamaño P05C13 incluye al dueño y corresponde a la empresa o negocio de la ocupación principal. Sus 11 categorías proceden del diccionario, con respuesta en los 21,233 ocupados. Las sumas describen personas ocupadas por tamaño de unidad. El tamaño interviene en la clasificación del sector, lo cual limita la interpretación de asociaciones. Las variables candidatas de protección del puesto requieren validación adicional.

La base pública aporta FACTOR trimestral y DOMINIO. No se identificaron UPM ni estrato. Los cortes nuevos y las medianas carecen de precisión acreditada y permanecen internos. Las comparaciones son descriptivas, con períodos explícitos. FORMAL_INFORMAL clasifica el sector de la unidad económica. Medir empleo informal requiere una medida independiente del puesto.

## Procedencia y discrepancias

El snapshot fijado en `fuentes_eneic_iv_2025.json` fue consultado el 25/11/2026 y corresponde a junio de 2026. Los 49,338 registros tienen ANIO=2025 y TRIMESTRE=5. Este código observado identifica el archivo rotulado IV-2025 y se exige como control, sin sustituirlo por 4.

La revisión de julio del boletín tiene SHA-256 `7912c384e8672b61652622bcac62c0826edcc89e445c9fba84e4bdecbded50fc`. La investigación aceptada encontró cifras laborales pertinentes iguales a las del snapshot de junio. La gráfica 4 publica 20.1% agricultura y 25.3% industria para IV-2025. La tabla 2 y el XLSX concilian agricultura 19.8730% (19.9 publicado), y la agregación industrial del XLSX da 25.5522%. La referencia seleccionada para ramas es la tabla 2. Las cifras discrepantes de la gráfica 4 quedan excluidas de publicación.

El catálogo de 88 divisiones CIIU Rev.4 se verifica contra el diccionario. Se observaron 82, con seis válidas sin muestra (05, 06, 09, 19, 31, 39). Las divisiones se relacionan por código, primero a sección y luego al catálogo existente. 99 en dos dígitos es sección U, y 999 es no declarado. Los huecos estructurales y códigos no reconocidos conservan peso en `Sin clasificar`. En la base aceptada no hay ocupados sin rama clasificada. La correspondencia con P05C04_1D se comprueba registro a registro. Las diferencias ortográficas del diccionario conservan sus códigos.

Fuentes oficiales consultadas durante la validación inicial.

- [Portal ENEIC](https://www.ine.gob.gt/encuesta-nacional-de-empleo-e-ingresos/).
- [Boletín fijado, edición 3](https://www.ine.gob.gt/wp-content/uploads/2026/06/Boletin-Estadistico-Edicion-No.3-ENEIC-2025-1.pdf).
- [Revisión de julio](https://www.ine.gob.gt/wp-content/uploads/2026/07/Boletin-Estadistico-Edicion-No.3-ENEIC-2025-2.pdf).
- [CIIU Rev.4, Naciones Unidas](https://unstats.un.org/unsd/classifications/Econ/Download/In%20Text/ISIC_Rev_4_publication_Spanish.pdf).

## Evaluación y operación

La réplica XML/SQLite aceptada usa exclusivamente biblioteca estándar y no importa el productor. Su código y resultado se preservan en `docs/evaluation/eneic_iv_2025/`. La CLI compara sus resultados nacionales y los tres dominios para n, volumen, tasa, media, mediana, ceros y cobertura. Los controles esperados son 21,233 ocupados, 7,944,838 expandidos, 65.628701% nacional y media Q2,842 sobre 20,239 ingresos válidos. Se conservaron 535 ceros y 994 faltantes.

Las entradas inválidas y divergencias se rechazan antes de escribir. Cada archivo se reemplaza atómicamente, con temporales únicos. El CSV público es una única unidad de publicación. El diagnóstico y la evidencia se escriben antes de ese CSV. La evidencia incluye SHA del CSV público para detectar una interrupción o concurrencia entre archivos, que no forman una transacción conjunta. El consumidor público usa únicamente el CSV. No se requiere red para consultar los agregados entregados.
