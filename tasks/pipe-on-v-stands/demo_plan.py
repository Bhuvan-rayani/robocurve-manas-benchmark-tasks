"""Scripted bimanual demo plans for pipe_on_v_stands (T17)."""

from __future__ import annotations

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.8"))


def _s(duration: float) -> float:
    """Scale segment duration."""
    return max(0.1, duration * SCALE)


def make_settle_plan() -> dict[str, list[Waypoint]]:
    """Hold ready pose for 8 seconds."""
    left = [
        Waypoint(_s(8.0), (0.15, 0.25, TABLE_TOP + 0.18), FINGER_OPEN, "settle hold"),
    ]
    right = [
        Waypoint(_s(8.0), (0.15, -0.25, TABLE_TOP + 0.18), FINGER_OPEN, "settle hold"),
    ]
    return {"left": left, "right": right}


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    """Bimanual carry demo for pipe_on_v_stands.

    Left arm operates at y = +0.22 m (> +0.10 m).
    Right arm operates at y = -0.22 m (< -0.10 m).
    Working points are 440 mm apart in y (>> 150 mm requirement).

    In ablation mode: Right arm remains idle at ready pose; Left arm lifts alone
    causing the pipe to tilt and slip (single-arm failure mode).
    """
    l_ready = (0.15, 0.25, TABLE_TOP + 0.18)
    r_ready = (0.15, -0.25, TABLE_TOP + 0.18)

    if ablation:
        left = [
            Waypoint(_s(1.0), l_ready, FINGER_OPEN, "left ready"),
            Waypoint(_s(1.2), (0.18, 0.22, TABLE_TOP + 0.16), FINGER_OPEN, "left hover pick", yaw=1.5708),
            Waypoint(_s(1.2), (0.18, 0.22, TABLE_TOP + 0.05), FINGER_OPEN, "left descend pick", yaw=1.5708),
            Waypoint(_s(0.8), (0.18, 0.22, TABLE_TOP + 0.05), FINGER_CLOSED, "left grasp one end", yaw=1.5708),
            Waypoint(_s(1.5), (0.18, 0.22, TABLE_TOP + 0.18), FINGER_CLOSED, "left lift one end", yaw=1.5708),
            Waypoint(_s(1.5), (0.326, 0.22, TABLE_TOP + 0.18), FINGER_CLOSED, "left carry (pipe tilted)", yaw=1.5708),
            Waypoint(_s(1.5), (0.326, 0.22, TABLE_TOP + 0.122), FINGER_CLOSED, "left place", yaw=1.5708),
            Waypoint(_s(0.8), (0.326, 0.22, TABLE_TOP + 0.122), FINGER_OPEN, "left release", yaw=1.5708),
            Waypoint(_s(1.0), (0.326, 0.22, TABLE_TOP + 0.18), FINGER_OPEN, "left retract up", yaw=1.5708),
            Waypoint(_s(1.5), l_ready, FINGER_OPEN, "left retract home"),
        ]
        right = [
            Waypoint(_s(12.0), r_ready, FINGER_OPEN, "ablation: right arm idle at ready"),
        ]
        return {"left": left, "right": right}

    left = [
        Waypoint(_s(1.0), l_ready, FINGER_OPEN, "left ready"),
        Waypoint(_s(1.2), (0.18, 0.22, TABLE_TOP + 0.16), FINGER_OPEN, "left hover pick", yaw=1.5708),
        Waypoint(_s(1.2), (0.18, 0.22, TABLE_TOP + 0.05), FINGER_OPEN, "left descend pick", yaw=1.5708),
        Waypoint(_s(0.8), (0.18, 0.22, TABLE_TOP + 0.05), FINGER_CLOSED, "left grasp pipe", yaw=1.5708),
        Waypoint(_s(1.5), (0.18, 0.22, TABLE_TOP + 0.18), FINGER_CLOSED, "left lift pipe", yaw=1.5708),
        Waypoint(_s(1.8), (0.326, 0.22, TABLE_TOP + 0.18), FINGER_CLOSED, "left carry forward", yaw=1.5708),
        Waypoint(_s(1.5), (0.326, 0.22, TABLE_TOP + 0.122), FINGER_CLOSED, "left lower to notch", yaw=1.5708),
        Waypoint(_s(0.8), (0.326, 0.22, TABLE_TOP + 0.122), FINGER_OPEN, "left release pipe", yaw=1.5708),
        Waypoint(_s(1.0), (0.326, 0.22, TABLE_TOP + 0.18), FINGER_OPEN, "left retract up", yaw=1.5708),
        Waypoint(_s(1.5), l_ready, FINGER_OPEN, "left retract home"),
        Waypoint(_s(2.0), l_ready, FINGER_OPEN, "left settle dwell"),
    ]

    right = [
        Waypoint(_s(1.0), r_ready, FINGER_OPEN, "right ready"),
        Waypoint(_s(1.2), (0.18, -0.22, TABLE_TOP + 0.16), FINGER_OPEN, "right hover pick", yaw=1.5708),
        Waypoint(_s(1.2), (0.18, -0.22, TABLE_TOP + 0.05), FINGER_OPEN, "right descend pick", yaw=1.5708),
        Waypoint(_s(0.8), (0.18, -0.22, TABLE_TOP + 0.05), FINGER_CLOSED, "right grasp pipe", yaw=1.5708),
        Waypoint(_s(1.5), (0.18, -0.22, TABLE_TOP + 0.18), FINGER_CLOSED, "right lift pipe", yaw=1.5708),
        Waypoint(_s(1.8), (0.326, -0.22, TABLE_TOP + 0.18), FINGER_CLOSED, "right carry forward", yaw=1.5708),
        Waypoint(_s(1.5), (0.326, -0.22, TABLE_TOP + 0.122), FINGER_CLOSED, "right lower to notch", yaw=1.5708),
        Waypoint(_s(0.8), (0.326, -0.22, TABLE_TOP + 0.122), FINGER_OPEN, "right release pipe", yaw=1.5708),
        Waypoint(_s(1.0), (0.326, -0.22, TABLE_TOP + 0.18), FINGER_OPEN, "right retract up", yaw=1.5708),
        Waypoint(_s(1.5), r_ready, FINGER_OPEN, "right retract home"),
        Waypoint(_s(2.0), r_ready, FINGER_OPEN, "right settle dwell"),
    ]

    return {"left": left, "right": right}


def plans(mode: str | None = None) -> dict[str, list[Waypoint]]:
    """Return arm plans according to environment or mode."""
    if mode is None:
        if os.getenv("SETTLE_ONLY") == "1":
            mode = "settle"
        elif os.getenv("ABLATION") == "1":
            mode = "ablation"
        else:
            mode = "demo"

    if mode == "settle":
        return make_settle_plan()
    elif mode == "ablation":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
