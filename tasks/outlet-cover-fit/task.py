"""Press a red safety cap into each of the three empty sockets of the wall plate."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    CAP_A_NAME,
    CAP_A_START_POS_WORLD,
    CAP_B_NAME,
    CAP_B_START_POS_WORLD,
    CAP_C_NAME,
    CAP_C_START_POS_WORLD,
    CAP_HEIGHT_M,
    CAP_MASS_KG,
    CAP_RADIUS_M,
    COLOR_CAP,
    PLATE_FRICTION,
    PLATE_MASS_KG,
    PLATE_NAME,
    PLATE_START_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
    WALL_PLATE_BOXES,
)
import tracekit  # noqa: F401
from parts import part
import demo_plan
import scoring
from yam_arena.task_file import Cylinder

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

# Wall plate: compound PLA body with 19 boxes forming 3 socket wells
WALL_PLATE = part(
    name=PLATE_NAME,
    pos=PLATE_START_POS_WORLD,
    boxes=WALL_PLATE_BOXES,
    mass=PLATE_MASS_KG,
    friction=PLATE_FRICTION,
)

# Three red safety caps (loose cylindrical rigid bodies)
CAP_A = Cylinder(
    name=CAP_A_NAME,
    pos=CAP_A_START_POS_WORLD,
    radius=CAP_RADIUS_M,
    height=CAP_HEIGHT_M,
    mass=CAP_MASS_KG,
    color=COLOR_CAP,
)

CAP_B = Cylinder(
    name=CAP_B_NAME,
    pos=CAP_B_START_POS_WORLD,
    radius=CAP_RADIUS_M,
    height=CAP_HEIGHT_M,
    mass=CAP_MASS_KG,
    color=COLOR_CAP,
)

CAP_C = Cylinder(
    name=CAP_C_NAME,
    pos=CAP_C_START_POS_WORLD,
    radius=CAP_RADIUS_M,
    height=CAP_HEIGHT_M,
    mass=CAP_MASS_KG,
    color=COLOR_CAP,
)

OBJECTS = [WALL_PLATE, CAP_A, CAP_B, CAP_C]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
