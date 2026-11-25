# Diccionario preliminar y análisis exploratorio - ENCOVI 2023

## 1. Entregables de la tarea I-02
Según el plan de trabajo, la tarea **I-02** requiere entregar:
- `docs/diccionario_encovi.csv` (Diccionario de variables estructurado)
- `notebooks/01_exploracion_encovi.ipynb` (Notebook ejecutado y verificado)

---

## 2. Hallazgos clave de la exploración inicial
1. **Dimensiones de la base de Personas (`encovi_2023_personas.sav`):**
   - 46,017 filas (individuos) y 626 columnas.
2. **Dimensiones de la base de Hogares (`encovi_2023_hogares.sav`):**
   - Registros de hogares vinculados mediante el identificador común `NO_HOGAR`.
3. **Ponderadores y diseño muestral:**
   - Se confirmó el uso de la variable `FACTOR` (peso principal). Nota: En la base de hogares se encontró `Factor3`, mientras que en personas está `Factor2`. Se debe usar siempre el factor correspondiente a la granularidad analizada (hogar o persona) para cumplir con las reglas del INE.
4. **Variables clave identificadas para los siguientes pasos (M-01 / M-03):**
   - Geografía: `DEPTO` (1 a 22 departamentos), `DOMINIO`, `AREA` (urbano/rural).
   - Identificadores: `UPM`, `NO_HOGAR`.
   - Bienestar / Pobreza: `POBREZA`.
   - Mercado laboral / Informalidad: `FORMAL_INFORMAL`, `OCUPADOS`, `PEA`, `PET`.
   - Ingresos y consumo: Variables de ingresos laborales y agregados de consumo.
