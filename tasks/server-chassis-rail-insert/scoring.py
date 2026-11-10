from __future__ import annotations

import json
import os
"""Scoring wrappers for yam_arena task file interface."""


from typing import Any, Mapping

from geometry import POST_A_POS_WORLD, POST_B_POS_WORLD
from logic import compute_ear_post_gap, evaluate_state


def _extract_state(objects: Mapping[str, Any]):
    chassis = objects.get("chassis_box")
    if chassis is None:
        raise KeyError("chassis_box missing from objects dict")

    post_a = objects.get("rack_post_a")
    post_b = objects.get("rack_post_b")

    post_a_pos = tuple(float(v) for v in post_a.pos) if post_a is not None else POST_A_POS_WORLD
    post_b_pos = tuple(float(v) for v in post_b.pos) if post_b is not None else POST_B_POS_WORLD
    chassis_pos = tuple(float(v) for v in chassis.pos)
    chassis_quat = getattr(chassis, "quat_xyzw", (0.0, 0.0, 0.0, 1.0))
    resting = getattr(chassis, "resting", lambda: True)()

    return post_a_pos, post_b_pos, chassis_pos, chassis_quat, resting


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    post_a_pos, post_b_pos, chassis_pos, chassis_quat, resting = _extract_state(objects)
    _, ok, _ = evaluate_state(post_a_pos, post_b_pos, chassis_pos, chassis_quat, resting=resting)
    return ok



_TRACE_STEP = [0]


def _trace(*args, **kwargs) -> None:
    """Optional debugging trace: set TASK_TRACE=<file> to log one JSON line per scorer call."""
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    record = {
        "n": _TRACE_STEP[0],
        "args": [str(a) for a in args],
        "kwargs": {k: str(v) for k, v in kwargs.items()},
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")

def score(objects: Mapping[str, Any]) -> float:
    """Return partial credit in 0..1."""
    post_a_pos, post_b_pos, chassis_pos, chassis_quat, resting = _extract_state(objects)
    s, _, _ = evaluate_state(post_a_pos, post_b_pos, chassis_pos, chassis_quat, resting=resting)
    _trace(s=s)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to goal completion."""
    chassis = objects.get("chassis_box")
    if chassis is None:
        return 0.25
    chassis_pos = tuple(float(v) for v in chassis.pos)
    return compute_ear_post_gap(chassis_pos)
