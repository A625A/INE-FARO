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

**Ejecución con los SAV originales.** El script y el notebook ejecutado generaron CSV idénticos. Se comprobaron 66 claves únicas, tres por departamento, y cinco resultados nacionales o por área. Para repetir la ejecución desde la raíz con las dependencias de la rama instaladas:

```bash
python -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_indicadores.ipynb
```

| Indicador | Registros | Denominador ponderado (personas) | Porcentaje |
|---|---:|---:|---:|
| Informalidad nacional | 17,523 | 6,623,170 | 70.304975 |
| Informalidad urbana | 9,764 | 3,883,725 | 61.332870 |
| Informalidad rural | 7,759 | 2,739,445 | 83.024773 |
| Pobreza total | 10,930 hogares | 17,237,068 | 56.041264 |
| Pobreza extrema | 10,930 hogares | 17,237,068 | 16.236599 |

Las 44 tasas departamentales de pobreza total y extrema coinciden al primer decimal con las secciones 2.5 y 2.9 de *ENCOVI 2023, Pobreza y desigualdad*. Las diferencias máximas son 0.049282 y 0.049227 puntos porcentuales, respectivamente.

Se verificaron los CV y los IC95 de las 71 estimaciones mediante los totales ponderados por UPM. Los CV de informalidad urbana y rural son 1.57366% y 0.86470%. M-01 conserva las 1,447 UPM y asigna contribución cero a las que quedan fuera del área. Restringir primero la muestra al área reproduce los CV de I-03 (1.51% y 0.81%). Las tasas puntuales coinciden en ambos cálculos.

Cinco estimaciones de pobreza extrema tienen CV superior al 30% y quedan marcadas como `no_publicable`: Guatemala, Sacatepéquez, Escuintla, Quetzaltenango y Retalhuleu.
