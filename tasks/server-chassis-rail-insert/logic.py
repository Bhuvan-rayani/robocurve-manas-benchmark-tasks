"""Pure-Python logic and scoring computation for server_chassis_rail_insert."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from geometry import (
    CHASSIS_GOAL_X,
    CHASSIS_REAR_LOCAL_X,
    CHASSIS_START_POS,
    EAR_BACK_LOCAL_X,
    FLUSH_TOLERANCE_M,
    LIFT_SCORE_THRESHOLD_M,
    MAX_LATERAL_DRIFT_GATE_M,
    MAX_POST_DISPLACEMENT_GATE_M,
    MAX_TILT_GATE_DEG,
    POST_A_POS_WORLD,
    POST_B_POS_WORLD,
    POST_FRONT_FACE_X,
    RAIL_DEPTH_STAGE1_M,
    RAIL_DEPTH_STAGE2_M,
    RAIL_START_X,
    SLIDE_START_THRESHOLD_M,
    SUCCESS_TILT_MAX_DEG,
    TABLE_TOP,
)


def compute_post_displacement(pos: Sequence[float], initial_pos: Sequence[float]) -> float:
    """Euclidean distance of post from its starting position."""
    return float(np.linalg.norm(np.asarray(pos, dtype=float) - np.asarray(initial_pos, dtype=float)))


def quat_to_rot_matrix(quat_xyzw: Sequence[float]) -> np.ndarray:
    """Convert quaternion [x, y, z, w] to 3x3 rotation matrix."""
    q = np.asarray(quat_xyzw, dtype=float)
    norm = np.linalg.norm(q)
    if norm < 1e-8:
        return np.eye(3)
    x, y, z, w = q / norm
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


def compute_chassis_tilt_deg(quat_xyzw: Sequence[float]) -> float:
    """Compute tilt of chassis (deviation of body +Z axis from world vertical [0, 0, 1]) in degrees."""
    r = quat_to_rot_matrix(quat_xyzw)
    # Z axis in world coordinates is r[:, 2]
    cos_tilt = float(np.clip(r[2, 2], -1.0, 1.0))
    return float(np.degrees(np.arccos(cos_tilt)))


def compute_chassis_yaw_deg(quat_xyzw: Sequence[float]) -> float:
    """Compute yaw deviation of chassis body +X axis from world +X [1, 0, 0] in degrees."""
    r = quat_to_rot_matrix(quat_xyzw)
    # X axis in world coordinates is r[:, 0]
    return float(np.degrees(abs(math.atan2(r[1, 0], r[0, 0]))))


def compute_chassis_total_angle_deg(quat_xyzw: Sequence[float]) -> float:
    """Compute total angular deviation from reference orientation."""
    tilt = compute_chassis_tilt_deg(quat_xyzw)
    yaw = compute_chassis_yaw_deg(quat_xyzw)
    return math.hypot(tilt, yaw)


def compute_rail_depth(chassis_pos: Sequence[float]) -> float:
    """Metres that the chassis rear end has entered the rails."""
    rear_x = float(chassis_pos[0]) + CHASSIS_REAR_LOCAL_X
    return max(0.0, rear_x - RAIL_START_X)


def compute_ear_post_gap(chassis_pos: Sequence[float]) -> float:
    """Distance in metres between the rear face of the front ears and the post front faces."""
    ear_back_x = float(chassis_pos[0]) + EAR_BACK_LOCAL_X
    return abs(ear_back_x - POST_FRONT_FACE_X)


def evaluate_state(
    post_a_pos: Sequence[float],
    post_b_pos: Sequence[float],
    chassis_pos: Sequence[float],
    chassis_quat: Sequence[float],
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Evaluate current state and return (score, success, reason).

    Rules:
      - First update on initial fixture pose must be 0.0 (idle policy = 0.0).
      - Gate 1: 0 if rack post A or B moved > 5 mm from start.
      - Gate 2: 0 if chassis tilts > 15 degrees.
      - Gate 3: 0 if chassis fell below table top (z < TABLE_TOP).
      - Gate 4: 0 if chassis drifted laterally > 5 cm (abs(y) > 5 cm).
      - Ladder:
        - 0.25: chassis lifted > 2 cm or advanced >= 2 cm.
        - 0.50: rear end in rails >= 6 cm.
        - 0.75: rear end in rails >= 15 cm.
        - 1.00: ears within 3 mm of post faces, tilt < 5 degrees, still 1 s.
    """
    # Gate 1: Rack posts moved > 5 mm
    disp_a = compute_post_displacement(post_a_pos, POST_A_POS_WORLD)
    disp_b = compute_post_displacement(post_b_pos, POST_B_POS_WORLD)
    if disp_a > MAX_POST_DISPLACEMENT_GATE_M:
        return 0.0, False, f"gate: rack post A moved {disp_a * 1000:.1f} mm (> 5 mm)"
    if disp_b > MAX_POST_DISPLACEMENT_GATE_M:
        return 0.0, False, f"gate: rack post B moved {disp_b * 1000:.1f} mm (> 5 mm)"

    # Gate 2: Chassis tilt > 15 degrees
    tilt_deg = compute_chassis_tilt_deg(chassis_quat)
    if tilt_deg > MAX_TILT_GATE_DEG:
        return 0.0, False, f"gate: chassis tilt {tilt_deg:.1f} deg (> 15 deg)"

    # Gate 3: Chassis fell below table top
    if float(chassis_pos[2]) < TABLE_TOP:
        return 0.0, False, "gate: chassis fell below table top"

    # Gate 4: Lateral drift > 5 cm
    lat_drift = abs(float(chassis_pos[1]))
    if lat_drift > MAX_LATERAL_DRIFT_GATE_M:
        return 0.0, False, f"gate: chassis lateral drift {lat_drift * 100:.1f} cm (> 5 cm)"

    # Check alignment and depth metrics
    total_angle = compute_chassis_total_angle_deg(chassis_quat)
    ear_gap = compute_ear_post_gap(chassis_pos)
    depth = compute_rail_depth(chassis_pos)
    lift = float(chassis_pos[2]) - CHASSIS_START_POS[2]
    advance = float(chassis_pos[0]) - CHASSIS_START_POS[0]

    # Full success: ears flush (gap <= 3 mm), tilt < 5 deg, resting
    if ear_gap <= FLUSH_TOLERANCE_M and total_angle < SUCCESS_TILT_MAX_DEG:
        if resting:
            return 1.0, True, "ears flush with post faces (gap <= 3 mm), tilt < 5 deg, still 1 s"
        return 0.75, False, "ears flush with post faces, settling"

    # Ladder 0.75: rear in rails >= 15 cm
    if depth >= RAIL_DEPTH_STAGE2_M:
        return 0.75, False, f"rear end in rails {depth * 100:.1f} cm (>= 15 cm)"

    # Ladder 0.50: rear in rails >= 6 cm
    if depth >= RAIL_DEPTH_STAGE1_M:
        return 0.50, False, f"rear end in rails {depth * 100:.1f} cm (>= 6 cm)"

    # Ladder 0.25: chassis lifted > 2 cm or advanced >= 2 cm
    if lift >= LIFT_SCORE_THRESHOLD_M or advance >= SLIDE_START_THRESHOLD_M:
        return 0.25, False, "chassis lifted > 2 cm or advanced >= 2 cm"

    # Initial state / zero progress
    return 0.0, False, "initial/zero progress: chassis at rest on staging plate"
