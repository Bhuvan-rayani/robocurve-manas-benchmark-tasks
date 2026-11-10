"""Scripted bimanual demo plans for resistor_band_pick."""

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
        Waypoint(_s(8.0), (0.20, 0.20, TABLE_TOP + 0.16), FINGER_OPEN, "settle hold"),
    ]
    right = [
        Waypoint(_s(8.0), (0.20, -0.20, TABLE_TOP + 0.16), FINGER_OPEN, "settle hold"),
    ]
    return {"left": left, "right": right}


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    """Bimanual demo: Left arm picks target resistor and seats it in socket;
    Right arm pushes socket cover open and holds it open during insertion.

    Left arm base at +y, right arm base at -y.
    Phase 1: Left arm approaches and grips target resistor res_c at (0.29, 0.08).
    Phase 2: Right arm descends to cover push surface at (0.36, -0.06) and slides cover along +X to (0.40, -0.06).
    Phase 3: Right arm holds cover open while Left arm carries res_c and seats it inside the socket at (0.30, -0.06).
    Phase 4: Left arm releases res_c and retreats to ready.
    Phase 5: Right arm eases back to (0.36, -0.06), allowing spring to close cover, then retreats to ready.

    In ablation mode: Right arm remains idle, so the cover stays closed;
    Left arm brings res_c over the socket but cannot seat it (ablation score: 0.75).
    """
    # Key coordinates
    l_ready = (0.20, 0.20, TABLE_TOP + 0.14)
    r_ready = (0.20, -0.20, TABLE_TOP + 0.14)

    # Resistor res_c coordinates (pocket floor z=0.010, cylinder top z=0.080)
    res_hover = (0.29, 0.08, TABLE_TOP + 0.14)
    res_grasp = (0.29, 0.08, TABLE_TOP + 0.060)
    res_lift = (0.29, 0.08, TABLE_TOP + 0.14)

    # Socket coordinates
    socket_hover = (0.26, -0.06, TABLE_TOP + 0.14)
    # release with the pad bottoms (TCP - 13 mm) still above the 80 mm collar: the resistor (46 mm below the TCP) is ~25 mm inside the hole and drops the rest
    socket_seat = (0.26, -0.06, TABLE_TOP + 0.105)

    # Socket cover push coordinates (push along +X from 0.36 to 0.40)
    cover_hover = (0.32, -0.22, TABLE_TOP + 0.14)
    cover_contact = (0.32, -0.22, TABLE_TOP + 0.090)
    cover_pushed = (0.365, -0.22, TABLE_TOP + 0.090)

    if ablation:
        # Right arm remains idle; Left arm hovers over socket but cannot insert
        left = [
            Waypoint(_s(1.5), res_hover, FINGER_OPEN, "left hover res_c"),
            Waypoint(_s(1.5), res_grasp, FINGER_OPEN, "left descend res_c"),
            Waypoint(_s(1.0), res_grasp, FINGER_CLOSED, "left grip res_c"),
            Waypoint(_s(1.5), res_lift, FINGER_CLOSED, "left lift res_c"),
            Waypoint(_s(2.0), socket_hover, FINGER_CLOSED, "left carry to socket hover"),
            Waypoint(_s(8.5), socket_hover, FINGER_CLOSED, "left hold above closed cover"),
            Waypoint(_s(2.0), l_ready, FINGER_CLOSED, "left retreat with resistor"),
            Waypoint(_s(3.0), l_ready, FINGER_CLOSED, "left hold ready"),
        ]
        right = [
            Waypoint(_s(21.0), r_ready, FINGER_OPEN, "ablation: idle right arm"),
        ]
        return {"left": left, "right": right}

    # Bimanual coordinated plan
    left = [
        # Phase 1: Pick res_c
        Waypoint(_s(1.5), res_hover, FINGER_OPEN, "left hover res_c"),
        Waypoint(_s(1.5), res_grasp, FINGER_OPEN, "left descend res_c"),
        Waypoint(_s(1.0), res_grasp, FINGER_CLOSED, "left grip res_c"),
        Waypoint(_s(1.5), res_lift, FINGER_CLOSED, "left lift res_c"),

        # Phase 2: Carry over to socket hover and wait for right arm to open cover
        Waypoint(_s(2.0), socket_hover, FINGER_CLOSED, "left carry to socket hover"),
        Waypoint(_s(1.0), socket_hover, FINGER_CLOSED, "left wait for cover open"),

        # Phase 3: Lower res_c into open socket, release, and lift
        Waypoint(_s(2.0), socket_seat, FINGER_CLOSED, "left seat res_c in socket"),
        Waypoint(_s(1.0), socket_seat, FINGER_OPEN, "left release res_c"),
        Waypoint(_s(1.5), socket_hover, FINGER_OPEN, "left lift from socket"),

        # Phase 4: Retreat to ready pose
        Waypoint(_s(2.0), l_ready, FINGER_OPEN, "left retreat ready"),
        Waypoint(_s(3.0), l_ready, FINGER_OPEN, "left hold ready"),
    ]

    right = [
        # Phase 1 & 2: Descend on cover push surface and push open along +X
        Waypoint(_s(2.0), cover_hover, FINGER_CLOSED, "right hover cover"),
        Waypoint(_s(1.5), cover_contact, FINGER_CLOSED, "right descend cover push"),
        Waypoint(_s(2.0), cover_pushed, FINGER_CLOSED, "right push cover open"),

        # Phase 3: Hold cover open while left arm seats, releases, and lifts (2.0 + 1.0 + 1.5 = 4.5s)
        Waypoint(_s(7.5), cover_pushed, FINGER_CLOSED, "right hold cover open"),

        # Phase 4: Ease back to let spring close cover, lift, and retreat
        Waypoint(_s(1.5), cover_contact, FINGER_CLOSED, "right ease back close cover"),
        Waypoint(_s(1.5), cover_hover, FINGER_CLOSED, "right lift cover"),
        Waypoint(_s(2.0), r_ready, FINGER_OPEN, "right retreat ready"),
        Waypoint(_s(3.0), r_ready, FINGER_OPEN, "right hold ready"),
    ]

    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by yam_arena demo runner."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
