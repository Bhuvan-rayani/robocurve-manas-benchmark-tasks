"""Geometry for air_fryer_basket_unhook_trivet (metres; x forward and y left from the arm midpoint; the table top stands for a bench)."""

from __future__ import annotations

TABLE_TOP = 0.7475

COLOR_HOUSING = (0.227, 0.243, 0.267)
COLOR_PLATE = (0.416, 0.439, 0.471)
COLOR_BASKET = (0.757, 0.341, 0.165)
COLOR_HANDLE = (0.08, 0.08, 0.09)
COLOR_MAT = (0.435, 0.639, 0.478)
COLOR_LAMP = (0.9, 0.05, 0.05)

# Air fryer housing: fixed, 22 x 28 x 26 cm, front face at x 0.46. Lit red lamp on the front face and the top face.
HOUSING_NAME = "af_housing"
HOUSING_CENTRE_XY = (0.57, 0.0)
HOUSING_SIZE = (0.22, 0.28, 0.26)
LAMP_FRONT = ("af_lamp_front", (0.4585, 0.0, 0.18), (0.003, 0.02, 0.02))     # centre (x, y, z above table), size
LAMP_TOP = ("af_lamp_top", (0.57, 0.0, 0.2615), (0.03, 0.03, 0.003))

# Drawer plate: fixed, 18 x 23 x 3.6 cm at (0.37, 0), against the housing. Two hooks: a post and an overhang each.
PLATE_BASE = ("af_plate", (0.37, 0.0, 0.018), (0.18, 0.23, 0.036))
HOOKS = (
    ("af_post_l", (0.447, 0.107, 0.074), (0.02, 0.01, 0.076)),
    ("af_post_r", (0.447, -0.107, 0.074), (0.02, 0.01, 0.076)),
    ("af_hook_l", (0.447, 0.094, 0.108), (0.02, 0.016, 0.008)),   # overhang, underside at z 0.104
    ("af_hook_r", (0.447, -0.094, 0.108), (0.02, 0.016, 0.008)),
)
HOOK_X_FRONT = 0.437               # front end of the overhangs
HOOK_UNDERSIDE_Z = 0.104
PLATE_TOP_Z = 0.036

# Basket: loose steel, 450 g, origin at the centre of the floor's underside. Boxes (centre, size) in the basket frame.
BASKET_NAME = "af_basket"
BASKET_START = (0.372, 0.0, 0.036)              # x, y, z above the table
BASKET_MASS_KG = 0.45
BASKET_FRICTION = 0.32
BASKET_FLOOR = ((0.0, 0.0, 0.0025), (0.17, 0.17, 0.005))
BASKET_WALLS = (
    ((-0.0825, 0.0, 0.0325), (0.005, 0.17, 0.055)),
    ((0.0825, 0.0, 0.0325), (0.005, 0.17, 0.055)),
    ((0.0, 0.0825, 0.0325), (0.16, 0.005, 0.055)),
    ((0.0, -0.0825, 0.0325), (0.16, 0.005, 0.055)),
)
BASKET_FLANGES = (
    ((0.07, 0.0895, 0.0575), (0.03, 0.009, 0.005)),
    ((0.07, -0.0895, 0.0575), (0.03, 0.009, 0.005)),
)
# Handle: two posts 3.7 cm long standing off the front wall, and a bar 4 x 12 x 2 cm across their ends. The bar sits 6.2 cm
# in front of the wall's outer face so that the rear finger of a fully open gripper (4.7 cm + 0.6 cm pad from the bar's
# centre) stays in front of the wall while the fingers close on the bar.
BASKET_HANDLE_POSTS = (
    ((-0.1035, 0.045, 0.045), (0.037, 0.02, 0.03)),
    ((-0.1035, -0.045, 0.045), (0.037, 0.02, 0.03)),
)
BASKET_HANDLE_BAR = ((-0.142, 0.0, 0.05), (0.04, 0.12, 0.02))
BASKET_HOT_BOXES = (BASKET_FLOOR, *BASKET_WALLS, *BASKET_FLANGES)
BASKET_ALL_BOXES = (*BASKET_HOT_BOXES, *BASKET_HANDLE_POSTS, BASKET_HANDLE_BAR)
FLANGE_REAR_LOCAL_X = 0.085         # rear end of the flanges in the basket frame

# Heat-proof mat: fixed, 20 x 20 x 1 cm at (0.35, -0.22).
MAT_NAME = "af_mat"
MAT_CENTRE_XY = (0.35, -0.22)
MAT_SIZE = (0.20, 0.20, 0.01)
MAT_TOP_Z = 0.01

# Scoring tolerances (the same numbers are in task.json).
MAT_MAX_OFFCENTRE_M = 0.010
MAT_MAX_FLOOR_GAP_M = 0.003
MAT_MAX_TILT_DEG = 3.0
MAT_MAX_TURN_DEG = 10.0
UNHOOK_ORIGIN_X_M = HOOK_X_FRONT - FLANGE_REAR_LOCAL_X     # basket origin x below this: flanges clear of the overhangs
SLIDE_MIN_M = 0.028                  # slide toward the robot for the 0.25 level (2.0 cm to clear plus 8 mm)
LIFT_MIN_M = 0.02
HOT_MARGIN_M = 0.012                 # a pad bottom point this close to a hot surface counts as touching
PAD_BELOW_TCP_M = 0.013
RELEASE_MIN_DIST_M = 0.03
TCP_BELOW_LINK_M = 0.138
FINGERS_OPEN_FRACTION = 0.9
STILL_SPEED_M_S = 0.01
SUCCESS_HOLD_TIME_S = 1.0
