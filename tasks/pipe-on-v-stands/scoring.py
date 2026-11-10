from __future__ import annotations

"""Scoring wrappers and TASK_TRACE logging for pipe_on_v_stands (T17)."""


import json
import os
from typing import Any, Mapping

from geometry import (
    PIPE_NAME,
    STAND_A_NAME,
    STAND_A_POS_WORLD,
    STAND_B_NAME,
    STAND_B_POS_WORLD,
)
from logic import evaluate_state


def _extract_state(objects: Mapping[str, Any]):
    """Extract object positions, orientations, and resting flags."""
    pipe_obj = objects.get(PIPE_NAME)
    if pipe_obj is None:
        raise KeyError(f"{PIPE_NAME} missing from objects dict")

    pipe_pos = tuple(float(v) for v in pipe_obj.pos)
    pipe_quat = tuple(float(v) for v in getattr(pipe_obj, "quat_xyzw", (0.0, 0.0, 0.0, 1.0)))
    resting = getattr(pipe_obj, "resting", lambda: True)()

    stand_a_obj = objects.get(STAND_A_NAME)
    if stand_a_obj is not None:
        stand_a_pos = tuple(float(v) for v in stand_a_obj.pos)
    else:
        stand_a_pos = STAND_A_POS_WORLD

    stand_b_obj = objects.get(STAND_B_NAME)
    if stand_b_obj is not None:
        stand_b_pos = tuple(float(v) for v in stand_b_obj.pos)
    else:
        stand_b_pos = STAND_B_POS_WORLD

    return pipe_pos, pipe_quat, stand_a_pos, stand_b_pos, resting


_TRACE_STEP = [0]


def _trace(pipe_pos, pipe_quat, score_val, ok, reason) -> None:
    """Optional trace log: set TASK_TRACE=<path> to record JSON lines."""
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    record = {
        "step": _TRACE_STEP[0],
        "pipe_pos": [round(v, 4) for v in pipe_pos],
        "pipe_quat": [round(v, 4) for v in pipe_quat],
        "score": round(score_val, 3),
        "success": bool(ok),
        "reason": str(reason),
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    pipe_pos, pipe_quat, stand_a_pos, stand_b_pos, resting = _extract_state(objects)
    _, ok, _ = evaluate_state(pipe_pos, pipe_quat, stand_a_pos, stand_b_pos, resting=resting)
    return ok


def score(objects: Mapping[str, Any]) -> float:
    """Return partial credit in 0..1."""
    pipe_pos, pipe_quat, stand_a_pos, stand_b_pos, resting = _extract_state(objects)
    s, ok, reason = evaluate_state(pipe_pos, pipe_quat, stand_a_pos, stand_b_pos, resting=resting)
    _trace(pipe_pos, pipe_quat, s, ok, reason)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to goal."""
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.10
