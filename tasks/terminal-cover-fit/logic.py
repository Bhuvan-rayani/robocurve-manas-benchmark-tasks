from __future__ import annotations

"""Scoring logic for terminal_cover_fit (T16)."""

import math
from typing import Mapping, Sequence

from geometry import (
    BLOCK_POS_WORLD,
    COVER_NAME,
    COVER_TARGET_POS,
    GATE_BLOCK_DRIFT_MAX_M,
    GATE_MIN_Z_M,
    TABLE_TOP,
)


def evaluate_state(
    block_pos: Sequence[float],
    cover_pos: Sequence[float],
    resting: bool = True,
) -> tuple[float, bool, str]:
    drift = math.sqrt(
        (block_pos[0] - BLOCK_POS_WORLD[0]) ** 2
        + (block_pos[1] - BLOCK_POS_WORLD[1]) ** 2
        + (block_pos[2] - BLOCK_POS_WORLD[2]) ** 2
    )
    if drift > GATE_BLOCK_DRIFT_MAX_M:
        return 0.0, False, f"Gate: block moved {drift*1000:.1f} mm > 5.0 mm"

    if cover_pos[2] < GATE_MIN_Z_M:
        return 0.0, False, "Gate: cover dropped below table"

    # Step 1: lifted > 3 cm
    lifted = cover_pos[2] >= TABLE_TOP + 0.045
    # Step 2: over both terminals within 3 cm (x near 0.30, y near 0.0)
    over_terminals = (abs(cover_pos[0] - 0.30) <= 0.030) and (abs(cover_pos[1] - 0.0) <= 0.030)
    # Step 3: within 1 cm and level
    near_seat = (abs(cover_pos[0] - 0.30) <= 0.010) and (abs(cover_pos[1] - 0.0) <= 0.010) and (cover_pos[2] <= TABLE_TOP + 0.050)
    # Step 4: fully seated on block rim (within 8 mm horizontal tolerance and 3 mm vertical seating depth)
    seated = (abs(cover_pos[0] - COVER_TARGET_POS[0]) <= 0.008) and (abs(cover_pos[1] - COVER_TARGET_POS[1]) <= 0.008) and (abs(cover_pos[2] - COVER_TARGET_POS[2]) <= 0.003)

    if not lifted and not over_terminals:
        return 0.0, False, "Cover resting at start"
    if not over_terminals:
        return 0.25, False, "Cover lifted > 3 cm"
    if not near_seat:
        return 0.50, False, "Cover over terminals within 3 cm"
    if not seated:
        return 0.75, False, "Cover within 1 cm of seat"

    if resting:
        return 1.00, True, "Cover seated on block and settled"
    return 0.75, False, "Cover seated, settling..."
