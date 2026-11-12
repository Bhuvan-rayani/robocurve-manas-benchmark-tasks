from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from geometry import (
    COLOR_LID,
    LID_BOXES,
    LID_DIMS_M,
    LID_FRICTION,
    LID_LEFT_NAME,
    LID_MASS_KG,
    LID_RIGHT_NAME,
    LID_START_POS,
    PAD_BOXES,
    PAD_LEFT_NAME,
    PAD_LEFT_POS,
    PAD_RIGHT_NAME,
    PAD_RIGHT_POS,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
    TRAY_BOXES,
    TRAY_FRICTION,
    TRAY_MASS_KG,
    TRAY_NAME,
    TRAY_POS_WORLD,
)
import tracekit  # noqa: F401
from parts import part
import demo_plan, scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

TRAY = part(TRAY_NAME, TRAY_POS_WORLD, boxes=TRAY_BOXES, mass=TRAY_MASS_KG, friction=TRAY_FRICTION)
PAD_L = part(PAD_LEFT_NAME, PAD_LEFT_POS, boxes=PAD_BOXES, mass=5.0, friction=1.0)
PAD_R = part(PAD_RIGHT_NAME, PAD_RIGHT_POS, boxes=PAD_BOXES, mass=5.0, friction=1.0)
LID_L = part(LID_LEFT_NAME, LID_START_POS[LID_LEFT_NAME], boxes=LID_BOXES, mass=LID_MASS_KG, friction=LID_FRICTION)
LID_R = part(LID_RIGHT_NAME, LID_START_POS[LID_RIGHT_NAME], boxes=LID_BOXES, mass=LID_MASS_KG, friction=LID_FRICTION)

OBJECTS = [TRAY, PAD_L, PAD_R, LID_L, LID_R]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans

# Aliases for backward compatibility
SCORER = score
SUCCESS = success
DEMO_PLANS = demo
DEMO_PLAN = demo
