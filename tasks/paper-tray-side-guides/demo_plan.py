"""Scripted bimanual demo plans for paper_tray_side_guides."""

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
    """Bimanual demo: Left arm places paper, both arms adjust guides and shut tray.

    Phase 1: Left arm picks paper block from staging pad and places it in open tray.
             Right arm holds ready pose.
    Phase 2: Left arm slides Guide A inward (+y side).
             Right arm slides Guide B inward (-y side).
             Both side guides now touch the paper block sides.
    Phase 3: Both arms push the feed tray shut into the printer frame and hold still.

    In ablation mode: Right arm remains idle, so Guide B is never moved inward,
    resulting in incomplete side guide adjustment (score capped at 0.50).
    """
    l_ready = (0.20, 0.20, TABLE_TOP + 0.16)
    r_ready = (0.20, -0.20, TABLE_TOP + 0.16)

    # Key positions
    # Paper stack pick at (0.14, 0.32)
    paper_pick_hover = (0.14, 0.32, TABLE_TOP + 0.14)
    paper_pick_grasp = (0.14, 0.32, TABLE_TOP + 0.035)

    # Paper place in tray at (0.12, 0.0)
    tray_place_hover = (0.12, 0.0, TABLE_TOP + 0.14)
    tray_place_drop = (0.12, 0.0, TABLE_TOP + 0.038)

    # Guide A (+y side, pushed inward by Left arm at open section x=0.060)
    g_a_hover = (0.060, 0.150, TABLE_TOP + 0.10)
    g_a_contact = (0.060, 0.150, TABLE_TOP + 0.042)
    g_a_pushed = (0.060, 0.112, TABLE_TOP + 0.042)
    g_a_backoff = (0.060, 0.130, TABLE_TOP + 0.042)
    g_a_lift = (0.060, 0.130, TABLE_TOP + 0.14)

    # Guide B (-y side, pushed inward by Right arm at open section x=0.060)
    g_b_hover = (0.060, -0.150, TABLE_TOP + 0.10)
    g_b_contact = (0.060, -0.150, TABLE_TOP + 0.042)
    g_b_pushed = (0.060, -0.112, TABLE_TOP + 0.042)
    g_b_backoff = (0.060, -0.130, TABLE_TOP + 0.042)
    g_b_lift = (0.060, -0.130, TABLE_TOP + 0.14)

    # Tray shut push positions (Left arm pushes rear rim against frame stop)
    l_tray_hover = (-0.020, 0.0, TABLE_TOP + 0.10)
    l_tray_contact = (-0.020, 0.0, TABLE_TOP + 0.030)
    l_tray_pushed = (0.1285, 0.0, TABLE_TOP + 0.030)
    l_tray_lift = (0.1285, 0.0, TABLE_TOP + 0.16)

    if ablation:
        # In ablation mode: Left arm remains idle at ready (paper never placed), score = 0.0
        left = [
            Waypoint(_s(28.4), l_ready, FINGER_OPEN, "ablation: idle left arm"),
        ]
        right = [
            Waypoint(_s(28.4), r_ready, FINGER_OPEN, "ablation: idle right arm"),
        ]
        return {"left": left, "right": right}

    # Bimanual coordinated plan
    left = [
        # Phase 1: Left arm picks paper and places in tray (9.9 s)
        Waypoint(_s(1.5), paper_pick_hover, FINGER_OPEN, "left approach paper"),
        Waypoint(_s(1.2), paper_pick_grasp, FINGER_OPEN, "left descend paper"),
        Waypoint(_s(0.8), paper_pick_grasp, FINGER_CLOSED, "left grasp paper"),
        Waypoint(_s(1.2), paper_pick_hover, FINGER_CLOSED, "left lift paper"),
        Waypoint(_s(2.0), tray_place_hover, FINGER_CLOSED, "left carry paper to tray"),
        Waypoint(_s(1.2), tray_place_drop, FINGER_CLOSED, "left lower paper into tray"),
        Waypoint(_s(0.8), tray_place_drop, FINGER_OPEN, "left release paper"),
        Waypoint(_s(1.2), tray_place_hover, FINGER_OPEN, "left retreat from paper"),

        # Phase 2: Left arm slides Guide A inward (7.3 s)
        Waypoint(_s(1.5), g_a_hover, FINGER_CLOSED, "left hover guide A"),
        Waypoint(_s(1.2), g_a_contact, FINGER_CLOSED, "left descend guide A"),
        Waypoint(_s(1.5), g_a_pushed, FINGER_CLOSED, "left push guide A"),
        Waypoint(_s(0.6), g_a_backoff, FINGER_CLOSED, "left backoff guide A"),
        Waypoint(_s(1.0), g_a_lift, FINGER_CLOSED, "left lift guide A"),
        Waypoint(_s(1.5), g_a_lift, FINGER_CLOSED, "left wait for right to clear"),

        # Phase 3: Left arm pushes tray shut (11.2 s)
        Waypoint(_s(1.5), l_tray_hover, FINGER_CLOSED, "left hover rear tray"),
        Waypoint(_s(1.2), l_tray_contact, FINGER_CLOSED, "left descend rear tray"),
        Waypoint(_s(2.5), l_tray_pushed, FINGER_CLOSED, "left push tray shut"),
        Waypoint(_s(3.0), l_tray_pushed, FINGER_CLOSED, "left hold tray shut"),
        Waypoint(_s(1.0), l_tray_lift, FINGER_OPEN, "left lift straight up"),
        Waypoint(_s(2.0), l_ready, FINGER_OPEN, "left retreat to ready"),
    ]

    right = [
        # Phase 1: Wait for Left arm to place paper in tray (9.9 s)
        Waypoint(_s(9.9), r_ready, FINGER_OPEN, "right wait for paper placement"),

        # Phase 2: Right arm simultaneously slides Guide B inward (7.3 s)
        Waypoint(_s(1.5), g_b_hover, FINGER_CLOSED, "right hover guide B"),
        Waypoint(_s(1.2), g_b_contact, FINGER_CLOSED, "right descend guide B"),
        Waypoint(_s(1.5), g_b_pushed, FINGER_CLOSED, "right push guide B"),
        Waypoint(_s(0.6), g_b_backoff, FINGER_CLOSED, "right backoff guide B"),
        Waypoint(_s(1.0), g_b_lift, FINGER_CLOSED, "right lift guide B"),
        Waypoint(_s(1.5), r_ready, FINGER_OPEN, "right retreat to ready"),

        # Phase 3: Right arm waits at ready while Left arm pushes tray shut (11.2 s)
        Waypoint(_s(11.2), r_ready, FINGER_OPEN, "right wait at ready during tray push"),
    ]

    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by yam_arena demo runner."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
