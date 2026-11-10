"""Stair nosing strip anti-slip installation task."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    NOSING_STRIP_BOXES,
    NOSING_STRIP_FRICTION,
    NOSING_STRIP_MASS_KG,
    NOSING_STRIP_NAME,
    NOSING_STRIP_START_POS_WORLD,
    STAIR_STEP_BOXES,
    STAIR_STEP_FRICTION,
    STAIR_STEP_MASS_KG,
    STAIR_STEP_NAME,
    STAIR_STEP_POS_WORLD,
    STRIP_PAD_BOXES,
    STRIP_PAD_FRICTION,
    STRIP_PAD_MASS_KG,
    STRIP_PAD_NAME,
    STRIP_PAD_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
import tracekit  # noqa: F401
from parts import part
import demo_plan
import scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

# Fixed reaction base: concrete step section (140x400x60 mm, 25 kg)
STAIR_STEP = part(
    name=STAIR_STEP_NAME,
    pos=STAIR_STEP_POS_WORLD,
    boxes=STAIR_STEP_BOXES,
    mass=STAIR_STEP_MASS_KG,
    friction=STAIR_STEP_FRICTION,
)

# Fixed staging pad for the strip (60x440x10 mm, 25 kg)
STRIP_PAD = part(
    name=STRIP_PAD_NAME,
    pos=STRIP_PAD_POS_WORLD,
    boxes=STRIP_PAD_BOXES,
    mass=STRIP_PAD_MASS_KG,
    friction=STRIP_PAD_FRICTION,
)

# Loose L-profile yellow nosing strip (40x380x40 mm, 0.15 kg)
NOSING_STRIP = part(
    name=NOSING_STRIP_NAME,
    pos=NOSING_STRIP_START_POS_WORLD,
    boxes=NOSING_STRIP_BOXES,
    mass=NOSING_STRIP_MASS_KG,
    friction=NOSING_STRIP_FRICTION,
)

OBJECTS = [STAIR_STEP, STRIP_PAD, NOSING_STRIP]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
