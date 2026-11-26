# Revisión de aceptación · INE FARO

El corte evaluado es el prototipo del Datatón con alcance v1.1. Las unidades de medida son la ocupación en el sector informal, el bienestar y la producción en sus respectivos universos. El recorrido usa los agregados entregados y desarrolla preguntas descriptivas.

| Frente | Criterio para puntaje completo en este corte | Referencia |
| --- | --- | --- |
| Empleo e ingresos | ENEIC concilia las 21 celdas públicas. La app muestra denominadores, período y dominio. Las ramas describen a todos los ocupados. | [Contrato ENEIC](ENEIC_CONTRATO_M05.md) |
| Producción | VAB informal nacional y por rama reproducible. 22.62 % nacional en 2023. La serie conserva el vacío en 2020. | [Contrato VAB](VAB_CONTRATO_M05.md) |
| Territorio y hogares | 22 departamentos con claves únicas. Los cinco diagnósticos ENCOVI y las 14 restricciones M-02 se preservan. | [M-03](M03_CONTRATO_MATRIZ.md) · [M-02](hallazgos_hogares.md) |
| Radar | 44 fichas, 21 escenarios, IDs deterministas, casos verificables y exportaciones coherentes. | [Evaluación del radar](evaluation/radar_evaluation.md) |
| Tablero y demo | Navegación y descargas desde el ZIP extraído, con escritorio y móvil emulado, recursos locales y red externa bloqueada. | [Informe M-05](evaluation/m05_final/INFORME.md) |
| Preparación del jurado | Caso, presentación, guion, ZIP, huella, capturas y checklist listos para el ensayo y la entrega. | [Caso](caso_demostracion.md) · [Guion](guion_demo.md) · [Checklist](checklist_entrega.md) |

## Pruebas del corte

```sh
python -m pytest -q
python docs/evaluation/m05_final/validar_consumo.py
python -m scripts.empacar_m05 --output faro-demo-1.zip
python -m scripts.empacar_m05 --output faro-demo-2.zip
cmp faro-demo-1.zip faro-demo-2.zip
```

Extraer el ZIP en una carpeta limpia y abrirlo con Python 3.14. Para repetir el recorrido de navegador usar `tests/browser/m05.cjs` desde el repositorio, con `BASE_URL` apuntando a la aplicación extraída. El recorrido verifica los 22 departamentos, el caso destacado y las exportaciones. La equivalencia byte por byte de dos ZIP se verifica en el mismo entorno de compresión.

La [verificación del equipo final y la entrega](checklist_entrega.md) se completa con el equipo organizador.
