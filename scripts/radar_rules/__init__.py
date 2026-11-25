"""Registro de evaluadores independientes en orden de publicación."""
from . import r1, r2, r3, r4

RULES = {
    "R1": (r1.evaluate, ("r1_i", "r1_p", "r1_y")),
    "R2a": (r2.evaluate_a, ()),
    "R2b": (r2.evaluate_b, ("r2b_p",)),
    "R3": (r3.evaluate, ("r3_percentil", "r3_i")),
    "R4": (r4.evaluate, ("r4_lq", "r4_s")),
}
