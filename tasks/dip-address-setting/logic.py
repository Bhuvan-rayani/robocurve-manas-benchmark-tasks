"""Pure-Python logic and scoring computation for dip_address_setting."""

from __future__ import annotations

import math
from typing import Mapping

from geometry import (
    BUTTON_NAME,
    BUTTON_PRESS_THRESHOLD_M,
    KNOB_NAMES,
    MAX_MODULE_DRIFT_GATE_M,
    MAX_MODULE_DRIFT_SCORE_M,
    MODULE_POS_WORLD,
    SWITCH_FLICK_THRESHOLD_M,
    TARGET_PATTERN,
)


def compute_module_drift(pos: tuple[float, float, float]) -> float:
    """Euclidean distance in XY plane from initial module position."""
    dx = pos[0] - MODULE_POS_WORLD[0]
    dy = pos[1] - MODULE_POS_WORLD[1]
    return math.hypot(dx, dy)


def read_switches(sliders: Mapping[str, float]) -> tuple[int, ...]:
    """Returns a tuple of 0 (DOWN) or 1 (UP) for each of the 4 knobs.

    Complement start layout:
      - addr_knob_1: starts DOWN, axis +X. Flicked UP when disp >= threshold.
      - addr_knob_2: starts UP, axis -X. Pushed DOWN when disp >= threshold.
      - addr_knob_3: starts UP, axis -X. Pushed DOWN when disp >= threshold.
      - addr_knob_4: starts DOWN, axis +X. Flicked UP when disp >= threshold.
    """
    k1_disp = sliders.get(KNOB_NAMES[0], 0.0)
    k2_disp = sliders.get(KNOB_NAMES[1], 0.0)
    k3_disp = sliders.get(KNOB_NAMES[2], 0.0)
    k4_disp = sliders.get(KNOB_NAMES[3], 0.0)

    s1 = 1 if abs(k1_disp) >= SWITCH_FLICK_THRESHOLD_M else 0
    s2 = 0 if abs(k2_disp) >= SWITCH_FLICK_THRESHOLD_M else 1
    s3 = 0 if abs(k3_disp) >= SWITCH_FLICK_THRESHOLD_M else 1
    s4 = 1 if abs(k4_disp) >= SWITCH_FLICK_THRESHOLD_M else 0

    return (s1, s2, s3, s4)


def count_correct_switches(switches: tuple[int, ...]) -> int:
    """Number of switches matching TARGET_PATTERN (1, 0, 0, 1)."""
    return sum(1 for actual, target in zip(switches, TARGET_PATTERN) if actual == target)


def is_button_pressed(sliders: Mapping[str, float]) -> bool:
    """Check if the commit button is depressed past the threshold."""
    disp = sliders.get(BUTTON_NAME, 0.0)
    return abs(disp) >= BUTTON_PRESS_THRESHOLD_M


def evaluate_state(
    module_pos: tuple[float, float, float],
    sliders: Mapping[str, float],
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Evaluate current state: returns (score, success, reason).

    Gates:
      - Gate 1: 0.0 if module drifted > 5 cm.
      - Gate 2: 0.0 if commit button pressed while pattern is incomplete (< 4 correct).
      - Ladder threshold: 0.0 if module drifted > 15 mm.

    Score ladder:
      - 0.00: 0 correct switches (initial state).
      - 0.25: >= 1 switch correct.
      - 0.50: >= 2 switches correct (also covers 3 correct).
      - 0.75: all 4 switches correct (matches target pattern).
      - 1.00: all 4 switches correct, commit button pressed >= 6.4 mm, stationary.
    """
    drift = compute_module_drift(module_pos)

    # Gate 1: module moved > 5 cm
    if drift > MAX_MODULE_DRIFT_GATE_M:
        return 0.0, False, f"gate: module drifted {drift * 100:.1f} cm (> 5 cm)"

    button_down = is_button_pressed(sliders)
    switches = read_switches(sliders)
    n_correct = count_correct_switches(switches)

    pattern_matched = (n_correct == 4)

    # Gate 2: commit button pressed with incorrect pattern gives 0
    if button_down and not pattern_matched:
        return 0.0, False, "gate: commit button pressed with incorrect switch pattern"

    # Score ladder requires module drift <= 15 mm
    if drift > MAX_MODULE_DRIFT_SCORE_M:
        return 0.0, False, f"module drifted {drift * 1000:.1f} mm (> 15 mm ladder threshold)"

    # Level 1.00: full success
    if pattern_matched and button_down and resting:
        return 1.0, True, "all 4 switches match target pattern and commit button pressed"

    # Level 0.75: all 4 switches match, button not yet pressed
    if pattern_matched:
        return 0.75, False, "all 4 switches match target pattern (1, 0, 0, 1)"

    # Level 0.50: 2 or 3 switches correct
    if n_correct >= 2:
        return 0.50, False, f"{n_correct} of 4 switches correct"

    # Level 0.25: 1 switch correct
    if n_correct >= 1:
        return 0.25, False, "1 of 4 switches correct"

    # 0 correct (start state)
    return 0.0, False, "initial state: 0 of 4 switches correct"
