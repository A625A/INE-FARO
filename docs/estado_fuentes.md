# Estado de Fuentes de Datos — INE FARO

**Fecha de actualización:** 24 de noviembre de 2026  
**Responsable:** Equipo INE FARO  

---

## 1. Resumen de Disponibilidad y Alcance

| ID | Fuente | Estado | Archivo Local | Observaciones / Alcance |
|---|---|---|---|---|
| **F1** | ENCOVI 2023 | 🟢 Disponible | `data/raw/encovi_2023/` | Fuente principal obligatoria (Personas, Hogares, Consumo, Negocios). |
| **F2** | Guía ENCOVI 2023 | 🟢 Disponible | `data\raw\encovi_2023\Guia-para-el-uso-de-bases-de-datos_v_final.pdf` | Necesaria para validar ponderadores (FACTOR / Factor3). |
| **F3** | PIB Departamental Banguat | 🟢 Disponible | `data/raw/banguat/` | Fuente principal obligatoria para PIB y actividad económica. |
| **F4** | DINESE 2021-2024 | 🟡 Condicional | `data/raw/dinese/` | Sujeta a revisión de comparabilidad (no forzar integración). |
| **F5** | ENEIC / ENEI | ❌ Descartado | `data/raw/eneic/` | Excluido por falta de representatividad departamental. |
| **F6** | ENIGH | ❌ Descartado | `data/raw/enigh/` | Excluido para evitar complejidad adicional en el MVP. |
| **F7** | Proyecciones Población | 🟡 Pendiente | `data/raw/proyecciones_poblacion.csv` | Útil para normalización per cápita si se requiere. |
| **F8** | Perfiles Departamentales INE | 🟡 Pendiente | `docs/perfiles_ine.pdf` | Usado exclusivamente para validación de agregados. |

---

## 2. Bitácora de Verificación y Descargas

### F1: ENCOVI 2023 (Microdatos)
- **Estado:** Descargado y organizado (`encovi_2023_personas.sav`, `encovi_2023_hogares.sav`, etc.).
- **Variables clave:** `NO_HOGAR`, `DEPTO`, `FACTOR`, variables de pobreza e informalidad.

### F2: Guía ENCOVI 2023
- **Estado:** Descargado en `data\raw\encovi_2023\Guia-para-el-uso-de-bases-de-datos_v_final.pdf`, etc.

### F3: PIB Departamental (Banguat)
- **Estado:** Descargado en `data/raw/banguat/`.
- **Cobertura:** 2013-2024 (Departamental y sectorial).

---

## 3. Información Crítica y Decisiones del MVP

- **Congelamiento de alcance:** Se decidió descartar ENEIC y ENIGH para mitigar riesgos de tiempo y complejidad en el procesamiento.
- **Enfoque:** Todo el esfuerzo analítico se concentrará en el núcleo **ENCOVI 2023 + PIB Banguat**, garantizando hallazgos explicables y verificables para los 22 departamentos.
