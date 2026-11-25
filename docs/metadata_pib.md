# I-04 — PIB departamental Banguat

Estado: procesado y validado localmente, 24/11/2026 (Guatemala). No integrado en
main ni publicado. Año seleccionado: 2023; cobertura de encabezados originales:
2013–2024. No se afirma haber validado todas las celdas de todos los años.

## Fuentes y versión

[Catálogo oficial Banguat](https://banguat.gob.gt/page/cuadros-estadisticos-por-departamento-2013-2024).
Se usan los tres XLSX del equipo, cuyo SHA-256 se comparó con descargas oficiales
independientes. URLs, tamaños y hashes: `data/reference/fuentes_I04_I05.json`.
Prueba de coincidencia: `docs/evidencia/verificacion_descargas.json`.
Los [cuadros oficiales](https://banguat.gob.gt/sites/default/files/banguat/Publica/PIB_Regional/6_Resultados_por_departamento.pdf)
advierten cifras preliminares y revisables. Una nueva versión debe revisarse; el
modo de descarga no reemplaza silenciosamente archivos con distinto hash.
El portal tiene derechos reservados; no se presume una licencia abierta genérica.

## Medidas y salidas

| Salida | Unidad de observación | Filas 2023 | Uso |
|---|---|---:|---|
| `pib_departamental.csv` | departamento × sector/total × valoración | 836 | integración con agregados ENCOVI |
| `pib_per_capita.csv` | departamento × año | 22 | producción por habitante |
| `pib_conciliacion.csv` | sector/total × valoración × año | 38 | conciliación nacional, no mapa |

La primera salida conserva las ocho columnas del contrato propuesto y añade
`medida`. No existe aún un consumidor publicado que necesite migración.

- `sector=TOTAL`, `medida=pib_total`: PIB total departamental.
- 17 grupos CIIU, `medida=valor_agregado`: valor agregado por actividad. Se preserva
  la denominación del cuadro; no se llama PIB sectorial al valor agregado.
- `sector=IPNS`, `medida=impuestos_netos`: impuestos netos de subvenciones a productos.
  Es un componente contable, no una actividad ni una empresa.
- `tipo_precio=corrientes`: cifras corrientes, en millones de quetzales.
- `tipo_precio=volumen_encadenado_2013`: millones de quetzales en medidas
  encadenadas de volumen, referencia 2013. No se reinterpretan como una serie
  aditiva de precios fijos.
- PIB por habitante conserva quetzales por habitante, separado de millones. Se
  toma la cifra oficial; no se reconstruye con otra versión poblacional. La nota
  del XLSX identifica las proyecciones INE 2010–2050 como denominador.

Secciones de Banguat: A, B, C, D-E, F, G, H, I, J, K, L, M, N, O, P, Q, R-S-T-U.
La fuente agrupa D+E y R+S+T+U. Las etiquetas de actividad se conservan en el
catálogo `data/reference/sectores_ciiu.csv` para interpretar las letras, sin
desagregar artificialmente los grupos de Banguat.

## Identificación territorial

`depto_id` es texto de dos dígitos, 01–22, en el orden oficial INE. Se contrastó
con el diccionario ENCOVI Personas publicado por el equipo y con el número y
nombre de cada fila Banguat. El lector exige coincidencia, sin inferencia difusa.
El catálogo común está en `scripts/comun.py`. Se normalizan acentos, mayúsculas y
espacios únicamente para reconocer nombres; la salida usa nombres canónicos.

## Controles ejecutados

Se exige cobertura 22, clave única, datos numéricos finitos no negativos,
encabezados 2013–2024, bloques y unidades esperados, total nacional y componente
extrarregional cuando se publica. No se leen los bloques de estructura porcentual
ni las variaciones como si fueran niveles.

En corrientes se verifican:
1. Cada grupo nacional = suma de departamentos + Extrarregional publicado.
2. Cada PIB departamental = 17 valores agregados + IPNS.

Tolerancia absoluta: 0.000001 millones de quetzales, sin redondear las salidas.
En 2023 el PIB nacional corriente es 816859.8790241099 millones; Extrarregional
es 223.09231393999994 millones. IPNS no presenta componente extrarregional en el
bloque: se conserva nulo y nota explícita, y se concilia con los 22 departamentos.

Para volumen encadenado se registra la diferencia y `estado=no_aditivo`, sin
exigir igualdad. Por ejemplo, en el total 2023 la diferencia nacional respecto
de departamentos más Extrarregional es aproximadamente 535.864 millones. La
nota oficial atribuye la no aditividad a estructuras de precios de base móvil.
Esto no se corrige redistribuyendo residuos ni se usa como fallo contable nominal.

## Reproducir

```sh
python scripts/procesar_pib.py
python scripts/procesar_pib.py --download
python scripts/procesar_pib.py --year 2024 --output-dir tmp/pib2024 --evidence-dir tmp/pib2024
```

Sin `--download` no se usa la red. Con la opción se descargan archivos faltantes
y se exige el SHA-256 fijado. `--input-dir`, `--output-dir` y `--evidence-dir`
permiten trabajar en otra ubicación. Primero se valida toda la tarea; después se
escriben las salidas. Si falla la validación no se reemplazan salidas anteriores:
no deben tratarse como resultado de la ejecución fallida.

También sin descarga se exige coincidencia de SHA-256 con el manifiesto antes
de procesar. Para un snapshot nuevo se deben revisar su origen y controles y
actualizar el manifiesto explícitamente. `--manifest` selecciona otro manifiesto
ya revisado, útil para versiones documentadas y pruebas; no acredita por sí solo
que el operador haya obtenido los hashes de fuentes oficiales. Las pruebas
semánticas usan manifiestos de fixtures sintéticos en directorios temporales.

Evidencia técnica: `docs/evidencia/I-04.json`, con hashes y hoja/fila de encabezado/
columna del año de cada bloque. Las pruebas usan el comando completo y controles
literales de fuente; también alteran copias para detectar faltantes, duplicados,
año incompleto, unidades inesperadas y descuadres.

## Límites para la integración

Filtrar `anio=2023`, `sector=TOTAL`, `tipo_precio=corrientes` entrega una fila
por departamento. Nunca sumar TOTAL con sus componentes ni corrientes con volumen.
Para estructura nominal usar VAB/total VAB o VAB/PIB con denominador explícito;
la segunda opción deja los impuestos como componente restante. No construir
participaciones aditivas con volúmenes encadenados.

El PIB mide producción territorial, no ingreso, consumo, riqueza ni distribución
entre hogares. Coincidir en año y departamento no establece una unión individual
con ENCOVI ni demuestra causalidad. No se generó aún matriz, radar ni hallazgo.
