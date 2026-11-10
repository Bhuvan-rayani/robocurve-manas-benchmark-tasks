"""Geometry definitions, dimensions, and physical properties for stair_nosing_strip_fit."""

from __future__ import annotations

TABLE_TOP = 0.7475

# -----------------------------------------------------------------------------
# Colors (sRGB)
# -----------------------------------------------------------------------------
COLOR_STAIR_STEP = (0.541, 0.565, 0.600)  # #8A9099 Grey PLA
COLOR_STRIP_PAD = (0.353, 0.376, 0.408)  # #5A6068 Slate PLA
COLOR_NOSING_STRIP = (0.961, 0.769, 0.000)  # #F5C400 Yellow PLA

# -----------------------------------------------------------------------------
# 1. Stair Step (Fixed reaction base)
# -----------------------------------------------------------------------------
STAIR_STEP_NAME = "stair_step"
STAIR_STEP_MASS_KG = 25.0
STAIR_STEP_FRICTION = 1.2
STAIR_STEP_POS_WORLD = (0.36, 0.0, TABLE_TOP)
STAIR_STEP_DIMS_M = (0.140, 0.400, 0.060)

# Tread top is at z = TABLE_TOP + 0.060 m (0.8075 m)
# Front face is at x = 0.360 - 0.070 = 0.290 m
STAIR_STEP_BOXES = [
    ((0.0, 0.0, 0.030), STAIR_STEP_DIMS_M, COLOR_STAIR_STEP),
]

# -----------------------------------------------------------------------------
# 2. Strip Pad (Fixed staging pad on table)
# -----------------------------------------------------------------------------
STRIP_PAD_NAME = "strip_pad"
STRIP_PAD_MASS_KG = 25.0
STRIP_PAD_FRICTION = 1.2
STRIP_PAD_POS_WORLD = (0.18, 0.0, TABLE_TOP)
STRIP_PAD_DIMS_M = (0.060, 0.440, 0.010)

STRIP_PAD_BOXES = [
    ((0.0, 0.0, 0.005), STRIP_PAD_DIMS_M, COLOR_STRIP_PAD),
]

# -----------------------------------------------------------------------------
# 3. Nosing Strip (Loose L-profile anti-slip strip)
# -----------------------------------------------------------------------------
NOSING_STRIP_NAME = "nosing_strip"
NOSING_STRIP_MASS_KG = 0.15
NOSING_STRIP_FRICTION = 1.2
NOSING_STRIP_DIMS_M = (0.040, 0.380, 0.040)

NOSING_STRIP_START_POS_WORLD = (0.18, 0.0, TABLE_TOP + 0.010)
NOSING_STRIP_TARGET_POS_WORLD = (0.295, 0.0, TABLE_TOP + 0.035)

# L-section compound collision primitives from parts.json:
# 1) Vertical front lip: 15 mm thick x 380 mm length x 40 mm height
# 2) Horizontal top flange: 40 mm width x 380 mm length x 15 mm thickness
NOSING_STRIP_BOXES = [
    ((-0.0125, 0.0, 0.020), (0.015, 0.380, 0.040), COLOR_NOSING_STRIP),
    ((0.0000, 0.0, 0.0325), (0.040, 0.380, 0.015), COLOR_NOSING_STRIP),
]

# Grasp carry points for dual carry (y = +/- 16 cm)
GRASP_LEFT_Y_M = 0.160
GRASP_RIGHT_Y_M = -0.160
DUAL_CARRY_SEPARATION_M = 0.320  # 320 mm (>> 150 mm design target)

# -----------------------------------------------------------------------------
# Scoring Thresholds & Gate Constants
# -----------------------------------------------------------------------------
GATE_BASE_DRIFT_MAX_M = 0.005  # 5 mm fixed base drift limit
GATE_MIN_Z_M = TABLE_TOP - 0.010  # Dropped below table level
GATE_MAX_TILT_DEG = 45.0  # Strip inverted / severely knocked

SCORE_025_LIFT_MIN_Z_M = TABLE_TOP + 0.040  # Lifted > 3 cm off pad
SCORE_050_OVER_STEP_X_MIN_M = 0.260  # Brought over step front edge
SCORE_050_OVER_STEP_X_MAX_M = 0.330
SCORE_075_ENGAGED_MAX_Z_M = TABLE_TOP + 0.075  # Flange lowered near step tread
SCORE_075_MAX_TILT_DEG = 6.0

SCORE_100_FLANGE_Z_TOL_M = 0.0025  # +/- 2.5 mm flush on tread
SCORE_100_LIP_X_TOL_M = 0.0030  # +/- 3.0 mm contacting step front
SCORE_100_ASYMMETRY_Y_TOL_M = 0.0040  # +/- 4.0 mm overhang asymmetry
SCORE_100_MAX_TILT_DEG = 3.0

SUCCESS_HOLD_TIME_S = 1.0
