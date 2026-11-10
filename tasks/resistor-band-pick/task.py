"""Pick the resistor marked brown, black, red from the tray and seat it in the socket while holding the socket cover aside."""

from __future__ import annotations

import pathlib
import sys

# Ensure local task directory is on path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    BAND_HEIGHT_M,
    BAND_RADIUS_M,
    BAND_Z_M,
    RES_BANDS,
    BOARD_BOXES,
    BOARD_FRICTION,
    BOARD_MASS_KG,
    BOARD_POS_WORLD,
    CARD_DIMS_M,
    CARD_MASS_KG,
    CARD_POS_WORLD,
    COLOR_CARD_WHITE,
    COLOR_RES_BEIGE,
    COVER_AXIS,
    COVER_BOXES,
    COVER_DAMPING,
    COVER_MASS_KG,
    COVER_NAME,
    COVER_REST_PART,
    COVER_SPRING_RATE,
    COVER_TRAVEL_M,
    RES_HEIGHT_M,
    RES_MASS_KG,
    RES_NAMES,
    RES_RADIUS_M,
    RES_START_POSITIONS,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
    TRAY_BOXES,
    TRAY_FRICTION,
    TRAY_MASS_KG,
    TRAY_POS_WORLD,
)
import tracekit  # noqa: F401
from parts import Slider, part
import demo_plan
import scoring
from yam_arena.task_file import Box, Cylinder

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

# Socket cover slider on the socket board
COVER_SLIDER = Slider(
    name=COVER_NAME,
    rest=COVER_REST_PART,
    boxes=COVER_BOXES,
    travel=COVER_TRAVEL_M,
    rate=COVER_SPRING_RATE,
    damping=COVER_DAMPING,
    mass=COVER_MASS_KG,
    axis=COVER_AXIS,
)

# Socket board compound part with spring slider
SOCKET_BOARD_PART = part(
    name="socket_board",
    pos=BOARD_POS_WORLD,
    boxes=BOARD_BOXES,
    mass=BOARD_MASS_KG,
    friction=BOARD_FRICTION,
    sliders=(COVER_SLIDER,),
)

# Part tray compound part
PART_TRAY_PART = part(
    name="part_tray",
    pos=TRAY_POS_WORLD,
    boxes=TRAY_BOXES,
    mass=TRAY_MASS_KG,
    friction=TRAY_FRICTION,
)

# Six upright resistors in tray pockets
RESISTORS = [
    part(
        name=name,
        pos=RES_START_POSITIONS[name],   # body origin = resistor centre
        boxes=[((0.0, 0.0, 0.0), (0.002, 0.002, 0.002), COLOR_RES_BEIGE)],
        cylinders=[((0.0, 0.0, 0.0), RES_RADIUS_M, RES_HEIGHT_M, COLOR_RES_BEIGE, "Z")]
        + [((0.0, 0.0, bz), BAND_RADIUS_M, BAND_HEIGHT_M, bc, "Z") for bz, bc in zip(BAND_Z_M, RES_BANDS[name])],
        mass=RES_MASS_KG,
        friction=1.2,
    )
    for name in RES_NAMES
]

# Reference colour-code card
COLOUR_CARD = Box(
    name="colour_card",
    pos=CARD_POS_WORLD,
    size=CARD_DIMS_M,
    mass=CARD_MASS_KG,
    color=COLOR_CARD_WHITE,
)

OBJECTS = [PART_TRAY_PART, SOCKET_BOARD_PART, *RESISTORS, COLOUR_CARD]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
