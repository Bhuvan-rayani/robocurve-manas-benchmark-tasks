from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tracekit  # noqa: F401
from geometry import (
    COLOR_PIN,
    COLOR_WHEEL,
    WHEEL_BOXES,
    PIN_BOXES,
    HOLDER_BOXES,
    HOLDER_NAME,
    HOLDER_POS_WORLD,
    PAD_BOXES,
    PAD_NAME,
    PAD_POS_WORLD,
    PIN_FRICTION,
    PIN_MASS_KG,
    PIN_NAME,
    PIN_START_POS,
    STAND_BOXES,
    STAND_CYLINDERS,
    STAND_FRICTION,
    STAND_MASS_KG,
    STAND_NAME,
    STAND_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
    WHEEL_FRICTION,
    WHEEL_MASS_KG,
    WHEEL_NAME,
    WHEEL_START_POS,
)
from parts import part
import demo_plan, scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

STAND = part(STAND_NAME, STAND_POS_WORLD, boxes=STAND_BOXES, cylinders=STAND_CYLINDERS, mass=STAND_MASS_KG, friction=STAND_FRICTION)
PAD = part(PAD_NAME, PAD_POS_WORLD, boxes=PAD_BOXES, mass=5.0, friction=1.0)
HOLDER = part(HOLDER_NAME, HOLDER_POS_WORLD, boxes=HOLDER_BOXES, mass=5.0, friction=1.0)
WHEEL = part(WHEEL_NAME, WHEEL_START_POS, boxes=WHEEL_BOXES, mass=WHEEL_MASS_KG, friction=WHEEL_FRICTION)
PIN = part(PIN_NAME, PIN_START_POS, boxes=PIN_BOXES, mass=PIN_MASS_KG, friction=PIN_FRICTION)

OBJECTS = [STAND, PAD, HOLDER, WHEEL, PIN]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans

# Aliases for backward compatibility
SCORER = score
SUCCESS = success
DEMO_PLANS = demo
DEMO_PLAN = demo
