# INE FARO · Entrega del Datatón INE 2026

**Corte v1.1 del 25 de noviembre de 2026.** INE FARO es un prototipo local para comparar la ocupación en el sector informal y las condiciones de vida de los 22 departamentos de Guatemala, cuantificar el aporte productivo del sector informal a nivel nacional y encontrar contrastes que el Instituto Nacional de Estadística (INE) pueda investigar.

La entrega está fijada en `63af665b30b567c662b8098946595e2df4ab0c9e`, que incorpora el cierre M-06 sobre la integración M-05 de `8bc88f8`. El PR #8 tramita ese corte hacia `main`. El expediente reúne la revisión técnica y los pasos de recepción. [Commit de entrega](https://github.com/A625A/INE-FARO/commit/63af665b30b567c662b8098946595e2df4ab0c9e) · [PR #8](https://github.com/A625A/INE-FARO/pull/8) · [Checklist de entrega](../checklist_entrega.md)

## Cómo usar el expediente

| Necesito | Abrir |
| --- | --- |
| Presentar la demo | [ZIP del jurado](../evidencia/entrega/INE-FARO-Dataton.zip) · [presentación de cinco diapositivas](../../presentacion.pdf) · [guion de siete minutos y respuestas](../guion_demo.md) |
| Comprobar de dónde salen las cifras o mantener el código | [Arquitectura, contratos y reglas](arquitectura.md) |
| Instalar, repetir las pruebas o reconstruir el ZIP | [Guía de reproducción y verificación](reproduccion.md) · [SHA-256](../evidencia/entrega/SHA256SUMS) |
| Ver el criterio de aceptación y sus resultados | [Revisión de aceptación](../revision_final.md) · [validación del corte](../evidencia/entrega/VALIDACION.md) · [registro de Chromium](../evidencia/entrega/chromium.txt) |

## Qué puede mostrar el tablero

| Vista | Qué se puede consultar | Referencia |
| --- | --- | --- |
| Empleo e ingresos | ENEIC IV-2025, Encuesta Nacional de Empleo e Ingresos Continua. Para Guatemala, 65.6 % de ocupados en el sector informal y Q2,842 de ingreso laboral medio. El 94.28 % es la proporción ponderada de ocupados con ingreso válido. Incluye Urbano Metropolitano, Resto Urbano y Rural Nacional, y la composición por rama de todos los ocupados. | [Contrato ENEIC](../ENEIC_CONTRATO_M05.md) |
| Territorio | ENCOVI 2023, Encuesta Nacional de Condiciones de Vida. Compara ocupación en el sector informal, pobreza y estructura productiva entre departamentos. Presenta perfiles descriptivos de remesas, negocios y consumo, e incorpora el producto interno bruto (PIB) por habitante del Banco de Guatemala (Banguat). | [Matriz](../M03_CONTRATO_MATRIZ.md) · [hogares](../hallazgos_hogares.md) |
| Producción | Valor agregado bruto (VAB) del sector informal de Guatemala, por año y actividad económica. En 2023 representa el 22.62 % del VAB total nacional a precios corrientes. La serie cubre 2013–2019 y 2021–2024. | [Contrato VAB](../VAB_CONTRATO_M05.md) |
| Radar de inteligencia | 44 fichas con evidencia, explicación y preguntas, con filtros por departamento y regla. Los 21 escenarios documentan la sensibilidad del corte a los umbrales. | [Reglas](../reglas_radar.md) · [evaluación](../evaluation/radar_evaluation.md) |
| Metodología y calidad | Fuentes, universos, ponderadores y diagnóstico de precisión de 66 estimaciones departamentales ENCOVI. Cinco valores de pobreza extrema y sus intervalos quedan suprimidos. | [M-01](../M01_IMPLEMENTACION.md) · [M-05](../M05_IMPLEMENTACION.md) |

## Caso de demostración

En **Empleo e ingresos**, pulsar **Ver contraste Chimaltenango–Alta Verapaz**. Se abre la ficha `R1:2023:04-16` con la evidencia y la pregunta de investigación. El identificador indica la regla R1, el año 2023 y los códigos 04 y 16 de los departamentos. Pulsar **Abrir comparación en Territorio** para ver ambos departamentos preseleccionados. Si la demo se interrumpe, el guion enlaza las cuatro capturas incluidas en el ZIP. [Guion y respaldo](../guion_demo.md)

| ENCOVI 2023 | Chimaltenango | Alta Verapaz | Brecha absoluta |
| --- | ---: | ---: | ---: |
| Ocupados de 15 años o más en el sector informal | 80.08 % | 81.06 % | 0.98 pp |
| Pobreza total de personas | 47.75 % | 90.30 % | 42.55 pp |

El radar identifica tasas cercanas de ocupación en el sector informal junto con una brecha de bienestar. El par también cumple por el contraste de PIB por habitante, con una razón de 1.5006. Aparece en los siete escenarios R1 evaluados, medida que el tablero llama robustez. Las cuatro tasas se publican con reserva e intervalos aproximados. `pp` significa puntos porcentuales. La pregunta para el INE es cuánto de la brecha de pobreza persiste al comparar por separado áreas urbanas y rurales con suficiente soporte muestral. [Caso y ponderadores](../caso_demostracion.md) · [Prueba que recalcula el caso desde los microdatos](../../tests/test_indicadores.py)

## Qué se trabajó

| Hito del plan | Resultado del corte | Evidencia principal |
| --- | --- | --- |
| I-01 a I-03 | Inventario de fuentes, claves y conciliación de ENCOVI, definiciones y controles publicados. | [Fuentes](../fuentes.csv) · [exploración](../exploracion_encovi_resumen.md) · [metodología](../metodologia.md) |
| I-04 e I-05 | PIB por departamento con conciliación nacional y extrarregional. Auditoría del Directorio Nacional Estadístico de Empresas (DINESE) 2023–2024 para uso descriptivo. | [PIB departamental](../metadata_pib.md) · [dictamen DINESE](../viabilidad_dinese.md) |
| M-01 y M-02 | 66 estimaciones departamentales y cinco referencias nacionales o por área. 207 celdas de hogares, con 14 restringidas. | [Indicadores](../M01_IMPLEMENTACION.md) · [perfiles](../hallazgos_hogares.md) |
| M-03 y M-04 | Matriz de 22 departamentos × 67 columnas. Radar con 26 fichas R1, cero R2a, una R2b, siete R3 y diez R4. | [Matriz](../M03_CONTRATO_MATRIZ.md) · [evaluación del radar](../evaluation/radar_evaluation.md) |
| M-05 | Cinco vistas integradas, 21 celdas ENEIC, tablas de VAB informal, mapa con supresión visible, caso destacado y exportaciones. | [Implementación](../M05_IMPLEMENTACION.md) · [cotejo y navegador](../evaluation/m05_final/INFORME.md) |
| M-06 y F-01 a F-05 | Cierre del caso, suite de 231 pruebas, PDF, guion, respaldo visual y ZIP de 58 archivos. El checklist indica qué queda por ensayar y confirmar antes del envío. | [Aceptación](../revision_final.md) · [validación](../evidencia/entrega/VALIDACION.md) · [checklist](../checklist_entrega.md) |

El alcance técnico y los hitos de entrega provienen del [plan del Datatón](../../INE_FARO_Plan_Trabajo_Dataton_24_26_Nov_2026.md) y de la [especificación v1.1](../superpowers/specs/2026-11-25-M04-v1.1.pdf).

## Qué queda por verificar o desarrollar

- **Recepción del jurado.** El registro de 100/100 corresponde a la aceptación técnica interna del prototipo v1.1. El checklist todavía deja abiertos el ensayo en el equipo de presentación, Windows nativo si se usará, el acceso con la referencia que se compartirá y la confirmación de recepción del INE. El plan fija el 26 de noviembre de 2026 a las 09:00, hora de Guatemala, para la entrega. [Validación](../evidencia/entrega/VALIDACION.md) · [checklist](../checklist_entrega.md)
- **Alcance estadístico.** La ocupación se clasifica por el sector de la unidad económica. Medir informalidad del puesto requiere variables adicionales. ENEIC y ENCOVI tienen períodos y universos propios. El VAB y el PIB miden producción, y la pobreza ENCOVI usa el consumo. Los contrastes orientan investigación descriptiva. [Metodología](../metodologia.md) · [contratos](arquitectura.md)
- **Desarrollo posterior.** Quedan pendientes las tasas municipales, los cruces con la Superintendencia de Administración Tributaria y el Ministerio de Economía, y el perfil de pobreza según la condición laboral del hogar. Los cortes de ENEIC por sexo, edad, tamaño de unidad o condición están en revisión estadística. La propuesta v1.2 explora priorizar investigaciones con cruces departamento, rama y subrama. La clasificación estadística oficial sigue su metodología institucional. El dictamen DINESE limita ese insumo a contexto de registros empresariales. [Cruce de hogares](../hallazgos_hogares.md#cruce-de-pobreza-de-la-especificación-v11) · [Diagnósticos ENEIC](../ENEIC_CONTRATO_M05.md#diagnósticos-y-precisión) · [DINESE](../viabilidad_dinese.md)
