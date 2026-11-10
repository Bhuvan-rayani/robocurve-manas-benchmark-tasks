"""Pure-Python evaluation logic for stair_nosing_strip_fit."""

from __future__ import annotations

import math
from typing import Sequence

from geometry import (
    GATE_BASE_DRIFT_MAX_M,
    GATE_MAX_TILT_DEG,
    GATE_MIN_Z_M,
    NOSING_STRIP_START_POS_WORLD,
    NOSING_STRIP_TARGET_POS_WORLD,
    SCORE_025_LIFT_MIN_Z_M,
    SCORE_050_OVER_STEP_X_MAX_M,
    SCORE_050_OVER_STEP_X_MIN_M,
    SCORE_075_ENGAGED_MAX_Z_M,
    SCORE_075_MAX_TILT_DEG,
    SCORE_100_ASYMMETRY_Y_TOL_M,
    SCORE_100_FLANGE_Z_TOL_M,
    SCORE_100_LIP_X_TOL_M,
    SCORE_100_MAX_TILT_DEG,
    STAIR_STEP_POS_WORLD,
    STRIP_PAD_POS_WORLD,
    TABLE_TOP,
)


def _dist3d(p1: Sequence[float], p2: Sequence[float]) -> float:
    return math.sqrt(
        (p1[0] - p2[0]) ** 2
        + (p1[1] - p2[1]) ** 2
        + (p1[2] - p2[2]) ** 2
    )


def compute_tilt_deg(quat_xyzw: Sequence[float]) -> float:
    """Compute tilt of body z-axis relative to world +Z in degrees."""
    qx, qy, qz, qw = quat_xyzw
    z_z = 1.0 - 2.0 * (qx * qx + qy * qy)
    z_z = max(-1.0, min(1.0, z_z))
    tilt_rad = math.acos(z_z)
    return math.degrees(tilt_rad)


def evaluate_state(
    step_pos: Sequence[float] = STAIR_STEP_POS_WORLD,
    pad_pos: Sequence[float] = STRIP_PAD_POS_WORLD,
    strip_pos: Sequence[float] = NOSING_STRIP_START_POS_WORLD,
    strip_quat_xyzw: Sequence[float] = (0.0, 0.0, 0.0, 1.0),
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Evaluate task state and return (score, success, reason).

    Ladder:
      0.00: Initial staging on pad.
      0.25: Strip lifted off pad (z >= TABLE_TOP + 40 mm).
      0.50: Strip brought over step edge (x in [0.26, 0.33] m).
      0.75: Front lip engaged over step front face (flange z <= TABLE_TOP + 75 mm, tilt <= 6 deg).
      1.00: Fully seated (flange flush |dz| <= 2.5 mm, lip contacting |dx| <= 3.0 mm,
            lateral asymmetry |dy| <= 4.0 mm, tilt <= 3 deg), resting for 1.0 s.
    """
    # -------------------------------------------------------------------------
    # Gate 1: Fixed base drift checks (<= 5 mm)
    # -------------------------------------------------------------------------
    d_step = _dist3d(step_pos, STAIR_STEP_POS_WORLD)
    if d_step > GATE_BASE_DRIFT_MAX_M:
        return 0.0, False, f"Gate: stair_step moved {d_step * 1000.0:.1f} mm > 5.0 mm"

    d_pad = _dist3d(pad_pos, STRIP_PAD_POS_WORLD)
    if d_pad > GATE_BASE_DRIFT_MAX_M:
        return 0.0, False, f"Gate: strip_pad moved {d_pad * 1000.0:.1f} mm > 5.0 mm"

    # -------------------------------------------------------------------------
    # Gate 2: Dropped below table level
    # -------------------------------------------------------------------------
    if strip_pos[2] < GATE_MIN_Z_M:
        return 0.0, False, f"Gate: nosing_strip dropped below table level (z={strip_pos[2]:.3f} m)"

    # -------------------------------------------------------------------------
    # Gate 3: Extreme tilt (inverted / overturned)
    # -------------------------------------------------------------------------
    tilt_deg = compute_tilt_deg(strip_quat_xyzw)
    if tilt_deg > GATE_MAX_TILT_DEG:
        return 0.0, False, f"Gate: nosing_strip overturned (tilt={tilt_deg:.1f} deg > {GATE_MAX_TILT_DEG} deg)"

    dx = abs(strip_pos[0] - NOSING_STRIP_TARGET_POS_WORLD[0])
    dy = abs(strip_pos[1] - NOSING_STRIP_TARGET_POS_WORLD[1])
    dz = abs(strip_pos[2] - NOSING_STRIP_TARGET_POS_WORLD[2])

    # -------------------------------------------------------------------------
    # 1.00: Strip fully seated flush on step tread
    # -------------------------------------------------------------------------
    if (
        dz <= SCORE_100_FLANGE_Z_TOL_M
        and dx <= SCORE_100_LIP_X_TOL_M
        and dy <= SCORE_100_ASYMMETRY_Y_TOL_M
        and tilt_deg <= SCORE_100_MAX_TILT_DEG
        and resting
    ):
        return (
            1.00,
            True,
            f"Nosing strip fully seated (dx={dx * 1000.0:.1f} mm, dy={dy * 1000.0:.1f} mm, dz={dz * 1000.0:.1f} mm, tilt={tilt_deg:.1f} deg)",
        )

    # -------------------------------------------------------------------------
    # 0.75: Front lip engaged over step front face
    # -------------------------------------------------------------------------
    if (
        dx <= 0.015
        and strip_pos[2] <= SCORE_075_ENGAGED_MAX_Z_M
        and tilt_deg <= SCORE_075_MAX_TILT_DEG
    ):
        return (
            0.75,
            False,
            f"Nosing strip lip engaged over step face (dx={dx * 1000.0:.1f} mm, z={strip_pos[2]:.3f} m, tilt={tilt_deg:.1f} deg)",
        )

    # -------------------------------------------------------------------------
    # 0.50: Strip brought over step edge
    # -------------------------------------------------------------------------
    if (
        SCORE_050_OVER_STEP_X_MIN_M <= strip_pos[0] <= SCORE_050_OVER_STEP_X_MAX_M
        and strip_pos[2] >= TABLE_TOP + 0.030
    ):
        return (
            0.50,
            False,
            f"Nosing strip brought over step front edge (x={strip_pos[0]:.3f} m, z={strip_pos[2]:.3f} m)",
        )

    # -------------------------------------------------------------------------
    # 0.25: Strip lifted off pad
    # -------------------------------------------------------------------------
    if strip_pos[2] >= SCORE_025_LIFT_MIN_Z_M:
        return (
            0.25,
            False,
            f"Nosing strip lifted from pad (z={strip_pos[2]:.3f} m >= {SCORE_025_LIFT_MIN_Z_M:.3f} m)",
        )

    return 0.00, False, "Nosing strip at initial staging position on pad"
