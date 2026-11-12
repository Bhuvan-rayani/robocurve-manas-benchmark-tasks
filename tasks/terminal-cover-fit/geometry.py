from __future__ import annotations

"""Geometric definitions and constants for terminal_cover_fit (T16)."""

TABLE_TOP = 0.7475
SUCCESS_HOLD_TIME_S = 1.0

COLOR_BLOCK = (0.90, 0.90, 0.92)     # White terminal block (#E6E6EB)
COLOR_TERM_RED = (0.85, 0.15, 0.15)  # Red terminal
COLOR_TERM_BLUE = (0.15, 0.35, 0.85) # Blue terminal
COLOR_COVER = (0.45, 0.50, 0.55)     # Clear-grey cover
COLOR_HANDLE = (0.30, 0.32, 0.35)

# Fixed heavy white terminal block (25 kg, friction 1.2)
BLOCK_NAME = "terminal_block"
BLOCK_MASS_KG = 25.0
BLOCK_FRICTION = 1.2
BLOCK_POS_WORLD = (0.30, 0.0, TABLE_TOP)

# Block 140 mm (X) x 200 mm (Y) x 30 mm (Z)
# Terminals: 30 mm dia x 30 mm height, red at y=+0.05, blue at y=-0.05
BLOCK_BOXES = [
    ((0.0, 0.0, 0.015), (0.140, 0.200, 0.030), COLOR_BLOCK),
    ((0.0, 0.050, 0.045), (0.030, 0.030, 0.030), COLOR_TERM_RED),
    ((0.0, -0.050, 0.045), (0.030, 0.030, 0.030), COLOR_TERM_BLUE),
]

# Staging pad at x = 0.16
PAD_NAME = "cover_pad"
PAD_POS_WORLD = (0.14, 0.0, TABLE_TOP)
PAD_BOXES = [((0.0, 0.0, 0.005), (0.14, 0.28, 0.010), (0.3, 0.3, 0.3))]

# Cover: 120 mm (X) x 180 mm (Y) x 40 mm (Z), 0.30 kg
# Handles on top center and sides
COVER_NAME = "terminal_cover"
COVER_MASS_KG = 0.30
COVER_FRICTION = 0.8
COVER_START_POS = (0.14, 0.0, TABLE_TOP + 0.010)
COVER_TARGET_POS = (0.30, 0.0, TABLE_TOP + 0.030)

COVER_BOXES = [
    # Top lid: 120 x 180 x 10 mm (z = 0.030 to 0.040)
    ((0.0, 0.0, 0.035), (0.120, 0.180, 0.010), COLOR_COVER),
    # Left skirt: 120 x 10 x 30 mm (z = 0.0 to 0.030)
    ((0.0, 0.085, 0.015), (0.120, 0.010, 0.030), COLOR_COVER),
    # Right skirt: 120 x 10 x 30 mm (z = 0.0 to 0.030)
    ((0.0, -0.085, 0.015), (0.120, 0.010, 0.030), COLOR_COVER),
    # Center handle on top: 40 x 25 x 20 mm (z = 0.040 to 0.060)
    ((0.0, 0.0, 0.050), (0.040, 0.025, 0.020), COLOR_HANDLE),
    # Left handle: 40 x 20 x 20 mm at y = +0.100
    ((0.0, 0.100, 0.030), (0.040, 0.020, 0.020), COLOR_HANDLE),
    # Right handle: 40 x 20 x 20 mm at y = -0.100
    ((0.0, -0.100, 0.030), (0.040, 0.020, 0.020), COLOR_HANDLE),
]

GATE_BLOCK_DRIFT_MAX_M = 0.005
GATE_MIN_Z_M = TABLE_TOP - 0.05
