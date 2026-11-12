"""Slide a hot air-fryer basket out from under its two retaining hooks by the handle, lift it and set it on the heat-proof mat."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    BASKET_FLANGES,
    BASKET_FLOOR,
    BASKET_FRICTION,
    BASKET_HANDLE_BAR,
    BASKET_HANDLE_POSTS,
    BASKET_MASS_KG,
    BASKET_NAME,
    BASKET_START,
    BASKET_WALLS,
    COLOR_BASKET,
    COLOR_HANDLE,
    COLOR_HOUSING,
    COLOR_LAMP,
    COLOR_MAT,
    COLOR_PLATE,
    HOOKS,
    HOUSING_CENTRE_XY,
    HOUSING_NAME,
    HOUSING_SIZE,
    LAMP_FRONT,
    LAMP_TOP,
    MAT_CENTRE_XY,
    MAT_NAME,
    MAT_SIZE,
    PLATE_BASE,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
import tracekit  # noqa: F401
from parts import part
from yam_arena.task_file import Box
import demo_plan
import scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"


def _fixed(name, centre, size, colour):
    return Box(name=name, pos=(centre[0], centre[1], TOP + centre[2]), size=size, color=colour, mass=None)


HOUSING = _fixed(HOUSING_NAME, (HOUSING_CENTRE_XY[0], HOUSING_CENTRE_XY[1], HOUSING_SIZE[2] / 2), HOUSING_SIZE, COLOR_HOUSING)
LAMPS = [_fixed(n, c, s, COLOR_LAMP) for n, c, s in (LAMP_FRONT, LAMP_TOP)]
PLATE = _fixed(PLATE_BASE[0], PLATE_BASE[1], PLATE_BASE[2], COLOR_PLATE)
HOOK_BOXES = [_fixed(n, c, s, COLOR_PLATE) for n, c, s in HOOKS]
MAT = _fixed(MAT_NAME, (MAT_CENTRE_XY[0], MAT_CENTRE_XY[1], MAT_SIZE[2] / 2), MAT_SIZE, COLOR_MAT)

BASKET = part(
    BASKET_NAME,
    (BASKET_START[0], BASKET_START[1], TOP + BASKET_START[2]),
    boxes=[(BASKET_FLOOR[0], BASKET_FLOOR[1], COLOR_BASKET)]
    + [(c, s, COLOR_BASKET) for c, s in BASKET_WALLS]
    + [(c, s, COLOR_BASKET) for c, s in BASKET_FLANGES]
    + [(c, s, COLOR_HANDLE) for c, s in BASKET_HANDLE_POSTS]
    + [(BASKET_HANDLE_BAR[0], BASKET_HANDLE_BAR[1], COLOR_HANDLE)],
    mass=BASKET_MASS_KG,
    friction=BASKET_FRICTION,
)

OBJECTS = [HOUSING, *LAMPS, PLATE, *HOOK_BOXES, MAT, BASKET]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
