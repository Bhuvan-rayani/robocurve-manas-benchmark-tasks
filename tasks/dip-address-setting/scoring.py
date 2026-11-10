from __future__ import annotations

"""Scoring wrappers for yam_arena task file interface."""


import json
import os
from typing import Any, Mapping

from logic import evaluate_state


def _get_module_state(objects: Mapping[str, Any]):
    state = objects.get("addr_module")
    if state is None:
        raise KeyError("addr_module missing from objects dict")
    return state


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    state = _get_module_state(objects)
    pos = tuple(float(v) for v in state.pos)
    sliders = getattr(state, "sliders", {})
    resting = getattr(state, "resting", lambda: True)()
    _, ok, _ = evaluate_state(pos, sliders, resting=resting)
    return ok


_TRACE_STEP = [0]


def _trace(pos, sliders, resting, s, reason) -> None:
    """Optional debugging trace: set TASK_TRACE=<file> to log one JSON line per scorer call."""
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    record = {
        "n": _TRACE_STEP[0],
        "pos": [round(v, 5) for v in pos],
        "sliders": {k: round(float(v), 5) for k, v in dict(sliders).items()},
        "resting": bool(resting),
        "score": s,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def score(objects: Mapping[str, Any]) -> float:
    """Return partial credit in 0..1."""
    state = _get_module_state(objects)
    pos = tuple(float(v) for v in state.pos)
    sliders = getattr(state, "sliders", {})
    resting = getattr(state, "resting", lambda: True)()
    s, _, reason = evaluate_state(pos, sliders, resting=resting)
    _trace(pos, sliders, resting, s, reason)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to completion."""
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.05
