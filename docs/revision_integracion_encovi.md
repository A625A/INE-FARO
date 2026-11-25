# Cambios concurrentes del equipo: precauciones para M-01

Inspección de lectura al cierre de I-04/I-05, 24/11/2026. No se modificó ni integró
trabajo de I-02. Su commit nuevo es
[476155b](https://github.com/A625A/INE-FARO/commit/476155bfa997941de07471dd996027fe69dee729),
ya contenido en el main remoto observado 5a5fb8f. Por eso el diagnóstico inicial
de «sin exploración publicada» dejó de describir el remoto y se actualizó.

La entrega añade un diccionario preliminar, resumen y notebook. El notebook
guardado tiene execution_count nulos y outputs vacíos: eso no acredita ejecución,
aunque el resumen proponga un notebook ejecutado como entregable. No se ejecutó
ese notebook en esta tarea ni se considera cerrada su validación científica.

El diccionario nuevo describe `pobreza` como binaria 1/0 e incluye nombres como
`ingreso_hogar`, `informalidad` y `consumo_total`. Antes de consumirlos, contrastar
con los diccionarios/SAV originales: POBREZA clasifica pobre extremo, pobre no
extremo y no pobre; FORMAL_INFORMAL tiene 1=Informal, 2=Formal. No asumir columnas
derivadas sin una transformación y definición reproducibles. Tampoco tratar
Factor3 como un ponderador alternativo genérico por dominio.

Estas advertencias son verificaciones de integración, no una sustitución de I-02.
El acuerdo de Q1 permanece: universo de ocupados, edad, códigos, denominador,
pesos y diseño deben validarse, reproducir 70.3% nacional e investigar diferencias
antes de publicar indicadores. I-04/I-05 no usan las columnas nuevas ni dependen
del notebook. No hay una decisión humana nueva necesaria para continuar sus
entregables; sí debe revisarse I-02 antes de M-01.
