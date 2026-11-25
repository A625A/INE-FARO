"""Desacoples departamentales de PIB por habitante, ocupación y pobreza."""
from .evidence import card, evidence
from .inputs import I, P


def above_median_y(u):
    reference = u.medians["pib_por_habitante"]
    for d in u.territories:
        if reference is not None and d.pib_per_capita is not None and d.pib_per_capita > reference:
            yield d, d.pib_per_capita - reference


def ranked(rows, primary):
    return sorted(rows, key=lambda r: (-r["magnitudes"][primary], -r["magnitudes"]["exceso_y_q"],
                                        r["territorios"]))


def evaluate_a(u, params):
    rows = []
    for d, excess_y in above_median_y(u):
        i, median_i = d.encovi[I].value, u.medians[I]
        if i is None or median_i is None or i <= median_i:
            continue
        rows.append(card("R2a", [d.code], "pib_e_informalidad_sobre_medianas",
                         {"exceso_i_pp": i - median_i, "exceso_y_q": excess_y,
                          "mediana_i_pct": median_i, "mediana_y_q": u.medians["pib_por_habitante"]},
                         evidence(d), f"En {d.name} tanto el PIB por habitante como la ocupación en el "
                         "sector informal superan sus respectivas medianas departamentales.",
                         "¿Cómo se distribuyen la producción y la ocupación entre áreas del departamento?",
                         "Datos comparables de producción y ocupación por área y actividad.",
                         "El PIB por habitante mide producción. Los agregados describen el departamento."))
    return ranked(rows, "exceso_i_pp")


def evaluate_b(u, params):
    national = u.national_informality
    rows = []
    for d, excess_y in above_median_y(u):
        i, p, median_p = d.encovi[I].value, d.encovi[P].value, u.medians[P]
        if (None in (i, p, median_p, national.value) or i < national.value
                or p - median_p < params["r2b_p"]):
            continue
        obs = evidence(d) + [{"territorio": "nacional", "indicador": I, "valor": national.value,
                              "unidad": "%", "fuente": "INE, ENCOVI 2023",
                              "universo": "Personas ocupadas de 15 años o más",
                              "diagnostico": {**national.diagnostic, "ic95_inf": national.lower,
                                              "ic95_sup": national.upper}}]
        rows.append(card("R2b", [d.code], "pib_pobreza_e_informalidad",
                         {"exceso_p_pp": p - median_p, "exceso_y_q": excess_y,
                          "mediana_p_pct": median_p, "mediana_y_q": u.medians["pib_por_habitante"],
                          "informalidad_nacional_pct": national.value}, obs,
                         f"{d.name} supera la mediana de PIB por habitante. Su pobreza total excede "
                         f"la mediana en {p-median_p:.2f} pp y la ocupación en el sector informal "
                         "alcanza o supera la referencia nacional ponderada.",
                         "¿Cómo varía el consumo de los hogares entre áreas del departamento?",
                         "Distribución territorial del consumo de hogares y precisión por área.",
                         "El PIB por habitante mide producción territorial y la pobreza se estima por consumo."))
    return ranked(rows, "exceso_p_pp")
