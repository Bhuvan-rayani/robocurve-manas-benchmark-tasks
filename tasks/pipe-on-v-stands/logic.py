"""Pure-Python scoring logic and gate checks for pipe_on_v_stands (T17)."""

from __future__ import annotations

import math
from typing import Tuple
import numpy as np

from geometry import (
    DRIFT_STAND_MAX_M,
    LIFT_Z_MIN_M,
    OVER_STANDS_X_TOL_M,
    OVER_STANDS_Z_MIN_M,
    PIPE_START_CENTRE,
    SEATED_BOTH_X_TOL_M,
    SEATED_BOTH_Y_TOL_M,
    SEATED_BOTH_Z_TOL_M,
    SEATED_ONE_X_TOL_M,
    SEATED_ONE_Z_TOL_M,
    SEATED_TILT_MAX_RAD,
    SEATED_X_TARGET_M,
    SEATED_Z_TARGET_M,
    STAND_A_POS_WORLD,
    STAND_B_POS_WORLD,
    TABLE_TOP,
)


def quat_to_matrix(q: Tuple[float, float, float, float]) -> np.ndarray:
    """Convert (x, y, z, w) quaternion to 3x3 rotation matrix."""
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n > 1e-9:
        x, y, z, w = x / n, y / n, z / n, w / n
    else:
        return np.eye(3)

    return np.array([
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
        [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
        [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
    ], dtype=float)


def compute_pipe_axis(pipe_quat: Tuple[float, float, float, float]) -> np.ndarray:
    """Return unit vector of the pipe's long axis (local Y) in world coordinates."""
    rot = quat_to_matrix(pipe_quat)
    return rot[:, 1]


def compute_pipe_tilt_rad(pipe_quat: Tuple[float, float, float, float]) -> float:
    """Return angle in radians between pipe axis and the stand line (world Y)."""
    axis = compute_pipe_axis(pipe_quat)
    dot = abs(float(axis[1]))
    dot = min(1.0, max(0.0, dot))
    return float(math.acos(dot))


def evaluate_state(
    pipe_pos: Tuple[float, float, float],
    pipe_quat: Tuple[float, float, float, float],
    stand_a_pos: Tuple[float, float, float],
    stand_b_pos: Tuple[float, float, float],
    resting: bool = True,
) -> Tuple[float, bool, str]:
    """Evaluate task state and return (score, success, reason).

    Ladder:
      0.00: Initial state / gates fail
      0.25: Pipe lifted > 5 cm
      0.50: Pipe carried over the stands (within 4 cm of stand line, clear of stands)
      0.75: Pipe resting in at least one V stand
      1.00: Pipe resting in both V stands, axis within 5 deg, centered, resting 1 s
    """
    # Gate 1: Check fixed stand drift
    drift_a = math.sqrt(
        (stand_a_pos[0] - STAND_A_POS_WORLD[0]) ** 2 +
        (stand_a_pos[1] - STAND_A_POS_WORLD[1]) ** 2
    )
    if drift_a > DRIFT_STAND_MAX_M:
        return 0.0, False, f"stand_a moved {drift_a * 1000:.1f} mm > {DRIFT_STAND_MAX_M * 1000:.1f} mm"

    drift_b = math.sqrt(
        (stand_b_pos[0] - STAND_B_POS_WORLD[0]) ** 2 +
        (stand_b_pos[1] - STAND_B_POS_WORLD[1]) ** 2
    )
    if drift_b > DRIFT_STAND_MAX_M:
        return 0.0, False, f"stand_b moved {drift_b * 1000:.1f} mm > {DRIFT_STAND_MAX_M * 1000:.1f} mm"

    # Gate 2: Pipe dropped or off table
    pipe_centre_z = pipe_pos[2] + 0.03  # body origin is at cylinder bottom; centre is +0.03
    if pipe_centre_z < TABLE_TOP:
        return 0.0, False, "pipe dropped below table surface"

    if pipe_pos[0] < 0.05 or pipe_pos[0] > 0.55 or abs(pipe_pos[1]) > 0.45:
        return 0.0, False, "pipe rolled out of table bounds"

    # Compute pipe geometry
    pipe_centre = (pipe_pos[0], pipe_pos[1], pipe_centre_z)
    lift_height = pipe_centre[2] - PIPE_START_CENTRE[2]
    tilt_rad = compute_pipe_tilt_rad(pipe_quat)

    # Check Level 0.25: lifted > 5 cm
    if lift_height < LIFT_Z_MIN_M:
        return 0.0, False, f"pipe lifted {lift_height * 1000:.1f} mm < {LIFT_Z_MIN_M * 1000:.1f} mm"

    score = 0.25
    reason = f"pipe lifted {lift_height * 1000:.1f} mm >= 50 mm"

    # Check Level 0.50: carried over the stands
    dx_to_stands = abs(pipe_centre[0] - SEATED_X_TARGET_M)
    is_over_stands = (dx_to_stands <= OVER_STANDS_X_TOL_M) and (pipe_centre[2] >= OVER_STANDS_Z_MIN_M)

    if is_over_stands:
        score = 0.50
        reason = f"pipe over stands (dx={dx_to_stands * 1000:.1f} mm, z={pipe_centre[2]:.3f} m)"

    # Compute height at stand A (y = +0.21) and stand B (y = -0.21)
    axis = compute_pipe_axis(pipe_quat)
    # If axis has non-negligible Y component, extrapolate height to stands
    if abs(axis[1]) > 0.3:
        s_a = (0.21 - pipe_centre[1]) / axis[1]
        z_at_stand_a = pipe_centre[2] + s_a * axis[2]
        x_at_stand_a = pipe_centre[0] + s_a * axis[0]

        s_b = (-0.21 - pipe_centre[1]) / axis[1]
        z_at_stand_b = pipe_centre[2] + s_b * axis[2]
        x_at_stand_b = pipe_centre[0] + s_b * axis[0]
    else:
        z_at_stand_a = z_at_stand_b = pipe_centre[2]
        x_at_stand_a = x_at_stand_b = pipe_centre[0]

    in_stand_a = (
        abs(x_at_stand_a - SEATED_X_TARGET_M) <= SEATED_ONE_X_TOL_M and
        abs(z_at_stand_a - SEATED_Z_TARGET_M) <= SEATED_ONE_Z_TOL_M
    )
    in_stand_b = (
        abs(x_at_stand_b - SEATED_X_TARGET_M) <= SEATED_ONE_X_TOL_M and
        abs(z_at_stand_b - SEATED_Z_TARGET_M) <= SEATED_ONE_Z_TOL_M
    )

    if in_stand_a or in_stand_b:
        score = 0.75
        which = "both" if (in_stand_a and in_stand_b) else ("stand_a" if in_stand_a else "stand_b")
        reason = f"pipe seated in {which}"

    # Check Level 1.00: seated in both V stands with full alignment and stillness
    both_in_notch = in_stand_a and in_stand_b
    aligned_x = dx_to_stands <= SEATED_BOTH_X_TOL_M
    aligned_y = abs(pipe_centre[1]) <= SEATED_BOTH_Y_TOL_M
    aligned_z = abs(pipe_centre[2] - SEATED_Z_TARGET_M) <= SEATED_BOTH_Z_TOL_M
    aligned_tilt = tilt_rad <= SEATED_TILT_MAX_RAD

    if both_in_notch and aligned_x and aligned_y and aligned_z and aligned_tilt:
        if resting:
            return 1.0, True, "pipe seated securely in both V stands and resting"
        else:
            return 0.75, False, "pipe seated in both V stands but still moving"

    return score, False, reason
