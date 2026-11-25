# Handoff a M-06

## Entorno y control de entrega

Partir de `feature/M-05-integracion-final`. Verificar la referencia remota,
leer [el informe](INFORME.md) y probar una copia del
[ZIP portable](../../M05_IMPLEMENTACION.md#zip-de-demostración-para-windows)
con dependencias instaladas. El recorrido mínimo muestra los controles
nacionales de ENEIC, cambia el mapa a pobreza extrema, compara dos
departamentos, comprueba la brecha de 2020 en Producción y abre Santa Rosa
en R2b, Alta Verapaz en R4 y el resultado vacío de R2a.

## Límites para la presentación

- INE FARO se identifica como prototipo del Datatón 2026. El logotipo y la fuente se atribuyen en el sistema de diseño.
- ENEIC IV-2025, ENCOVI 2023 y cuentas Banguat 2023 aportan mediciones con períodos, universos y unidades propios.
- El radar orienta preguntas de investigación. La robustez frente a umbrales describe la estabilidad de la regla.
- Los cinco diagnósticos de pobreza extrema y las 14 restricciones de M-02 conservan la supresión en las descargas.
- El PIB por habitante mide producción. El VAB informal entregado es nacional.
- La comparación de registros DINESE entre años requiere resolver cobertura. Los cruces ENCOVI de pobreza por tipo de hogar y los cortes nuevos ENEIC requieren validación adicional.

## Mantenimiento

`app.py` selecciona la vista. `dashboard_data.py` valida el grano y enmascara
el dato antes de la presentación. `dashboard_radar.py` valida fichas y
`dashboard_radar_ui.py` organiza su exploración. `dashboard_precision.py`
mantiene el diagnóstico. El sistema de diseño explica los recursos locales.
Para incorporar un corte distinto, actualizar su contrato junto con las
pruebas de consumo, cotejar la presentación y repetir el recorrido Chromium.
Usar la [evaluación independiente](validar_consumo.py) y la
[evidencia existente](../../evidencia/M-05/final/) como referencia del corte.
