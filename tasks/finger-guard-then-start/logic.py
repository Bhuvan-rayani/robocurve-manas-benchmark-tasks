from __future__ import annotations

"""Scoring logic for finger_guard_then_start (T20)."""

import math
from typing import Mapping, Sequence

from geometry import GATE_MACHINE_DRIFT_MAX_M, MACHINE_POS_WORLD


def evaluate_state(
    machine_pos: Sequence[float],
    guard_travel_m: float,
    button_press_m: float,
    resting: bool = True,
) -> tuple[float, bool, str]:
    drift = math.sqrt(
        (machine_pos[0] - MACHINE_POS_WORLD[0]) ** 2
        + (machine_pos[1] - MACHINE_POS_WORLD[1]) ** 2
        + (machine_pos[2] - MACHINE_POS_WORLD[2]) ** 2
    )
    if drift > GATE_MACHINE_DRIFT_MAX_M:
        return 0.0, False, f"Gate: machine moved {drift*1000:.1f} mm > 5.0 mm"

    # Interlock check: if button pressed while guard open < 12 cm -> fault
    guard_closed_12 = guard_travel_m >= 0.120
    guard_closed_6 = guard_travel_m >= 0.060
    button_pressed = button_press_m >= 0.0064

    if button_pressed and not guard_closed_12:
        return 0.25, False, "Fault: button pressed with guard open (capped at 0.25)"

    if not guard_closed_6:
        return 0.0, False, f"Guard closed {guard_travel_m*100:.1f} cm < 6 cm"
    if not guard_closed_12:
        return 0.25, False, f"Guard closed {guard_travel_m*100:.1f} cm >= 6 cm"
    if not button_pressed:
        return 0.50, False, "Guard fully closed >= 12 cm, waiting for button press"

    if resting:
        return 1.00, True, "Button pressed >= 6.4 mm while guard closed, settled"
    return 0.75, False, "Button pressed while guard closed, settling..."
