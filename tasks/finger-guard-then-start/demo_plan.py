from __future__ import annotations

"""Demo plan for finger_guard_then_start (T20)."""

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))


def _s(t: float) -> float:
    return max(0.1, t * SCALE)


def make_settle_plan():
    return {
        "left": [Waypoint(_s(8.0), (0.20, 0.15, TABLE_TOP + 0.15), FINGER_OPEN, "l_settle")],
        "right": [Waypoint(_s(8.0), (0.20, -0.15, TABLE_TOP + 0.15), FINGER_OPEN, "r_settle")],
    }


def make_demo_plan(ablation: bool = False):
    # Left arm closes guard at y = +0.12 m
    # Right arm presses button at y = -0.12 m
    # TCP distance = 240 mm (clearance 155 mm >= 30 mm)
    if ablation:
        # Left arm idle -> Right arm presses button with guard open -> fault (0.25)
        left = [Waypoint(_s(15.0), (0.20, 0.20, TABLE_TOP + 0.15), FINGER_OPEN, "l_idle")]
        right = [
            Waypoint(_s(2.0), (0.30, -0.12, TABLE_TOP + 0.14), FINGER_CLOSED, "r_hover"),
            Waypoint(_s(1.5), (0.30, -0.12, TABLE_TOP + 0.08), FINGER_CLOSED, "r_press_fault"),
            Waypoint(_s(11.5), (0.30, -0.12, TABLE_TOP + 0.08), FINGER_CLOSED, "r_hold"),
        ]
        return {"left": left, "right": right}

    left = [
        # Hover & approach guard handle at (0.23, 0.12, TABLE_TOP + 0.09)
        Waypoint(_s(2.0), (0.23, 0.12, TABLE_TOP + 0.14), FINGER_CLOSED, "l_hover_guard"),
        Waypoint(_s(1.5), (0.23, 0.12, TABLE_TOP + 0.09), FINGER_CLOSED, "l_contact_guard"),
        # Push guard closed by 14 cm along +X to x=0.37
        Waypoint(_s(2.5), (0.37, 0.12, TABLE_TOP + 0.09), FINGER_CLOSED, "l_push_guard_closed"),
        # Maintain firm hold for 10 s while Right arm presses start button
        Waypoint(_s(10.0), (0.37, 0.12, TABLE_TOP + 0.09), FINGER_CLOSED, "l_hold_guard_closed"),
        Waypoint(_s(1.5), (0.37, 0.12, TABLE_TOP + 0.14), FINGER_OPEN, "l_lift_clear"),
        Waypoint(_s(2.0), (0.20, 0.15, TABLE_TOP + 0.15), FINGER_OPEN, "l_standby"),
        Waypoint(_s(4.0), (0.20, 0.15, TABLE_TOP + 0.15), FINGER_OPEN, "l_settle"),
    ]

    right = [
        # Wait safely at right standby while Left arm closes guard (6.0 s)
        Waypoint(_s(6.0), (0.20, -0.15, TABLE_TOP + 0.15), FINGER_CLOSED, "r_wait_for_guard"),
        # Approach start button at (0.30, -0.12, TABLE_TOP + 0.09)
        Waypoint(_s(1.5), (0.30, -0.12, TABLE_TOP + 0.14), FINGER_CLOSED, "r_hover_button"),
        # Press button down 8 mm
        Waypoint(_s(1.5), (0.30, -0.12, TABLE_TOP + 0.075), FINGER_CLOSED, "r_press_button"),
        # Pause 1.5 s
        Waypoint(_s(1.5), (0.30, -0.12, TABLE_TOP + 0.075), FINGER_CLOSED, "r_hold_press"),
        Waypoint(_s(1.5), (0.30, -0.12, TABLE_TOP + 0.14), FINGER_OPEN, "r_retract"),
        Waypoint(_s(2.0), (0.20, -0.15, TABLE_TOP + 0.15), FINGER_OPEN, "r_standby"),
        Waypoint(_s(7.5), (0.20, -0.15, TABLE_TOP + 0.15), FINGER_OPEN, "r_settle"),
    ]
    return {"left": left, "right": right}


def plans():
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
