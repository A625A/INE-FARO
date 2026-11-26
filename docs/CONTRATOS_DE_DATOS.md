# Contratos I-04 / I-05

Contrato de origen validado el 24 de noviembre de 2026 para las salidas de PIB
departamental y DINESE. El [expediente del corte v1.1](entrega/README.md) y su
[arquitectura](entrega/arquitectura.md) describen los consumidores integrados.

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

La [matriz M-03](M03_CONTRATO_MATRIZ.md) incorpora los indicadores ENCOVI y el
PIB departamental de 2023. Es la entrada departamental del [radar M-04](reglas_radar.md).
Los cruces entre instituciones usan agregados territoriales.
