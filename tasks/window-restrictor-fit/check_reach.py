"""Offline IK reach check for all demo waypoints in window_restrictor_fit."""

from __future__ import annotations

import pathlib
import sys

import numpy as np

# Setup paths
_TASK_DIR = pathlib.Path(__file__).resolve().parent
_UPSTREAM = (
    _TASK_DIR.parents[2]
    / "robocurve-windows-transfer-2026-11-05"
    / "project"
    / "robocurve"
    / "tmp"
    / "yam-upstream"
)
for p in (_TASK_DIR, _UPSTREAM):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from demo_plan import plans
from yam_arena import ik
from yam_arena.constants import LEFT_BASE_POS, READY, RIGHT_BASE_POS
from yam_arena.demo import grip_rotation


def check_plan(name: str, waypoints, base_pos, q_init=READY) -> tuple[float, float, float]:
    worst_pe_mm = 0.0
    worst_re_deg = 0.0
    min_margin_rad = float("inf")

    q = np.array(q_init, dtype=float)
    for i, w in enumerate(waypoints):
        target_pos = np.asarray(w.pos, dtype=float)
        rot_mat = grip_rotation(w.yaw)
        quat_xyzw = ik.matrix_to_quat_xyzw(rot_mat)

        q, pe, re = ik.solve(target_pos, quat_xyzw, q, base_pos=base_pos, iters=150)
        pe_mm = pe * 1000.0
        re_deg = float(np.degrees(re))
        worst_pe_mm = max(worst_pe_mm, pe_mm)
        worst_re_deg = max(worst_re_deg, re_deg)

        margin = np.minimum(q - ik.LOWER, ik.UPPER - q).min()
        min_margin_rad = min(min_margin_rad, float(margin))

        assert pe_mm < 1.0, f"Waypoint {i} ({w.label}) IK position error too large: {pe_mm:.3f} mm (must be < 1 mm)"
        assert margin >= 0.02, f"Waypoint {i} ({w.label}) joint limit margin too small: {margin:.4f} rad (must be >= 0.02 rad)"

    return worst_pe_mm, worst_re_deg, min_margin_rad


def main():
    p = plans()
    print("Checking IK reach for window_restrictor_fit demo plan...")
    l_pe, l_re, l_margin = check_plan("left", p["left"], LEFT_BASE_POS)
    r_pe, r_re, r_margin = check_plan("right", p["right"], RIGHT_BASE_POS)

    print(f"Left arm: worst pe = {l_pe:.3f} mm, worst re = {l_re:.3f} deg, min margin = {l_margin:.4f} rad")
    print(f"Right arm: worst pe = {r_pe:.3f} mm, worst re = {r_re:.3f} deg, min margin = {r_margin:.4f} rad")

    if l_margin < 0.02 or r_margin < 0.02 or l_pe >= 1.0 or r_pe >= 1.0:
        print("FAILED: IK reach criteria not met!")
        sys.exit(1)
    else:
        print("SUCCESS: all waypoints reachable with pe < 1 mm and joint margin >= 0.02 rad.")


if __name__ == "__main__":
    main()
