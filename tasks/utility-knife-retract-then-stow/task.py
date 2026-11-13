"""Utility knife retract then stow task: retract exposed utility knife blade and stow knife in holster."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import demo_plan
from geometry import (
    BLADE_BOX,
    BUTTON_BOX,
    COLOR_BUTTON,
    COLOR_HOLDER,
    COLOR_KNIFE,
    COLOR_SLIDER,
    HOLDER_BOXES,
    HOLDER_FRICTION,
    HOLDER_POS,
    KNIFE_FRICTION,
    KNIFE_HANDLE_BOX,
    KNIFE_MASS,
    KNIFE_START_POS,
    SLIDER_AT,
    MAT_POS,
    MAT_BOX,
    COLOR_MAT,
    SLIDER_DAMPING_NS_M,
    SLIDER_FRICTION,
    SLIDER_MASS,
    SLIDER_RATE_N_M,
    SLIDER_TRAVEL_M,
    TABLE_TOP,
)
from mechkit import Joint, Mech, box
import scoring

SCENE = "station"
TOP = TABLE_TOP
SUCCESS_HOLD_S = 1.0
SCORE_OVER = "end"

# 1. Utility knife (loose 90 g Mech) carrying the blade slider
knife_shapes = [box(KNIFE_HANDLE_BOX[0], KNIFE_HANDLE_BOX[1], COLOR_KNIFE)]
slider_shapes = [
    box(BLADE_BOX[0], BLADE_BOX[1], COLOR_SLIDER),
    box(BUTTON_BOX[0], BUTTON_BOX[1], COLOR_BUTTON),
]

blade_joint = Joint(
    "blade",
    "slide",
    axis="y",
    at=SLIDER_AT,
    low=0.0,
    high=SLIDER_TRAVEL_M,
    spring=SLIDER_RATE_N_M,
    damping=SLIDER_DAMPING_NS_M,
    mass=SLIDER_MASS,
    friction=SLIDER_FRICTION,
    shapes=slider_shapes,
)

KNIFE = Mech(
    "ku_knife",
    pos=KNIFE_START_POS,
    mass=KNIFE_MASS,
    friction=KNIFE_FRICTION,
    shapes=knife_shapes,
    joints=[blade_joint],
)

# 2. Holster (fixed 25 kg stand-in)
holster_shapes = [box(c, s, COLOR_HOLDER) for c, s in HOLDER_BOXES]
HOLDER = Mech(
    "ku_holder",
    pos=HOLDER_POS,
    mass=None,
    friction=HOLDER_FRICTION,
    shapes=holster_shapes,
)

# 3. Cutting mat (fixed) under the knife
CUTTING_MAT = Mech(
    "ku_mat",
    pos=MAT_POS,
    mass=None,
    friction=HOLDER_FRICTION,
    shapes=[box(MAT_BOX[0], MAT_BOX[1], COLOR_MAT)],
)

OBJECTS = [KNIFE, HOLDER, CUTTING_MAT]

score = scoring.score
success = scoring.success
distance = scoring.distance
demo = demo_plan.plans
