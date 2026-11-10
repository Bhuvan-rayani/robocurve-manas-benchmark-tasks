"""Geometry, masses, colours, and positions for dip_address_setting."""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_MODULE_VIOLET = (123 / 255, 63 / 255, 191 / 255)   # #7B3FBF
COLOR_KNOB_BLUE = (31 / 255, 79 / 255, 224 / 255)        # #1F4FE0
COLOR_BUTTON_LIME = (155 / 255, 224 / 255, 0 / 255)      # #9BE000
COLOR_CARD_WHITE = (244 / 255, 244 / 255, 244 / 255)     # #F4F4F4

# addr_module specs (140 x 260 x 30 mm, rebuilt larger per assets/dip_address_setting/parts.json)
MODULE_POS_WORLD = (0.30, 0.0, TABLE_TOP)
MODULE_DIMS_M = (0.140, 0.260, 0.030)
MODULE_MASS_KG = 25.0
MODULE_FRICTION = 1.2

# Module body collision boxes (part frame) from parts.json
MODULE_BOXES = (
    ((0.0, 0.0, 0.006), (0.140, 0.260, 0.012), COLOR_MODULE_VIOLET),
    ((-0.068, -0.0745, 0.021), (0.004, 0.111, 0.018), COLOR_MODULE_VIOLET),
    ((-0.068, 0.0, 0.021), (0.004, 0.038, 0.018), COLOR_MODULE_VIOLET),
    ((-0.068, 0.0745, 0.021), (0.004, 0.111, 0.018), COLOR_MODULE_VIOLET),
    ((-0.047, -0.0745, 0.021), (0.038, 0.111, 0.018), COLOR_MODULE_VIOLET),
    ((-0.047, 0.0745, 0.021), (0.038, 0.111, 0.018), COLOR_MODULE_VIOLET),
    ((0.021, -0.0745, 0.021), (0.098, 0.111, 0.018), COLOR_MODULE_VIOLET),
    ((0.021, 0.0, 0.021), (0.098, 0.038, 0.018), COLOR_MODULE_VIOLET),
    ((0.021, 0.0745, 0.021), (0.098, 0.111, 0.018), COLOR_MODULE_VIOLET),
)

# Switch knobs (4 sliders on addr_module at 50 mm pitch, 12 x 16 x 14 mm)
KNOB_DIMS_M = (0.012, 0.016, 0.014)
KNOB_MASS_KG = 0.004
KNOB_TRAVEL_M = 0.015       # 15 mm travel
KNOB_RATE = 0.001           # near-zero spring (damped slider that stays where pushed)
KNOB_DAMPING = 20.0
KNOB_Y_COORDS = (0.075, 0.025, -0.025, -0.075)  # 50 mm pitch, +y to -y order
KNOB_NAMES = ("addr_knob_1", "addr_knob_2", "addr_knob_3", "addr_knob_4")
KNOB_REST_X = 0.0355
KNOB_REST_Z = 0.030

# Axes: start in complement (DOWN, UP, UP, DOWN) of target (UP, DOWN, DOWN, UP)
# Knobs 1 & 4 start at DOWN end, travel along +X to UP
# Knobs 2 & 3 start at UP end, travel along -X to DOWN
KNOB_AXES = ("+X", "-X", "-X", "+X")

# Commit button (slider on addr_module along Z, dia 36 mm, 90 mm behind knob row)
BUTTON_NAME = "addr_button"
BUTTON_REST_PART = (-0.047, 0.0, 0.022)
BUTTON_RADIUS_M = 0.018     # 36 mm diameter
BUTTON_HEIGHT_M = 0.012
BUTTON_MASS_KG = 0.008
BUTTON_TRAVEL_M = 0.008
BUTTON_RATE = 100.0         # 0.1 N/mm = 100 N/m
BUTTON_DAMPING = 10.0

# Dot card (60 x 220 mm)
CARD_POS_WORLD = (0.22, 0.26, TABLE_TOP + 0.0012)
CARD_SIZE_M = (0.060, 0.220, 0.0024)
CARD_MASS_KG = 0.012

# Card dots (flat 24 x 24 x 1 mm squares, +y to -y at the knob pitch): dark = UP, light grey = DOWN (target 1, 0, 0, 1)
COLOR_DOT_UP = (26 / 255, 26 / 255, 26 / 255)        # #1A1A1A
COLOR_DOT_DOWN = (189 / 255, 189 / 255, 189 / 255)   # #BDBDBD
CARD_DOT_SIZE_M = 0.024
CARD_DOT_Y = (0.075, 0.025, -0.025, -0.075)

# Task rules & target state
TARGET_PATTERN = (1, 0, 0, 1)   # 1 = UP, 0 = DOWN (+y to -y order)
START_PATTERN = (0, 1, 1, 0)    # Complement: all 4 wrong at start
SWITCH_FLICK_THRESHOLD_M = 0.010  # >= 10 mm displacement counts as flicked
BUTTON_PRESS_THRESHOLD_M = 0.0064 # >= 6.4 mm travel
MAX_MODULE_DRIFT_GATE_M = 0.050   # 5 cm gate
MAX_MODULE_DRIFT_SCORE_M = 0.015  # 15 mm for score ladder
SUCCESS_HOLD_TIME_S = 1.0
