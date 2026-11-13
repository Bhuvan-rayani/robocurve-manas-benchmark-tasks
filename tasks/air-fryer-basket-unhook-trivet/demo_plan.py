"""Demo plan for air_fryer_basket_release_button_v2: one hand pinches the handle across its release button, which frees the
catches, lifts the basket out of the drawer and sets it on the mat. The left arm stays at its ready pose."""

from __future__ import annotations

import os

from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN
from yam_arena.demo import Waypoint

from geometry import L_READY, R_READY, TABLE_TOP

# yam_arena: yaw 0 closes the fingers along world y, yaw pi/2 along world x. Finger commands open NEGATIVE.
GRIP_OPEN = -0.034    # each finger 34 mm out along x: around the 45 mm from the release cap face to the bar's back face
RELEASE_OPEN = -0.021  # to let go: a 42 mm span just clears the held bar (the closed grip is about 35 mm) and keeps the rear pad outer edge 5 mm inside the hot front wall's zone (GPU r83: 24 mm touched it as the hand rose)
GRIP_YAW = 1.5708     # right fingers close along x: the front finger presses the cap in as the grip closes on the bar
MAT_YAW = 1.40        # over the mat the right wrist reaches its joint6 limit at pi/2 (9 deg IK error offline); 80 deg is exact
CAP_GRIP = (0.2195, -0.120)    # centred between the pressed cap face (x 0.204) and the bar's back face (x 0.235), on the cap
BAR_ONLY_GRIP = (0.2225, -0.195)  # ablation: the bar end, 25 mm beyond the cap edge (the catches stay hooked)
PINCH_Z = 0.095       # tool point above the table: pads on the cap and bar (z 7.0 to 9.5 cm), the tips 6 mm above the drawer front's hot zone
LIFT_Z = 0.175        # basket floor rises 8 cm, past the drawer walls
MAT_GRIP = (0.2195, -0.410)    # the grip is at the handle centre, so the basket centre lands on the mat centre (0.384, -0.410)
SET_Z = 0.065         # basket floor 5 mm above the mat top when let go


def plans() -> dict[str, list[Waypoint]]:
    """Return waypoint lists for left and right arms."""
    top = TABLE_TOP
    if os.getenv("SETTLE_ONLY"):
        return {
            "left": [Waypoint(8.0, L_READY, FINGER_OPEN, "settle", 0.0)],
            "right": [Waypoint(8.0, R_READY, FINGER_OPEN, "settle", 0.0)],
        }

    gx, gy = BAR_ONLY_GRIP if os.getenv("ABLATION") else CAP_GRIP
    mx, my = MAT_GRIP
    right = [
        # Hover over the handle, clear of everything, until the arm has converged; then straight down
        Waypoint(3.0, (gx, gy, top + 0.150), GRIP_OPEN, "over handle", GRIP_YAW),
        Waypoint(2.0, (gx, gy, top + 0.150), GRIP_OPEN, "settle over handle", GRIP_YAW),
        Waypoint(2.0, (gx, gy, top + PINCH_Z), GRIP_OPEN, "down around handle", GRIP_YAW),
        # Close: the front finger pushes the release cap in to its stop (catches clear), the back finger takes the bar
        Waypoint(1.2, (gx, gy, top + PINCH_Z), FINGER_CLOSED, "pinch handle and release", GRIP_YAW),
        Waypoint(0.8, (gx, gy, top + PINCH_Z), FINGER_CLOSED, "hold", GRIP_YAW),
        # Lift straight up out of the drawer, then carry to the mat and set down
        Waypoint(4.0, (gx, gy, top + LIFT_Z), FINGER_CLOSED, "lift out of drawer", GRIP_YAW),
        Waypoint(4.0, (mx, my, top + LIFT_Z), FINGER_CLOSED, "carry over mat", MAT_YAW),
        Waypoint(2.5, (mx, my, top + SET_Z), FINGER_CLOSED, "lower onto mat", MAT_YAW),
        Waypoint(1.0, (mx - 0.004, my, top + SET_Z), RELEASE_OPEN, "let go", MAT_YAW),
        Waypoint(2.0, (mx - 0.004, my, top + 0.140), RELEASE_OPEN, "lift above basket", MAT_YAW),
        Waypoint(2.0, R_READY, FINGER_OPEN, "withdraw", 0.0),
        Waypoint(1.5, R_READY, FINGER_OPEN, "stillness wait", 0.0),
    ]
    total = sum(w.duration for w in right)
    left = [Waypoint(total, L_READY, FINGER_OPEN, "left idle at ready", 0.0)]
    return {"left": left, "right": right}
