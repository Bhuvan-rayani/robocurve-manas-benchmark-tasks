from __future__ import annotations

"""Scoring wrappers and TASK_TRACE logging for outlet_cover_fit."""


import json
import os
from typing import Any, Mapping

from geometry import CAP_NAMES, PLATE_NAME
from logic import evaluate_state


def _extract_state(objects: Mapping[str, Any]):
    plate = objects.get(PLATE_NAME)
    if plate is None:
        raise KeyError(f"{PLATE_NAME} missing from objects dict")

    plate_pos = tuple(float(v) for v in plate.pos)

    caps = {}
    for name in CAP_NAMES:
        c = objects.get(name)
        if c is not None:
            caps[name] = tuple(float(v) for v in c.pos)

    # Check resting property if present
    resting = getattr(plate, "resting", lambda: True)()
    for name in CAP_NAMES:
        c = objects.get(name)
        if c is not None:
            resting = resting and getattr(c, "resting", lambda: True)()

    return plate_pos, caps, resting


_TRACE_STEP = [0]


def _trace(plate_pos, caps, resting, s, reason) -> None:
    """Optional trace log: set TASK_TRACE=<file> to log JSON records per scorer call."""
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    record = {
        "n": _TRACE_STEP[0],
        "plate_pos": [round(v, 5) for v in plate_pos],
        "caps": {k: [round(v, 5) for v in pos] for k, pos in caps.items()},
        "resting": bool(resting),
        "score": s,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    plate_pos, caps, resting = _extract_state(objects)
    _, ok, _ = evaluate_state(plate_pos, caps, resting=resting)
    return ok


def score(objects: Mapping[str, Any]) -> float:
    """Return partial credit in 0..1."""
    plate_pos, caps, resting = _extract_state(objects)
    s, _, reason = evaluate_state(plate_pos, caps, resting=resting)
    _trace(plate_pos, caps, resting, s, reason)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to completion."""
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.05
