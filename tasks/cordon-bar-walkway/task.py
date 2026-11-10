from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import tracekit  # noqa: F401
from geometry import (
    BAR_BOXES,
    BAR_FRICTION,
    BAR_MASS_KG,
    BAR_NAME,
    BAR_PAD_BOXES,
    BAR_PAD_FRICTION,
    BAR_PAD_MASS_KG,
    BAR_PAD_NAME,
    BAR_PAD_POS_WORLD,
    BAR_START_POS,
    POST_A_FRICTION,
    POST_A_MASS_KG,
    POST_A_NAME,
    POST_A_POS_WORLD,
    POST_B_FRICTION,
    POST_B_MASS_KG,
    POST_B_NAME,
    POST_B_POS_WORLD,
    POST_BOXES,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
from parts import part
import demo_plan
import scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

POST_A = part(
    name=POST_A_NAME,
    pos=POST_A_POS_WORLD,
    boxes=POST_BOXES,
    mass=POST_A_MASS_KG,
    friction=POST_A_FRICTION,
)

POST_B = part(
    name=POST_B_NAME,
    pos=POST_B_POS_WORLD,
    boxes=POST_BOXES,
    mass=POST_B_MASS_KG,
    friction=POST_B_FRICTION,
)

BAR_PAD = part(
    name=BAR_PAD_NAME,
    pos=BAR_PAD_POS_WORLD,
    boxes=BAR_PAD_BOXES,
    mass=BAR_PAD_MASS_KG,
    friction=BAR_PAD_FRICTION,
)

CORDON_BAR = part(
    name=BAR_NAME,
    pos=BAR_START_POS,
    boxes=BAR_BOXES,
    mass=BAR_MASS_KG,
    friction=BAR_FRICTION,
)

OBJECTS = [POST_A, POST_B, BAR_PAD, CORDON_BAR]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans

# Aliases for backward compatibility
SCORER = score
SUCCESS = success
DEMO_PLANS = demo
DEMO_PLAN = demo
