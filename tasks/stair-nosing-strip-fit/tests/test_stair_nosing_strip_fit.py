"""Unit and integration tests for stair_nosing_strip_fit task."""

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
    if str(p) not in sys.path and p.exists():
        sys.path.insert(0, str(p))

import geometry
import logic
import scoring
import demo_plan
import yam_arena.task_file


class DummyPartState:
    def __init__(self, pos, quat_xyzw=(0.0, 0.0, 0.0, 1.0), resting=True):
        self.pos = tuple(float(v) for v in pos)
        self.quat_xyzw = tuple(float(v) for v in quat_xyzw)
        self._resting = resting

    def resting(self):
        return self._resting


class TestGeometry(unittest.TestCase):
    def test_dimensions_and_masses(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.STAIR_STEP_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.STRIP_PAD_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.NOSING_STRIP_MASS_KG, 0.15)

        self.assertEqual(geometry.STAIR_STEP_POS_WORLD, (0.36, 0.0, 0.7475))
        self.assertEqual(geometry.STRIP_PAD_POS_WORLD, (0.18, 0.0, 0.7475))
        self.assertEqual(geometry.NOSING_STRIP_START_POS_WORLD, (0.18, 0.0, 0.7475 + 0.010))

    def test_dual_carry_separation(self):
        self.assertAlmostEqual(geometry.DUAL_CARRY_SEPARATION_M, 0.320)
        self.assertGreaterEqual(geometry.DUAL_CARRY_SEPARATION_M, 0.150)


class TestScoringLogic(unittest.TestCase):
    def test_first_update_zero(self):
        s, ok, reason = logic.evaluate_state(
            step_pos=geometry.STAIR_STEP_POS_WORLD,
            pad_pos=geometry.STRIP_PAD_POS_WORLD,
            strip_pos=geometry.NOSING_STRIP_START_POS_WORLD,
            strip_quat_xyzw=(0.0, 0.0, 0.0, 1.0),
            resting=True,
        )
        self.assertEqual(s, 0.0, "First scorer update must evaluate to 0.0")
        self.assertFalse(ok, "First scorer update must have success=False")

    def test_idle_policy_zero(self):
        objects = {
            "stair_step": DummyPartState(geometry.STAIR_STEP_POS_WORLD),
            "strip_pad": DummyPartState(geometry.STRIP_PAD_POS_WORLD),
            "nosing_strip": DummyPartState(geometry.NOSING_STRIP_START_POS_WORLD),
        }
        self.assertEqual(scoring.score(objects), 0.0)
        self.assertFalse(scoring.success(objects))

    def test_all_ladder_levels_reachable(self):
        # 0.00: start
        s0, ok0, _ = logic.evaluate_state(strip_pos=geometry.NOSING_STRIP_START_POS_WORLD)
        self.assertEqual(s0, 0.0)
        self.assertFalse(ok0)

        # 0.25: lifted > 3 cm off pad (z >= TABLE_TOP + 0.040)
        lifted_pos = (0.18, 0.0, geometry.TABLE_TOP + 0.045)
        s25, ok25, _ = logic.evaluate_state(strip_pos=lifted_pos)
        self.assertEqual(s25, 0.25)
        self.assertFalse(ok25)

        # 0.50: brought over step front edge (x in [0.26, 0.33])
        over_edge_pos = (0.280, 0.0, geometry.TABLE_TOP + 0.090)
        s50, ok50, _ = logic.evaluate_state(strip_pos=over_edge_pos)
        self.assertEqual(s50, 0.50)
        self.assertFalse(ok50)

        # 0.75: front lip engaged near front face (flange z <= TABLE_TOP + 75 mm, tilt <= 6 deg)
        engaged_pos = (0.295, 0.0, geometry.TABLE_TOP + 0.060)
        s75, ok75, _ = logic.evaluate_state(strip_pos=engaged_pos)
        self.assertEqual(s75, 0.75)
        self.assertFalse(ok75)

        # 1.00: fully seated flush on tread (|dz| <= 2.5 mm, |dx| <= 3.0 mm, |dy| <= 4.0 mm, tilt <= 3 deg)
        seated_pos = geometry.NOSING_STRIP_TARGET_POS_WORLD
        s100, ok100, _ = logic.evaluate_state(strip_pos=seated_pos, resting=True)
        self.assertEqual(s100, 1.0)
        self.assertTrue(ok100)

    def test_dual_solutions_reach_full_score(self):
        # Solution 1: nominal target position
        s1, ok1, _ = logic.evaluate_state(
            strip_pos=geometry.NOSING_STRIP_TARGET_POS_WORLD,
            strip_quat_xyzw=(0.0, 0.0, 0.0, 1.0),
            resting=True,
        )
        self.assertEqual(s1, 1.0)
        self.assertTrue(ok1)

        # Solution 2: slight valid offset (dx = +1.5 mm, dy = -2.0 mm, dz = +1.0 mm, tilt = 1 deg)
        half_ang = np.radians(0.5)
        quat_b = (float(np.sin(half_ang)), 0.0, 0.0, float(np.cos(half_ang)))
        sol2_pos = (
            geometry.NOSING_STRIP_TARGET_POS_WORLD[0] + 0.0015,
            geometry.NOSING_STRIP_TARGET_POS_WORLD[1] - 0.0020,
            geometry.NOSING_STRIP_TARGET_POS_WORLD[2] + 0.0010,
        )
        s2, ok2, _ = logic.evaluate_state(
            strip_pos=sol2_pos,
            strip_quat_xyzw=quat_b,
            resting=True,
        )
        self.assertEqual(s2, 1.0)
        self.assertTrue(ok2)

    def test_failure_gates(self):
        # Gate: stair_step drifted 6 mm
        drifted_step = (
            geometry.STAIR_STEP_POS_WORLD[0] + 0.006,
            geometry.STAIR_STEP_POS_WORLD[1],
            geometry.STAIR_STEP_POS_WORLD[2],
        )
        s, ok, reason = logic.evaluate_state(
            step_pos=drifted_step,
            strip_pos=geometry.NOSING_STRIP_TARGET_POS_WORLD,
            resting=True,
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("gate", reason.lower())

        # Gate: strip dropped below table
        dropped_strip = (0.295, 0.0, geometry.TABLE_TOP - 0.05)
        s, ok, reason = logic.evaluate_state(strip_pos=dropped_strip)
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("gate", reason.lower())

        # Gate: strip overturned (tilt > 45 deg)
        # 60 deg rotation around Y
        ang = np.radians(30.0)
        inv_quat = (0.0, float(np.sin(ang)), 0.0, float(np.cos(ang)))
        s, ok, reason = logic.evaluate_state(
            strip_pos=geometry.NOSING_STRIP_TARGET_POS_WORLD,
            strip_quat_xyzw=inv_quat,
            resting=True,
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("gate", reason.lower())

    def test_fuzz_scoring(self):
        rng = np.random.default_rng(42)
        for _ in range(500):
            r_step = (
                float(rng.uniform(0.34, 0.38)),
                float(rng.uniform(-0.02, 0.02)),
                geometry.TABLE_TOP,
            )
            r_strip = (
                float(rng.uniform(0.15, 0.35)),
                float(rng.uniform(-0.05, 0.05)),
                float(rng.uniform(0.70, 0.95)),
            )
            q_raw = rng.normal(size=4)
            quat = tuple(float(v) for v in (q_raw / np.linalg.norm(q_raw)))
            s, ok, reason = logic.evaluate_state(
                step_pos=r_step,
                strip_pos=r_strip,
                strip_quat_xyzw=quat,
                resting=bool(rng.choice([True, False])),
            )
            self.assertTrue(0.0 <= s <= 1.0)
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
        self.assertIn("stair_step", names)
        self.assertIn("strip_pad", names)
        self.assertIn("nosing_strip", names)

    def test_scoring_wrappers(self):
        objects = {
            "stair_step": DummyPartState(geometry.STAIR_STEP_POS_WORLD),
            "strip_pad": DummyPartState(geometry.STRIP_PAD_POS_WORLD),
            "nosing_strip": DummyPartState(geometry.NOSING_STRIP_TARGET_POS_WORLD),
        }
        self.assertEqual(scoring.score(objects), 1.0)
        self.assertTrue(scoring.success(objects))
        self.assertAlmostEqual(scoring.distance(objects), 0.0)


class TestDemoPlans(unittest.TestCase):
    def test_modes_and_step_lengths(self):
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

        from yam_arena.constants import LEFT_BASE_POS, RIGHT_BASE_POS
        from yam_arena.demo import ArmPlan

        lp = ArmPlan(p_demo["left"], LEFT_BASE_POS)
        rp = ArmPlan(p_demo["right"], RIGHT_BASE_POS)
        total_s = max(lp.duration, rp.duration)
        steps = int(np.ceil(total_s / 0.05))
        self.assertTrue(
            600 <= steps <= 1200,
            f"Demo plan steps {steps} outside 600-1200 target range",
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
