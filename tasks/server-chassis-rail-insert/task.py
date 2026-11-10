"""Slide the silver server chassis into the rack until its front ears are flush with the posts."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    CHASSIS_BOXES,
    CHASSIS_FRICTION,
    CHASSIS_MASS_KG,
    CHASSIS_START_POS,
    COLOR_PLATE_GREY,
    COLOR_POST_TEAL,
    COLOR_RAIL_STEEL,
    PLATE_DIMS_M,
    PLATE_POS_WORLD,
    POST_A_POS_WORLD,
    POST_B_POS_WORLD,
    POST_DIMS_M,
    RAIL_A_LEDGE_POS,
    RAIL_A_LEDGE_SIZE,
    RAIL_A_WALL_POS,
    RAIL_A_WALL_SIZE,
    RAIL_B_LEDGE_POS,
    RAIL_B_LEDGE_SIZE,
    RAIL_B_WALL_POS,
    RAIL_B_WALL_SIZE,
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

# Fixed rack posts
RACK_POST_A = Box(
    name="rack_post_a",
    pos=POST_A_POS_WORLD,
    size=POST_DIMS_M,
    color=COLOR_POST_TEAL,
    mass=None,
)

RACK_POST_B = Box(
    name="rack_post_b",
    pos=POST_B_POS_WORLD,
    size=POST_DIMS_M,
    color=COLOR_POST_TEAL,
    mass=None,
)

# Fixed staging plate
STAGING_PLATE = Box(
    name="staging_plate",
    pos=PLATE_POS_WORLD,
    size=PLATE_DIMS_M,
    color=COLOR_PLATE_GREY,
    mass=None,
)

# Fixed rack rails (guide walls and bottom support ledges)
RACK_RAIL_A = Box(
    name="rack_rail_a",
    pos=RAIL_A_WALL_POS,
    size=RAIL_A_WALL_SIZE,
    color=COLOR_RAIL_STEEL,
    mass=None,
)

RACK_RAIL_A_LEDGE = Box(
    name="rack_rail_a_ledge",
    pos=RAIL_A_LEDGE_POS,
    size=RAIL_A_LEDGE_SIZE,
    color=COLOR_RAIL_STEEL,
    mass=None,
)

RACK_RAIL_B = Box(
    name="rack_rail_b",
    pos=RAIL_B_WALL_POS,
    size=RAIL_B_WALL_SIZE,
    color=COLOR_RAIL_STEEL,
    mass=None,
)

RACK_RAIL_B_LEDGE = Box(
    name="rack_rail_b_ledge",
    pos=RAIL_B_LEDGE_POS,
    size=RAIL_B_LEDGE_SIZE,
    color=COLOR_RAIL_STEEL,
    mass=None,
)

# Loose compound server chassis (main body + two front ear tabs)
CHASSIS_BOX = part(
    name="chassis_box",
    pos=CHASSIS_START_POS,
    boxes=CHASSIS_BOXES,
    mass=CHASSIS_MASS_KG,
    friction=CHASSIS_FRICTION,
)

OBJECTS = [
    RACK_POST_A,
    RACK_POST_B,
    STAGING_PLATE,
    RACK_RAIL_A,
    RACK_RAIL_A_LEDGE,
    RACK_RAIL_B,
    RACK_RAIL_B_LEDGE,
    CHASSIS_BOX,
]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
