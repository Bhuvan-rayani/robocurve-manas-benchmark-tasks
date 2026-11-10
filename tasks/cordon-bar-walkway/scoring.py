from __future__ import annotations

"""Scoring wrappers and TASK_TRACE logging for cordon_bar_walkway (T26)."""

import json
import os
from typing import Any, Mapping

from geometry import BAR_NAME, POST_A_NAME, POST_B_NAME
from logic import evaluate_state

_TRACE_STEP = [0]


def _trace(post_a_pos, post_b_pos, bar_pos, s, ok, reason) -> None:
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    rec = {
        "step": _TRACE_STEP[0],
        "post_a_pos": [round(v, 4) for v in post_a_pos],
        "post_b_pos": [round(v, 4) for v in post_b_pos],
        "bar_pos": [round(v, 4) for v in bar_pos],
        "score": s,
        "success": ok,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + chr(10))


def _extract(objects: Mapping[str, Any]):
    p_a = objects[POST_A_NAME]
    p_b = objects[POST_B_NAME]
    bar = objects[BAR_NAME]

    p_a_pos = tuple(float(v) for v in p_a.pos)
    p_b_pos = tuple(float(v) for v in p_b.pos)
    bar_pos = tuple(float(v) for v in bar.pos)

    resting = (
        getattr(p_a, "resting", lambda: True)()
        and getattr(p_b, "resting", lambda: True)()
        and getattr(bar, "resting", lambda: True)()
    )
    return p_a_pos, p_b_pos, bar_pos, resting


def score(objects: Mapping[str, Any]) -> float:
    p_a_pos, p_b_pos, bar_pos, resting = _extract(objects)
    s, ok, reason = evaluate_state(p_a_pos, p_b_pos, bar_pos, resting=resting)
    _trace(p_a_pos, p_b_pos, bar_pos, s, ok, reason)
    return s


def success(objects: Mapping[str, Any]) -> bool:
    p_a_pos, p_b_pos, bar_pos, resting = _extract(objects)
    _, ok, _ = evaluate_state(p_a_pos, p_b_pos, bar_pos, resting=resting)
    return ok

def distance(objects) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.05
