# M-01 — Cálculo de indicadores ENCOVI 2023

Genera `data/processed/indicadores_encovi_2023.csv` (66 filas: 22 departamentos × tres indicadores) y `data/processed/indicadores_encovi_nacional_2023.csv` (cinco indicadores nacionales y por área). No guarda registros individuales.

```bash
python scripts/calcular_indicadores_encovi.py
python -m pytest tests/test_indicadores_m01.py -q
```

También puede ejecutarse `notebooks/02_indicadores.ipynb` desde la raíz. Requiere los SAV originales y `requirements.txt` ya integrados en la Fase 1.

**Universos:** informalidad = ocupados de 15 años o más, `PPA03>=15`, `OCUPADOS=1`, `FORMAL_INFORMAL=1`, peso `FACTOR`. Pobreza = hogares con consumo, `pobreza` en 1–3, peso `Factor3`; pobreza total 1/2, extrema 1. El script aborta si no se reproducen los valores publicados de 70.3%, 56.0%, 16.2%, 61.3% urbano y 83.0% rural o si falla el contraste departamental de pobreza.

**Limitación:** CV/IC usan aproximación con `DEPTO` como estrato y `UPM` como conglomerado, sin estratos originales ni corrección de población finita. Se indican como `aproximada_depto_upm_sin_estratos_originales`, no son valores oficiales. Si `n<30` o `CV>30%`, `estado=no_publicable`. No se infiere causalidad ni se interpretan resultados municipales.

**Contrato:** `depto_id` texto de 2 dígitos, `anio=2023`, `indicador` en `ocupacion_sector_informal`, `pobreza_total`, `pobreza_extrema`, `valor` expresado en porcentaje, `n`, `upm_n`, `ponderador`, `cv`, `ic95_inf`, `ic95_sup`, `precision` y `estado`.

**Estado de entrega:** código y pruebas sintéticas listos; ejecución completa con los SAV originales pendiente en el entorno del equipo.