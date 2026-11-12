from __future__ import annotations

import json
import os
from typing import Any, Mapping

from geometry import FRAME_POS_WORLD
from logic import evaluate_state


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


def success(objects: Mapping[str, Any]) -> bool:
    """Return True if success condition holds."""
    return score(objects) >= 1.0


def score(objects: Mapping[str, Any]) -> float:
    """Return partial credit in 0..1."""
    tray_state = objects.get("feed_tray")
    paper_state = objects.get("paper_stack")
    if tray_state is None or paper_state is None:
        return 0.0

    frame_state = objects.get("printer_frame")
    if frame_state is not None:
        frame_pos = tuple(float(v) for v in frame_state.pos)
    else:
        frame_pos = FRAME_POS_WORLD

    tray_pos = tuple(float(v) for v in tray_state.pos)
    paper_pos = tuple(float(v) for v in paper_state.pos)
    paper_quat = getattr(paper_state, "quat_xyzw", (0.0, 0.0, 0.0, 1.0))
    sliders = getattr(tray_state, "sliders", {})

    tray_resting = getattr(tray_state, "resting", lambda: True)()
    paper_resting = getattr(paper_state, "resting", lambda: True)()
    resting = bool(tray_resting and paper_resting)

    s, _, _ = evaluate_state(
        frame_pos,
        tray_pos,
        paper_pos,
        sliders,
        paper_quat=paper_quat,
        resting=resting,
    )
    _trace(s=s)
    return s


def distance(objects: Mapping[str, Any]) -> float:
    """Estimated distance in metres to completion."""
    s = score(objects)
    return max(0.0, 1.0 - s) * 0.10
