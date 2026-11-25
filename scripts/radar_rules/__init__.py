"""Registro de evaluadores independientes en orden de publicación."""
from . import r1

RULES = {
    "R1": (r1.evaluate, ("r1_i", "r1_p", "r1_y")),
}
