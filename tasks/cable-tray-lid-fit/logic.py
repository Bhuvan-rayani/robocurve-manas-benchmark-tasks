from __future__ import annotations

"""Pure-Python evaluation logic for cable_tray_lid_fit (T13)."""

import math
from typing import Mapping, Sequence

from geometry import (
    GATE_MIN_Z_M,
    GATE_TRAY_DRIFT_MAX_M,
    LID_LEFT_NAME,
    LID_RIGHT_NAME,
    LID_TARGET_POS,
    TRAY_POS_WORLD,
)


def evaluate_state(
    tray_pos: Sequence[float],
    lids: Mapping[str, Sequence[float]],
    resting: bool = True,
) -> tuple[float, bool, str]:
    drift = math.sqrt(
        (tray_pos[0] - TRAY_POS_WORLD[0]) ** 2
        + (tray_pos[1] - TRAY_POS_WORLD[1]) ** 2
        + (tray_pos[2] - TRAY_POS_WORLD[2]) ** 2
    )
    if drift > GATE_TRAY_DRIFT_MAX_M:
        return 0.0, False, f"Gate: tray drifted {drift*1000:.1f} mm > 5.0 mm"

    pos_l = lids.get(LID_LEFT_NAME)
    pos_r = lids.get(LID_RIGHT_NAME)
    if pos_l is None or pos_r is None:
        return 0.0, False, "Lid missing"

    if pos_l[2] < GATE_MIN_Z_M or pos_r[2] < GATE_MIN_Z_M:
        return 0.0, False, "Gate: lid dropped below table"

    # Check on rails: x near 0.30, z near TABLE_TOP + 0.06
    on_rails_l = (abs(pos_l[0] - 0.30) <= 0.025) and (abs(pos_l[2] - (0.7475 + 0.0632)) <= 0.008)
    on_rails_r = (abs(pos_r[0] - 0.30) <= 0.025) and (abs(pos_r[2] - (0.7475 + 0.0632)) <= 0.008)

    if not on_rails_l and not on_rails_r:
        return 0.0, False, "Neither lid on rails"

    if on_rails_l and not on_rails_r:
        return 0.25, False, "Left lid on rails"
    if on_rails_r and not on_rails_l:
        return 0.25, False, "Right lid on rails"

    # Both on rails: check center gap
    # Target centers are +0.099 and -0.099; inner edges meet at y=0.0
    gap = abs(pos_l[1] - pos_r[1]) - 0.196
    z_diff = abs(pos_l[2] - pos_r[2])

    if gap > 0.060:
        return 0.50, False, f"Both lids on rails, gap {gap*1000:.1f} mm"

    if gap > 0.005 or z_diff > 0.003:
        return 0.75, False, f"Lids near center, gap {gap*1000:.1f} mm"

    if resting:
        return 1.00, True, "Both lids flush in middle and settled"

    return 0.75, False, "Lids flush in middle, settling..."
