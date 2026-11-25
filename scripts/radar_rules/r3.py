"""Similitud de la estructura del VAB y contraste laboral."""
from decimal import Decimal
from itertools import combinations

from .evidence import card, evidence, production
from .inputs import I, GROUPS


def evaluate(u, params):
    pairs = [(a, b, sum(abs(a.shares[g] - b.shares[g]) for g in GROUPS) / 2)
             for a, b in combinations(u.territories, 2)]
    if not pairs:
        return []
    distances = sorted(distance for _, _, distance in pairs)
    pos = Decimal(params["r3_percentil"]) * (len(distances) - 1) / 100
    left = int(pos)
    cutoff = distances[left] + (pos-left) * (distances[min(left+1, len(distances)-1)] - distances[left])
    rows = []
    for a, b, distance in pairs:
        ia, ib = a.encovi[I].value, b.encovi[I].value
        if distance > cutoff or ia is None or ib is None or abs(ia-ib) < params["r3_i"]:
            continue
        obs = []
        for d in (a, b):
            obs.extend(item for item in evidence(d) if item["indicador"] == I)
            obs.extend(production(d.code, f"participacion_{g}", d.shares[g], "%",
                                  "VAB departamental de los 17 grupos") for g in GROUPS)
        rows.append(card("R3", [a.code, b.code], "estructura_similar_y_brecha_laboral",
                         {"distancia_pp": distance, "umbral_distancia_pp": cutoff,
                          "brecha_informalidad_pp": abs(ia-ib)}, obs,
                         f"La distancia entre las estructuras productivas de {a.name} y {b.name} "
                         f"es {distance:.2f} pp. Sus tasas de ocupación en el sector informal "
                         f"difieren en {abs(ia-ib):.2f} pp.",
                         "¿Qué diferencias de ocupación por tamaño de unidad se observan entre los departamentos?",
                         "Distribuciones laborales comparables por tamaño y área, con precisión publicada.",
                         "La distancia resume participaciones productivas y la brecha laboral es departamental."))
    return sorted(rows, key=lambda r: (-r["magnitudes"]["brecha_informalidad_pp"],
                                        r["magnitudes"]["distancia_pp"], r["territorios"]))
