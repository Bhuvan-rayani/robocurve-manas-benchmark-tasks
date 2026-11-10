"""Set address switches on the violet module to match the dot pattern and press commit."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    BUTTON_DAMPING,
    BUTTON_HEIGHT_M,
    BUTTON_MASS_KG,
    BUTTON_NAME,
    BUTTON_RADIUS_M,
    BUTTON_RATE,
    BUTTON_REST_PART,
    BUTTON_TRAVEL_M,
    CARD_MASS_KG,
    CARD_POS_WORLD,
    CARD_SIZE_M,
    COLOR_BUTTON_LIME,
    COLOR_CARD_WHITE,
    COLOR_KNOB_BLUE,
    COLOR_DOT_DOWN,
    COLOR_DOT_UP,
    CARD_DOT_SIZE_M,
    CARD_DOT_Y,
    TARGET_PATTERN,
    KNOB_AXES,
    KNOB_DAMPING,
    KNOB_DIMS_M,
    KNOB_MASS_KG,
    KNOB_NAMES,
    KNOB_RATE,
    KNOB_REST_X,
    KNOB_REST_Z,
    KNOB_TRAVEL_M,
    KNOB_Y_COORDS,
    MODULE_BOXES,
    MODULE_FRICTION,
    MODULE_MASS_KG,
    MODULE_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
import tracekit  # noqa: F401
from parts import Slider, part
import demo_plan
import scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"


def _make_knob(name: str, y_coord: float, axis: str) -> Slider:
    rest = (KNOB_REST_X, y_coord, KNOB_REST_Z)
    box_spec = ((KNOB_REST_X, y_coord, KNOB_REST_Z + KNOB_DIMS_M[2] / 2), KNOB_DIMS_M, COLOR_KNOB_BLUE)
    return Slider(
        name=name,
        rest=rest,
        boxes=(box_spec,),
        travel=KNOB_TRAVEL_M,
        rate=KNOB_RATE,
        damping=KNOB_DAMPING,
        mass=KNOB_MASS_KG,
        axis=axis,
    )


def _make_button() -> Slider:
    btn_box = (
        (BUTTON_REST_PART[0], BUTTON_REST_PART[1], BUTTON_REST_PART[2] + BUTTON_HEIGHT_M / 2),
        (BUTTON_RADIUS_M * 1.4, BUTTON_RADIUS_M * 1.4, BUTTON_HEIGHT_M),
        COLOR_BUTTON_LIME,
    )
    cyl_spec = (
        (BUTTON_REST_PART[0], BUTTON_REST_PART[1], BUTTON_REST_PART[2] + BUTTON_HEIGHT_M / 2),
        BUTTON_RADIUS_M,
        BUTTON_HEIGHT_M,
        COLOR_BUTTON_LIME,
        "Z",
    )
    return Slider(
        name=BUTTON_NAME,
        rest=BUTTON_REST_PART,
        boxes=(btn_box,),
        cylinders=(cyl_spec,),
        travel=BUTTON_TRAVEL_M,
        rate=BUTTON_RATE,
        damping=BUTTON_DAMPING,
        mass=BUTTON_MASS_KG,
        axis="Z",
    )


_SLIDERS = (
    _make_knob(KNOB_NAMES[0], KNOB_Y_COORDS[0], KNOB_AXES[0]),
    _make_knob(KNOB_NAMES[1], KNOB_Y_COORDS[1], KNOB_AXES[1]),
    _make_knob(KNOB_NAMES[2], KNOB_Y_COORDS[2], KNOB_AXES[2]),
    _make_knob(KNOB_NAMES[3], KNOB_Y_COORDS[3], KNOB_AXES[3]),
    _make_button(),
)

MODULE_PART = part(
    name="addr_module",
    pos=MODULE_POS_WORLD,
    boxes=MODULE_BOXES,
    mass=MODULE_MASS_KG,
    friction=MODULE_FRICTION,
    sliders=_SLIDERS,
)

_CARD_BOXES = ((((0.0, 0.0, CARD_SIZE_M[2] / 2), CARD_SIZE_M, COLOR_CARD_WHITE),)
               + tuple(((0.0, y, CARD_SIZE_M[2] + 0.0005), (CARD_DOT_SIZE_M, CARD_DOT_SIZE_M, 0.001),
                        COLOR_DOT_UP if bit else COLOR_DOT_DOWN) for y, bit in zip(CARD_DOT_Y, TARGET_PATTERN)))
DOT_CARD = part(
    name="dot_card",
    pos=(CARD_POS_WORLD[0], CARD_POS_WORLD[1], TABLE_TOP),
    boxes=_CARD_BOXES,
    mass=CARD_MASS_KG,
    friction=1.0,
)

OBJECTS = [MODULE_PART, DOT_CARD]
DISTANCE = scoring.distance

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans

# Aliases for backward compatibility
SCORER = score
SUCCESS = success
DEMO_PLANS = demo
DEMO_PLAN = demo
