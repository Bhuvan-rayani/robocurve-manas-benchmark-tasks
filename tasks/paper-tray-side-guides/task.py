"""Load the paper block into the feed tray with side guides snug and tray pushed shut."""

from __future__ import annotations

import pathlib
import sys

# Ensure local directory is on path for parts and helper modules
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    COLOR_FRAME_GREY,
    COLOR_GUIDE_GREY,
    COLOR_PAD_GREY,
    COLOR_PAPER_WHITE,
    COLOR_TRAY_SKY_BLUE,
    FRAME_BOXES,
    FRAME_FRICTION,
    FRAME_MASS_KG,
    FRAME_NAME,
    FRAME_POS_WORLD,
    GUIDE_A_AXIS,
    GUIDE_A_BOX,
    GUIDE_A_NAME,
    GUIDE_A_REST_PART,
    GUIDE_B_AXIS,
    GUIDE_B_BOX,
    GUIDE_B_NAME,
    GUIDE_B_REST_PART,
    GUIDE_DAMPING,
    GUIDE_MASS_KG,
    GUIDE_RATE,
    GUIDE_TRAVEL_M,
    PAD_MASS_KG,
    PAD_NAME,
    PAD_POS_WORLD,
    PAD_SIZE_M,
    PAPER_BOXES,
    PAPER_DIMS_M,
    PAPER_FRICTION,
    PAPER_MASS_KG,
    PAPER_NAME,
    PAPER_START_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
    TRAY_BOXES,
    TRAY_FRICTION,
    TRAY_MASS_KG,
    TRAY_NAME,
    TRAY_START_POS_WORLD,
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

# Side guides: two prismatic sliders on feed_tray along Y
SLIDER_GUIDE_A = Slider(
    name=GUIDE_A_NAME,
    rest=GUIDE_A_REST_PART,
    boxes=(GUIDE_A_BOX,),
    travel=GUIDE_TRAVEL_M,
    rate=GUIDE_RATE,
    damping=GUIDE_DAMPING,
    mass=GUIDE_MASS_KG,
    axis=GUIDE_A_AXIS,
)

SLIDER_GUIDE_B = Slider(
    name=GUIDE_B_NAME,
    rest=GUIDE_B_REST_PART,
    boxes=(GUIDE_B_BOX,),
    travel=GUIDE_TRAVEL_M,
    rate=GUIDE_RATE,
    damping=GUIDE_DAMPING,
    mass=GUIDE_MASS_KG,
    axis=GUIDE_B_AXIS,
)

# Feed tray: compound body with side guide sliders
FEED_TRAY_PART = part(
    name=TRAY_NAME,
    pos=TRAY_START_POS_WORLD,
    boxes=TRAY_BOXES,
    mass=TRAY_MASS_KG,
    friction=TRAY_FRICTION,
    sliders=(SLIDER_GUIDE_A, SLIDER_GUIDE_B),
)

# Printer frame: fixed structure with slot
PRINTER_FRAME_PART = part(
    name=FRAME_NAME,
    pos=FRAME_POS_WORLD,
    boxes=FRAME_BOXES,
    mass=FRAME_MASS_KG,
    friction=FRAME_FRICTION,
)

# Paper stack: free rigid compound body with grab handle
PAPER_STACK = part(
    name=PAPER_NAME,
    pos=PAPER_START_POS_WORLD,
    boxes=PAPER_BOXES,
    mass=PAPER_MASS_KG,
    friction=PAPER_FRICTION,
)

# Paper staging pad: fixed surface marker on table
PAPER_PAD = Box(
    name=PAD_NAME,
    pos=PAD_POS_WORLD,
    size=PAD_SIZE_M,
    mass=PAD_MASS_KG,
    color=COLOR_PAD_GREY,
)

OBJECTS = [PRINTER_FRAME_PART, FEED_TRAY_PART, PAPER_STACK, PAPER_PAD]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
