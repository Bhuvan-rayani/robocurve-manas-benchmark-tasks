from __future__ import annotations

"""Demo plan for terminal_cover_fit (T16)."""

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))


def _s(t: float) -> float:
    return max(0.1, t * SCALE)


def make_settle_plan():
    return {
        "left": [Waypoint(_s(8.0), (0.20, 0.20, TABLE_TOP + 0.16), FINGER_OPEN, "l_settle")],
        "right": [Waypoint(_s(8.0), (0.20, -0.25, TABLE_TOP + 0.16), FINGER_OPEN, "r_settle")],
    }


def make_demo_plan(ablation: bool = False):
    if ablation:
        left = [
            Waypoint(_s(2.0), (0.14, 0.0, TABLE_TOP + 0.15), FINGER_OPEN, "l_hover"),
            Waypoint(_s(2.0), (0.14, 0.0, TABLE_TOP + 0.12), FINGER_OPEN, "l_descend_no_grip"),
            Waypoint(_s(12.0), (0.14, 0.0, TABLE_TOP + 0.12), FINGER_OPEN, "l_idle"),
        ]
        right = [Waypoint(_s(16.0), (0.20, -0.25, TABLE_TOP + 0.16), FINGER_OPEN, "r_idle")]
        return {"left": left, "right": right}

    left = [
        # Hover above center handle at (0.14, 0.0)
        Waypoint(_s(2.0), (0.14, 0.0, TABLE_TOP + 0.14), FINGER_OPEN, "l_hover"),
        Waypoint(_s(1.5), (0.14, 0.0, TABLE_TOP + 0.065), FINGER_OPEN, "l_descend"),
        Waypoint(_s(1.0), (0.14, 0.0, TABLE_TOP + 0.065), FINGER_CLOSED, "l_grip"),
        Waypoint(_s(1.5), (0.14, 0.0, TABLE_TOP + 0.14), FINGER_CLOSED, "l_lift"),
        # Carry to terminal block to land at x=0.30
        Waypoint(_s(2.5), (0.300, 0.0, TABLE_TOP + 0.14), FINGER_CLOSED, "l_align_block"),
        # Lower over terminals to 25 mm above rim (handle at 0.030 + 0.050 = 0.080, + 0.025 = 0.105)
        Waypoint(_s(2.0), (0.300, 0.0, TABLE_TOP + 0.105), FINGER_CLOSED, "l_seat"),
        Waypoint(_s(1.0), (0.300, 0.0, TABLE_TOP + 0.105), FINGER_OPEN, "l_release"),
        # Lift straight up high before sideways retraction
        Waypoint(_s(1.5), (0.300, 0.0, TABLE_TOP + 0.150), FINGER_OPEN, "l_lift_straight"),
        Waypoint(_s(1.5), (0.220, 0.0, TABLE_TOP + 0.160), FINGER_OPEN, "l_back_lift"),
        Waypoint(_s(2.0), (0.20, 0.20, TABLE_TOP + 0.160), FINGER_OPEN, "l_standby"),
        Waypoint(_s(4.0), (0.20, 0.20, TABLE_TOP + 0.160), FINGER_OPEN, "l_settle"),
    ]

    right = [
        # Right arm remains safely parked at ready pose throughout
        Waypoint(_s(21.0), (0.20, -0.25, TABLE_TOP + 0.16), FINGER_OPEN, "r_parked"),
    ]
    return {"left": left, "right": right}


def plans():
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
