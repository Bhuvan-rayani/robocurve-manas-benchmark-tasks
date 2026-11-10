"""Scripted bimanual demo plans for dip_address_setting."""

from __future__ import annotations

import os
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

TABLE_TOP = TABLE_HEIGHT
SCALE = float(os.getenv("DEMO_TIME_SCALE", "1.5"))


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
    """Bimanual demo: Both arms coordinate bracing and switch flicking.

    Left arm base at +y, right arm base at -y.
    Rebuilt larger module: 140 x 260 x 30 mm at (0.30, 0.0).
    Hold zones at y = +0.125 (Left) and y = -0.125 (Right).
    Working points kept >= 150 mm apart in y throughout.

    Phase 1: Left arm holds at y = +0.125; Right arm sets Knobs 4 and 3.
      - Knob 4 (y = -0.075, starts DOWN): flicked along +x to UP.
      - Knob 3 (y = -0.025, starts UP): pushed along -x to DOWN.
    Phase 2: Right arm holds at y = -0.125; Left arm sets Knobs 2 and 1.
      - Knob 2 (y = +0.025, starts UP): pushed along -x to DOWN.
      - Knob 1 (y = +0.075, starts DOWN): flicked along +x to UP.
    Phase 3: Left arm holds at y = +0.125; Right arm presses commit button at (0.253, 0.0).
    """
    l_ready = (0.20, 0.22, TABLE_TOP + 0.18)
    r_ready = (0.20, -0.22, TABLE_TOP + 0.18)

    # Bracing points on module ends (module top is at z = TABLE_TOP + 0.030)
    l_brace_hover = (0.30, 0.125, TABLE_TOP + 0.080)
    l_brace = (0.30, 0.125, TABLE_TOP + 0.031)
    r_brace_hover = (0.30, -0.125, TABLE_TOP + 0.080)
    r_brace = (0.30, -0.125, TABLE_TOP + 0.031)

    # Knob Z levels: module top is +0.030, knob height is 0.014 (top at +0.044)
    # Flick contact height: TABLE_TOP + 0.036
    z_flick = TABLE_TOP + 0.036
    z_hover = TABLE_TOP + 0.075

    # Knob 4 (y = -0.075, flick along +X: contact at x=0.325, push to x=0.345)
    k4_hover1 = (0.320, -0.075, z_hover)
    k4_contact = (0.320, -0.075, z_flick)
    k4_pushed = (0.348, -0.075, z_flick)
    k4_hover2 = (0.348, -0.075, z_hover)

    # Knob 3 (y = -0.025, push along -X: contact at x=0.355, push to x=0.330)
    k3_hover1 = (0.355, -0.025, z_hover)
    k3_contact = (0.355, -0.025, z_flick)
    k3_pushed = (0.328, -0.025, z_flick)
    k3_hover2 = (0.328, -0.025, z_hover)

    # Knob 2 (y = +0.025, push along -X: contact at x=0.355, push to x=0.330)
    k2_hover1 = (0.355, 0.025, z_hover)
    k2_contact = (0.355, 0.025, z_flick)
    k2_pushed = (0.328, 0.025, z_flick)
    k2_hover2 = (0.328, 0.025, z_hover)

    # Knob 1 (y = +0.075, flick along +X: contact at x=0.320, push to x=0.348)
    k1_hover1 = (0.320, 0.075, z_hover)
    k1_contact = (0.320, 0.075, z_flick)
    k1_pushed = (0.348, 0.075, z_flick)
    k1_hover2 = (0.348, 0.075, z_hover)

    # Button at (0.253, 0.0), height +0.034, pressed to +0.024
    btn_hover = (0.253, 0.0, TABLE_TOP + 0.080)
    btn_contact = (0.253, 0.0, TABLE_TOP + 0.034)
    btn_pressed = (0.253, 0.0, TABLE_TOP + 0.024)

    if ablation:
        left = [Waypoint(_s(40.0), l_ready, FINGER_OPEN, "ablation: idle left")]
        right = [
            Waypoint(_s(1.5), k4_hover1, FINGER_CLOSED, "right hover k4"),
            Waypoint(_s(1.2), k4_contact, FINGER_CLOSED, "right descend k4"),
            Waypoint(_s(1.5), k4_pushed, FINGER_CLOSED, "right push k4"),
            Waypoint(_s(1.0), k4_hover2, FINGER_CLOSED, "right lift k4"),
            Waypoint(_s(1.5), btn_hover, FINGER_CLOSED, "right hover btn"),
            Waypoint(_s(1.5), btn_contact, FINGER_CLOSED, "right descend btn"),
            Waypoint(_s(1.5), btn_pressed, FINGER_CLOSED, "right press btn"),
            Waypoint(_s(2.0), btn_pressed, FINGER_CLOSED, "right hold btn"),
            Waypoint(_s(2.0), r_ready, FINGER_CLOSED, "right retreat"),
        ]
        return {"left": left, "right": right}

    # Bimanual plan with strict y-separation:
    # Phase 1: Left arm holds at y = +0.125 (total duration ~11 s)
    #          Right arm sets Knob 4 then Knob 3
    left_phase1 = [
        Waypoint(_s(1.5), l_brace_hover, FINGER_CLOSED, "left approach brace"),
        Waypoint(_s(1.2), l_brace, FINGER_CLOSED, "left brace module"),
        Waypoint(_s(8.5), l_brace, FINGER_CLOSED, "left hold brace p1"),
    ]
    right_phase1 = [
        Waypoint(_s(1.5), k4_hover1, FINGER_CLOSED, "right hover k4"),
        Waypoint(_s(1.2), k4_contact, FINGER_CLOSED, "right contact k4"),
        Waypoint(_s(1.5), k4_pushed, FINGER_CLOSED, "right flick k4"),
        Waypoint(_s(1.0), k4_hover2, FINGER_CLOSED, "right lift k4"),
        Waypoint(_s(1.2), k3_hover1, FINGER_CLOSED, "right hover k3"),
        Waypoint(_s(1.2), k3_contact, FINGER_CLOSED, "right contact k3"),
        Waypoint(_s(1.5), k3_pushed, FINGER_CLOSED, "right push k3"),
        Waypoint(_s(1.0), k3_hover2, FINGER_CLOSED, "right lift k3"),
        Waypoint(_s(1.1), r_brace_hover, FINGER_CLOSED, "right to brace hover"),
    ]

    # Handover: Right arm transitions to hold at y = -0.125
    # Left arm lifts from brace to k2
    left_handover = [
        Waypoint(_s(1.2), l_brace, FINGER_CLOSED, "left keep hold while right lands"),
        Waypoint(_s(1.2), l_brace_hover, FINGER_CLOSED, "left lift brace"),
    ]
    right_handover = [
        Waypoint(_s(1.2), r_brace, FINGER_CLOSED, "right brace module"),
        Waypoint(_s(1.2), r_brace, FINGER_CLOSED, "right hold brace"),
    ]

    # Phase 2: Right arm holds at y = -0.125 (~10 s)
    #          Left arm sets Knob 2 then Knob 1
    left_phase2 = [
        Waypoint(_s(1.2), k2_hover1, FINGER_CLOSED, "left hover k2"),
        Waypoint(_s(1.2), k2_contact, FINGER_CLOSED, "left contact k2"),
        Waypoint(_s(1.5), k2_pushed, FINGER_CLOSED, "left push k2"),
        Waypoint(_s(1.0), k2_hover2, FINGER_CLOSED, "left lift k2"),
        Waypoint(_s(1.2), k1_hover1, FINGER_CLOSED, "left hover k1"),
        Waypoint(_s(1.2), k1_contact, FINGER_CLOSED, "left contact k1"),
        Waypoint(_s(1.5), k1_pushed, FINGER_CLOSED, "left flick k1"),
        Waypoint(_s(1.0), k1_hover2, FINGER_CLOSED, "left lift k1"),
        Waypoint(_s(1.2), l_brace_hover, FINGER_CLOSED, "left to brace hover"),
        Waypoint(_s(1.0), l_brace, FINGER_CLOSED, "left re-brace module"),
    ]
    right_phase2 = [
        Waypoint(_s(12.0), r_brace, FINGER_CLOSED, "right hold brace p2"),
    ]

    # Phase 3: Left arm holds at y = +0.125
    # Right arm lifts from brace and presses commit button at (0.253, 0.0)
    left_phase3 = [
        Waypoint(_s(8.0), l_brace, FINGER_CLOSED, "left hold brace p3"),
        Waypoint(_s(2.0), l_ready, FINGER_OPEN, "left retreat to ready"),
    ]
    right_phase3 = [
        Waypoint(_s(1.2), r_brace_hover, FINGER_CLOSED, "right lift brace"),
        Waypoint(_s(1.5), btn_hover, FINGER_CLOSED, "right hover btn"),
        Waypoint(_s(1.2), btn_contact, FINGER_CLOSED, "right contact btn"),
        Waypoint(_s(1.5), btn_pressed, FINGER_CLOSED, "right press btn"),
        Waypoint(_s(2.0), btn_pressed, FINGER_CLOSED, "right hold btn 1s"),
        Waypoint(_s(2.6), r_ready, FINGER_OPEN, "right retreat to ready"),
    ]

    left = left_phase1 + left_handover + left_phase2 + left_phase3
    right = right_phase1 + right_handover + right_phase2 + right_phase3

    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by the yam_arena demo runner: the mode comes from the environment."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
