"""Scoring wrappers and TASK_TRACE telemetry for stair_nosing_strip_fit."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

from logic import evaluate_state


_TRACE_STEP = [0]


def _trace(step_pos, pad_pos, strip_pos, quat, s, reason) -> None:
    """Optional trace logging: append one JSON line per call to TASK_TRACE."""
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    record = {
        "n": _TRACE_STEP[0],
        "step_pos": [round(v, 5) for v in step_pos],
        "pad_pos": [round(v, 5) for v in pad_pos],
        "strip_pos": [round(v, 5) for v in strip_pos],
        "quat_xyzw": [round(v, 5) for v in quat],
        "score": float(s),
        "reason": str(reason),
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _extract_state(objects: Mapping[str, Any]):
    stair_step = objects.get("stair_step")
    step_pos = tuple(float(v) for v in stair_step.pos) if stair_step is not None else (0.36, 0.0, 0.7475)

    strip_pad = objects.get("strip_pad")
    pad_pos = tuple(float(v) for v in strip_pad.pos) if strip_pad is not None else (0.18, 0.0, 0.7475)

    nosing_strip = objects.get("nosing_strip")
    strip_pos = tuple(float(v) for v in nosing_strip.pos) if nosing_strip is not None else (0.18, 0.0, 0.7575)
    quat = tuple(float(v) for v in getattr(nosing_strip, "quat_xyzw", (0.0, 0.0, 0.0, 1.0)))

    s_rest = getattr(stair_step, "resting", lambda: True)() if stair_step else True
    p_rest = getattr(strip_pad, "resting", lambda: True)() if strip_pad else True
    n_rest = getattr(nosing_strip, "resting", lambda: True)() if nosing_strip else True
    resting = s_rest and p_rest and n_rest

    return step_pos, pad_pos, strip_pos, quat, resting


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    step_pos, pad_pos, strip_pos, quat, resting = _extract_state(objects)
    _, ok, _ = evaluate_state(
        step_pos=step_pos,
        pad_pos=pad_pos,
        strip_pos=strip_pos,
        strip_quat_xyzw=quat,
        resting=resting,
    )
    return ok


def score(objects: Mapping[str, Any]) -> float:
    """Return partial credit in 0..1."""
    step_pos, pad_pos, strip_pos, quat, resting = _extract_state(objects)
    s, _, reason = evaluate_state(
        step_pos=step_pos,
        pad_pos=pad_pos,
        strip_pos=strip_pos,
        strip_quat_xyzw=quat,
        resting=resting,
    )
    _trace(step_pos, pad_pos, strip_pos, quat, s, reason)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to goal completion."""
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.15
