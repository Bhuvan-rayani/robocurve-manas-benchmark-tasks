"""Pure-Python logic and scoring computation for window_restrictor_fit."""

from __future__ import annotations

import math
from typing import Mapping, Optional

from geometry import (
    BLOCK_LIFT_XY_THRESHOLD_M,
    BLOCK_LIFT_Z_THRESHOLD_M,
    BLOCK_START_POS_WORLD,
    BLOCK_TRACK_X_TOLERANCE_M,
    FRAME_POS_WORLD,
    GRIPPER_CLEARANCE_MIN_M,
    HOLE_MATCH_Y_TOLERANCE_M,
    HOLE_OPENINGS_M,
    HOLE_Y_COORDS,
    MAX_FRAME_DRIFT_GATE_M,
    MAX_OPENING_LADDER_075_M,
    PEG_SEATED_Z_MAX_M,
    SASH_NAME,
    SASH_TOUCH_TOL_M,
    TABLE_TOP,
    TARGET_HOLE_INDEX,
    TARGET_HOLE_Y,
    TARGET_OPENING_MAX_M,
    TARGET_OPENING_MIN_M,
)


def compute_frame_drift(frame_pos: tuple[float, float, float]) -> float:
    """Planar XY drift of window frame from starting position."""
    dx = frame_pos[0] - FRAME_POS_WORLD[0]
    dy = frame_pos[1] - FRAME_POS_WORLD[1]
    return math.hypot(dx, dy)


def is_block_lifted(block_pos: tuple[float, float, float]) -> bool:
    """Check if the stop block has been lifted from its starting pad."""
    dx = block_pos[0] - BLOCK_START_POS_WORLD[0]
    dy = block_pos[1] - BLOCK_START_POS_WORLD[1]
    xy_dist = math.hypot(dx, dy)
    z_lift = block_pos[2] - BLOCK_START_POS_WORLD[2]
    return (xy_dist >= BLOCK_LIFT_XY_THRESHOLD_M) or (z_lift >= BLOCK_LIFT_Z_THRESHOLD_M)


def find_nearest_track_hole(
    block_pos: tuple[float, float, float],
    frame_pos: tuple[float, float, float] = FRAME_POS_WORLD,
) -> tuple[int, float, bool]:
    """Find the index of the nearest track hole and whether the block is aligned.

    Returns:
        (nearest_index, dy_to_hole, is_aligned)
    """
    # Relative y position of block in frame coordinates
    y_rel = block_pos[1] - frame_pos[1]

    nearest_idx = min(range(len(HOLE_Y_COORDS)), key=lambda i: abs(y_rel - HOLE_Y_COORDS[i]))
    dy = abs(y_rel - HOLE_Y_COORDS[nearest_idx])
    aligned = dy <= HOLE_MATCH_Y_TOLERANCE_M
    return nearest_idx, dy, aligned


def is_block_seated_in_track(
    block_pos: tuple[float, float, float],
    frame_pos: tuple[float, float, float] = FRAME_POS_WORLD,
) -> tuple[bool, Optional[int], str]:
    """Check if the stop block is properly seated in one of the track holes with peg inserted.

    Returns:
        (is_seated, hole_index_or_None, reason)
    """
    # 1. Centred in track along X
    dx = abs(block_pos[0] - frame_pos[0])
    if dx > BLOCK_TRACK_X_TOLERANCE_M:
        return False, None, f"block not in track channel: x error {dx * 1000:.1f} mm"

    # 2. Aligned with a track hole along Y
    hole_idx, dy, aligned = find_nearest_track_hole(block_pos, frame_pos)
    if not aligned:
        return False, None, f"block not aligned with hole {hole_idx} (y error {dy * 1000:.1f} mm)"

    # 3. Peg seated vertically (peg >= 4 mm in hole, block body bottom near floor)
    if block_pos[2] > PEG_SEATED_Z_MAX_M:
        return False, None, f"block peg not seated: z = {block_pos[2]:.4f} m (max {PEG_SEATED_Z_MAX_M:.4f} m)"

    return True, hole_idx, f"block seated at hole {hole_idx} (y={HOLE_Y_COORDS[hole_idx]:.3f} m)"


def evaluate_state(
    frame_pos: tuple[float, float, float],
    sash_travel: float,
    block_pos: tuple[float, float, float],
    resting: bool = True,
    gripper_clearance_m: Optional[float] = None,
) -> tuple[float, bool, str]:
    """Evaluate the task state against gates and the score ladder.

    Rules from TASKS_10_FINAL.md:
      - Gate: 0 if frame moved > 5 mm.
      - 0.00: First update on start pose (block on pad, idle).
      - 0.25: Block lifted off start pad.
      - 0.50: Block seated in a track hole (peg >= 4 mm in).
      - 0.75: Sash maximum open <= 120 mm (block in track constraining sash).
      - 1.00: Block at the 100 mm hole, sash maximum open 95-105 mm, sash pushed open against the block,
              released (no gripper within 3 cm), still 1 s.

    Returns:
        (score, success, reason)
    """
    # Gate 1: frame stability
    frame_drift = compute_frame_drift(frame_pos)
    if frame_drift > MAX_FRAME_DRIFT_GATE_M:
        return 0.0, False, f"gate: window frame drifted {frame_drift * 1000:.1f} mm (> 5 mm)"

    # Gate 2: part left table
    if block_pos[2] < TABLE_TOP - 0.05:
        return 0.0, False, "gate: stop block fell below table level"

    lifted = is_block_lifted(block_pos)
    if not lifted:
        return 0.0, False, "initial/idle: block resting on pad"

    seated, hole_idx, seat_msg = is_block_seated_in_track(block_pos, frame_pos)
    if not seated:
        return 0.25, False, f"block lifted ({seat_msg})"

    # Block is seated in a track hole!
    # Gripper clearance gate for 1.0 (if provided)
    gripper_ok = (gripper_clearance_m is None) or (gripper_clearance_m >= GRIPPER_CLEARANCE_MIN_M)

    # Check 1.0 condition: target hole (index 1 = 100 mm opening), sash open 95-105 mm, still 1 s
    is_target_hole = (hole_idx == TARGET_HOLE_INDEX)
    sash_in_target_window = (TARGET_OPENING_MIN_M <= sash_travel <= TARGET_OPENING_MAX_M)

    if is_target_hole and sash_in_target_window and gripper_ok and resting:
        return (
            1.0,
            True,
            f"block seated at 100 mm hole, sash open {sash_travel * 1000:.1f} mm (95-105 mm), released, resting",
        )

    # 0.75 condition: the sash was pushed open and is stopped by the block (front face touching the block, short of
    # its own 120 mm end stop)
    sash_front_gap = abs(sash_travel - (block_pos[1] - frame_pos[1] + 0.015))
    if sash_front_gap <= SASH_TOUCH_TOL_M and 0.02 <= sash_travel <= MAX_OPENING_LADDER_075_M:
        return (
            0.75,
            False,
            f"block seated at hole {hole_idx}, sash stopped by block at {sash_travel * 1000:.1f} mm",
        )

    # 0.50: seated in a track hole, sash not stopped by it
    return 0.50, False, f"block seated in track hole {hole_idx} (peg >= 4 mm in)"
