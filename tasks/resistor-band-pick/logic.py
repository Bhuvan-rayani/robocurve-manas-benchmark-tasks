"""Pure-Python logic and scoring computation for resistor_band_pick."""

from __future__ import annotations

import math
from typing import Mapping

from geometry import (
    BOARD_POS_WORLD,
    COVER_CLOSED_TOLERANCE_M,
    MAX_BOARD_DRIFT_GATE_M,
    RES_HEIGHT_M,
    RES_NAMES,
    RES_START_POSITIONS,
    RESISTOR_LIFTED_THRESHOLD_M,
    SOCKET_HOLE_WORLD_XY,
    SOCKET_HOVER_RADIUS_M,
    SOCKET_RIM_Z_WORLD,
    SOCKET_SEATED_DEPTH_THRESHOLD_M,
    TARGET_RES_NAME,
)


def compute_board_drift(pos: tuple[float, float, float]) -> float:
    """Distance in XY plane from initial socket board position."""
    dx = pos[0] - BOARD_POS_WORLD[0]
    dy = pos[1] - BOARD_POS_WORLD[1]
    return math.hypot(dx, dy)


def compute_resistor_xy_offset_from_socket(pos: tuple[float, float, float]) -> float:
    """Distance in XY plane from socket center."""
    dx = pos[0] - SOCKET_HOLE_WORLD_XY[0]
    dy = pos[1] - SOCKET_HOLE_WORLD_XY[1]
    return math.hypot(dx, dy)


def is_resistor_lifted(name: str, pos: tuple[float, float, float]) -> bool:
    """Check if resistor has been lifted > 2 cm from its starting pocket pose."""
    start_z = RES_START_POSITIONS[name][2]
    return pos[2] >= start_z + RESISTOR_LIFTED_THRESHOLD_M


def is_resistor_in_socket(pos: tuple[float, float, float]) -> bool:
    """Check if a resistor is positioned inside the socket hole (below rim)."""
    xy_dist = compute_resistor_xy_offset_from_socket(pos)
    top_z = pos[2] + RES_HEIGHT_M / 2
    # Socket hole has 16 mm radius (32 mm square/round)
    return (xy_dist <= 0.018) and (top_z <= SOCKET_RIM_Z_WORLD + 0.005)


def compute_seated_depth(pos: tuple[float, float, float]) -> float:
    """Insertion depth of resistor base into the socket relative to the rim."""
    base_z = pos[2] - RES_HEIGHT_M / 2
    return max(0.0, SOCKET_RIM_Z_WORLD - base_z)


def is_cover_closed(cover_disp: float) -> bool:
    """Check if the socket cover slider is within 3 mm of rest position."""
    return abs(cover_disp) <= COVER_CLOSED_TOLERANCE_M


def evaluate_state(
    board_pos: tuple[float, float, float],
    resistor_positions: Mapping[str, tuple[float, float, float]],
    cover_disp: float = 0.0,
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Evaluate current state: returns (score, success, reason).

    Scoring ladder:
      - Gate 1: 0 if the board moved > 5 mm.
      - Gate 2: 0 if any wrong resistor ends in the socket.
      - 0.25: any resistor lifted > 2 cm.
      - 0.50: the brown-black-red target resistor (res_c) lifted > 2 cm.
      - 0.75: target resistor is over the socket within 8 mm (lifted).
      - 1.00: seated >= 60 mm deep (top below the rim), cover bar closed (within 3 mm of rest), still 1 s.
    """
    # Gate 1: Board moved > 5 mm
    drift = compute_board_drift(board_pos)
    if drift > MAX_BOARD_DRIFT_GATE_M:
        return 0.0, False, f"gate: board moved {drift * 1000:.1f} mm (> 5 mm gate threshold)"

    # Gate 2: Any wrong resistor ends in the socket
    for name in RES_NAMES:
        if name != TARGET_RES_NAME:
            r_pos = resistor_positions.get(name)
            if r_pos is not None and is_resistor_in_socket(r_pos):
                return 0.0, False, f"gate: wrong resistor {name} entered socket"

    target_pos = resistor_positions.get(TARGET_RES_NAME)
    if target_pos is None:
        return 0.0, False, f"missing state for target resistor {TARGET_RES_NAME}"

    xy_dist = compute_resistor_xy_offset_from_socket(target_pos)
    seated_depth = compute_seated_depth(target_pos)
    top_z = target_pos[2] + RES_HEIGHT_M / 2
    top_below_rim = top_z <= (SOCKET_RIM_Z_WORLD + 0.001)
    cover_shut = is_cover_closed(cover_disp)

    # 1.00: Seated >= 60 mm deep, top below rim, cover closed within 3 mm, resting
    if (
        xy_dist <= SOCKET_HOVER_RADIUS_M
        and seated_depth >= SOCKET_SEATED_DEPTH_THRESHOLD_M
        and top_below_rim
        and cover_shut
        and resting
    ):
        return (
            1.0,
            True,
            f"target resistor seated {seated_depth * 1000:.1f} mm deep (top below rim), cover closed, resting",
        )

    # 0.75: Target resistor over socket within 8 mm (lifted above table)
    target_lifted = is_resistor_lifted(TARGET_RES_NAME, target_pos)
    if xy_dist <= SOCKET_HOVER_RADIUS_M and target_lifted:
        return (
            0.75,
            False,
            f"target resistor over socket (offset {xy_dist * 1000:.1f} mm <= 8 mm)",
        )

    # 0.50: Target brown-black-red resistor lifted > 2 cm
    if target_lifted:
        return 0.50, False, "target brown-black-red resistor lifted > 2 cm"

    # 0.25: Any resistor lifted > 2 cm
    for name in RES_NAMES:
        pos = resistor_positions.get(name)
        if pos is not None and is_resistor_lifted(name, pos):
            return 0.25, False, f"resistor {name} lifted > 2 cm"

    # Initial state / zero effort
    return 0.0, False, "initial start pose / no resistor lifted"
