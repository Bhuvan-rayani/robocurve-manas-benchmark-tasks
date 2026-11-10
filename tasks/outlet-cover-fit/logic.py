"""Pure-Python scoring logic and gate checks for outlet_cover_fit."""

from __future__ import annotations

import math
from typing import Mapping, Sequence, Tuple

from geometry import (
    CAP_HEIGHT_M,
    CAP_NAMES,
    CAP_SEATED_XY_TOL_M,
    FALLEN_Z_THRESHOLD,
    GATE_PLATE_MAX_DRIFT_M,
    PLATE_DIMS_M,
    PLATE_START_POS_WORLD,
    SOCKET_A_OFFSET_M,
    SOCKET_B_OFFSET_M,
    SOCKET_C_OFFSET_M,
    SUCCESS_PLATE_MAX_DRIFT_M,
)


def _get_cap_top_z(cap_pos: Sequence[float], plate_base_z: float) -> float:
    """Return top z of cap whether pos is given as bbox centre or base."""
    # If pos[2] is close to table top (base origin), top is pos[2] + height
    # If pos[2] is center (~TABLE_TOP + height/2), top is pos[2] + height/2
    if cap_pos[2] < plate_base_z + 0.010:
        return cap_pos[2] + CAP_HEIGHT_M
    return cap_pos[2] + (CAP_HEIGHT_M / 2.0)


def evaluate_state(
    plate_pos: Sequence[float],
    cap_positions: Mapping[str, Sequence[float]] | Sequence[Sequence[float]],
    resting: bool = True,
) -> Tuple[float, bool, str]:
    """Evaluate task state and return (score, success, reason)."""
    # Normalize cap positions
    if isinstance(cap_positions, Mapping):
        caps = [cap_positions[name] for name in CAP_NAMES if name in cap_positions]
    else:
        caps = list(cap_positions)

    # Gate 1: Plate drift gate (> 6 cm)
    dx = plate_pos[0] - PLATE_START_POS_WORLD[0]
    dy = plate_pos[1] - PLATE_START_POS_WORLD[1]
    plate_drift = math.hypot(dx, dy)
    if plate_drift > GATE_PLATE_MAX_DRIFT_M:
        return 0.0, False, f"Gate failed: wall plate moved {plate_drift * 1000.0:.1f} mm (> 60 mm)"

    # Gate 2: Objects fallen off table
    if plate_pos[2] < FALLEN_Z_THRESHOLD:
        return 0.0, False, "Gate failed: wall plate fell off table"

    for i, c_pos in enumerate(caps):
        if c_pos[2] < FALLEN_Z_THRESHOLD:
            return 0.0, False, f"Gate failed: cap {i} fell off table"

    # Compute current socket world positions based on plate pose
    plate_face_z = plate_pos[2] + PLATE_DIMS_M[2]
    socket_targets = [
        (plate_pos[0] + SOCKET_A_OFFSET_M[0], plate_pos[1] + SOCKET_A_OFFSET_M[1]),
        (plate_pos[0] + SOCKET_B_OFFSET_M[0], plate_pos[1] + SOCKET_B_OFFSET_M[1]),
        (plate_pos[0] + SOCKET_C_OFFSET_M[0], plate_pos[1] + SOCKET_C_OFFSET_M[1]),
    ]

    # Check which sockets have a seated cap
    occupied_sockets = set()
    for c_pos in caps:
        cap_top_z = _get_cap_top_z(c_pos, plate_pos[2])
        # Nominal seated cap top is plate_pos[2] + 0.002 (socket floor) + 0.030 (cap height) = plate_pos[2] + 0.032 m
        # Plate face is plate_pos[2] + 0.020 m -> nominal top_diff is +0.012 m
        # A seated cap has top_diff within 8 mm of nominal (and far below hover/carry height)
        top_diff = cap_top_z - plate_face_z
        z_seated = abs(top_diff - 0.012) <= 0.008

        if not z_seated:
            continue

        for s_idx, (sx, sy) in enumerate(socket_targets):
            if s_idx in occupied_sockets:
                continue
            dist_xy = math.hypot(c_pos[0] - sx, c_pos[1] - sy)
            if dist_xy <= CAP_SEATED_XY_TOL_M:
                occupied_sockets.add(s_idx)
                break

    seated_count = len(occupied_sockets)

    # Ladder scoring
    if seated_count == 0:
        return 0.0, False, "0 caps seated"
    elif seated_count == 1:
        return 0.25, False, "1 cap seated"
    elif seated_count == 2:
        return 0.50, False, "2 caps seated"
    elif seated_count == 3:
        if plate_drift >= SUCCESS_PLATE_MAX_DRIFT_M:
            return (
                0.75,
                False,
                f"3 caps seated, but plate moved {plate_drift * 1000.0:.1f} mm (>= 15 mm)",
            )
        ok = bool(resting)
        return (
            1.00,
            ok,
            f"Success: 3 caps seated and plate drift {plate_drift * 1000.0:.1f} mm < 15 mm",
        )

    return 0.0, False, "Invalid state"
