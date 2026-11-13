"""Geometry and physical specifications for utility_knife_retract_then_stow."""

from __future__ import annotations

# Table surface in yam_arena
TABLE_TOP = 0.7475

# Colours (sRGB 0..1)
COLOR_KNIFE = (0.890, 0.698, 0.235)     # #E3B23C yellow ABS handle
COLOR_SLIDER = (0.788, 0.808, 0.831)    # #C9CED4 steel blade carrier
COLOR_BUTTON = (0.120, 0.120, 0.140)    # cool-touch black rubber button
COLOR_HOLDER = (0.263, 0.282, 0.310)    # #43484F dark grey holster stand-in

# Knife definition (loose Mech)
LANE_Y = -0.200   # the whole layout sits in front of the right arm (base y -0.30), which does the task alone
KNIFE_START_POS = (0.220, LANE_Y, TABLE_TOP + 0.020)   # lying on the 2 cm cutting mat
KNIFE_MASS = 0.09                        # 90 g
KNIFE_FRICTION = 0.6
KNIFE_FRICTION_DYNAMIC = 0.5

# Knife handle collision box (in knife body frame)
# 3.2 x 19.0 x 1.8 cm handle
KNIFE_HANDLE_BOX = ((0.000, 0.000, 0.009), (0.032, 0.190, 0.018))

# Blade slider definition (prismatic slide joint on knife)
# Mount origin relative to knife body origin
SLIDER_AT = (0.000, -0.0925, 0.0083)
SLIDER_TRAVEL_M = 0.025                 # 25 mm travel along +y
SLIDER_RATE_N_M = 0.0                   # no return spring: a friction-lock slide stays where it is pushed (0.1 N/m let it creep back 1 mm on the GPU)
SLIDER_DAMPING_NS_M = 100.0             # 100 N s/m: holds its place on a flat knife; slow enough (about 6 mm/s) that the push force stays under the knife's friction on the mat
SLIDER_MASS = 0.02                      # 20 g
SLIDER_FRICTION = 1.0

# 2 Slider collision boxes (in slider joint frame)
# 1. Blade carrier box: 1.8 x 5.5 x 0.15 cm (1.5 mm thick, simulator's thinnest)
BLADE_BOX = ((0.000, 0.000, 0.00075), (0.018, 0.055, 0.0015))
# 2. Push button box: 1.4 x 2.0 x 0.8 cm black rubber button
BUTTON_BOX = ((0.000, 0.0325, 0.0162), (0.014, 0.020, 0.012))   # in the slider frame (origin z 8.3 mm): sits on the handle top, z 18.5 to 30.5 mm above the bench

# Holster definition (fixed 25 kg stand-in, mass=None)
# Rubber cutting mat the knife lies on (fixed): 7 x 26 x 2 cm, its +x edge meets the holster
MAT_POS = (0.220, LANE_Y, TABLE_TOP)
MAT_BOX = ((0.000, 0.000, 0.010), (0.070, 0.260, 0.020))  # x 0.185 to 0.255: clear of the holster (x >= 0.258)
COLOR_MAT = (0.180, 0.420, 0.300)       # green self-healing cutting mat

HOLDER_POS = (0.300, LANE_Y, TABLE_TOP)
HOLDER_MASS = 25.0
HOLDER_FRICTION = 1.2

# 5 Holster collision boxes (in holster origin frame)
# Pocket inside is 5.2 x 20.6 x 2.6 cm (10 mm play each side of the 3.2 cm handle, the stow tolerance); floor at z = 0.004 m
HOLDER_BOXES = [
    ((0.000, 0.000, 0.002), (0.084, 0.236, 0.004)),      # floor (4 mm thick)
    ((0.034, 0.000, 0.017), (0.016, 0.236, 0.026)),      # +x outer wall
    ((-0.034, 0.000, 0.017), (0.016, 0.236, 0.026)),     # -x outer wall
    ((0.000, 0.1105, 0.017), (0.052, 0.015, 0.026)),     # +y end wall
    ((0.000, -0.1105, 0.017), (0.052, 0.015, 0.026)),    # -y end wall
]

# Keep-out and contact scoring specifications
PAD_BOX_SIZE = (0.012, 0.012, 0.012)    # 12 mm cube
PAD_BOX_HALF = (0.006, 0.006, 0.006)
BLADE_INFLATION_M = 0.003               # 3 mm inflation of blade box
KEEPOUT_ACTIVE_DISP_M = 0.024           # active while slider displacement < 24 mm

# Scoring thresholds
RETRACTED_DISP_M = 0.0225               # displacement >= 22.5 mm (90%)
POCKET_CENTRE = (0.300, LANE_Y)
STOWED_TOL_X_M = 0.010                  # 10 mm in x
STOWED_TOL_Y_M = 0.015                  # 15 mm in y
STOWED_BASE_Z_MAX = TABLE_TOP + 0.009   # base z <= 0.9 cm above table top
TILT_MAX_DEG = 5.0                      # tilt <= 5 degrees
RELEASE_MIN_DIST_M = 0.030              # 3 cm clearance
STILL_MOTION_M = 0.001                  # 1 mm peak-to-peak motion
STILL_WINDOW_STEPS = 20                 # 1.0 s at 20 Hz

# TCP and ready poses
TCP_BELOW_LINK_M = 0.134  # yam_arena TCP_OFFSET: the tool point sits 0.134 m below the gripper link (measured on the GPU)
L_READY = (0.100, 0.140, TABLE_TOP + 0.120)
R_READY = (0.100, -0.140, TABLE_TOP + 0.120)
