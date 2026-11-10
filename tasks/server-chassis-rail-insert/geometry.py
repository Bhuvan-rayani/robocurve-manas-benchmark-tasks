"""Geometry, masses, colours, and positions for server_chassis_rail_insert."""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_POST_TEAL = (0 / 255, 163 / 255, 163 / 255)         # #00A3A3
COLOR_RAIL_STEEL = (169 / 255, 179 / 255, 190 / 255)     # #A9B3BE
COLOR_CHASSIS_SILVER = (122 / 255, 133 / 255, 145 / 255) # #7A8591
COLOR_PLATE_GREY = (71 / 255, 77 / 255, 84 / 255)        # #474D54

# Posts are 39 cm apart (inner 36 cm) and the chassis is 23 cm wide with 5 cm ear tabs out to y +-0.185: both hands can push the body face at y +-0.095, 19 cm apart,
# because the arms collide when the hands are closer than ~19 cm near the bases (GPU runs 1 and 2 of this task).
# Rack posts (fixed teal PLA posts at front face x=39 cm, inside spacing 22 cm). The whole rack is 12 cm further out than the first version so the
# hands push the chassis from x >= 0.16: GPU run 1 showed the arm cannot reach low waypoints at x = 0.04.
POST_A_POS_WORLD = (0.405, 0.195, TABLE_TOP + 0.100)
POST_B_POS_WORLD = (0.405, -0.195, TABLE_TOP + 0.100)
POST_DIMS_M = (0.030, 0.030, 0.200)
POST_FRONT_FACE_X = 0.390
POST_MASS_KG = 0.22

# Staging plate (fixed grey PLA plate, 270x120x60 mm, top at z = 6 cm above table)
PLATE_POS_WORLD = (0.285, 0.0, TABLE_TOP + 0.030)
PLATE_DIMS_M = (0.270, 0.120, 0.060)
PLATE_MASS_KG = 25.0

# Rails: inner faces at y = +-0.127, i.e. 12 mm clearance per side for the 230 mm chassis (open-loop hand wobbles +-6 mm; was 3 mm)
# (fixed steel rails with 2.2 cm bottom ledge and side guide wall)
RAIL_START_X = 0.420
RAIL_LENGTH_M = 0.240
RAIL_MASS_KG = 0.50

RAIL_A_WALL_POS = (0.540, 0.133, TABLE_TOP + 0.0675)
RAIL_A_WALL_SIZE = (0.240, 0.012, 0.015)
RAIL_A_LEDGE_POS = (0.540, 0.123, TABLE_TOP + 0.059)
RAIL_A_LEDGE_SIZE = (0.240, 0.032, 0.002)

RAIL_B_WALL_POS = (0.540, -0.133, TABLE_TOP + 0.0675)
RAIL_B_WALL_SIZE = (0.240, 0.012, 0.015)
RAIL_B_LEDGE_POS = (0.540, -0.123, TABLE_TOP + 0.059)
RAIL_B_LEDGE_SIZE = (0.240, 0.032, 0.002)

# Chassis (aluminium 1U server box: 240x190x44 mm, 700 g, with two 20 mm ear tabs)
CHASSIS_START_POS = (0.290, 0.0, TABLE_TOP + 0.060)
CHASSIS_MASS_KG = 0.70
CHASSIS_FRICTION = 0.3   # aluminium on a steel ledge; at 1.2 the 0.7 kg chassis needed ~8 N to slide, far more than the arms can push evenly
CHASSIS_BODY_DIMS_M = (0.240, 0.230, 0.044)
CHASSIS_EAR_DIMS_M = (0.004, 0.050, 0.044)

# Collision boxes in chassis body frame (origin at base centre)
CHASSIS_BOXES = (
    ((0.0, 0.0, 0.022), (0.240, 0.230, 0.044), COLOR_CHASSIS_SILVER),
    ((-0.118, 0.160, 0.022), (0.004, 0.050, 0.044), COLOR_CHASSIS_SILVER),
    ((-0.118, -0.160, 0.022), (0.004, 0.050, 0.044), COLOR_CHASSIS_SILVER),
)

# Relative coordinates of ears in chassis frame
EAR_BACK_LOCAL_X = -0.116
EAR_FRONT_LOCAL_X = -0.120
CHASSIS_REAR_LOCAL_X = 0.120
CHASSIS_GOAL_X = POST_FRONT_FACE_X - EAR_BACK_LOCAL_X  # 0.390 - (-0.116) = 0.506 m

# Scoring thresholds
MAX_POST_DISPLACEMENT_GATE_M = 0.005  # 5 mm post drift gate
MAX_TILT_GATE_DEG = 15.0              # 15 degrees tilt gate
MAX_LATERAL_DRIFT_GATE_M = 0.050      # 5 cm lateral drift gate

LIFT_SCORE_THRESHOLD_M = 0.020        # > 2 cm lift (ladder 0.25)
SLIDE_START_THRESHOLD_M = 0.020       # >= 2 cm advance (ladder 0.25)
RAIL_DEPTH_STAGE1_M = 0.060           # >= 6 cm in rails (ladder 0.50)
RAIL_DEPTH_STAGE2_M = 0.150           # >= 15 cm in rails (ladder 0.75)
FLUSH_TOLERANCE_M = 0.003             # <= 3 mm from post face (ladder 1.00)
SUCCESS_TILT_MAX_DEG = 5.0            # < 5 degrees tilt (ladder 1.00)
SUCCESS_HOLD_TIME_S = 1.0
