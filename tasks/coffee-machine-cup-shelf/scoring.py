"""Scorer wrappers for coffee_machine_cup_shelf: they read the simulator, keep the ledger (logic.py) and drive the display markers."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

import numpy as np

import parts
from display import DISPLAY
from geometry import (
    BUTTON_NAME,
    FINGERS_OPEN_FRACTION,
    MACHINE_NAME,
    MUG_CRACKED_NAME,
    MUG_GOOD_NAME,
    SHELF_NAME,
    TCP_BELOW_LINK_M,
)
from logic import (
    advance,
    evaluate_state,
    fault_reasons,
    hands_clear,
    new_ledger,
    shelf_at_rest,
    shelf_out_m,
    still,
)

# Facts the end state cannot show; reset at every reset. A fault is permanent for the run.
_RUN = new_ledger()
_LAST = {"objects": None}          # offline replays: the objects mapping the ledger was last advanced with


def _hand_tcps(environment) -> dict[str, np.ndarray]:
    scene = environment.unwrapped.scene
    origin = parts._to_numpy(scene.env_origins[0])
    out = {}
    for arm in ("left", "right"):
        robot = scene[f"{arm}_robot"]
        names = list(robot.body_names)
        body_xyz = parts._to_numpy(robot.data.body_pos_w)[0]
        idx = names.index("gripper") if "gripper" in names else len(names) - 1
        out[arm] = np.asarray(body_xyz[idx] - origin, dtype=float) - np.array([0.0, 0.0, TCP_BELOW_LINK_M])
    return out


def _state(environment, name):
    return parts._read_part_state(environment, parts._PARTS[name])


def _advance_from(objects: Mapping[str, Any], tcps: list) -> None:
    machine = objects[MACHINE_NAME]
    mugs = {n: (objects[n].pos, objects[n].quat_xyzw) for n in (MUG_GOOD_NAME, MUG_CRACKED_NAME) if n in objects}
    shelf = float(machine.sliders.get(SHELF_NAME, 0.0))
    button = float(machine.sliders.get(BUTTON_NAME, 0.0))
    advance(_RUN, shelf, button, mugs, machine.pos, tcps)
    DISPLAY.update(parts.env(), _RUN, mugs, shelf_at_rest(shelf))


def _on_reset(environment) -> None:
    _RUN.clear()
    _RUN.update(new_ledger())
    _LAST["objects"] = None
    DISPLAY.reset(environment, _RUN)


def _on_step(environment) -> None:
    try:
        objects = {n: _state(environment, n) for n in (MACHINE_NAME, MUG_GOOD_NAME, MUG_CRACKED_NAME)}
        _advance_from(objects, list(_hand_tcps(environment).values()))
    except Exception:  # never break an episode for bookkeeping
        pass


parts.on_reset(_on_reset)
parts.on_step(_on_step)


def _released(machine, mug) -> bool:
    environment = parts.env()
    if environment is None:
        return False
    try:
        for arm in ("left", "right"):
            if not parts.gripper_open(environment, arm, FINGERS_OPEN_FRACTION):
                return False
        tcps = list(_hand_tcps(environment).values())
        return hands_clear(
            tcps,
            mug.pos,
            mug.quat_xyzw,
            machine.pos,
            shelf_out_m(machine.sliders.get(SHELF_NAME, 0.0)),
            max(0.0, float(machine.sliders.get(BUTTON_NAME, 0.0))),
        )
    except Exception:
        return False


def _trace(record: dict) -> None:
    path = os.environ.get("TASK_TRACE")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")


def score(objects: Mapping[str, Any]) -> float:
    machine = objects.get(MACHINE_NAME)
    mug = objects.get(MUG_GOOD_NAME)
    if machine is None or mug is None:
        return 0.0
    if parts.env() is None and _LAST["objects"] is not objects:
        # offline replay (no simulator env, so no gripper positions): advance the ledger once per objects mapping
        _LAST["objects"] = objects
        try:
            _advance_from(objects, [])
        except Exception:
            pass
    shelf = float(machine.sliders.get(SHELF_NAME, 0.0))
    s, ok, reason = evaluate_state(
        tuple(float(v) for v in mug.pos),
        tuple(float(v) for v in mug.quat_xyzw),
        float(_RUN["level"][MUG_GOOD_NAME]),
        len(_RUN["tiles"]),
        shelf,
        fault_reasons(_RUN),
        _released(machine, mug),
        still(_RUN),
    )
    _trace(
        {
            "score": s,
            "reason": reason,
            "mug": [round(float(v), 4) for v in mug.pos],
            "shelf_mm": round(shelf * 1000, 1),
            "level": round(float(_RUN["level"][MUG_GOOD_NAME]), 3),
            "tiles": len(_RUN["tiles"]),
            "brew_step": _RUN["brew_step"],
            "faults": fault_reasons(_RUN),
        }
    )
    return s


def success(objects: Mapping[str, Any]) -> bool:
    return score(objects) >= 1.0


def distance(objects: Mapping[str, Any]) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.10
