"""Unit and integration tests for till_make_change task."""

from __future__ import annotations

import math
import os
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
    def __init__(self, pos, sliders=None, resting=True):
        self.pos = pos
        self.sliders = sliders or {}
        self._resting = resting

    def resting(self):
        return self._resting


class TestGeometry(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertEqual(len(geometry.TOKEN_A_NAMES), 4)
        self.assertEqual(len(geometry.TOKEN_B_NAMES), 4)
        self.assertEqual(geometry.TARGET_CHANGE, 3)

    def test_token_stack_spacing(self):
        d = math.hypot(geometry.TOKEN_A_XY[0] - geometry.TOKEN_B_XY[0], geometry.TOKEN_A_XY[1] - geometry.TOKEN_B_XY[1])
        self.assertGreaterEqual(d, 0.100, "token stacks must be >= 100 mm apart")
        # stacked tokens: spacing equals the token thickness, the first token rests on the table
        for zs, h in ((geometry.TOKEN_A_Z_STARTS, geometry.TOKEN_A_HEIGHT_M), (geometry.TOKEN_B_Z_STARTS, geometry.TOKEN_B_HEIGHT_M)):
            self.assertAlmostEqual(zs[0], 0.0)
            for lo, hi in zip(zs, zs[1:]):
                self.assertAlmostEqual(hi - lo, h)

    def test_sides_of_the_midline(self):
        # left arm: till + knob (y > +0.08); right arm: tokens + tray (y < -0.08)
        self.assertGreater(geometry.KNOB_Y_WORLD, 0.08)
        for y in (geometry.TOKEN_A_XY[1], geometry.TOKEN_B_XY[1], geometry.TRAY_POS_WORLD[1]):
            self.assertLess(y, -0.08)
        self.assertGreaterEqual(geometry.KNOB_Y_WORLD - geometry.TOKEN_A_XY[1], 0.150)
        tx = (geometry.TOKEN_A_XY, geometry.TOKEN_B_XY, geometry.TRAY_POS_WORLD[:2])
        for i in range(3):
            for j in range(i + 1, 3):
                self.assertGreaterEqual(math.hypot(tx[i][0] - tx[j][0], tx[i][1] - tx[j][1]), 0.070)

    def test_drawer_stays_pushed(self):
        self.assertLessEqual(geometry.DRAWER_SPRING_RATE, 0.01)
        self.assertGreaterEqual(geometry.DRAWER_DAMPING, 40.0)


class TestScoringLogic(unittest.TestCase):
    def setUp(self):
        self.default_tokens = {}
        for name, z in zip(geometry.TOKEN_A_NAMES, geometry.TOKEN_A_Z_STARTS):
            self.default_tokens[name] = (geometry.TOKEN_A_XY[0], geometry.TOKEN_A_XY[1], geometry.TABLE_TOP + z)
        for name, z in zip(geometry.TOKEN_B_NAMES, geometry.TOKEN_B_Z_STARTS):
            self.default_tokens[name] = (geometry.TOKEN_B_XY[0], geometry.TOKEN_B_XY[1], geometry.TABLE_TOP + z)

    def test_first_update_on_real_start_pose(self):
        score, ok, reason = logic.evaluate_state(
            geometry.TILL_POS_WORLD,
            0.0,
            self.default_tokens,
            resting=True,
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_partial_credit_drawer_opened(self):
        score, ok, reason = logic.evaluate_state(
            geometry.TILL_POS_WORLD,
            -0.070,  # 7 cm open
            self.default_tokens,
            resting=True,
        )
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_partial_credit_one_unit_token_in_tray(self):
        tokens = dict(self.default_tokens)
        tokens["coin_a4"] = (geometry.TRAY_POS_WORLD[0], geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        score, ok, reason = logic.evaluate_state(geometry.TILL_POS_WORLD, -0.10, tokens, resting=True)
        self.assertEqual(score, 0.50)
        self.assertFalse(ok)

    def test_partial_credit_two_units_in_tray(self):
        tokens = dict(self.default_tokens)
        tokens["coin_b4"] = (geometry.TRAY_POS_WORLD[0], geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        score, ok, reason = logic.evaluate_state(geometry.TILL_POS_WORLD, -0.10, tokens, resting=True)
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_full_success_three_units(self):
        # 1x 2-unit + 1x 1-unit = 3 units
        tokens = dict(self.default_tokens)
        tokens["coin_b4"] = (geometry.TRAY_POS_WORLD[0] - 0.01, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        tokens["coin_a4"] = (geometry.TRAY_POS_WORLD[0] + 0.01, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        score, ok, reason = logic.evaluate_state(geometry.TILL_POS_WORLD, -0.10, tokens, resting=True)
        self.assertEqual(score, 1.00)
        self.assertTrue(ok)

    def test_two_different_valid_solutions_both_reach_full_score(self):
        # Solution A: 1x 2-unit + 1x 1-unit = 3 units
        tokens_a = dict(self.default_tokens)
        tokens_a["coin_b4"] = (geometry.TRAY_POS_WORLD[0] - 0.01, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        tokens_a["coin_a4"] = (geometry.TRAY_POS_WORLD[0] + 0.01, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)

        # Solution B: 3x 1-unit = 3 units
        tokens_b = dict(self.default_tokens)
        tokens_b["coin_a4"] = (geometry.TRAY_POS_WORLD[0] - 0.02, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        tokens_b["coin_a3"] = (geometry.TRAY_POS_WORLD[0], geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        tokens_b["coin_a2"] = (geometry.TRAY_POS_WORLD[0] + 0.02, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)

        s_a, ok_a, _ = logic.evaluate_state(geometry.TILL_POS_WORLD, -0.10, tokens_a, resting=True)
        s_b, ok_b, _ = logic.evaluate_state(geometry.TILL_POS_WORLD, -0.10, tokens_b, resting=True)
        self.assertEqual(s_a, 1.0)
        self.assertTrue(ok_a)
        self.assertEqual(s_b, 1.0)
        self.assertTrue(ok_b)

    def test_tray_credit_needs_open_drawer(self):
        tokens = dict(self.default_tokens)
        tokens["coin_b4"] = (geometry.TRAY_POS_WORLD[0] - 0.01, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        tokens["coin_a4"] = (geometry.TRAY_POS_WORLD[0] + 0.01, geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        score, ok, _ = logic.evaluate_state(geometry.TILL_POS_WORLD, 0.0, tokens, resting=True)
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_loose_token_zeroes_score(self):
        tokens = dict(self.default_tokens)
        tokens["coin_b4"] = (geometry.TRAY_POS_WORLD[0], geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        tokens["coin_a4"] = (geometry.TRAY_POS_WORLD[0], geometry.TRAY_POS_WORLD[1], geometry.TABLE_TOP + 0.010)
        # One loose token dropped in the middle of the table
        tokens["coin_a3"] = (0.20, 0.00, geometry.TABLE_TOP + 0.005)
        score, ok, reason = logic.evaluate_state(geometry.TILL_POS_WORLD, -0.10, tokens, resting=True)
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_till_drift_gate(self):
        drifted_till = (geometry.TILL_POS_WORLD[0] + 0.008, geometry.TILL_POS_WORLD[1], geometry.TILL_POS_WORLD[2])
        score, ok, reason = logic.evaluate_state(drifted_till, -0.10, self.default_tokens)
        self.assertEqual(score, 0.0)

    def test_token_fall_off_table_gate(self):
        tokens = dict(self.default_tokens)
        tokens["coin_a1"] = (0.20, 0.0, geometry.TABLE_TOP - 0.05)  # fell off
        score, ok, reason = logic.evaluate_state(geometry.TILL_POS_WORLD, -0.10, tokens)
        self.assertEqual(score, 0.0)

    def test_fuzz_scoring(self):
        rng = np.random.default_rng(123)
        for _ in range(300):
            rand_till = (
                float(rng.uniform(0.28, 0.32)),
                float(rng.uniform(0.08, 0.12)),
                geometry.TABLE_TOP,
            )
            rand_slider = float(rng.uniform(-0.12, 0.02))
            rand_tokens = {}
            for name in geometry.TOKEN_A_NAMES + geometry.TOKEN_B_NAMES:
                rand_tokens[name] = (
                    float(rng.uniform(0.1, 0.4)),
                    float(rng.uniform(-0.3, 0.3)),
                    float(rng.uniform(geometry.TABLE_TOP - 0.05, geometry.TABLE_TOP + 0.1)),
                )
            s, ok, reason = logic.evaluate_state(rand_till, rand_slider, rand_tokens, resting=bool(rng.choice([True, False])))
            self.assertTrue(0.0 <= s <= 1.0)
            self.assertIsInstance(ok, bool)


class TestTaskFileContract(unittest.TestCase):
    def test_task_file_loads(self):
        task_path = _TASK_DIR / "task.py"
        t = yam_arena.task_file.load(str(task_path))
        self.assertEqual(t.scene, "station")
        self.assertAlmostEqual(t.table_top, 0.7475)
        self.assertEqual(t.success_hold_s, 1.0)
        self.assertIn("till_body", [o.name for o in t.objects])
        self.assertIn("change_tray", [o.name for o in t.objects])

    def test_scoring_wrappers(self):
        objects = {
            "till_body": DummyObject(geometry.TILL_POS_WORLD, {"till_drawer": 0.0}),
            "change_tray": DummyObject(geometry.TRAY_POS_WORLD),
        }
        for name, z in zip(geometry.TOKEN_A_NAMES, geometry.TOKEN_A_Z_STARTS):
            objects[name] = DummyObject((geometry.TOKEN_A_XY[0], geometry.TOKEN_A_XY[1], geometry.TABLE_TOP + z))
        for name, z in zip(geometry.TOKEN_B_NAMES, geometry.TOKEN_B_Z_STARTS):
            objects[name] = DummyObject((geometry.TOKEN_B_XY[0], geometry.TOKEN_B_XY[1], geometry.TABLE_TOP + z))

        self.assertEqual(scoring.score(objects), 0.0)
        self.assertFalse(scoring.success(objects))


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
