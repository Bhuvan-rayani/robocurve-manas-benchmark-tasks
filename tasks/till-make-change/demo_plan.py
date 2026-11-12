"""Scripted bimanual demo plans for till_make_change."""

from __future__ import annotations

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint
from geometry import KNOB_GRASP_X_WORLD, KNOB_Y_WORLD, TOKEN_A_HEIGHT_M, TRAY_POS_WORLD

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.0"))


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


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    """Bimanual demo, one arm per side of the midline (left y > +0.08, right y < -0.08).

    Left arm: pinch the drawer knob (y +0.14), pull the drawer out 90 mm (it stays: damped slider), release, retreat.
    Right arm: pick the top 2-unit token, drop it in the tray, pick the top 1-unit token, drop it in the tray.
    Target change: 3 units. In ablation mode the left arm stays idle, so the drawer is never opened.
    """
    l_ready = (0.20, 0.20, TABLE_TOP + 0.16)
    r_ready = (0.20, -0.20, TABLE_TOP + 0.16)
    kx, ky = KNOB_GRASP_X_WORLD, KNOB_Y_WORLD
    tray_x, tray_y = TRAY_POS_WORLD[0], TRAY_POS_WORLD[1]
    hover = TABLE_TOP + 0.12
    # top token of a 4-high stack: pad bottom (13 mm below the TCP) sits 4 mm above the joint to the token below
    grip_z = TABLE_TOP + 3 * TOKEN_A_HEIGHT_M + 0.004 + 0.013
    rel_z = TABLE_TOP + 0.056

    if ablation:
        left = [Waypoint(_s(30.0), l_ready, FINGER_OPEN, "ablation: idle left (drawer stays shut)")]
        right = _right_plan(r_ready, hover, grip_z, rel_z, tray_x, tray_y)
        return {"left": left, "right": right}

    left = [
        Waypoint(_s(1.5), l_ready, FINGER_OPEN, "left ready"),
        Waypoint(_s(1.5), (kx, ky, TABLE_TOP + 0.090), FINGER_OPEN, "left hover knob"),
        Waypoint(_s(1.2), (kx, ky, TABLE_TOP + 0.048), FINGER_OPEN, "left descend knob"),
        Waypoint(_s(0.8), (kx, ky, TABLE_TOP + 0.048), FINGER_CLOSED, "left pinch knob"),
        Waypoint(_s(3.0), (kx - 0.095, ky, TABLE_TOP + 0.048), FINGER_CLOSED, "left pull drawer open"),
        Waypoint(_s(0.8), (kx - 0.095, ky, TABLE_TOP + 0.048), FINGER_OPEN, "left release knob"),
        Waypoint(_s(1.0), (kx - 0.095, ky, TABLE_TOP + 0.100), FINGER_OPEN, "left lift clear"),
        Waypoint(_s(1.5), l_ready, FINGER_OPEN, "left retreat to ready"),
        Waypoint(_s(40.0), l_ready, FINGER_OPEN, "left hold ready"),
    ]
    right = _right_plan(r_ready, hover, grip_z, rel_z, tray_x, tray_y)
    return {"left": left, "right": right}


def _right_plan(r_ready, hover, grip_z, rel_z, tray_x, tray_y) -> list[Waypoint]:
    from geometry import TOKEN_A_XY, TOKEN_B_XY

    wp = [Waypoint(_s(1.5), r_ready, FINGER_OPEN, "right ready")]
    # (stack xy, top-token z offset above grip_z (0: stacks are 4 high), drop y in tray, label)
    for (sx, sy), dy, tag in ((TOKEN_B_XY, -0.025, "coin_b4 (2 units)"), (TOKEN_A_XY, +0.030, "coin_a4 (1 unit)")):
        ty = tray_y + dy
        wp += [
            Waypoint(_s(1.5), (sx, sy, hover), FINGER_OPEN, f"right hover {tag}"),
            Waypoint(_s(1.2), (sx, sy, grip_z), FINGER_OPEN, f"right descend {tag}"),
            Waypoint(_s(0.8), (sx, sy, grip_z), FINGER_CLOSED, f"right grasp {tag}"),
            Waypoint(_s(1.2), (sx, sy, hover), FINGER_CLOSED, f"right lift {tag}"),
            Waypoint(_s(2.0), (tray_x, ty, hover), FINGER_CLOSED, f"right carry {tag}"),
            Waypoint(_s(1.0), (tray_x, ty, rel_z), FINGER_CLOSED, f"right lower {tag}"),
            Waypoint(_s(0.8), (tray_x, ty, rel_z), FINGER_OPEN, f"right release {tag}"),
            Waypoint(_s(1.0), (tray_x, ty, hover), FINGER_OPEN, f"right lift clear {tag}"),
        ]
    wp += [
        Waypoint(_s(1.5), r_ready, FINGER_OPEN, "right retreat to ready"),
        Waypoint(_s(30.0), r_ready, FINGER_OPEN, "right hold ready"),
    ]
    return wp


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by yam_arena demo runner."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
