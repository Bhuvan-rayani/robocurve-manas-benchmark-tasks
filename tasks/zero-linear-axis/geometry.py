"""Geometry, masses, colours, and positions for zero_linear_axis (v2, redesigned after the first GPU run).

What changed and why (GPU run 1, trace evidence):
- The spring-less lock-pin slider dropped to its lower limit under gravity within 30 steps, so "pin seated" was true at
  the start. The pin is now a LOOSE cylinder the left arm carries to the lug hole and drops in.
- The carriage return spring is gone (rate ~0): it stays where it is pushed, so the pin can lock it. Damping makes pushing
  it need a real force, and the base sits on a very slippery film so an unheld base slides away from that push.
- The pin guide fixture is removed.
"""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_BASE_GREY = (106 / 255, 112 / 255, 120 / 255)         # #6A7078
COLOR_CARRIAGE_SILVER = (170 / 255, 179 / 255, 189 / 255)   # #AAB3BD
COLOR_PIN_GUIDE_GREY = (78 / 255, 84 / 255, 91 / 255)       # #4E545B (hold zone inlay)
COLOR_PIN_YELLOW = (242 / 255, 197 / 255, 0 / 255)          # #F2C500
COLOR_MARK_WHITE = (244 / 255, 244 / 255, 244 / 255)        # #F4F4F4

# axis_base: loose block on a very slippery film
BASE_NAME = "axis_base"
BASE_POS_WORLD = (0.26, 0.0, TABLE_TOP)
BASE_DIMS_M = (0.080, 0.320, 0.040)
BASE_MASS_KG = 0.60
BASE_FRICTION = 0.02  # slippery film: an unheld base slides when the carriage is pushed (GPU run 6: at 0.08 an unheld base did not move at all)

BASE_BOXES = (
    ((0.0, 0.0, 0.020), (0.080, 0.320, 0.040), COLOR_BASE_GREY),
    # Darker hold zone at the +y end (the left arm presses here)
    ((0.0, 0.130, 0.0405), (0.070, 0.060, 0.001), COLOR_PIN_GUIDE_GREY),
    # White datum mark strip on the base top near its -x edge at y = -0.060 (x 10 mm, y 6 mm, z 2 mm)
    ((-0.030, -0.060, 0.041), (0.010, 0.006, 0.002), COLOR_MARK_WHITE),
)

# axis_carriage: prismatic slider along +Y on the base, stays where pushed
CARRIAGE_NAME = "axis_carriage"
CARRIAGE_REST_PART = (0.0, -0.100, 0.040)  # slider frame at rest (part frame); marks align after a +40 mm push (y -0.060)
CARRIAGE_TRAVEL_M = 0.120
CARRIAGE_RETURN_SPRING_RATE = 0.001        # ~0: no return, the carriage stays where it is pushed
CARRIAGE_DAMPING = 150.0                   # pushing at 10 mm/s needs ~1.5 N, more than the base friction, so an unheld base slides
CARRIAGE_MASS_KG = 0.15
CARRIAGE_AXIS = "+Y"

# Carriage body on the base top (80 x 60 x 30 mm) and a 3 x 3 box ring (lug) outside the base's -x edge.
# Lug: outer 54 x 54 mm, 25 mm thick (z 0.040-0.065), centre hole 30 x 30 mm (the pin is 16 mm: 7 mm per side).
_LUG_CX = -0.085   # lug centre in the part frame (x): lug spans x -0.110..-0.060, clear of the base (-0.040)
_LUG_CY = -0.100   # lug centre at rest (y)
_LUG_Z = 0.0525
_LUG_H = 0.025
_CELL_EDGE = 0.012  # outer cell edge (GPU runs 3-4: 22 and 26 mm holes were clipped by a +-6 mm hand wobble; now 30 mm, 7 mm per side)
_CELL_MID = 0.030   # hole width (lug outer size is therefore 54 mm)
CARRIAGE_BOXES = (
    ((0.0, -0.100, 0.055), (0.080, 0.060, 0.030), COLOR_CARRIAGE_SILVER),  # body on the base
    # Bridge joining the body to the lug (above the base edge)
    ((-0.050, -0.100, 0.0525), (0.020, 0.050, 0.025), COLOR_CARRIAGE_SILVER),
) + tuple(
    (
        (_LUG_CX + ix * (_CELL_EDGE + _CELL_MID) / 2, _LUG_CY + iy * (_CELL_EDGE + _CELL_MID) / 2, _LUG_Z),
        ((_CELL_MID if ix == 0 else _CELL_EDGE), (_CELL_MID if iy == 0 else _CELL_EDGE), _LUG_H),
        COLOR_CARRIAGE_SILVER,
    )
    for ix in (-1, 0, 1)
    for iy in (-1, 0, 1)
    if not (ix == 0 and iy == 0)
) + (
    # White mark strip on the carriage top edge near its -x side, aligns with the base mark when the carriage has moved 40 mm
    ((-0.030, -0.100, 0.071), (0.010, 0.006, 0.002), COLOR_MARK_WHITE),
)

# Lock pin: a loose yellow cylinder, 16 mm dia x 60 mm, standing on the table on the left arm's side
PIN_NAME = "lock_pin"
PIN_RADIUS_M = 0.008
PIN_HEIGHT_M = 0.060
PIN_MASS_KG = 0.030
PIN_FRICTION = 1.0
PIN_START_XY = (0.20, 0.20)

# World positions of the hole at carriage displacement d (m): x fixed, y = base_y + (-0.060 + d)
HOLE_WORLD_X = BASE_POS_WORLD[0] + _LUG_CX
HOLE_REST_WORLD_Y = BASE_POS_WORLD[1] + _LUG_CY
HOLE_HALF_WIDTH_M = _CELL_MID / 2            # 11 mm
LUG_TOP_Z = TABLE_TOP + 0.065
LUG_BOTTOM_Z = TABLE_TOP + 0.040

# Task alignment thresholds and scoring parameters
CARRIAGE_TARGET_DISP_M = 0.040               # marks are 40 mm apart at start
CARRIAGE_MIN_MOVE_LADDER_0_25_M = 0.020      # 0.25: carriage moved >= 20 mm toward the datum
MARK_OFFSET_LADDER_0_50_M = 0.006            # offset <= 6 mm
MARK_OFFSET_LADDER_0_75_M = 0.003            # offset <= 3 mm
MARK_OFFSET_LADDER_1_00_M = 0.003            # offset <= 3 mm

# The pin counts as "through the lug" when its axis is within the hole and its bottom is below the lug bottom
PIN_AXIS_IN_HOLE_M = HOLE_HALF_WIDTH_M - PIN_RADIUS_M + 0.002   # centre within 5 mm of the hole centre
PIN_BOTTOM_THROUGH_Z = LUG_BOTTOM_Z - 0.005                      # bottom at least 5 mm below the lug bottom
PIN_MAX_TILT_DEG = 15.0

MAX_BASE_DRIFT_SCORE_M = 0.008               # base moved < 8 mm from start
MAX_BASE_DRIFT_GATE_M = 0.050                # 5 cm gate
MAX_BASE_TILT_DEG = 20.0                     # 20 deg gate
SUCCESS_HOLD_TIME_S = 1.0
