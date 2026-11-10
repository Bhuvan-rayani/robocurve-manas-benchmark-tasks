from __future__ import annotations

"""Geometric constants and parameters for cordon_bar_walkway (T26)."""

TABLE_TOP = 0.7475
SUCCESS_HOLD_TIME_S = 1.0

COLOR_POST = (0.961, 0.769, 0.000)  # Yellow (#F5C400)
COLOR_PAD = (0.420, 0.447, 0.502)   # Grey (#6B7280)
COLOR_BAR = (0.957, 0.957, 0.957)   # White/Red (#F4F4F4)

# Fixed yellow barrier posts (25.0 kg, friction 1.2) spaced 40 cm apart at y = +/-20 cm
POST_A_NAME = "cordon_post_a"
POST_A_MASS_KG = 25.0
POST_A_FRICTION = 1.2
POST_A_POS_WORLD = (0.28, 0.20, TABLE_TOP)

POST_B_NAME = "cordon_post_b"
POST_B_MASS_KG = 25.0
POST_B_FRICTION = 1.2
POST_B_POS_WORLD = (0.28, -0.20, TABLE_TOP)

# Post collision boxes: 40 x 40 x 400 mm post column plus cradle notch
POST_BOXES = [
    ((0.0, 0.0, 0.01), (0.12, 0.12, 0.02), COLOR_POST),  # base plate: a 25 kg 40 cm post on a 4 cm footprint tipped over when the bar rolled into it (GPU)
    ((0.0, 0.0, 0.0525), (0.04, 0.04, 0.105), COLOR_POST),  # 10.5 cm column: the hands only lift the bar ~12 cm at y +-0.12 / yaw 90 (GPU), so the supports are low
    ((0.0, 0.0, 0.110), (0.080, 0.06, 0.01), COLOR_POST),
]

# Fixed staging pad for cordon bar: 60 x 500 x 10 mm
BAR_PAD_NAME = "bar_pad"
BAR_PAD_MASS_KG = 25.0
BAR_PAD_FRICTION = 1.2
BAR_PAD_POS_WORLD = (0.18, 0.0, TABLE_TOP)
BAR_PAD_BOXES = [
    ((0.0, 0.0, 0.005), (0.06, 0.50, 0.01), COLOR_PAD),
]

# Loose cordon bar: 31 x 460 x 31 mm, mass 0.3 kg
BAR_NAME = "cordon_bar"
BAR_MASS_KG = 0.3
BAR_FRICTION = 1.2
BAR_START_POS = (0.18, 0.0, TABLE_TOP + 0.010)
BAR_TARGET_POS = (0.28, 0.0, TABLE_TOP + 0.115)  # the bar part origin is its base: it rests with its base on the 11.5 cm plate top
BAR_BOXES = [
    ((0.0, 0.0, 0.0155), (0.031, 0.460, 0.031), COLOR_BAR),
]

# Gates and tolerances
GATE_POST_DRIFT_MAX_M = 0.005
GATE_MIN_Z_M = TABLE_TOP - 0.05
