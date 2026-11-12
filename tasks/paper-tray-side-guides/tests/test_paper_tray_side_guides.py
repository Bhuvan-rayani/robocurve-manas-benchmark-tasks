"""Unit and integration tests for paper_tray_side_guides task."""

from __future__ import annotations

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
    def __init__(self, pos, sliders=None, quat_xyzw=(0.0, 0.0, 0.0, 1.0), resting=True):
        self.pos = pos
        self.sliders = sliders or {}
        self.quat_xyzw = quat_xyzw
        self._resting = resting

    def resting(self):
        return self._resting


class TestGeometry(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertEqual(geometry.FRAME_NAME, "printer_frame")
        self.assertEqual(geometry.TRAY_NAME, "feed_tray")
        self.assertEqual(geometry.PAPER_NAME, "paper_stack")
        self.assertAlmostEqual(geometry.TRAY_CLOSED_X, 0.240)

    def test_object_no_initial_overlap(self):
        # Printer frame bbox in XY: [0.28 - 0.17, 0.28 + 0.17] x [-0.20, +0.20] = [0.11, 0.45] x [-0.20, 0.20]
        # Paper pad bbox in XY: [0.14 - 0.085, 0.14 + 0.085] x [0.32 - 0.115, 0.32 + 0.115] = [0.055, 0.225] x [0.205, 0.435]
        # Frame Y is [-0.20, +0.20], Pad Y is [0.205, 0.435] -> NO overlap!
        frame_min_y = geometry.FRAME_POS_WORLD[1] - geometry.FRAME_DIMS_M[1] / 2
        frame_max_y = geometry.FRAME_POS_WORLD[1] + geometry.FRAME_DIMS_M[1] / 2
        pad_min_y = geometry.PAD_POS_WORLD[1] - geometry.PAD_SIZE_M[1] / 2
        pad_max_y = geometry.PAD_POS_WORLD[1] + geometry.PAD_SIZE_M[1] / 2

        y_overlap = (frame_min_y < pad_max_y) and (frame_max_y > pad_min_y)
        self.assertFalse(y_overlap, "Printer frame and paper pad must not overlap in Y at start")


class TestScoringLogic(unittest.TestCase):
    def setUp(self):
        self.frame_pos = geometry.FRAME_POS_WORLD
        self.tray_start_pos = geometry.TRAY_START_POS_WORLD
        self.paper_start_pos = geometry.PAPER_START_POS_WORLD
        self.sliders_start = {geometry.GUIDE_A_NAME: 0.0, geometry.GUIDE_B_NAME: 0.0}

    def test_first_update_on_real_start_pose(self):
        # Starting pose: paper on pad, tray open, guides wide
        score, ok, reason = logic.evaluate_state(
            self.frame_pos,
            self.tray_start_pos,
            self.paper_start_pos,
            self.sliders_start,
            resting=True,
        )
        self.assertEqual(score, 0.0, "First scorer update on start pose must give 0.0")
        self.assertFalse(ok, "First scorer update must have success=False")

    def test_partial_credit_paper_inside_tray(self):
        # Paper placed in open tray: tray at x=0.12, paper at (0.12, 0.0, TABLE_TOP + 0.029)
        paper_in_tray_pos = (0.12, 0.0, geometry.TABLE_TOP + 0.029)
        score, ok, reason = logic.evaluate_state(
            self.frame_pos,
            self.tray_start_pos,
            paper_in_tray_pos,
            self.sliders_start,
            resting=True,
        )
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_partial_credit_one_guide_touching(self):
        # Paper flat in tray, Guide A pushed inward 25 mm (disp = -0.025 m), Guide B at rest
        paper_in_tray_pos = (0.12, 0.0, geometry.TABLE_TOP + 0.029)
        sliders = {geometry.GUIDE_A_NAME: -0.025, geometry.GUIDE_B_NAME: 0.0}
        score, ok, reason = logic.evaluate_state(
            self.frame_pos,
            self.tray_start_pos,
            paper_in_tray_pos,
            sliders,
            resting=True,
        )
        self.assertEqual(score, 0.50)
        self.assertFalse(ok)

    def test_partial_credit_both_guides_and_centred(self):
        # Paper flat in tray, both guides pushed inward 25 mm, paper centred at y=0, tray still open
        paper_in_tray_pos = (0.12, 0.0, geometry.TABLE_TOP + 0.029)
        sliders = {geometry.GUIDE_A_NAME: -0.025, geometry.GUIDE_B_NAME: 0.025}
        score, ok, reason = logic.evaluate_state(
            self.frame_pos,
            self.tray_start_pos,
            paper_in_tray_pos,
            sliders,
            resting=True,
        )
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_full_success(self):
        # Paper in tray, both guides touching, centred, tray shut at x=0.240
        tray_shut_pos = (0.240, 0.0, geometry.TABLE_TOP + 0.010)
        paper_shut_pos = (0.240, 0.0, geometry.TABLE_TOP + 0.029)
        sliders = {geometry.GUIDE_A_NAME: -0.025, geometry.GUIDE_B_NAME: 0.025}
        score, ok, reason = logic.evaluate_state(
            self.frame_pos,
            tray_shut_pos,
            paper_shut_pos,
            sliders,
            resting=True,
        )
        self.assertEqual(score, 1.00)
        self.assertTrue(ok)

    def test_two_different_valid_solutions_both_reach_full_score(self):
        # Solution A: Nominal perfectly aligned
        tray_a = (0.240, 0.0, geometry.TABLE_TOP + 0.010)
        paper_a = (0.240, 0.0, geometry.TABLE_TOP + 0.029)
        sliders_a = {geometry.GUIDE_A_NAME: -0.025, geometry.GUIDE_B_NAME: 0.025}

        # Solution B: Slight 1 mm offsets within all tolerances
        tray_b = (0.239, 0.0, geometry.TABLE_TOP + 0.010)
        paper_b = (0.239, 0.001, geometry.TABLE_TOP + 0.029)
        # Guide A inner face at 0.130 - 0.024 = 0.106; paper top at 0.001 + 0.105 = 0.106 -> gap 0.0 mm
        # Guide B inner face at -0.130 + 0.026 = -0.104; paper bottom at 0.001 - 0.105 = -0.104 -> gap 0.0 mm
        sliders_b = {geometry.GUIDE_A_NAME: -0.024, geometry.GUIDE_B_NAME: 0.026}

        s_a, ok_a, _ = logic.evaluate_state(self.frame_pos, tray_a, paper_a, sliders_a, resting=True)
        s_b, ok_b, _ = logic.evaluate_state(self.frame_pos, tray_b, paper_b, sliders_b, resting=True)

        self.assertEqual(s_a, 1.0)
        self.assertTrue(ok_a)
        self.assertEqual(s_b, 1.0)
        self.assertTrue(ok_b)

    def test_tilted_paper_cannot_reach_0_5(self):
        # Paper tilted 10 degrees (> 5 deg threshold)
        paper_in_tray_pos = (0.12, 0.0, geometry.TABLE_TOP + 0.029)
        # Tilt around X: angle = 10 deg -> sin(5 deg) ~ 0.087, quat = (0.087, 0, 0, 0.996)
        tilted_quat = (0.087, 0.0, 0.0, 0.996)
        sliders = {geometry.GUIDE_A_NAME: -0.025, geometry.GUIDE_B_NAME: 0.0}
        score, ok, _ = logic.evaluate_state(
            self.frame_pos,
            self.tray_start_pos,
            paper_in_tray_pos,
            sliders,
            paper_quat=tilted_quat,
            resting=True,
        )
        self.assertEqual(score, 0.25, "Tilted paper must not pass flat check for score >= 0.5")

    def test_uncentred_paper_cannot_reach_0_75(self):
        # Paper shifted in Y by 5 mm (> 3 mm centring threshold)
        paper_uncentred = (0.12, 0.005, geometry.TABLE_TOP + 0.029)
        # Adjust guides to touch shifted paper
        # paper top at 0.005 + 0.105 = 0.110 -> disp_a = 0.130 - 0.110 = 0.020
        # paper bottom at 0.005 - 0.105 = -0.100 -> disp_b = 0.130 - 0.100 = 0.030
        sliders = {geometry.GUIDE_A_NAME: -0.020, geometry.GUIDE_B_NAME: 0.030}
        score, ok, _ = logic.evaluate_state(
            self.frame_pos,
            self.tray_start_pos,
            paper_uncentred,
            sliders,
            resting=True,
        )
        self.assertEqual(score, 0.50, "Uncentred paper (> 3 mm) must not reach 0.75")

    def test_printer_frame_drift_gate(self):
        # Frame drifted 8 mm (> 5 mm gate)
        drifted_frame = (geometry.FRAME_POS_WORLD[0] + 0.008, geometry.FRAME_POS_WORLD[1], geometry.FRAME_POS_WORLD[2])
        tray_shut = (0.240, 0.0, geometry.TABLE_TOP + 0.010)
        paper_shut = (0.240, 0.0, geometry.TABLE_TOP + 0.029)
        sliders = {geometry.GUIDE_A_NAME: -0.025, geometry.GUIDE_B_NAME: 0.025}
        score, ok, _ = logic.evaluate_state(drifted_frame, tray_shut, paper_shut, sliders, resting=True)
        self.assertEqual(score, 0.0, "Printer frame drift > 5 mm must zero score")

    def test_paper_fall_off_table_gate(self):
        # Paper dropped below table
        paper_fell = (0.14, 0.32, geometry.TABLE_TOP - 0.05)
        score, ok, _ = logic.evaluate_state(self.frame_pos, self.tray_start_pos, paper_fell, self.sliders_start)
        self.assertEqual(score, 0.0, "Paper below table must zero score")

    def test_fuzz_scoring(self):
        rng = np.random.default_rng(77)
        for _ in range(500):
            rand_frame = (
                float(rng.uniform(0.26, 0.30)),
                float(rng.uniform(-0.02, 0.02)),
                geometry.TABLE_TOP,
            )
            rand_tray = (
                float(rng.uniform(0.10, 0.26)),
                float(rng.uniform(-0.03, 0.03)),
                geometry.TABLE_TOP + 0.010,
            )
            rand_paper = (
                float(rng.uniform(0.08, 0.35)),
                float(rng.uniform(-0.15, 0.35)),
                float(rng.uniform(geometry.TABLE_TOP - 0.05, geometry.TABLE_TOP + 0.15)),
            )
            rand_sliders = {
                geometry.GUIDE_A_NAME: float(rng.uniform(-0.06, 0.01)),
                geometry.GUIDE_B_NAME: float(rng.uniform(-0.01, 0.06)),
            }
            s, ok, reason = logic.evaluate_state(
                rand_frame,
                rand_tray,
                rand_paper,
                rand_sliders,
                resting=bool(rng.choice([True, False])),
            )
            self.assertTrue(0.0 <= s <= 1.0, f"Score out of bounds: {s}")
            self.assertIsInstance(ok, bool)


class TestTaskFileContract(unittest.TestCase):
    def test_task_file_loads(self):
        task_path = _TASK_DIR / "task.py"
        t = yam_arena.task_file.load(str(task_path))
        self.assertEqual(t.scene, "station")
        self.assertAlmostEqual(t.table_top, 0.7475)
        self.assertEqual(t.success_hold_s, 1.0)
        names = [o.name for o in t.objects]
        self.assertIn("printer_frame", names)
        self.assertIn("feed_tray", names)
        self.assertIn("paper_stack", names)
        self.assertIn("paper_pad", names)

    def test_scoring_wrappers(self):
        objects = {
            "printer_frame": DummyObject(geometry.FRAME_POS_WORLD),
            "feed_tray": DummyObject(geometry.TRAY_START_POS_WORLD, {geometry.GUIDE_A_NAME: 0.0, geometry.GUIDE_B_NAME: 0.0}),
            "paper_stack": DummyObject(geometry.PAPER_START_POS_WORLD),
            "paper_pad": DummyObject(geometry.PAD_POS_WORLD),
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

    def test_plan_steps_within_limit(self):
        p = demo_plan.plans()
        left_dur = sum(w.duration for w in p["left"])
        right_dur = sum(w.duration for w in p["right"])
        total_steps = int(max(left_dur, right_dur) * 20)
        self.assertTrue(600 <= total_steps <= 1200, f"Plan steps {total_steps} outside 600-1200 range")


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
