from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from geometry import (
    BLOCK_BOXES,
    BLOCK_FRICTION,
    BLOCK_MASS_KG,
    BLOCK_NAME,
    BLOCK_POS_WORLD,
    COVER_BOXES,
    COVER_FRICTION,
    COVER_MASS_KG,
    COVER_NAME,
    COVER_START_POS,
    PAD_BOXES,
    PAD_NAME,
    PAD_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
import tracekit  # noqa: F401
from parts import part
import demo_plan, scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

BLOCK = part(BLOCK_NAME, BLOCK_POS_WORLD, boxes=BLOCK_BOXES, mass=BLOCK_MASS_KG, friction=BLOCK_FRICTION)
PAD = part(PAD_NAME, PAD_POS_WORLD, boxes=PAD_BOXES, mass=5.0, friction=1.0)
COVER = part(COVER_NAME, COVER_START_POS, boxes=COVER_BOXES, mass=COVER_MASS_KG, friction=COVER_FRICTION)

OBJECTS = [BLOCK, PAD, COVER]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans

# Aliases for backward compatibility
SCORER = score
SUCCESS = success
DEMO_PLANS = demo
DEMO_PLAN = demo
