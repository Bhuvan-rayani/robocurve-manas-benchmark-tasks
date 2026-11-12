"""Pure scoring logic for air_fryer_basket_unhook_trivet."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from geometry import (
    BASKET_START,
    LIFT_MIN_M,
    MAT_CENTRE_XY,
    MAT_MAX_FLOOR_GAP_M,
    MAT_MAX_OFFCENTRE_M,
    MAT_MAX_TILT_DEG,
    MAT_MAX_TURN_DEG,
    MAT_TOP_Z,
    SLIDE_MIN_M,
    TABLE_TOP,
    UNHOOK_ORIGIN_X_M,
)


def rotation_from_quat(q: Sequence[float]) -> np.ndarray:
    x, y, z, w = np.asarray(q, dtype=float) / np.linalg.norm(q)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def tilt_deg(q: Sequence[float]) -> float:
    return math.degrees(math.acos(max(-1.0, min(1.0, float(rotation_from_quat(q)[2, 2])))))


def turn_deg(q: Sequence[float]) -> float:
    r = rotation_from_quat(q)
    return abs(math.degrees(math.atan2(r[1, 0], r[0, 0])))


def on_mat(pos: Sequence[float], quat: Sequence[float]) -> bool:
    """The basket origin is the centre of its floor's underside."""
    x, y, z = (float(v) for v in pos)
    off = math.hypot(x - MAT_CENTRE_XY[0], y - MAT_CENTRE_XY[1])
    gap = z - TABLE_TOP - MAT_TOP_Z
    return (
        off <= MAT_MAX_OFFCENTRE_M
        and abs(gap) <= MAT_MAX_FLOOR_GAP_M
        and tilt_deg(quat) <= MAT_MAX_TILT_DEG
        and turn_deg(quat) <= MAT_MAX_TURN_DEG
    )


def evaluate_state(
    pos: Sequence[float],
    quat: Sequence[float],
    min_x: float,
    max_free_lift: float,
    fault: bool,
    released: bool,
    still: bool,
) -> tuple[float, bool, str]:
    """End state plus the run's latched facts: min_x = lowest basket-origin x reached, max_free_lift = highest the basket
    was lifted (m) while its flanges were clear of the hooks, fault = a hot surface was touched."""
    if fault:
        return 0.0, False, "fault: a gripper touched a hot surface"
    if on_mat(pos, quat):
        if released and still:
            return 1.0, True, "basket on the mat; released and still"
        return 0.75, False, "basket on the mat; not released or not still"
    if min_x < UNHOOK_ORIGIN_X_M and max_free_lift >= LIFT_MIN_M:
        return 0.5, False, "basket unhooked and lifted but not on the mat"
    if BASKET_START[0] - min_x >= SLIDE_MIN_M:
        return 0.25, False, "basket slid clear toward the robot"
    return 0.0, False, "basket not out of the hooks"
