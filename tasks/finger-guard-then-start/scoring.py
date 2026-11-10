from __future__ import annotations

"""Scoring wrappers and TASK_TRACE logging for finger_guard_then_start (T20)."""

import json
import os
from typing import Any, Mapping

from geometry import MACHINE_NAME
from logic import evaluate_state

_TRACE_STEP = [0]


def _trace(m_pos, g_tr, b_pr, s, ok, reason) -> None:
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    rec = {
        "step": _TRACE_STEP[0],
        "machine_pos": [round(v, 4) for v in m_pos],
        "guard_travel_m": round(g_tr, 4),
        "button_press_m": round(b_pr, 4),
        "score": s,
        "success": ok,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + chr(10))


def _extract(objects: Mapping[str, Any]):
    machine = objects[MACHINE_NAME]
    m_pos = tuple(float(v) for v in machine.pos)
    sliders = getattr(machine, "sliders", {})
    g_tr = abs(float(sliders.get("guard", 0.0)))
    b_pr = abs(float(sliders.get("button", 0.0)))
    m_rest = getattr(machine, "resting", lambda: True)()
    return m_pos, g_tr, b_pr, m_rest


def score(objects: Mapping[str, Any]) -> float:
    m_pos, g_tr, b_pr, resting = _extract(objects)
    s, ok, reason = evaluate_state(m_pos, g_tr, b_pr, resting=resting)
    _trace(m_pos, g_tr, b_pr, s, ok, reason)
    return s


def success(objects: Mapping[str, Any]) -> bool:
    m_pos, g_tr, b_pr, resting = _extract(objects)
    _, ok, _ = evaluate_state(m_pos, g_tr, b_pr, resting=resting)
    return ok

def distance(objects) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.05
