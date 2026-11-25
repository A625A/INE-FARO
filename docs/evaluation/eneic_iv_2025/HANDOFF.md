# Entrega ENEIC IV-2025

Componente listo para revisión de M-05. Entrada pública y reglas de consumo en `docs/ENEIC_CONTRATO_M05.md`. Ejecutar `python scripts/procesar_eneic.py` sin red con los snapshots raw locales, o utilizar `--download` si faltan. Manifiesto y controles oficiales en `data/reference/*eneic_iv_2025.json`.

## Verificación

- CLI real completada con 49,338 registros, 21,233 ocupados y 7,944,838 personas expandidas. Tasa 65.62870130265715%, media Q2,841.584067017995, mediana interna Q2,400 y 20,239 ingresos válidos.
- Los tres dominios concilian al decimal 44.3%, 65.0% y 77.3%. Los ingresos medios y las diez ramas concilian a la precisión oficial.
- La réplica independiente XML/SQLite, preservada en esta carpeta, concilia n, volumen, tasas, ingresos y cobertura nacional y por dominio. Se reutilizó la validación inicial aceptada.
- TDD inicial con productor ausente y posteriormente con publicación y control independiente ausentes. Se verificaron ponderación, duplicados, cobertura, categorías inválidas, ceros y faltantes, medianas, particiones, residual CIIU, orden de entrada y protección de salida ante hash inválido.
- `python -m pytest -q` completó 60 pruebas en 49.66 segundos. Log en `pruebas.txt`. `python -m compileall -q scripts tests` y `git diff --check` correctos. Entorno de ejecución disponible en `/private/tmp/ine-faro-m05-venv`.
- CSV público de 21 filas y diagnóstico interno de 50 filas. El SHA público fue cotejado con `docs/evidencia/eneic_iv_2025/validacion.json`.

## Decisiones y límites

TRIMESTRE=5 es el código observado del archivo IV-2025. Se documentó la discrepancia entre gráfica 4 y tabla 2. La tabla 2 controla las ramas. La lista pública incorpora dos volúmenes nacionales derivados, identificados como conciliación indirecta. Las medianas y los cortes nuevos permanecen internos. UPM y estratos no están disponibles y no se calculó precisión nueva. La integración visual en M-05 queda a cargo de su consumidor.

Se trabajó directamente con executing-plans, TDD, validate-data y verification-before-completion, sobre el worktree previamente preparado con using-git-worktrees y el plan existente de writing-plans. Se preservó la especificación aprobada. La revisión final de código fue propia, sin subagentes conforme a la instrucción actual. La evaluación estadística conserva la independencia de la réplica aceptada.

Commits de implementación 173fa9a y a68c0a1, seguidos por el commit de agregados y evidencia. La rama de entrega es feature/eneic-iv-2025, basada en 5634fbf. Para continuar la integración usar el contrato M-05 y las skills validate-data y verification-before-completion. Los cambios de diseño o publicación requieren acreditar precisión antes de ampliar la lista de celdas.
