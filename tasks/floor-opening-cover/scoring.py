from __future__ import annotations

import json
import os
"""Scoring wrappers for yam_arena task file interface in floor_opening_cover."""


from typing import Any, Mapping

from geometry import (
    BOARD_POS_WORLD,
    PIN_A_START_POS,
    PIN_B_START_POS,
    PLATE_START_POS,
)
from logic import evaluate_state


def success(objects: Mapping[str, Any]) -> bool:
    s = score(objects)
    _trace(s=s)
    return s >= 1.0



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
    board_obj = objects.get("floor_board")
    plate_obj = objects.get("cover_plate")
    pin_a_obj = objects.get("wedge_pin_a")
    pin_b_obj = objects.get("wedge_pin_b")

    board_pos = tuple(float(v) for v in board_obj.pos) if board_obj is not None else BOARD_POS_WORLD
    plate_pos = tuple(float(v) for v in plate_obj.pos) if plate_obj is not None else PLATE_START_POS
    pin_a_pos = tuple(float(v) for v in pin_a_obj.pos) if pin_a_obj is not None else PIN_A_START_POS
    pin_b_pos = tuple(float(v) for v in pin_b_obj.pos) if pin_b_obj is not None else PIN_B_START_POS

    plate_quat = getattr(plate_obj, "quat_xyzw", None)
    pin_a_quat = getattr(pin_a_obj, "quat_xyzw", None)
    pin_b_quat = getattr(pin_b_obj, "quat_xyzw", None)

    resting = True
    if plate_obj is not None and hasattr(plate_obj, "resting"):
        resting = resting and plate_obj.resting()
    if pin_a_obj is not None and hasattr(pin_a_obj, "resting"):
        resting = resting and pin_a_obj.resting()
    if pin_b_obj is not None and hasattr(pin_b_obj, "resting"):
        resting = resting and pin_b_obj.resting()

    s, _, _ = evaluate_state(
        board_pos,
        plate_pos,
        pin_a_pos,
        pin_b_pos,
        plate_quat=plate_quat,
        pin_a_quat=pin_a_quat,
        pin_b_quat=pin_b_quat,
        resting=resting,
    )
    _trace(s=s)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.10
