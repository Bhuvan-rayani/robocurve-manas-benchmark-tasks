"""Scripted bimanual demo plans for floor_opening_cover."""

from __future__ import annotations

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SLOT_X_CMD = 0.24   # slot x
SLOT_Y_CMD = 0.13   # slot |y|
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.2"))


def _s(duration: float) -> float:
    """Scale segment duration."""
    return max(0.1, duration * SCALE)


def make_settle_plan() -> dict[str, list[Waypoint]]:
    """Hold ready pose for 8 seconds."""
    left = [
        Waypoint(_s(8.0), (0.20, 0.20, TABLE_TOP + 0.16), FINGER_OPEN, "settle hold"),
    ]
    right = [
        Waypoint(_s(8.0), (0.20, -0.20, TABLE_TOP + 0.16), FINGER_OPEN, "settle hold"),
    ]
    return {"left": left, "right": right}


YAW90R = 1.5708  # right arm turns +90
YAW90 = -1.5708  # left arm turns the other way: the +90 deg wrist twist leaves its joint range at y < 0.14
L_READY = (0.20, 0.20, TABLE_TOP + 0.16)
R_READY = (0.20, -0.20, TABLE_TOP + 0.16)

# Left arm (y > 0 side): plate handle grip point at plate start; plate goal is the board centre.
HANDLE_Y_OFFSET = 0.0                     # handle is at the plate centre
PLATE_X, PLATE_Y = 0.16, 0.33             # plate start (centre)
GOAL_X, GOAL_Y = 0.30, 0.0                # plate goal (centre)
CARRY_X_CMD = 0.30                        # TCP x command for the carry (hand limit with yaw 90 is ~0.30)
GRIP_Z = TABLE_TOP + 0.058                # TCP on the handle (pads 13 mm below the TCP stay above the plate top)
CARRY_Z = TABLE_TOP + 0.14
# Release: plate bottom 25 mm above the board top (grip height is 28 mm above the plate bottom)
RELEASE_Z = TABLE_TOP + 0.050 + 0.025 + 0.028

PIN_GRIP_Z = TABLE_TOP + 0.062            # TCP near the pin top (pin top 0.065)
PIN_DROP_Z = TABLE_TOP + 0.075            # release: pin bottom ~3 mm above the slot floor, pad bottoms 2 mm above the plate top
PIN_CARRY_Z = TABLE_TOP + 0.14


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    """Bimanual demo for floor_opening_cover.

    The left arm (+y) lifts the plate by its 4 x 8 x 2 cm handle (yaw 90), carries it to the board and releases it
    25 mm above the board, then seats pin A (left rack) in slot A at (0.24, +0.13). The right arm (-y) waits at its
    ready pose and then seats pin B in slot B at (0.24, -0.13). The arms work one after the other, on their own side
    of the midline, so the hands are always >= 150 mm apart.

    In ablation mode both arms stay idle, so nothing is placed.
    """
    if ablation:
        return {
            "left": [Waypoint(_s(43.0), L_READY, FINGER_OPEN, "ablation: idle left")],
            "right": [Waypoint(_s(43.0), R_READY, FINGER_OPEN, "ablation: idle right")],
        }

    hy = PLATE_Y + HANDLE_Y_OFFSET
    gy = GOAL_Y + HANDLE_Y_OFFSET
    left = [
        Waypoint(_s(1.0), L_READY, FINGER_OPEN, "left ready"),
        Waypoint(_s(1.4), (PLATE_X, hy, TABLE_TOP + 0.14), FINGER_OPEN, "left hover handle", yaw=YAW90),
        Waypoint(_s(1.2), (PLATE_X, hy, GRIP_Z), FINGER_OPEN, "left descend handle", yaw=YAW90),
        Waypoint(_s(0.8), (PLATE_X, hy, GRIP_Z), FINGER_CLOSED, "left grip handle", yaw=YAW90),
        Waypoint(_s(1.0), (PLATE_X, hy, CARRY_Z), FINGER_CLOSED, "left lift plate", yaw=YAW90),
        Waypoint(_s(2.0), (CARRY_X_CMD, gy, CARRY_Z), FINGER_CLOSED, "left carry plate", yaw=YAW90),
        Waypoint(_s(1.2), (CARRY_X_CMD, gy, RELEASE_Z), FINGER_CLOSED, "left lower plate", yaw=YAW90),
        Waypoint(_s(0.8), (CARRY_X_CMD, gy, RELEASE_Z), FINGER_OPEN, "left release plate", yaw=YAW90),
        Waypoint(_s(1.0), (CARRY_X_CMD, gy, CARRY_Z), FINGER_OPEN, "left lift clear", yaw=YAW90),
        Waypoint(_s(1.2), (0.30, 0.33, TABLE_TOP + 0.14), FINGER_OPEN, "left hover pin a", yaw=YAW90),
        Waypoint(_s(1.0), (0.30, 0.33, PIN_GRIP_Z), FINGER_OPEN, "left descend pin a", yaw=YAW90),
        Waypoint(_s(0.8), (0.30, 0.33, PIN_GRIP_Z), FINGER_CLOSED, "left grip pin a", yaw=YAW90),
        Waypoint(_s(1.0), (0.30, 0.33, PIN_CARRY_Z), FINGER_CLOSED, "left lift pin a", yaw=YAW90),
        Waypoint(_s(1.6), (SLOT_X_CMD, SLOT_Y_CMD, PIN_CARRY_Z), FINGER_CLOSED, "left carry pin a", yaw=YAW90),
        Waypoint(_s(1.0), (SLOT_X_CMD, SLOT_Y_CMD, PIN_DROP_Z), FINGER_CLOSED, "left lower pin a", yaw=YAW90),
        Waypoint(_s(0.8), (SLOT_X_CMD, SLOT_Y_CMD, PIN_DROP_Z), FINGER_OPEN, "left release pin a", yaw=YAW90),
        Waypoint(_s(1.0), (SLOT_X_CMD, SLOT_Y_CMD, PIN_CARRY_Z), FINGER_OPEN, "left lift clear", yaw=YAW90),
        Waypoint(_s(1.6), L_READY, FINGER_OPEN, "left retreat to ready"),
        Waypoint(_s(14.0), L_READY, FINGER_OPEN, "left wait for right"),
    ]
    t_left = sum(w.duration for w in left) / SCALE

    right = [
        Waypoint(_s(t_left - 1.0 + 1.0), R_READY, FINGER_OPEN, "right wait for left"),
        Waypoint(_s(1.4), (0.16, -0.33, TABLE_TOP + 0.14), FINGER_OPEN, "right hover pin b", yaw=YAW90R),
        Waypoint(_s(1.0), (0.16, -0.33, PIN_GRIP_Z), FINGER_OPEN, "right descend pin b", yaw=YAW90R),
        Waypoint(_s(0.8), (0.16, -0.33, PIN_GRIP_Z), FINGER_CLOSED, "right grip pin b", yaw=YAW90R),
        Waypoint(_s(1.0), (0.16, -0.33, PIN_CARRY_Z), FINGER_CLOSED, "right lift pin b", yaw=YAW90R),
        Waypoint(_s(1.6), (SLOT_X_CMD, -SLOT_Y_CMD, PIN_CARRY_Z), FINGER_CLOSED, "right carry pin b", yaw=YAW90R),
        Waypoint(_s(1.0), (SLOT_X_CMD, -SLOT_Y_CMD, PIN_DROP_Z), FINGER_CLOSED, "right lower pin b", yaw=YAW90R),
        Waypoint(_s(0.8), (SLOT_X_CMD, -SLOT_Y_CMD, PIN_DROP_Z), FINGER_OPEN, "right release pin b", yaw=YAW90R),
        Waypoint(_s(1.0), (SLOT_X_CMD, -SLOT_Y_CMD, PIN_CARRY_Z), FINGER_OPEN, "right lift clear", yaw=YAW90R),
        Waypoint(_s(1.6), R_READY, FINGER_OPEN, "right retreat to ready"),
        Waypoint(_s(6.0), R_READY, FINGER_OPEN, "right hold ready"),
    ]
    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by yam_arena demo runner."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
