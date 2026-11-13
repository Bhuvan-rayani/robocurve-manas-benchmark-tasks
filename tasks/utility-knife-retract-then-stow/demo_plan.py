"""Demo plan for utility_knife_retract_then_stow: one hand slides the blade home with the slider button, then lifts the knife
into its holster. The whole layout sits in front of the right arm; the left arm stays at its ready pose."""

from __future__ import annotations

import os

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN
from yam_arena.demo import Waypoint

from geometry import KNIFE_START_POS, L_READY, POCKET_CENTRE, R_READY, SLIDER_AT, BUTTON_BOX, SLIDER_TRAVEL_M, TABLE_TOP

# yam_arena: yaw 0 closes the fingers along world y, yaw pi/2 along world x. Finger commands open NEGATIVE.
BUTTON_OPEN = -0.020   # yaw 0: fingers 20 mm out each side along y, around the 20 mm long slider button
HANDLE_OPEN = -0.026   # yaw pi/2: fingers 26 mm out each side along x, 10 mm clear of the 32 mm wide handle
HANDLE_YAW = 1.5708

KX, KY = KNIFE_START_POS[0], KNIFE_START_POS[1]
BUTTON_Y = KY + SLIDER_AT[1] + BUTTON_BOX[0][1]          # slider button centre at rest (knife y -0.060)
BUTTON_HOME_Y = BUTTON_Y + SLIDER_TRAVEL_M + 0.012       # 25 mm stroke, commanded 12 mm past the stop
GRIP_Y = KY + 0.020                                      # handle grip 2 cm behind the knife centre, clear of the slider
PX, PY = POCKET_CENTRE
STOW_Y = GRIP_Y + (PY - KY) - 0.009   # GPU r80: the knife shifts about 9 mm toward +y while the blade is pushed, so the carry is aimed 9 mm back


def plans() -> dict[str, list[Waypoint]]:
    """Return waypoint lists for left and right arms."""
    top = TABLE_TOP
    if os.getenv("SETTLE_ONLY"):
        return {
            "left": [Waypoint(8.0, L_READY, FINGER_OPEN, "settle left", 0.0)],
            "right": [Waypoint(8.0, R_READY, FINGER_OPEN, "settle right", 0.0)],
        }

    retract = [
        # Hover over the slider button until the arm has converged, then straight down around it
        Waypoint(2.5, (KX, BUTTON_Y, top + 0.100), BUTTON_OPEN, "over slider button", 0.0),
        Waypoint(2.0, (KX, BUTTON_Y, top + 0.100), BUTTON_OPEN, "settle over slider button", 0.0),
        Waypoint(2.0, (KX, BUTTON_Y, top + 0.050), BUTTON_OPEN, "around slider button", 0.0),
        Waypoint(0.8, (KX, BUTTON_Y, top + 0.050), FINGER_CLOSED, "pinch slider button", 0.0),
        # Slide the blade home (25 mm to the stop) and let go: the friction-lock slide stays there
        Waypoint(4.0, (KX, BUTTON_HOME_Y, top + 0.050), FINGER_CLOSED, "slide blade home", 0.0),
        Waypoint(0.8, (KX, BUTTON_HOME_Y, top + 0.050), FINGER_CLOSED, "hold at stop", 0.0),
        Waypoint(0.6, (KX, BUTTON_HOME_Y, top + 0.050), BUTTON_OPEN, "let go of button", 0.0),
        Waypoint(1.0, (KX, BUTTON_HOME_Y, top + 0.100), BUTTON_OPEN, "lift off button", 0.0),
    ]
    stow = [
        # Take the knife across its handle, lift it, and set it into the holster pocket
        Waypoint(2.0, (KX, GRIP_Y, top + 0.100), HANDLE_OPEN, "over handle", HANDLE_YAW),
        Waypoint(1.5, (KX, GRIP_Y, top + 0.100), HANDLE_OPEN, "settle over handle", HANDLE_YAW),
        Waypoint(2.0, (KX, GRIP_Y, top + 0.035), HANDLE_OPEN, "down beside handle", HANDLE_YAW),
        Waypoint(0.8, (KX, GRIP_Y, top + 0.035), FINGER_CLOSED, "grip handle", HANDLE_YAW),
        Waypoint(1.5, (KX, GRIP_Y, top + 0.100), FINGER_CLOSED, "lift knife", HANDLE_YAW),
        Waypoint(2.5, (PX, STOW_Y, top + 0.100), FINGER_CLOSED, "carry over holster", HANDLE_YAW),
        Waypoint(1.5, (PX, STOW_Y, top + 0.055), FINGER_CLOSED, "lower over pocket", HANDLE_YAW),
        Waypoint(0.8, (PX, STOW_Y, top + 0.055), HANDLE_OPEN, "let go into pocket", HANDLE_YAW),
        Waypoint(1.0, (PX, STOW_Y, top + 0.120), HANDLE_OPEN, "lift above holster", HANDLE_YAW),
        Waypoint(2.0, R_READY, FINGER_OPEN, "withdraw", 0.0),
        Waypoint(1.5, R_READY, FINGER_OPEN, "stillness wait", 0.0),
    ]
    # Ablation: skip the retract and try to stow the knife with the blade out
    right = stow if os.getenv("ABLATION") else retract + stow
    total = sum(w.duration for w in right)
    return {"left": [Waypoint(total, L_READY, FINGER_OPEN, "left idle at ready", 0.0)], "right": right}
