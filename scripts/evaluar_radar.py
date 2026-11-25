"""Cotejo independiente de la corrida estándar de M-04 contra M-01 y Banguat I-04."""
import argparse
import csv
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
from math import isclose
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
I, P = "ocupacion_sector_informal", "pobreza_total"
GRID = {
    "R1": {"r1_i": (2, 3, 5), "r1_p": (10, 15, 20), "r1_y": (1.25, 1.5, 2)},
    "R2a": {}, "R2b": {"r2b_p": (10, 15, 20)},
    "R3": {"r3_percentil": (20, 25, 30), "r3_i": (8, 10, 12)},
    "R4": {"r4_lq": (1.25, 1.5, 2), "r4_s": (8, 10, 12)},
}
EXPECTED = {"R1": 26, "R2a": 0, "R2b": 1, "R3": 7, "R4": 10}


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass
class Control:
    parejas: int
    celdas: int
    conteos: dict
    escenarios: dict
    referencias: dict
    ejemplos: dict
    r1_pobreza: dict
    r1_union: dict
    restringidas: int


def source(folder, name):
    df = pd.read_csv(folder / name, dtype={"depto_id": str})
    require(df.anio.eq(2023).all(), f"Año incompatible en {name}")
    return df


def eligible(df):
    return df.estado.eq("publicable_con_reserva") & df.n.ge(30) & df.cv.between(0, 30)


def recalcular(data):
    folder = data / "processed"
    obs = source(folder, "indicadores_encovi_2023.csv")
    matrix = source(folder, "matriz_departamental.csv").set_index("depto_id")
    require(matrix.index.is_unique, "Clave M-03 duplicada")
    valid = eligible(obs)
    for r in obs.loc[~valid].itertuples():
        for field in ("valor", "ic95_inf", "ic95_sup"):
            require(pd.isna(matrix.at[r.depto_id, f"{r.indicador}_{field}_2023"]),
                    f"{r.depto_id} {r.indicador} {field} restringido en M-03")
    dep = obs.loc[valid].pivot(index="depto_id", columns="indicador", values="valor").reindex(matrix.index)
    dep = dep.rename(columns={I: "i", P: "p"})
    per_capita = source(folder, "pib_per_capita.csv").set_index("depto_id")
    require(per_capita.index.is_unique, "Clave de PIB duplicada")
    dep["y"] = per_capita.pib_per_capita
    dep["y"] = dep.y.where(dep.y.gt(0))
    dep = dep.sort_index()
    ref = dep[["i", "p", "y"]].median()
    national = source(folder, "indicadores_encovi_nacional_2023.csv")
    ni = national.loc[(national.ambito == "nacional") & (national.indicador == I) & eligible(national), "valor"].item()
    raw = source(folder, "pib_departamental.csv")
    sectors = raw.loc[(raw.tipo_precio == "corrientes") & (raw.medida == "valor_agregado")]
    amounts = sectors.pivot(index="depto_id", columns="sector", values="pib_valor").sort_index()
    require(amounts.shape == (22, 17) and amounts.index.equals(dep.index)
            and not amounts.isna().any().any(), "Universo de VAB incompleto")
    shares = amounts.div(amounts.sum(axis=1), axis=0) * 100
    regional = amounts.sum() * 100 / amounts.sum().sum()
    left, right = np.triu_indices(len(dep), 1)
    vectors = shares.to_numpy()
    distance = np.abs(vectors[left] - vectors[right]).sum(axis=1) / 2
    iv, pv, yv = (dep[k].to_numpy() for k in ("i", "p", "y"))
    pairs = pd.DataFrame({
        "a": dep.index[left], "b": dep.index[right], "dist": distance,
        "di": abs(iv[left]-iv[right]), "dp": abs(pv[left]-pv[right]),
        "ratio": np.maximum(yv[left], yv[right]) / np.minimum(yv[left], yv[right])})
    local = shares.reset_index().melt(id_vars="depto_id", var_name="g", value_name="s")
    local["lq"] = local.s / local.g.map(regional.where(regional.gt(0)))
    local = local.join(dep[["i", "p"]], on="depto_id")
    departments = dep.reset_index()
    med_y = departments.y.gt(ref.y)

    def select(rule, par):
        if rule == "R1":
            poverty, prod = pairs.dp.ge(par["r1_p"]), pairs.ratio.ge(par["r1_y"])
            rows = pairs.assign(priority=np.select([poverty & prod, poverty], [0, 1], default=2))
            rows = rows.loc[pairs.di.le(par["r1_i"]) & (poverty | prod)]
            rows = rows.sort_values(["priority", "dp", "ratio", "di", "a", "b"],
                                    ascending=[True, False, False, True, True, True])
        elif rule == "R3":
            limit = np.percentile(distance, par["r3_percentil"], method="linear")
            rows = pairs.loc[pairs.dist.le(limit) & pairs.di.ge(par["r3_i"])]
            rows = rows.sort_values(["di", "dist", "a", "b"], ascending=[False, True, True, True])
        elif rule == "R4":
            rows = local.loc[local.i.gt(ref.i) & local.p.gt(ref.p) & local.s.ge(par["r4_s"])
                             & local.lq.ge(par["r4_lq"])]
            rows = rows.sort_values(["lq", "s", "depto_id", "g"], ascending=[False, False, True, True])
            return tuple(rule + ":2023:" + rows.depto_id + ":" + rows.g)
        else:
            primary = "i" if rule == "R2a" else "p"
            social = (departments.i.gt(ref.i) if rule == "R2a" else
                      departments.p.ge(ref.p + par["r2b_p"]) & departments.i.ge(ni))
            rows = departments.loc[med_y & social].sort_values([primary, "y", "depto_id"],
                                                               ascending=[False, False, True])
            return tuple(rule + ":2023:" + rows.depto_id)
        return tuple(rule + ":2023:" + rows.a + "-" + rows.b)

    scenarios, counts = {}, {}
    for rule, grid in GRID.items():
        base = {k: values[1] for k, values in grid.items()}
        scenarios[rule, None, None] = select(rule, base)
        counts[rule] = len(scenarios[rule, None, None])
        for key, values in grid.items():
            for v in (values[0], values[-1]):
                scenarios[rule, key, v] = select(rule, {**base, key: v})
    pairs_by_id = pairs.set_index(["a", "b"])
    r1 = pairs_by_id.loc["04", "16"]
    r3 = pairs_by_id.loc["04", "18"]
    r4 = local.set_index(["depto_id", "g"]).loc["16", "A"]
    examples = {"R1:2023:04-16": {"brecha_pobreza_pp": r1.dp},
                "R2b:2023:06": {"exceso_p_pp": dep.at["06", "p"]-ref.p, "exceso_y_q": dep.at["06","y"]-ref.y},
                "R3:2023:04-18": {"distancia_pp": r3.dist, "brecha_informalidad_pp": r3.di},
                "R4:2023:16:A": {"lq": r4.lq, "participacion_local_pct": r4.s}}
    # Decimal conserva el redondeo de presentación de las cifras del control.
    examples = {k: {m: Decimal(str(v)) for m, v in row.items()} for k, row in examples.items()}
    refs = {"distancia_p25": Decimal(str(np.percentile(distance, 25))), "i_nacional": ni,
            "mediana_i": ref.i, "mediana_p": ref.p, "mediana_y": ref.y}
    poverty_counts = {t: int((pairs.di.le(t) & pairs.dp.ge(15)).sum()) for t in (2, 3, 5)}
    unions = {t: int((pairs.di.le(t) & (pairs.dp.ge(15) | pairs.ratio.ge(1.5))).sum()) for t in (2, 3, 5)}
    return Control(len(pairs), len(local), counts, scenarios, refs, examples, poverty_counts, unions, int((~valid).sum()))


def tabla_sensibilidad(c):
    rows = []
    for (rule, key, value), ids in c.escenarios.items():
        base = set(c.escenarios[rule, None, None])
        rows.append({"regla": rule, "parametro": key, "valor": value, "conteo": len(ids),
                     "aparecen": sorted(set(ids)-base), "desaparecen": sorted(base-set(ids))})
    return rows


def contrastar_sensibilidad(c, actual):
    expected = tabla_sensibilidad(c)
    require(len(actual) == len(expected), "Número de escenarios incompatible")
    for row, other in zip(expected, actual):
        for k, v in row.items():
            require(other.get(k) == v, f"{row['regla']} {row['parametro']} {k} incompatible")


def contrastar_csv(path, cards):
    with path.open(encoding="utf8", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
    require(len(rows) == len(cards), "Longitud de CSV incompatible")
    for row, card in zip(rows, cards):
        require(set(row) == set(card), "Columnas CSV incompatibles")
        for key, v in card.items():
            value = row[key]
            if isinstance(v, (dict, list)):
                match = json.loads(value) == v
            else:
                match = value == ("" if v is None else str(v))
            require(match, f"{card['id']} {key} incompatible")


def validate(data, run_dir, output):
    c = recalcular(data)
    # Fijar la generación una vez para leer los archivos correspondientes al mismo corte.
    generation = (run_dir / "hallazgos.json").resolve().parent
    report = json.loads((generation / "hallazgos.json").read_text())
    cards = report["hallazgos"]
    require(report["modo"] == "standard" and c.conteos == EXPECTED == report["conteos"], "Conteos estándar")
    require(c.r1_union == {2: 16, 3: 26, 5: 44} and c.r1_pobreza == {2: 14, 3: 22, 5: 36}, "Control R1")
    require(round(c.referencias["distancia_p25"], 8) == Decimal("12.24314885"), "Control P25")
    contrastar_csv(generation / "hallazgos.csv", cards)
    contrastar_sensibilidad(c, report["sensibilidad"])
    all_ids = [ident for rule in GRID for ident in c.escenarios[rule, None, None]]
    require([row["id"] for row in cards] == all_ids, "Orden o identidad de las fichas")
    for row in cards:
        ident = row["id"]
        cases = [ids for (rule, _, _), ids in c.escenarios.items() if rule == row["regla"]]
        hits = sum(ident in ids for ids in cases)
        require(row["robustez"] == dict(presentes=hits, escenarios=len(cases), proporcion=hits/len(cases)),
                f"Robustez incompatible en {ident}")
        for key, val in c.ejemplos.get(ident, {}).items():
            require(isclose(row["magnitudes"][key], val, rel_tol=1e-12, abs_tol=1e-10), f"{ident} {key}")
        for item in row["evidencias"]:
            diag = item["diagnostico"]
            if diag.get("elegible") is False:
                require(all(v is None for v in (item["valor"], diag.get("ic95_inf"), diag.get("ic95_sup"))),
                        f"{ident} contiene evidencia restringida")
    output.mkdir(parents=True, exist_ok=True)
    table = tabla_sensibilidad(c)
    with (output / "radar_sensitivity.csv").open("w", encoding="utf8", newline="") as stream:
        writer = csv.DictWriter(stream, table[0], lineterminator="\n")
        writer.writeheader()
        for row in table:
            writer.writerow({**row, **{k: json.dumps(row[k]) for k in ("aparecen", "desaparecen")}})
    result = {"base_m03": "f731d26", "parejas": c.parejas, "celdas": c.celdas, "conteos": c.conteos,
              "total": len(cards), "escenarios": len(table), "estimaciones_restringidas": c.restringidas,
              "referencias": c.referencias, "casos": c.ejemplos, "r1_pobreza": c.r1_pobreza,
              "r1_union": c.r1_union, "sha256": {name: sha256((generation / name).read_bytes()).hexdigest()
              for name in ("hallazgos.json", "hallazgos.csv")}}
    (output / "radar_validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                                              default=float) + "\n", encoding="utf8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--run-dir", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/evaluation")
    args = parser.parse_args()
    print(validate(args.data_dir, args.run_dir, args.output_dir)["conteos"])
