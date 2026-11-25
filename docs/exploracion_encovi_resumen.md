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

## Controles complementarios reconciliados con I-03 — 25/11/2026

Se conserva el diccionario de main y la metodología del compañero, incluidos
universos, ponderadores, validaciones nacionales y precisión aproximada. No se
recalculan ni sustituyen sus resultados. Los conteos siguientes son controles de
estructura y conjuntos, no estimaciones poblacionales.

- Las cinco bases suman 821 columnas publicadas. Los nombres y etiquetas coinciden
  con sus XLSX; el inventario completo se guarda como complemento en
  `docs/evidencia/I-02/diccionario_detallado.csv`, sin reemplazar el diccionario
  seleccionado de `docs/diccionario_encovi.csv`.
- Las claves verificadas son NO_HOGAR en Hogares, Consumo y Negocios 1;
  NO_HOGAR+CP en Personas y NO_HOGAR+ID_NEGOCIO en Negocios 2. Las uniones con
  Hogares conservan las filas y rechazan duplicados en vez de eliminarlos.
- Hay 10,964 hogares en Hogares y 10,930 en Consumo. Los **34 hogares sin
  correspondencia en Consumo contienen 95 personas**. No son registros huérfanos:
  existen en Hogares y Personas. Se mantienen en las uniones izquierdas. Sus
  POBREZA=0 y pesos alternativos cero no se imputan ni convierten en no pobreza.
- Los mismos 2,142 hogares declarantes tienen detalle de negocios. Los **73
  hogares con cantidades discordantes** se identifican dentro de ese conjunto;
  no son los hogares sin correspondencia en Consumo. Su intersección se informa
  separadamente en el JSON de controles, sin inferir identidades por conteos.
- **2,469** suma P14A02A en todos los hogares; **2,440** suma esa variable sólo en
  hogares declarantes; **2,490** son registros de detalle, no hogares. La diferencia
  dentro de declarantes es +50 registros. Fuera del conjunto SI hay 37 hogares
  con cantidad registrada, 23 positiva: no se los incorpora como declarantes.
  Las discrepancias pertenecen a los datos originales, con claves únicas; no se
  corrigen artificialmente ni se atribuye una causa sin evidencia.

Personas contiene 18,036 registros con OCUPADOS=1 sin el filtro de edad. Ese conteo
no debe confundirse con los 17,523 ocupados de 15 años o más documentados en I-03.
Se conserva FACTOR para informalidad y Factor3 en Consumo para pobreza, según
`docs/metodologia.md`. La correlación exploratoria del notebook no justifica
intercambiar ponderadores. SECTOR en Consumo identifica la UPM y se contrasta con
UPM de Hogares; esto no cambia el enlace por NO_HOGAR utilizado en la metodología.

El notebook conserva las celdas anteriores de cálculo y añade controles, sin
mostrar una muestra de registros individuales. Los scripts permiten repetirlos:

```sh
python -m pip install -r requirements.txt
python scripts/ejecutar_exploracion_encovi.py
python -m pytest tests/test_encovi_i02.py -q
```

Los resultados y hashes de los insumos están en `docs/evidencia/I-02/validacion.json`.
No se desarrollan M-01, radar o interfaz. Las cantidades de negocios siguen siendo
una limitación para futuros indicadores; no impiden revisar estos controles de
calidad. Se preservan los cálculos científicos ya incorporados en I-02/I-03.
