from __future__ import annotations

"""Scoring wrappers for yam_arena task file interface."""


import json
import os
from typing import Any, Mapping

from geometry import (
    DRAWER_NAME,
    TILL_POS_WORLD,
    TOKEN_A_NAMES,
    TOKEN_B_NAMES,
)
from logic import evaluate_state


_TRACE_STEP = [0]


def _trace(till_pos, drawer_slider, token_positions, resting, s, reason) -> None:
    """Optional debugging trace: set TASK_TRACE=<file> to log one JSON line per scorer call."""
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    record = {
        "n": _TRACE_STEP[0],
        "till_pos": [round(v, 5) for v in till_pos],
        "drawer_slider": round(float(drawer_slider), 5),
        "resting": bool(resting),
        "score": s,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def success(objects: Mapping[str, Any]) -> bool:
    s = score(objects)
    return s >= 1.0


def score(objects: Mapping[str, Any]) -> float:
    till_state = objects.get("till_body")
    if till_state is None:
        return 0.0

    till_pos = tuple(float(v) for v in till_state.pos)
    sliders = getattr(till_state, "sliders", {})
    drawer_slider = float(sliders.get(DRAWER_NAME, 0.0))

    # Also check if drawer is a separate object
    if DRAWER_NAME in objects and DRAWER_NAME not in sliders:
        drawer_obj = objects[DRAWER_NAME]
        drawer_slider = float(drawer_obj.pos[0] - (TILL_POS_WORLD[0] - 0.010))

    token_positions = {}
    for name in TOKEN_A_NAMES + TOKEN_B_NAMES:
        if name in objects:
            token_positions[name] = tuple(float(v) for v in objects[name].pos)

    resting = getattr(till_state, "resting", lambda: True)()
    s, _, reason = evaluate_state(till_pos, drawer_slider, token_positions, resting=resting)
    _trace(till_pos, drawer_slider, token_positions, resting, s, reason)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.10
