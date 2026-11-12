from __future__ import annotations

import json
import os
"""Scoring wrappers for yam_arena task file interface in window_restrictor_fit."""


from typing import Any, Mapping

from logic import evaluate_state


def _get_required_states(objects: Mapping[str, Any]):
    frame = objects.get("window_frame")
    if frame is None:
        raise KeyError("window_frame missing from objects dict")
    block = objects.get("stop_block")
    if block is None:
        raise KeyError("stop_block missing from objects dict")
    return frame, block


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    frame, block = _get_required_states(objects)
    frame_pos = tuple(float(v) for v in frame.pos)
    block_pos = tuple(float(v) for v in block.pos)
    sliders = getattr(frame, "sliders", {})
    sash_travel = float(sliders.get("sash_pane", 0.0))

    frame_rest = getattr(frame, "resting", lambda: True)()
    block_rest = getattr(block, "resting", lambda: True)()
    resting = frame_rest and block_rest

    _, ok, _ = evaluate_state(frame_pos, sash_travel, block_pos, resting=resting)
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
    frame, block = _get_required_states(objects)
    frame_pos = tuple(float(v) for v in frame.pos)
    block_pos = tuple(float(v) for v in block.pos)
    sliders = getattr(frame, "sliders", {})
    sash_travel = float(sliders.get("sash_pane", 0.0))

    frame_rest = getattr(frame, "resting", lambda: True)()
    block_rest = getattr(block, "resting", lambda: True)()
    resting = frame_rest and block_rest

    s, _, _ = evaluate_state(frame_pos, sash_travel, block_pos, resting=resting)
    _trace(s=s, block=block_pos, sash=sash_travel)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to goal completion."""
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.10
