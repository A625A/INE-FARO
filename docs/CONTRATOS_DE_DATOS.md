# Contratos I-04 / I-05

Versión local validada el 24/11/2026. Extiende las propuestas del paquete de
contexto; no altera consumidores existentes, pues aún no están publicados.

| Archivo | Clave | Columnas |
|---|---|---|
| `pib_departamental.csv` | depto_id, anio, sector, tipo_precio | depto_id, departamento, anio, sector, pib_valor, unidad, tipo_precio, fuente, medida |
| `pib_per_capita.csv` | depto_id, anio | depto_id, departamento, anio, pib_per_capita, unidad, tipo_precio, fuente |
| `pib_conciliacion.csv` | anio, sector, tipo_precio | anio, sector, medida, tipo_precio, unidad, suma_departamentos, extrarregional, nacional, diferencia, estado, nota, fuente |
| `dinese_resumen.csv` | depto_id, anio, seccion_codigo, movimiento_ventas | depto_id, departamento, anio, seccion_ciiu_4, seccion_codigo, sector_banguat, movimiento_ventas, empresas, unidad, fuente, uso, crecimiento_habilitado |

`depto_id`: texto 01–22. No asignar código departamental a Nacional ni
Extrarregional. La conciliación no se une al mapa. CSV UTF-8, coma separadora,
punto decimal, vacíos para componentes no publicados, nunca ceros sustitutos.

PIB: filtrar año/tipo_precio/sector antes de unir. `medida` distingue PIB total,
VAB e impuestos. Per cápita usa quetzales por habitante y va separado.
DINESE: conteos por snapshot; el único uso habilitado es descriptivo transversal.
Las combinaciones ausentes no son filas vacías ni estimaciones imputadas.

La tabla de indicadores ENCOVI, la matriz departamental y los hallazgos siguen
pendientes. Estos contratos no autorizan joins individuales entre instituciones.
