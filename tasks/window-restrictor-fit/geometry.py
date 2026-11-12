"""Geometry, masses, colours, and positions for window_restrictor_fit.

Redesign (offline screen): the left arm seats the cyan stop block in one of three wide floor pockets, the right arm then
pushes the sash open from behind until the block stops it. The sash holds where it is pushed (spring ~0, high damping).
The pocket is 30 x 30 mm for a 16 mm peg (7 mm per side), and the block ends up against the pocket's +y wall once the
sash pushes it, so the final opening does not depend on where the hand dropped the block.
"""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_FRAME_BROWN = (107 / 255, 62 / 255, 31 / 255)   # #6B3E1F
COLOR_SASH_WHITE = (244 / 255, 244 / 255, 244 / 255)   # #F4F4F4
COLOR_BLOCK_CYAN = (0 / 255, 200 / 255, 215 / 255)    # #00C8D7
COLOR_PAD_GREY = (141 / 255, 147 / 255, 155 / 255)    # #8D939B

# Window Frame specs
FRAME_POS_WORLD = (0.30, 0.0, TABLE_TOP)
FRAME_DIMS_M = (0.250, 0.380, 0.030)
FRAME_MASS_KG = 25.0
FRAME_FRICTION = 1.2

# Stop block: 30 x 30 x 30 mm body on a 16 mm round peg 6 mm long (origin = body bottom, peg below it)
BLOCK_BODY_M = (0.030, 0.030, 0.030)
PEG_RADIUS_M = 0.008
PEG_LEN_M = 0.006

# Floor pockets (through the 6 mm floor), 30 x 30 mm: peg clearance per side = 15 - 8 = 7 mm
FLOOR_T_M = 0.006
POCKET_SIZE_M = 0.030
PEG_CLEARANCE_PER_SIDE_M = POCKET_SIZE_M / 2 - PEG_RADIUS_M
# Pocket centres along y in the frame, and the opening each one allows once the block is pushed to the +y pocket wall:
# opening = block_y + 0.015 (sash front edge starts at y -0.03, block half width 15 mm), block_y = centre + clearance
HOLE_Y_COORDS = (0.028, 0.078, 0.128)
BLOCK_HALF_Y_M = BLOCK_BODY_M[1] / 2
SASH_FRONT_REST_Y_M = -0.03
HOLE_OPENINGS_M = tuple(
    round(c + PEG_CLEARANCE_PER_SIDE_M - BLOCK_HALF_Y_M - SASH_FRONT_REST_Y_M, 6) for c in HOLE_Y_COORDS
)  # 0.050, 0.100, 0.150 (sash front = -0.03 + opening touches the block's -y face at block_y - 0.015)

_X, _Y = FRAME_DIMS_M[0] / 2, FRAME_DIMS_M[1] / 2
_H = POCKET_SIZE_M / 2


def _floor_boxes():
    boxes = []
    z = FLOOR_T_M / 2
    edges = [-_Y]
    for c in HOLE_Y_COORDS:
        edges += [c - _H, c + _H]
    edges.append(_Y)
    # solid strips between pockets (full width)
    for i in range(0, len(edges), 2):
        y0, y1 = edges[i], edges[i + 1]
        boxes.append(((0.0, (y0 + y1) / 2, z), (2 * _X, y1 - y0, FLOOR_T_M), COLOR_FRAME_BROWN))
    # strips either side of each pocket
    for c in HOLE_Y_COORDS:
        w = _X - _H
        for sx in (-1, 1):
            boxes.append(((sx * (_H + w / 2), c, z), (w, POCKET_SIZE_M, FLOOR_T_M), COLOR_FRAME_BROWN))
    return boxes


# Rails and end walls around the channel (as in the original frame)
_RAILS = (
    ((-0.1185, 0.0, 0.018), (0.013, 0.34, 0.024), COLOR_FRAME_BROWN),
    ((0.1185, 0.0, 0.018), (0.013, 0.34, 0.024), COLOR_FRAME_BROWN),
    ((0.0, -0.18, 0.018), (0.224, 0.02, 0.024), COLOR_FRAME_BROWN),
    ((0.0, 0.18, 0.018), (0.224, 0.02, 0.024), COLOR_FRAME_BROWN),
)
FRAME_BOXES = tuple(_floor_boxes()) + _RAILS

# Sash Pane specs (slider on window_frame along +Y); it stays where it is pushed
SASH_NAME = "sash_pane"
SASH_DIMS_M = (0.220, 0.140, 0.020)
SASH_MASS_KG = 0.15
SASH_REST_PART = (0.0, -0.10, 0.006)
SASH_TRAVEL_M = 0.120
SASH_SPRING_RATE = 0.001   # N/m: stays where pushed (the arm cannot hold a stiff spring)
SASH_DAMPING = 50.0        # N s/m
SASH_AXIS = "+Y"

# Sash: plate on the floor (top at +0.016) and a rear push tab 20 mm thick, 45 mm proud (top at +0.061)
SASH_TAB_Y_M = -0.16
SASH_TAB_PROUD_M = 0.045
SASH_BOXES = (
    ((0.0, -0.10, 0.011), (0.220, 0.140, 0.010), COLOR_SASH_WHITE),
    ((0.0, SASH_TAB_Y_M, 0.016 + SASH_TAB_PROUD_M / 2), (0.080, 0.020, SASH_TAB_PROUD_M), COLOR_SASH_WHITE),
)

# Stop Pad specs (fixed datum pad for stop block), on the LEFT side
PAD_NAME = "stop_pad"
PAD_POS_WORLD = (0.14, 0.20, TABLE_TOP + 0.0025)
PAD_SIZE_M = (0.060, 0.060, 0.005)
PAD_MASS_KG = 0.06

# Stop Block specs (movable cyan restrictor block with round peg); peg bottom rests on the pad top
BLOCK_NAME = "stop_block"
BLOCK_START_POS_WORLD = (0.14, 0.20, TABLE_TOP + PAD_SIZE_M[2] + PEG_LEN_M)
BLOCK_DIMS_M = (0.030, 0.030, 0.036)
BLOCK_MASS_KG = 0.020
BLOCK_FRICTION = 1.2

BLOCK_BOXES = (
    ((0.0, 0.0, BLOCK_BODY_M[2] / 2), BLOCK_BODY_M, COLOR_BLOCK_CYAN),
)
BLOCK_CYLINDERS = (
    ((0.0, 0.0, -PEG_LEN_M / 2), PEG_RADIUS_M, PEG_LEN_M, COLOR_BLOCK_CYAN, "Z"),
)

# Target: 100 mm opening restrictor pocket (index 1, y = 0.078 m)
TARGET_HOLE_INDEX = 1
TARGET_HOLE_Y = HOLE_Y_COORDS[TARGET_HOLE_INDEX]
TARGET_HOLE_POS_WORLD = (0.30, TARGET_HOLE_Y, TABLE_TOP + FLOOR_T_M)
TARGET_OPENING_M = 0.100

# Scoring tolerances & thresholds
MAX_FRAME_DRIFT_GATE_M = 0.005      # 5 mm gate
BLOCK_LIFT_Z_THRESHOLD_M = 0.008    # lifted > 8 mm off pad
BLOCK_LIFT_XY_THRESHOLD_M = 0.020   # moved > 20 mm from pad
BLOCK_TRACK_X_TOLERANCE_M = 0.010   # centred within 10 mm along X (pocket allows 7 mm)
PEG_SEATED_Z_MAX_M = TABLE_TOP + FLOOR_T_M + 0.002  # body bottom within 2 mm of the floor top = peg >= 4 mm in
HOLE_MATCH_Y_TOLERANCE_M = 0.010    # within 10 mm along Y of a pocket centre (pocket allows +-7 mm)
SASH_TOUCH_TOL_M = 0.006            # sash front within 6 mm of the block face = constrained by the block
TARGET_OPENING_MIN_M = 0.095        # 95 mm
TARGET_OPENING_MAX_M = 0.105        # 105 mm
MAX_OPENING_LADDER_075_M = 0.119    # sash stopped short of its 120 mm end stop
GRIPPER_CLEARANCE_MIN_M = 0.030     # 30 mm
SUCCESS_HOLD_TIME_S = 1.0           # 1.0 s
