"""Pure-Python logic and scoring computation for zero_linear_axis (v2)."""

from __future__ import annotations

import math
from typing import Sequence

from geometry import (
    BASE_POS_WORLD,
    CARRIAGE_MIN_MOVE_LADDER_0_25_M,
    CARRIAGE_TARGET_DISP_M,
    HOLE_REST_WORLD_Y,
    HOLE_WORLD_X,
    MARK_OFFSET_LADDER_0_50_M,
    MARK_OFFSET_LADDER_0_75_M,
    MARK_OFFSET_LADDER_1_00_M,
    MAX_BASE_DRIFT_GATE_M,
    MAX_BASE_DRIFT_SCORE_M,
    MAX_BASE_TILT_DEG,
    PIN_AXIS_IN_HOLE_M,
    PIN_BOTTOM_THROUGH_Z,
    PIN_HEIGHT_M,
    PIN_MAX_TILT_DEG,
    TABLE_TOP,
)


def compute_base_drift(base_pos: Sequence[float]) -> float:
    """Distance in the XY plane of the base from its start position (m)."""
    return math.hypot(float(base_pos[0]) - BASE_POS_WORLD[0], float(base_pos[1]) - BASE_POS_WORLD[1])


def tilt_deg(quat_xyzw: Sequence[float]) -> float:
    """Angle between a body's local +Z axis and world +Z (degrees)."""
    x, y, z, w = (float(v) for v in quat_xyzw)
    r22 = max(-1.0, min(1.0, 1.0 - 2.0 * (x * x + y * y)))
    return math.degrees(math.acos(r22))


def mark_offset(carriage_disp: float) -> float:
    """Offset (m) between the base mark and the carriage mark along y: 40 mm at the start, 0 after a 40 mm push."""
    return abs(float(carriage_disp) - CARRIAGE_TARGET_DISP_M)


def hole_world_xy(base_pos: Sequence[float], carriage_disp: float) -> tuple[float, float]:
    """World xy of the lug hole centre for the given base position and carriage displacement."""
    dx = float(base_pos[0]) - BASE_POS_WORLD[0]
    dy = float(base_pos[1]) - BASE_POS_WORLD[1]
    return HOLE_WORLD_X + dx, HOLE_REST_WORLD_Y + dy + float(carriage_disp)


def pin_through_hole(pin_pos: Sequence[float], pin_quat: Sequence[float], base_pos: Sequence[float], carriage_disp: float) -> bool:
    """True when the pin stands in the lug hole: axis within the hole, bottom below the lug, pin nearly upright."""
    hx, hy = hole_world_xy(base_pos, carriage_disp)
    px, py, pz = (float(v) for v in pin_pos)
    if math.hypot(px - hx, py - hy) > PIN_AXIS_IN_HOLE_M:
        return False
    if pz - PIN_HEIGHT_M / 2 > PIN_BOTTOM_THROUGH_Z:
        return False
    return tilt_deg(pin_quat) <= PIN_MAX_TILT_DEG


def evaluate_state(
    base_pos: Sequence[float],
    base_quat: Sequence[float],
    carriage_disp: float,
    pin_pos: Sequence[float],
    pin_quat: Sequence[float],
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Return (score, success, reason).

    Gates (score 0): base off the table, base tilted > 20 degrees, base drifted > 5 cm.
    Ladder: 0.25 carriage pushed >= 20 mm; 0.5 mark offset <= 6 mm; 0.75 mark offset <= 3 mm;
    1.0 offset <= 3 mm AND the pin stands through the lug hole AND the base drifted < 8 mm AND everything is still.
    """
    if float(base_pos[2]) < TABLE_TOP - 0.020:
        return 0.0, False, "gate: base fell off the table"
    tilt = tilt_deg(base_quat)
    if tilt > MAX_BASE_TILT_DEG:
        return 0.0, False, f"gate: base tilted {tilt:.1f} deg"
    drift = compute_base_drift(base_pos)
    if drift > MAX_BASE_DRIFT_GATE_M:
        return 0.0, False, f"gate: base drifted {drift * 100:.1f} cm"

    offset = mark_offset(carriage_disp)
    moved = float(carriage_disp)

    if (
        offset <= MARK_OFFSET_LADDER_1_00_M
        and pin_through_hole(pin_pos, pin_quat, base_pos, carriage_disp)
        and drift < MAX_BASE_DRIFT_SCORE_M
        and resting
    ):
        return 1.0, True, "marks aligned, pin through the lug hole, base held"
    if offset <= MARK_OFFSET_LADDER_0_75_M:
        return 0.75, False, f"marks aligned within {offset * 1000:.1f} mm"
    if offset <= MARK_OFFSET_LADDER_0_50_M:
        return 0.5, False, f"marks within {offset * 1000:.1f} mm"
    if moved >= CARRIAGE_MIN_MOVE_LADDER_0_25_M and offset <= CARRIAGE_TARGET_DISP_M:
        return 0.25, False, f"carriage moved {moved * 1000:.1f} mm"
    return 0.0, False, "carriage at rest"
