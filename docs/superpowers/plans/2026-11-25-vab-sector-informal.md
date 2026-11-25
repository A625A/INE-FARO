# Plan de implementación del VAB nacional

**Objetivo.** Entregar dos tablas nacionales reproducibles y evidencia que permita verificar cada cociente.
**Arquitectura.** Un CLI lee snapshots Banguat con openpyxl y reutiliza procedencia, descarga y escritura de comun.py. Un cotejo independiente contrasta los agregados publicados con los XLSX.
**Especificación.** docs/specs/VAB-sector-informal.md. Ejecutar en la rama feature/vab-sector-informal creada desde ee41cce. Commits locales por tarea.
**Restricciones.** Grano nacional. Años comunes 2013–2019 y 2021–2024, precios explícitos, vacíos para medidas inaplicables. Usar los totales encadenados publicados.
**Foco de revisión.** Encabezados anuales duplicados, columna de variaciones adyacente a niveles, subtotales CCIS, años preliminares y asignación NAEG incompatible.

### 1. Fijar las fuentes y sus formatos

- [ ] Registrar URL, SHA-256, edición y consulta en data/reference/fuentes_vab_informal.json. Conservar los dos XLSX en data/raw/banguat_nacional para reproducción local.
- [ ] En tests/test_vab_informal.py escribir pruebas de las funciones lectoras en scripts/procesar_vab_informal.py. Verificar años, unidad, grupos, duplicados, nulos y S1/B1b. Ejecutar pytest del módulo y observar fallo.
- [ ] Leer encabezados, claves y valores; rechazar discrepancias que superen el redondeo de las celdas oficiales. Ejecutar las mismas pruebas y guardar el cambio.

### 2. Publicar observaciones y cocientes admisibles

- [ ] Con los lectores de 1, probar el CLI con directorios de salida temporales y el caso de correspondencia incompleta. Verificar alcance de tasas, campos vacíos, ceros, exclusión de 2020 y unicidad antes de implementar.
- [ ] Escribir data/processed/vab_informal_nacional.csv (año y precio) y vab_informal_grupo.csv (año, precio y grupo). Añadir evidencia de conciliación por año y estado del mapeo.
- [ ] Ejecutar dos veces. Comparar los bytes de ambos CSV y evidencia. Confirmar fallo por hash alterado y conservar las salidas previas ante error de validación. Commit del CLI y contrato.

### 3. Reproducir y revisar

- [ ] Verificar los cuatro controles desde celdas oficiales, por una vía independiente del procesador. Cotejar comercio con el bloque de estructura y guardar cifras y diferencias.
- [ ] Documentar en docs/VAB_CONTRATO_M05.md cómo leer, representar faltantes y reproducir. Ejecutar suite completa, compileall y git diff --check.
- [ ] Revisar el diff completo con revisor independiente, atender hallazgos y verificar nuevamente. Entregar rutas, commits, cifras y limitaciones.
