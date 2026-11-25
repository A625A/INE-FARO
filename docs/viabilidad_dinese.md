# I-05 — Viabilidad de DINESE 2023–2024

Estado: auditoría completa local, 24/11/2026 (Guatemala). No integrado ni publicado.

## Dictamen

**Viable para descripción transversal separada por año. Comparabilidad temporal
insuficientemente acreditada para habilitar crecimiento empresarial en el radar.**
La capa 2023 queda preparada como complemento opcional de ENCOVI/PIB 2023.
Se excluyen las interpretaciones de creación de empresas, altas/bajas netas y
formalización laboral. Es la condición ya autorizada del MVP; I-05 no bloquea I-04.

## Evidencia verificada

Se auditaron todas las filas de los dos XLSX del
[catálogo oficial](https://datos.ine.gob.gt/dataset/directorio-nacional-estadistico-de-empresas-dinese),
que declara Creative Commons Attribution. Los cinco insumos I-04/I-05 coinciden
por SHA-256 con descargas oficiales independientes. Manifiesto y prueba en
`data/reference/fuentes_I04_I05.json` y `docs/evidencia/verificacion_descargas.json`.

| Año del archivo | Empresas activas | Con movimiento de ventas | Sin movimiento |
|---|---:|---:|---:|
| 2023 | 425464 | 220903 | 204561 |
| 2024 | 645431 | 338415 | 307016 |

Los totales y con movimiento concilian con el
[resumen oficial 2023, cuadros 4 y 7](https://www.ine.gob.gt/wp-content/uploads/2024/12/Resumen-Base-de-datos-DINESE.pdf)
y el [resumen 2024, cuadros 1 y 6](https://www.ine.gob.gt/wp-content/uploads/2026/03/RESUMEN-ESTADISTICO-FORMATO-DINESE.pdf).
Sin movimiento se obtiene por diferencia y también por conteo de registros.
Guatemala concilia adicionalmente: 209804/108182 (total/con ventas) en 2023 y
235807/120141 en 2024.

En ambos archivos se verificaron ocho columnas, AÑO esperado, códigos positivos
únicos dentro de año, 22 departamentos, 21 secciones CIIU Rev.4 y las categorías
Con/Sin movimiento. No hubo filas descartadas ni faltantes en personería, rango
de ventas o municipio. No se auditaron el catálogo municipal, las ventas monetarias
individuales ni la identidad jurídica de cada registro. El archivo no contiene
un importe de ventas: `CLA_RANGO_VENTAS` es una clasificación, no dinero sumable.

El resumen 2024 contiene una discrepancia: cuadro 2, Enseñanza, muestra 7073 y
2.65%; el XLSX auditado contiene 17073 registros, coherente con ese porcentaje
redondeado. No se modifica la fuente ni se adopta 7073 como control. Se priorizan
los datos descargados y los controles nacionales/departamentales conciliados.

## Universo y comparabilidad

El total corresponde al directorio de empresas activas registradas SAT/INE, con
y sin movimiento de ventas. No representa todas las empresas del país ni toda
la economía informal. El INE llama económicamente activas al subconjunto con
movimiento. No se transforma esa clasificación administrativa en condición
laboral de las personas.

La [metodología oficial de actualización](https://www.ine.gob.gt/wp-content/uploads/2023/12/METODOLOGIA-DE-ACTUALIZACION-DINESE.pdf)
documenta interrupción en 2021 y reanudación a finales de 2022, depuración de
registros y adaptación de catálogos. **No demuestra un cambio específico
2023–2024 que explique el aumento observado.** Tampoco se localizó una garantía
de persistencia interanual del CÓDIGO público ni una tabla puente de universos.
No se atribuye el aumento a la interrupción histórica ni a creación real.

La estructura y los nombres sectoriales coinciden entre snapshots; eso permite
describir sus conteos, pero no prueba cobertura administrativa estable. La
distinción empresa/establecimiento y ubicación registrada/actividad efectiva
tampoco autoriza enlazar el directorio con hogares o identificar formalizaciones.

Se conserva AÑO=2023/2024 tal como aparece en los archivos. La metodología explica
un proceso anual con datos SAT del año anterior: no se resta un año sin validación
específica. Publicación, referencia y descarga se documentan separadamente: los
boletines son de diciembre 2024/2025; el recurso 2024 se publicó en marzo 2026.
Más evidencia y enlaces de historial en `docs/evidencia/investigacion_dinese.md`.

## Contrato y reproducción

`data/processed/dinese_resumen.csv` tiene 1750 grupos observados (876 de 2023 y
874 de 2024), por departamento × sección × movimiento × año. `empresas` cuenta
registros, no personas. Las combinaciones sin registros no se materializan.
La clave es `(depto_id, anio, seccion_codigo, movimiento_ventas)`.

`seccion_codigo` conserva A–U. `sector_banguat` ofrece correspondencia explícita:
D y E → D-E; R, S, T y U → R-S-T-U; las otras letras permanecen. La correspondencia
prepara una agregación, no vincula empresas específicas a producción o empleo.
No mezclar los dos años en un total ni calcular crecimiento como indicador del
MVP. `crecimiento_habilitado=no` y la evidencia JSON mantienen esa exclusión.

```sh
python scripts/auditar_dinese.py
python scripts/auditar_dinese.py --download
```

Se admiten directorios de entrada/salida/evidencia. Sin `--download` no se usa la
red. La descarga verifica SHA-256 y no reemplaza archivos distintos. Se validan
ambos años antes de escribir CSV y `docs/evidencia/I-05.json`. Un fallo no debe
confundirse con las salidas válidas de una ejecución anterior.

Para reconsiderar el uso temporal hacen falta documentación de cobertura y
depuración comparable, tratamiento de revisiones y prueba del significado de
los identificadores. No hay un bloqueo que requiera nueva decisión del usuario.
