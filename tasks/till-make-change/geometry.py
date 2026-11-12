"""Geometry, masses, colours, and positions for till_make_change."""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_TILL_BODY = (184 / 255, 134 / 255, 11 / 255)    # #B8860B
COLOR_DRAWER = (224 / 255, 168 / 255, 28 / 255)       # #E0A81C
COLOR_TOKEN_GOLD = (255 / 255, 211 / 255, 77 / 255)   # #FFD34D
COLOR_TRAY_NAVY = (31 / 255, 42 / 255, 90 / 255)      # #1F2A5A

# Till body (fixed heavy base, 25 kg). It sits on the LEFT arm's side of the midline (y > +0.08).
TILL_POS_WORLD = (0.30, 0.14, TABLE_TOP)
TILL_DIMS_M = (0.200, 0.240, 0.080)
TILL_MASS_KG = 25.0  # stands in for "taped to the table"
TILL_FRICTION = 1.2

# Drawer slider inside till body (travel along -X). A damped "stays pushed" slider: the spring is ~0 so the
# drawer stays where the left arm leaves it (nobody has to hold it open).
DRAWER_NAME = "till_drawer"
DRAWER_REST_PART = (-0.010, 0.0, 0.010)
DRAWER_DIMS_M = (0.195, 0.220, 0.050)
DRAWER_MASS_KG = 0.25
DRAWER_TRAVEL_M = 0.100      # 100 mm travel
DRAWER_SPRING_RATE = 0.001   # N/m (stays where pushed)
DRAWER_DAMPING = 50.0
DRAWER_AXIS = "-X"
# Pull knob on the drawer front: 24 mm wide (y), 35 mm proud (x), 32 mm tall (z). Pinched across y.
KNOB_Y_WORLD = TILL_POS_WORLD[1]
KNOB_FRONT_X_WORLD = TILL_POS_WORLD[0] - 0.0925 - 0.035
KNOB_GRASP_X_WORLD = KNOB_FRONT_X_WORLD + 0.0125

# Tokens live on the RIGHT arm's side of the midline (y < -0.08), on the table, one stack per value.
# Stack spacing = token thickness, first token rests exactly on the table.
# 1-unit (dia 40 mm, h 14 mm, 16 g) and 2-unit (dia 50 mm, h 14 mm, 25 g)
TOKEN_A_NAMES = tuple(f"coin_a{i}" for i in range(1, 5))
TOKEN_B_NAMES = tuple(f"coin_b{i}" for i in range(1, 5))

TOKEN_A_RADIUS_M = 0.020
TOKEN_A_HEIGHT_M = 0.014
TOKEN_A_MASS_KG = 0.016
TOKEN_A_XY = (0.17, -0.10)
TOKEN_A_Z_STARTS = tuple(i * TOKEN_A_HEIGHT_M for i in range(4))

TOKEN_B_RADIUS_M = 0.025
TOKEN_B_HEIGHT_M = 0.014
TOKEN_B_MASS_KG = 0.025
TOKEN_B_XY = (0.17, -0.22)
TOKEN_B_Z_STARTS = tuple(i * TOKEN_B_HEIGHT_M for i in range(4))

# Customer tray (navy PLA): open box, 4 mm floor and 6 mm x 16 mm walls, also on the right side
TRAY_POS_WORLD = (0.28, -0.16, TABLE_TOP)
TRAY_DIMS_M = (0.080, 0.120, 0.020)
TRAY_WALL_M = 0.006
TRAY_FLOOR_M = 0.004
TRAY_WALL_H_M = 0.016
TRAY_MASS_KG = 0.080
TRAY_FRICTION = 1.0

# Tray inner cavity for counting tokens
TRAY_INNER_X_MIN = TRAY_POS_WORLD[0] - 0.034
TRAY_INNER_X_MAX = TRAY_POS_WORLD[0] + 0.034
TRAY_INNER_Y_MIN = TRAY_POS_WORLD[1] - 0.054
TRAY_INNER_Y_MAX = TRAY_POS_WORLD[1] + 0.054
TRAY_INNER_Z_MAX = TABLE_TOP + 0.040

# Supply zones: a token resting within this distance of its stack centre is not "loose"
SUPPLY_RADIUS_M = 0.045

# Target change
SALE_AMOUNT = 7
PAID_AMOUNT = 10
TARGET_CHANGE = PAID_AMOUNT - SALE_AMOUNT  # 3 units

# Drawer open threshold
DRAWER_OPEN_THRESHOLD_M = 0.060  # >= 6 cm open
MAX_TILL_DRIFT_M = 0.005        # 5 mm gate
SUCCESS_HOLD_TIME_S = 1.0
