"""Pruebas desde la interfaz pública de M-04."""
import csv
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/radar.py"


def run_radar(out, *args, data=None, check=True):
    return subprocess.run(
        [sys.executable, str(CLI), "--data-dir", str(data or ROOT / "data"),
         "--config", str(ROOT / "config/radar_m04_v1.json"),
         "--output-dir", str(out), *args],
        capture_output=True, text=True, check=check,
    )


def read_run(out):
    return json.loads((out / "hallazgos.json").read_text(encoding="utf-8"))


def test_r1_recorrido_completo(tmp_path):
    run_radar(tmp_path, "--mode", "standard", "--rule", "R1")
    result = read_run(tmp_path)
    findings = result["hallazgos"]
    assert result["conteos"]["R1"] == len(findings) == 26
    ids = [f["id"] for f in findings]
    assert len(set(ids)) == 26
    assert "R1:2023:04-16" in ids
    with (tmp_path / "hallazgos.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["id"] for row in rows] == ids
    for row, finding in zip(rows, findings):
        for field, value in finding.items():
            if isinstance(value, (list, dict)):
                assert json.loads(row[field]) == value
            else:
                assert row[field] == ("" if value is None else str(value))


def test_r1_contraste_independiente_con_encovi_y_banguat(tmp_path):
    from decimal import Decimal
    from itertools import combinations

    source = ROOT / "data/processed"
    with (source / "indicadores_encovi_2023.csv").open(encoding="utf8") as f:
        rates = {(r["depto_id"], r["indicador"]): Decimal(r["valor"]) for r in csv.DictReader(f)
                 if r["estado"] == "publicable_con_reserva" and r["cv"]
                 and Decimal(r["cv"]) <= 30 and int(r["n"]) >= 30}
    with (source / "pib_per_capita.csv").open(encoding="utf8") as f:
        y = {r["depto_id"]: Decimal(r["pib_per_capita"]) for r in csv.DictReader(f)}
    pairs = list(combinations(sorted(y), 2))
    assert len(pairs) == 231
    for tolerance, poverty_count, union in [(2, 14, 16), (3, 22, 26), (5, 36, 44)]:
        run_radar(tmp_path, "--mode", "exploratory", "--set", f"r1_i={tolerance}")
        result = read_run(tmp_path)
        expected = []
        for a, b in pairs:
            di = abs(rates[a, "ocupacion_sector_informal"] - rates[b, "ocupacion_sector_informal"])
            dp = abs(rates[a, "pobreza_total"] - rates[b, "pobreza_total"])
            ratio = max(y[a], y[b]) / min(y[a], y[b])
            if di <= tolerance and (dp >= 15 or ratio >= Decimal("1.5")):
                reason = (dp < 15, ratio < Decimal("1.5"))
                expected.append((reason, -dp, -ratio, di, f"R1:2023:{a}-{b}"))
        assert len(expected) == union
        assert sum(not reason[0] for reason, *_ in expected) == poverty_count
        assert [row["id"] for row in result["hallazgos"]] == [r[-1] for r in sorted(expected)]


def test_archivos_identicos_tras_invertir_filas_y_fallo_de_contrato(tmp_path):
    data = tmp_path / "data"
    out = tmp_path / "salida"
    (data / "processed").mkdir(parents=True)
    run_radar(out)
    def contents():
        return [(out / name).read_bytes() for name in ("hallazgos.csv", "hallazgos.json")]
    original = contents()
    for name in ("matriz_departamental.csv", "indicadores_encovi_nacional_2023.csv"):
        header, *rows = (ROOT / "data/processed" / name).read_bytes().splitlines()
        (data / "processed" / name).write_bytes(b"\n".join([header, *reversed(rows)]) + b"\n")
    run_radar(out, data=data)
    assert contents() == original
    (data / "processed/matriz_departamental.csv").write_text("invalido\n")
    assert run_radar(out, data=data, check=False).returncode != 0
    assert contents() == original


def test_vista_vacia_conserva_referencias(tmp_path):
    run_radar(tmp_path)
    full = read_run(tmp_path)
    run_radar(tmp_path, "--depto", "01")
    filtered = read_run(tmp_path)
    assert filtered["cobertura"] == full["cobertura"]
    assert filtered["sensibilidad"] == full["sensibilidad"]
    assert filtered["conteos"] == {"R1": 0}
    assert filtered["hallazgos"] == []
    assert len((tmp_path / "hallazgos.csv").read_text().splitlines()) == 1


def test_parametro_sin_regla_activa_se_rechaza(tmp_path):
    assert run_radar(tmp_path, "--mode", "exploratory", "--rule", "R1", "--set", "r4_lq=2", check=False).returncode != 0


def test_no_publica_estimaciones_ni_ic_restringidos(tmp_path):
    import shutil

    data = tmp_path / "data"
    inputs = data / "processed"
    out = tmp_path / "salida"
    inputs.mkdir(parents=True)
    shutil.copy(ROOT / "data/processed/indicadores_encovi_nacional_2023.csv", inputs)
    name = "matriz_departamental.csv"
    with (ROOT / "data/processed" / name).open() as f:
        rows = list(csv.DictReader(f))
    row = next(r for r in rows if r["depto_id"] == "04")
    row["pobreza_total_cv_2023"] = "31"
    for field in ("valor", "ic95_inf", "ic95_sup"):
        row[f"pobreza_total_{field}_2023"] = "51.123456789"
    with (inputs / name).open("w") as f:
        writer = csv.DictWriter(f, rows[0])
        writer.writeheader()
        writer.writerows(rows)
    run_radar(out, data=data)
    for p in out.glob("*.?s*"):
        assert "51.123456789" not in p.read_text()
    finding = next(r for r in read_run(out)["hallazgos"] if r["id"] == "R1:2023:04-16")
    assert finding["motivo"] == "solo_pib"
    assert finding["magnitudes"]["brecha_pobreza_pp"] is None
    ev = next(e for e in finding["evidencias"] if e["territorio"] == "04" and e["indicador"] == "pobreza_total")
    assert ev["valor"] is ev["diagnostico"]["ic95_inf"] is ev["diagnostico"]["ic95_sup"] is None


def test_robustez_y_diferencias_por_escenario(tmp_path):
    run_radar(tmp_path, "--rule", "R1")
    standard = read_run(tmp_path)
    ids = {f["id"] for f in standard["hallazgos"]}
    members = []
    assert len(standard["sensibilidad"]) == 7
    for scenario in standard["sensibilidad"]:
        key = scenario["parametro"]
        if key is None:
            actual = ids
        else:
            run_radar(tmp_path, "--mode", "exploratory", "--rule", "R1", "--set", f"{key}={scenario['valor']}")
            actual = {f["id"] for f in read_run(tmp_path)["hallazgos"]}
        assert len(actual) == scenario["conteo"]
        assert sorted(actual - ids) == scenario["aparecen"]
        assert sorted(ids - actual) == scenario["desaparecen"]
        members.append(actual)
    for finding in standard["hallazgos"]:
        hits = sum(finding["id"] in case for case in members)
        assert finding["robustez"] == {"presentes": hits, "escenarios": 7, "proporcion": hits / 7}
