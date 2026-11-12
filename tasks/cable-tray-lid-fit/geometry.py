from __future__ import annotations

"""Geometric constants for cable_tray_lid_fit (T13)."""

TABLE_TOP = 0.7475
SUCCESS_HOLD_TIME_S = 1.0

COLOR_TRAY = (0.45, 0.48, 0.52)   # Steel-grey (#737A85)
COLOR_LID = (0.12, 0.65, 0.60)    # Teal (#1FA699)
COLOR_PAD = (0.28, 0.30, 0.34)

# Fixed heavy cable tray (25 kg, friction 1.2)
TRAY_NAME = "cable_tray"
TRAY_MASS_KG = 25.0
TRAY_FRICTION = 1.2
TRAY_POS_WORLD = (0.30, 0.0, TABLE_TOP)

# Open cable tray rails: 120 mm wide (X) x 400 mm long (Y) x 60 mm rail top (Z)
# Lids rest directly on top of the rails with no lateral guide walls (open seating)
TRAY_BOXES = [
    # Bottom floor: 120 x 400 x 10 mm
    ((0.0, 0.0, 0.005), (0.120, 0.400, 0.010), COLOR_TRAY),
    # Front support rail: 15 x 400 x 50 mm (top at TABLE_TOP + 0.060)
    ((0.0525, 0.0, 0.035), (0.015, 0.400, 0.050), COLOR_TRAY),
    # Back support rail: 15 x 400 x 50 mm (top at TABLE_TOP + 0.060)
    ((-0.0525, 0.0, 0.035), (0.015, 0.400, 0.050), COLOR_TRAY),
]



# Two staging pads at x = 0.16
PAD_LEFT_NAME = "pad_left"
PAD_RIGHT_NAME = "pad_right"
PAD_LEFT_POS = (0.16, 0.22, TABLE_TOP)
PAD_RIGHT_POS = (0.16, -0.22, TABLE_TOP)
PAD_BOXES = [((0.0, 0.0, 0.005), (0.12, 0.22, 0.010), COLOR_PAD)]

# Two teal lids with 4 x 8 x 1 cm handles:
LID_LEFT_NAME = "lid_left"
LID_RIGHT_NAME = "lid_right"
LID_DIMS_M = (0.118, 0.196, 0.012)
HANDLE_DIMS_M = (0.040, 0.080, 0.010)
COLOR_HANDLE = (0.25, 0.25, 0.28)
LID_MASS_KG = 0.30
LID_FRICTION = 0.6

LID_BOXES = [
    # Base plate: 118 x 196 x 12 mm
    ((0.0, 0.0, 0.0), LID_DIMS_M, COLOR_LID),
    # Handle: 40 x 80 x 10 mm standing on top of base plate
    ((0.0, 0.0, 0.011), HANDLE_DIMS_M, COLOR_HANDLE),
]

LID_START_POS = {
    "lid_left": (0.16, 0.22, TABLE_TOP + 0.016),
    "lid_right": (0.16, -0.22, TABLE_TOP + 0.016),
}

# Target positions when fully seated on tray rails meeting in middle
LID_TARGET_POS = {
    "lid_left": (0.30, 0.099, TABLE_TOP + 0.060),
    "lid_right": (0.30, -0.099, TABLE_TOP + 0.060),
}

GATE_TRAY_DRIFT_MAX_M = 0.005
GATE_MIN_Z_M = TABLE_TOP - 0.05
