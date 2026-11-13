"""Geometry for receipt_printer_roll_reload (metres; x forward and y left from the arm midpoint; the table top stands for a bench).

Frames: z of a part is its height above the table top. The printer part's origin is the centre of its base on the table; the
cover is a slider of the printer part (its shapes are given in the printer frame at rest). The roll part's origin is the
bottom of the paper cylinder on its axis: the cylinder axis runs along the part's y, the paper tail runs along the part's +x
and lies 3 mm under the cylinder (z -0.003 to 0). The stand part's origin is the centre of its plate on the table.
"""

from __future__ import annotations

import math

TABLE_TOP = 0.7475

COLOR_BODY = (0.17, 0.18, 0.20)        # charcoal ABS
COLOR_COVER = (0.10, 0.11, 0.13)       # darker ABS
COLOR_RIB = (0.22, 0.23, 0.25)
COLOR_WINDOW = (0.55, 0.70, 0.78)      # clear window
COLOR_TAB = (0.12, 0.34, 0.85)         # blue push tab
COLOR_BEZEL = (0.05, 0.05, 0.06)
COLOR_BUTTON = (0.62, 0.64, 0.67)
COLOR_PAPER = (0.95, 0.94, 0.90)
COLOR_CORE = (0.62, 0.46, 0.28)        # cardboard core
COLOR_TAPE = (0.90, 0.45, 0.10)        # tape on the paper's free end
COLOR_STAND = (0.12, 0.12, 0.13)       # rubber
COLOR_LAMP_RED = (0.95, 0.05, 0.05)
COLOR_LAMP_GREEN = (0.05, 0.85, 0.20)
COLOR_LAMP_AMBER = (1.0, 0.62, 0.0)

# -- printer: fixed (a 25 kg stand-in for a bolted-down printer), 14 x 20 x 10 cm, front face at x 0.19, rear face at 0.33 ---------
PRINTER_NAME = "rp_printer"
PRINTER_XY = (0.26, 0.0)
PRINTER_SIZE = (0.14, 0.20, 0.100)
PRINTER_MASS_KG = 25.0
PRINTER_FRICTION = 1.2
FRONT_FACE_X = PRINTER_XY[0] - PRINTER_SIZE[0] / 2        # 0.19
BAY_FLOOR_Z = 0.03                                         # top of the base slab: the bay floor and the chute top
WALL_TOP_Z = PRINTER_SIZE[2]                               # the cover rests on the walls' tops
# Bay facts used by the scorer and the tests (absolute x, y; z above the table).
BAY_X_RANGE = (0.21, 0.292)            # interior between the front posts and the rear wall: 8.2 cm
CRADLE_HALF_WIDTH_M = 0.034            # the roll's channel between the shoulders: 6.8 cm (58 mm roll + 5 mm per side)
FINGER_RECESS_HALF_WIDTH_M = 0.065     # the bay opens to 13 cm above the shoulders, for the gripper pads
NOTCH_HALF_WIDTH_M = 0.045             # the exit notch in the front wall: 9 cm (58 mm paper + 16 mm per side), open to the cover
SHOULDER_TOP_Z = 0.042
CHUTE_X_RANGE = (0.11, FRONT_FACE_X)
_SIDE = PRINTER_SIZE[1] / 2            # 0.10


def _mirror_y(centre_x, y_lo, y_hi, z_c, size_x, size_z, colour):
    """The same box on both sides of y = 0: (centre, size, colour) for y in [y_lo, y_hi] and [-y_hi, -y_lo]."""
    yc, sy = (y_lo + y_hi) / 2, y_hi - y_lo
    return (((centre_x, yc, z_c), (size_x, sy, size_z), colour), ((centre_x, -yc, z_c), (size_x, sy, size_z), colour))


# Printer-frame boxes: (centre, size, colour).
PRINTER_BOXES = (
    ((0.0, 0.0, 0.015), (0.14, 0.20, 0.03), COLOR_BODY),                       # base slab
    *_mirror_y(-0.06, NOTCH_HALF_WIDTH_M, _SIDE, 0.065, 0.02, 0.070, COLOR_BODY),                       # front posts (x 0.19 to 0.21): the exit notch lies between them
    *_mirror_y(0.0, FINGER_RECESS_HALF_WIDTH_M, _SIDE, 0.065, 0.14, 0.070, COLOR_BODY),                 # side walls
    ((0.051, 0.0, 0.065), (0.038, 0.20, 0.070), COLOR_BODY),                  # rear wall (x 0.032 to 0.070)
    *_mirror_y(-0.009, CRADLE_HALF_WIDTH_M, FINGER_RECESS_HALF_WIDTH_M, 0.036, 0.082, 0.012, COLOR_BODY),  # cradle shoulders, 12 mm tall
    ((-0.11, 0.0, 0.015), (0.08, 0.10, 0.03), COLOR_BODY),                     # chute apron in front, top flush with the bay floor
    ((-0.072, 0.065, 0.080), (0.004, 0.026, 0.026), COLOR_BEZEL),              # lamp bezel on the front face
    ((-0.073, -0.065, 0.080), (0.006, 0.020, 0.020), COLOR_BUTTON),            # power button
)

# Lamp (display only, VisualizationMarkers): centre in the printer frame, size.
LAMP_CENTRE = (-0.0755, 0.065, 0.080)
LAMP_SIZE = (0.003, 0.018, 0.018)

# -- cover: ONE sprung slide along +x carried by the printer part -----------------------------------------------------
COVER_NAME = "rp_cover"
COVER_TRAVEL_M = 0.125
COVER_SPRING_N_PER_M = 8.0
COVER_DAMPING = 5.0
COVER_MASS_KG = 0.15
COVER_REST = (0.0, 0.0, 0.100)
COVER_PLATE = ((0.0, 0.0, 0.105), (0.14, 0.20, 0.010), COLOR_COVER)            # z 0.100 to 0.110, rests on the walls
COVER_RIBS = tuple(((x, 0.0, 0.1115), (0.006, 0.16, 0.003), COLOR_RIB) for x in (-0.05, -0.04, -0.03))   # z 0.110 to 0.113
COVER_WINDOW = ((0.02, 0.0, 0.111), (0.06, 0.08, 0.002), COLOR_WINDOW)
COVER_ARM = ((-0.055, 0.13, 0.105), (0.03, 0.06, 0.010), COLOR_COVER)           # side arm, y 0.10 to 0.16
COVER_TAB = ((-0.076, 0.13, 0.089), (0.012, 0.04, 0.04), COLOR_TAB)             # blue tab, front face x 0.178 at rest, z 0.069 to 0.109
COVER_BOXES = (COVER_PLATE, *COVER_RIBS, COVER_WINDOW, COVER_ARM, COVER_TAB)
TAB_FRONT_X = PRINTER_XY[0] + COVER_TAB[0][0] - COVER_TAB[1][0] / 2             # 0.178
TAB_CENTRE_XYZ = (PRINTER_XY[0] + COVER_TAB[0][0], COVER_TAB[0][1], COVER_TAB[0][2])
BAY_OPEN_M = 0.105                     # near edge of the cover at x 0.295: past the bay's rear wall and the roll's rear edge
COVER_CLOSED_TOL_M = 0.002

# -- roll: loose, 58 mm wide, 60 mm across, 25 mm core, 90 g, thermal paper --------------------------------------------------
ROLL_NAME = "rp_roll"
PAPER_ROLL_MASS_KG = 0.09
ROLL_FRICTION = 0.5
ROLL_RADIUS_M = 0.030
ROLL_WIDTH_M = 0.058
ROLL_CORE_RADIUS_M = 0.0125
ROLL_CORE_WIDTH_M = 0.059
TAIL_LEN_M = 0.12                      # from the roll's axis to the free end
TAIL_T_M = 0.003
ROLL_CENTRE_Z = ROLL_RADIUS_M          # axis height above the part origin
ROLL_CYL = ((0.0, 0.0, ROLL_CENTRE_Z), ROLL_RADIUS_M, ROLL_WIDTH_M, COLOR_PAPER, "Y")
ROLL_CORE = ((0.0, 0.0, ROLL_CENTRE_Z), ROLL_CORE_RADIUS_M, ROLL_CORE_WIDTH_M, COLOR_CORE, "Y")
ROLL_TAIL = ((TAIL_LEN_M / 2, 0.0, -TAIL_T_M / 2), (TAIL_LEN_M, ROLL_WIDTH_M, TAIL_T_M), COLOR_PAPER)
# The free end's orange tape is a display marker (a 15 mm square, 0.6 mm thick, on the tail's top face) that follows the tail.
TAPE_MARKER_SIZE = (0.015, 0.015, 0.0006)
TAPE_MARKER_LOCAL = (TAIL_LEN_M - 0.0075, 0.0, 0.0004)
TAIL_TIP_LOCAL = (TAIL_LEN_M, 0.0, -TAIL_T_M / 2)
ROLL_AXIS_LOCAL = (0.0, 1.0, 0.0)
ROLL_UP_LOCAL = (0.0, 0.0, 1.0)

# -- stand: rubber plate 9 x 14 x 1 cm with ONE chock 8.5 mm behind the roll (the tail runs the other way) --------------------
STAND_NAME = "rp_stand"
STAND_XY = (0.14, -0.14)
STAND_MASS_KG = 25.0
STAND_FRICTION = 1.2
STAND_PLATE = ((0.0, 0.0, 0.005), (0.09, 0.14, 0.01), COLOR_STAND)
STAND_CHOCK = ((0.0, 0.0465, 0.021), (0.04, 0.016, 0.022), COLOR_STAND)         # inner face 38.5 mm from the roll's axis
STAND_TOP_Z = 0.01
STAND_HALF = (0.045, 0.07)

# Roll at the start: axis along world x, free end running toward -y (yaw -90 deg), on the plate with the tail under it.
ROLL_START_YAW = -math.pi / 2
ROLL_START_XY = STAND_XY
ROLL_START_ORIGIN_Z = STAND_TOP_Z + TAIL_T_M                                    # 0.013
ROLL_START_CENTRE_Z = ROLL_START_ORIGIN_Z + ROLL_CENTRE_Z                       # 0.043

# Correct seating: roll across the bay (axis along y), free end toward -x through the notch, tail lying on the bay floor.
SEAT_XY = (0.251, 0.0)                                                          # middle of the bay's x range
SEAT_ORIGIN_Z = BAY_FLOOR_Z + TAIL_T_M                                          # 0.033
SEAT_CENTRE_Z = SEAT_ORIGIN_Z + ROLL_CENTRE_Z                                   # 0.063
SEAT_TOL_X_M = 0.012
SEAT_TOL_Y_M = 0.008
SEAT_TOL_Z_M = 0.003
SEAT_MAX_AXIS_DEG = 5.0                # roll axis within this angle of the y line
SEAT_MAX_TILT_DEG = 5.0                # the roll's up direction within this angle of vertical
FEED_TIP_MAX_X = FRONT_FACE_X - 0.02   # free end at least 2 cm outside the front face
FEED_TIP_MAX_ABS_Y = 0.02
FEED_TIP_MAX_Z = 0.045                 # the free end lies on the chute, not hanging up
STAND_MAX_TILT_DEG = 10.0
STAND_Z_BAND_M = (-0.010, 0.012)       # roll centre z relative to ROLL_START_CENTRE_Z when it is back on the stand

# Latched facts and thresholds.
LIFT_MIN_M = 0.03
OPEN_HOLD_STEPS = 20                   # 1 s at 20 Hz
FIXTURE_MOVE_M = 0.005
RELEASE_MIN_DIST_M = 0.03
FINGERS_OPEN_FRACTION = 0.9
STILL_SPEED_M_S = 0.01
STILL_WINDOW_STEPS = 20
STILL_MOTION_M = 0.001
SUCCESS_HOLD_TIME_S = 1.0
PAD_BELOW_TCP_M = 0.013
TCP_BELOW_LINK_M = 0.138
