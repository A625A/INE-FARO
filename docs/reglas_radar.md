# Radar territorial · corte estándar de 2023

Desde la raíz del proyecto, generar el corte estándar con Python 3.10 o posterior:

```sh
python scripts/radar.py --data-dir data --config config/radar_m04_v1.json --mode standard --output-dir data/processed
```

R1 evalúa las parejas de los 22 departamentos de 2023. Exige una diferencia absoluta de ocupación en el sector informal de hasta 3 pp y al menos uno de estos contrastes: brecha absoluta de pobreza total de 15 pp o más, o razón del mayor PIB por habitante al menor de 1.5 o más. Cada motivo requiere sus dos medidas elegibles. Un estado restringido, muestra inferior a 30, CV superior a 30 % o CV indefinido suprimen valor e intervalo de ENCOVI. El cociente productivo exige dos valores positivos. La regla compara a precisión de entrada. Ordena primero ambos motivos, luego solo pobreza y finalmente solo PIB. En cada bloque prioriza brecha de pobreza y razón de PIB descendentes, brecha laboral ascendente y códigos INE ascendentes. Los nulos van al final.

| Variante | Detección estándar | Orden anterior al desempate por código y grupo |
|---|---|---|
| R2a | PIB por habitante y ocupación en el sector informal superiores a sus medianas simples | Exceso laboral y exceso de PIB por habitante, descendentes |
| R2b | PIB por habitante superior a su mediana, pobreza total al menos 15 pp por encima de su mediana y tasa laboral al menos igual a la nacional ponderada | Exceso de pobreza y exceso de PIB por habitante, descendentes |
| R3 | Mitad de la suma de las diferencias absolutas de las 17 participaciones, hasta el P25 inclusive, con brecha laboral de al menos 10 pp | Brecha laboral descendente y distancia ascendente |
| R4 | LQ de al menos 1.5, participación local de al menos 10 %, tasas laboral y de pobreza superiores a sus medianas | LQ y participación local descendentes |

Las medianas usan los valores elegibles de cada indicador. El P25 interpola linealmente en la posición 0.25 × (n − 1) de las distancias ordenadas desde cero. Una tasa laboral restringida impide evaluar el contraste de esa pareja sin alterar la distribución de distancias productivas. El denominador del LQ es la participación del grupo en la suma del VAB corriente de los 22 departamentos. Un grupo con VAB agregado cero queda fuera de la evaluación de LQ.

La ficha documenta fuentes, universos, ponderadores y precisión. Los IC95 y CV son aproximaciones con DEPTO/UPM. Las brechas describen estimaciones puntuales. El PIB por habitante expresa producción territorial por persona.

El modo `--mode exploratory --set r1_i=2` admite los valores de la rejilla versionada. La robustez divide las apariciones de una ficha entre los escenarios de su variante, con la base contada una vez. R1 tiene siete escenarios, R2a uno, R2b tres, R3 cinco y R4 cinco. El archivo de sensibilidad identifica las fichas que entran o salen frente al estándar. La opción repetible `--rule` permite seleccionar variantes. La opción repetible `--depto 04` muestra parejas que incluyen algún código solicitado. Las referencias y la sensibilidad conservan el universo completo.

Las rutas públicas son `hallazgos.json`, `hallazgos.csv` y `radar_fuentes.json`. CSV presenta una ficha por fila, con campos anidados como JSON. El manifiesto contiene hashes brutos y el JSON principal incluye los hashes canónicos. El publicador necesita un sistema de archivos con enlaces simbólicos. Prepara los tres archivos y cambia un único enlace. Un consumidor que abra varias salidas durante una regeneración puede resolver `.radar_m04/actual` una sola vez y leerlas desde ese directorio. Al copiar el paquete, conservar los enlaces y el directorio oculto, o copiar los archivos resueltos.
