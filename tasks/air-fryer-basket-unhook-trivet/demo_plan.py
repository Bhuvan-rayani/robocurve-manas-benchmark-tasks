"""Scripted demo for air_fryer_basket_unhook_trivet: the right arm pinches the handle bar (yaw 90), pulls the basket 3.1 cm
toward the robot level so the flanges leave the hooks, lifts 3 cm, carries it to the mat, sets it down, releases and
withdraws; the left arm stays at ready. Positions are commanded gripper centres (open loop); it stops to settle before
each engage."""

from __future__ import annotations

import os

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))
YAW = 1.5708


def _s(t: float) -> float:
    return max(0.1, t * SCALE)


L_READY = (0.10, 0.14, TOP + 0.12)
R_READY = (0.10, -0.14, TOP + 0.12)


def make_settle_plan() -> dict[str, list[Waypoint]]:
    return {
        "left": [Waypoint(_s(8.0), L_READY, FINGER_OPEN, "left settle")],
        "right": [Waypoint(_s(8.0), R_READY, FINGER_OPEN, "right settle")],
    }


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    left = [Waypoint(_s(30.0), L_READY, FINGER_OPEN, "left arm parked")]
    if ablation:
        return {"left": left, "right": [Waypoint(_s(30.0), R_READY, FINGER_OPEN, "ablation: right arm idle")]}

    def w(t, p, f, label):
        return Waypoint(_s(t), p, f, label, yaw=YAW)

    grip = (0.230, 0.000, TOP + 0.086)
    pulled = (0.199, 0.000, TOP + 0.086)
    lifted = (0.199, 0.000, TOP + 0.116)
    mat_hi = (0.208, -0.220, TOP + 0.116)
    mat_lo = (0.208, -0.220, TOP + 0.061)
    clear = (0.208, -0.220, TOP + 0.110)
    right = [
        w(2.5, (0.230, 0.000, TOP + 0.120), FINGER_OPEN, "above the handle bar"),
        w(0.6, (0.230, 0.000, TOP + 0.120), FINGER_OPEN, "settle above the bar"),
        w(1.5, grip, FINGER_OPEN, "lower the open fingers around the bar"),
        w(0.6, grip, FINGER_OPEN, "settle"),
        w(0.8, grip, FINGER_CLOSED, "pinch the bar"),
        w(1.5, pulled, FINGER_CLOSED, "pull the basket 3.1 cm toward the robot, level"),
        w(0.6, pulled, FINGER_CLOSED, "settle"),
        w(1.0, lifted, FINGER_CLOSED, "lift 3 cm, clear of the hooks"),
        w(3.0, mat_hi, FINGER_CLOSED, "carry to the mat"),
        w(0.6, mat_hi, FINGER_CLOSED, "settle"),
        w(1.5, mat_lo, FINGER_CLOSED, "set the basket on the mat"),
        w(0.6, mat_lo, FINGER_CLOSED, "settle"),
        w(0.8, mat_lo, FINGER_OPEN, "release"),
        w(1.0, clear, FINGER_OPEN, "lift straight up"),
        Waypoint(_s(2.0), R_READY, FINGER_OPEN, "back to ready"),
        Waypoint(_s(3.0), R_READY, FINGER_OPEN, "wait for stillness"),
    ]
    return {"left": left, "right": right}


def plans():
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
