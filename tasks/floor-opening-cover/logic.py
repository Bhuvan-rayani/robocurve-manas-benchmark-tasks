"""Pure-Python logic and scoring computation for floor_opening_cover."""

from __future__ import annotations

import math
from typing import Sequence

from geometry import (
    BOARD_POS_WORLD,
    BOARD_TOP_Z,
    MAX_BOARD_DRIFT_M,
    MAX_PLATE_TILT_DEG,
    MIN_OVERHANG_M,
    MIN_PLATE_LIFT_M,
    MIN_SEATED_DEPTH_M,
    OPENING_X_MAX,
    OPENING_X_MIN,
    OPENING_Y_MAX,
    OPENING_Y_MIN,
    PIN_HALF_Z,
    PLATE_GOAL_POS,
    PLATE_HALF_X,
    PLATE_HALF_Y,
    PLATE_HALF_Z,
    PLATE_START_POS,
    SLOT_A_POS,
    SLOT_B_POS,
    TABLE_TOP,
)


def compute_drift(pos: Sequence[float], origin: Sequence[float]) -> float:
    """Euclidean distance in XY plane."""
    return math.hypot(pos[0] - origin[0], pos[1] - origin[1])


def compute_tilt_deg(quat: Sequence[float] | None) -> float:
    """Tilt angle in degrees from vertical +z axis for a quaternion (x, y, z, w)."""
    if quat is None:
        return 0.0
    qx, qy, qz, qw = quat[0], quat[1], quat[2], quat[3]
    # Normal vector rotated: R * [0, 0, 1]^T -> z-component is 1 - 2*(qx^2 + qy^2)
    z_comp = 1.0 - 2.0 * (qx * qx + qy * qy)
    z_comp = max(-1.0, min(1.0, z_comp))
    return math.degrees(math.acos(z_comp))


def compute_overhang(plate_pos: Sequence[float]) -> tuple[float, float, float, float, float]:
    """Compute overhang of the plate over the 16x16 cm opening on all four sides.

    Returns (min_overhang, overhang_west, overhang_east, overhang_south, overhang_north).
    """
    px, py = plate_pos[0], plate_pos[1]
    plate_x_min = px - PLATE_HALF_X
    plate_x_max = px + PLATE_HALF_X
    plate_y_min = py - PLATE_HALF_Y
    plate_y_max = py + PLATE_HALF_Y

    west = OPENING_X_MIN - plate_x_min
    east = plate_x_max - OPENING_X_MAX
    south = OPENING_Y_MIN - plate_y_min
    north = plate_y_max - OPENING_Y_MAX

    min_overhang = min(west, east, south, north)
    return min_overhang, west, east, south, north


def is_in_opening(pos: Sequence[float]) -> bool:
    """Check if an XY coordinate lies within the 16x16 cm opening."""
    return OPENING_X_MIN <= pos[0] <= OPENING_X_MAX and OPENING_Y_MIN <= pos[1] <= OPENING_Y_MAX


def is_pin_seated(
    pin_pos: Sequence[float],
    slot_pos: Sequence[float],
    pin_quat: Sequence[float] | None = None,
) -> tuple[bool, float]:
    """Check if a wedge pin is seated in a designated slot (>= 10 mm depth)."""
    dx = abs(pin_pos[0] - slot_pos[0])
    dy = abs(pin_pos[1] - slot_pos[1])
    # Slot is 26x26 mm, pin is 12x12 mm: pin centre within 10 mm of the slot centre
    if dx > 0.016 or dy > 0.016:
        return False, 0.0

    if pin_quat is not None and compute_tilt_deg(pin_quat) > 20.0:
        return False, 0.0

    pin_bottom_z = pin_pos[2] - PIN_HALF_Z
    seated_depth = BOARD_TOP_Z - pin_bottom_z

    # Seated depth >= 10 mm and pin bottom not through table
    if seated_depth >= (MIN_SEATED_DEPTH_M - 0.0005) and pin_bottom_z >= (TABLE_TOP + 0.020):
        return True, seated_depth

    return False, max(0.0, seated_depth)


def evaluate_state(
    board_pos: Sequence[float],
    plate_pos: Sequence[float],
    pin_a_pos: Sequence[float],
    pin_b_pos: Sequence[float],
    plate_quat: Sequence[float] | None = None,
    pin_a_quat: Sequence[float] | None = None,
    pin_b_quat: Sequence[float] | None = None,
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Evaluate floor opening cover task state against gates and ladder."""
    # Gate 1: Floor board moved > 5 mm
    board_drift = compute_drift(board_pos, BOARD_POS_WORLD)
    if board_drift > MAX_BOARD_DRIFT_M:
        return 0.0, False, f"gate: floor board moved {board_drift * 1000:.1f} mm (> 5 mm)"

    # Gate 2: Any object fell off table
    if (
        plate_pos[2] < (TABLE_TOP - 0.010)
        or pin_a_pos[2] < (TABLE_TOP - 0.010)
        or pin_b_pos[2] < (TABLE_TOP - 0.010)
    ):
        return 0.0, False, "gate: an object fell off the table"

    # Gate 3: Plate or pin ends below the board top inside the opening (pit hazard)
    plate_top_z = plate_pos[2] + PLATE_HALF_Z
    if is_in_opening(plate_pos) and plate_top_z < (BOARD_TOP_Z - 0.005):
        return 0.0, False, "gate: cover plate fell into floor opening below board top"

    pin_a_top_z = pin_a_pos[2] + PIN_HALF_Z
    if is_in_opening(pin_a_pos) and pin_a_top_z < (BOARD_TOP_Z - 0.005):
        return 0.0, False, "gate: wedge pin a fell into floor opening below board top"

    pin_b_top_z = pin_b_pos[2] + PIN_HALF_Z
    if is_in_opening(pin_b_pos) and pin_b_top_z < (BOARD_TOP_Z - 0.005):
        return 0.0, False, "gate: wedge pin b fell into floor opening below board top"

    # Ladder metrics
    plate_lift = plate_pos[2] - PLATE_START_POS[2]
    plate_lifted = plate_lift >= (MIN_PLATE_LIFT_M - 0.001)

    min_overhang, _, _, _, _ = compute_overhang(plate_pos)
    plate_resting_on_board = abs(plate_pos[2] - PLATE_GOAL_POS[2]) <= 0.015
    plate_over_opening = (min_overhang >= (MIN_OVERHANG_M - 0.001)) and plate_resting_on_board

    # Check pin seating in both slots (either pin in either slot)
    a_in_slot_a, _ = is_pin_seated(pin_a_pos, SLOT_A_POS, pin_a_quat)
    b_in_slot_b, _ = is_pin_seated(pin_b_pos, SLOT_B_POS, pin_b_quat)
    b_in_slot_a, _ = is_pin_seated(pin_b_pos, SLOT_A_POS, pin_b_quat)
    a_in_slot_b, _ = is_pin_seated(pin_a_pos, SLOT_B_POS, pin_a_quat)

    both_pins_seated = (a_in_slot_a and b_in_slot_b) or (b_in_slot_a and a_in_slot_b)
    one_pin_seated = both_pins_seated or a_in_slot_a or b_in_slot_b or b_in_slot_a or a_in_slot_b

    plate_tilt = compute_tilt_deg(plate_quat) if plate_quat is not None else 0.0
    plate_flat = plate_tilt <= MAX_PLATE_TILT_DEG

    # Ladder 1.0: Both pins seated >= 10 mm, plate flat within 3 degrees, resting 1 s
    if plate_over_opening and both_pins_seated and plate_flat and resting:
        return 1.0, True, "cover plate over opening, both wedge pins seated >= 10 mm, plate flat and resting"

    # Ladder 0.75: Plate over opening with overhang >= 20 mm + one pin seated >= 10 mm
    if plate_over_opening and one_pin_seated:
        return 0.75, False, "plate over opening with overhang >= 20 mm and one wedge pin seated >= 10 mm"

    # Ladder 0.50: Plate over opening with overhang >= 20 mm on all four sides
    if plate_over_opening:
        return 0.50, False, f"plate over opening with overhang {min_overhang * 1000:.1f} mm (>= 20 mm)"

    # Ladder 0.25: Plate lifted > 2 cm from stand
    if plate_lifted:
        return 0.25, False, f"plate lifted {plate_lift * 1000:.1f} mm (> 20 mm)"

    # Initial state
    return 0.0, False, "initial: plate on stand, pins in rack"
