"""Scripted bimanual demo plans for window_restrictor_fit.

Left arm (y > 0) carries the stop block from the pad at y +0.20 into the 100 mm pocket at y +0.078 and goes back to its
ready pose. Right arm (y < 0) then pushes the sash open from behind by its rear tab until the block stops it. The arms
stay >= 150 mm apart in y the whole time.
"""

from __future__ import annotations

import os

from geometry import BLOCK_START_POS_WORLD, FRAME_POS_WORLD, HOLE_Y_COORDS, TARGET_HOLE_INDEX
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.8"))

L_READY = (0.20, 0.24, TABLE_TOP + 0.16)
R_READY = (0.20, -0.20, TABLE_TOP + 0.16)

# Pick: TCP 20 mm above the block origin (pads end 13 mm below the TCP, 7 mm above the block bottom)
PICK_DZ = float(os.getenv("DEMO_PICK_DZ", "0.020"))
# Release: block (TCP - 20 mm) peg bottom is TCP - 26 mm; floor top is +0.006 => TCP +0.066 drops it ~28 mm
RELEASE_Z = TABLE_TOP + float(os.getenv("DEMO_RELEASE_DZ", "0.066"))
CARRY_Z = TABLE_TOP + 0.11
HOLE_X = FRAME_POS_WORLD[0]
HOLE_Y = HOLE_Y_COORDS[TARGET_HOLE_INDEX]

# Push: TCP z puts the pad bottoms 13 mm lower inside the 45 mm tab (top +0.061)
PUSH_Z = TABLE_TOP + 0.055
PUSH_X = float(os.getenv("DEMO_PUSH_X", "0.28"))
PUSH_Y0 = float(os.getenv("DEMO_PUSH_Y0", "-0.215"))
PUSH_Y1 = float(os.getenv("DEMO_PUSH_Y1", "-0.075"))   # beyond the goal (the block stops the sash at about -0.12)


def _s(duration: float) -> float:
    """Scale segment duration."""
    return max(0.1, duration * SCALE)


def make_settle_plan() -> dict[str, list[Waypoint]]:
    """Hold ready pose for 8 seconds."""
    left = [Waypoint(_s(8.0), L_READY, FINGER_OPEN, "settle hold")]
    right = [Waypoint(_s(8.0), R_READY, FINGER_OPEN, "settle hold")]
    return {"left": left, "right": right}


def _right_push() -> list[Waypoint]:
    return [
        Waypoint(_s(1.5), (PUSH_X, PUSH_Y0, TABLE_TOP + 0.11), FINGER_CLOSED, "right hover behind sash tab"),
        Waypoint(_s(1.2), (PUSH_X, PUSH_Y0, PUSH_Z), FINGER_CLOSED, "right descend behind tab"),
        Waypoint(_s(3.5), (PUSH_X, PUSH_Y1, PUSH_Z), FINGER_CLOSED, "right push sash open until the block stops it"),
        Waypoint(_s(1.0), (PUSH_X, PUSH_Y1, PUSH_Z), FINGER_CLOSED, "right hold push"),
        Waypoint(_s(1.2), (PUSH_X, PUSH_Y1, TABLE_TOP + 0.12), FINGER_OPEN, "right lift straight up"),
        Waypoint(_s(1.8), R_READY, FINGER_OPEN, "right retreat ready"),
    ]


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    """Left arm places the block, right arm pushes the sash. Ablation: left arm never places the block."""
    bx, by = BLOCK_START_POS_WORLD[0], BLOCK_START_POS_WORLD[1]
    pick_z = BLOCK_START_POS_WORLD[2] + PICK_DZ

    left_place = [
        Waypoint(_s(1.5), (bx, by, TABLE_TOP + 0.11), FINGER_OPEN, "left hover block"),
        Waypoint(_s(1.2), (bx, by, pick_z), FINGER_OPEN, "left descend block"),
        Waypoint(_s(0.8), (bx, by, pick_z), FINGER_CLOSED, "left grip block"),
        Waypoint(_s(1.2), (bx, by, CARRY_Z), FINGER_CLOSED, "left lift block"),
        Waypoint(_s(1.5), (HOLE_X, HOLE_Y, CARRY_Z), FINGER_CLOSED, "left carry over pocket"),
        Waypoint(_s(1.2), (HOLE_X, HOLE_Y, RELEASE_Z), FINGER_CLOSED, "left lower to release height"),
        Waypoint(_s(0.8), (HOLE_X, HOLE_Y, RELEASE_Z), FINGER_OPEN, "left release block"),
        Waypoint(_s(1.0), (HOLE_X, HOLE_Y, CARRY_Z), FINGER_OPEN, "left lift straight up"),
        Waypoint(_s(1.5), L_READY, FINGER_OPEN, "left retreat ready"),
    ]
    right_wait_s = sum(w.duration for w in left_place)
    right_push = _right_push()
    right_total = right_wait_s + sum(w.duration for w in right_push)

    if ablation:
        left = [Waypoint(right_total + _s(6.0), L_READY, FINGER_OPEN, "ablation: left idle, block never placed")]
    else:
        left = left_place + [Waypoint(sum(w.duration for w in right_push) + _s(6.0), L_READY, FINGER_OPEN, "left parked")]

    right = [Waypoint(right_wait_s, R_READY, FINGER_OPEN, "right parked while the block is placed")]
    right += right_push
    right += [Waypoint(_s(6.0), R_READY, FINGER_OPEN, "right settle hold")]
    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point matching yam_arena task file demo interface."""
    if os.getenv("SETTLE_ONLY"):
        return make_settle_plan()
    if os.getenv("ABLATION"):
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
