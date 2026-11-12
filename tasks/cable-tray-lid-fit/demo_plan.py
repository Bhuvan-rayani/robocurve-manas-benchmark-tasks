from __future__ import annotations

"""Demo plan for cable_tray_lid_fit (T13)."""

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))


def _s(t: float) -> float:
    return max(0.1, t * SCALE)


def make_settle_plan():
    return {
        "left": [Waypoint(_s(8.0), (0.20, 0.22, TABLE_TOP + 0.15), FINGER_OPEN, "l_settle")],
        "right": [Waypoint(_s(8.0), (0.20, -0.22, TABLE_TOP + 0.15), FINGER_OPEN, "r_settle")],
    }


def make_demo_plan(ablation: bool = False):
    if ablation:
        left = [
            Waypoint(_s(2.0), (0.16, 0.22, TABLE_TOP + 0.14), FINGER_OPEN, "l_hover", yaw=-1.5708),
            Waypoint(_s(18.0), (0.16, 0.22, TABLE_TOP + 0.14), FINGER_OPEN, "l_idle", yaw=-1.5708),
        ]
        right = [Waypoint(_s(20.0), (0.20, -0.25, TABLE_TOP + 0.15), FINGER_OPEN, "r_idle")]
        return {"left": left, "right": right}


    left = [
        # Hover & grip left lid at (0.16, 0.22)
        Waypoint(_s(2.0), (0.16, 0.22, TABLE_TOP + 0.14), FINGER_OPEN, "l_hover", yaw=-1.5708),
        Waypoint(_s(1.5), (0.16, 0.22, TABLE_TOP + 0.036), FINGER_OPEN, "l_descend", yaw=-1.5708),
        Waypoint(_s(0.8), (0.16, 0.22, TABLE_TOP + 0.036), FINGER_CLOSED, "l_grip", yaw=-1.5708),
        Waypoint(_s(1.5), (0.16, 0.22, TABLE_TOP + 0.14), FINGER_CLOSED, "l_lift", yaw=-1.5708),
        # Move to tray left end (0.30, 0.22)
        Waypoint(_s(2.5), (0.30, 0.22, TABLE_TOP + 0.14), FINGER_CLOSED, "l_align_tray", yaw=-1.5708),
        Waypoint(_s(1.5), (0.30, 0.22, TABLE_TOP + 0.086), FINGER_CLOSED, "l_lower_rails", yaw=-1.5708),
        # Slide along -y into middle (command y = 0.065 to compensate carry lag)
        Waypoint(_s(2.5), (0.30, 0.065, TABLE_TOP + 0.086), FINGER_CLOSED, "l_slide_middle", yaw=-1.5708),
        Waypoint(_s(0.8), (0.30, 0.065, TABLE_TOP + 0.086), FINGER_OPEN, "l_release", yaw=-1.5708),
        Waypoint(_s(1.5), (0.30, 0.065, TABLE_TOP + 0.14), FINGER_OPEN, "l_lift_clear", yaw=-1.5708),
        Waypoint(_s(2.0), (0.20, 0.22, TABLE_TOP + 0.15), FINGER_OPEN, "l_standby", yaw=-1.5708),
        Waypoint(_s(4.0), (0.20, 0.22, TABLE_TOP + 0.15), FINGER_OPEN, "l_settle", yaw=-1.5708),
    ]

    right = [
        # Hover & grip right lid at (0.16, -0.22)
        Waypoint(_s(2.0), (0.16, -0.22, TABLE_TOP + 0.14), FINGER_OPEN, "r_hover", yaw=1.5708),
        Waypoint(_s(1.5), (0.16, -0.22, TABLE_TOP + 0.036), FINGER_OPEN, "r_descend", yaw=1.5708),
        Waypoint(_s(0.8), (0.16, -0.22, TABLE_TOP + 0.036), FINGER_CLOSED, "r_grip", yaw=1.5708),
        Waypoint(_s(1.5), (0.16, -0.22, TABLE_TOP + 0.14), FINGER_CLOSED, "r_lift", yaw=1.5708),
        # Move to tray right end (0.30, -0.22)
        Waypoint(_s(2.5), (0.30, -0.22, TABLE_TOP + 0.14), FINGER_CLOSED, "r_align_tray", yaw=1.5708),
        Waypoint(_s(1.5), (0.30, -0.22, TABLE_TOP + 0.086), FINGER_CLOSED, "r_lower_rails", yaw=1.5708),
        # Slide along +y into middle (command y = -0.065 to compensate carry lag)
        Waypoint(_s(2.5), (0.30, -0.065, TABLE_TOP + 0.086), FINGER_CLOSED, "r_slide_middle", yaw=1.5708),
        Waypoint(_s(0.8), (0.30, -0.065, TABLE_TOP + 0.086), FINGER_OPEN, "r_release", yaw=1.5708),
        Waypoint(_s(1.5), (0.30, -0.065, TABLE_TOP + 0.14), FINGER_OPEN, "r_lift_clear", yaw=1.5708),
        Waypoint(_s(2.0), (0.20, -0.22, TABLE_TOP + 0.15), FINGER_OPEN, "r_standby", yaw=1.5708),
        Waypoint(_s(4.0), (0.20, -0.22, TABLE_TOP + 0.15), FINGER_OPEN, "r_settle", yaw=1.5708),
    ]
    return {"left": left, "right": right}


def plans():
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
