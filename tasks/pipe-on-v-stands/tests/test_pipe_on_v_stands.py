"""Unit and integration tests for pipe_on_v_stands (T17)."""

from __future__ import annotations

import math
from pathlib import Path
import re
import sys
import unittest
import numpy as np

_TASK_DIR = Path(__file__).resolve().parent.parent
_UPSTREAM = _TASK_DIR.parents[2] / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"

for p in (_TASK_DIR, _UPSTREAM):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import geometry
import logic
import scoring
import demo_plan
import yam_arena.task_file


class DummyObject:
    def __init__(self, pos, quat_xyzw=(0.0, 0.0, 0.0, 1.0), resting=True):
        self.pos = pos
        self.quat_xyzw = quat_xyzw
        self._resting = resting

    def resting(self):
        return self._resting


class TestGeometry(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertEqual(geometry.STAND_A_NAME, "v_stand_a")
        self.assertEqual(geometry.STAND_B_NAME, "v_stand_b")
        self.assertEqual(geometry.PIPE_NAME, "pipe")
        self.assertEqual(geometry.PIPE_PAD_NAME, "pipe_pad")
        self.assertAlmostEqual(geometry.STAND_A_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.STAND_B_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.PIPE_MASS_KG, 1.0)
        self.assertAlmostEqual(geometry.PIPE_RADIUS_M, 0.03)
        self.assertAlmostEqual(geometry.PIPE_LENGTH_M, 0.60)
        self.assertAlmostEqual(geometry.STAND_A_FRICTION, 1.2)

    def test_stand_spacing(self):
        # 42 cm apart in Y
        dist_y = abs(geometry.STAND_A_POS_WORLD[1] - geometry.STAND_B_POS_WORLD[1])
        self.assertAlmostEqual(dist_y, 0.42, places=3)
        self.assertAlmostEqual(geometry.STAND_A_POS_WORLD[0], 0.34, places=3)
        self.assertAlmostEqual(geometry.STAND_B_POS_WORLD[0], 0.34, places=3)

    def test_no_initial_overlap(self):
        # Pipe starts on pipe_pad; verify stands are clear of start pad
        pad_x, pad_y, _ = geometry.PIPE_PAD_POS_WORLD
        pad_sx, pad_sy, _ = geometry.PIPE_PAD_DIMS_M

        sa_x, sa_y, _ = geometry.STAND_A_POS_WORLD
        sa_sx, sa_sy, _ = geometry.STAND_A_DIMS_M

        overlap_x = (abs(pad_x - sa_x) < (pad_sx + sa_sx) / 2)
        overlap_y = (abs(pad_y - sa_y) < (pad_sy + sa_sy) / 2)
        self.assertFalse(overlap_x and overlap_y, "Pipe pad and stand A overlap")


class TestScoringLogic(unittest.TestCase):
    def test_first_update_on_real_start_pose(self):
        s, ok, reason = logic.evaluate_state(
            geometry.PIPE_START_POS,
            geometry.PIPE_START_QUAT,
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s, 0.0, "First scorer update on start pose must give 0.0")
        self.assertFalse(ok, "First scorer update must give ok=False")

    def test_gate_stand_drift(self):
        # Stand A moved > 5 mm
        drifted_a = (geometry.STAND_A_POS_WORLD[0] + 0.006, geometry.STAND_A_POS_WORLD[1], geometry.TABLE_TOP)
        s, ok, reason = logic.evaluate_state(
            geometry.PIPE_TARGET_POS,
            geometry.PIPE_START_QUAT,
            drifted_a,
            geometry.STAND_B_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("stand_a moved", reason)

        # Stand B moved > 5 mm
        drifted_b = (geometry.STAND_B_POS_WORLD[0], geometry.STAND_B_POS_WORLD[1] - 0.006, geometry.TABLE_TOP)
        s, ok, reason = logic.evaluate_state(
            geometry.PIPE_TARGET_POS,
            geometry.PIPE_START_QUAT,
            geometry.STAND_A_POS_WORLD,
            drifted_b,
            resting=True,
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("stand_b moved", reason)

    def test_gate_pipe_dropped(self):
        # Pipe dropped below table
        dropped_pos = (0.20, 0.0, geometry.TABLE_TOP - 0.05)
        s, ok, reason = logic.evaluate_state(
            dropped_pos,
            geometry.PIPE_START_QUAT,
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("dropped", reason)

    def test_ladder_0_25_lifted(self):
        # Pipe lifted by 6 cm (> 5 cm) at start XY
        lifted_pos = (0.18, 0.0, geometry.PIPE_START_POS[2] + 0.06)
        s, ok, reason = logic.evaluate_state(
            lifted_pos,
            geometry.PIPE_START_QUAT,
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=False,
        )
        self.assertEqual(s, 0.25)
        self.assertFalse(ok)
        self.assertIn("lifted", reason)

    def test_ladder_0_50_over_stands(self):
        # Pipe carried over stands (x = 0.34, z = TABLE_TOP + 0.15)
        over_pos = (0.34, 0.0, geometry.TABLE_TOP + 0.12 + 0.02)
        s, ok, reason = logic.evaluate_state(
            over_pos,
            geometry.PIPE_START_QUAT,
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=False,
        )
        self.assertEqual(s, 0.50)
        self.assertFalse(ok)
        self.assertIn("over stands", reason)

    def test_ladder_0_75_in_one_stand(self):
        # Pipe seated in stand A but tilted up at stand B
        # Stand A is at y = +0.21, Stand B at y = -0.21
        # Place pipe with tilt around X axis so stand B end is high
        tilt_angle = math.radians(6.0)
        # Quaternion for rotation around X
        qx = math.sin(tilt_angle / 2)
        qw = math.cos(tilt_angle / 2)
        quat = (qx, 0.0, 0.0, qw)

        # Position so stand A end is seated
        pos = (0.34, 0.0, geometry.TABLE_TOP + 0.0924 + 0.21 * math.sin(tilt_angle))
        s, ok, reason = logic.evaluate_state(
            pos,
            quat,
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s, 0.75)
        self.assertFalse(ok)

    def test_ladder_1_00_success(self):
        # Fully seated in both stands and resting
        s, ok, reason = logic.evaluate_state(
            geometry.PIPE_TARGET_POS,
            geometry.PIPE_START_QUAT,
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s, 1.0)
        self.assertTrue(ok)
        self.assertIn("seated securely", reason)

    def test_moving_caps_at_0_75(self):
        # Position is fully seated, but pipe is still moving (resting=False)
        s, ok, reason = logic.evaluate_state(
            geometry.PIPE_TARGET_POS,
            geometry.PIPE_START_QUAT,
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=False,
        )
        self.assertEqual(s, 0.75)
        self.assertFalse(ok)
        self.assertIn("moving", reason)

    def test_two_different_valid_solutions_both_score_1(self):
        # Solution 1: Exact nominal centre
        s1, ok1, _ = logic.evaluate_state(
            geometry.PIPE_TARGET_POS,
            (0.0, 0.0, 0.0, 1.0),
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s1, 1.0)
        self.assertTrue(ok1)

        # Solution 2: Small translation and 2 deg yaw rotation (within 5 deg tolerance)
        yaw_rad = math.radians(2.0)
        qz = math.sin(yaw_rad / 2)
        qw = math.cos(yaw_rad / 2)
        sol2_pos = (
            geometry.SEATED_X_TARGET_M + 0.004,
            geometry.SEATED_Y_TARGET_M + 0.015,
            geometry.TABLE_TOP + 0.0924 - 0.002,
        )
        s2, ok2, _ = logic.evaluate_state(
            sol2_pos,
            (0.0, 0.0, qz, qw),
            geometry.STAND_A_POS_WORLD,
            geometry.STAND_B_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s2, 1.0)
        self.assertTrue(ok2)


class TestScoringWrappers(unittest.TestCase):
    def test_scoring_with_dummy_objects(self):
        objects = {
            geometry.PIPE_NAME: DummyObject(geometry.PIPE_START_POS, geometry.PIPE_START_QUAT, resting=True),
            geometry.STAND_A_NAME: DummyObject(geometry.STAND_A_POS_WORLD),
            geometry.STAND_B_NAME: DummyObject(geometry.STAND_B_POS_WORLD),
        }
        self.assertEqual(scoring.score(objects), 0.0)
        self.assertFalse(scoring.success(objects))
        self.assertAlmostEqual(scoring.distance(objects), 0.10)

        # Goal pose
        objects[geometry.PIPE_NAME] = DummyObject(geometry.PIPE_TARGET_POS, geometry.PIPE_START_QUAT, resting=True)
        self.assertEqual(scoring.score(objects), 1.0)
        self.assertTrue(scoring.success(objects))
        self.assertAlmostEqual(scoring.distance(objects), 0.0)


class TestDemoPlans(unittest.TestCase):
    def test_modes(self):
        p_demo = demo_plan.plans("demo")
        self.assertIn("left", p_demo)
        self.assertIn("right", p_demo)
        self.assertGreaterEqual(len(p_demo["left"]), 8)

        p_settle = demo_plan.plans("settle")
        self.assertEqual(len(p_settle["left"]), 1)
        self.assertIn("settle", p_settle["left"][0].label)

        p_ablation = demo_plan.plans("ablation")
        self.assertEqual(len(p_ablation["right"]), 1)
        self.assertIn("idle", p_ablation["right"][0].label)


class TestFuzzing(unittest.TestCase):
    def test_random_poses_never_crash_and_score_in_bounds(self):
        np.random.seed(42)
        for _ in range(300):
            rx = float(np.random.uniform(0.0, 0.6))
            ry = float(np.random.uniform(-0.5, 0.5))
            rz = float(np.random.uniform(0.6, 1.2))
            pos = (rx, ry, rz)

            q = np.random.normal(0, 1, 4)
            q = tuple(float(v) for v in (q / np.linalg.norm(q)))
            resting = bool(np.random.choice([True, False]))

            s, ok, reason = logic.evaluate_state(
                pos, q, geometry.STAND_A_POS_WORLD, geometry.STAND_B_POS_WORLD, resting=resting
            )
            self.assertTrue(0.0 <= s <= 1.0)
            self.assertIsInstance(ok, bool)
            self.assertIsInstance(reason, str)


class TestBlindReviewScan(unittest.TestCase):
    def test_no_forbidden_patterns(self):
        forbidden = [
            r"C:\\Users",
            r"/home/",
            r"@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        ]
        files_to_check = [
            _TASK_DIR / "task.py",
            _TASK_DIR / "geometry.py",
            _TASK_DIR / "logic.py",
            _TASK_DIR / "scoring.py",
            _TASK_DIR / "demo_plan.py",
            _TASK_DIR / "check_reach.py",
            _TASK_DIR / "check_collisions.py",
        ]
        for f in files_to_check:
            if not f.exists():
                continue
            content = f.read_text(encoding="utf-8")
            for pattern in forbidden:
                self.assertIsNone(
                    re.search(pattern, content, re.IGNORECASE),
                    f"Forbidden pattern {pattern} found in {f.name}"
                )


if __name__ == "__main__":
    unittest.main()
