"""Unit and integration tests for server_chassis_rail_insert task."""

from __future__ import annotations

import os
from pathlib import Path
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
    def test_dimensions_and_positions(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.POST_FRONT_FACE_X, 0.390)
        self.assertAlmostEqual(geometry.RAIL_START_X, 0.420)
        self.assertAlmostEqual(geometry.CHASSIS_START_POS[0], 0.290)
        self.assertAlmostEqual(geometry.CHASSIS_MASS_KG, 0.70)
        self.assertAlmostEqual(geometry.CHASSIS_GOAL_X, 0.506)

    def test_no_initial_overlap(self):
        # Post A and Post B separation
        dist_posts = abs(geometry.POST_A_POS_WORLD[1] - geometry.POST_B_POS_WORLD[1])
        self.assertAlmostEqual(dist_posts, 0.390)  # 390 mm center-to-center = 360 mm inside clearance

        # Chassis starts resting on staging plate
        # Staging plate top: z = TABLE_TOP + 0.060
        # Chassis base: z = TABLE_TOP + 0.060
        self.assertAlmostEqual(geometry.CHASSIS_START_POS[2], geometry.TABLE_TOP + 0.060)

        # Chassis rear is at x = 0.170 + 0.120 = 0.290 m
        # Rail starts at x = 0.300 m
        # Thus at start, chassis does not overlap/penetrate the rails
        chassis_rear_x = geometry.CHASSIS_START_POS[0] + geometry.CHASSIS_REAR_LOCAL_X
        self.assertLessEqual(chassis_rear_x, geometry.RAIL_START_X)


class TestScoringLogic(unittest.TestCase):
    def test_first_update_on_real_start_pose(self):
        score, ok, reason = logic.evaluate_state(
            geometry.POST_A_POS_WORLD,
            geometry.POST_B_POS_WORLD,
            geometry.CHASSIS_START_POS,
            (0.0, 0.0, 0.0, 1.0),
            resting=True,
        )
        self.assertEqual(score, 0.0, f"First scorer update must give 0.0, got {score}")
        self.assertFalse(ok, "First scorer update must have success=False")

    def test_partial_credit_lift_or_slide_start(self):
        # Lifted > 2 cm
        lifted_pos = (geometry.CHASSIS_START_POS[0], geometry.CHASSIS_START_POS[1], geometry.CHASSIS_START_POS[2] + 0.025)
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD,
            geometry.POST_B_POS_WORLD,
            lifted_pos,
            (0.0, 0.0, 0.0, 1.0),
            resting=False,
        )
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

        # Advanced >= 2 cm along X
        advanced_pos = (geometry.CHASSIS_START_POS[0] + 0.025, geometry.CHASSIS_START_POS[1], geometry.CHASSIS_START_POS[2])
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD,
            geometry.POST_B_POS_WORLD,
            advanced_pos,
            (0.0, 0.0, 0.0, 1.0),
            resting=False,
        )
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_ladder_0_50_depth_6cm(self):
        # Rear end in rails >= 6 cm: rear_x >= 0.300 + 0.060 = 0.360 m
        # chassis_x = 0.360 - 0.120 = 0.240 m
        pos_6cm = (0.365, 0.0, geometry.CHASSIS_START_POS[2])
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD,
            geometry.POST_B_POS_WORLD,
            pos_6cm,
            (0.0, 0.0, 0.0, 1.0),
            resting=False,
        )
        self.assertEqual(score, 0.50)
        self.assertFalse(ok)

    def test_ladder_0_75_depth_15cm(self):
        # Rear end in rails >= 15 cm: rear_x >= 0.300 + 0.150 = 0.450 m
        # chassis_x = 0.450 - 0.120 = 0.330 m
        pos_15cm = (0.455, 0.0, geometry.CHASSIS_START_POS[2])
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD,
            geometry.POST_B_POS_WORLD,
            pos_15cm,
            (0.0, 0.0, 0.0, 1.0),
            resting=False,
        )
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_full_success(self):
        # Full insertion: chassis at goal (x=0.386 m), ears flush (gap=0), tilt=0, resting=True
        goal_pos = (geometry.CHASSIS_GOAL_X, 0.0, geometry.CHASSIS_START_POS[2])
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD,
            geometry.POST_B_POS_WORLD,
            goal_pos,
            (0.0, 0.0, 0.0, 1.0),
            resting=True,
        )
        self.assertEqual(score, 1.0)
        self.assertTrue(ok)

    def test_two_different_valid_solutions_both_reach_full_score(self):
        # Solution A: perfectly centered flush
        sol_a_pos = (geometry.CHASSIS_GOAL_X, 0.0, geometry.CHASSIS_START_POS[2])
        sol_a_quat = (0.0, 0.0, 0.0, 1.0)

        # Solution B: 1 mm gap (within 3 mm tolerance), 1 mm lateral offset (within 3 mm clearance), 1.5 deg tilt
        angle_rad = np.radians(1.5)
        sol_b_quat = (np.sin(angle_rad / 2), 0.0, 0.0, np.cos(angle_rad / 2))
        sol_b_pos = (geometry.CHASSIS_GOAL_X - 0.001, 0.001, geometry.CHASSIS_START_POS[2])

        s_a, ok_a, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, geometry.POST_B_POS_WORLD, sol_a_pos, sol_a_quat, resting=True
        )
        s_b, ok_b, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, geometry.POST_B_POS_WORLD, sol_b_pos, sol_b_quat, resting=True
        )

        self.assertEqual(s_a, 1.0)
        self.assertTrue(ok_a)
        self.assertEqual(s_b, 1.0)
        self.assertTrue(ok_b)

    def test_gates(self):
        # Gate 1: Rack post A moved > 5 mm
        moved_post_a = (geometry.POST_A_POS_WORLD[0] + 0.006, geometry.POST_A_POS_WORLD[1], geometry.POST_A_POS_WORLD[2])
        goal_pos = (geometry.CHASSIS_GOAL_X, 0.0, geometry.CHASSIS_START_POS[2])
        score, ok, _ = logic.evaluate_state(
            moved_post_a, geometry.POST_B_POS_WORLD, goal_pos, (0.0, 0.0, 0.0, 1.0), resting=True
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

        # Gate 1: Rack post B moved > 5 mm
        moved_post_b = (geometry.POST_A_POS_WORLD[0], geometry.POST_B_POS_WORLD[1] - 0.006, geometry.POST_B_POS_WORLD[2])
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, moved_post_b, goal_pos, (0.0, 0.0, 0.0, 1.0), resting=True
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

        # Gate 2: Tilt > 15 degrees
        tilt_16_rad = np.radians(16.0)
        tilted_quat = (np.sin(tilt_16_rad / 2), 0.0, 0.0, np.cos(tilt_16_rad / 2))
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, geometry.POST_B_POS_WORLD, goal_pos, tilted_quat, resting=True
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

        # Gate 3: Chassis fell below table
        fell_pos = (geometry.CHASSIS_GOAL_X, 0.0, geometry.TABLE_TOP - 0.010)
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, geometry.POST_B_POS_WORLD, fell_pos, (0.0, 0.0, 0.0, 1.0), resting=True
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

        # Gate 4: Lateral drift > 5 cm
        drifted_pos = (geometry.CHASSIS_GOAL_X, 0.060, geometry.CHASSIS_START_POS[2])
        score, ok, _ = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, geometry.POST_B_POS_WORLD, drifted_pos, (0.0, 0.0, 0.0, 1.0), resting=True
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_fuzz_scoring(self):
        rng = np.random.default_rng(42)
        for _ in range(500):
            rand_chassis = (
                float(rng.uniform(0.1, 0.5)),
                float(rng.uniform(-0.1, 0.1)),
                float(rng.uniform(geometry.TABLE_TOP - 0.05, geometry.TABLE_TOP + 0.2)),
            )
            rand_q = rng.normal(size=4)
            rand_q /= np.linalg.norm(rand_q)
            rand_post_a = (
                float(geometry.POST_A_POS_WORLD[0] + rng.uniform(-0.01, 0.01)),
                float(geometry.POST_A_POS_WORLD[1] + rng.uniform(-0.01, 0.01)),
                float(geometry.POST_A_POS_WORLD[2]),
            )
            rand_post_b = (
                float(geometry.POST_B_POS_WORLD[0] + rng.uniform(-0.01, 0.01)),
                float(geometry.POST_B_POS_WORLD[1] + rng.uniform(-0.01, 0.01)),
                float(geometry.POST_B_POS_WORLD[2]),
            )
            s, ok, reason = logic.evaluate_state(
                rand_post_a, rand_post_b, rand_chassis, tuple(rand_q), resting=bool(rng.choice([True, False]))
            )
            self.assertTrue(0.0 <= s <= 1.0, f"Score out of bounds: {s}")
            self.assertIsInstance(ok, bool)
            self.assertIsInstance(reason, str)


class TestTaskFileContract(unittest.TestCase):
    def test_task_file_loads(self):
        task_path = _TASK_DIR / "task.py"
        t = yam_arena.task_file.load(str(task_path))
        self.assertEqual(t.scene, "station")
        self.assertAlmostEqual(t.table_top, 0.7475)
        self.assertEqual(t.success_hold_s, 1.0)
        names = [o.name for o in t.objects]
        self.assertIn("chassis_box", names)
        self.assertIn("rack_post_a", names)
        self.assertIn("rack_post_b", names)
        self.assertIn("staging_plate", names)
        self.assertIn("rack_rail_a", names)
        self.assertIn("rack_rail_b", names)

    def test_scoring_wrappers(self):
        objects = {
            "chassis_box": DummyObject(geometry.CHASSIS_START_POS),
            "rack_post_a": DummyObject(geometry.POST_A_POS_WORLD),
            "rack_post_b": DummyObject(geometry.POST_B_POS_WORLD),
        }
        self.assertEqual(scoring.score(objects), 0.0)
        self.assertFalse(scoring.success(objects))
        dist = scoring.distance(objects)
        self.assertGreater(dist, 0.15)


class TestDemoPlans(unittest.TestCase):
    def test_modes(self):
        os.environ["SETTLE_ONLY"] = "1"
        p_settle = demo_plan.plans()
        self.assertIn("left", p_settle)
        self.assertIn("right", p_settle)
        del os.environ["SETTLE_ONLY"]

        os.environ["ABLATION"] = "1"
        p_ablation = demo_plan.plans()
        self.assertIn("left", p_ablation)
        self.assertIn("right", p_ablation)
        del os.environ["ABLATION"]

        p_demo = demo_plan.plans()
        self.assertIn("left", p_demo)
        self.assertIn("right", p_demo)


class TestBlindReview(unittest.TestCase):
    def test_no_forbidden_strings(self):
        import re
        forbidden_substrings = ["c:\\users", "c:/users", "github.com/"]
        email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        team_words = [w.strip() for w in os.getenv("TEAM_WORDS", "").split(",") if w.strip()]

        for ext in (".py", ".json", ".md", ".sh"):
            for f in _TASK_DIR.rglob(f"*{ext}"):
                if "tests" in f.parts or "__pycache__" in f.parts or f.name == "VM_NOTES.md":
                    continue
                content = f.read_text(encoding="utf-8", errors="ignore")
                content_lower = content.lower()
                for bad in forbidden_substrings:
                    self.assertNotIn(bad, content_lower, f"Forbidden substring {bad!r} in {f.name}")
                self.assertIsNone(email_pattern.search(content), f"Email found in {f.name}")
                for tw in team_words:
                    self.assertNotIn(tw.lower(), content_lower, f"Team word {tw!r} in {f.name}")


if __name__ == "__main__":
    unittest.main()
