"""Scorer wrappers for air_fryer_basket_unhook_trivet."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

import numpy as np

import parts
from geometry import (
    BASKET_ALL_BOXES,
    BASKET_HOT_BOXES,
    BASKET_NAME,
    BASKET_START,
    FINGERS_OPEN_FRACTION,
    HOOKS,
    HOT_MARGIN_M,
    HOUSING_CENTRE_XY,
    HOUSING_SIZE,
    PAD_BELOW_TCP_M,
    PLATE_BASE,
    RELEASE_MIN_DIST_M,
    STILL_SPEED_M_S,
    TABLE_TOP,
    TCP_BELOW_LINK_M,
    UNHOOK_ORIGIN_X_M,
)
from logic import evaluate_state, rotation_from_quat

# Facts the end state cannot show; reset at every reset. A fault is permanent for the run.
_RUN = {"fault": False, "min_x": 9.0, "max_free_lift": 0.0}

_EYE = np.eye(3)
# Fixed hot surfaces in the world frame: (centre, half size). The housing, the drawer plate and the hooks.
_FIXED_HOT = [
    (np.array([HOUSING_CENTRE_XY[0], HOUSING_CENTRE_XY[1], TABLE_TOP + HOUSING_SIZE[2] / 2]), np.array(HOUSING_SIZE) / 2),
    (np.array([PLATE_BASE[1][0], PLATE_BASE[1][1], TABLE_TOP + PLATE_BASE[1][2]]), np.array(PLATE_BASE[2]) / 2),
] + [(np.array([c[0], c[1], TABLE_TOP + c[2]]), np.array(s) / 2) for _, c, s in HOOKS]


def _hand_tcps(environment) -> dict[str, np.ndarray]:
    scene = environment.unwrapped.scene
    origin = parts._to_numpy(scene.env_origins[0])
    out = {}
    for arm in ("left", "right"):
        robot = scene[f"{arm}_robot"]
        names = list(robot.body_names)
        pos = parts._to_numpy(robot.data.body_pos_w)[0]
        idx = names.index("gripper") if "gripper" in names else len(names) - 1
        out[arm] = np.asarray(pos[idx] - origin, dtype=float) - np.array([0.0, 0.0, TCP_BELOW_LINK_M])
    return out


def _state(environment, name):
    return parts._read_part_state(environment, parts._PARTS[name])


def _box_distance(point: np.ndarray, centre_world: np.ndarray, rot: np.ndarray, half: np.ndarray) -> float:
    local = (point - centre_world) @ rot
    d = np.maximum(np.abs(local) - half, 0.0)
    return float(np.linalg.norm(d))


def _touches_hot(tcp: np.ndarray, basket_state) -> bool:
    """A pad's bottom point (13 mm below the gripper centre) within the margin of a hot surface."""
    p = tcp - np.array([0.0, 0.0, PAD_BELOW_TCP_M])
    for centre, half in _FIXED_HOT:
        if _box_distance(p, centre, _EYE, half) < HOT_MARGIN_M:
            return True
    rot = rotation_from_quat(basket_state.quat_xyzw)
    origin = np.asarray(basket_state.pos, dtype=float)
    for c, s in BASKET_HOT_BOXES:
        if _box_distance(p, origin + rot @ np.asarray(c, dtype=float), rot, np.asarray(s, dtype=float) / 2) < HOT_MARGIN_M:
            return True
    return False


def _on_reset(environment) -> None:
    _RUN.update(fault=False, min_x=9.0, max_free_lift=0.0)


def _on_step(environment) -> None:
    try:
        st = _state(environment, BASKET_NAME)
        pos = np.asarray(st.pos, dtype=float)
        _RUN["min_x"] = min(_RUN["min_x"], float(pos[0]))
        if pos[0] < UNHOOK_ORIGIN_X_M:
            _RUN["max_free_lift"] = max(_RUN["max_free_lift"], float(pos[2]) - (TABLE_TOP + BASKET_START[2]))
        for tcp in _hand_tcps(environment).values():
            if _touches_hot(tcp, st):
                _RUN["fault"] = True
    except Exception:  # never break an episode for bookkeeping
        pass


parts.on_reset(_on_reset)
parts.on_step(_on_step)


def _released(basket_state) -> bool:
    environment = parts.env()
    if environment is None:
        return False
    try:
        for arm in ("left", "right"):
            if not parts.gripper_open(environment, arm, FINGERS_OPEN_FRACTION):
                return False
        tcps = _hand_tcps(environment)
        rot = rotation_from_quat(basket_state.quat_xyzw)
        origin = np.asarray(basket_state.pos, dtype=float)
        for tcp in tcps.values():
            for c, s in BASKET_ALL_BOXES:
                if _box_distance(tcp, origin + rot @ np.asarray(c, dtype=float), rot, np.asarray(s, dtype=float) / 2) < RELEASE_MIN_DIST_M:
                    return False
        return True
    except Exception:
        return False


def _trace(record: dict) -> None:
    path = os.environ.get("TASK_TRACE")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")


def score(objects: Mapping[str, Any]) -> float:
    basket = objects.get(BASKET_NAME)
    if basket is None:
        return 0.0
    pos = tuple(float(v) for v in basket.pos)
    still = bool(basket.resting(STILL_SPEED_M_S))
    s, ok, reason = evaluate_state(
        pos,
        tuple(float(v) for v in basket.quat_xyzw),
        float(_RUN["min_x"]),
        float(_RUN["max_free_lift"]),
        bool(_RUN["fault"]),
        _released(basket),
        still,
    )
    _trace({"score": s, "reason": reason, "basket": [round(v, 4) for v in pos], "fault": _RUN["fault"], "min_x": round(_RUN["min_x"], 4)})
    return s


def success(objects: Mapping[str, Any]) -> bool:
    return score(objects) >= 1.0


def distance(objects: Mapping[str, Any]) -> float:
    return max(0.0, 1.0 - score(objects)) * 0.10
