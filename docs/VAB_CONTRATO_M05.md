# Producción informal nacional para M-05

Los CSV usan UTF-8, coma y LF. El grano es nacional y corresponde a los años 2013–2019 y 2021–2024. El índice del cuadro 12 explica que en 2020 no se desagregó la producción informal porque INE no realizó la ENEI. El consumidor debe representar un salto. Los años 2023 y 2024 son preliminares.

`data/processed/vab_informal_nacional.csv` tiene clave `(anio,tipo_precio)`. `vab_informal` es el total oficial, `vab_total` es B1b S1 y `participacion_informal_pct` usa ambos en precios corrientes. La unidad es millones de quetzales.

`data/processed/vab_informal_grupo.csv` tiene clave `(anio,tipo_precio,grupo_ciiu)`. Incluye nombre de grupo, VAB informal, denominador de rama, composición del VAB informal nacional y participación del sector informal en la rama. Los porcentajes usan importes sin redondeo previo. Los denominadores por rama agrupan todas las actividades NAEG del cuadro 5 con la concordancia Banguat y se contrastan con la fila Nacional del cuadro departamental. El grupo O tiene denominador positivo y VAB informal cero.

Las filas `volumen_encadenado_2013` contienen los valores oficiales de 12.2. Sus campos de denominador y porcentajes están vacíos. Los componentes encadenados no son aditivos. El dato productivo describe valor agregado, mientras la ocupación en el sector informal describe trabajadores. Las cifras no tienen desagregación departamental.

## Fuentes y reproducción

Snapshot consultado el 25 de noviembre de 2026, cuentas con año de referencia 2013. Los XLSX se excluyen de Git mediante `data/raw/`. Guardar los archivos siguientes en `data/raw/banguat_nacional/` con sus nombres originales y el cuadro departamental en `data/raw/banguat/`.

- [Cuadro 12, producción informal](https://banguat.gob.gt/sites/default/files/banguat/cuentasnac/PIB2013/12_Valor_agregado_bruto_del_sector_informal.xlsx), SHA-256 `cc653433a922db3e6f7222eee6cab7394e7ed193390cb640ae2f5072caa290d3`.
- [Cuadro 5, clasificación cruzada](https://banguat.gob.gt/sites/default/files/banguat/cuentasnac/PIB2013/5_Clasificacion_cruzada_de_industrias_y_sectores_institucionales.xlsx), SHA-256 `154fa12f69d11fd6c187cccf237af9f3fcc80b6f61f4aa6dfeaa29a60d151618`. La hoja 5.103 es B1b, S1, 2023.
- [Nomenclaturas Banguat](https://banguat.gob.gt/sites/default/files/banguat/cuentasnac/PIB2013/Nomenclaturas_2013.xlsx), hoja NAEG-CIIU revisión 4, SHA-256 `3c4ccbf16be5d4a04828ed26a5535218aaa70219f13a06ce7d6b0bf559c1c355`. Las divisiones se agrupan según la estructura CIIU revisión 4 y los 17 grupos publicados en cuadro 12.
- [Cuadro departamental por actividad](https://banguat.gob.gt/sites/default/files/banguat/Publica/PIB_Regional/7_Resultados_por_actividad_economica_en_departamentos.xlsx), SHA-256 `7acce7a4f90c92245fe481e3c853e2b48659c8e84c9176c064bad4e09db6951a`. Se usa solamente su fila Nacional corriente para contrastar la asignación de las 105 actividades. Las 187 combinaciones de rama y año presentes en la serie informal concilian dentro de 0.000053 millones de Q.

Con las dependencias de `requirements.txt` y los cuatro XLSX locales, ejecutar:

```sh
python scripts/procesar_vab_informal.py
python scripts/verificar_vab_2023.py --salida docs/evidencia/vab_informal_controles_2023.json
python -m pytest -q tests/test_vab_informal.py tests/test_verificar_vab_2023.py
```

La evidencia de conciliación por grupo está en `docs/evidencia/vab_informal_conciliacion.json`. El cotejo independiente lee directamente las celdas 12.1 O26, O14 y O42 y 5.103 I126. En 2023 obtiene 172538.678503 y 762881.363889 millones de Q, 22.6167116763 % y 38.5535560618 %. Redondeados a dos decimales coinciden con los cuatro controles aprobados. Las pequeñas diferencias en las sumas provienen del redondeo de celdas oficiales.
