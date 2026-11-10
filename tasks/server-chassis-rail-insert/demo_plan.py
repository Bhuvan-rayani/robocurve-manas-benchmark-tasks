"""Scripted bimanual demo plans for server_chassis_rail_insert."""

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
    """Coordinated bimanual demo: Both arms push symmetrically to slide the chassis into the rack.

    Left arm base at +y, right arm base at -y.
    Phase 1: Both arms approach hover in front of the chassis at y = +-0.095 m.
    Phase 2: Both arms descend to contact height (z = TABLE_TOP + 0.082 m).
    Phase 3: Smooth coordinated multi-stage push along +X into the rails until ears are flush.
    Phase 4: Dwell flush for 4.0 s (guaranteeing >= 1.0 s stillness for success hold).
    Phase 5: Both arms lift and retreat to ready.

    Ablation mode: Left arm remains idle; Right arm attempts single-handed push.
    Single-handed off-centre push creates yaw torque that cocks and binds the chassis in the rails.
    """
    l_ready = (0.20, 0.20, TABLE_TOP + 0.16)
    r_ready = (0.20, -0.20, TABLE_TOP + 0.16)

    # Lateral push coordinates (symmetrical about midline)
    l_y = 0.095
    r_y = -0.095

    # Heights
    z_hover = TABLE_TOP + 0.160
    z_contact = TABLE_TOP + 0.082

    # Waypoint X coordinates
    x_approach = 0.160
    x_stage1 = 0.240
    x_stage2 = 0.320
    x_flush = 0.394

    if ablation:
        # Left arm idle throughout
        left = [
            Waypoint(_s(30.0), l_ready, FINGER_OPEN, "ablation: idle left"),
        ]
        # Right arm pushes alone, causing cocking and jamming
        right = [
            Waypoint(_s(1.8), (x_approach, r_y, z_hover), FINGER_CLOSED, "right approach hover"),
            Waypoint(_s(1.8), (x_approach, r_y, z_contact), FINGER_CLOSED, "right descend contact"),
            Waypoint(_s(2.5), (x_stage1, r_y, z_contact), FINGER_CLOSED, "right uncoordinated push 1"),
            Waypoint(_s(2.5), (x_stage2, r_y, z_contact), FINGER_CLOSED, "right uncoordinated push 2"),
            Waypoint(_s(2.5), (x_flush, r_y, z_contact), FINGER_CLOSED, "right uncoordinated push flush"),
            Waypoint(_s(4.0), (x_flush, r_y, z_contact), FINGER_CLOSED, "right hold"),
            Waypoint(_s(1.5), (x_flush, -0.200, z_contact), FINGER_CLOSED, "right step out sideways"),
            Waypoint(_s(1.8), (x_flush - 0.100, -0.200, z_hover), FINGER_CLOSED, "right lift and back"),
            Waypoint(_s(2.5), r_ready, FINGER_OPEN, "right retreat to ready"),
        ]
        return {"left": left, "right": right}

    # Bimanual coordinated plan
    left = [
        Waypoint(_s(1.8), (x_approach, l_y, z_hover), FINGER_CLOSED, "left approach hover"),
        Waypoint(_s(1.8), (x_approach, l_y, z_contact), FINGER_CLOSED, "left descend contact"),
        Waypoint(_s(2.5), (x_stage1, l_y, z_contact), FINGER_CLOSED, "bimanual push stage 1"),
        Waypoint(_s(2.5), (x_stage2, l_y, z_contact), FINGER_CLOSED, "bimanual push stage 2"),
        Waypoint(_s(2.5), (x_flush, l_y, z_contact), FINGER_CLOSED, "bimanual push flush"),
        Waypoint(_s(4.0), (x_flush, l_y, z_contact), FINGER_CLOSED, "hold flush for success"),
        Waypoint(_s(1.5), (x_flush, +0.200, z_contact), FINGER_CLOSED, "left step out sideways"),
        Waypoint(_s(1.8), (x_flush - 0.100, +0.200, z_hover), FINGER_CLOSED, "left lift and back"),
        Waypoint(_s(2.5), l_ready, FINGER_OPEN, "left retreat to ready"),
    ]

    right = [
        Waypoint(_s(1.8), (x_approach, r_y, z_hover), FINGER_CLOSED, "right approach hover"),
        Waypoint(_s(1.8), (x_approach, r_y, z_contact), FINGER_CLOSED, "right descend contact"),
        Waypoint(_s(2.5), (x_stage1, r_y, z_contact), FINGER_CLOSED, "bimanual push stage 1"),
        Waypoint(_s(2.5), (x_stage2, r_y, z_contact), FINGER_CLOSED, "bimanual push stage 2"),
        Waypoint(_s(2.5), (x_flush, r_y, z_contact), FINGER_CLOSED, "bimanual push flush"),
        Waypoint(_s(4.0), (x_flush, r_y, z_contact), FINGER_CLOSED, "hold flush for success"),
        Waypoint(_s(1.5), (x_flush, -0.200, z_contact), FINGER_CLOSED, "right step out sideways"),
        Waypoint(_s(1.8), (x_flush - 0.100, -0.200, z_hover), FINGER_CLOSED, "right lift and back"),
        Waypoint(_s(2.5), r_ready, FINGER_OPEN, "right retreat to ready"),
    ]

    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by yam_arena demo runner."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
