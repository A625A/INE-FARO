# Validación de entrega · 25 de noviembre de 2026

**100/100 en aceptación técnica del alcance del Datatón.** El corte parte de `8bc88f8` e incluye el material de M-06. La evaluación usa los [criterios de la revisión final](../../revision_final.md).

| Frente | Puntos | Comprobación |
| --- | ---: | --- |
| Empleo e ingresos | 20/20 | 21 celdas ENEIC y denominadores en la vista laboral. |
| Producción | 15/15 | 22.62 % de VAB informal nacional en 2023 y discontinuidad en 2020. |
| Territorio y hogares | 15/15 | 22 departamentos seleccionables y supresión de cinco estimaciones ENCOVI y 14 de M-02. |
| Radar | 20/20 | 44 fichas, 21 escenarios y exportación coherente. Caso M-06 recalculado desde los SAV. |
| Tablero y demo | 20/20 | ZIP extraído y probado en macOS, en escritorio y móvil emulado. |
| Preparación para el jurado | 10/10 | Presentación, guion, caso, capturas, checklist y paquete reproducible disponibles. |

- **Pruebas:** 231 aprobadas en 51.13 s mediante `python -m pytest -p no:cacheprovider -q` en Python 3.14.3.
- **Navegador:** Chromium 155, red externa bloqueada, sin errores de consola y sin solicitudes externas. [Registro](chromium.txt)
- **Paquete:** 58 archivos regulares, CRC íntegro y dos empaquetados idénticos en Python 3.14.3 con zlib 1.2.12. [Huellas SHA-256](SHA256SUMS)

El [checklist](../../checklist_entrega.md) conserva el ensayo en el equipo de presentación, la prueba en Windows nativo si se usará ese sistema, la aprobación de la referencia, el envío y su confirmación.
