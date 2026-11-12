from __future__ import annotations

"""Scoring wrappers and TASK_TRACE logging for wheel_axle_lynch_pin (T18)."""

import json
import os
from typing import Any, Mapping

from geometry import PIN_NAME, STAND_NAME, WHEEL_NAME
from logic import evaluate_state

_TRACE_STEP = [0]


def _trace(s_pos, w_pos, p_pos, s, ok, reason) -> None:
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    rec = {
        "step": _TRACE_STEP[0],
        "stand_pos": [round(v, 4) for v in s_pos],
        "wheel_pos": [round(v, 4) for v in w_pos],
        "pin_pos": [round(v, 4) for v in p_pos],
        "score": s,
        "success": ok,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + chr(10))


def score(objects: Mapping[str, Any]) -> float:
    stand = objects[STAND_NAME]
    wheel = objects[WHEEL_NAME]
    pin = objects[PIN_NAME]
    s_pos = tuple(float(v) for v in stand.pos)
    w_pos = tuple(float(v) for v in wheel.pos)
    p_pos = tuple(float(v) for v in pin.pos)
    resting = (
        getattr(stand, "resting", lambda: True)()
        and getattr(wheel, "resting", lambda: True)()
        and getattr(pin, "resting", lambda: True)()
    )
    s, ok, reason = evaluate_state(s_pos, w_pos, p_pos, resting=resting)
    _trace(s_pos, w_pos, p_pos, s, ok, reason)
    return s


def success(objects: Mapping[str, Any]) -> bool:
    stand = objects[STAND_NAME]
    wheel = objects[WHEEL_NAME]
    pin = objects[PIN_NAME]
    s_pos = tuple(float(v) for v in stand.pos)
    w_pos = tuple(float(v) for v in wheel.pos)
    p_pos = tuple(float(v) for v in pin.pos)
    resting = (
        getattr(stand, "resting", lambda: True)()
        and getattr(wheel, "resting", lambda: True)()
        and getattr(pin, "resting", lambda: True)()
    )
    _, ok, _ = evaluate_state(s_pos, w_pos, p_pos, resting=resting)
    return ok

def distance(objects) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.05
