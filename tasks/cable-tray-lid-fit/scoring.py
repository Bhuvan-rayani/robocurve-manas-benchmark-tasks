from __future__ import annotations

"""Scoring wrappers and TASK_TRACE logging for cable_tray_lid_fit (T13)."""

import json
import os
from typing import Any, Mapping

from geometry import LID_LEFT_NAME, LID_RIGHT_NAME, TRAY_NAME
from logic import evaluate_state

_TRACE_STEP = [0]


def _trace(t_pos, l_poses, s, ok, reason) -> None:
    path = os.environ.get("TASK_TRACE")
    if not path:
        return
    _TRACE_STEP[0] += 1
    rec = {
        "step": _TRACE_STEP[0],
        "tray_pos": [round(v, 4) for v in t_pos],
        "lid_poses": {k: [round(v, 4) for v in p] for k, p in l_poses.items()},
        "score": s,
        "success": ok,
        "reason": reason,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def score(objects: Mapping[str, Any]) -> float:
    tray = objects[TRAY_NAME]
    lids = {LID_LEFT_NAME: objects[LID_LEFT_NAME].pos, LID_RIGHT_NAME: objects[LID_RIGHT_NAME].pos}
    t_pos = tuple(float(v) for v in tray.pos)
    t_rest = getattr(tray, "resting", lambda: True)()
    l_rest = getattr(objects[LID_LEFT_NAME], "resting", lambda: True)() and getattr(objects[LID_RIGHT_NAME], "resting", lambda: True)()
    s, ok, reason = evaluate_state(t_pos, lids, resting=t_rest and l_rest)
    _trace(t_pos, lids, s, ok, reason)
    return s


def success(objects: Mapping[str, Any]) -> bool:
    tray = objects[TRAY_NAME]
    lids = {LID_LEFT_NAME: objects[LID_LEFT_NAME].pos, LID_RIGHT_NAME: objects[LID_RIGHT_NAME].pos}
    t_pos = tuple(float(v) for v in tray.pos)
    t_rest = getattr(tray, "resting", lambda: True)()
    l_rest = getattr(objects[LID_LEFT_NAME], "resting", lambda: True)() and getattr(objects[LID_RIGHT_NAME], "resting", lambda: True)()
    _, ok, _ = evaluate_state(t_pos, lids, resting=t_rest and l_rest)
    return ok

def distance(objects) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.05
