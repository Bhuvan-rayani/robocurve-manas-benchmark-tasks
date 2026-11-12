from __future__ import annotations

"""Demo plan for wheel_axle_lynch_pin (T18)."""

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
        "right": [Waypoint(_s(8.0), (0.20, -0.20, TABLE_TOP + 0.15), FINGER_OPEN, "r_settle")],
    }


def make_demo_plan(ablation: bool = False):
    # Left arm stabilizes stand brace at y = +0.12 m
    # Right arm operates on wheel and pin at y <= -0.06 m
    # TCP distance >= 180 mm (clearance >= 95 mm >= 30 mm)
    if ablation:
        left = [Waypoint(_s(20.0), (0.20, 0.25, TABLE_TOP + 0.15), FINGER_OPEN, "l_idle")]
        right = [
            Waypoint(_s(2.0), (0.16, -0.18, TABLE_TOP + 0.12), FINGER_OPEN, "r_hover"),
            Waypoint(_s(1.5), (0.16, -0.18, TABLE_TOP + 0.07), FINGER_CLOSED, "r_push_unbraced"),
            Waypoint(_s(16.5), (0.25, -0.10, TABLE_TOP + 0.02), FINGER_CLOSED, "r_hold"),
        ]
        return {"left": left, "right": right}

    left = [
        # Hover & brace stand base handle at (0.30, 0.12, TABLE_TOP + 0.04)
        Waypoint(_s(2.0), (0.30, 0.12, TABLE_TOP + 0.14), FINGER_OPEN, "l_hover_brace"),
        Waypoint(_s(1.5), (0.30, 0.12, TABLE_TOP + 0.04), FINGER_OPEN, "l_descend_brace"),
        Waypoint(_s(0.8), (0.30, 0.12, TABLE_TOP + 0.04), FINGER_CLOSED, "l_clamp_brace"),
        # Hold firm for 22 s while Right arm installs wheel and pin
        Waypoint(_s(22.0), (0.30, 0.12, TABLE_TOP + 0.04), FINGER_CLOSED, "l_hold_firm"),
        Waypoint(_s(0.8), (0.30, 0.12, TABLE_TOP + 0.04), FINGER_OPEN, "l_release_brace"),
        Waypoint(_s(1.5), (0.30, 0.12, TABLE_TOP + 0.14), FINGER_OPEN, "l_lift_clear"),
        Waypoint(_s(2.0), (0.20, 0.15, TABLE_TOP + 0.15), FINGER_OPEN, "l_standby"),
        Waypoint(_s(4.0), (0.20, 0.15, TABLE_TOP + 0.15), FINGER_OPEN, "l_settle"),
    ]

    right = [
        # 1. Hover & grasp wheel top rim at (0.16, -0.18)
        Waypoint(_s(2.0), (0.16, -0.18, TABLE_TOP + 0.18), FINGER_OPEN, "r_hover_wheel"),
        Waypoint(_s(1.5), (0.16, -0.18, TABLE_TOP + 0.134), FINGER_OPEN, "r_descend_wheel"),
        Waypoint(_s(0.8), (0.16, -0.18, TABLE_TOP + 0.134), FINGER_CLOSED, "r_grasp_wheel"),
        Waypoint(_s(1.5), (0.16, -0.18, TABLE_TOP + 0.170), FINGER_CLOSED, "r_lift_wheel"),
        # 2. Align wheel with axle tip at (0.30, -0.18, TABLE_TOP + 0.145)
        Waypoint(_s(2.0), (0.30, -0.18, TABLE_TOP + 0.145), FINGER_CLOSED, "r_align_axle"),
        # 3. Slide wheel along +y onto axle to stop at y = -0.06 (command -0.030 to compensate lag)
        Waypoint(_s(3.0), (0.30, -0.030, TABLE_TOP + 0.145), FINGER_CLOSED, "r_slide_wheel_stop"),
        Waypoint(_s(0.8), (0.30, -0.030, TABLE_TOP + 0.145), FINGER_OPEN, "r_release_wheel"),
        Waypoint(_s(1.5), (0.28, -0.08, TABLE_TOP + 0.170), FINGER_OPEN, "r_lift_wheel_clear"),
        # 4. Move to pin holder at (0.20, -0.30)
        Waypoint(_s(2.0), (0.20, -0.30, TABLE_TOP + 0.160), FINGER_OPEN, "r_hover_pin"),
        Waypoint(_s(1.2), (0.20, -0.30, TABLE_TOP + 0.095), FINGER_OPEN, "r_descend_pin"),
        Waypoint(_s(0.8), (0.20, -0.30, TABLE_TOP + 0.095), FINGER_CLOSED, "r_grasp_pin"),
        Waypoint(_s(1.2), (0.20, -0.30, TABLE_TOP + 0.160), FINGER_CLOSED, "r_lift_pin"),
        # 5. Transport pin to axle cross hole at (0.30, -0.14, TABLE_TOP + 0.16)
        Waypoint(_s(2.0), (0.30, -0.140, TABLE_TOP + 0.160), FINGER_CLOSED, "r_align_hole"),
        # 6. Lower pin into cross hole
        Waypoint(_s(1.5), (0.30, -0.140, TABLE_TOP + 0.100), FINGER_CLOSED, "r_insert_pin"),
        Waypoint(_s(0.8), (0.30, -0.140, TABLE_TOP + 0.100), FINGER_OPEN, "r_release_pin"),
        Waypoint(_s(1.5), (0.30, -0.140, TABLE_TOP + 0.160), FINGER_OPEN, "r_retract"),
        Waypoint(_s(2.0), (0.20, -0.20, TABLE_TOP + 0.150), FINGER_OPEN, "r_standby"),
        Waypoint(_s(4.0), (0.20, -0.20, TABLE_TOP + 0.150), FINGER_OPEN, "r_settle"),
    ]
    return {"left": left, "right": right}


def plans():
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
