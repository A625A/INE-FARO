# Evaluación del radar territorial 2023

Con la matriz M-03 del commit `f731d26`, el corte estándar contiene **44 hallazgos**. El evaluador lee los indicadores departamentales y nacionales de M-01, el PIB por habitante y los VAB sectoriales corrientes de I-04. Reconstruye las participaciones desde importes y usa tablas de pandas y el percentil lineal de NumPy. Contrasta la publicación del motor, que compara con Decimal, sin importar sus reglas.

| Variante | Hallazgos | Caso de control y sensibilidad |
|---|---:|---|
| R1 | 26 | Chimaltenango–Alta Verapaz presenta una brecha de pobreza de 42.55 pp. Aparece en 7/7 escenarios. |
| R2a | 0 | Ningún departamento supera simultáneamente las medianas de PIB por habitante y ocupación en el sector informal. La prueba sintética cubre un caso positivo y empates. |
| R2b | 1 | Santa Rosa supera la mediana de pobreza en 20.28 pp. Permanece con márgenes de 10, 15 y 20 pp. |
| R3 | 7 | Chimaltenango–Izabal presenta una distancia de 9.85 pp y una brecha laboral de 16.08 pp. Aparece en 5/5 escenarios. |
| R4 | 10 | Agricultura representa 20.31 % del VAB de Alta Verapaz, con LQ de 1.97. Aparece en 4/5 escenarios y sale cuando el LQ mínimo sube a 2. |

Se recalcularon las **231 parejas** y las **374 combinaciones departamento–grupo**. El P25 de distancia fue **12.24314885 pp**. Los 21 escenarios coincidieron en IDs y orden con los cálculos independientes. Se comprobaron también las diferencias frente a la base y la fracción de escenarios de cada ficha. [Detalle de sensibilidad](radar_sensitivity.csv) · [Referencias, casos y SHA-256](radar_validation.json)

Las cinco restricciones de publicación del insumo corresponden a pobreza extrema. Las pruebas introducen restricciones adicionales en los indicadores usados por las reglas y comprueban la exclusión de valores e intervalos. Las fichas describen comparaciones de estimaciones puntuales con precisión aproximada de ENCOVI. La tasa laboral se refiere al departamento. La especialización se refiere al VAB del grupo económico.

## Reproducción y evidencia

Desde la raíz del repositorio con las dependencias del proyecto:

```sh
python scripts/radar.py --mode standard --output-dir data/processed
python scripts/evaluar_radar.py
python -m pytest -q
```

La suite completa pasó **127 pruebas** en 55.21 s, incluidas 61 de M-04. Las verificaciones cubrieron fronteras, orden, selección vacía, calidad, paridad CSV/JSON, permutación de entradas y conservación de la publicación ante un insumo inválido. Una segunda generación en un directorio temporal, con eventos de red bloqueados, reprodujo byte por byte ambos archivos de hallazgos, el manifiesto bruto y los dos archivos de evaluación legibles por máquina.

La rama se apoya en M-03, PR #6 abierto al publicar. El alcance de R4 es la especialización de 2023. Para habilitar dinamismo histórico se requieren cortes anuales 2019–2023 y la comparación de cada serie local de volumen encadenado con la serie nacional oficial de la misma rama, conforme a la página 8 de la especificación.
