"""Carry the green pipe and lay it in both wooden V stands."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    PIPE_BOXES,
    PIPE_CYLINDERS,
    PIPE_FRICTION,
    PIPE_MASS_KG,
    PIPE_NAME,
    PIPE_PAD_BOXES,
    PIPE_PAD_FRICTION,
    PIPE_PAD_MASS_KG,
    PIPE_PAD_NAME,
    PIPE_PAD_POS_WORLD,
    PIPE_START_POS,
    STAND_A_BOXES,
    STAND_A_FRICTION,
    STAND_A_MASS_KG,
    STAND_A_NAME,
    STAND_A_POS_WORLD,
    STAND_B_BOXES,
    STAND_B_FRICTION,
    STAND_B_MASS_KG,
    STAND_B_NAME,
    STAND_B_POS_WORLD,
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

# Fixed heavy wooden V stands (25 kg each, 42 cm apart at y = +/-0.21 m)
STAND_A = part(
    name=STAND_A_NAME,
    pos=STAND_A_POS_WORLD,
    boxes=STAND_A_BOXES,
    mass=STAND_A_MASS_KG,
    friction=STAND_A_FRICTION,
)

STAND_B = part(
    name=STAND_B_NAME,
    pos=STAND_B_POS_WORLD,
    boxes=STAND_B_BOXES,
    mass=STAND_B_MASS_KG,
    friction=STAND_B_FRICTION,
)

# Fixed staging pad for the pipe
PIPE_PAD = part(
    name=PIPE_PAD_NAME,
    pos=PIPE_PAD_POS_WORLD,
    boxes=PIPE_PAD_BOXES,
    mass=PIPE_PAD_MASS_KG,
    friction=PIPE_PAD_FRICTION,
)

# Loose green pipe (60 cm long x 6 cm dia, 1.0 kg)
PIPE = part(
    name=PIPE_NAME,
    pos=PIPE_START_POS,
    boxes=PIPE_BOXES,
    cylinders=PIPE_CYLINDERS,
    mass=PIPE_MASS_KG,
    friction=PIPE_FRICTION,
)

OBJECTS = [STAND_A, STAND_B, PIPE_PAD, PIPE]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
