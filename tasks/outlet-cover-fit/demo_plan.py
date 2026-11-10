"""Scripted bimanual demo plans for outlet_cover_fit."""

from __future__ import annotations

import os
from geometry import (
    CAP_A_START_POS_WORLD,
    CAP_B_START_POS_WORLD,
    CAP_C_START_POS_WORLD,
    PLATE_LEFT_HOLD_WORLD,
    PLATE_RIGHT_HOLD_WORLD,
    SOCKET_A_OFFSET_M,
    SOCKET_B_OFFSET_M,
    SOCKET_C_OFFSET_M,
    TABLE_TOP,
)
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN
from yam_arena.demo import Waypoint

SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.5"))


def _s(duration: float) -> float:
    return max(0.1, duration * SCALE)


def make_settle_plan() -> dict[str, list[Waypoint]]:
    """Hold ready pose for 8 seconds."""
    left = [
        Waypoint(_s(8.0), (0.20, 0.22, TABLE_TOP + 0.18), FINGER_OPEN, "settle hold"),
    ]
    right = [
        Waypoint(_s(8.0), (0.20, -0.22, TABLE_TOP + 0.18), FINGER_OPEN, "settle hold"),
    ]
    return {"left": left, "right": right}


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    """Bimanual demo for outlet cover safety caps.

    Left arm base at +y, right arm base at -y.
    Phase 1: Left arm braces left hold zone on loose plate; Right arm picks and inserts Cap C.
    Phase 2: Right arm braces right hold zone on loose plate; Left arm picks and inserts Cap A.
    Phase 3: Right arm continues bracing; Left arm picks and inserts Cap B in center socket.

    In ablation mode: Left arm remains idle at ready pose (unbraced), causing loose plate drift.
    """
    l_ready = (0.20, 0.22, TABLE_TOP + 0.18)
    r_ready = (0.20, -0.22, TABLE_TOP + 0.18)

    # Plate hold points (at table + 0.022 m)
    l_hold = PLATE_LEFT_HOLD_WORLD
    l_hold_hover = (l_hold[0], l_hold[1], TABLE_TOP + 0.12)

    r_hold = PLATE_RIGHT_HOLD_WORLD
    r_hold_hover = (r_hold[0], r_hold[1], TABLE_TOP + 0.12)

    # Socket insertion positions (top of socket well)
    # GPU run (cap_b): with the TCP at +0.022 the pad bottoms (TCP - 13 mm) were 8 mm below the plate top, inside the 7 mm gap beside the cap, and dragged it out.
    # Release 40 mm above the table: pad bottoms stay ~10 mm above the plate top and the cap drops the last ~20 mm into the socket.
    z_insert = TABLE_TOP + float(os.getenv("DEMO_Z_INSERT", "0.040"))
    z_carry = TABLE_TOP + 0.12

    sock_c_hover = (0.30 + SOCKET_C_OFFSET_M[0], SOCKET_C_OFFSET_M[1], z_carry)
    sock_c_insert = (0.30 + SOCKET_C_OFFSET_M[0], SOCKET_C_OFFSET_M[1], z_insert)

    sock_a_hover = (0.30 + SOCKET_A_OFFSET_M[0], SOCKET_A_OFFSET_M[1], z_carry)
    sock_a_insert = (0.30 + SOCKET_A_OFFSET_M[0], SOCKET_A_OFFSET_M[1], z_insert)

    sock_b_hover = (0.30 + SOCKET_B_OFFSET_M[0], SOCKET_B_OFFSET_M[1], z_carry)
    sock_b_insert = (0.30 + SOCKET_B_OFFSET_M[0], SOCKET_B_OFFSET_M[1], z_insert)

    # Pick positions (cylinder start)
    z_pick = TABLE_TOP + 0.020
    cap_c_hover = (CAP_C_START_POS_WORLD[0], CAP_C_START_POS_WORLD[1], z_carry)
    cap_c_pick = (CAP_C_START_POS_WORLD[0], CAP_C_START_POS_WORLD[1], z_pick)

    cap_a_hover = (CAP_A_START_POS_WORLD[0], CAP_A_START_POS_WORLD[1], z_carry)
    cap_a_pick = (CAP_A_START_POS_WORLD[0], CAP_A_START_POS_WORLD[1], z_pick)

    cap_b_hover = (CAP_B_START_POS_WORLD[0], CAP_B_START_POS_WORLD[1], z_carry)
    cap_b_pick = (CAP_B_START_POS_WORLD[0], CAP_B_START_POS_WORLD[1], z_pick)

    if ablation:
        left = [
            Waypoint(_s(30.0), l_ready, FINGER_OPEN, "ablation: idle left (no plate bracing)"),
        ]
        right = [
            # Right arm attempts to insert caps without left arm bracing plate
            Waypoint(_s(1.2), cap_c_hover, FINGER_OPEN, "right hover cap c"),
            Waypoint(_s(1.0), cap_c_pick, FINGER_OPEN, "right descend cap c"),
            Waypoint(_s(0.8), cap_c_pick, FINGER_CLOSED, "right grasp cap c"),
            Waypoint(_s(1.0), cap_c_hover, FINGER_CLOSED, "right lift cap c"),
            Waypoint(_s(1.4), sock_c_hover, FINGER_CLOSED, "right carry cap c"),
            Waypoint(_s(1.2), sock_c_insert, FINGER_CLOSED, "right press cap c (slides unbraced plate)"),
            Waypoint(_s(0.8), sock_c_insert, FINGER_OPEN, "right release cap c"),
            Waypoint(_s(1.0), sock_c_hover, FINGER_OPEN, "right retreat cap c"),
            Waypoint(_s(2.0), r_ready, FINGER_OPEN, "right retreat to ready"),
            Waypoint(_s(18.0), r_ready, FINGER_OPEN, "right idle"),
        ]
        return {"left": left, "right": right}

    left = [
        # Phase 1: Left arm braces plate while Right arm places Cap C (8.8 s unscaled)
        Waypoint(_s(1.2), l_ready, FINGER_OPEN, "left wait start"),
        Waypoint(_s(1.2), l_hold_hover, FINGER_CLOSED, "left hover hold zone"),
        Waypoint(_s(1.0), l_hold, FINGER_CLOSED, "left descend brace plate"),
        Waypoint(_s(5.4), l_hold, FINGER_CLOSED, "left hold brace plate"),
        Waypoint(_s(0.8), l_hold_hover, FINGER_CLOSED, "left lift from brace"),
        Waypoint(_s(1.2), l_ready, FINGER_OPEN, "left retreat to ready"),
        # Phase 2: Left arm picks and places Cap A while Right arm braces (8.8 s unscaled)
        Waypoint(_s(1.2), l_ready, FINGER_OPEN, "left wait for right brace"),
        Waypoint(_s(1.0), cap_a_hover, FINGER_OPEN, "left hover cap a"),
        Waypoint(_s(0.8), cap_a_pick, FINGER_OPEN, "left descend cap a"),
        Waypoint(_s(0.8), cap_a_pick, FINGER_CLOSED, "left grasp cap a"),
        Waypoint(_s(0.8), cap_a_hover, FINGER_CLOSED, "left lift cap a"),
        Waypoint(_s(1.2), sock_a_hover, FINGER_CLOSED, "left carry cap a"),
        Waypoint(_s(1.0), sock_a_insert, FINGER_CLOSED, "left insert cap a"),
        Waypoint(_s(0.6), sock_a_insert, FINGER_OPEN, "left release cap a"),
        Waypoint(_s(0.8), sock_a_hover, FINGER_OPEN, "left retreat cap a"),
        Waypoint(_s(1.2), l_ready, FINGER_OPEN, "left retreat to ready"),
        # Phase 3: Left arm picks and places Cap B while Right arm continues bracing (9.0 s unscaled)
        Waypoint(_s(1.0), cap_b_hover, FINGER_OPEN, "left hover cap b"),
        Waypoint(_s(0.8), cap_b_pick, FINGER_OPEN, "left descend cap b"),
        Waypoint(_s(0.8), cap_b_pick, FINGER_CLOSED, "left grasp cap b"),
        Waypoint(_s(0.8), cap_b_hover, FINGER_CLOSED, "left lift cap b"),
        Waypoint(_s(1.2), sock_b_hover, FINGER_CLOSED, "left carry cap b"),
        Waypoint(_s(1.0), sock_b_insert, FINGER_CLOSED, "left insert cap b"),
        Waypoint(_s(0.6), sock_b_insert, FINGER_OPEN, "left release cap b"),
        Waypoint(_s(0.8), sock_b_hover, FINGER_OPEN, "left retreat cap b"),
        Waypoint(_s(2.0), l_ready, FINGER_OPEN, "left finish at ready"),
    ]

    right = [
        # Phase 1: Right arm picks and places Cap C while Left arm braces (8.8 s unscaled)
        Waypoint(_s(1.2), r_ready, FINGER_OPEN, "right wait for left brace"),
        Waypoint(_s(1.0), cap_c_hover, FINGER_OPEN, "right hover cap c"),
        Waypoint(_s(0.8), cap_c_pick, FINGER_OPEN, "right descend cap c"),
        Waypoint(_s(0.8), cap_c_pick, FINGER_CLOSED, "right grasp cap c"),
        Waypoint(_s(0.8), cap_c_hover, FINGER_CLOSED, "right lift cap c"),
        Waypoint(_s(1.2), sock_c_hover, FINGER_CLOSED, "right carry cap c"),
        Waypoint(_s(1.0), sock_c_insert, FINGER_CLOSED, "right insert cap c"),
        Waypoint(_s(0.6), sock_c_insert, FINGER_OPEN, "right release cap c"),
        Waypoint(_s(0.8), sock_c_hover, FINGER_OPEN, "right retreat cap c"),
        Waypoint(_s(1.2), r_ready, FINGER_OPEN, "right retreat to ready"),
        # Phase 2: Right arm moves to right hold and braces plate (8.8 s unscaled)
        Waypoint(_s(1.2), r_ready, FINGER_OPEN, "right prepare brace"),
        Waypoint(_s(1.2), r_hold_hover, FINGER_CLOSED, "right hover right hold"),
        Waypoint(_s(1.0), r_hold, FINGER_CLOSED, "right descend brace plate"),
        Waypoint(_s(5.4), r_hold, FINGER_CLOSED, "right hold brace plate (phase 2)"),
        # Phase 3: Right arm continues bracing during Cap B placement (9.0 s unscaled)
        Waypoint(_s(7.0), r_hold, FINGER_CLOSED, "right hold brace plate (phase 3)"),
        Waypoint(_s(0.8), r_hold_hover, FINGER_CLOSED, "right lift from brace"),
        Waypoint(_s(2.0), r_ready, FINGER_OPEN, "right finish at ready"),
    ]

    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by yam_arena demo runner."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
