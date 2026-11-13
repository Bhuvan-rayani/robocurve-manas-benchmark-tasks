"""Scorer wrappers for receipt_printer_roll_reload."""

from __future__ import annotations

import json
import math
import os
from typing import Any, Mapping

import numpy as np

import parts
from display import DISPLAY
from geometry import (
    BAY_OPEN_M,
    COVER_BOXES,
    FINGERS_OPEN_FRACTION,
    FIXTURE_MOVE_M,
    PRINTER_BOXES,
    PRINTER_NAME,
    PRINTER_XY,
    RELEASE_MIN_DIST_M,
    ROLL_CENTRE_Z,
    ROLL_CORE_WIDTH_M,
    ROLL_NAME,
    ROLL_RADIUS_M,
    ROLL_START_ORIGIN_Z,
    ROLL_TAIL,
    COVER_NAME,
    STAND_NAME,
    STILL_MOTION_M,
    STILL_SPEED_M_S,
    STILL_WINDOW_STEPS,
    TABLE_TOP,
    TCP_BELOW_LINK_M,
)
from logic import evaluate_state, lamp_state, rotation_from_quat

# Facts the end state cannot show; reset at every reset.
_RUN = {
    "fixture_start": None,   # printer and stand positions at the first step
    "fixture_moved": False,
    "open_run": 0,           # control steps in a row with the cover pushed open at least BAY_OPEN_M
    "open_run_max": 0,       # the longest such run so far
    "max_lift": 0.0,         # highest the roll's origin has been above its start height
    "hist": [],              # (roll position, cover slide) of the last STILL_WINDOW_STEPS steps
}

_EYE = np.eye(3)


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


def _box_distance(point: np.ndarray, centre_world: np.ndarray, rot: np.ndarray, half: np.ndarray) -> float:
    local = (point - centre_world) @ rot
    d = np.maximum(np.abs(local) - half, 0.0)
    return float(np.linalg.norm(d))


def tcp_to_printer(tcp: np.ndarray, slide: float) -> float:
    """Distance from a gripper centre to the printer body, the chute and the cover (shifted by its slide)."""
    base = np.array([PRINTER_XY[0], PRINTER_XY[1], TABLE_TOP])
    nearest = 9.0
    for c, s, _ in PRINTER_BOXES:
        nearest = min(nearest, _box_distance(tcp, base + np.asarray(c, dtype=float), _EYE, np.asarray(s, dtype=float) / 2))
    shift = np.array([float(slide), 0.0, 0.0])
    for c, s, _ in COVER_BOXES:
        nearest = min(nearest, _box_distance(tcp, base + shift + np.asarray(c, dtype=float), _EYE, np.asarray(s, dtype=float) / 2))
    return nearest


def tcp_to_roll(tcp: np.ndarray, roll_pos, roll_quat) -> float:
    """Distance from a gripper centre to the paper cylinder or the paper tail."""
    rot = rotation_from_quat(roll_quat)
    p = (np.asarray(tcp, dtype=float) - np.asarray(roll_pos, dtype=float)) @ rot            # roll frame
    radial = max(math.hypot(p[0], p[2] - ROLL_CENTRE_Z) - ROLL_RADIUS_M, 0.0)
    axial = max(abs(p[1]) - ROLL_CORE_WIDTH_M / 2, 0.0)
    cylinder = math.hypot(radial, axial)
    tail = _box_distance(p, np.asarray(ROLL_TAIL[0], dtype=float), _EYE, np.asarray(ROLL_TAIL[1], dtype=float) / 2)
    return min(cylinder, tail)


def hands_clear(tcps, roll_pos, roll_quat, slide: float) -> bool:
    """Every gripper centre is at least RELEASE_MIN_DIST_M from the printer (with its cover) and from the roll."""
    for tcp in tcps:
        if tcp_to_printer(np.asarray(tcp, dtype=float), slide) < RELEASE_MIN_DIST_M:
            return False
        if tcp_to_roll(np.asarray(tcp, dtype=float), roll_pos, roll_quat) < RELEASE_MIN_DIST_M:
            return False
    return True


def _reset_run() -> None:
    _RUN.update(fixture_start=None, fixture_moved=False, open_run=0, open_run_max=0, max_lift=0.0, hist=[])


def advance(printer, roll, stand) -> None:
    """Update the run's latched facts from one control step's part states. Pure bookkeeping (no simulator calls), so an
    offline replay can drive it too."""
    slide = float(printer.sliders.get(COVER_NAME, 0.0))
    if _RUN["fixture_start"] is None:
        _RUN["fixture_start"] = (np.asarray(printer.pos, dtype=float), np.asarray(stand.pos, dtype=float))
    p0, s0 = _RUN["fixture_start"]
    if (
        float(np.linalg.norm(np.asarray(printer.pos, dtype=float) - p0)) > FIXTURE_MOVE_M
        or float(np.linalg.norm(np.asarray(stand.pos, dtype=float) - s0)) > FIXTURE_MOVE_M
    ):
        _RUN["fixture_moved"] = True
    _RUN["open_run"] = _RUN["open_run"] + 1 if slide >= BAY_OPEN_M else 0
    _RUN["open_run_max"] = max(_RUN["open_run_max"], _RUN["open_run"])
    _RUN["max_lift"] = max(_RUN["max_lift"], float(roll.pos[2]) - (TABLE_TOP + ROLL_START_ORIGIN_Z))
    _RUN["hist"] = (_RUN["hist"] + [(np.asarray(roll.pos, dtype=float), slide)])[-STILL_WINDOW_STEPS:]


def window_still() -> bool:
    """The roll moved less than 1 mm and the cover less than 1 mm over the last second. True when too little history."""
    hist = _RUN["hist"]
    if len(hist) < STILL_WINDOW_STEPS:
        return True
    roll_xyz = np.array([h[0] for h in hist])
    slides = np.array([h[1] for h in hist])
    return bool(np.ptp(roll_xyz, axis=0).max() <= STILL_MOTION_M and np.ptp(slides) <= STILL_MOTION_M)


def _on_reset(environment) -> None:
    _reset_run()
    try:
        printer, roll = _state(environment, PRINTER_NAME), _state(environment, ROLL_NAME)
        DISPLAY.reset(environment, lamp_state(roll.pos, roll.quat_xyzw, float(printer.sliders.get(COVER_NAME, 0.0))), roll.pos, roll.quat_xyzw)
    except Exception:  # display only
        pass


def _on_step(environment) -> None:
    try:
        printer, roll, stand = _state(environment, PRINTER_NAME), _state(environment, ROLL_NAME), _state(environment, STAND_NAME)
        advance(printer, roll, stand)
        slide = float(printer.sliders.get(COVER_NAME, 0.0))
    except Exception:  # never break an episode for bookkeeping
        return
    DISPLAY.update(environment, lamp_state(roll.pos, roll.quat_xyzw, slide), roll.pos, roll.quat_xyzw)  # display only; it guards itself


parts.on_reset(_on_reset)
parts.on_step(_on_step)


def _released(printer_state, roll_state) -> bool:
    environment = parts.env()
    if environment is None:
        return False
    try:
        for arm in ("left", "right"):
            if not parts.gripper_open(environment, arm, FINGERS_OPEN_FRACTION):
                return False
        return hands_clear(
            list(_hand_tcps(environment).values()), roll_state.pos, roll_state.quat_xyzw, float(printer_state.sliders.get(COVER_NAME, 0.0))
        )
    except Exception:
        return False


def _trace(record: dict) -> None:
    path = os.environ.get("TASK_TRACE")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")


def score(objects: Mapping[str, Any]) -> float:
    printer = objects.get(PRINTER_NAME)
    roll = objects.get(ROLL_NAME)
    if printer is None or roll is None:
        return 0.0
    slide = float(printer.sliders.get(COVER_NAME, 0.0))
    still = bool(roll.resting(STILL_SPEED_M_S) and window_still())
    s, ok, reason = evaluate_state(
        tuple(float(v) for v in roll.pos),
        tuple(float(v) for v in roll.quat_xyzw),
        slide,
        int(_RUN["open_run_max"]),
        float(_RUN["max_lift"]),
        bool(_RUN["fixture_moved"]),
        _released(printer, roll),
        still,
    )
    _trace(
        {
            "score": s,
            "reason": reason,
            "roll": [round(float(v), 4) for v in roll.pos],
            "cover_mm": round(slide * 1000, 1),
            "open_run_max": _RUN["open_run_max"],
            "max_lift_mm": round(_RUN["max_lift"] * 1000, 1),
            "fixture_moved": _RUN["fixture_moved"],
        }
    )
    return s


def success(objects: Mapping[str, Any]) -> bool:
    return score(objects) >= 1.0


def distance(objects: Mapping[str, Any]) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.10
