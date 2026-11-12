"""Geometry, masses, colours, and positions for floor_opening_cover."""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_FLOOR_BOARD = (107 / 255, 114 / 255, 122 / 255)  # #6B727A
COLOR_COVER_PLATE = (214 / 255, 40 / 255, 40 / 255)    # #D62828
COLOR_PLATE_STAND = (75 / 255, 81 / 255, 88 / 255)     # #4B5158
COLOR_WEDGE_PIN = (255 / 255, 209 / 255, 0 / 255)      # #FFD100
COLOR_PIN_RACK = (138 / 255, 145 / 255, 153 / 255)     # #8A9199

# Floor board (fixed base)
BOARD_POS_WORLD = (0.30, 0.0, TABLE_TOP)
BOARD_DIMS_M = (0.34, 0.44, 0.05)
BOARD_MASS_KG = 25.0
BOARD_FRICTION = 1.2
BOARD_TOP_Z = TABLE_TOP + BOARD_DIMS_M[2]  # 0.7975 m

# Opening in floor board (16 x 16 cm centred at (0.30, 0.0))
OPENING_HALF_X = 0.08
OPENING_HALF_Y = 0.08
OPENING_X_MIN = BOARD_POS_WORLD[0] - OPENING_HALF_X  # 0.22 m
OPENING_X_MAX = BOARD_POS_WORLD[0] + OPENING_HALF_X  # 0.38 m
OPENING_Y_MIN = BOARD_POS_WORLD[1] - OPENING_HALF_Y  # -0.08 m
OPENING_Y_MAX = BOARD_POS_WORLD[1] + OPENING_HALF_Y  # +0.08 m

# Locking slots in floor board (26 x 26 mm, 15 mm deep, at x 0.24, y = +/-13 cm): 7 mm per side around a 12 mm pin
SLOT_Y = 0.13
SLOT_X = 0.24  # 60 mm west of the board centre: clear of the plate handle (x 0.28-0.32) and closer to the arms
SLOT_A_POS = (SLOT_X, +SLOT_Y, BOARD_TOP_Z)  # (0.24, +0.13)
SLOT_B_POS = (SLOT_X, -SLOT_Y, BOARD_TOP_Z)  # (0.24, -0.13)
SLOT_SIZE_M = (0.026, 0.026, 0.015)
SLOT_FLOOR_Z = BOARD_TOP_Z - SLOT_SIZE_M[2]           # TABLE_TOP + 0.035 m

# Cover plate (free body, 22 x 22 x 1 cm, 400 g)
PLATE_DIMS_M = (0.22, 0.22, 0.01)
PLATE_MASS_KG = 0.40
# Grip handle at the centre of the plate's top face: 4 cm along x, 8 cm along y, 2 cm tall. The gripper (opening
# 94 mm) closes across the 4 cm side (yaw -90 for the left arm). Handle centre in the plate frame (origin = plate
# centre). Centred, so the plate hangs level from the grip. (An edge handle at y +0.10 cannot be reached by the
# left arm at yaw 90 / -90 from the plate stand: IK fails at y 0.43 for x 0.16, and at y 0.10 for yaw +90.)
HANDLE_DIMS_M = (0.04, 0.08, 0.02)
HANDLE_CENTRE_M = (0.0, 0.0, 0.005 + 0.010)
PLATE_HALF_X = PLATE_DIMS_M[0] / 2.0  # 0.11 m
PLATE_HALF_Y = PLATE_DIMS_M[1] / 2.0  # 0.11 m
PLATE_HALF_Z = PLATE_DIMS_M[2] / 2.0  # 0.005 m
PLATE_START_POS = (0.16, 0.33, TABLE_TOP + 0.030 + PLATE_HALF_Z)  # (0.16, 0.33, TABLE_TOP + 0.035)
PLATE_GOAL_POS = (BOARD_POS_WORLD[0], BOARD_POS_WORLD[1], BOARD_TOP_Z + PLATE_HALF_Z)

# Plate stand (fixed, 18 x 18 x 3 cm, 25 kg)
STAND_DIMS_M = (0.18, 0.18, 0.03)
STAND_MASS_KG = 25.0
STAND_POS_WORLD = (0.16, 0.33, TABLE_TOP + STAND_DIMS_M[2] / 2.0)

# Wedge pins (12 x 12 x 40 mm, 15 g each)
PIN_DIMS_M = (0.012, 0.012, 0.040)
PIN_MASS_KG = 0.015
PIN_HALF_Z = PIN_DIMS_M[2] / 2.0  # 0.020 m
# Pin A stands on the left rack (left arm), pin B on the right rack (right arm); each arm stays on its own side.
PIN_A_START_POS = (0.30, 0.33, TABLE_TOP + 0.025 + PIN_HALF_Z)
PIN_B_START_POS = (0.16, -0.33, TABLE_TOP + 0.025 + PIN_HALF_Z)

# Pin rack (fixed, 8 x 16 x 2.5 cm, 25 kg)
RACK_DIMS_M = (0.080, 0.160, 0.025)
RACK_MASS_KG = 25.0
RACK_POS_WORLD = (0.16, -0.33, TABLE_TOP + RACK_DIMS_M[2] / 2.0)

# Left pin rack (fixed, 8 x 8 x 2.5 cm, 25 kg) holds pin A
LRACK_DIMS_M = (0.080, 0.080, 0.025)
LRACK_POS_WORLD = (0.30, 0.33, TABLE_TOP + LRACK_DIMS_M[2] / 2.0)

# Scoring thresholds
MIN_OVERHANG_M = 0.020        # Overhang >= 20 mm on all four sides
MIN_SEATED_DEPTH_M = 0.010    # Pin seated >= 10 mm in slot
MAX_PLATE_TILT_DEG = 3.0      # Plate flat within 3 degrees
MAX_BOARD_DRIFT_M = 0.005     # 5 mm gate on floor board movement
MIN_PLATE_LIFT_M = 0.020      # Plate lifted > 2 cm from stand
SUCCESS_HOLD_TIME_S = 1.0     # Success hold duration
RUN_LIMIT_STEPS = 2400        # Run limit: 2,400 steps (2 minutes at 20 Hz)

# Floor board collision boxes in the board frame (origin at the board's base centre): perimeter walls, a thin
# floor layer (z 30-35 mm) under everything except the opening, and a top layer (z 35-50 mm) cut by the 16 x 16 cm
# opening and the two 26 x 26 mm slots. The slot floor is the thin layer (15 mm below the board top).
def _build_board_boxes():
    c = COLOR_FLOOR_BOARD
    boxes = [
        ((0.165, 0.0, 0.015), (0.01, 0.44, 0.03), c),
        ((-0.165, 0.0, 0.015), (0.01, 0.44, 0.03), c),
        ((0.0, 0.215, 0.015), (0.32, 0.01, 0.03), c),
        ((0.0, -0.215, 0.015), (0.32, 0.01, 0.03), c),
    ]
    xs = [-0.17, -0.08, 0.08, 0.17]
    ys = [-0.22, -0.08, 0.08, 0.22]
    # floor layer: 3 x 3 grid minus the centre cell
    for i in range(3):
        for j in range(3):
            if i == 1 and j == 1:
                continue
            boxes.append((((xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2, 0.0325),
                          (xs[i + 1] - xs[i], ys[j + 1] - ys[j], 0.005), c))
    # top layer: x breaks around the slot (|x| < h), y breaks around the slots
    h = SLOT_SIZE_M[0] / 2.0
    sx = SLOT_X - BOARD_POS_WORLD[0]
    xt = [-0.17, -0.08, sx - h, sx + h, 0.08, 0.17]
    sy0, sy1 = SLOT_Y - SLOT_SIZE_M[1] / 2.0, SLOT_Y + SLOT_SIZE_M[1] / 2.0
    yt = [-0.22, -sy1, -sy0, -0.08, 0.08, sy0, sy1, 0.22]
    for i in range(len(xt) - 1):
        for j in range(len(yt) - 1):
            xc, yc = (xt[i] + xt[i + 1]) / 2, (yt[j] + yt[j + 1]) / 2
            wx, wy = xt[i + 1] - xt[i], yt[j + 1] - yt[j]
            in_opening = abs(xc) < 0.08 and abs(yc) < 0.08
            in_slot = abs(xc - sx) < h and sy0 < abs(yc) < sy1
            if in_opening or in_slot:
                continue
            boxes.append(((xc, yc, 0.0425), (wx, wy, 0.015), c))
    return tuple(boxes)


BOARD_BOXES = _build_board_boxes()
