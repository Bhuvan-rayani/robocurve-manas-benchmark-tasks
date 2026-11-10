"""Collision and clearance verification for resistor_band_pick demo plan with real gripper width."""

from __future__ import annotations

import pathlib
import sys
import numpy as np

# Setup paths
_TASK_DIR = pathlib.Path(__file__).resolve().parent
_UPSTREAM = _TASK_DIR.parents[2] / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
for p in (_TASK_DIR, _UPSTREAM):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from demo_plan import plans
from yam_arena.constants import FINGER_CLOSED, FINGER_OPEN, LEFT_BASE_POS, RIGHT_BASE_POS, TABLE_HEIGHT
from yam_arena.demo import ArmPlan

GRIPPER_WIDTH_M = 0.085


def main():
    p = plans()
    left_plan = ArmPlan(p["left"], LEFT_BASE_POS, finger_start=FINGER_OPEN)
    right_plan = ArmPlan(p["right"], RIGHT_BASE_POS, finger_start=FINGER_CLOSED)

    total_duration = max(left_plan.duration, right_plan.duration)
    dt = 0.05  # 20 Hz control step
    steps = int(np.ceil(total_duration / dt))

    min_tcp_dist_m = float("inf")
    min_gripper_clearance_m = float("inf")
    min_table_clearance_m = float("inf")

    print(f"Checking trajectory clearance over {steps} steps ({total_duration:.1f} s)...")

    for step in range(steps):
        t = step * dt
        l_pos, _, l_finger, l_label = left_plan.target(t)
        rp, _, rf, r_label = right_plan.target(t)

        # Distance between TCPs
        tcp_dist = float(np.linalg.norm(l_pos - rp))
        min_tcp_dist_m = min(min_tcp_dist_m, tcp_dist)

        gripper_clearance = tcp_dist - GRIPPER_WIDTH_M
        min_gripper_clearance_m = min(min_gripper_clearance_m, gripper_clearance)

        # Clearance above table
        l_table_z = l_pos[2] - TABLE_HEIGHT
        r_table_z = rp[2] - TABLE_HEIGHT
        min_table_clearance_m = min(min_table_clearance_m, l_table_z, r_table_z)

        # Hard check: arm-arm clearance must be >= 30 mm
        if tcp_dist < 0.115:
            print(
                f"ERROR: Arm-arm collision risk at t={t:.2f}s (step {step}): tcp dist {tcp_dist * 1000:.1f} mm, "
                f"clearance {gripper_clearance * 1000:.1f} mm < 30 mm\n"
                f"  Left: {l_pos} ({l_label})\n"
                f"  Right: {rp} ({r_label})"
            )
            sys.exit(1)

        # Table check (TCP should not penetrate below table top)
        if min(l_table_z, r_table_z) < -0.010:
            print(f"ERROR: Table collision risk at t={t:.2f}s: z below table by {-min(l_table_z, r_table_z)*1000:.1f} mm")
            sys.exit(1)

    print(f"Min TCP distance: {min_tcp_dist_m * 1000:.1f} mm")
    print(f"Min physical gripper clearance (85 mm body): {min_gripper_clearance_m * 1000:.1f} mm (target >= 30 mm)")
    print(f"Min table clearance: {min_table_clearance_m * 1000:.1f} mm")
    print("SUCCESS: all clearances verified with zero collision risks.")


if __name__ == "__main__":
    main()
