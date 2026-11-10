"""Unit and integration tests for outlet_cover_fit task."""

from __future__ import annotations

import os
from pathlib import Path
import re
import sys
import unittest
import numpy as np

_TASK_DIR = Path(__file__).resolve().parent.parent
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

import geometry
import logic
import scoring
import demo_plan
import yam_arena.task_file


class DummyObject:
    def __init__(self, pos, resting=True):
        self.pos = pos
        self._resting = resting

    def resting(self):
        return self._resting


class TestGeometry(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.PLATE_START_POS_WORLD[0], 0.30)
        self.assertAlmostEqual(geometry.PLATE_START_POS_WORLD[1], 0.0)
        self.assertAlmostEqual(geometry.PLATE_DIMS_M[0], 0.12)
        self.assertAlmostEqual(geometry.PLATE_DIMS_M[1], 0.26)
        self.assertAlmostEqual(geometry.PLATE_DIMS_M[2], 0.02)
        self.assertAlmostEqual(geometry.PLATE_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.PLATE_FRICTION, 0.35)

    def test_cap_dimensions(self):
        self.assertAlmostEqual(geometry.CAP_RADIUS_M, 0.020)
        self.assertAlmostEqual(geometry.CAP_HEIGHT_M, 0.030)
        self.assertAlmostEqual(geometry.CAP_MASS_KG, 0.02)
        self.assertEqual(len(geometry.CAP_NAMES), 3)

    def test_sockets_pitch(self):
        self.assertAlmostEqual(geometry.SOCKET_A_OFFSET_M[1], 0.07)
        self.assertAlmostEqual(geometry.SOCKET_B_OFFSET_M[1], 0.0)
        self.assertAlmostEqual(geometry.SOCKET_C_OFFSET_M[1], -0.07)
        pitch_ab = geometry.SOCKET_A_OFFSET_M[1] - geometry.SOCKET_B_OFFSET_M[1]
        pitch_bc = geometry.SOCKET_B_OFFSET_M[1] - geometry.SOCKET_C_OFFSET_M[1]
        self.assertAlmostEqual(pitch_ab, 0.07, places=3)
        self.assertAlmostEqual(pitch_bc, 0.07, places=3)


class TestScoringLogic(unittest.TestCase):
    def setUp(self):
        self.plate_pos = geometry.PLATE_START_POS_WORLD
        self.caps_start = {
            geometry.CAP_A_NAME: geometry.CAP_A_START_POS_WORLD,
            geometry.CAP_B_NAME: geometry.CAP_B_START_POS_WORLD,
            geometry.CAP_C_NAME: geometry.CAP_C_START_POS_WORLD,
        }

    def test_first_update_on_real_start_pose(self):
        s, ok, reason = logic.evaluate_state(self.plate_pos, self.caps_start, resting=True)
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)

    def test_ladder_one_cap_seated(self):
        # Seat cap_c in socket C: socket C is at (0.30, -0.07, TABLE_TOP + 0.011)
        # Cap center when seated on socket floor (z = TABLE_TOP + 0.002) is TABLE_TOP + 0.017
        caps = dict(self.caps_start)
        caps[geometry.CAP_C_NAME] = (0.30, -0.07, geometry.TABLE_TOP + 0.017)
        s, ok, reason = logic.evaluate_state(self.plate_pos, caps, resting=True)
        self.assertEqual(s, 0.25)
        self.assertFalse(ok)

    def test_ladder_two_caps_seated(self):
        caps = dict(self.caps_start)
        caps[geometry.CAP_C_NAME] = (0.30, -0.07, geometry.TABLE_TOP + 0.017)
        caps[geometry.CAP_A_NAME] = (0.30, 0.07, geometry.TABLE_TOP + 0.017)
        s, ok, reason = logic.evaluate_state(self.plate_pos, caps, resting=True)
        self.assertEqual(s, 0.50)
        self.assertFalse(ok)

    def test_ladder_three_caps_seated_plate_moved_excessively(self):
        # Move plate by 20 mm in x (>= 15 mm, but < 60 mm gate)
        moved_plate = (0.320, 0.0, geometry.TABLE_TOP)
        caps = {
            geometry.CAP_A_NAME: (0.320, 0.07, geometry.TABLE_TOP + 0.017),
            geometry.CAP_B_NAME: (0.320, 0.0, geometry.TABLE_TOP + 0.017),
            geometry.CAP_C_NAME: (0.320, -0.07, geometry.TABLE_TOP + 0.017),
        }
        s, ok, reason = logic.evaluate_state(moved_plate, caps, resting=True)
        self.assertEqual(s, 0.75)
        self.assertFalse(ok)

    def test_ladder_three_caps_seated_full_success(self):
        caps = {
            geometry.CAP_A_NAME: (0.30, 0.07, geometry.TABLE_TOP + 0.017),
            geometry.CAP_B_NAME: (0.30, 0.0, geometry.TABLE_TOP + 0.017),
            geometry.CAP_C_NAME: (0.30, -0.07, geometry.TABLE_TOP + 0.017),
        }
        s, ok, reason = logic.evaluate_state(self.plate_pos, caps, resting=True)
        self.assertEqual(s, 1.00)
        self.assertTrue(ok)

    def test_two_different_valid_solutions_both_reach_full_score(self):
        # Solution 1: Cap A in A, Cap B in B, Cap C in C
        sol1 = {
            geometry.CAP_A_NAME: (0.30, 0.07, geometry.TABLE_TOP + 0.017),
            geometry.CAP_B_NAME: (0.30, 0.0, geometry.TABLE_TOP + 0.017),
            geometry.CAP_C_NAME: (0.30, -0.07, geometry.TABLE_TOP + 0.017),
        }
        s1, ok1, _ = logic.evaluate_state(self.plate_pos, sol1, resting=True)

        # Solution 2: Swapped caps (Cap C in A, Cap A in B, Cap B in C)
        sol2 = {
            geometry.CAP_C_NAME: (0.30, 0.07, geometry.TABLE_TOP + 0.017),
            geometry.CAP_A_NAME: (0.30, 0.0, geometry.TABLE_TOP + 0.017),
            geometry.CAP_B_NAME: (0.30, -0.07, geometry.TABLE_TOP + 0.017),
        }
        s2, ok2, _ = logic.evaluate_state(self.plate_pos, sol2, resting=True)

        self.assertEqual(s1, 1.00)
        self.assertTrue(ok1)
        self.assertEqual(s2, 1.00)
        self.assertTrue(ok2)

    def test_gate_plate_drift_exceeded(self):
        # Plate shifted > 6 cm (e.g. 65 mm)
        drifted_plate = (0.365, 0.0, geometry.TABLE_TOP)
        caps = {
            geometry.CAP_A_NAME: (0.365, 0.07, geometry.TABLE_TOP + 0.017),
            geometry.CAP_B_NAME: (0.365, 0.0, geometry.TABLE_TOP + 0.017),
            geometry.CAP_C_NAME: (0.365, -0.07, geometry.TABLE_TOP + 0.017),
        }
        s, ok, reason = logic.evaluate_state(drifted_plate, caps, resting=True)
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("Gate failed", reason)

    def test_gate_object_fallen_off_table(self):
        fallen_caps = dict(self.caps_start)
        fallen_caps[geometry.CAP_A_NAME] = (0.15, 0.12, geometry.TABLE_TOP - 0.08)
        s, ok, reason = logic.evaluate_state(self.plate_pos, fallen_caps, resting=True)
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("fell off table", reason)

    def test_fuzz_scoring(self):
        rng = np.random.default_rng(42)
        for _ in range(200):
            r_plate = (
                float(rng.uniform(0.25, 0.38)),
                float(rng.uniform(-0.08, 0.08)),
                float(rng.uniform(geometry.TABLE_TOP - 0.02, geometry.TABLE_TOP + 0.05)),
            )
            r_caps = {
                name: (
                    float(rng.uniform(0.10, 0.40)),
                    float(rng.uniform(-0.25, 0.25)),
                    float(rng.uniform(geometry.TABLE_TOP - 0.05, geometry.TABLE_TOP + 0.10)),
                )
                for name in geometry.CAP_NAMES
            }
            s, ok, reason = logic.evaluate_state(
                r_plate, r_caps, resting=bool(rng.choice([True, False]))
            )
            self.assertTrue(0.0 <= s <= 1.0)
            self.assertIsInstance(ok, bool)


class TestTaskFileContract(unittest.TestCase):
    def test_task_file_loads(self):
        task_path = _TASK_DIR / "task.py"
        t = yam_arena.task_file.load(str(task_path))
        self.assertEqual(t.scene, "station")
        self.assertAlmostEqual(t.table_top, 0.7475)
        self.assertEqual(t.success_hold_s, 1.0)
        obj_names = [o.name for o in t.objects]
        self.assertIn("wall_plate", obj_names)
        self.assertIn("cap_a", obj_names)
        self.assertIn("cap_b", obj_names)
        self.assertIn("cap_c", obj_names)

    def test_scoring_wrappers(self):
        objects = {
            "wall_plate": DummyObject(geometry.PLATE_START_POS_WORLD),
            "cap_a": DummyObject(geometry.CAP_A_START_POS_WORLD),
            "cap_b": DummyObject(geometry.CAP_B_START_POS_WORLD),
            "cap_c": DummyObject(geometry.CAP_C_START_POS_WORLD),
        }
        self.assertEqual(scoring.score(objects), 0.0)
        self.assertFalse(scoring.success(objects))
        self.assertAlmostEqual(scoring.distance(objects), 0.05)


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
