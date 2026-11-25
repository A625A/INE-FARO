"""Evidencia pública compartida por las reglas de 2023."""
from .inputs import I, P


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


def production(territory, indicator, value, unit, universe):
    return {"territorio": territory, "indicador": indicator, "valor": value, "unidad": unit,
            "fuente": "Banguat, cuadro 7, VAB a precios corrientes 2023", "universo": universe,
            "diagnostico": {"revision": "preliminar"}}


def card(rule, territories, reason, magnitudes, observations, explanation, question, required,
         limitation, group=None):
    identifier = f"{rule}:2023:{'-'.join(territories)}"
    return {
        "id": identifier if group is None else f"{identifier}:{group}",
        "regla": rule, "anio": 2023, "territorios": territories, "grupo": group, "motivo": reason,
        "magnitudes": magnitudes, "evidencias": observations, "explicacion": explanation,
        "pregunta": question, "evidencia_requerida": required,
        "limitacion": limitation + " Las estimaciones puntuales de ENCOVI tienen IC95 y CV "
                                   "aproximados (DEPTO/UPM sin estratos originales).",
    }
