"""Scoring wrappers for the yam_arena task-file interface (zero_linear_axis v2)."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

from geometry import BASE_NAME, CARRIAGE_NAME, PIN_NAME
from logic import evaluate_state

_TRACE_STEP = [0]


def _evaluate(objects: Mapping[str, Any]):
    base = objects[BASE_NAME]
    pin = objects[PIN_NAME]
    carriage = float(getattr(base, "sliders", {}).get(CARRIAGE_NAME, 0.0))
    resting = base.resting() and pin.resting()
    result = evaluate_state(tuple(float(v) for v in base.pos), tuple(float(v) for v in base.quat_xyzw), carriage,
                            tuple(float(v) for v in pin.pos), tuple(float(v) for v in pin.quat_xyzw), resting=resting)
    return result, carriage, base, pin, resting


def _trace(result, carriage, base, pin, resting) -> None:
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    record = {
        "n": _TRACE_STEP[0],
        "score": result[0],
        "reason": result[2],
        "carriage_mm": round(carriage * 1000, 2),
        "base": [round(float(v), 4) for v in base.pos],
        "pin": [round(float(v), 4) for v in pin.pos],
        "resting": bool(resting),
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def success(objects: Mapping[str, Any]) -> bool:
    return bool(_evaluate(objects)[0][1])


def score(objects: Mapping[str, Any]) -> float:
    result, carriage, base, pin, resting = _evaluate(objects)
    _trace(result, carriage, base, pin, resting)
    return float(result[0])


def distance(objects: Mapping[str, Any]) -> float:
    """Rough distance to completion (m), for diagnostics only."""
    return max(0.0, 1.0 - score(objects)) * 0.05
