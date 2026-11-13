"""Scripted demo for receipt_printer_roll_reload. The left arm pushes the blue tab of the sprung cover back with closed
fingers and holds it; the right arm pinches the roll across its 58 mm width (yaw 90, the roll lies with its axis along x and
its free end running to the right), lifts it, carries it in front of the printer while turning a quarter turn (yaw 90 to 0)
so the free end swings from -y to -x, moves it over the open bay, lowers it onto the seat, lets go and withdraws; then the
left arm lets the cover go and withdraws. Positions are commanded gripper centres (open loop, times only); every working
point is at x <= 0.286, |y| <= 0.14, z <= 0.16 above the table, straight-down grip with only a yaw."""

from __future__ import annotations

import os

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN
from yam_arena.demo import Waypoint

from geometry import (
    ROLL_START_CENTRE_Z,
    ROLL_WIDTH_M,
    ROLL_START_XY,
    SEAT_CENTRE_Z,
    SEAT_XY,
    TABLE_TOP,
    TAB_CENTRE_XYZ,
)

TOP = TABLE_TOP
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))
YAW_ACROSS = 1.5708          # pads close along world x: across the roll's 58 mm width while its axis runs along x
# The roll is gripped with the fingers commanded 2 mm per side tighter than its width (about 10 N each, below their 50 N limit),
# so the two pads act as a centring spring and the roll stays on the hand's axis; a fully closed command would saturate.
FINGER_GRIP = -(ROLL_WIDTH_M - 0.004) / 2


def _s(t: float) -> float:
    return max(0.1, t * SCALE)


L_READY = (0.10, 0.14, TOP + 0.12)
R_READY = (0.10, -0.14, TOP + 0.12)

# Left arm: closed fingers (12 mm wide, 20 mm deep) push the blue tab's front face (x 0.178 at rest, z 0.069 to 0.109) toward +x.
# The finger front is 10 mm ahead of the commanded centre, so contact starts at x 0.168 and the cover reaches 105 mm of slide
# (bay open) at x 0.273; the final command (0.286) leaves 13 mm for the arm's lag and is the arm's reach limit.
PUSH_Y = TAB_CENTRE_XYZ[1]                        # 0.13
PUSH_Z = TOP + TAB_CENTRE_XYZ[2]                  # tab centre height, 0.10 above the table
PUSH_X_NEAR = 0.150
PUSH_X_FAR = 0.286

# Right arm: pads reach 13 mm below the commanded centre and the palm starts 30 mm above it, so the roll (60 mm across) is
# gripped with the commanded centre 8 mm above its axis: the roll's top then stays 8 mm below the palm.
GRIP_DZ = 0.008
GRASP = (ROLL_START_XY[0], ROLL_START_XY[1], TOP + ROLL_START_CENTRE_Z + GRIP_DZ)        # 0.051 above the table
CARRY_Z = TOP + 0.160                              # roll bottom 0.122, tail bottom 0.119: 9 mm over a closed cover's ribs (0.113), 19 mm over the walls (0.100)
IN_FRONT = (0.14, 0.0, CARRY_Z)                    # in front of the notch, after the quarter turn
OVER_BAY = (SEAT_XY[0], SEAT_XY[1], CARRY_Z)
SEAT_LOW = (SEAT_XY[0], SEAT_XY[1], TOP + SEAT_CENTRE_Z + GRIP_DZ + 0.002)               # 2 mm above the seat


def make_settle_plan() -> dict[str, list[Waypoint]]:
    return {
        "left": [Waypoint(_s(8.0), L_READY, FINGER_OPEN, "left settle")],
        "right": [Waypoint(_s(8.0), R_READY, FINGER_OPEN, "right settle")],
    }


def _left_hold_and_release():
    def w(t, p, f, label):
        return Waypoint(_s(t), p, f, label)

    return [
        w(1.0, L_READY, FINGER_OPEN, "hold the ready pose"),
        w(2.0, (PUSH_X_NEAR, PUSH_Y, PUSH_Z), FINGER_OPEN, "beside the blue tab, 3 cm in front of it"),
        w(0.5, (PUSH_X_NEAR, PUSH_Y, PUSH_Z), FINGER_OPEN, "settle"),
        w(0.8, (PUSH_X_NEAR, PUSH_Y, PUSH_Z), FINGER_CLOSED, "close the fingers"),
        w(5.0, (PUSH_X_FAR, PUSH_Y, PUSH_Z), FINGER_CLOSED, "push the cover back against its spring"),
        w(8.2, (PUSH_X_FAR, PUSH_Y, PUSH_Z), FINGER_CLOSED, "hold the cover back while the roll goes in"),
        w(0.8, (PUSH_X_FAR, PUSH_Y, PUSH_Z), FINGER_OPEN, "let the cover go"),
        w(2.4, (PUSH_X_FAR, PUSH_Y, PUSH_Z), FINGER_OPEN, "wait for the cover to close"),
        w(1.0, (PUSH_X_FAR, PUSH_Y, TOP + 0.150), FINGER_OPEN, "lift clear"),
        w(2.0, L_READY, FINGER_OPEN, "back to ready"),
        w(4.0, L_READY, FINGER_OPEN, "wait for stillness"),
    ]


def _right_load():
    def w(t, p, f, label, yaw=0.0):
        return Waypoint(_s(t), p, f, label, yaw=yaw)

    hi = (GRASP[0], GRASP[1], TOP + 0.110)
    lift = (GRASP[0], GRASP[1], CARRY_Z)
    return [
        w(1.0, R_READY, FINGER_OPEN, "hold the ready pose"),
        w(2.0, hi, FINGER_OPEN, "over the roll", YAW_ACROSS),
        w(0.5, hi, FINGER_OPEN, "settle", YAW_ACROSS),
        w(1.5, GRASP, FINGER_OPEN, "lower the open fingers beside the roll's ends", YAW_ACROSS),
        w(0.5, GRASP, FINGER_OPEN, "settle", YAW_ACROSS),
        w(0.8, GRASP, FINGER_GRIP, "pinch the roll across its width", YAW_ACROSS),
        w(0.3, GRASP, FINGER_GRIP, "settle", YAW_ACROSS),
        w(1.2, lift, FINGER_GRIP, "lift the roll clear of the chock", YAW_ACROSS),
        w(3.0, IN_FRONT, FINGER_GRIP, "carry it in front of the notch, a quarter turn so the free end leads toward -x", 0.0),
        w(0.7, IN_FRONT, FINGER_GRIP, "settle until the cover is back", 0.0),
        w(2.0, OVER_BAY, FINGER_GRIP, "move the roll over the open bay, the free end through the notch", 0.0),
        w(1.5, SEAT_LOW, FINGER_GRIP, "lower the roll onto the seat", 0.0),
        w(0.4, SEAT_LOW, FINGER_GRIP, "settle", 0.0),
        w(0.8, SEAT_LOW, FINGER_OPEN, "let go", 0.0),
        w(1.0, OVER_BAY, FINGER_OPEN, "lift straight up", 0.0),
        w(2.2, (R_READY[0], R_READY[1], TOP + 0.155), FINGER_OPEN, "back toward ready, high over the printer front", 0.0),
        w(0.8, R_READY, FINGER_OPEN, "down to ready", 0.0),
        w(7.4, R_READY, FINGER_OPEN, "wait for the cover to close and everything to stop", 0.0),
    ]


def make_demo_plan(ablation: str | None = None) -> dict[str, list[Waypoint]]:
    left = _left_hold_and_release()
    right = _right_load()
    total_l = sum(w.duration for w in left)
    total_r = sum(w.duration for w in right)
    if ablation == "left":      # the left arm never touches the cover: the roll cannot be seated
        left = [Waypoint(total_l, L_READY, FINGER_OPEN, "ablation: left arm idle")]
    elif ablation == "right":   # the right arm never touches the roll: the cover is held open and nothing is loaded
        right = [Waypoint(total_r, R_READY, FINGER_OPEN, "ablation: right arm idle")]
    return {"left": left, "right": right}


def plans():
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation="right" if os.getenv("ABLATION") == "right" else "left")
    return make_demo_plan()
