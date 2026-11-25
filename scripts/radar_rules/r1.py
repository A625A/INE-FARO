"""R1. Contrastes entre parejas con estimaciones puntuales de ocupación próximas."""
from itertools import combinations

from .inputs import I, P

RANK = {"ambos": 0, "solo_pobreza": 1, "solo_pib": 2}
LABELS = {"ambos": "la pobreza total y el PIB por habitante",
          "solo_pobreza": "la pobreza total", "solo_pib": "el PIB por habitante"}


def evidence(d):
    result = []
    for key, universe in ((I, "Personas ocupadas de 15 años o más"),
                          (P, "Personas representadas por hogares con clasificación de consumo válida")):
        est = d.encovi[key]
        result.append({"territorio": d.code, "indicador": key, "valor": est.value,
                       "unidad": "%", "fuente": "INE, ENCOVI 2023", "universo": universe,
                       "diagnostico": {**est.diagnostic, "ic95_inf": est.lower, "ic95_sup": est.upper}})
    result.append({"territorio": d.code, "indicador": "pib_por_habitante",
                   "valor": d.pib_per_capita, "unidad": "Q corrientes por habitante",
                   "fuente": "Banguat, cuadro 8, 2023", "universo": "Población departamental proyectada",
                   "diagnostico": {"elegible": d.pib_per_capita is not None, "revision": "preliminar"}})
    return result


def order(f):
    m = f["magnitudes"]
    p, y = m["brecha_pobreza_pp"], m["razon_pib_por_habitante"]
    return (RANK[f["motivo"]], p is None, -(p or 0), y is None, -(y or 0),
            m["brecha_informalidad_pp"], f["territorios"])


def evaluate(universe, params):
    findings = []
    for a, b in combinations(universe.territories, 2):
        ia, ib = a.encovi[I].value, b.encovi[I].value
        if ia is None or ib is None or abs(ia - ib) > params["r1_i"]:
            continue
        pa, pb = a.encovi[P].value, b.encovi[P].value
        gap = abs(pa - pb) if pa is not None and pb is not None else None
        ya, yb = a.pib_per_capita, b.pib_per_capita
        ratio = None
        qualifies_y = False
        if ya is not None and yb is not None:
            larger, smaller = max(ya, yb), min(ya, yb)
            ratio = larger / smaller
            qualifies_y = larger >= params["r1_y"] * smaller
        qualifies_p = gap is not None and gap >= params["r1_p"]
        if not (qualifies_p or qualifies_y):
            continue
        reason = "ambos" if qualifies_p and qualifies_y else "solo_pobreza" if qualifies_p else "solo_pib"
        findings.append({
            "id": f"R1:2023:{a.code}-{b.code}", "regla": "R1", "anio": 2023,
            "territorios": [a.code, b.code], "grupo": None, "motivo": reason,
            "magnitudes": {"brecha_informalidad_pp": abs(ia - ib), "brecha_pobreza_pp": gap,
                           "razon_pib_por_habitante": ratio},
            "evidencias": evidence(a) + evidence(b),
            "explicacion": f"{a.name} y {b.name} difieren en {abs(ia - ib):.2f} pp de ocupación en el sector "
                           f"informal. El contraste supera o iguala el umbral para {LABELS[reason]}.",
            "pregunta": f"¿Cómo varía {LABELS[reason]} entre territorios con estimaciones puntuales "
                        "próximas de ocupación en el sector informal?",
            "evidencia_requerida": "Desagregaciones comparables por área y composición de los hogares, "
                                   "junto con errores de muestreo del diseño completo.",
            "limitacion": "Comparación descriptiva departamental. La cercanía de las estimaciones puntuales "
                          "no establece equivalencia estadística. Los IC95 y CV de ENCOVI son aproximados "
                          "(DEPTO/UPM sin estratos originales). El PIB por habitante mide producción por persona.",
        })
    return sorted(findings, key=order)
