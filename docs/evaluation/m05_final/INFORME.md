# Evaluación de M-05 · INE FARO

Fecha de validación: 25 de noviembre de 2026, Guatemala. Rama de revisión:
`feature/M-05-integracion-final`. Base de GitHub verificada: `ee41cce`.

## Integraciones

| Orden | Rama revisada | Commit | Integración en M-05 |
| --- | --- | --- | --- |
| 1 | `feature/M-03-matriz-departamental` | `f731d26` | `4589df5` |
| 2 | `feature/M-04-radar` | `ba0afdc` | `88251dc` |
| 3 | `feature/eneic-iv-2025` | `24840a2` | `8462e46` |
| 4 | `feature/vab-sector-informal` | `d56d56c` | `047ba71` |
| 5 | `feature/M-05-precision-estadistica` | `17c7df3` | `3907c57` |
| 6 | `feature/m02-hogares-negocios` | `d6f76ca` | `ae5caa7` |

El historial conserva los seis commits revisados y sus ancestros. El
consumidor comparte el catálogo departamental, la clasificación de precisión
y el serializador de M-04. Los productores y sus pruebas se conservan.

## Controles y alcance científico

El [cotejo independiente](validar_consumo.py) lee los agregados con la biblioteca
estándar sin importar los productores ni la interfaz. Verifica el corte laboral
frente a los controles del boletín conciliados por ENEIC, recalcula las
participaciones corrientes del VAB y reproduce magnitudes de R1
(Chimaltenango–Alta Verapaz), el cero de R2a, R2b (Santa Rosa), R3
(Chimaltenango–Izabal) y R4 (Alta Verapaz, agricultura). Contrasta la robustez
de todas las fichas con las entradas y salidas de los escenarios. Se preservan
los [resultados y SHA-256](../../evidencia/M-05/final/controles.json).

| Control | Resultado |
| --- | --- |
| Matriz departamental | 22 filas × 67 columnas |
| ENCOVI | 66 estimaciones. Cinco restricciones de pobreza extrema. |
| M-02 | 207 filas. 14 restricciones. |
| ENEIC | 21 celdas públicas. 7,944,838 ocupados, 65.6 % en el sector informal, 5,214,094 estimados por conciliación indirecta y Q2,842 de ingreso medio y 94.28 % de cobertura ponderada. |
| VAB informal | 22 registros nacionales y 374 sectoriales. 2023: Q172,538.68 millones de VAB informal y 22.62 % del VAB total. Comercio: 38.55 % del VAB informal. |
| Radar | 44 fichas (R1 26, R2a 0, R2b 1, R3 7 y R4 10) y 21 escenarios. |

El cotejo es de consumo y de una muestra de magnitudes. La conciliación de
microdatos, la reproducción del boletín y la lectura de XLSX quedan trazadas
en las evaluaciones de los productores. La robustez mide estabilidad frente a
umbrales. Las tasas ENCOVI conservan precisión aproximada. Los intervalos de
ENEIC proceden del boletín cuando están disponibles.

## Contraste destacado

Desde Empleo e ingresos, **Ver contraste Chimaltenango–Alta Verapaz** abre
R1:2023:04-16 con ambas estimaciones, sus fuentes y diagnósticos abiertos, y
la ficha «¿Qué investigar ahora?». El segundo clic abre Territorio con ambos
departamentos seleccionados. La brecha de pobreza total es de 42.55 pp y la
de ocupación en el sector informal, de 0.98 pp. El contraste aparece en
7 de 7 escenarios de R1. Los datos proceden de la ficha validada de M-04.

## Pruebas y evidencia de navegador

Las dos pruebas heredadas recorren la navegación vigente. Mantienen los controles
de carga local, cobertura, PIB departamental, supresión de cifras e intervalos,
diagnóstico por CV y filtros con resultado vacío. El [resultado de pytest](../../evidencia/M-05/final/pytest.txt)
corresponde a la suite completa.

**Empleo e ingresos.** Con la leyenda y el título dentro de los 85 px originales,
la barra invadía las etiquetas del eje en 4,5 px. La gráfica de 125 px usa seis
marcas entre 0 y 100 %. Chromium midió 7 px libres entre la barra y los números
en [escritorio](../../evidencia/M-05/final/barra-escritorio.png) y
[móvil](../../evidencia/M-05/final/barra-movil.png).

**Territorio.** Los 22 códigos de la matriz corresponden a 22 geometrías del
catálogo. La proyección Mercator conservaba la forma del país, pero el canal
cuantitativo de Vega descartaba cinco filas con valor nulo al dibujar pobreza
extrema. El mapa conserva cada geometría y aplica gris según el estado de
publicación. En Chromium se seleccionó un punto interior de cada departamento
con ratón y por toque. En cada selección coincidieron el perfil y el selector.
El CSV conserva vacíos los cinco valores y sus intervalos.
[Mapa de escritorio](../../evidencia/M-05/final/mapa-escritorio.png) y
[mapa móvil](../../evidencia/M-05/final/mapa-movil.png).

**Radar.** Las cinco categorías se presentan con su nombre y una explicación de
los umbrales del corte estándar. Las fichas y exportaciones conservan sus
identificadores. El recorrido del contraste destacado abre la evidencia en un
clic y la comparación territorial en dos.

El recorrido Playwright usa un escritorio de 1440 × 1000 y una pantalla táctil
emulada de 390 × 844. El [registro de Chromium](../../evidencia/M-05/final/chromium.txt)
incluye navegación, selección, descargas, errores de consola y solicitudes externas.

```sh
python -m pytest -q
python docs/evaluation/m05_final/validar_consumo.py
```

La suite de productores puede necesitar los insumos originales que ignora Git.
La aplicación y las pruebas de consumo nuevas usan los agregados versionados.
Los scripts de consumo, capturas y resultado de Chromium se encuentran en
[prueba Playwright](../../../tests/browser/m05.cjs) y
[evidencia](../../evidencia/M-05/final/). Para repetir el recorrido: arrancar
Streamlit con `--server.port 8516`, instalar Playwright en un entorno Node
separado, instalar Chromium para Playwright y ejecutar
`node tests/browser/m05.cjs`. Cuando Chromium está instalado en otra ruta se
puede fijar `FARO_CHROME`. `BASE_URL` permite probar el ZIP extraído. El argumento `--destacado` ejecuta solo el recorrido prioritario.

## Diseño y proceso aplicado

Se usaron PDF para la lectura de la especificación, las guías Superpowers de
`using-superpowers`, `using-git-worktrees`, `brainstorming`, `writing-plans`,
`executing-plans`, `test-driven-development`, `systematic-debugging`,
`requesting-code-review` y `verification-before-completion`. La revisión se
hizo en esta sesión. Se aplicaron `analyze-data-quality`, `validate-data`,
`visualize-data` en su guía de codificación y revisión de gráficas, Unslop en
la revisión de la interfaz y Playwright en Chromium.

Se aplicaron los lineamientos de Superdesign para el
[sistema de diseño](../../../.superdesign/design-system.md) por vía local. La
versión on-demand del CLI no estaba en la caché y el flujo de canvas requiere
acceso externo. El kit aportó el imagotipo horizontal RGB, Ubuntu Sans
variable y su Ubuntu Font Licence 1.0. La guía confirmó los azules institucionales
`#004080` y `#0080FF` y blanco. Las figuras y la geometría usan los datos
del proyecto.

## Límites y decisiones

El ZIP es portable a sistemas sin enlaces simbólicos y se comprobó en macOS.
Se probó el puntero de texto que crea Git para Windows con enlaces desactivados. La instalación de Python y la ejecución en Windows nativo siguen pendientes de verificación.
El panel de sensibilidad usa los 21 escenarios ya calculados. DINESE se
mantiene como contexto metodológico. Los cruces de pobreza por perfil del
hogar y los cortes ENEIC sin publicación validada permanecen pendientes.
La rama queda para revisión y M-06 recibe el [handoff](HANDOFF_M06.md).
