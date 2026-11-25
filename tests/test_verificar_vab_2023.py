import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verificar_vab_2023.py"


@pytest.fixture
def datos(tmp_path):
    (tmp_path / "vab_informal_nacional.csv").write_text(
        "anio,tipo_precio,vab_informal,vab_total,participacion_informal_pct\n"
        "2023,corrientes,172538.678503,762881.363889,22.616711676\n",
        encoding="utf-8",
    )
    (tmp_path / "vab_informal_grupo.csv").write_text(
        "anio,tipo_precio,grupo_ciiu,vab_informal,composicion_pct\n"
        "2023,corrientes,G,66519.796145,38.553556062\n",
        encoding="utf-8",
    )
    return tmp_path


def ejecutar(datos, *opciones):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--datos", str(datos), *map(str, opciones)],
        cwd=datos, capture_output=True, text=True,
    )


def test_recalcula_cuatro_controles_desde_las_celdas_publicadas(datos):
    proceso = ejecutar(datos)
    assert proceso.returncode == 0, proceso.stderr
    evidencia = json.loads(proceso.stdout)
    assert evidencia["controles_redondeados"] == {
        "vab_informal": "172538.68",
        "vab_total": "762881.36",
        "participacion_informal_pct": "22.62",
        "composicion_comercio_pct": "38.55",
    }
    assert evidencia["celdas"]["composicion_publicada_comercio_pct"] == "12.1!O42"
    assert evidencia["errores"] == []
