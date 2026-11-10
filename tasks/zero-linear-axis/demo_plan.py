"""Scripted bimanual demo plans for zero_linear_axis (v2).

Right arm (y < 0 side): pushes the carriage 40 mm along +y.
Left arm (y > 0 side): braces the slippery base while the carriage is pushed, then carries the yellow pin to the lug hole and drops it in.
Every tunable is an environment variable (DEMO_*), so a scan needs no code change. Modes: demo (default), settle, ablation (no brace).
"""

from __future__ import annotations

import os

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, TABLE_HEIGHT
from yam_arena.demo import Waypoint

from geometry import HOLE_WORLD_X, HOLE_REST_WORLD_Y, CARRIAGE_TARGET_DISP_M, PIN_START_XY

TABLE_TOP = TABLE_HEIGHT


def _f(name: str, default: float) -> float:
    return float(os.getenv(name, default))


SCALE = _f("DEMO_TIME_SCALE", 1.8)

# Right arm: push the carriage. Measured on the GPU (trace, run 2): the finger face touches the carriage's -y face (y = -0.130)
# when the tool point is at y = -0.136, i.e. the contact face is only ~6 mm ahead of it. Approach at -0.140, push by 44 mm.
R_CONTACT_Y = _f("DEMO_R_CONTACT_Y", -0.140)
R_X = _f("DEMO_R_X", 0.26)
R_Z = _f("DEMO_R_Z", 0.060)               # TCP height above the table top while pushing (pad bottom 13 mm lower)
PUSH_M = _f("DEMO_PUSH_M", CARRIAGE_TARGET_DISP_M + 0.004)

# Left arm: brace the base by pressing down on its top, and carry the pin.
L_BRACE_X, L_BRACE_Y = _f("DEMO_L_BRACE_X", 0.26), _f("DEMO_L_BRACE_Y", 0.13)
L_BRACE_Z = _f("DEMO_L_BRACE_Z", 0.048)
PIN_GRASP_Z = _f("DEMO_PIN_GRASP_Z", 0.040)
# GPU run 5: at a TCP height of 0.078 the pad bottoms (TCP - 0.013) sat ON the lug top (0.065) and dragged the carriage back.
DROP_Z = _f("DEMO_DROP_Z", 0.098)         # TCP height at release: pads 20 mm above the lug top; the pin bottom is 18 mm inside the hole
PRE_Z = _f("DEMO_PRE_Z", 0.125)           # pin bottom ~20 mm above the lug top while the hand settles
HOLE_Y = HOLE_REST_WORLD_Y + CARRIAGE_TARGET_DISP_M
# Measured (GPU run 3): the hand arrives ~4 mm short of a commanded y over the hole, so aim 4 mm further -y.
PIN_Y_OFFSET = _f("DEMO_PIN_Y_OFFSET", -0.002)
PIN_X_OFFSET = _f("DEMO_PIN_X_OFFSET", 0.0)
HOVER = _f("DEMO_HOVER", 0.16)


def _s(duration: float) -> float:
    """Scale a segment duration."""
    return max(0.1, duration * SCALE)


def make_settle_plan() -> dict[str, list[Waypoint]]:
    """Explicit hold at the ready pose (never an empty plan: that would fall back to the driver's built-in demo)."""
    return {
        "left": [Waypoint(_s(8.0), (0.20, 0.20, TABLE_TOP + HOVER), FINGER_OPEN, "settle hold left")],
        "right": [Waypoint(_s(8.0), (0.20, -0.20, TABLE_TOP + HOVER), FINGER_OPEN, "settle hold right")],
    }


def make_demo_plan(ablation: bool = False) -> dict[str, list[Waypoint]]:
    l_ready = (0.20, 0.20, TABLE_TOP + HOVER)
    r_ready = (0.20, -0.20, TABLE_TOP + HOVER)

    r_hover = (R_X, R_CONTACT_Y, TABLE_TOP + HOVER)
    r_contact = (R_X, R_CONTACT_Y, TABLE_TOP + R_Z)
    r_pushed = (R_X, R_CONTACT_Y + PUSH_M, TABLE_TOP + R_Z)
    r_pushed_hover = (R_X, R_CONTACT_Y + PUSH_M, TABLE_TOP + HOVER)

    l_brace_hover = (L_BRACE_X, L_BRACE_Y, TABLE_TOP + HOVER)
    l_brace = (L_BRACE_X, L_BRACE_Y, TABLE_TOP + L_BRACE_Z)

    pin_hover = (PIN_START_XY[0], PIN_START_XY[1], TABLE_TOP + HOVER)
    pin_grasp = (PIN_START_XY[0], PIN_START_XY[1], TABLE_TOP + PIN_GRASP_Z)
    hole_hover = (HOLE_WORLD_X + PIN_X_OFFSET, HOLE_Y + PIN_Y_OFFSET, TABLE_TOP + HOVER)
    hole_pre = (HOLE_WORLD_X + PIN_X_OFFSET, HOLE_Y + PIN_Y_OFFSET, TABLE_TOP + PRE_Z)
    hole_drop = (HOLE_WORLD_X + PIN_X_OFFSET, HOLE_Y + PIN_Y_OFFSET, TABLE_TOP + DROP_Z)

    right = [
        Waypoint(_s(1.5), r_hover, FINGER_CLOSED, "right hover carriage"),
        Waypoint(_s(1.5), r_contact, FINGER_CLOSED, "right contact carriage"),
        Waypoint(_s(2.5), r_pushed, FINGER_CLOSED, "right push carriage"),
        Waypoint(_s(1.0), r_pushed, FINGER_CLOSED, "right dwell at datum"),
        Waypoint(_s(1.0), r_pushed_hover, FINGER_CLOSED, "right lift clear"),
        Waypoint(_s(2.0), r_ready, FINGER_OPEN, "right retreat to ready"),
        Waypoint(_s(14.0), r_ready, FINGER_OPEN, "right hold ready"),
    ]

    if ablation:
        left = [Waypoint(_s(sum(w.duration for w in right) / SCALE), l_ready, FINGER_OPEN, "ablation: left idle (base not held)")]
        return {"left": left, "right": right}

    left = [
        Waypoint(_s(1.5), l_brace_hover, FINGER_CLOSED, "left hover base"),
        Waypoint(_s(1.5), l_brace, FINGER_CLOSED, "left press base"),
        Waypoint(_s(6.0), l_brace, FINGER_CLOSED, "left hold base while the carriage is pushed"),
        Waypoint(_s(1.0), l_brace_hover, FINGER_CLOSED, "left lift"),
        Waypoint(_s(1.5), pin_hover, FINGER_OPEN, "left hover pin"),
        Waypoint(_s(1.2), pin_grasp, FINGER_OPEN, "left descend to pin"),
        Waypoint(_s(0.8), pin_grasp, FINGER_CLOSED, "left grasp pin"),
        Waypoint(_s(1.2), pin_hover, FINGER_CLOSED, "left lift pin"),
        Waypoint(_s(2.0), hole_hover, FINGER_CLOSED, "left carry pin over the hole"),
        Waypoint(_s(1.2), hole_pre, FINGER_CLOSED, "left lower the pin to just above the lug"),
        Waypoint(_s(1.5), hole_pre, FINGER_CLOSED, "left settle over the hole (hand lag)"),
        Waypoint(_s(2.0), hole_drop, FINGER_CLOSED, "left lower pin slowly into the hole"),
        Waypoint(_s(0.8), hole_drop, FINGER_OPEN, "left release pin"),
        Waypoint(_s(1.2), hole_hover, FINGER_OPEN, "left lift clear"),
        Waypoint(_s(2.0), l_ready, FINGER_OPEN, "left retreat to ready"),
        Waypoint(_s(3.0), l_ready, FINGER_OPEN, "left hold ready"),
    ]
    return {"left": left, "right": right}


def plans() -> dict[str, list[Waypoint]]:
    """Entry point called by the yam_arena demo runner: the mode comes from the environment."""
    if os.getenv("SETTLE_ONLY") == "1":
        return make_settle_plan()
    if os.getenv("ABLATION") == "1":
        return make_demo_plan(ablation=True)
    return make_demo_plan(ablation=False)
