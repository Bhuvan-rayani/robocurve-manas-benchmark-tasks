"""Geometry, masses, colours, and positions for paper_tray_side_guides."""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_FRAME_GREY = (124 / 255, 131 / 255, 139 / 255)   # #7C838B
COLOR_TRAY_SKY_BLUE = (91 / 255, 184 / 255, 232 / 255) # #5BB8E8
COLOR_GUIDE_GREY = (63 / 255, 69 / 255, 76 / 255)      # #3F454C
COLOR_PAPER_WHITE = (244 / 255, 244 / 255, 240 / 255)  # #F4F4F0
COLOR_PAD_GREY = (141 / 255, 147 / 255, 154 / 255)     # #8D939A

# Printer frame (fixed structure with tray slot)
FRAME_NAME = "printer_frame"
FRAME_POS_WORLD = (0.28, 0.0, TABLE_TOP)
FRAME_DIMS_M = (0.340, 0.400, 0.120)
FRAME_MASS_KG = 25.0
FRAME_FRICTION = 1.2

FRAME_BOXES = (
    # Bottom plate (z 0..0.010)
    ((0.0, 0.0, 0.005), (0.340, 0.400, 0.010), COLOR_FRAME_GREY),
    # Top structure above tray slot (z 0.070..0.120, x >= 0.230 world)
    ((0.060, 0.0, 0.095), (0.220, 0.400, 0.050), COLOR_FRAME_GREY),
    # Left side wall (+y)
    ((0.0, 0.184, 0.040), (0.340, 0.032, 0.060), COLOR_FRAME_GREY),
    # Right side wall (-y)
    ((0.0, -0.184, 0.040), (0.340, 0.032, 0.060), COLOR_FRAME_GREY),
    # Back slot end wall (physical stop at x=0.360 world, tray closed at x=0.240)
    ((0.120, 0.0, 0.040), (0.080, 0.336, 0.060), COLOR_FRAME_GREY),
)

# Feed tray (sliding part inside printer slot)
TRAY_NAME = "feed_tray"
TRAY_START_POS_WORLD = (0.12, 0.0, TABLE_TOP + 0.010)
TRAY_CLOSED_X = 0.240
TRAY_DIMS_M = (0.240, 0.320, 0.030)
TRAY_MASS_KG = 0.35
TRAY_FRICTION = 0.2
TRAY_TRAVEL_M = 0.120

TRAY_BOXES = (
    # Floor (z 0..0.004)
    ((0.0, 0.0, 0.002), (0.240, 0.320, 0.004), COLOR_TRAY_SKY_BLUE),
    # Front rim (+x)
    ((0.1185, 0.0, 0.017), (0.003, 0.320, 0.026), COLOR_TRAY_SKY_BLUE),
    # Rear rim (-x)
    ((-0.1185, 0.0, 0.017), (0.003, 0.320, 0.026), COLOR_TRAY_SKY_BLUE),
    # Left rim (+y)
    ((0.0, 0.1585, 0.017), (0.234, 0.003, 0.026), COLOR_TRAY_SKY_BLUE),
    # Right rim (-y)
    ((0.0, -0.1585, 0.017), (0.234, 0.003, 0.026), COLOR_TRAY_SKY_BLUE),
)

# Side guides (sliders mounted on feed_tray)
GUIDE_A_NAME = "side_guide_a"
GUIDE_B_NAME = "side_guide_b"
GUIDE_DIMS_M = (0.200, 0.010, 0.030)
GUIDE_MASS_KG = 0.04
GUIDE_TRAVEL_M = 0.025
GUIDE_RATE = 0.001       # damped slider as modelled (rate 0.001 N/m, damping 20.0 N s/m)
GUIDE_DAMPING = 20.0

# Guide A: +y side, moves inward along -Y
GUIDE_A_REST_PART = (0.0, 0.135, 0.004)
GUIDE_A_BOX = ((0.0, 0.135, 0.019), GUIDE_DIMS_M, COLOR_GUIDE_GREY)
GUIDE_A_AXIS = "Y"

# Guide B: -y side, moves inward along +Y
GUIDE_B_REST_PART = (0.0, -0.135, 0.004)
GUIDE_B_BOX = ((0.0, -0.135, 0.019), GUIDE_DIMS_M, COLOR_GUIDE_GREY)
GUIDE_B_AXIS = "+Y"

# Paper stack
PAPER_NAME = "paper_stack"
PAPER_START_POS_WORLD = (0.14, 0.32, TABLE_TOP + 0.020)
PAPER_DIMS_M = (0.150, 0.210, 0.030)
PAPER_MASS_KG = 0.25
PAPER_FRICTION = 0.2

# Paper stack boxes: solid paper block + top grab handle tab
PAPER_BOXES = (
    # Main paper block: 150 x 210 x 30 mm
    ((0.0, 0.0, 0.0), (0.150, 0.210, 0.030), COLOR_PAPER_WHITE),
    # Top grab handle tab: 40 x 40 x 15 mm
    ((0.0, 0.0, 0.0225), (0.040, 0.040, 0.015), COLOR_GUIDE_GREY),
)

# Paper pad (staging pad on table)
PAD_NAME = "paper_pad"
PAD_POS_WORLD = (0.14, 0.32, TABLE_TOP + 0.0025)
PAD_SIZE_M = (0.170, 0.230, 0.005)
PAD_MASS_KG = 0.12

# Scoring thresholds & rules
MAX_FRAME_DRIFT_GATE_M = 0.005   # 5 mm frame movement gate
MAX_PAPER_TILT_RAD = 0.087       # ~5.0 degrees tilt threshold for flat
GUIDE_CONTACT_THRESHOLD_M = 0.0015 # 1.5 mm distance from guide inner face to paper side
BLOCK_CENTRING_THRESHOLD_M = 0.003 # 3 mm from tray midline
TRAY_CLOSED_TOLERANCE_M = 0.003    # 3 mm from stop at x = 0.240
SUCCESS_HOLD_TIME_S = 1.0
