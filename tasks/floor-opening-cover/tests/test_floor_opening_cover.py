"""Unit and integration tests for floor_opening_cover task."""

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
    def __init__(self, pos, quat_xyzw=None, resting=True):
        self.pos = pos
        self.quat_xyzw = quat_xyzw
        self._resting = resting

    def resting(self):
        return self._resting


class TestGeometry(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.BOARD_POS_WORLD[0], 0.30)
        self.assertAlmostEqual(geometry.BOARD_POS_WORLD[1], 0.0)
        self.assertAlmostEqual(geometry.BOARD_DIMS_M[0], 0.34)
        self.assertAlmostEqual(geometry.BOARD_DIMS_M[1], 0.44)
        self.assertAlmostEqual(geometry.BOARD_DIMS_M[2], 0.05)
        self.assertAlmostEqual(geometry.PLATE_DIMS_M[0], 0.22)
        self.assertAlmostEqual(geometry.PLATE_DIMS_M[1], 0.22)
        self.assertAlmostEqual(geometry.PLATE_DIMS_M[2], 0.01)

    def test_opening_and_slot_dimensions(self):
        dx = geometry.OPENING_X_MAX - geometry.OPENING_X_MIN
        dy = geometry.OPENING_Y_MAX - geometry.OPENING_Y_MIN
        self.assertAlmostEqual(dx, 0.16, places=3, msg="Opening must be 16 cm in x")
        self.assertAlmostEqual(dy, 0.16, places=3, msg="Opening must be 16 cm in y")

        # Slots at x = 0.24, y = +/-13 cm, 26 mm square
        self.assertAlmostEqual(geometry.SLOT_A_POS[0], 0.24, places=3)
        self.assertAlmostEqual(geometry.SLOT_A_POS[1], 0.13, places=3)
        self.assertAlmostEqual(geometry.SLOT_B_POS[1], -0.13, places=3)
        self.assertAlmostEqual(geometry.SLOT_SIZE_M[0], 0.026, places=4)

    def test_handle_and_slot_clearance(self):
        self.assertAlmostEqual(geometry.HANDLE_DIMS_M[0], 0.04)
        self.assertAlmostEqual(geometry.HANDLE_DIMS_M[1], 0.08)
        self.assertAlmostEqual(geometry.HANDLE_DIMS_M[2], 0.02)
        self.assertLess(geometry.HANDLE_DIMS_M[0], 0.094)  # gripper opening
        per_side = (geometry.SLOT_SIZE_M[0] - geometry.PIN_DIMS_M[0]) / 2.0
        self.assertGreaterEqual(per_side, 0.007 - 1e-9)
        # pin on the rack, rack top flush with pin bottom
        self.assertAlmostEqual(geometry.PIN_A_START_POS[2] - geometry.PIN_HALF_Z, geometry.LRACK_POS_WORLD[2] + geometry.LRACK_DIMS_M[2] / 2)
        self.assertAlmostEqual(geometry.PIN_B_START_POS[2] - geometry.PIN_HALF_Z, geometry.RACK_POS_WORLD[2] + geometry.RACK_DIMS_M[2] / 2)

    def test_centred_overhang(self):
        min_ov, w, e, s, n = logic.compute_overhang(geometry.PLATE_GOAL_POS)
        self.assertAlmostEqual(min_ov, 0.030, places=3, msg="Centred overhang should be 30 mm")
        self.assertGreaterEqual(min_ov, geometry.MIN_OVERHANG_M)


class TestScoringLogic(unittest.TestCase):
    def setUp(self):
        self.board_pos = geometry.BOARD_POS_WORLD
        self.plate_start = geometry.PLATE_START_POS
        self.pin_a_start = geometry.PIN_A_START_POS
        self.pin_b_start = geometry.PIN_B_START_POS

    def test_first_update_on_real_start_pose(self):
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            self.plate_start,
            self.pin_a_start,
            self.pin_b_start,
            resting=True,
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_partial_credit_plate_lifted(self):
        lifted_plate = (self.plate_start[0], self.plate_start[1], self.plate_start[2] + 0.025)
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            lifted_plate,
            self.pin_a_start,
            self.pin_b_start,
            resting=True,
        )
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_partial_credit_plate_over_opening(self):
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            self.pin_a_start,
            self.pin_b_start,
            resting=True,
        )
        self.assertEqual(score, 0.50)
        self.assertFalse(ok)

    def test_partial_credit_one_pin_seated(self):
        # Slot B seated with pin b
        seated_pin_b = (geometry.SLOT_B_POS[0], geometry.SLOT_B_POS[1], geometry.TABLE_TOP + 0.055)
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            self.pin_a_start,
            seated_pin_b,
            resting=True,
        )
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_full_success_both_pins_seated(self):
        seated_pin_a = (geometry.SLOT_A_POS[0], geometry.SLOT_A_POS[1], geometry.TABLE_TOP + 0.055)
        seated_pin_b = (geometry.SLOT_B_POS[0], geometry.SLOT_B_POS[1], geometry.TABLE_TOP + 0.055)
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            seated_pin_a,
            seated_pin_b,
            plate_quat=(0.0, 0.0, 0.0, 1.0),
            resting=True,
        )
        self.assertEqual(score, 1.00)
        self.assertTrue(ok)

    def test_two_different_valid_solutions_both_reach_full_score(self):
        # Solution A: Pin A in Slot A, Pin B in Slot B
        seated_a_in_a = (geometry.SLOT_A_POS[0], geometry.SLOT_A_POS[1], geometry.TABLE_TOP + 0.055)
        seated_b_in_b = (geometry.SLOT_B_POS[0], geometry.SLOT_B_POS[1], geometry.TABLE_TOP + 0.055)
        s_a, ok_a, _ = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            seated_a_in_a,
            seated_b_in_b,
            resting=True,
        )

        # Solution B: Pin B in Slot A, Pin A in Slot B (swapped pins)
        seated_b_in_a = (geometry.SLOT_A_POS[0], geometry.SLOT_A_POS[1], geometry.TABLE_TOP + 0.055)
        seated_a_in_b = (geometry.SLOT_B_POS[0], geometry.SLOT_B_POS[1], geometry.TABLE_TOP + 0.055)
        s_b, ok_b, _ = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            seated_a_in_b,
            seated_b_in_a,
            resting=True,
        )

        self.assertEqual(s_a, 1.0)
        self.assertTrue(ok_a)
        self.assertEqual(s_b, 1.0)
        self.assertTrue(ok_b)

    def test_board_drift_gate(self):
        drifted_board = (self.board_pos[0] + 0.008, self.board_pos[1], self.board_pos[2])
        score, ok, reason = logic.evaluate_state(
            drifted_board,
            geometry.PLATE_GOAL_POS,
            geometry.SLOT_A_POS,
            geometry.SLOT_B_POS,
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_plate_drop_into_pit_gate(self):
        # Plate dropped into pit below board top
        pit_plate = (0.30, 0.0, geometry.TABLE_TOP + 0.020)
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            pit_plate,
            self.pin_a_start,
            self.pin_b_start,
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_pin_fall_off_table_gate(self):
        fallen_pin = (0.16, -0.28, geometry.TABLE_TOP - 0.050)
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            fallen_pin,
            self.pin_b_start,
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_plate_tilt_threshold(self):
        seated_pin_a = (geometry.SLOT_A_POS[0], geometry.SLOT_A_POS[1], geometry.TABLE_TOP + 0.055)
        seated_pin_b = (geometry.SLOT_B_POS[0], geometry.SLOT_B_POS[1], geometry.TABLE_TOP + 0.055)

        # 2 degrees tilt (within 3 degrees) -> 1.0
        # rot around x by 2 deg: qx = sin(1 deg), qw = cos(1 deg)
        ang_rad = np.radians(2.0)
        quat_2deg = (float(np.sin(ang_rad / 2)), 0.0, 0.0, float(np.cos(ang_rad / 2)))
        s_ok, ok_2deg, _ = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            seated_pin_a,
            seated_pin_b,
            plate_quat=quat_2deg,
            resting=True,
        )
        self.assertEqual(s_ok, 1.00)
        self.assertTrue(ok_2deg)

        # 5 degrees tilt (exceeds 3 degrees) -> partial credit 0.75
        ang_rad_5 = np.radians(5.0)
        quat_5deg = (float(np.sin(ang_rad_5 / 2)), 0.0, 0.0, float(np.cos(ang_rad_5 / 2)))
        s_tilt, ok_5deg, _ = logic.evaluate_state(
            self.board_pos,
            geometry.PLATE_GOAL_POS,
            seated_pin_a,
            seated_pin_b,
            plate_quat=quat_5deg,
            resting=True,
        )
        self.assertEqual(s_tilt, 0.75)
        self.assertFalse(ok_5deg)

    def test_insufficient_overhang_threshold(self):
        # Shift plate in x so overhang on west side is 15 mm (< 20 mm)
        # Centred overhang is 30 mm, shifting by 15 mm gives 15 mm overhang
        shifted_plate = (geometry.PLATE_GOAL_POS[0] + 0.015, geometry.PLATE_GOAL_POS[1], geometry.PLATE_GOAL_POS[2])
        score, ok, reason = logic.evaluate_state(
            self.board_pos,
            shifted_plate,
            self.pin_a_start,
            self.pin_b_start,
            resting=True,
        )
        # Should not get 0.50 credit due to insufficient overhang
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_fuzz_scoring(self):
        rng = np.random.default_rng(42)
        for _ in range(300):
            rand_board = (
                float(rng.uniform(0.28, 0.32)),
                float(rng.uniform(-0.02, 0.02)),
                geometry.TABLE_TOP,
            )
            rand_plate = (
                float(rng.uniform(0.1, 0.4)),
                float(rng.uniform(-0.1, 0.4)),
                float(rng.uniform(geometry.TABLE_TOP - 0.05, geometry.TABLE_TOP + 0.2)),
            )
            rand_pin_a = (
                float(rng.uniform(0.1, 0.4)),
                float(rng.uniform(-0.4, 0.2)),
                float(rng.uniform(geometry.TABLE_TOP - 0.05, geometry.TABLE_TOP + 0.2)),
            )
            rand_pin_b = (
                float(rng.uniform(0.1, 0.4)),
                float(rng.uniform(-0.4, 0.2)),
                float(rng.uniform(geometry.TABLE_TOP - 0.05, geometry.TABLE_TOP + 0.2)),
            )
            s, ok, reason = logic.evaluate_state(
                rand_board,
                rand_plate,
                rand_pin_a,
                rand_pin_b,
                resting=bool(rng.choice([True, False])),
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
        self.assertIn("floor_board", obj_names)
        self.assertIn("cover_plate", obj_names)
        self.assertIn("plate_stand", obj_names)
        self.assertIn("wedge_pin_a", obj_names)
        self.assertIn("wedge_pin_b", obj_names)
        self.assertIn("pin_rack", obj_names)
        self.assertIn("pin_rack_left", obj_names)

    def test_scoring_wrappers(self):
        objects = {
            "floor_board": DummyObject(geometry.BOARD_POS_WORLD),
            "cover_plate": DummyObject(geometry.PLATE_START_POS),
            "plate_stand": DummyObject(geometry.STAND_POS_WORLD),
            "wedge_pin_a": DummyObject(geometry.PIN_A_START_POS),
            "wedge_pin_b": DummyObject(geometry.PIN_B_START_POS),
            "pin_rack": DummyObject(geometry.RACK_POS_WORLD),
            "pin_rack_left": DummyObject(geometry.LRACK_POS_WORLD),
        }
        self.assertEqual(scoring.score(objects), 0.0)
        self.assertFalse(scoring.success(objects))
        self.assertAlmostEqual(scoring.distance(objects), 0.10)


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
        self.assertGreater(len(p_demo["left"]), 10)
        self.assertGreater(len(p_demo["right"]), 8)
        # each arm stays on its own side while working (ready poses are at |y| = 0.20)
        for w in p_demo["right"]:
            self.assertLess(w.pos[1], -0.08)


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
