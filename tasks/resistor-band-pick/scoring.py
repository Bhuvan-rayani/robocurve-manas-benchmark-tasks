from __future__ import annotations

import json
import os
"""Scoring wrappers for yam_arena task file interface."""


from typing import Any, Mapping

from geometry import COVER_NAME, RES_NAMES, TARGET_RES_NAME
from logic import evaluate_state


def _extract_state(objects: Mapping[str, Any]):
    board = objects.get("socket_board")
    if board is None:
        raise KeyError("socket_board missing from objects dict")

    board_pos = tuple(float(v) for v in board.pos)
    sliders = getattr(board, "sliders", {})
    cover_disp = float(sliders.get(COVER_NAME, 0.0))

    resistor_positions = {}
    for name in RES_NAMES:
        r = objects.get(name)
        if r is not None:
            resistor_positions[name] = tuple(float(v) for v in r.pos)

    target_res = objects.get(TARGET_RES_NAME)
    resting = True
    if target_res is not None and hasattr(target_res, "resting"):
        resting = bool(target_res.resting())

    return board_pos, resistor_positions, cover_disp, resting


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    board_pos, res_positions, cover_disp, resting = _extract_state(objects)
    _, ok, _ = evaluate_state(board_pos, res_positions, cover_disp=cover_disp, resting=resting)
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
    board_pos, res_positions, cover_disp, resting = _extract_state(objects)
    s, _, _ = evaluate_state(board_pos, res_positions, cover_disp=cover_disp, resting=resting)
    _trace(s=s, res_c=[round(v, 4) for v in res_positions.get(TARGET_RES_NAME, (0, 0, 0))], cover=round(cover_disp, 4))
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to completion."""
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.05
