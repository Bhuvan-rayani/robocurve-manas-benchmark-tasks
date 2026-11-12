"""Make the open floor hatch safe: cover it with the red plate and secure it with the yellow wedge pins."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    BOARD_BOXES,
    BOARD_FRICTION,
    BOARD_MASS_KG,
    BOARD_POS_WORLD,
    COLOR_COVER_PLATE,
    COLOR_PIN_RACK,
    COLOR_PLATE_STAND,
    COLOR_WEDGE_PIN,
    HANDLE_CENTRE_M,
    HANDLE_DIMS_M,
    LRACK_DIMS_M,
    LRACK_POS_WORLD,
    PIN_A_START_POS,
    PIN_B_START_POS,
    PIN_DIMS_M,
    PIN_MASS_KG,
    PLATE_DIMS_M,
    PLATE_MASS_KG,
    PLATE_START_POS,
    RACK_DIMS_M,
    RACK_MASS_KG,
    RACK_POS_WORLD,
    STAND_DIMS_M,
    STAND_MASS_KG,
    STAND_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
import tracekit  # noqa: F401
from parts import part
import demo_plan
import scoring
from yam_arena.task_file import Box

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

FLOOR_BOARD = part(
    name="floor_board",
    pos=BOARD_POS_WORLD,
    boxes=BOARD_BOXES,
    mass=BOARD_MASS_KG,
    friction=BOARD_FRICTION,
)

# Body origin = plate centre; the 4 x 8 x 2 cm handle sits at the centre of the top face.
COVER_PLATE = part(
    name="cover_plate",
    pos=PLATE_START_POS,
    boxes=[
        ((0.0, 0.0, 0.0), PLATE_DIMS_M, COLOR_COVER_PLATE),
        (HANDLE_CENTRE_M, HANDLE_DIMS_M, COLOR_COVER_PLATE),
    ],
    mass=PLATE_MASS_KG,
    friction=1.2,
    color=COLOR_COVER_PLATE,
)

PLATE_STAND = Box(
    name="plate_stand",
    pos=STAND_POS_WORLD,
    size=STAND_DIMS_M,
    mass=STAND_MASS_KG,
    color=COLOR_PLATE_STAND,
)

WEDGE_PIN_A = Box(
    name="wedge_pin_a",
    pos=PIN_A_START_POS,
    size=PIN_DIMS_M,
    mass=PIN_MASS_KG,
    color=COLOR_WEDGE_PIN,
)

WEDGE_PIN_B = Box(
    name="wedge_pin_b",
    pos=PIN_B_START_POS,
    size=PIN_DIMS_M,
    mass=PIN_MASS_KG,
    color=COLOR_WEDGE_PIN,
)

PIN_RACK = Box(
    name="pin_rack",
    pos=RACK_POS_WORLD,
    size=RACK_DIMS_M,
    mass=RACK_MASS_KG,
    color=COLOR_PIN_RACK,
)

PIN_RACK_LEFT = Box(
    name="pin_rack_left",
    pos=LRACK_POS_WORLD,
    size=LRACK_DIMS_M,
    mass=RACK_MASS_KG,
    color=COLOR_PIN_RACK,
)

OBJECTS = [FLOOR_BOARD, COVER_PLATE, PLATE_STAND, WEDGE_PIN_A, WEDGE_PIN_B, PIN_RACK, PIN_RACK_LEFT]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
