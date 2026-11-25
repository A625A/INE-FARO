"""Regresiones del cotejo independiente del radar M-04."""
import csv
import json
import shutil
from decimal import Decimal
from pathlib import Path

import pytest

from scripts import evaluar_radar

DATOS = Path(__file__).resolve().parents[1] / "data"


def test_reproduce_controles_de_la_especificacion():
    control = evaluar_radar.recalcular(DATOS)
    assert control.parejas == 231
    assert control.celdas == 374
    assert control.conteos == {"R1": 26, "R2a": 0, "R2b": 1, "R3": 7, "R4": 10}
    assert control.r1_pobreza == {2: 14, 3: 22, 5: 36}
    assert control.r1_union == {2: 16, 3: 26, 5: 44}
    assert round(control.referencias["distancia_p25"], 8) == Decimal("12.24314885")
    assert control.escenarios[("R2b", None, None)] == ("R2b:2023:06",)
    assert len(control.escenarios) == 21
    assert set(control.ejemplos) == {
        "R1:2023:04-16", "R2b:2023:06", "R3:2023:04-18", "R4:2023:16:A"
    }
    assert round(control.ejemplos["R1:2023:04-16"]["brecha_pobreza_pp"], 2) == Decimal("42.55")
    assert round(control.ejemplos["R3:2023:04-18"]["distancia_pp"], 2) == Decimal("9.85")
    assert round(control.ejemplos["R3:2023:04-18"]["brecha_informalidad_pp"], 2) == Decimal("16.08")
    assert round(control.ejemplos["R4:2023:16:A"]["lq"], 2) == Decimal("1.97")
    assert round(control.ejemplos["R4:2023:16:A"]["participacion_local_pct"], 2) == Decimal("20.31")


def test_detecta_valor_restringido_expuesto_en_matriz(tmp_path):
    shutil.copytree(DATOS / "processed", tmp_path / "processed")
    matriz = tmp_path / "processed" / "matriz_departamental.csv"
    with matriz.open(newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        columnas, filas = lector.fieldnames, list(lector)
    filas[0]["pobreza_extrema_valor_2023"] = "8.57"
    with matriz.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    with pytest.raises(ValueError, match=r"01.*pobreza_extrema.*valor"):
        evaluar_radar.recalcular(tmp_path)


def test_paridad_reconoce_estructuras_json_y_ausencia(tmp_path):
    ficha = {
        "id": "R1:2023:04-16", "regla": "R1", "anio": 2023, "territorios": ["04", "16"],
        "grupo": None, "motivo": "pobreza", "magnitudes": {"brecha": 42.55}, "evidencias": [],
        "explicacion": "Contraste", "pregunta": "¿Qué observar?",
        "evidencia_requerida": "Serie", "limitacion": "Precisión aproximada",
        "robustez": {"presentes": 5, "escenarios": 7, "proporcion": 5 / 7},
    }
    csv_path = tmp_path / "hallazgos.csv"
    fila = {
        k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
        for k, v in ficha.items()
    }

    def escribir(fila):
        with csv_path.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=ficha, lineterminator="\n")
            escritor.writeheader()
            escritor.writerow(fila)

    escribir(fila)
    evaluar_radar.contrastar_csv(csv_path, [ficha])
    fila["magnitudes"] = '{"brecha":42.54}'
    escribir(fila)
    with pytest.raises(ValueError, match=r"R1:2023:04-16.*magnitudes"):
        evaluar_radar.contrastar_csv(csv_path, [ficha])


def test_detecta_deltas_inexactos_en_cualquier_escenario():
    control = evaluar_radar.recalcular(DATOS)
    escenarios = evaluar_radar.tabla_sensibilidad(control)
    next(f for f in escenarios if f["parametro"] == "r4_lq" and f["valor"] == 2)["desaparecen"] = []
    with pytest.raises(ValueError, match=r"R4.*r4_lq.*desaparecen"):
        evaluar_radar.contrastar_sensibilidad(control, escenarios)


def test_orden_y_robustez_exploratorios_contra_fuentes(tmp_path):
    import subprocess
    import sys

    control = evaluar_radar.recalcular(DATOS)
    for (rule, key, value), ordered in control.escenarios.items():
        args = ["--rule", rule, "--output-dir", str(tmp_path)]
        if key is not None:
            args += ["--mode", "exploratory", "--set", f"{key}={value}"]
        subprocess.run([sys.executable, str(DATOS.parent / "scripts/radar.py"), *args], check=True,
                       capture_output=True)
        with (tmp_path / "hallazgos.json").open() as f:
            cards = json.load(f)["hallazgos"]
        assert tuple(card["id"] for card in cards) == ordered
        cases = [ids for (variant, _, _), ids in control.escenarios.items() if variant == rule]
        for card in cards:
            hits = sum(card["id"] in ids for ids in cases)
            assert card["robustez"] == dict(presentes=hits, escenarios=len(cases), proporcion=hits / len(cases))


def test_rechaza_exportaciones_adulteradas(tmp_path):
    import subprocess
    import sys

    run = tmp_path / "run"
    subprocess.run([sys.executable, str(DATOS.parent / "scripts/radar.py"), "--output-dir", str(run)],
                   check=True, capture_output=True)
    result = evaluar_radar.validate(DATOS, run, tmp_path / "report")
    assert result["total"] == 44
    csv_path = run / "hallazgos.csv"
    csv_path.write_text(csv_path.read_text().replace("R3:2023:", "otro:2023:", 1))
    with pytest.raises(ValueError, match="incompatible"):
        evaluar_radar.validate(DATOS, run, tmp_path / "report")
