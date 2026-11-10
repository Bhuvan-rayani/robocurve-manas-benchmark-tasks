"""Physical dimensions, poses, and thresholds for pipe_on_v_stands (T17)."""

from __future__ import annotations

import numpy as np

# Table surface in station scene
TABLE_TOP = 0.7475

# Colours (sRGB 0..1 from asset hex codes)
COLOR_STAND = (169 / 255, 115 / 255, 63 / 255)   # #A9733F wood brown
COLOR_PAD = (138 / 255, 132 / 255, 120 / 255)    # #8A8478 slate grey
COLOR_PIPE = (47 / 255, 161 / 255, 75 / 255)     # #2FA14B green

# V Stands (fixed 25 kg bases at x=0.34 m, y=+/-0.21 m, 42 cm apart)
STAND_A_NAME = "v_stand_a"
STAND_A_POS_WORLD = (0.34, 0.21, TABLE_TOP)
STAND_A_DIMS_M = (0.10, 0.06, 0.12)
STAND_A_MASS_KG = 25.0
STAND_A_FRICTION = 1.2

STAND_B_NAME = "v_stand_b"
STAND_B_POS_WORLD = (0.34, -0.21, TABLE_TOP)
STAND_B_DIMS_M = (0.10, 0.06, 0.12)
STAND_B_MASS_KG = 25.0
STAND_B_FRICTION = 1.2

# V Stand collision boxes: base block + notch sides and slope approximation
STAND_BOXES = (
    # Base block: 100 x 60 x 80 mm
    ((0.0, 0.0, 0.04), (0.10, 0.06, 0.08), COLOR_STAND),
    # Left outer upright horn: 10 x 60 x 40 mm
    ((0.045, 0.0, 0.10), (0.01, 0.06, 0.04), COLOR_STAND),
    # Right outer upright horn: 10 x 60 x 40 mm
    ((-0.045, 0.0, 0.10), (0.01, 0.06, 0.04), COLOR_STAND),
    # Slope fill left: step approximating 45 deg notch
    ((0.022, 0.0, 0.088), (0.020, 0.06, 0.020), COLOR_STAND),
    # Slope fill right: step approximating 45 deg notch
    ((-0.022, 0.0, 0.088), (0.020, 0.06, 0.020), COLOR_STAND),
)

STAND_A_BOXES = STAND_BOXES
STAND_B_BOXES = STAND_BOXES

# Staging pad for pipe (fixed 25 kg base at x=0.18 m, y=0.0 m, 8x50x2 cm)
PIPE_PAD_NAME = "pipe_pad"
PIPE_PAD_POS_WORLD = (0.18, 0.0, TABLE_TOP)
PIPE_PAD_DIMS_M = (0.08, 0.50, 0.02)
PIPE_PAD_MASS_KG = 25.0
PIPE_PAD_FRICTION = 1.2
PIPE_PAD_BOXES = (
    ((0.0, 0.0, 0.01), (0.08, 0.50, 0.02), COLOR_PAD),
)

# Green pipe (loose body, 1.0 kg, 60 cm long x 6 cm dia)
PIPE_NAME = "pipe"
PIPE_RADIUS_M = 0.03
PIPE_DIAMETER_M = 0.06
PIPE_LENGTH_M = 0.60
PIPE_MASS_KG = 1.0
PIPE_FRICTION = 1.2
PIPE_DIMS_M = (PIPE_DIAMETER_M, PIPE_LENGTH_M, PIPE_DIAMETER_M)

# Start pose: resting on pipe_pad (pad top is TABLE_TOP + 0.02, pipe centre at TABLE_TOP + 0.05)
PIPE_START_POS = (0.18, 0.0, TABLE_TOP + 0.02)
PIPE_START_CENTRE = (0.18, 0.0, TABLE_TOP + 0.05)
PIPE_START_QUAT = (0.0, 0.0, 0.0, 1.0)

# Bounding box and cylindrical collision representation in part frame
PIPE_BOXES = (
    ((0.0, 0.0, 0.03), (PIPE_DIAMETER_M, PIPE_LENGTH_M, PIPE_DIAMETER_M), COLOR_PIPE),
)
PIPE_CYLINDERS = (
    ((0.0, 0.0, 0.03), PIPE_RADIUS_M, PIPE_LENGTH_M, COLOR_PIPE, "Y"),
)

# Seated target geometry:
# V notch vertex at z = TABLE_TOP + 0.08 m.
# Cylinder R=0.03 m in 90 deg V rests at z = TABLE_TOP + 0.08 + 0.03 * sqrt(2) = TABLE_TOP + 0.12243 m.
SEATED_X_TARGET_M = 0.34
SEATED_Y_TARGET_M = 0.0
SEATED_Z_TARGET_M = TABLE_TOP + 0.1224
PIPE_TARGET_POS = (SEATED_X_TARGET_M, SEATED_Y_TARGET_M, TABLE_TOP + 0.0924)
PIPE_TARGET_CENTRE = (SEATED_X_TARGET_M, SEATED_Y_TARGET_M, SEATED_Z_TARGET_M)

# Tolerances & Thresholds
DRIFT_STAND_MAX_M = 0.005           # Gate: stand moved > 5 mm = 0
LIFT_Z_MIN_M = 0.05                 # Level 0.25: lifted > 5 cm above start
OVER_STANDS_X_TOL_M = 0.04          # Level 0.50: carried over stands (within 4 cm of stand line)
OVER_STANDS_Z_MIN_M = TABLE_TOP + 0.12  # Level 0.50: height clear of stands

SEATED_ONE_X_TOL_M = 0.020          # Level 0.75: in at least one V stand (x within 20 mm)
SEATED_ONE_Z_TOL_M = 0.015          # Level 0.75: height within 15 mm of seat

SEATED_BOTH_X_TOL_M = 0.010         # Level 1.00: x aligned within 10 mm
SEATED_BOTH_Y_TOL_M = 0.030         # Level 1.00: y centered within 30 mm (9 cm overhang +/- 3 cm)
SEATED_BOTH_Z_TOL_M = 0.012         # Level 1.00: z seated within 12 mm
SEATED_TILT_MAX_RAD = float(np.radians(5.0))  # Level 1.00: axis within 5 degrees of stand line (world Y)

SUCCESS_HOLD_TIME_S = 1.0
