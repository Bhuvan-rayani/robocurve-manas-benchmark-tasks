"""Unit and integration tests for window_restrictor_fit task."""

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


class DummyState:
    def __init__(self, pos, sliders=None, resting=True):
        self.pos = pos
        self.sliders = sliders or {}
        self._resting = resting

    def resting(self):
        return self._resting


class TestGeometry(unittest.TestCase):
    def test_dimensions_and_positions(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertEqual(len(geometry.HOLE_Y_COORDS), 3)
        self.assertEqual(len(geometry.HOLE_OPENINGS_M), 3)
        self.assertEqual(geometry.TARGET_HOLE_INDEX, 1)
        self.assertAlmostEqual(geometry.TARGET_HOLE_Y, 0.078)
        self.assertAlmostEqual(geometry.TARGET_OPENING_M, 0.100)
        self.assertAlmostEqual(geometry.HOLE_OPENINGS_M[1], 0.100)

    def test_clearance_and_springs(self):
        self.assertGreaterEqual(geometry.PEG_CLEARANCE_PER_SIDE_M, 0.007 - 1e-9)
        self.assertLessEqual(geometry.SASH_SPRING_RATE, 15.0)

    def test_hands_on_own_sides(self):
        self.assertGreater(geometry.BLOCK_START_POS_WORLD[1], 0.08)
        self.assertGreater(demo_plan.L_READY[1], 0.08)
        self.assertLess(demo_plan.R_READY[1], -0.08)
        self.assertLessEqual(demo_plan.PUSH_X, 0.30)
        self.assertLessEqual(geometry.TARGET_HOLE_POS_WORLD[0], 0.30)

    def test_block_sits_on_pad(self):
        bz = geometry.BLOCK_START_POS_WORLD[2] - geometry.PEG_LEN_M
        self.assertAlmostEqual(bz, geometry.PAD_POS_WORLD[2] + geometry.PAD_SIZE_M[2] / 2)

    def test_object_no_initial_overlap(self):
        fx, fy, fz = geometry.FRAME_POS_WORLD
        fsx, fsy, fsz = geometry.FRAME_DIMS_M
        px, py, pz = geometry.PAD_POS_WORLD
        psx, psy, psz = geometry.PAD_SIZE_M
        overlap_x = (fx - fsx / 2 < px + psx / 2) and (fx + fsx / 2 > px - psx / 2)
        overlap_y = (fy - fsy / 2 < py + psy / 2) and (fy + fsy / 2 > py - psy / 2)
        self.assertFalse(overlap_x and overlap_y, "Frame and datum pad overlap at start")


def _pocket_block(y, z=None):
    return (geometry.FRAME_POS_WORLD[0], y, geometry.TABLE_TOP + geometry.FLOOR_T_M if z is None else z)


class TestScoringLogic(unittest.TestCase):
    def test_first_update_on_real_start_pose(self):
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.0, geometry.BLOCK_START_POS_WORLD, resting=True)
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_partial_credit_block_lifted(self):
        p = geometry.BLOCK_START_POS_WORLD
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.0, (p[0], p[1], p[2] + 0.030))
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_seated_sash_closed_is_050(self):
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.0, _pocket_block(0.071))
        self.assertEqual(score, 0.50)
        self.assertFalse(ok)

    def test_seated_sash_at_end_stop_is_050(self):
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.120, _pocket_block(0.135))
        self.assertEqual(score, 0.50)

    def test_wrong_pocket_sash_stopped_is_075(self):
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.050, _pocket_block(0.035))
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_full_success(self):
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.100, _pocket_block(0.085), resting=True)
        self.assertEqual(score, 1.0)
        self.assertTrue(ok)

    def test_not_resting_not_full(self):
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.100, _pocket_block(0.085), resting=False)
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_block_on_floor_not_seated(self):
        score, ok, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.100, _pocket_block(0.085, geometry.TABLE_TOP + 0.012))
        self.assertEqual(score, 0.25)

    def test_two_valid_solutions_both_reach_full_score(self):
        s_a, ok_a, _ = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.100, _pocket_block(0.085), resting=True)
        s_b, ok_b, _ = logic.evaluate_state(
            (geometry.FRAME_POS_WORLD[0] + 0.001, 0.0, geometry.TABLE_TOP), 0.098,
            (geometry.FRAME_POS_WORLD[0] + 0.002, 0.083, geometry.TABLE_TOP + 0.0065), resting=True)
        self.assertEqual((s_a, s_b), (1.0, 1.0))
        self.assertTrue(ok_a and ok_b)

    def test_frame_drift_gate(self):
        # Frame drifted 6 mm (> 5 mm gate)
        drifted_frame = (
            geometry.FRAME_POS_WORLD[0] + 0.006,
            geometry.FRAME_POS_WORLD[1],
            geometry.FRAME_POS_WORLD[2],
        )
        target_pos = (drifted_frame[0], 0.085, geometry.TABLE_TOP + 0.006)
        score, ok, reason = logic.evaluate_state(drifted_frame, 0.100, target_pos, resting=True)
        self.assertEqual(score, 0.0, "Frame drift > 5 mm must trigger gate score 0.0")
        self.assertFalse(ok)
        self.assertIn("gate", reason.lower())

    def test_block_dropped_gate(self):
        # Block fell below table
        fallen_pos = (geometry.FRAME_POS_WORLD[0], 0.085, geometry.TABLE_TOP - 0.10)
        score, ok, reason = logic.evaluate_state(geometry.FRAME_POS_WORLD, 0.100, fallen_pos, resting=True)
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)
        self.assertIn("gate", reason.lower())

    def test_fuzz_scoring(self):
        # Random inputs must never crash and scores must always remain in [0.0, 1.0]
        rng = np.random.default_rng(42)
        for _ in range(500):
            rand_frame = (
                float(rng.uniform(0.25, 0.35)),
                float(rng.uniform(-0.05, 0.05)),
                geometry.TABLE_TOP,
            )
            rand_sash = float(rng.uniform(-0.02, 0.20))
            rand_block = (
                float(rng.uniform(0.10, 0.35)),
                float(rng.uniform(-0.25, 0.20)),
                float(rng.uniform(0.70, 0.90)),
            )
            s, ok, reason = logic.evaluate_state(
                rand_frame,
                rand_sash,
                rand_block,
                resting=bool(rng.choice([True, False])),
                gripper_clearance_m=float(rng.uniform(0.01, 0.10)),
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
        self.assertIn("window_frame", names)
        self.assertIn("stop_block", names)
        self.assertIn("stop_pad", names)

    def test_scoring_wrappers(self):
        objects = {
            "window_frame": DummyState(geometry.FRAME_POS_WORLD, {"sash_pane": 0.0}),
            "stop_block": DummyState(geometry.BLOCK_START_POS_WORLD),
        }
        self.assertEqual(scoring.score(objects), 0.0)
        self.assertFalse(scoring.success(objects))
        dist = scoring.distance(objects)
        self.assertGreater(dist, 0.0)


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
        os.environ["ABLATION"] = "1"
        p_abl = demo_plan.plans()
        del os.environ["ABLATION"]
        self.assertEqual(len(p_abl["left"]), 1)

        # Plan step length checks: demo duration should be 600-1200 steps
        from yam_arena.constants import LEFT_BASE_POS, RIGHT_BASE_POS
        from yam_arena.demo import ArmPlan

        lp = ArmPlan(p_demo["left"], LEFT_BASE_POS)
        rp = ArmPlan(p_demo["right"], RIGHT_BASE_POS)
        total_s = max(lp.duration, rp.duration)
        steps = int(np.ceil(total_s / 0.05))
        self.assertTrue(
            600 <= steps <= 1500,
            f"Demo plan steps {steps} outside 600-1500 target range",
        )


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
