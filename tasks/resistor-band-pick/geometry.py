"""Geometry, masses, colours, and positions for resistor_band_pick."""

from __future__ import annotations

TABLE_TOP = 0.7475

# Colours in sRGB (0..1)
COLOR_TRAY_WHITE = (242 / 255, 242 / 255, 242 / 255)   # #F2F2F2
COLOR_RES_BEIGE = (227 / 255, 210 / 255, 164 / 255)    # #E3D2A4
COLOR_BOARD_GREEN = (46 / 255, 139 / 255, 62 / 255)    # #2E8B3E
COLOR_COVER_GREY = (74 / 255, 80 / 255, 88 / 255)      # #4A5058
COLOR_CARD_WHITE = (217 / 255, 217 / 255, 217 / 255)   # #D9D9D9

# Band colours
COLOR_BAND_BROWN = (139 / 255, 69 / 255, 19 / 255)
COLOR_BAND_BLACK = (20 / 255, 20 / 255, 20 / 255)
COLOR_BAND_RED = (220 / 255, 20 / 255, 20 / 255)

# --- Part Tray ---
TRAY_POS_WORLD = (0.24, 0.18, TABLE_TOP)
TRAY_DIMS_M = (0.200, 0.300, 0.030)
TRAY_MASS_KG = 0.400
TRAY_FRICTION = 1.2

# 30 collision boxes defining tray floor, outer walls, and pocket dividers
TRAY_BOXES = (
    ((0.000, 0.000, 0.005), (0.200, 0.300, 0.010), COLOR_TRAY_WHITE),
    ((-0.095, -0.135, 0.020), (0.010, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((-0.095, -0.100, 0.020), (0.010, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((-0.095, -0.050, 0.020), (0.010, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((-0.095, 0.000, 0.020), (0.010, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((-0.095, 0.050, 0.020), (0.010, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((-0.095, 0.100, 0.020), (0.010, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((-0.095, 0.135, 0.020), (0.010, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((-0.050, -0.135, 0.020), (0.080, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((-0.050, -0.050, 0.020), (0.080, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((-0.050, 0.050, 0.020), (0.080, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((-0.050, 0.135, 0.020), (0.080, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((0.000, -0.135, 0.020), (0.020, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((0.000, -0.100, 0.020), (0.020, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((0.000, -0.050, 0.020), (0.020, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((0.000, 0.000, 0.020), (0.020, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((0.000, 0.050, 0.020), (0.020, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((0.000, 0.100, 0.020), (0.020, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((0.000, 0.135, 0.020), (0.020, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((0.050, -0.135, 0.020), (0.080, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((0.050, -0.050, 0.020), (0.080, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((0.050, 0.050, 0.020), (0.080, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((0.050, 0.135, 0.020), (0.080, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((0.095, -0.135, 0.020), (0.010, 0.030, 0.020), COLOR_TRAY_WHITE),
    ((0.095, -0.100, 0.020), (0.010, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((0.095, -0.050, 0.020), (0.010, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((0.095, 0.000, 0.020), (0.010, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((0.095, 0.050, 0.020), (0.010, 0.060, 0.020), COLOR_TRAY_WHITE),
    ((0.095, 0.100, 0.020), (0.010, 0.040, 0.020), COLOR_TRAY_WHITE),
    ((0.095, 0.135, 0.020), (0.010, 0.030, 0.020), COLOR_TRAY_WHITE),
)

# --- Resistors ---
# Six upright cylinders (pegs) standing in the 2x3 pockets of the tray
RES_RADIUS_M = 0.015
RES_HEIGHT_M = 0.070
RES_MASS_KG = 0.025
RES_START_Z_M = 0.010 + RES_HEIGHT_M / 2  # base on pocket floor z=0.010 m

COLOR_BAND_ORANGE = (240 / 255, 120 / 255, 10 / 255)
COLOR_BAND_GREEN = (30 / 255, 150 / 255, 60 / 255)
COLOR_BAND_YELLOW = (245 / 255, 215 / 255, 20 / 255)
COLOR_BAND_VIOLET = (130 / 255, 50 / 255, 180 / 255)
# Three colour bands per resistor, top to bottom (the target is brown-black-red)
RES_BANDS = {
    "res_a": (COLOR_BAND_ORANGE, COLOR_BAND_ORANGE, COLOR_BAND_BROWN),
    "res_b": (COLOR_BAND_GREEN, COLOR_BAND_BROWN, COLOR_BAND_RED),
    "res_c": (COLOR_BAND_BROWN, COLOR_BAND_BLACK, COLOR_BAND_RED),
    "res_d": (COLOR_BAND_BLACK, COLOR_BAND_BROWN, COLOR_BAND_RED),
    "res_e": (COLOR_BAND_YELLOW, COLOR_BAND_VIOLET, COLOR_BAND_RED),
    "res_f": (COLOR_BAND_RED, COLOR_BAND_BLACK, COLOR_BAND_BROWN),
}
BAND_HEIGHT_M = 0.008
BAND_RADIUS_M = 0.0158
BAND_Z_M = (0.020, 0.005, -0.010)  # band centres relative to the resistor centre

RES_NAMES = ("res_a", "res_b", "res_c", "res_d", "res_e", "res_f")
TARGET_RES_NAME = "res_c"

RES_POCKET_COORDS = {
    "res_a": (0.29, 0.28),  # orange-orange-brown
    "res_b": (0.29, 0.18),  # green-brown-red
    "res_c": (0.29, 0.08),  # brown-black-red (TARGET: 1-0-2 = 1 kΩ)
    "res_d": (0.19, 0.28),  # black-brown-red
    "res_e": (0.19, 0.18),  # yellow-violet-red
    "res_f": (0.19, 0.08),  # red-black-brown
}

RES_START_POSITIONS = {
    name: (xy[0], xy[1], TABLE_TOP + RES_START_Z_M)
    for name, xy in RES_POCKET_COORDS.items()
}

# --- Socket Board & Cover ---
# Placed at y = -0.06 m so both arms have symmetric IK reach and clearance >= 70 mm
BOARD_POS_WORLD = (0.26, -0.06, TABLE_TOP)  # GPU: the left arm cannot reach y -0.06 at x 0.30 (reach radius ~0.45 m around its base); at x 0.26 it can
BOARD_DIMS_M = (0.240, 0.160, 0.080)
BOARD_MASS_KG = 25.0
BOARD_FRICTION = 1.2

# 16 collision boxes creating a central vertical 32x32 mm socket hole through the 80 mm tall boss
_HW = 0.023                      # socket half width: 46 mm hole for a 30 mm resistor = 8 mm clearance per side (it was 32 mm: the resistor sat on the rim)
_OUT = 0.120                     # board half length (x)
_YO = 0.080                      # board half width (y)
_FX = (_HW + _OUT) / 2           # centre of the long floor boxes in x
_FY = (_HW + _YO) / 2
BOARD_BOXES = (
    # 30 mm thick floor with a square hole
    ((_FX, -_FY, 0.015), (_OUT - _HW, _YO - _HW, 0.030), COLOR_BOARD_GREEN),
    ((0.0, -_FY, 0.015), (2 * _HW, _YO - _HW, 0.030), COLOR_BOARD_GREEN),
    ((-_FX, -_FY, 0.015), (_OUT - _HW, _YO - _HW, 0.030), COLOR_BOARD_GREEN),
    ((_FX, 0.0, 0.015), (_OUT - _HW, 2 * _HW, 0.030), COLOR_BOARD_GREEN),
    ((-_FX, 0.0, 0.015), (_OUT - _HW, 2 * _HW, 0.030), COLOR_BOARD_GREEN),
    ((_FX, _FY, 0.015), (_OUT - _HW, _YO - _HW, 0.030), COLOR_BOARD_GREEN),
    ((0.0, _FY, 0.015), (2 * _HW, _YO - _HW, 0.030), COLOR_BOARD_GREEN),
    ((-_FX, _FY, 0.015), (_OUT - _HW, _YO - _HW, 0.030), COLOR_BOARD_GREEN),
    # 50 mm tall collar (z 0.03-0.08) around the hole
    ((_HW + 0.007, -(_HW + 0.007), 0.055), (0.014, 0.014, 0.050), COLOR_BOARD_GREEN),
    ((0.0, -(_HW + 0.007), 0.055), (2 * _HW, 0.014, 0.050), COLOR_BOARD_GREEN),
    ((-(_HW + 0.007), -(_HW + 0.007), 0.055), (0.014, 0.014, 0.050), COLOR_BOARD_GREEN),
    ((_HW + 0.007, 0.0, 0.055), (0.014, 2 * _HW, 0.050), COLOR_BOARD_GREEN),
    ((-(_HW + 0.007), 0.0, 0.055), (0.014, 2 * _HW, 0.050), COLOR_BOARD_GREEN),
    ((_HW + 0.007, _HW + 0.007, 0.055), (0.014, 0.014, 0.050), COLOR_BOARD_GREEN),
    ((0.0, _HW + 0.007, 0.055), (2 * _HW, 0.014, 0.050), COLOR_BOARD_GREEN),
    ((-(_HW + 0.007), _HW + 0.007, 0.055), (0.014, 0.014, 0.050), COLOR_BOARD_GREEN),
)

SOCKET_HOLE_WORLD_XY = (BOARD_POS_WORLD[0], BOARD_POS_WORLD[1])
SOCKET_RIM_Z_WORLD = TABLE_TOP + 0.080
SOCKET_DEPTH_M = 0.080

# Socket Cover Slider (on socket_board along +X)
COVER_NAME = "socket_cover"
COVER_DIMS_M = (0.100, 0.040, 0.010)
COVER_MASS_KG = 0.020
COVER_REST_PART = (0.030, 0.0, 0.080)
COVER_TRAVEL_M = 0.040  # 40 mm slide uncovers 32 mm hole
COVER_SPRING_RATE = 10.0  # 0.01 N/mm: at 60 N/m the arm (about 165 N/m) only held the cover open 31 of 40 mm and it sprang shut mid-insertion
COVER_DAMPING = 10.0
COVER_AXIS = "+X"
COVER_BOXES = (
    ((0.030, -0.080, 0.085), (0.100, 0.200, 0.010), COLOR_COVER_GREY),  # extended to y -0.18 (world -0.24) so the right hand can push it 16 cm from the left hand (arms collide closer),
)

# --- Reference Colour Code Card ---
CARD_POS_WORLD = (0.18, -0.20, TABLE_TOP + 0.00125)
CARD_DIMS_M = (0.060, 0.080, 0.0025)
CARD_MASS_KG = 0.008

# --- Task Scoring Thresholds ---
MAX_BOARD_DRIFT_GATE_M = 0.005      # 5 mm gate
RESISTOR_LIFTED_THRESHOLD_M = 0.020 # 2 cm lift
SOCKET_HOVER_RADIUS_M = 0.012       # 12 mm: the hole leaves 8 mm of play per side, so a seated resistor can sit 8-9 mm off-centre
SOCKET_SEATED_DEPTH_THRESHOLD_M = 0.060  # >= 60 mm deep from rim
COVER_CLOSED_TOLERANCE_M = 0.003    # cover bar within 3 mm of rest
SUCCESS_HOLD_TIME_S = 1.0
