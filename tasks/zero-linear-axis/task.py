"""On the station table: a grey axis base (80 x 240 x 40 mm, 0.6 kg) lies on a very slippery film at x 26 cm, y 0. A silver carriage
(80 x 60 mm body with a square lug 50 mm wide that has a 22 mm hole) slides along +y on the base; a white mark on the carriage starts 40 mm
from the white mark on the base. A yellow lock pin (16 mm dia x 60 mm, 30 g) stands on the table at x 20 cm, y +20 cm.

Run it:  inspect-robots run --embodiment yam_arena -E task=task.py -E object_jitter=0 --scorer task_score ...
"""

from __future__ import annotations

import pathlib
import sys

# Ensure the local task directory is on the path for parts and helpers
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    BASE_BOXES,
    BASE_FRICTION,
    BASE_MASS_KG,
    BASE_NAME,
    BASE_POS_WORLD,
    CARRIAGE_AXIS,
    CARRIAGE_BOXES,
    CARRIAGE_DAMPING,
    CARRIAGE_MASS_KG,
    CARRIAGE_NAME,
    CARRIAGE_REST_PART,
    CARRIAGE_RETURN_SPRING_RATE,
    CARRIAGE_TRAVEL_M,
    COLOR_PIN_YELLOW,
    PIN_FRICTION,
    PIN_HEIGHT_M,
    PIN_MASS_KG,
    PIN_NAME,
    PIN_RADIUS_M,
    PIN_START_XY,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
from parts import Slider, part
import demo_plan
import scoring
import tracekit  # noqa: F401  (debug trace of hands and parts when TASK_TRACE is set)
from yam_arena.task_file import Cylinder

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

# Carriage: a spring-less (rate ~0) damped slider along +Y, so it stays where it is pushed
CARRIAGE_SLIDER = Slider(
    name=CARRIAGE_NAME,
    rest=CARRIAGE_REST_PART,
    boxes=CARRIAGE_BOXES,
    travel=CARRIAGE_TRAVEL_M,
    rate=CARRIAGE_RETURN_SPRING_RATE,
    damping=CARRIAGE_DAMPING,
    mass=CARRIAGE_MASS_KG,
    axis=CARRIAGE_AXIS,
)

# Axis base on a slippery film: loose, so an unheld base slides when the carriage is pushed
BASE_PART = part(
    name=BASE_NAME,
    pos=BASE_POS_WORLD,
    boxes=BASE_BOXES,
    mass=BASE_MASS_KG,
    friction=BASE_FRICTION,
    sliders=(CARRIAGE_SLIDER,),
)

# Lock pin: a loose cylinder standing on the table
LOCK_PIN = Cylinder(
    name=PIN_NAME,
    pos=(PIN_START_XY[0], PIN_START_XY[1], TABLE_TOP + PIN_HEIGHT_M / 2),
    radius=PIN_RADIUS_M,
    height=PIN_HEIGHT_M,
    mass=PIN_MASS_KG,
    color=COLOR_PIN_YELLOW,
)

OBJECTS = [BASE_PART, LOCK_PIN]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
