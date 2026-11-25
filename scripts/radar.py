"""Radar territorial M-04. Entrada pública offline para generar fichas del corte 2023."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if not __package__:
    sys.path.insert(0, str(ROOT))

from scripts.radar_rules import RULES
from scripts.radar_rules.export import publish, serialize
from scripts.radar_rules.inputs import load_inputs

CONFIG = ROOT / "config/radar_m04_v1.json"


def read_config(path):
    def parse(p):
        return json.loads(p.read_text(encoding="utf-8"), parse_float=Decimal)
    config = parse(path)
    if config != parse(CONFIG):
        raise ValueError("Configuración incompatible con la versión aprobada")
    return config


def classify(universe, config, mode, selected_rules, departments, parameters):
    keys_used = [key for rule, (_, keys) in RULES.items() if rule in selected_rules for key in keys]
    base = {key: config["standard"][key] for key in keys_used}
    grid = config["grid"]
    for key, value in parameters.items():
        if mode != "exploratory" or key not in base or not value.is_finite() or value not in grid[key]:
            raise ValueError(f"Ajuste fuera del modo exploratorio o de la rejilla: {key}")
    params = {**base, **parameters}
    findings, sensitivity, counts = [], [], {}
    for rule, (evaluate, keys) in RULES.items():
        if rule not in selected_rules:
            continue
        standard = evaluate(universe, base)
        ids = {row["id"] for row in standard}
        scenarios = [(None, None, ids)]
        for key in keys:
            for value in grid[key]:
                if value != base[key]:
                    rows = evaluate(universe, {**base, key: value})
                    scenarios.append((key, value, {row["id"] for row in rows}))
        selected = standard if all(params[k] == base[k] for k in keys) else evaluate(universe, params)
        for key, value, members in scenarios:
            sensitivity.append({
                "regla": rule, "parametro": key, "valor": value, "conteo": len(members),
                "aparecen": sorted(members - ids), "desaparecen": sorted(ids - members),
            })
        visible = [f for f in selected if not departments or departments.intersection(f["territorios"])]
        for finding in visible:
            hits = sum(finding["id"] in members for _, _, members in scenarios)
            finding["robustez"] = {"presentes": hits, "escenarios": len(scenarios),
                                   "proporcion": hits / len(scenarios)}
        findings.extend(visible)
        counts[rule] = len(visible)
    return {
        "schema_version": "1.0", "rules_version": config["rules_version"], "modo": mode,
        "hashes_filas_canonicas": universe.canonical_hashes,
        "parametros": params, "filtros": {"reglas": [k for k in RULES if k in selected_rules],
                                           "departamentos": sorted(departments)},
        "cobertura": universe.coverage, "conteos": counts,
        "sensibilidad": sensitivity, "hallazgos": findings,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--mode", choices=("standard", "exploratory"), default="standard")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    parser.add_argument("--rule", choices=RULES, action="append", help="Regla visible (repetible)")
    parser.add_argument("--depto", choices=[f"{i:02}" for i in range(1, 23)], action="append",
                        help="Departamento presente en la ficha (repetible)")
    parser.add_argument("--set", metavar="PARAMETRO=VALOR", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        config = read_config(args.config)
        overrides = {}
        for entry in args.set:
            key, value = entry.split("=", 1)
            if key in overrides:
                raise ValueError(f"Parámetro repetido: {key}")
            overrides[key] = Decimal(value)
        universe = load_inputs(args.data_dir)
        result = classify(universe, config, args.mode, set(args.rule or RULES),
                          set(args.depto or []), overrides)
        publish(args.output_dir, serialize(result, universe.raw_hashes))
    except (ValueError, OSError, csv.Error, InvalidOperation) as error:
        print(f"Error de contrato M-04: {error}", file=sys.stderr)
        return 1
    print(f"Fichas publicadas: {len(result['hallazgos'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
