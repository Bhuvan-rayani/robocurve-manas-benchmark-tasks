"""Unit and integration tests for dip_address_setting task."""

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
        self.assertEqual(len(geometry.KNOB_NAMES), 4)
        self.assertEqual(len(geometry.TARGET_PATTERN), 4)
        self.assertEqual(geometry.TARGET_PATTERN, (1, 0, 0, 1))
        self.assertEqual(geometry.START_PATTERN, (0, 1, 1, 0))

    def test_object_no_initial_overlap(self):
        # Module bounding box
        mx, my, mz = geometry.MODULE_POS_WORLD
        sx, sy, sz = geometry.MODULE_DIMS_M
        m_min = (mx - sx / 2, my - sy / 2, mz)
        m_max = (mx + sx / 2, my + sy / 2, mz + sz)

        # Card bounding box
        cx, cy, cz = geometry.CARD_POS_WORLD
        csx, csy, csz = geometry.CARD_SIZE_M
        c_min = (cx - csx / 2, cy - csy / 2, cz)
        c_max = (cx + csx / 2, cy + csy / 2, cz + csz)

        # Check XY separation
        overlap_x = (m_min[0] < c_max[0]) and (m_max[0] > c_min[0])
        overlap_y = (m_min[1] < c_max[1]) and (m_max[1] > c_min[1])
        self.assertFalse(overlap_x and overlap_y, "Module and card overlap at start")


class TestScoringLogic(unittest.TestCase):
    def test_first_update_on_real_start_pose(self):
        # Starting pose: module at start, all switches at 0 (complement start: 0 correct)
        score, ok, reason = logic.evaluate_state(
            geometry.MODULE_POS_WORLD,
            {k: 0.0 for k in geometry.KNOB_NAMES},
            resting=True,
        )
        self.assertEqual(score, 0.0, "First scorer update on start pose must give 0.0")
        self.assertFalse(ok, "First scorer update must have success=False")

    def test_partial_credit_one_switch(self):
        # 1 switch corrected (knob 1 flicked along +x)
        sliders = {"addr_knob_1": 0.010, "addr_knob_2": 0.0, "addr_knob_3": 0.0, "addr_knob_4": 0.0}
        score, ok, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sliders)
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_partial_credit_two_switches_reachable_05(self):
        # 2 switches corrected (knob 1 flicked +x, knob 4 flicked +x) -> exactly 0.50!
        sliders = {"addr_knob_1": 0.010, "addr_knob_2": 0.0, "addr_knob_3": 0.0, "addr_knob_4": 0.010}
        score, ok, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sliders)
        self.assertEqual(score, 0.50, "0.50 level must be reachable for 2 correct switches")
        self.assertFalse(ok)

    def test_partial_credit_three_switches(self):
        # 3 switches corrected (knobs 1, 2, 4 corrected) -> stays 0.50
        sliders = {"addr_knob_1": 0.010, "addr_knob_2": 0.010, "addr_knob_3": 0.0, "addr_knob_4": 0.010}
        score, ok, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sliders)
        self.assertEqual(score, 0.50)
        self.assertFalse(ok)

    def test_all_switches_correct_no_button(self):
        # All 4 switches corrected (knobs 1 & 4 flicked +x, knobs 2 & 3 pushed -x)
        sliders = {"addr_knob_1": 0.010, "addr_knob_2": 0.010, "addr_knob_3": 0.010, "addr_knob_4": 0.010}
        score, ok, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sliders)
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_full_success(self):
        # All 4 switches corrected and button pressed >= 6.4 mm
        sliders = {
            "addr_knob_1": 0.010,
            "addr_knob_2": 0.010,
            "addr_knob_3": 0.010,
            "addr_knob_4": 0.010,
            "addr_button": -0.007,
        }
        score, ok, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sliders, resting=True)
        self.assertEqual(score, 1.0)
        self.assertTrue(ok)

    def test_two_different_valid_solutions_both_reach_full_score(self):
        # Solution A: minimum valid travel (10 mm on switches, 6.5 mm on button)
        sol_a = {"addr_knob_1": 0.010, "addr_knob_2": 0.010, "addr_knob_3": 0.010, "addr_knob_4": 0.010, "addr_button": -0.0065}
        # Solution B: full travel (15 mm on switches, 8 mm on button)
        sol_b = {"addr_knob_1": 0.015, "addr_knob_2": 0.014, "addr_knob_3": 0.015, "addr_knob_4": 0.014, "addr_button": -0.0080}

        s_a, ok_a, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sol_a, resting=True)
        s_b, ok_b, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sol_b, resting=True)
        self.assertEqual(s_a, 1.0)
        self.assertTrue(ok_a)
        self.assertEqual(s_b, 1.0)
        self.assertTrue(ok_b)

    def test_commit_button_with_wrong_pattern_gives_zero(self):
        # Button pressed with wrong switches (only 1 or 2 correct)
        sliders = {"addr_knob_1": 0.010, "addr_knob_2": 0.0, "addr_knob_3": 0.0, "addr_knob_4": 0.0, "addr_button": -0.007}
        score, ok, _ = logic.evaluate_state(geometry.MODULE_POS_WORLD, sliders)
        self.assertEqual(score, 0.0, "Pressing commit with wrong pattern must trigger Gate 2 (0.0)")

    def test_module_drift_gates(self):
        # Pattern correct, but module drifted 20 mm (> 15 mm)
        drifted_pos = (geometry.MODULE_POS_WORLD[0] + 0.020, geometry.MODULE_POS_WORLD[1], geometry.MODULE_POS_WORLD[2])
        sliders = {"addr_knob_1": 0.010, "addr_knob_2": 0.010, "addr_knob_3": 0.010, "addr_knob_4": 0.010, "addr_button": -0.007}
        score, ok, _ = logic.evaluate_state(drifted_pos, sliders)
        self.assertEqual(score, 0.0)

        # Module drifted > 50 mm (gate)
        gate_drift_pos = (geometry.MODULE_POS_WORLD[0] + 0.060, geometry.MODULE_POS_WORLD[1], geometry.MODULE_POS_WORLD[2])
        score, ok, _ = logic.evaluate_state(gate_drift_pos, sliders)
        self.assertEqual(score, 0.0)

    def test_fuzz_scoring(self):
        rng = np.random.default_rng(42)
        for _ in range(500):
            rand_pos = (
                float(rng.uniform(0.1, 0.5)),
                float(rng.uniform(-0.3, 0.3)),
                float(rng.uniform(0.7, 0.9)),
            )
            rand_sliders = {
                "addr_knob_1": float(rng.uniform(-0.005, 0.020)),
                "addr_knob_2": float(rng.uniform(-0.005, 0.020)),
                "addr_knob_3": float(rng.uniform(-0.005, 0.020)),
                "addr_knob_4": float(rng.uniform(-0.005, 0.020)),
                "addr_button": float(rng.uniform(-0.015, 0.005)),
            }
            s, ok, reason = logic.evaluate_state(rand_pos, rand_sliders, resting=bool(rng.choice([True, False])))
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
        self.assertIn("addr_module", names)
        self.assertIn("dot_card", names)

    def test_scoring_wrappers(self):
        objects = {
            "addr_module": DummyState(geometry.MODULE_POS_WORLD, {k: 0.0 for k in geometry.KNOB_NAMES})
        }
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
