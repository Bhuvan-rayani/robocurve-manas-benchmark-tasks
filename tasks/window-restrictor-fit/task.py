"""Fit the cyan stop block so the window sash cannot open more than 100 mm, and open the sash as far as it will go."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    BLOCK_BOXES,
    BLOCK_CYLINDERS,
    BLOCK_FRICTION,
    BLOCK_MASS_KG,
    BLOCK_NAME,
    BLOCK_START_POS_WORLD,
    COLOR_PAD_GREY,
    FRAME_BOXES,
    FRAME_FRICTION,
    FRAME_MASS_KG,
    FRAME_POS_WORLD,
    PAD_NAME,
    PAD_POS_WORLD,
    PAD_SIZE_M,
    SASH_AXIS,
    SASH_BOXES,
    SASH_DAMPING,
    SASH_MASS_KG,
    SASH_NAME,
    SASH_REST_PART,
    SASH_SPRING_RATE,
    SASH_TRAVEL_M,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
import tracekit  # noqa: F401
from parts import Slider, part
import demo_plan
import scoring
from yam_arena.task_file import Box

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

# Prismatic sash slider inside window_frame track
SASH_SLIDER = Slider(
    name=SASH_NAME,
    rest=SASH_REST_PART,
    boxes=SASH_BOXES,
    travel=SASH_TRAVEL_M,
    rate=SASH_SPRING_RATE,
    damping=SASH_DAMPING,
    mass=SASH_MASS_KG,
    axis=SASH_AXIS,
)

WINDOW_FRAME = part(
    name="window_frame",
    pos=FRAME_POS_WORLD,
    boxes=FRAME_BOXES,
    mass=FRAME_MASS_KG,
    friction=FRAME_FRICTION,
    sliders=(SASH_SLIDER,),
)

STOP_BLOCK = part(
    name=BLOCK_NAME,
    pos=BLOCK_START_POS_WORLD,
    boxes=BLOCK_BOXES,
    cylinders=BLOCK_CYLINDERS,
    mass=BLOCK_MASS_KG,
    friction=BLOCK_FRICTION,
)

STOP_PAD = Box(
    name=PAD_NAME,
    pos=PAD_POS_WORLD,
    size=PAD_SIZE_M,
    color=COLOR_PAD_GREY,
)

OBJECTS = [WINDOW_FRAME, STOP_BLOCK, STOP_PAD]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
