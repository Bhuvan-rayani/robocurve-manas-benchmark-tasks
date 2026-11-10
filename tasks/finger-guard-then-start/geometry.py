from __future__ import annotations

"""Geometric constants for finger_guard_then_start (T20)."""

TABLE_TOP = 0.7475
SUCCESS_HOLD_TIME_S = 1.0

COLOR_MACHINE = (0.45, 0.48, 0.52)  # Machine grey (#737A85)
COLOR_GUARD = (0.95, 0.80, 0.10)    # Yellow guard (#F2CC1A)
COLOR_BUTTON = (0.15, 0.75, 0.25)   # Green start button (#26BF40)

# Fixed machine block (25 kg, friction 1.2) at x=0.30, y=0.0
MACHINE_NAME = "cutting_machine"
MACHINE_MASS_KG = 25.0
MACHINE_FRICTION = 1.2
MACHINE_POS_WORLD = (0.30, 0.0, TABLE_TOP)

# Machine body: 200 x 320 x 80 mm
# Left side has cutting zone with yellow sliding guard (at y = +0.12)
# Right side has green start button (at y = -0.12)
MACHINE_BOXES = [
    ((0.0, 0.0, 0.040), (0.200, 0.320, 0.080), COLOR_MACHINE),
]

# Guard: 140 mm travel along -X (slider) on Left side (y = +0.12)
# Rest position is open (x = 0.23, y = 0.12, z = TABLE_TOP + 0.09)
GUARD_NAME = "finger_guard"
GUARD_DIMS_M = (0.120, 0.100, 0.030)

# Button: 40 mm dia x 15 mm slider along -Z on Right side (y = -0.12)
BUTTON_NAME = "start_button"
BUTTON_DIMS_M = (0.040, 0.040, 0.015)

GATE_MACHINE_DRIFT_MAX_M = 0.005
