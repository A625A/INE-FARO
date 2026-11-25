"""Réplica ENEIC IV-2025 a partir del XLSX de Personas. Sólo biblioteca estándar."""
import argparse
import json
import sqlite3
from contextlib import closing
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
COLUMNS = (
    "ANIO", "TRIMESTRE", "DOMINIO", "FACTOR", "P02A03", "PET", "PEA", "OCUPADOS",
    "DESOCUPADOS", "SUBVISIBLES", "INACTIVOS", "FORMAL_INFORMAL", "YLAB_PUBLI",
)
DOMAINS = {1: "Urbano metropolitano", 2: "Resto urbano", 3: "Rural nacional"}


def numeric_cell(cell, strings):
    value = cell.findtext(NS + "v")
    if cell.get("t") == "s":
        value = strings[int(value)]
    if cell.get("t") == "inlineStr":
        value = "".join(t.text or "" for t in cell.iter(NS + "t"))
    if value is None or not value.strip():
        return None
    try:
        return int(value)
    except ValueError:
        return float(value)


def read_workbook(path):
    """Parse the official single-sheet workbook, keeping only documented columns."""
    with ZipFile(path) as archive:
        strings = [
            "".join(tag.text or "" for tag in item.iter(NS + "t"))
            for item in ET.fromstring(archive.read("xl/sharedStrings.xml"))
        ]
        selected = {}
        with archive.open("xl/worksheets/sheet1.xml") as sheet:
            for _, row in ET.iterparse(sheet):
                if row.tag != NS + "row":
                    continue
                if row.get("r") == "1":
                    for cell in row:
                        name = strings[int(cell.findtext(NS + "v"))]
                        if name in COLUMNS:
                            selected[cell.get("r").rstrip("0123456789")] = COLUMNS.index(name)
                    if len(selected) != len(COLUMNS):
                        raise ValueError("Faltan variables en el encabezado de Personas.")
                else:
                    values = [None] * len(COLUMNS)
                    for cell in row:
                        index = selected.get(cell.get("r").rstrip("0123456789"))
                        if index is not None:
                            values[index] = numeric_cell(cell, strings)
                    yield values
                row.clear()


def summarize(db, scope):
    """Ratios use distinct denominators. Income coverage counts observed zeroes."""
    def query(statement):
        return db.execute("WITH universo AS (SELECT * FROM personas WHERE " + scope +
                          ") " + statement).fetchone()

    volumes = {}
    conditions = {
        "personas": "1", "pet": "PET=1", "pea": "PEA=1", "ocupados": "OCUPADOS=1",
        "desocupados": "DESOCUPADOS=1", "subvisibles": "SUBVISIBLES=1",
        "inactivos": "INACTIVOS=1",
        "informal": "OCUPADOS=1 AND FORMAL_INFORMAL=1",
        "formal": "OCUPADOS=1 AND FORMAL_INFORMAL=2",
        "sin_clasificar": "OCUPADOS=1 AND (FORMAL_INFORMAL IS NULL OR FORMAL_INFORMAL NOT IN (1,2))",
    }
    for name, condition in conditions.items():
        n, weight = query("SELECT COUNT(*), COALESCE(SUM(FACTOR),0) FROM universo WHERE " + condition)
        volumes[name] = {"n": n, "personas_expandidas": weight}

    rates = {}
    for name, numerator, denominator in (
        ("participacion", "pea", "pet"), ("ocupacion_especifica", "ocupados", "pea"),
        ("ocupacion_bruta", "ocupados", "pet"), ("desempleo", "desocupados", "pea"),
        ("subempleo_visible", "subvisibles", "ocupados"), ("informalidad", "informal", "ocupados"),
        ("formalidad", "formal", "ocupados"),
    ):
        rates[name] = 100 * volumes[numerator]["personas_expandidas"] / volumes[denominator]["personas_expandidas"]

    incomes = {}
    for name in ("ocupados", "informal", "formal"):
        base = conditions[name]
        n, valid_weight, average, zero_n, zero_weight = query(
            """SELECT COUNT(*), SUM(FACTOR), SUM(FACTOR*1.0*YLAB_PUBLI)/SUM(FACTOR),
                      SUM(YLAB_PUBLI=0), SUM(CASE WHEN YLAB_PUBLI=0 THEN FACTOR ELSE 0 END)
               FROM universo WHERE """ + base + " AND YLAB_PUBLI >= 0")
        median, = query(
            """SELECT MIN(YLAB_PUBLI) FROM
                  (SELECT YLAB_PUBLI, SUM(SUM(FACTOR)) OVER (ORDER BY YLAB_PUBLI) AS acumulado,
                          SUM(SUM(FACTOR)) OVER () AS total
                   FROM universo WHERE """ + base + """ AND YLAB_PUBLI >= 0 GROUP BY YLAB_PUBLI)
               WHERE 2*acumulado>=total""")
        incomes[name] = {
            "n_valido": n, "n_no_valido": volumes[name]["n"] - n,
            "n_ceros": zero_n, "peso_ceros": zero_weight,
            "peso_valido": valid_weight, "peso_no_valido": volumes[name]["personas_expandidas"] - valid_weight,
            "cobertura_ponderada_pct": 100*valid_weight / volumes[name]["personas_expandidas"],
            "media_quetzales": average, "mediana_quetzales": median,
        }
    return {"volumenes": volumes, "tasas_pct": rates, "ingresos": incomes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("personas_xlsx")
    args = parser.parse_args()
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE personas (" + ", ".join(COLUMNS) + ")")
        db.executemany("INSERT INTO personas VALUES (" + ", ".join("?" for k in COLUMNS) + ")",
                       read_workbook(args.personas_xlsx))
        periods = db.execute("SELECT DISTINCT ANIO, TRIMESTRE FROM personas").fetchall()
        domain_codes = dict(db.execute("SELECT DOMINIO, COUNT(*) FROM personas GROUP BY DOMINIO"))
        bad_weight, bad_age, negative_income = db.execute(
            """SELECT COUNT(*) FILTER (WHERE FACTOR IS NULL OR FACTOR<=0),
                      COUNT(*) FILTER (WHERE OCUPADOS=1 AND (P02A03 IS NULL OR P02A03<15)),
                      COUNT(*) FILTER (WHERE OCUPADOS=1 AND YLAB_PUBLI<0)
               FROM personas""").fetchone()
        if periods != [(2025, 5)] or set(domain_codes) != set(DOMAINS):
            raise ValueError(f"Verificar códigos de período o dominio: {periods}, {list(domain_codes)}")
        if bad_weight or bad_age or negative_income:
            raise ValueError(f"Pesos, edades o ingresos fuera de rango: {bad_weight}, {bad_age}, {negative_income}")
        output = {"anio": 2025, "trimestre_en_base": 5, "nacional": summarize(db, "1"),
                  "dominios": {name: summarize(db, f"DOMINIO={code}") for code, name in DOMAINS.items()}}
        print(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
