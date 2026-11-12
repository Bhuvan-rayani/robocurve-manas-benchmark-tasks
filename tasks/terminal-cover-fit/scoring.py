from __future__ import annotations

"""Scoring wrappers and TASK_TRACE logging for terminal_cover_fit (T16)."""

import json
import os
from typing import Any, Mapping

from geometry import BLOCK_NAME, COVER_NAME
from logic import evaluate_state

_TRACE_STEP = [0]


def _trace(b_pos, c_pos, s, ok, reason) -> None:
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    rec = {
        "step": _TRACE_STEP[0],
        "block_pos": [round(v, 4) for v in b_pos],
        "cover_pos": [round(v, 4) for v in c_pos],
        "score": s,
        "success": ok,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def score(objects: Mapping[str, Any]) -> float:
    block = objects[BLOCK_NAME]
    cover = objects[COVER_NAME]
    b_pos = tuple(float(v) for v in block.pos)
    c_pos = tuple(float(v) for v in cover.pos)
    b_rest = getattr(block, "resting", lambda: True)()
    c_rest = getattr(cover, "resting", lambda: True)()
    s, ok, reason = evaluate_state(b_pos, c_pos, resting=b_rest and c_rest)
    _trace(b_pos, c_pos, s, ok, reason)
    return s


def success(objects: Mapping[str, Any]) -> bool:
    block = objects[BLOCK_NAME]
    cover = objects[COVER_NAME]
    b_pos = tuple(float(v) for v in block.pos)
    c_pos = tuple(float(v) for v in cover.pos)
    b_rest = getattr(block, "resting", lambda: True)()
    c_rest = getattr(cover, "resting", lambda: True)()
    _, ok, _ = evaluate_state(b_pos, c_pos, resting=b_rest and c_rest)
    return ok

def distance(objects) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.05
