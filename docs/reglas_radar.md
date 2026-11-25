# Radar territorial · R1

Desde la raíz del proyecto, generar el corte estándar con Python 3.10 o posterior:

```sh
python scripts/radar.py --data-dir data --config config/radar_m04_v1.json --mode standard --rule R1 --output-dir data/processed
```

R1 evalúa las parejas de los 22 departamentos de 2023. Exige una diferencia absoluta de ocupación en el sector informal de hasta 3 pp y al menos uno de estos contrastes: brecha absoluta de pobreza total de 15 pp o más, o razón del mayor PIB por habitante al menor de 1.5 o más. Cada motivo requiere sus dos medidas elegibles. Un estado restringido, muestra inferior a 30, CV superior a 30 % o CV indefinido suprimen valor e intervalo de ENCOVI. El cociente productivo exige dos valores positivos. La regla compara a precisión de entrada. Ordena primero ambos motivos, luego solo pobreza y finalmente solo PIB. En cada bloque prioriza brecha de pobreza y razón de PIB descendentes, brecha laboral ascendente y códigos INE ascendentes. Los nulos van al final.

La ficha documenta fuentes, universos, ponderadores y precisión. Los IC95 y CV son aproximaciones con DEPTO/UPM. Las brechas describen estimaciones puntuales. El PIB por habitante expresa producción territorial por persona.

El modo `--mode exploratory --set r1_i=2` admite los valores de la rejilla versionada. La robustez de cada ficha es su frecuencia en siete escenarios de R1: la base y seis cambios de un solo parámetro. La opción repetible `--depto 04` muestra parejas que incluyen algún código solicitado. Las referencias y la sensibilidad conservan el universo completo.

Las rutas públicas son `hallazgos.json`, `hallazgos.csv` y `radar_fuentes.json`. CSV presenta una ficha por fila, con campos anidados como JSON. El manifiesto contiene hashes brutos y el JSON principal incluye los hashes canónicos. El publicador necesita un sistema de archivos con enlaces simbólicos. Prepara los tres archivos y cambia un único enlace. Un consumidor que abra varias salidas durante una regeneración puede resolver `.radar_m04/actual` una sola vez y leerlas desde ese directorio. Al copiar el paquete, conservar los enlaces y el directorio oculto, o copiar los archivos resueltos.
