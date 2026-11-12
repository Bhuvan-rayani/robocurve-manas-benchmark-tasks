"""Make change for a sale of 7 paid with 10 into the navy tray."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from geometry import (
    COLOR_DRAWER,
    COLOR_TILL_BODY,
    COLOR_TOKEN_GOLD,
    COLOR_TRAY_NAVY,
    DRAWER_AXIS,
    DRAWER_DAMPING,
    DRAWER_DIMS_M,
    DRAWER_MASS_KG,
    DRAWER_NAME,
    DRAWER_REST_PART,
    DRAWER_SPRING_RATE,
    DRAWER_TRAVEL_M,
    SUCCESS_HOLD_TIME_S,
    TABLE_TOP,
    TILL_DIMS_M,
    TILL_FRICTION,
    TILL_MASS_KG,
    TILL_POS_WORLD,
    TOKEN_A_HEIGHT_M,
    TOKEN_A_MASS_KG,
    TOKEN_A_NAMES,
    TOKEN_A_RADIUS_M,
    TOKEN_A_XY,
    TOKEN_A_Z_STARTS,
    TOKEN_B_HEIGHT_M,
    TOKEN_B_MASS_KG,
    TOKEN_B_NAMES,
    TOKEN_B_RADIUS_M,
    TOKEN_B_XY,
    TOKEN_B_Z_STARTS,
    TRAY_DIMS_M,
    TRAY_FLOOR_M,
    TRAY_FRICTION,
    TRAY_MASS_KG,
    TRAY_WALL_H_M,
    TRAY_WALL_M,
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

# Till body boxes (hollow shell, fixed 25 kg base)
_TILL_BOXES = (
    ((0.0, 0.0, 0.005), (TILL_DIMS_M[0], TILL_DIMS_M[1], 0.010), COLOR_TILL_BODY),
    ((0.025, 0.0, 0.072), (0.150, TILL_DIMS_M[1], 0.016), COLOR_TILL_BODY),   # lid over the back 150 mm; front stays open for the hand
    ((0.0, 0.116, 0.037), (TILL_DIMS_M[0], 0.008, 0.054), COLOR_TILL_BODY),
    ((0.0, -0.116, 0.037), (TILL_DIMS_M[0], 0.008, 0.054), COLOR_TILL_BODY),
    ((0.092, 0.0, 0.037), (0.016, 0.224, 0.054), COLOR_TILL_BODY),
)

# Drawer slider inside till body: hollowed well geometry
# Base slab is 18 mm high (z=0.009), rim walls around periphery and central divider
# so wells at y=+0.05 and y=-0.05 are hollow open cavities (tokens start at z>=0.020)
_DRAWER_BOXES = (
    # Base floor slab
    ((0.0, 0.0, 0.020), (0.180, 0.220, 0.018), COLOR_DRAWER),
    # Front wall (-x)
    ((-0.085, 0.0, 0.045), (0.015, 0.220, 0.032), COLOR_DRAWER),
    # Back wall (+x)
    ((0.085, 0.0, 0.045), (0.015, 0.220, 0.032), COLOR_DRAWER),
    # Left wall (+y)
    ((0.0, 0.1025, 0.045), (0.180, 0.015, 0.032), COLOR_DRAWER),
    # Right wall (-y)
    ((0.0, -0.1025, 0.045), (0.180, 0.015, 0.032), COLOR_DRAWER),
    # Central divider (y=0) separating A and B compartments
    ((0.0, 0.0, 0.045), (0.180, 0.015, 0.032), COLOR_DRAWER),
    # Pull knob on the front (-x): 35 mm proud, 24 mm wide
    ((-0.110, 0.0, 0.045), (0.035, 0.024, 0.032), COLOR_DRAWER),
)

DRAWER_SLIDER = Slider(
    name=DRAWER_NAME,
    rest=DRAWER_REST_PART,
    boxes=_DRAWER_BOXES,
    travel=DRAWER_TRAVEL_M,
    rate=DRAWER_SPRING_RATE,
    damping=DRAWER_DAMPING,
    mass=DRAWER_MASS_KG,
    axis=DRAWER_AXIS,
)

TILL_PART = part(
    name="till_body",
    pos=TILL_POS_WORLD,
    boxes=_TILL_BOXES,
    mass=TILL_MASS_KG,
    friction=TILL_FRICTION,
    sliders=(DRAWER_SLIDER,),
)

# Tokens (1-unit stack: coin_a1..a4)
TOKENS_A = [
    Cylinder(
        name=name,
        pos=(TOKEN_A_XY[0], TOKEN_A_XY[1], TOP + z + TOKEN_A_HEIGHT_M / 2),
        radius=TOKEN_A_RADIUS_M,
        height=TOKEN_A_HEIGHT_M,
        mass=TOKEN_A_MASS_KG,
        color=COLOR_TOKEN_GOLD,
    )
    for name, z in zip(TOKEN_A_NAMES, TOKEN_A_Z_STARTS)
]

# Tokens (2-unit stack: coin_b1..b4)
TOKENS_B = [
    Cylinder(
        name=name,
        pos=(TOKEN_B_XY[0], TOKEN_B_XY[1], TOP + z + TOKEN_B_HEIGHT_M / 2),
        radius=TOKEN_B_RADIUS_M,
        height=TOKEN_B_HEIGHT_M,
        mass=TOKEN_B_MASS_KG,
        color=COLOR_TOKEN_GOLD,
    )
    for name, z in zip(TOKEN_B_NAMES, TOKEN_B_Z_STARTS)
]

# Customer tray: open box (floor + four walls), loose 80 g body
_TW = TRAY_WALL_M
_TX, _TY, _TZ = TRAY_DIMS_M
_WZ = TRAY_FLOOR_M + TRAY_WALL_H_M / 2
CHANGE_TRAY = part(
    name="change_tray",
    pos=TRAY_POS_WORLD,
    boxes=(
        ((0.0, 0.0, TRAY_FLOOR_M / 2), (_TX, _TY, TRAY_FLOOR_M), COLOR_TRAY_NAVY),
        ((_TX / 2 - _TW / 2, 0.0, _WZ), (_TW, _TY, TRAY_WALL_H_M), COLOR_TRAY_NAVY),
        ((-_TX / 2 + _TW / 2, 0.0, _WZ), (_TW, _TY, TRAY_WALL_H_M), COLOR_TRAY_NAVY),
        ((0.0, _TY / 2 - _TW / 2, _WZ), (_TX - 2 * _TW, _TW, TRAY_WALL_H_M), COLOR_TRAY_NAVY),
        ((0.0, -_TY / 2 + _TW / 2, _WZ), (_TX - 2 * _TW, _TW, TRAY_WALL_H_M), COLOR_TRAY_NAVY),
    ),
    mass=TRAY_MASS_KG,
    friction=TRAY_FRICTION,
)

OBJECTS = [TILL_PART, *TOKENS_A, *TOKENS_B, CHANGE_TRAY]

success = scoring.success
score = scoring.score
distance = scoring.distance
demo = demo_plan.plans
