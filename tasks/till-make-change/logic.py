"""Pure-Python logic and scoring computation for till_make_change."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

from geometry import (
    DRAWER_NAME,
    DRAWER_OPEN_THRESHOLD_M,
    MAX_TILL_DRIFT_M,
    TABLE_TOP,
    TARGET_CHANGE,
    TILL_POS_WORLD,
    TOKEN_A_NAMES,
    TOKEN_B_NAMES,
    TRAY_INNER_X_MAX,
    TRAY_INNER_X_MIN,
    TRAY_INNER_Y_MAX,
    TRAY_INNER_Y_MIN,
    TRAY_INNER_Z_MAX,
    SUPPLY_RADIUS_M,
    TOKEN_A_XY,
    TOKEN_B_XY,
)


def compute_drift(pos: Sequence[float], origin: Sequence[float]) -> float:
    """Euclidean distance in XY plane."""
    return math.hypot(pos[0] - origin[0], pos[1] - origin[1])


def is_in_tray(pos: Sequence[float]) -> bool:
    """Check if a point is within the customer tray cavity."""
    x, y, z = pos[0], pos[1], pos[2]
    return (
        TRAY_INNER_X_MIN <= x <= TRAY_INNER_X_MAX
        and TRAY_INNER_Y_MIN <= y <= TRAY_INNER_Y_MAX
        and (TABLE_TOP - 0.005) <= z <= TRAY_INNER_Z_MAX
    )


def is_in_supply(pos: Sequence[float], name: str = "") -> bool:
    """A token still resting at (or on) its own stack is not loose."""
    centre = TOKEN_A_XY if name in TOKEN_A_NAMES else TOKEN_B_XY
    return math.hypot(pos[0] - centre[0], pos[1] - centre[1]) <= SUPPLY_RADIUS_M and pos[2] >= (TABLE_TOP - 0.005)


def evaluate_state(
    till_pos: Sequence[float],
    drawer_slider: float,
    token_positions: Mapping[str, Sequence[float]],
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Evaluate till make change task state."""
    # Gate 1: Till moved > 5 mm
    drift = compute_drift(till_pos, TILL_POS_WORLD)
    if drift > MAX_TILL_DRIFT_M:
        return 0.0, False, f"gate: till moved {drift * 1000:.1f} mm (> 5 mm)"

    # Check tokens
    tray_total = 0
    tokens_in_tray = 0
    loose_tokens = 0

    for name, pos in token_positions.items():
        # Gate 2: token dropped off table
        if pos[2] < (TABLE_TOP - 0.020):
            return 0.0, False, f"gate: token {name} fell off table (z={pos[2]:.3f} m)"

        in_tray = is_in_tray(pos)
        in_supply = is_in_supply(pos, name)

        if in_tray:
            tokens_in_tray += 1
            if name in TOKEN_A_NAMES:
                tray_total += 1
            elif name in TOKEN_B_NAMES:
                tray_total += 2
        elif not in_supply:
            loose_tokens += 1

    # Gate 3: loose tokens on table outside its stack and the tray zeroes credit
    if loose_tokens > 0:
        return 0.0, False, f"gate: {loose_tokens} token(s) dropped loose outside its stack and the tray"

    drawer_open_dist = abs(drawer_slider)
    drawer_open = drawer_open_dist >= DRAWER_OPEN_THRESHOLD_M

    # The till rule: change can only be counted once the drawer has been pulled open (and it stays open)
    if not drawer_open:
        return 0.0, False, "initial: drawer closed, tray credit needs the drawer open"

    # Ladder 1.0: exact change (3 units) in tray, no loose tokens, resting
    if tray_total == TARGET_CHANGE and loose_tokens == 0 and resting:
        return 1.0, True, "exact change of 3 units in customer tray"

    # Ladder 0.75: tray total is 2 or 4 units
    if tray_total in (2, 4):
        return 0.75, False, f"tray total is {tray_total} units (target 3)"

    # Ladder 0.50: any token in tray
    if tokens_in_tray > 0:
        return 0.50, False, f"tray has {tokens_in_tray} token(s) totaling {tray_total} units"

    # Ladder 0.25: drawer opened >= 6 cm
    if drawer_open:
        return 0.25, False, f"drawer opened {drawer_open_dist * 100:.1f} cm (>= 6 cm)"

    # Initial state
    return 0.0, False, "initial: drawer closed, no tokens in tray"
