**INE FARO / DATATÓN INE 2026**

**PLAN DE INVESTIGACIÓN Y DESARROLLO · 24–26 NOV 2026**

# INE FARO

### Radiografía de la economía informal y radar de contrastes económicos territoriales

**Objetivo del prototipo** Conectar fuentes públicas del INE y del Banco de Guatemala para describir la informalidad laboral, explorar pobreza e ingresos, contrastar actividad productiva y generar hallazgos **explicables, verificables y no causales** sobre los 22 departamentos.

## Cómo trabajar sin asignar roles

- **Elegir una tarjeta de tarea.** Cada sección tiene un código y un entregable propio. Cualquiera puede tomarla independientemente de su experiencia.
- **Trabajar en paralelo.** Las tareas de investigación pueden comenzar de inmediato; las tareas de implementación indican qué archivos necesitan.
- **Entregar un archivo o evidencia.** No basta con decir “ya investigué”: dejar dataset, script, tabla, documento o prueba, con fuente y fecha.
- **Comunicar hallazgos y bloqueos.** Marcar en el tablero: Pendiente / En curso / En revisión / Integrado, sin sobrescribir el trabajo de los demás.
## Fechas que no se pueden mover

Martes 24 Investigación y primeros archivos procesados; decidir fuentes utilizables.

Miércoles 25 Análisis reproducible, radar, interfaz y pruebas. Congelar alcance al mediodía.

Jueves 26, 09:00 Entrega del prototipo y repositorio según instrucciones del INE.

Viernes 27 Presentación: 7 minutos + 3 minutos de preguntas.

**Versión mínima que SÍ debemos entregar** Una aplicación local que muestre indicadores oficiales por departamento, contraste al menos una medida de informalidad con PIB departamental y produzca **2–3 hallazgos reales** con fuente, año, advertencia y explicación. DINESE es ampliación si supera sus pruebas de comparabilidad.

Plan distribuible | actualizado el 24 de noviembre de 2026

## Fuentes comprobadas y orden de prioridad

No hace falta conseguir acceso privado a SAT, PNC o entidades bancarias para el prototipo.

|FUENTE Y CONTENIDO|ENLACE|USO|
|---|---|---|
|F1 ENCOVI 2023 Bases de hogares, personas, consumo y negocios. Fuente principal y requisito de datos INE.|Abrir fuente|Principal|
|F2 Guía ENCOVI 2023 35 tablas, identificadores, factores de expansión, precisión y diseño muestral.|Abrir fuente|Leer hoy|
|F3 PIB por departamento Banguat, 2013–2024; PIB total, actividad económica y per cápita en Excel.|Abrir fuente|Principal|
|F4 DINESE 2021–2024|Abrir fuente|Condicion|
|Directorio de empresas registradas; XLSX y estructura sectorial.||al|
|F5 ENEIC Microdatos de empleo y diccionarios; actualización trimestral y dominios nacionales.|Abrir fuente|Opcional|
|F6 ENIGH Ingresos y gastos de hogares; fuentes y diccionarios publicados por INE.|Abrir fuente|Opcional|
|F7 Proyecciones población Población por municipio y año; normalización de registros por habitante.|Abrir fuente|Apoyo|
|F8 Perfiles del INE Perfiles departamentales basados en ENCOVI 2023 para contrastar indicadores.|Abrir fuente|Validación|

#### Reglas estadísticas que deben seguir TODAS las secciones

- **Misma encuesta:** vincular datos usando **NO_HOGAR** y, cuando corresponda, identificadores de persona; verificar cardinalidad para no duplicar hogares o individuos [F2].
- **Ponderaciones:** aplicar el factor de expansión apropiado. La guía describe **FACTOR** y **Factor3**; no asumir que sirven indistintamente para todo indicador [F2].
- **Precisión:** declarar dominios, estratos/conglomerados según diseño, intervalos de confianza o CV cuando sea posible. No publicar subgrupos con pocos casos como si fueran precisos [F2].
- **Cruces entre instituciones:** comparar indicadores **agregados** por departamento/sector/año; no afirmar que los registros de empresas corresponden a los hogares encuestados.
- **Interpretación:** PIB es producción, consumo es gasto/uso, remesas son transferencias y DINESE es registro empresarial. No se suman ni se convierten en causalidad. **Criterio de elección** Si la integración de una fuente tarda demasiado o impide validar cifras, se reemplaza por un indicador oficial publicado y se documenta la decisión. Calidad y entrega pesan más que cantidad de bases.

## ETAPA 1 | Comienzo: investigar y preparar

Prioridad: martes 24. Todas estas tarjetas pueden iniciarse por separado desde hoy.

**I-01 Inventario público y fichas de fuentes** Obligatorio

**Qué investigar / hacer:** Abrir F1–F8. Anotar enlace de descarga, archivo, año, granularidad, variables relevantes, formato, licencia, riesgos y si se pudo descargar. **Entregar:** docs/fuentes.csv + docs/estado_fuentes.md **Se puede iniciar:** ya, sin prerequisitos

#### I-02 Exploración de ENCOVI 2023 Obligatorio

**Qué investigar / hacer:** Descargar Personas, Hogares, Agregado.Consumo y Negocios.1/.2 (si están disponibles). Identificar claves, columnas de informalidad/ocupación, pobreza, ingreso, consumo, negocios; contar filas y faltantes. Consultar guía F2. **Entregar:** docs/diccionario_encovi.csv + notebooks/01_exploracion_encovi.ipynb **Se puede iniciar:** ya, sin prerequisitos

#### I-03 Metodología y definiciones Obligatorio

**Qué investigar / hacer:** Documentar diferencia entre economía informal, sector informal y empleo informal; reglas del INE, ponderación, dominios departamentales de ENCOVI, UPM, precisión, no respuesta y períodos. Extraer los indicadores oficiales a reproducir. **Entregar:** docs/metodologia.md + docs/indicadores_objetivo.csv **Se puede iniciar:** ya, sin prerequisitos

**I-04 PIB departamental y actividades económicas** Obligatorio

**Qué investigar / hacer:** Descargar XLSX F3; identificar 22 departamentos, unidad monetaria, PIB corriente/constante, clasificación sectorial, cobertura 2013–2024 y posibilidad de seleccionar 2023. Normalizar nombres y años. **Entregar:** data/processed/pib_departamental.csv + docs/metadata_pib.md **Se puede iniciar:** ya, sin prerequisitos

**I-05 Auditoría de DINESE (no forzar integración)** Condicional

**Qué investigar / hacer:** Descargar 2023–2024 de F4; revisar si hay desglose por departamento y sector, si distingue “activa” de “con ventas” y si se puede comparar la cobertura. Documentar quiebres metodológicos. **Entregar:** docs/viabilidad_dinese.md + data/processed/dinese_resumen.csv (si procede) **Se puede iniciar:** ya, sin prerequisitos

**I-06 Búsqueda de variables económicas adicionales** Opcional

**Qué investigar / hacer:** Examinar remesas/otros ingresos y negocios en ENCOVI; ENIGH como complemento. Identificar variables exactas, su unidad (persona/hogar/negocio), horizonte de referencia y disponibilidad. NO inventar campos. **Entregar:** docs/hipotesis_y_variables.md + muestras de tablas **Se puede iniciar:** ya, sin prerequisitos

**Punto de control-martes 24, al cierre de la jornada** Tener comprobadas las fuentes, un diccionario mínimo, 22 departamentos armonizados y una pregunta de investigación validable. Si DINESE o ENIGH no están listos, **no deben bloquear la etapa 2**.

## ETAPA 2 | Mitad: análisis y prototipo

Entre martes 24 y miércoles 25. Las tarjetas pueden ejecutarse simultáneamente al estar disponibles sus insumos.

**M-01 Calcular indicadores de informalidad y pobreza** Obligatorio

**Qué investigar / hacer:** Con la exploración ENCOVI y F2: estimar tasas por departamento y desgloses defendibles. Aplicar ponderaciones; registrar n no ponderado y precisión cuando sea viable. Comparar con perfiles oficiales F8. **Entregar:** data/processed/indicadores_encovi_2023.csv + notebooks/02_indicadores.ipynb **Se puede iniciar:** con I-02 + I-03 listos

#### M-02 Examinar hogares y negocios Obligatorio

**Qué investigar / hacer:** Investigar ingresos no laborales, negocios familiares y consumo dentro de ENCOVI. Construir 2–3 tablas descriptivas sin joins muchos-a-muchos; no afirmar que remesas explican PIB o consumo sin evidencia. **Entregar:** data/processed/perfiles_hogares.csv + docs/hallazgos_hogares.md **Se puede iniciar:** con I-02 + variables I-06; independiente de DINESE

#### M-03 Matriz departamental integrada Obligatorio

**Qué investigar / hacer:** Combinar ENCOVI departamental 2023 y PIB Banguat 2023; cada indicador con fuente, año, unidad y nombre estándar. Opcional: DINESE solo como capa separada si I-05 lo valida. **Entregar:** data/processed/matriz_departamental.csv + scripts/build_matriz.py **Se puede iniciar:** con M-01 + I-04

#### M-04 Motor de hallazgos explicables Obligatorio

**Qué investigar / hacer:** Crear reglas de contraste: alta informalidad vs PIB per cápita; sector productivo destacado vs perfil laboral; territorios similares con diferencias económicas. Producir 2–3 resultados reales, condiciones y cautelas. **Entregar:** data/processed/hallazgos.csv + scripts/radar.py + docs/reglas_radar.md **Se puede iniciar:** con M-03; empezar diseñando reglas desde I-03

#### M-05 Interfaz Streamlit y visualización Obligatorio

**Qué investigar / hacer:** Crear páginas: (1) mapa/selector de departamento; (2) comparación de indicadores; (3) ficha del hallazgo. Usar CSV de ejemplo con la misma estructura mientras terminan los datos reales. **Entregar:** app.py + app/pages/ + requirements.txt **Se puede iniciar:** puede empezar ya con contrato de columnas acordado

**M-06 Revisión de cifras y narrativa económica** Obligatorio

**Qué investigar / hacer:** Elegir 1 caso de demostración entre los hallazgos reales. Verificar números en fuente, normalización, interpretación y límites. Preparar texto de 100–150 palabras y tres preguntas de investigación. **Entregar:** docs/caso_demostracion.md + tests/test_indicadores.py **Se puede iniciar:** con M-01/M-03; independiente de la interfaz

**Congelar alcance-miércoles 25, 12:00** Debe funcionar el camino ENCOVI + PIB + radar + interfaz. Desde este punto no incorporar más fuentes, modelos o componentes si amenazan la demostración. DINESE pasa a “futura mejora” si no fue validado.

## ETAPA 3 | Final: integrar, probar y entregar

Miércoles 25 por la tarde y jueves 26 antes de las 09:00. Varias tareas de cierre pueden empezar anticipadamente.

**F-01 Integración y contrato de datos** Obligatorio

**Qué investigar / hacer:** Conectar app.py a archivos finales; revisar nombres exactos de columnas, tipos, filtros, rutas relativas y ausencia de dependencias a archivos personales. Crear un único comando de arranque. **Entregar:** app.py funcional + scripts/build_matriz.py repetible **Se puede iniciar:** con M-03 y M-05

**F-02 Pruebas de datos y flujo de usuario** Obligatorio

**Qué investigar / hacer:** Revisar 22 departamentos, 0 duplicados en la matriz departamental, no nulos críticos, suma/conteo coherente, fuentes/años visibles, comportamiento sin internet y selección de 3 departamentos. **Entregar:** tests/ + docs/revision_final.md **Se puede iniciar:** con primeras tablas; repetir tras F-01

#### F-03 README y entrega reproducible Obligatorio

**Qué investigar / hacer:** Documentar instalación, dependencias, orden de descarga, comandos para generar datos y ejecutar app, fuentes, limitaciones, licencia y alcance futuro. Mantener historial Git; dar acceso al jurado según instrucción. **Entregar:** README.md + docs/fuentes.csv + .gitignore + repositorio verificado **Se puede iniciar:** puede comenzar hoy; finalizar tras F-01

#### F-04 Presentación y demostración Obligatorio

**Qué investigar / hacer:** Preparar una exposición de 7 minutos y respuestas de 3 minutos: problema, datos, metodología, hallazgo, utilidad al INE y límites. Practicar desde una copia limpia del repositorio. **Entregar:** presentacion.pdf o .pptx + docs/guion_demo.md **Se puede iniciar:** puede empezar hoy; actualizar con M-06

**F-05 Checklist de entrega y respaldo** Obligatorio

**Qué investigar / hacer:** Verificar medio de entrega por correo del INE, formato y acceso de jurado, repositorio visible, firmas de participación si se solicitan y video/capturas como respaldo del prototipo. **Entregar:** docs/checklist_entrega.md + paquete final **Se puede iniciar:** puede empezar hoy; cerrar el jueves 26 **antes** de las 09:00

#### Criterios de aceptación del prototipo

[] Se ejecuta desde cero siguiendo el README en un entorno limpio. [] Al menos una base pública del INE alimenta resultados reales y visibles. [] Se puede seleccionar departamento y consultar indicadores con año y fuente. [] Existen dos o tres hallazgos calculados, comprobables y no inventados. [] Hay advertencias cuando una comparación mezcla fuentes o años. [] El repositorio tiene historial Git, dependencias y acceso de evaluación. [] El demo puede mostrarse localmente aunque falle la red.

## Cómo conectar trabajos paralelos sin conflictos

Reglas para que cualquier persona tome una sección cuando tenga tiempo.

#### Contrato de datos mínimo

**Archivo / unidad Columnas recomendadas**

indicadores_encovi_2023.csv / depto_id, departamento, anio, indicador, valor, departamento unidad, fuente, n

pib_departamental.csv / depto_id, departamento, anio, sector, pib_valor, departamento-sector-año unidad, tipo_precio

matriz_departamental.csv / depto_id, departamento + columnas con sufijo departamento _2023

hallazgos.csv / regla y hallazgo_id, depto_id, regla, evidencia, advertencia, departamento fuentes

**Observación**

Tasa ponderada; agregar CV/IC si es confiable.

No mezclar nominal con real.

Una fila por departamento para mapa y comparación.

Sin afirmaciones causales ni IA alucinada.

#### Estructura sugerida del repositorio

**Carpetas y archivos** app.py · requirements.txt · README.md · .gitignore **data/raw/** (descargas locales, ignoradas por Git cuando aplique) **data/processed/** (tablas agregadas y anonimizadas) **docs/** (fuentes, metodología, evidencia, guion) **notebooks/** (exploración y análisis reproducible) **scripts/** (ETL, integración y motor de hallazgos) **tests/** (controles y verificación)

#### Protocolo corto para subir cada tarea

**1.** Crear una rama con el código: tarea/I-02-encovi, tarea/M-04-radar, etc.
**2.** Adjuntar código o documento, enlace a fuente, fecha de consulta y cómo reproducirlo.
**3.** Indicar si está validado, pendiente o bloqueado; un PR pequeño por entrega.
**4.** No cambiar rutas ni nombres de columnas acordadas sin avisar antes de fusionar. **Punto científico no negociable** Los indicadores de ENCOVI se estiman respetando pesos y diseño muestral; el mapa departamental no autoriza fabricar informalidad municipal. ENEIC permite dominios nacional/urbano metropolitano/resto urbano/rural nacional, no tasas por cada departamento. La variación de DINESE no equivale necesariamente a crecimiento real de la producción.

## Guion de demostración, cortes y riesgos

Usar un caso real que aparezca en los resultados; Jutiapa u otro territorio solo si la evidencia lo justifica.

#### Estructura de presentación - 7 minutos

0:00–0:55 El problema: la informalidad no se entiende desde una sola estadística.

0:55–1:50 Qué fuentes usamos y qué podemos (y no podemos) comparar.

1:50–4:30 Demostración: mapa, selección de departamento, contraste y ficha del hallazgo.

4:30–5:35 Qué explica el algoritmo: reglas, evidencia, precisión y fuentes.

5:35–6:30 Utilidad institucional: dónde investigar, no dónde prometer inversión.

6:30–7:00 Limitaciones, siguiente versión y cierre.

#### Decisiones para reducir riesgo

**Problema Plan de respuesta**

ENCOVI tarda en procesarse Usar tablas y perfiles agregados oficiales para MVP; mantener enlaces y aclarar alcance.

DINESE no es comparable Excluirlo del análisis principal; citarlo como ampliación futura.

No hay remesas suficientemente No plantear explicación; presentar hipótesis pendiente. desglosadas

El clustering produce grupos Usar comparaciones y reglas interpretables en lugar de clusters forzados. inestables con 22 datos

La nube o conexión falla Ejecutar app local con CSV preparados; guardar capturas o video de respaldo.

La fuente y el algoritmo discrepan No publicar hallazgo hasta resolver o documentar la diferencia.

#### Tres preguntas que probablemente hará el jurado

**¿Están cruzando personas con empresas?** No. Los cruces directos ocurren solo entre módulos compatibles de ENCOVI; entre instituciones comparamos agregados con su año y unidad. **¿La plataforma determina por qué existe informalidad?** No demuestra causalidad. Identifica contrastes e hipótesis estadísticamente sustentadas para investigación posterior. **¿Por qué no utilizar un modelo de IA generativa?** El prototipo prioriza un motor explicable con datos y fuentes verificables; futuras versiones pueden añadir consultas en lenguaje natural sin inventar resultados.

**Definición de éxito** El jurado puede abrir el prototipo, elegir un departamento, ver un contraste económico auténtico, examinar sus fuentes y comprender qué se sabe, qué sigue siendo una hipótesis y qué investigación recomienda priorizar.

Fuentes: páginas oficiales F1–F8 (enlaces clicables en la página 2). Lineamientos de entrega y exposición: “Presentación Datatón 2026”, documento compartido por el equipo. Consulta web realizada el 24/11/2026.