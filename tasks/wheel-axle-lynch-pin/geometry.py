from __future__ import annotations

"""Geometric constants for wheel_axle_lynch_pin (T18)."""

TABLE_TOP = 0.7475
SUCCESS_HOLD_TIME_S = 1.0

COLOR_STAND = (0.55, 0.58, 0.62)    # Silver stand (#8C949E)
COLOR_AXLE = (0.80, 0.82, 0.85)     # Silver axle
COLOR_WHEEL = (0.15, 0.15, 0.18)    # Black wheel (#26262E)
COLOR_PIN = (0.95, 0.35, 0.65)      # Pink lynch pin (#F259A6)
COLOR_PAD = (0.28, 0.30, 0.34)

# Fixed heavy stand with horizontal axle along -y (25 kg, friction 1.2)
STAND_NAME = "axle_stand"
STAND_MASS_KG = 25.0
STAND_FRICTION = 1.2
STAND_POS_WORLD = (0.30, 0.0, TABLE_TOP)

# Stand body: 120 (X) x 100 (Y) x 120 (Z) mm
# Horizontal axle extends from y = 0 to y = -0.16 m at z = TABLE_TOP + 0.08 m
# Cross hole is at y = -0.14 m, diameter 16 mm (clearance >= 7 mm per side for 8 mm pin)
STAND_BOXES = [
    ((0.0, 0.0, 0.040), (0.120, 0.100, 0.080), COLOR_STAND),
    # Base brace handle on left for Left arm (y = +0.12)
    ((0.0, 0.100, 0.040), (0.040, 0.100, 0.040), COLOR_STAND),
    # Axle cross hole side cheeks at y = -0.140 to guide and seat lynch pin collar
    ((-0.007, -0.140, 0.080), (0.004, 0.020, 0.020), COLOR_AXLE),
    ((+0.007, -0.140, 0.080), (0.004, 0.020, 0.020), COLOR_AXLE),
]
STAND_CYLINDERS = [
    # Inner axle from y=0 to y=-0.130 (length 130 mm)
    ((0.0, -0.065, 0.080), 0.010, 0.130, COLOR_AXLE, "Y"),
    # Axle tip from y=-0.150 to y=-0.160 (length 10 mm), leaving 20 mm cross hole at y=-0.140
    ((0.0, -0.155, 0.080), 0.010, 0.010, COLOR_AXLE, "Y"),
]

# Staging pad for wheel at (0.16, -0.18)
PAD_NAME = "staging_pad"
PAD_POS_WORLD = (0.16, -0.18, TABLE_TOP)
PAD_BOXES = [
    ((0.0, 0.0, 0.005), (0.16, 0.16, 0.010), COLOR_PAD),
    ((-0.035, 0.0, 0.012), (0.015, 0.120, 0.014), COLOR_PAD),
    ((+0.035, 0.0, 0.012), (0.015, 0.120, 0.014), COLOR_PAD),
]

# Pin holder at (0.20, -0.26)
HOLDER_NAME = "pin_holder"
HOLDER_POS_WORLD = (0.20, -0.30, TABLE_TOP)
HOLDER_BOXES = [((0.0, 0.0, 0.020), (0.04, 0.04, 0.040), (0.3, 0.3, 0.3))]

# Wheel: 120 mm dia x 30 mm, hub hole 28 mm dia, 0.40 kg
WHEEL_NAME = "axle_wheel"
WHEEL_MASS_KG = 0.40
WHEEL_FRICTION = 0.8
WHEEL_START_POS = (0.16, -0.18, TABLE_TOP + 0.079)
WHEEL_TARGET_POS = (0.30, -0.060, TABLE_TOP + 0.080)

# Lynch pin: 8 mm dia x 60 mm, 0.05 kg
PIN_NAME = "lynch_pin"
PIN_MASS_KG = 0.05
PIN_FRICTION = 0.5
PIN_START_POS = (0.20, -0.30, TABLE_TOP + 0.068)
PIN_TARGET_POS = (0.30, -0.140, TABLE_TOP + 0.080)

GATE_STAND_DRIFT_MAX_M = 0.005
GATE_MIN_Z_M = TABLE_TOP - 0.05

WHEEL_BOXES = [
    # Top rim (grasp target, 120 mm wide across X, 30 mm thick along Y, 43 mm tall)
    ((0.0, 0.0, 0.0385), (0.120, 0.030, 0.043), COLOR_WHEEL),
    # Bottom rim
    ((0.0, 0.0, -0.0385), (0.120, 0.030, 0.043), COLOR_WHEEL),
    # Left rim
    ((-0.0385, 0.0, 0.0), (0.043, 0.030, 0.034), COLOR_WHEEL),
    # Right rim
    ((+0.0385, 0.0, 0.0), (0.043, 0.030, 0.034), COLOR_WHEEL),
]
PIN_BOXES = [
    # Shaft: 6 mm square x 56 mm tall
    ((0.0, 0.0, 0.0), (0.006, 0.006, 0.056), COLOR_PIN),
    # Head collar: 24x24 mm x 8 mm tall centered at z = +0.032 to rest on axle cross-hole rim
    ((0.0, 0.0, 0.032), (0.024, 0.024, 0.008), COLOR_PIN),
]

