from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path

import pytest

from scripts.radar_rules import RULES
from scripts.radar_rules.inputs import I, P, GROUPS, load_inputs


@pytest.fixture
def universe():
    return load_inputs(Path(__file__).resolve().parents[1] / "data")


def territory(d, i, p, y):
    encovi = dict(d.encovi)
    for ind, val in ((I, i), (P, p)):
        encovi[ind] = replace(encovi[ind], value=val)
    return replace(d, encovi=encovi, pib_per_capita=y)


@pytest.mark.parametrize("rule,i,p,y,expected", [
    ("R2a", 51, None, 101, True), ("R2a", 50, 99, 101, False),
    ("R2a", 51, 99, 100, False), ("R2a", None, 99, 101, False),
    ("R2b", 60, 65, 101, True), ("R2b", 59, 65, 101, False),
    ("R2b", 60, 64, 101, False), ("R2b", 60, 65, 100, False),
])
def test_r2_seleccion_y_desempate(universe, rule, i, p, y, expected):
    u = replace(universe, medians={I: 50, P: 50, "pib_por_habitante": 100},
                national_informality=replace(universe.national_informality, value=60),
                territories=tuple(territory(d, i, p, y) for d in universe.territories[:2]))
    cards = RULES[rule][0](u, {"r2b_p": 15})
    assert [c["territorios"] for c in cards] == ([["01"], ["02"]] if expected else [])


def test_r3_percentil_incluye_pares_con_i_restringida(universe):
    # Distancias 10, 20 y 30; P25 lineal = 15. Solo la pareja 01-02 tiene dos tasas.
    ds = []
    for d, share, i in zip(universe.territories, (0, 10, 30), (20, 30, None)):
        shares = dict.fromkeys(GROUPS, D(0))
        shares.update(A=D(share), B=D(100-share))
        ds.append(replace(territory(d, i, None, None), shares=shares))
    u = replace(universe, territories=tuple(ds))
    for percentile, cutoff in ((25, 15), (0, 10)):
        cards = RULES["R3"][0](u, {"r3_percentil": percentile, "r3_i": 10})
        assert [r["id"] for r in cards] == ["R3:2023:01-02"]
        assert cards[0]["magnitudes"]["umbral_distancia_pp"] == cutoff


@pytest.mark.parametrize("i,p,min_lq,min_share,selected", [
    (51, 51, 2, 10, True), (50, 51, 2, 10, False), (51, 50, 2, 10, False),
    (51, 51, D("2.000001"), 10, False), (51, 51, 2, D("10.000001"), False),
    (None, 51, 2, 10, False),
])
def test_r4_igualdades_y_denominador_cero(universe, i, p, min_lq, min_share, selected):
    ds = []
    for d, local, rate in zip(universe.territories, (10, 0), (i, 0)):
        shares = dict.fromkeys(GROUPS, D(0))
        shares.update(A=D(local), B=D(100-local))
        ds.append(replace(territory(d, rate, p, 100), shares=shares, amounts=shares, vab_total=D(100)))
    u = replace(universe, territories=tuple(ds), medians={I: 50, P: 50})
    cards = RULES["R4"][0](u, {"r4_lq": min_lq, "r4_s": min_share})
    assert [r["id"] for r in cards] == (["R4:2023:01:A"] if selected else [])
