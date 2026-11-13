"""Reload a receipt printer: hold its sprung cover back, turn the new paper roll so the paper feeds out of the front slot, seat it, let the cover close."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    COVER_BOXES,
    COVER_DAMPING,
    COVER_MASS_KG,
    COVER_NAME,
    COVER_REST,
    COVER_SPRING_N_PER_M,
    COVER_TRAVEL_M,
    PRINTER_BOXES,
    PRINTER_FRICTION,
    PRINTER_MASS_KG,
    PRINTER_NAME,
    PRINTER_XY,
    ROLL_CORE,
    ROLL_CYL,
    ROLL_FRICTION,
    PAPER_ROLL_MASS_KG,
    ROLL_NAME,
    ROLL_START_ORIGIN_Z,
    ROLL_START_XY,
    ROLL_START_YAW,
    ROLL_TAIL,
    STAND_CHOCK,
    STAND_FRICTION,
    STAND_MASS_KG,
    STAND_NAME,
    STAND_PLATE,
    STAND_XY,
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

# The cover (plate, grip ribs, window, side arm and blue tab) is ONE slide along +x carried by the printer part; its joint
# position is 0 at rest and positive when pushed back toward +x.
COVER = Slider(
    COVER_NAME,
    rest=COVER_REST,
    boxes=list(COVER_BOXES),
    travel=COVER_TRAVEL_M,
    rate=COVER_SPRING_N_PER_M,
    damping=COVER_DAMPING,
    mass=COVER_MASS_KG,
    axis="+X",
)

PRINTER = part(
    PRINTER_NAME,
    (PRINTER_XY[0], PRINTER_XY[1], TOP),
    boxes=list(PRINTER_BOXES),
    sliders=[COVER],
    mass=PRINTER_MASS_KG,
    friction=PRINTER_FRICTION,
)

# The roll: cylinder along the part's y plus the paper tail along its +x. A cylinder needs a box in the same part (parts.py).
ROLL = part(
    ROLL_NAME,
    (ROLL_START_XY[0], ROLL_START_XY[1], TOP + ROLL_START_ORIGIN_Z),
    boxes=[ROLL_TAIL],
    cylinders=[ROLL_CYL, ROLL_CORE],
    mass=PAPER_ROLL_MASS_KG,
    yaw=ROLL_START_YAW,
    friction=ROLL_FRICTION,
)

STAND = part(
    STAND_NAME,
    (STAND_XY[0], STAND_XY[1], TOP),
    boxes=[STAND_PLATE, STAND_CHOCK],
    mass=STAND_MASS_KG,
    friction=STAND_FRICTION,
)

OBJECTS = [PRINTER, ROLL, STAND]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
