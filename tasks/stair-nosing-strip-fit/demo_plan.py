"""Demo trajectory plan for stair_nosing_strip_fit."""

from __future__ import annotations

import os
import pathlib
import sys

# Setup paths
_TASK_DIR = pathlib.Path(__file__).resolve().parent
_UPSTREAM = (
    _TASK_DIR.parents[2]
    / "robocurve-windows-transfer-2026-11-05"
    / "project"
    / "robocurve"
    / "tmp"
    / "yam-upstream"
)
for p in (_TASK_DIR, _UPSTREAM):
    if str(p) not in sys.path and p.exists():
        sys.path.insert(0, str(p))

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT

# Tunables
DEMO_TIME_SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))
DEMO_APPROACH_SPEED = 0.05


def _t(seconds: float) -> float:
    return max(0.1, seconds * DEMO_TIME_SCALE)


def plans() -> dict[str, list[Waypoint]]:
    """Return dictionary with 'left' and 'right' waypoint plans."""
    settle_only = os.environ.get("SETTLE_ONLY") == "1"
    ablation = os.environ.get("ABLATION") == "1"

    # Ready positions
    l_ready = (0.20, 0.25, TABLE_TOP + 0.16)
    r_ready = (0.20, -0.25, TABLE_TOP + 0.16)

    if settle_only:
        left_wp = [
            Waypoint(_t(8.0), l_ready, FINGER_OPEN, "left_settle"),
        ]
        right_wp = [
            Waypoint(_t(8.0), r_ready, FINGER_OPEN, "right_settle"),
        ]
        return {"left": left_wp, "right": right_wp}

    # Waypoints for symmetric dual carry at y = +/- 0.160 m (Delta y = 320 mm)
    # 1. Hover above nosing strip ends
    l_hover_pickup = (0.180, 0.160, TABLE_TOP + 0.120)
    r_hover_pickup = (0.180, -0.160, TABLE_TOP + 0.120)

    # 2. Grasp contact at strip ends
    l_grip = (0.180, 0.160, TABLE_TOP + 0.045)
    r_grip = (0.180, -0.160, TABLE_TOP + 0.045)

    # 3. Synchronous lift clear of step height
    l_lift = (0.180, 0.160, TABLE_TOP + 0.120)
    r_lift = (0.180, -0.160, TABLE_TOP + 0.120)

    # 4. Advance forward to step front edge (x = 0.295 m)
    l_advance = (0.295, 0.160, TABLE_TOP + 0.120)
    r_advance = (0.295, -0.160, TABLE_TOP + 0.120)

    # 5. Lower down onto step tread (flange flush on tread, lip over front face)
    l_place = (0.295, 0.160, TABLE_TOP + 0.070)
    r_place = (0.295, -0.160, TABLE_TOP + 0.070)

    # 6. Lift fingers slightly to clear strip before retracting
    l_lift_clear = (0.295, 0.160, TABLE_TOP + 0.095)
    r_lift_clear = (0.295, -0.160, TABLE_TOP + 0.095)

    # 7. Retreat back to ready
    l_retreat = (0.200, 0.200, TABLE_TOP + 0.120)
    r_retreat = (0.200, -0.200, TABLE_TOP + 0.120)

    left_wp = [
        # Start at ready
        Waypoint(_t(2.0), l_ready, FINGER_OPEN, "left_start"),
        # Hover and descend to grasp
        Waypoint(_t(3.0), l_hover_pickup, FINGER_OPEN, "left_hover_pickup", yaw=1.5708),
        Waypoint(_t(2.5), l_grip, FINGER_OPEN, "left_descend_grip", yaw=1.5708),
        Waypoint(_t(1.5), l_grip, FINGER_CLOSED, "left_close_grip", yaw=1.5708),
        # Lift clear of pad and step
        Waypoint(_t(3.0), l_lift, FINGER_CLOSED, "left_lift_strip", yaw=1.5708),
        # Advance forward along +X
        Waypoint(_t(4.0), l_advance, FINGER_CLOSED, "left_advance_step", yaw=1.5708),
        # Lower flush onto tread
        Waypoint(_t(3.0), l_place, FINGER_CLOSED, "left_seat_tread", yaw=1.5708),
        Waypoint(_t(1.5), l_place, FINGER_CLOSED, "left_dwell_settle", yaw=1.5708),
        # Release and retreat
        Waypoint(_t(1.5), l_place, FINGER_OPEN, "left_open_release", yaw=1.5708),
        Waypoint(_t(2.0), l_lift_clear, FINGER_OPEN, "left_lift_clear", yaw=1.5708),
        Waypoint(_t(3.0), l_retreat, FINGER_OPEN, "left_retreat"),
        Waypoint(_t(4.0), l_ready, FINGER_OPEN, "left_hold_success"),
    ]

    if ablation:
        # In ablation: Right arm remains idle at ready pose
        right_wp = [
            Waypoint(_t(31.0), r_ready, FINGER_OPEN, "right_ablation_idle"),
        ]
        return {"left": left_wp, "right": right_wp}

    right_wp = [
        # Start at ready
        Waypoint(_t(2.0), r_ready, FINGER_OPEN, "right_start"),
        # Hover and descend to grasp
        Waypoint(_t(3.0), r_hover_pickup, FINGER_OPEN, "right_hover_pickup", yaw=1.5708),
        Waypoint(_t(2.5), r_grip, FINGER_OPEN, "right_descend_grip", yaw=1.5708),
        Waypoint(_t(1.5), r_grip, FINGER_CLOSED, "right_close_grip", yaw=1.5708),
        # Lift clear of pad and step
        Waypoint(_t(3.0), r_lift, FINGER_CLOSED, "right_lift_strip", yaw=1.5708),
        # Advance forward along +X
        Waypoint(_t(4.0), r_advance, FINGER_CLOSED, "right_advance_step", yaw=1.5708),
        # Lower flush onto tread
        Waypoint(_t(3.0), r_place, FINGER_CLOSED, "right_seat_tread", yaw=1.5708),
        Waypoint(_t(1.5), r_place, FINGER_CLOSED, "right_dwell_settle", yaw=1.5708),
        # Release and retreat
        Waypoint(_t(1.5), r_place, FINGER_OPEN, "right_open_release", yaw=1.5708),
        Waypoint(_t(2.0), r_lift_clear, FINGER_OPEN, "right_lift_clear", yaw=1.5708),
        Waypoint(_t(3.0), r_retreat, FINGER_OPEN, "right_retreat"),
        Waypoint(_t(4.0), r_ready, FINGER_OPEN, "right_hold_success"),
    ]

    return {"left": left_wp, "right": right_wp}
