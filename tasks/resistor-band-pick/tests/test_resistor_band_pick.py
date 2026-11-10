"""Unit and integration tests for resistor_band_pick task."""

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
    def test_dimensions_and_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertEqual(len(geometry.RES_NAMES), 6)
        self.assertEqual(geometry.TARGET_RES_NAME, "res_c")
        self.assertEqual(len(geometry.TRAY_BOXES), 30)
        self.assertEqual(len(geometry.BOARD_BOXES), 16)

    def test_resistor_spacing(self):
        # Pick spacing rule: >= 100 mm between pick targets
        coords = list(geometry.RES_POCKET_COORDS.values())
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                d = np.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])
                self.assertGreaterEqual(
                    d,
                    0.099,
                    f"Pick spacing between resistors {i} and {j} too small: {d * 1000:.1f} mm < 100 mm",
                )

    def test_object_no_initial_overlap(self):
        # Tray bbox in XY
        tx, ty, _ = geometry.TRAY_POS_WORLD
        tsx, tsy, _ = geometry.TRAY_DIMS_M
        t_min = (tx - tsx / 2, ty - tsy / 2)
        t_max = (tx + tsx / 2, ty + tsy / 2)

        # Board bbox in XY
        bx, by, _ = geometry.BOARD_POS_WORLD
        bsx, bsy, _ = geometry.BOARD_DIMS_M
        b_min = (bx - bsx / 2, by - bsy / 2)
        b_max = (bx + bsx / 2, by + bsy / 2)

        # Card bbox in XY
        cx, cy, _ = geometry.CARD_POS_WORLD
        csx, csy, _ = geometry.CARD_DIMS_M
        c_min = (cx - csx / 2, cy - csy / 2)
        c_max = (cx + csx / 2, cy + csy / 2)

        # Tray vs Board
        overlap_tb = (t_min[0] < b_max[0] and t_max[0] > b_min[0]) and (
            t_min[1] < b_max[1] and t_max[1] > b_min[1]
        )
        self.assertFalse(overlap_tb, "Tray and socket board overlap at start")

        # Board vs Card
        overlap_bc = (b_min[0] < c_max[0] and b_max[0] > c_min[0]) and (
            b_min[1] < c_max[1] and b_max[1] > c_min[1]
        )
        self.assertFalse(overlap_bc, "Socket board and colour card overlap at start")

        # Tray vs Card
        overlap_tc = (t_min[0] < c_max[0] and t_max[0] > c_min[0]) and (
            t_min[1] < c_max[1] and t_max[1] > c_min[1]
        )
        self.assertFalse(overlap_tc, "Tray and colour card overlap at start")


class TestScoringLogic(unittest.TestCase):
    def test_first_update_on_real_start_pose(self):
        # Starting pose: board at start, all resistors in pockets, cover closed
        score, ok, reason = logic.evaluate_state(
            geometry.BOARD_POS_WORLD,
            geometry.RES_START_POSITIONS,
            cover_disp=0.0,
            resting=True,
        )
        self.assertEqual(score, 0.0, "First scorer update on start pose must give 0.0")
        self.assertFalse(ok, "First scorer update must have success=False")

    def test_partial_credit_any_resistor_lifted(self):
        # Non-target resistor lifted > 2 cm
        res_positions = dict(geometry.RES_START_POSITIONS)
        r_a = res_positions["res_a"]
        res_positions["res_a"] = (r_a[0], r_a[1], r_a[2] + 0.030)

        score, ok, _ = logic.evaluate_state(geometry.BOARD_POS_WORLD, res_positions)
        self.assertEqual(score, 0.25)
        self.assertFalse(ok)

    def test_partial_credit_target_resistor_lifted(self):
        # Target resistor res_c lifted > 2 cm
        res_positions = dict(geometry.RES_START_POSITIONS)
        r_c = res_positions["res_c"]
        res_positions["res_c"] = (r_c[0], r_c[1], r_c[2] + 0.030)

        score, ok, _ = logic.evaluate_state(geometry.BOARD_POS_WORLD, res_positions)
        self.assertEqual(score, 0.50)
        self.assertFalse(ok)

    def test_partial_credit_target_resistor_over_socket(self):
        # Target resistor res_c positioned over socket within 8 mm (lifted)
        res_positions = dict(geometry.RES_START_POSITIONS)
        sx, sy = geometry.SOCKET_HOLE_WORLD_XY
        res_positions["res_c"] = (sx + 0.005, sy - 0.003, geometry.TABLE_TOP + 0.095)

        score, ok, _ = logic.evaluate_state(geometry.BOARD_POS_WORLD, res_positions)
        self.assertEqual(score, 0.75)
        self.assertFalse(ok)

    def test_full_success(self):
        # res_c seated in socket (base at table top, top at 70 mm < 80 mm rim), cover shut, resting
        res_positions = dict(geometry.RES_START_POSITIONS)
        sx, sy = geometry.SOCKET_HOLE_WORLD_XY
        res_positions["res_c"] = (sx, sy, geometry.TABLE_TOP + geometry.RES_HEIGHT_M / 2)

        score, ok, reason = logic.evaluate_state(
            geometry.BOARD_POS_WORLD,
            res_positions,
            cover_disp=0.001,
            resting=True,
        )
        self.assertEqual(score, 1.0)
        self.assertTrue(ok)

    def test_two_different_valid_solutions_both_reach_full_score(self):
        # Solution A: seated at bottom (base at z=0), cover disp 0.001 m
        sx, sy = geometry.SOCKET_HOLE_WORLD_XY
        pos_a = dict(geometry.RES_START_POSITIONS)
        pos_a["res_c"] = (sx + 0.002, sy - 0.001, geometry.TABLE_TOP + 0.035)

        # Solution B: seated 72 mm deep (base at z=0.008), cover disp -0.002 m
        pos_b = dict(geometry.RES_START_POSITIONS)
        pos_b["res_c"] = (sx - 0.003, sy + 0.002, geometry.TABLE_TOP + 0.008 + 0.035)

        s_a, ok_a, _ = logic.evaluate_state(geometry.BOARD_POS_WORLD, pos_a, cover_disp=0.001, resting=True)
        s_b, ok_b, _ = logic.evaluate_state(geometry.BOARD_POS_WORLD, pos_b, cover_disp=-0.002, resting=True)
        self.assertEqual(s_a, 1.0)
        self.assertTrue(ok_a)
        self.assertEqual(s_b, 1.0)
        self.assertTrue(ok_b)

    def test_gate_wrong_resistor_in_socket(self):
        # Non-target resistor res_b placed into socket
        res_positions = dict(geometry.RES_START_POSITIONS)
        sx, sy = geometry.SOCKET_HOLE_WORLD_XY
        res_positions["res_b"] = (sx, sy, geometry.TABLE_TOP + 0.035)

        score, ok, reason = logic.evaluate_state(geometry.BOARD_POS_WORLD, res_positions)
        self.assertEqual(score, 0.0, "Wrong resistor in socket must trigger gate (score=0)")
        self.assertFalse(ok)
        self.assertIn("gate", reason.lower())

    def test_gate_board_drift(self):
        # Board drifted > 5 mm
        drifted_board = (geometry.BOARD_POS_WORLD[0] + 0.008, geometry.BOARD_POS_WORLD[1], geometry.BOARD_POS_WORLD[2])
        res_positions = dict(geometry.RES_START_POSITIONS)
        sx, sy = geometry.SOCKET_HOLE_WORLD_XY
        res_positions["res_c"] = (sx, sy, geometry.TABLE_TOP + 0.035)

        score, ok, reason = logic.evaluate_state(drifted_board, res_positions, cover_disp=0.0, resting=True)
        self.assertEqual(score, 0.0, "Board drift > 5 mm must trigger gate (score=0)")
        self.assertFalse(ok)
        self.assertIn("gate", reason.lower())

    def test_cover_open_prevents_full_score(self):
        # Resistor seated, but cover is still held open (disp 0.020 m > 0.003 m)
        res_positions = dict(geometry.RES_START_POSITIONS)
        sx, sy = geometry.SOCKET_HOLE_WORLD_XY
        res_positions["res_c"] = (sx, sy, geometry.TABLE_TOP + 0.035)

        score, ok, _ = logic.evaluate_state(geometry.BOARD_POS_WORLD, res_positions, cover_disp=0.020, resting=True)
        self.assertLess(score, 1.0, "Unclosed cover must not reach 1.0 score")
        self.assertFalse(ok)

    def test_fuzz_scoring(self):
        # 500 random inputs must never crash and scores must remain within [0.0, 1.0]
        rng = np.random.default_rng(42)
        for _ in range(500):
            rand_board = (
                float(rng.uniform(0.25, 0.35)),
                float(rng.uniform(-0.15, 0.05)),
                float(rng.uniform(0.70, 0.80)),
            )
            rand_res = {
                name: (
                    float(rng.uniform(0.10, 0.40)),
                    float(rng.uniform(-0.25, 0.35)),
                    float(rng.uniform(0.70, 0.95)),
                )
                for name in geometry.RES_NAMES
            }
            rand_cover = float(rng.uniform(-0.010, 0.050))
            rand_resting = bool(rng.choice([True, False]))

            s, ok, reason = logic.evaluate_state(rand_board, rand_res, cover_disp=rand_cover, resting=rand_resting)
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
        self.assertIn("socket_board", names)
        self.assertIn("part_tray", names)
        self.assertIn("res_c", names)
        self.assertIn("colour_card", names)

    def test_scoring_wrappers(self):
        objects = {
            "socket_board": DummyState(geometry.BOARD_POS_WORLD, {"socket_cover": 0.0}),
            "part_tray": DummyState(geometry.TRAY_POS_WORLD),
            **{name: DummyState(pos) for name, pos in geometry.RES_START_POSITIONS.items()},
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
