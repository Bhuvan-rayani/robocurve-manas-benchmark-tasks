from __future__ import annotations

"""Pure-Python scoring logic for wheel_axle_lynch_pin (T18)."""

import math
from typing import Mapping, Sequence

from geometry import (
    GATE_MIN_Z_M,
    GATE_STAND_DRIFT_MAX_M,
    PIN_NAME,
    PIN_START_POS,
    PIN_TARGET_POS,
    STAND_POS_WORLD,
    WHEEL_NAME,
    WHEEL_START_POS,
    WHEEL_TARGET_POS,
)


def evaluate_state(
    stand_pos: Sequence[float],
    wheel_pos: Sequence[float],
    pin_pos: Sequence[float],
    resting: bool = True,
) -> tuple[float, bool, str]:
    drift = math.sqrt(
        (stand_pos[0] - STAND_POS_WORLD[0]) ** 2
        + (stand_pos[1] - STAND_POS_WORLD[1]) ** 2
        + (stand_pos[2] - STAND_POS_WORLD[2]) ** 2
    )
    if drift > GATE_STAND_DRIFT_MAX_M:
        return 0.0, False, f"Gate: stand moved {drift*1000:.1f} mm > 5.0 mm"

    if wheel_pos[2] < GATE_MIN_Z_M or pin_pos[2] < GATE_MIN_Z_M:
        return 0.0, False, "Gate: component dropped below table"

    # Step 1: wheel lifted
    wheel_lifted = wheel_pos[2] >= WHEEL_START_POS[2] + 0.030
    # Step 2: wheel on axle >= 2 cm (x near 0.30, y >= -0.14, z near 0.08)
    wheel_on_axle = (abs(wheel_pos[0] - 0.30) <= 0.030) and (abs(wheel_pos[2] - (0.7475 + 0.080)) <= 0.020) and (wheel_pos[1] >= -0.140)
    # Step 3: wheel fully on against stop (y near -0.060)
    wheel_seated = wheel_on_axle and (abs(wheel_pos[1] - (-0.060)) <= 0.015)
    # Step 4: pin through cross hole (x near 0.30, y near -0.140, z near target)
    pin_inserted = (abs(pin_pos[0] - 0.30) <= 0.015) and (abs(pin_pos[1] - (-0.140)) <= 0.015) and (abs(pin_pos[2] - PIN_TARGET_POS[2]) <= 0.020)

    if not wheel_lifted and not wheel_on_axle:
        return 0.0, False, "Wheel at start"
    if not wheel_on_axle:
        return 0.25, False, "Wheel lifted"
    if not wheel_seated:
        return 0.50, False, "Wheel on axle >= 2 cm"
    if not pin_inserted:
        return 0.75, False, "Wheel fully on axle, pin not yet inserted"

    if resting:
        return 1.00, True, "Wheel fully seated and locked with lynch pin"
    return 0.75, False, "Wheel and pin in place, settling..."
