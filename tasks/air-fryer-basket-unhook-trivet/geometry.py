"""Geometry and physical specifications for air_fryer_basket_release_button_v2."""

from __future__ import annotations

import math
import numpy as np

# Table surface in yam_arena
TABLE_TOP = 0.7475

# Colours (sRGB 0..1)
COLOR_HOUSING = (0.369, 0.384, 0.408)    # #5E6268 heat-tinted grey
COLOR_DRAWER = (0.784, 0.267, 0.122)     # #C8441F orange painted steel
COLOR_BASKET = (0.824, 0.271, 0.118)     # #D2451E orange fry basket
COLOR_HANDLE = (0.120, 0.120, 0.140)     # #1E1E24 cool-touch black rubber
COLOR_BUTTON = (0.231, 0.435, 0.839)     # #3B6FD6 blue ABS release button
COLOR_MAT = (0.478, 0.180, 0.180)        # #7A2E2E dark red silicone mat
COLOR_AMBER = (0.950, 0.550, 0.100)      # amber glow tiles and heating lamp

# Mat definition (fixed on table beside drawer)
MAT_CENTRE = (0.384, -0.410, TABLE_TOP)   # a 30 x 30 cm silicone trivet mat on the right of the appliance; its +y edge (y -0.26) clears the housing board (y -0.25)
MAT_SIZE = (0.300, 0.300, 0.010)
MAT_X_MIN = 0.234
MAT_X_MAX = 0.534
MAT_Y_MIN = -0.560
MAT_Y_MAX = -0.260
MAT_TOP_Z = TABLE_TOP + 0.010
MAT_Z_TOL = 0.005
TILT_MAX_DEG = 5.0

# Housing definition (fixed, mass=None)
HOUSING_POS = (0.650, -0.120, TABLE_TOP + 0.030)   # on a 3 cm stand so the handle and release button are within the arm's low reach
HOUSING_MASS = 25.0
HOUSING_FRICTION = 1.2

# Heat-resistant board the appliance stands on (part of the fixed housing, not hot): fills the 3 cm under the housing
STAND_BOX = ((0.000, 0.000, -0.015), (0.260, 0.260, 0.030))
COLOR_STAND = (0.690, 0.545, 0.369)     # #B08B5E bamboo board

# 5 Housing collision boxes (all hot: true) - relative to housing origin
HOUSING_BOXES = [
    ((0.000, 0.000, 0.002), (0.260, 0.260, 0.004), True),    # floor
    ((0.000, 0.000, 0.185), (0.260, 0.260, 0.190), True),    # top & panel
    ((0.122, 0.000, 0.047), (0.016, 0.260, 0.086), True),    # back wall
    ((0.000, 0.1235, 0.047), (0.260, 0.013, 0.086), True),   # left wall
    ((0.000, -0.1235, 0.047), (0.260, 0.013, 0.086), True),  # right wall
]

# Drawer slide definition (joint on housing)
DRAWER_AT = (-0.265, 0.000, 0.006)   # relative to housing origin (pulled out at start)
DRAWER_MASS = 0.8
DRAWER_TRAVEL_M = 0.255
DRAWER_RATE_N_M = 4.0
DRAWER_DAMPING_NS_M = 30.0

# 9 Drawer collision boxes (all hot: true) - relative to drawer origin
DRAWER_BOXES = [
    ((0.000, 0.000, 0.003), (0.240, 0.224, 0.006), True),     # floor
    ((0.000, 0.109, 0.041), (0.240, 0.006, 0.070), True),     # left wall
    ((0.000, -0.109, 0.041), (0.240, 0.006, 0.070), True),    # right wall
    ((0.117, 0.000, 0.041), (0.006, 0.224, 0.070), True),     # back wall
    ((-0.117, 0.000, 0.019), (0.006, 0.224, 0.026), True),   # front bottom strip
    ((-0.117, 0.106, 0.0565), (0.006, 0.012, 0.041), True),   # front left remnant
    ((-0.117, -0.106, 0.0565), (0.006, 0.012, 0.041), True),  # front right remnant
    ((-0.117, 0.095, 0.058), (0.006, 0.010, 0.008), True),    # catch ledge left
    ((-0.117, -0.095, 0.058), (0.006, 0.010, 0.008), True),   # catch ledge right
]

# Basket definition (loose Mech)
BASKET_START_POS = (0.384, -0.120, TABLE_TOP + 0.047)
BASKET_MASS = 0.35
BASKET_FRICTION = 0.4

# 5 Basket body collision boxes (all hot: true) - relative to basket origin
BASKET_BODY_BOXES = [
    ((-0.024, 0.000, 0.000), (0.178, 0.204, 0.010), True),   # floor (with 5 mm feet stand-in); x -0.113 to 0.065
    ((-0.024, 0.100, 0.035), (0.178, 0.004, 0.060), True),   # left wall
    ((-0.024, -0.100, 0.035), (0.178, 0.004, 0.060), True),  # right wall
    ((0.063, 0.000, 0.035), (0.004, 0.204, 0.060), True),    # back wall: 49 mm play to the drawer's back wall so the basket can pitch as it is lifted by its front handle (GPU r79: 17 mm jammed it at 11 deg)
    ((-0.111, 0.000, 0.035), (0.004, 0.155, 0.060), True),   # front wall with a 20 mm slot at each side for the catch lugs
]

# 3 Handle collision boxes (touchable, hot: false) - relative to basket origin
BASKET_HANDLE_BOXES = [
    ((-0.131, 0.025, 0.0355), (0.036, 0.014, 0.025), False),   # left post
    ((-0.131, -0.025, 0.0355), (0.036, 0.014, 0.025), False),  # right post
    ((-0.1615, 0.000, 0.0355), (0.025, 0.180, 0.025), False),  # cool-touch bar
]

# Basket floor half extents for corner checks
BASKET_FLOOR_HALF_X = 0.113   # front half (handle side)
BASKET_FLOOR_BACK_X = 0.065   # back edge of the floor (the basket is 17.8 cm long)
BASKET_FLOOR_HALF_Y = 0.102

# Release button definition (slide joint on basket)
BUTTON_AT = (-0.1815, 0.000, 0.028)    # relative to basket origin
BUTTON_MASS = 0.04
BUTTON_TRAVEL_M = 0.014
BUTTON_RATE_N_M = 8.0
BUTTON_DAMPING_NS_M = 5.0
BUTTON_CLEARANCE_DISPLACEMENT_M = 0.006 # at 6 mm travel, catches clear ledges
BUTTON_OUT_THRESHOLD_M = 0.0009         # >= 90% extended (<= 0.9 mm displaced)

# 3 Button collision boxes (touchable, hot: false) - relative to button joint origin
BUTTON_BOXES = [
    ((-0.010, 0.000, 0.005), (0.005, 0.100, 0.030), False),  # 30 mm tall: covers the bar's whole front face (bar z 7.0 to 9.5 cm) so a pushing finger cannot slip under it onto the bar;    # button cap: a 5 mm plate, face at the same x, so a full 9 mm stroke stays clear of the handle bar (sibling collision)
    ((0.0675, 0.090, 0.004), (0.012, 0.010, 0.010), False),   # catch lug left: 6 mm under its ledge at rest, 3 mm past it at full travel (test_catch_lugs_hold_then_clear)
    ((0.0675, -0.090, 0.004), (0.012, 0.010, 0.010), False),  # catch lug right
]

# Mat box (touchable, hot: false) - relative to mat origin
MAT_BOXES = [
    ((0.000, 0.000, 0.005), (0.300, 0.300, 0.010), False),
]

# Contact scoring dimensions
PAD_BOX_SIZE = (0.012, 0.012, 0.012)   # 12 mm cube
PAD_BOX_HALF = (0.006, 0.006, 0.006)
HOT_INFLATION_M = 0.002                # 2 mm inflation of hot boxes
RELEASE_MIN_DIST_M = 0.030             # 3 cm clearance from basket/handle/button
STILL_MOTION_M = 0.001                 # 1 mm peak-to-peak motion
STILL_WINDOW_STEPS = 20                # 1.0 s at 20 Hz
BASKET_CLEARED_DRAWER_Z = TABLE_TOP + 0.120  # 9 cm above table
BASKET_LIFT_MIN_M = 0.020              # 20 mm lift above start

# TCP and ready poses
TCP_BELOW_LINK_M = 0.134  # yam_arena TCP_OFFSET: the tool point sits 0.134 m below the gripper link (measured on the GPU)
R_READY = (0.100, -0.220, TABLE_TOP + 0.120)
L_READY = (0.100, 0.140, TABLE_TOP + 0.120)

# Display markers (VisualizationMarkers, _Tiles pattern)
VENT_GLOW_TILES_LOCAL = [
    (0.040, 0.040, 0.281),
    (0.040, -0.040, 0.281),
    (-0.040, 0.040, 0.281),
    (-0.040, -0.040, 0.281),
]
LAMP_TILE_LOCAL = (-0.080, 0.000, 0.281)
