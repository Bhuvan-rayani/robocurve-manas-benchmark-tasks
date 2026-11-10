from __future__ import annotations

"""Demo plan for cordon_bar_walkway (T26)."""

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))


def _s(t: float) -> float:
    return max(0.1, t * SCALE)


def make_settle_plan():
    return {
        "left": [Waypoint(_s(8.0), (0.20, 0.20, TABLE_TOP + 0.15), FINGER_OPEN, "l_settle")],
        "right": [Waypoint(_s(8.0), (0.20, -0.20, TABLE_TOP + 0.15), FINGER_OPEN, "r_settle")],
    }


def make_demo_plan(ablation: bool = False):
    # Symmetrical dual carry: Left arm grips bar at y = +0.20 m, Right arm grips at y = -0.20 m
    # TCP distance = 400 mm constant throughout (clearance = 315 mm >> 30 mm)
    # Both arms lift bar and place into post cradles at (0.28, +/-0.20, TABLE_TOP + 0.18)
    if ablation:
        left = [
            Waypoint(_s(2.0), (0.18, 0.12, TABLE_TOP + 0.12), FINGER_OPEN, "l_hover"),
            Waypoint(_s(1.5), (0.18, 0.20, TABLE_TOP + 0.025), FINGER_CLOSED, "l_grip_solo"),
            Waypoint(_s(2.0), (0.25, 0.15, TABLE_TOP + 0.10), FINGER_CLOSED, "l_tilt_fail"),
            Waypoint(_s(10.0), (0.25, 0.15, TABLE_TOP + 0.10), FINGER_CLOSED, "l_hold_fail"),
        ]
        right = [Waypoint(_s(15.5), (0.20, -0.25, TABLE_TOP + 0.15), FINGER_OPEN, "r_idle")]
        return {"left": left, "right": right}

    left = [
        # Hover & pick bar left end at (0.18, 0.20)
        Waypoint(_s(2.0), (0.18, 0.12, TABLE_TOP + 0.12), FINGER_OPEN, "l_hover", yaw=-1.5708),
        Waypoint(_s(1.5), (0.18, 0.12, TABLE_TOP + 0.025), FINGER_OPEN, "l_descend", yaw=-1.5708),
        Waypoint(_s(0.8), (0.18, 0.12, TABLE_TOP + 0.025), FINGER_CLOSED, "l_grasp", yaw=-1.5708),
        Waypoint(_s(1.5), (0.18, 0.12, TABLE_TOP + 0.135), FINGER_CLOSED, "l_lift", yaw=-1.5708),
        # Advance to post cradle at (0.28, 0.20, TABLE_TOP + 0.18)
        Waypoint(_s(2.5), (0.28, 0.12, TABLE_TOP + 0.135), FINGER_CLOSED, "l_advance_cradle", yaw=-1.5708),
        Waypoint(_s(1.5), (0.28, 0.12, TABLE_TOP + 0.135), FINGER_CLOSED, "l_seat_cradle", yaw=-1.5708),
        Waypoint(_s(0.8), (0.28, 0.12, TABLE_TOP + 0.135), FINGER_OPEN, "l_release_bar", yaw=-1.5708),
        Waypoint(_s(1.5), (0.28, 0.12, TABLE_TOP + 0.20), FINGER_OPEN, "l_clear_bar", yaw=-1.5708),
        # Retract to standby
        Waypoint(_s(2.0), (0.20, 0.12, TABLE_TOP + 0.20), FINGER_OPEN, "l_standby", yaw=-1.5708),
        Waypoint(_s(4.0), (0.20, 0.12, TABLE_TOP + 0.20), FINGER_OPEN, "l_settle", yaw=-1.5708),
    ]

    right = [
        # Hover & pick bar right end at (0.18, -0.20)
        Waypoint(_s(2.0), (0.18, -0.12, TABLE_TOP + 0.12), FINGER_OPEN, "r_hover", yaw=1.5708),
        Waypoint(_s(1.5), (0.18, -0.12, TABLE_TOP + 0.025), FINGER_OPEN, "r_descend", yaw=1.5708),
        Waypoint(_s(0.8), (0.18, -0.12, TABLE_TOP + 0.025), FINGER_CLOSED, "r_grasp", yaw=1.5708),
        Waypoint(_s(1.5), (0.18, -0.12, TABLE_TOP + 0.135), FINGER_CLOSED, "r_lift", yaw=1.5708),
        # Advance to post cradle at (0.28, -0.20, TABLE_TOP + 0.18)
        Waypoint(_s(2.5), (0.28, -0.12, TABLE_TOP + 0.135), FINGER_CLOSED, "r_advance_cradle", yaw=1.5708),
        Waypoint(_s(1.5), (0.28, -0.12, TABLE_TOP + 0.135), FINGER_CLOSED, "r_seat_cradle", yaw=1.5708),
        Waypoint(_s(0.8), (0.28, -0.12, TABLE_TOP + 0.135), FINGER_OPEN, "r_release_bar", yaw=1.5708),
        Waypoint(_s(1.5), (0.28, -0.12, TABLE_TOP + 0.20), FINGER_OPEN, "r_clear_bar", yaw=1.5708),
        # Retract to standby
        Waypoint(_s(2.0), (0.20, -0.12, TABLE_TOP + 0.20), FINGER_OPEN, "r_standby", yaw=1.5708),
        Waypoint(_s(4.0), (0.20, -0.12, TABLE_TOP + 0.20), FINGER_OPEN, "r_settle", yaw=1.5708),
    ]

    return {"left": left, "right": right}


def plans():
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
