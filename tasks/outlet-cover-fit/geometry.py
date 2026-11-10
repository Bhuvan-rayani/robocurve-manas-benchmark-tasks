"""Geometry, dimensions, colors, and poses for outlet_cover_fit."""

from __future__ import annotations

TABLE_TOP = 0.7475

# sRGB colors
COLOR_WALL_PLATE = (0.941, 0.886, 0.737)  # Cream PLA #F0E2BC
COLOR_CAP = (0.843, 0.149, 0.239)         # Red PLA #D7263D
COLOR_PLATE_HOLD = (0.800, 0.740, 0.580)  # Darker cream hold zone

# Wall plate
PLATE_NAME = "wall_plate"
PLATE_START_POS_WORLD = (0.30, 0.0, TABLE_TOP)
PLATE_DIMS_M = (0.12, 0.26, 0.02)
PLATE_MASS_KG = 25.0
PLATE_FRICTION = 0.35

# Sockets (relative to plate origin at base center)
SOCKET_A_OFFSET_M = (0.0, 0.07, 0.011)
SOCKET_B_OFFSET_M = (0.0, 0.0, 0.011)
SOCKET_C_OFFSET_M = (0.0, -0.07, 0.011)

SOCKET_DEPTH_M = 0.018
SOCKET_INNER_WIDTH_M = 0.054
SOCKET_PITCH_Y_M = 0.070   # 85 mm gripper body + 40 mm cap needs ~63 mm; 70 mm leaves the gripper clear of caps already seated next door

# Hold zones on plate ends (for bimanual bracing)
PLATE_LEFT_HOLD_WORLD = (0.26, 0.125, TABLE_TOP + 0.022)
PLATE_RIGHT_HOLD_WORLD = (0.26, -0.125, TABLE_TOP + 0.022)

# Safety caps (3 red cylinders)
CAP_A_NAME = "cap_a"
CAP_B_NAME = "cap_b"
CAP_C_NAME = "cap_c"
CAP_NAMES = (CAP_A_NAME, CAP_B_NAME, CAP_C_NAME)

CAP_RADIUS_M = 0.020  # 40 mm diameter
CAP_HEIGHT_M = 0.030  # 30 mm height
CAP_MASS_KG = 0.02
CAP_FRICTION = 1.2

# Cylinder center is at TABLE_TOP + CAP_HEIGHT_M / 2
CAP_A_START_POS_WORLD = (0.15, 0.12, TABLE_TOP + CAP_HEIGHT_M / 2.0)
CAP_B_START_POS_WORLD = (0.15, 0.0, TABLE_TOP + CAP_HEIGHT_M / 2.0)
CAP_C_START_POS_WORLD = (0.15, -0.12, TABLE_TOP + CAP_HEIGHT_M / 2.0)

# Scoring thresholds & gates
GATE_PLATE_MAX_DRIFT_M = 0.060     # Score 0 if plate moved > 6 cm
SUCCESS_PLATE_MAX_DRIFT_M = 0.015  # 1.0 requires plate moved < 15 mm
CAP_SEATED_XY_TOL_M = 0.020        # Cap within 20 mm of socket center in xy
CAP_SEATED_TOP_TOL_M = 0.005       # Cap top within 3 mm (with 5 mm tol) of plate face
FALLEN_Z_THRESHOLD = TABLE_TOP - 0.05
SUCCESS_HOLD_TIME_S = 1.0

# Wall plate compound collision boxes (19 primitives forming plate + 3 sockets)
# Each box: (centre_xyz, size_xyz, color)
_H = SOCKET_INNER_WIDTH_M            # hole width (x and y), 7 mm clearance per side for a 40 mm cap (open-loop hand wobbles +-6 mm)
_WALL = SOCKET_PITCH_Y_M - _H        # wall between neighbouring holes (16 mm)
_XW = PLATE_DIMS_M[0] / 2 - _H / 2   # x extent of the front and back walls (33 mm)
_XC = _H / 2 + _XW / 2               # their centre
_YE = PLATE_DIMS_M[1] / 2 - (SOCKET_PITCH_Y_M + _H / 2)  # y extent of the end pads (33 mm)
_YEC = SOCKET_PITCH_Y_M + _H / 2 + _YE / 2               # their centre
_Z, _HT = 0.011, 0.018
WALL_PLATE_BOXES = (
    ((0.0, 0.0, 0.001), (0.12, 0.26, 0.002), COLOR_WALL_PLATE),
    # end pads (hold zones) at both ends
    ((-_XC, -_YEC, _Z), (_XW, _YE, _HT), COLOR_PLATE_HOLD),
    ((0.0, -_YEC, _Z), (_H, _YE, _HT), COLOR_PLATE_HOLD),
    ((_XC, -_YEC, _Z), (_XW, _YE, _HT), COLOR_PLATE_HOLD),
    ((-_XC, _YEC, _Z), (_XW, _YE, _HT), COLOR_PLATE_HOLD),
    ((0.0, _YEC, _Z), (_H, _YE, _HT), COLOR_PLATE_HOLD),
    ((_XC, _YEC, _Z), (_XW, _YE, _HT), COLOR_PLATE_HOLD),
) + tuple(
    ((sx, sy, _Z), (_XW, _H, _HT), COLOR_WALL_PLATE) for sx in (-_XC, _XC) for sy in (-SOCKET_PITCH_Y_M, 0.0, SOCKET_PITCH_Y_M)
) + tuple(
    ((sx, sy * SOCKET_PITCH_Y_M / 2, _Z), (sw, _WALL, _HT), COLOR_WALL_PLATE) for sx, sw in ((-_XC, _XW), (0.0, _H), (_XC, _XW)) for sy in (-1, 1)
)
