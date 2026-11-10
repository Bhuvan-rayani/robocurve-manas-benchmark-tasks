from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tracekit  # noqa: F401
from geometry import (
    BUTTON_DIMS_M,
    COLOR_BUTTON,
    COLOR_GUARD,
    GUARD_DIMS_M,
    MACHINE_BOXES,
    MACHINE_FRICTION,
    MACHINE_MASS_KG,
    MACHINE_NAME,
    MACHINE_POS_WORLD,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
)
from parts import Slider, part
import demo_plan, scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = SUCCESS_HOLD_TIME_S
SCORE_OVER = "end"

# Sliders:
# 1. Guard on Left (+X slider with spring 80 N/m)
# 2. Button on Right (-Z slider with spring 100 N/m)
MACHINE = part(
    MACHINE_NAME,
    MACHINE_POS_WORLD,
    boxes=MACHINE_BOXES,
    mass=MACHINE_MASS_KG,
    friction=MACHINE_FRICTION,
    sliders=[
        Slider("guard", rest=(-0.070, 0.120, 0.095), boxes=[((-0.070, 0.120, 0.095), GUARD_DIMS_M, COLOR_GUARD)], axis="+X", travel=0.140, rate=10.0, damping=20.0),
        Slider("button", rest=(0.0, -0.120, 0.0875), boxes=[((0.0, -0.120, 0.0875), BUTTON_DIMS_M, COLOR_BUTTON)], axis="Z", travel=0.008, rate=100.0, damping=10.0),
    ],
)

OBJECTS = [MACHINE]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans

# Aliases for backward compatibility
SCORER = score
SUCCESS = success
DEMO_PLANS = demo
DEMO_PLAN = demo
