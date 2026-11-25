"""Lectura de instantáneas M-03/M-01 y supresión previa al análisis."""
import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import io
from statistics import median

from scripts.comun import DEPARTAMENTOS

I = "ocupacion_sector_informal"
P = "pobreza_total"
WEIGHTS = {I: "FACTOR", P: "Factor3", "pobreza_extrema": "Factor3"}
PRECISION = "aproximada_depto_upm_sin_estratos_originales"
DIAGNOSTICS = "valor ic95_inf ic95_sup cv n upm_n ponderador estado".split()
GROUPS = "A B C D-E F G H I J K L M N O P Q R-S-T-U".split()


@dataclass
class Estimate:
    value: Decimal | None
    lower: Decimal | None
    upper: Decimal | None
    diagnostic: dict


@dataclass
class Territory:
    code: str
    name: str
    encovi: dict
    pib_per_capita: Decimal | None


@dataclass
class Universe:
    territories: tuple
    national_informality: Estimate
    medians: dict
    coverage: dict
    canonical_hashes: dict
    raw_hashes: dict


def number(text):
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise ValueError("Número inválido en el insumo") from None
    if not value.is_finite():
        raise ValueError("Número no finito en el insumo")
    return value


def estimate(row, weight):
    state = row["estado"]
    n, upm = int(row["n"]), int(row["upm_n"])
    cv = number(row["cv"]) if row["cv"] else None
    if (state not in ("publicable_con_reserva", "no_publicable") or row["ponderador"] != weight
            or not 1 <= upm <= n or (cv is not None and cv < 0)):
        raise ValueError("Diagnóstico ENCOVI incompatible")
    eligible = state != "no_publicable" and n >= 30 and cv is not None and cv <= 30
    diag = dict(estado=state, n=n, upm_n=upm, cv=float(cv) if cv is not None else None,
                ponderador=weight, precision=PRECISION, elegible=eligible)
    if not eligible:
        return Estimate(None, None, None, diag)
    val, lo, hi = (number(row[k]) for k in ("valor", "ic95_inf", "ic95_sup"))
    if not 0 <= lo <= val <= hi <= 100:
        raise ValueError("Intervalo o tasa ENCOVI incoherente")
    return Estimate(val, lo, hi, diag)


def sector_fields(group):
    suffix = group.lower().replace("-", "_")
    return f"vab_{suffix}_millones_q_2023", f"participacion_{suffix}_pct_2023"


def matrix_columns():
    cols = ["depto_id", "departamento", "anio"]
    cols.extend(f"{ind}_{k}_2023" for ind in WEIGHTS for k in DIAGNOSTICS)
    cols.extend(("pib_total_millones_q_2023", "pib_por_habitante_q_2023",
                 "vab_total_millones_q_2023", "ipns_millones_q_2023"))
    cols.extend(col for group in GROUPS for col in sector_fields(group))
    return cols + ["actividad_predominante_2023", "participacion_predominante_pct_2023"]


def read_rows(path, columns, keys, canonical, raw):
    data = path.read_bytes()
    raw[path.name] = sha256(data).hexdigest()
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""), strict=True)
    if sorted(reader.fieldnames or []) != sorted(columns):
        raise ValueError(f"cabecera incompatible en {path.name}")
    rows = list(reader)
    if any(None in row or None in row.values() or row["anio"] != "2023" for row in rows):
        raise ValueError(f"Año o longitud de fila incompatible en {path.name}")
    def key(row):
        return tuple(row[k] for k in keys)
    if len({key(row) for row in rows}) != len(rows):
        raise ValueError(f"Clave duplicada en {path.name}")
    rows.sort(key=key)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    canonical[path.name] = sha256(stream.getvalue().encode()).hexdigest()
    return rows


def check_vab(row):
    total = number(row["vab_total_millones_q_2023"])
    amounts, shares = {}, {}
    for group in GROUPS:
        amount, share = sector_fields(group)
        amounts[group], shares[group] = number(row[amount]), number(row[share])
        if (total <= 0 or amounts[group] < 0 or not 0 <= shares[group] <= 100 or
                abs(100 * amounts[group] / total - shares[group]) > Decimal("1e-9")):
            raise ValueError("VAB o participación sectorial incoherente")
    largest = max(amounts, key=amounts.get)
    ipns = number(row["ipns_millones_q_2023"])
    if (abs(sum(amounts.values()) - total) > Decimal("1e-6") or
            abs(sum(shares.values()) - 100) > Decimal("1e-9") or
            abs(total + ipns - number(row["pib_total_millones_q_2023"])) > Decimal("1e-6") or
            row["actividad_predominante_2023"] != largest or
            number(row["participacion_predominante_pct_2023"]) != shares[largest]):
        raise ValueError("Conciliación productiva incompatible con M-03")


def load_inputs(data_dir):
    folder = data_dir / "processed"
    canonical, raw = {}, {}
    rows = read_rows(folder / "matriz_departamental.csv", matrix_columns(), ["depto_id"], canonical, raw)
    if [row["depto_id"] for row in rows] != [f"{i:02}" for i in DEPARTAMENTOS]:
        raise ValueError("cobertura departamental incompleta")
    territories = []
    for row in rows:
        code = row["depto_id"]
        if row["departamento"] != DEPARTAMENTOS[int(code)]:
            raise ValueError("Nombre y código departamental incompatibles")
        check_vab(row)
        estimates = {ind: estimate({k: row[f"{ind}_{k}_2023"] for k in DIAGNOSTICS}, weight)
                     for ind, weight in WEIGHTS.items()}
        y = number(row["pib_por_habitante_q_2023"]) if row["pib_por_habitante_q_2023"] else None
        territories.append(Territory(code, row["departamento"], estimates, y if y and y > 0 else None))
    keys = ["ambito", "area", "indicador"]
    cols = "ambito area anio indicador ponderador valor n upm_n cv ic95_inf ic95_sup precision estado".split()
    national = read_rows(folder / "indicadores_encovi_nacional_2023.csv", cols, keys, canonical, raw)
    national_i = None
    for row in national:
        scope, area, ind = (row[k] for k in keys)
        if scope == "nacional" and area == "" and ind in WEIGHTS:
            weight = WEIGHTS[ind]
        elif scope == "area" and area in ("urbana", "rural") and ind == f"{I}_{area}":
            weight = WEIGHTS[I]
        else:
            raise ValueError("Clave nacional/área incompatible")
        if row["precision"] != PRECISION:
            raise ValueError("Diseño de precisión incompatible")
        value = estimate(row, weight)
        if scope == "nacional" and ind == I:
            national_i = value
    if national_i is None:
        raise ValueError("Falta la referencia de ocupación nacional")
    diagnostics = {}
    medians = {}
    for ind in WEIGHTS:
        values = [d.encovi[ind].value for d in territories if d.encovi[ind].value is not None]
        diagnostics[ind] = {"elegibles": len(values), "total": len(rows),
                            "diagnosticos": {d.code: d.encovi[ind].diagnostic for d in territories}}
        if ind in (I, P):
            medians[ind] = median(values) if values else None
    production = [d.pib_per_capita for d in territories if d.pib_per_capita is not None]
    medians["pib_por_habitante"] = median(production) if production else None
    coverage = {"encovi_departamental": diagnostics, "encovi_nacional": national_i.diagnostic,
                "pib_por_habitante": {"elegibles": len(production), "total": len(rows)},
                "medianas": {k: float(v) if v is not None else None for k, v in medians.items()},
                "parejas": len(rows) * (len(rows) - 1) // 2}
    return Universe(tuple(territories), national_i, medians, coverage, canonical, raw)
