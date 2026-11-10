from __future__ import annotations

"""Pure-Python scoring logic for cordon_bar_walkway (T26)."""

import math
from typing import Sequence

from geometry import (
    BAR_START_POS,
    BAR_TARGET_POS,
    GATE_MIN_Z_M,
    GATE_POST_DRIFT_MAX_M,
    POST_A_POS_WORLD,
    POST_B_POS_WORLD,
)


def evaluate_state(
    post_a_pos: Sequence[float],
    post_b_pos: Sequence[float],
    bar_pos: Sequence[float],
    resting: bool = True,
) -> tuple[float, bool, str]:
    # Gate 1: Post A drift
    drift_a = math.sqrt(
        (post_a_pos[0] - POST_A_POS_WORLD[0]) ** 2
        + (post_a_pos[1] - POST_A_POS_WORLD[1]) ** 2
        + (post_a_pos[2] - POST_A_POS_WORLD[2]) ** 2
    )
    if drift_a > GATE_POST_DRIFT_MAX_M:
        return 0.0, False, f"Gate: post A moved {drift_a*1000:.1f} mm > 5.0 mm"

    # Gate 2: Post B drift
    drift_b = math.sqrt(
        (post_b_pos[0] - POST_B_POS_WORLD[0]) ** 2
        + (post_b_pos[1] - POST_B_POS_WORLD[1]) ** 2
        + (post_b_pos[2] - POST_B_POS_WORLD[2]) ** 2
    )
    if drift_b > GATE_POST_DRIFT_MAX_M:
        return 0.0, False, f"Gate: post B moved {drift_b*1000:.1f} mm > 5.0 mm"

    # Gate 3: Drop below table
    if bar_pos[2] < GATE_MIN_Z_M:
        return 0.0, False, "Gate: component dropped below table"

    # Step 1: Bar lifted off staging pad
    bar_lifted = bar_pos[2] >= BAR_START_POS[2] + 0.04

    # Step 2: One end resting in cradle (asymmetric y or height near cradle)
    near_cradle_x = abs(bar_pos[0] - BAR_TARGET_POS[0]) <= 0.03
    near_cradle_z = abs(bar_pos[2] - BAR_TARGET_POS[2]) <= 0.03
    one_cradle_seated = near_cradle_x and near_cradle_z and (abs(bar_pos[1]) > 0.03)

    # Step 3: Bar resting in both cradles, but slightly offset
    both_cradles_near = (
        near_cradle_x
        and near_cradle_z
        and (abs(bar_pos[1] - BAR_TARGET_POS[1]) <= 0.03)
    )

    # Step 4: Bar securely centered and level in both cradles
    both_cradles_seated = (
        abs(bar_pos[0] - BAR_TARGET_POS[0]) <= 0.015
        and abs(bar_pos[1] - BAR_TARGET_POS[1]) <= 0.015
        and abs(bar_pos[2] - BAR_TARGET_POS[2]) <= 0.015
    )

    if not bar_lifted and not both_cradles_near:
        return 0.0, False, "Bar at initial staging"
    if not one_cradle_seated and not both_cradles_near:
        return 0.25, False, "Bar lifted from pad"
    if not both_cradles_near:
        return 0.50, False, "Bar resting in one post cradle"
    if not both_cradles_seated:
        return 0.75, False, "Bar resting near both cradles with minor offset"

    if resting:
        return 1.00, True, "Bar securely resting in both cradles"
    return 0.75, False, "Bar in cradles; awaiting settling"
