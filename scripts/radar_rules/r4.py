"""Especialización en el VAB corriente del territorio."""
from .evidence import card, evidence, production
from .inputs import I, P, GROUPS


def evaluate(u, params):
    total = sum(d.vab_total for d in u.territories)
    amounts = {g: sum(d.amounts[g] for d in u.territories) for g in GROUPS}
    rows = []
    for d in u.territories:
        i, p = d.encovi[I].value, d.encovi[P].value
        if None in (i, p, u.medians[I], u.medians[P]) or i <= u.medians[I] or p <= u.medians[P]:
            continue
        for g, amount in amounts.items():
            share = d.shares[g]
            if (amount <= 0 or total <= 0 or share < params["r4_s"] or
                    share * total < params["r4_lq"] * 100 * amount):
                continue
            reference = 100 * amount / total
            lq = share * total / (100 * amount)
            obs = [item for item in evidence(d) if item["indicador"] in (I, P)]
            obs.extend((production(d.code, f"participacion_{g}", share, "%", "VAB departamental"),
                        production("22_departamentos", f"participacion_{g}", reference, "%",
                                   "Suma del VAB corriente de los 22 departamentos")))
            rows.append(card("R4", [d.code], "especializacion_sectorial",
                             {"lq": lq, "participacion_local_pct": share, "participacion_agregada_pct": reference,
                              "mediana_i_pct": u.medians[I], "mediana_p_pct": u.medians[P]}, obs,
                             f"El grupo {g} representa {share:.2f} % del VAB de {d.name}, "
                             f"{lq:.2f} veces su participación agregada. Las tasas departamentales "
                             "de pobreza y ocupación en el sector informal superan sus medianas.",
                             f"¿Qué fuentes permiten caracterizar la ocupación en el grupo {g} en {d.name}?",
                             "Estimaciones laborales representativas para el cruce departamento y grupo.",
                             "La especialización mide producción. La tasa laboral departamental no permite "
                             "atribuir informalidad al grupo productivo.", group=g))
    return sorted(rows, key=lambda r: (-r["magnitudes"]["lq"], -r["magnitudes"]["participacion_local_pct"],
                                        r["territorios"], r["grupo"]))
