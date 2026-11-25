# INE FARO · Sistema de diseño

La interfaz se lee como un atlas estadístico. La navegación introduce cinco preguntas de investigación y cada página encabeza sus resultados con un período y una fuente. El mapa y las fichas son el centro de Territorio y Radar.

## Recursos institucionales

El ZIP «Kit de diseño Datatón» pasó la verificación CRC. La guía PowerPoint de 10 láminas reproduce páginas del Manual de Imagen Institucional 2025. Contiene variantes del logotipo, fondos y tonalidades permitidos, cintillo de cooperantes, paletas principal y secundaria, familia tipográfica y piezas de redes. El archivo incluye 20 PNG, 12 SVG y tres AI de logotipos, un AI de cintillo y Ubuntu Sans en 50 archivos TTF con README y OFL. También contiene archivos temporales y metadatos del sistema. El inventario carece de geometrías, iconos de interfaz, plantillas de dashboard y ejemplos o normas específicas de gráficos estadísticos.

La paleta principal y Ubuntu Sans coinciden con la especificación v1.1. FARO usa el imagotipo horizontal RGB original sobre blanco para identificar el contexto del Datatón, con «Prototipo del Datatón INE 2026» junto a la identidad. El kit se entregó a los participantes. La guía identifica sus variantes y fondos de uso y carece de una licencia general de redistribución de marcas. El uso del imagotipo queda circunscrito al prototipo. La redistribución de Ubuntu Sans se rige por SIL Open Font License 1.1, incluida en el proyecto.

## Color y tipografía

- Azul oscuro institucional `#004080` para títulos, controles activos y serie primaria.
- Azul radiante institucional `#0080FF` para énfasis gráfico. El texto sobre blanco emplea el azul oscuro.
- Blanco `#FFFFFF`, fondo auxiliar `#F1F5FA`, tinta `#10243B`, texto secundario `#455971` y borde `#D6E0EA`.
- Mayor precisión relativa `#175943`, precisión limitada `#805200`, restricción `#575E62`. Cada estado incluye una etiqueta. Los errores usan el estilo de alerta nativo.
- Ubuntu Sans local, 400–700. H1 de 36–52 px, H2 de 24–28 px, cuerpo de 16 px y notas de 14 px. Las cifras usan numerales tabulares.

## Componentes y comportamiento

- Cabecera blanca con línea azul, wordmark y atribución. Navegación horizontal con contorno de foco, cambio por teclado y ajuste de líneas en pantallas estrechas. Estado de vista y filtros conservado durante el recorrido.
- Retícula de 4 px. Márgenes y separaciones principales de 16, 24 y 32 px. Filas de cifras con línea superior, sin sombras. Separadores agrupan bloques analíticos.
- Barras horizontales desde cero, intervalos cuando corresponden, etiquetas de unidad en ejes y fuente junto al gráfico. Etiquetas extensas completas en tooltips y tablas. El 2020 ausente se distingue con espacio y nota.
- Mapa secuencial azul o categórico para actividad, relleno gris para estimaciones restringidas y borde oscuro para la selección. El selector de departamento ofrece el mismo acceso con teclado. El mapa no requiere teselas externas.
- Las tablas preservan el orden de lectura, dan prioridad a valor y unidad y mantienen los diagnósticos visibles. Los estados vacíos explican qué filtro buscar. La restricción muestra únicamente el diagnóstico. Un contrato inválido identifica el bloque afectado.
- En móvil la cabecera y navegación se ajustan y las columnas se apilan. Los gráficos permiten inspección táctil y los datos tabulares ofrecen desplazamiento interno. El texto y el foco mantienen contraste en fondo blanco y azul auxiliar.
