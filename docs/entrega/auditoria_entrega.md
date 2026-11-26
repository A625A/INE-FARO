# Auditoría de cierre · INE FARO v1.1

Fecha de revisión: 25 de noviembre de 2026 (Guatemala).

**Dictamen: paquete técnico documentado; autorización de entrega condicionada a los controles pendientes.** La revisión distingue evidencia histórica del corte, comprobaciones nuevas de GitHub y verificaciones que necesitan intervención del equipo. No es una calificación oficial del jurado.

- Corte técnico validado: [63af665](https://github.com/A625A/INE-FARO/commit/63af665b30b567c662b8098946595e2df4ab0c9e).
- Base de la revisión documental: [7af13ec](https://github.com/A625A/INE-FARO/commit/7af13ec814d7aa135d58e9f12f1ffd4c050a1098); PR #8 cerrado e integrado.
- Alcance de los cambios: README y esta auditoría; no se modifican aplicación, datos, dependencias, ZIP, PDF ni configuración de despliegue.

## 1. Evidencia técnica

| Control | Estado | Evidencia |
|---|---|---|
| Repositorio público y rama main | Verificado en GitHub | [Repositorio](https://github.com/A625A/INE-FARO) y [PR #8](https://github.com/A625A/INE-FARO/pull/8) |
| Instrucciones de ejecución, reproducción y respaldo | Revisadas contra documentación y archivos del corte | [README](../../README.md) · [Guía](reproduccion.md) |
| Capturas de las cinco vistas, caso central, calidad y móvil | Rutas y archivos verificados en el árbol Git | [Capturas versionadas](../evidencia/M-05/final/) |
| Matriz y radar | Evidencia técnica existente: 22 × 67, 44 fichas, 21 escenarios | [Arquitectura](arquitectura.md) · [Evaluación](../evaluation/radar_evaluation.md) |
| Precisión de ENCOVI | Evidencia existente: 66 estimaciones, cinco restringidas; 207 celdas de hogares, 14 restringidas | [Revisión de aceptación](../revision_final.md) |
| Pruebas automatizadas | 231 aprobadas en el corte; no reejecutadas durante esta revisión documental | [Validación](../evidencia/entrega/VALIDACION.md) |
| Navegación y descargas | Ensayo anterior de escritorio y móvil emulado, cero errores de consola y solicitudes externas; no equivale a prueba del hosting | [Registro Chromium](../evidencia/entrega/chromium.txt) |
| ZIP de demostración | Archivo presente; validación previa de 58 entradas regulares e igualdad binaria | [ZIP](../evidencia/entrega/INE-FARO-Dataton.zip) · [Huellas](../evidencia/entrega/SHA256SUMS) |
| Presentación y guion | Archivos presentes | [PDF](../../presentacion.pdf) · [Guion](../guion_demo.md) |
| Licencia y condiciones de redistribución | Pendiente de decisión y comprobación | [Inventario](../fuentes.csv) |

Los controles de código, datos y navegador proceden de las pruebas del corte documentado. No se volvió a ejecutar el pipeline completo ni se descargaron y revalidaron los binarios durante esta auditoría.

## 2. Controles de recepción y despliegue pendientes

| Prioridad | Acción | Criterio para cerrar |
|---|---|---|
| P0 | Probar la [demo principal Streamlit](https://ine-faro.streamlit.app/) en incógnito o desde otra conexión | Arranca sin cuenta del equipo; cinco vistas, contraste R1, mapa y una descarga funcionan |
| P0 | Probar el [respaldo Render](https://ine-faro.onrender.com/) | Arranca y muestra el mismo caso del corte; si no funciona, utilizar el ZIP |
| P0 | Finalizar el video oficial | Se visualiza y escucha completo; evidencia las cinco vistas reales, caso R1, sensibilidad y calidad; cumple el formato/duración oficial; enlace accesible al jurado |
| P0 | Verificar los lineamientos y la recepción | Confirmar medio, formato, firmas, fecha y acceso; comprobar enlaces en sesión sin credenciales y registrar recepción antes del hito |
| P0 | Revisar derechos de uso y redistribución | Confirmar licencia del código con los autores y las condiciones de los insumos y recursos publicados; no aplicar una licencia general a materiales de terceros |
| P1 | Ensayar el ZIP en el equipo de presentación | Instalar dependencias antes de desconectar; abrir las cinco vistas, caso de dos clics, mapa y exportación |
| P1 | Verificar la copia que se adjuntará | Comparar SHA-256 de ZIP y PDF con el registro versionado y conservar respaldo local |
| P1 | Windows nativo, si corresponde | Ejecutar comandos PowerShell y repetir recorrido en el equipo final |

Los intentos de abrir ambos servicios desde el entorno de esta revisión no permitieron acceder a las páginas. No se ha determinado que estén caídos ni se acredita su disponibilidad. La versión local validada sigue siendo el respaldo verificable.

El inventario de fuentes identifica condiciones de reutilización no verificadas para ENCOVI y derechos reservados de Banguat; el repositorio público incluye archivos originales SAV, XLSX y PDF. Revisar autorización de redistribución y ausencia de datos sensibles antes de compartir la referencia final. El repositorio no declara una licencia general del código; usar tecnologías abiertas no equivale por sí solo a licenciar el código propio. No se ha modificado ninguna licencia ni material de origen.

## 3. Recorrido de aceptación rápido

1. Abrir Streamlit en una ventana privada. Si no funciona, probar Render y posteriormente el ZIP local.
2. Confirmar que la vista inicial sea Empleo e ingresos.
3. Abrir **Ver contraste Chimaltenango–Alta Verapaz**. Deben aparecer 0.98 pp de brecha de ocupación en el sector informal y 42.55 pp de brecha de pobreza total, ENCOVI 2023.
4. Revisar la sensibilidad de siete de siete escenarios R1 y abrir la comparación en Territorio.
5. Seleccionar Pobreza extrema en el mapa. Confirmar cinco departamentos restringidos en gris; descargar el indicador y comprobar que valores e intervalos de esas cinco filas estén vacíos.
6. Abrir Producción, Radar y Metodología y calidad; confirmar que no haya errores ni vistas vacías inesperadas.
7. Descargar y abrir el ZIP y el PDF; verificar huellas. Abrir el video final desde una sesión sin permisos del equipo.
8. Registrar la referencia exacta, el canal de envío y el comprobante de recepción.

## 4. Dictamen para el cierre

La evidencia técnica del corte respalda la entrega del prototipo. No se recomienda agregar funcionalidades antes de entregar. La revisión documental no acredita por sí sola el cumplimiento de todos los requisitos de recepción: cerrar los P0 aplicables y completar el [checklist operativo](../checklist_entrega.md).

La evaluación interna de aceptación técnica y la evaluación simulada de presentación no son calificaciones del jurado. No se atribuye un aumento de puntuación sin una evaluación independiente del video y del producto final.

Hito documentado: jueves 26 de noviembre de 2026, 09:00, hora de Guatemala. Confirmar los detalles de entrega con la comunicación del organizador.
