# Estado de Fuentes de Datos — INE FARO

**Fecha de actualización:** 25 de noviembre de 2026
**Rama:** `fix/i01-fuentes`, creada desde `main` en `b3f9f4a`
**Estado de GitHub verificado:** `main` contiene I-02/I-03 validados y documentados, e I-04/I-05 validados localmente. Las fases M siguen pendientes.

---

## 1. Inventario y estados

| ID | Fuente | Estado (`descargado`) | Archivo local | Alcance verificado |
|---|---|---|---|---|
| F1 | ENCOVI 2023 | Sí | `data/raw/encovi_2023/` | Microdatos SAV de personas, hogares, consumo agregado y negocios (1 y 2); diccionarios XLSX y PDFs de apoyo. Sin CSV. |
| F2 | Guía ENCOVI 2023 | Sí | `data/raw/encovi_2023/Guia-para-el-uso-de-bases-de-datos_v_final.pdf` | PDF metodológico; enlace directo oficial verificado el 25/11/2026. |
| F3 | PIB Banguat | Sí | `data/raw/banguat/` | Tres XLSX, encabezados 2013–2024; procesamiento local del año 2023. |
| F4 | DINESE | Sí | `data/raw/dinese/` | Catálogo con cobertura mayor; solo snapshots 2023 y 2024 procesados. |
| F5 | ENEIC / ENEI | Descartado | Sin archivo local | Sin representatividad departamental; no descargada. |
| F6 | ENIGH | Descartado | Sin archivo local | Complejidad adicional fuera del MVP; no descargada. |
| F7 | Proyecciones Población | Pendiente | Sin archivo local | Ruta prevista `data/raw/proyecciones_poblacion.csv` ausente. |
| F8 | Perfiles Departamentales INE | Pendiente | Sin archivo local | PDF departamental no descargado. |

Los ocho identificadores F1–F8 se conservan. Los estados son idénticos a la columna `descargado` de `docs/fuentes.csv`.

---

## 2. Verificación por fuente

### F1 — ENCOVI 2023

- Archivos confirmados: `encovi_2023_personas.sav`, `encovi_2023_hogares.sav`, `encovi_2023_agregado_consumo.sav`, `encovi_2023_c14sa_negocios_1.sav` y `encovi_2023_c14sa_negocios_2.sav`; cinco diccionarios XLSX y PDFs metodológicos.
- Formatos reales: SAV, XLSX y PDF. No se describen como CSV.
- Granularidades: persona, hogar, agregado de consumo y negocio.
- La ruta `https://www.ine.gob.gt/encovi-2023` respondió CAPTCHA al verificador; se conserva como referencia institucional, sin sustituto inventado.

### F2 — Guía ENCOVI 2023

- Ruta local corregida y existente: `data/raw/encovi_2023/Guia-para-el-uso-de-bases-de-datos_v_final.pdf`.
- Enlace directo oficial verificado: `https://www.ine.gob.gt/wp-content/uploads/2024/11/Guia-para-el-uso-de-bases-de-datos_v_final.pdf`.
- La página antigua `https://www.ine.gob.gt/encovi-2023-guia` respondió CAPTCHA; no se usa como enlace de descarga.

### F3 — PIB Banguat

- Coinciden `docs/fuentes.csv`, `docs/metadata_pib.md` y `data/reference/fuentes_I04_I05.json`: tres XLSX en `data/raw/banguat/`, encabezados 2013–2024 y SHA-256 fijados.
- Salidas procesadas: 836 filas departamentales de 2023, 22 de PIB por habitante y 38 de conciliación.
- Unidades: millones de quetzales para niveles y quetzales por habitante para la medida per cápita.
- Granularidad: departamento, sector y tipo de precio. Volumen encadenado 2013 no aditivo; PIB no equivale a ingreso ni consumo.

### F4 — DINESE

- El catálogo institucional cubre más años; los únicos archivos procesados son `dinese-2023.xlsx` y `dinese-2024.xlsx`, con hashes en el manifiesto I-04/I-05.
- Granularidad del procesamiento: departamento, sección CIIU y movimiento de ventas.
- Uso habilitado: descripción transversal separada por año. No se interpretan variaciones como crecimiento empresarial, altas/bajas netas ni formalización laboral.
- `CLA_RANGO_VENTAS` es una categoría, no un importe sumable.

### F5–F8

- F5, F6, F7 y F8 no tienen archivos locales; por eso no aparecen como descargadas.
- Los enlaces institucionales de INE consultados respondieron CAPTCHA al verificador. Se conservan los enlaces oficiales ya documentados y no se inventan sustitutos.
- F7 mantiene estado `Pendiente` aunque exista una ruta planeada en el inventario anterior; la ruta no existe en el repositorio.

---

## 3. Licencias y condiciones

| Fuente | Condición documentada |
|---|---|
| F1, F2, F5, F6, F7, F8 | Condiciones de uso en el sitio del INE; licencia de reutilización no verificada en el repositorio. No se trata “Pública” como licencia abierta. |
| F3 | Derechos reservados Banguat; ver `docs/metadata_pib.md`. No se presume licencia abierta genérica. |
| F4 | El catálogo oficial declara Creative Commons Attribution; ver `docs/viabilidad_dinese.md`. |

---

## 4. Consistencia con el estado comprobado de GitHub

- En `main` (`b3f9f4a`) están I-02/I-03 validados y documentados, e I-04/I-05 validados localmente con pruebas y evidencia.
- No se afirma que I-04/I-05 estén todavía integradas en matriz, radar o aplicación: esas tareas pertenecen a M-01..M-06 y siguen pendientes.
- Se eliminó la afirmación de que las cifras de informalidad seguían sin validarse: el 70.3% nacional fue reproducido y documentado en I-02/I-03.
- Este cierre de I-01 no modifica microdatos, datos procesados ni entregas I-02..I-05.

---

## 5. Validación ejecutada

- `docs/fuentes.csv` se leyó con `csv` y delimitador `;`: 9 filas, 12 columnas uniformes, identificadores `F1`–`F8`.
- Los estados de esta tabla coinciden con la columna `descargado` del CSV.
- Las rutas locales marcadas como `Sí` existen: cuatro directorios/archivos de F1–F4.
- No se agregaron dependencias ni se descargaron nuevas bases.
