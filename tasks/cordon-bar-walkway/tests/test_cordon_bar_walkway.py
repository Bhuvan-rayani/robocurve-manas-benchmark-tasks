"""Unit tests for cordon_bar_walkway (T26)."""
from __future__ import annotations

import pathlib
import sys
import unittest

_TASK_DIR = pathlib.Path(__file__).resolve().parent.parent
_UPSTREAM = _TASK_DIR.parents[2] / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
for p in (_TASK_DIR, _UPSTREAM):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import geometry
import logic
import scoring


class DummyObj:
    def __init__(self, pos, resting=True):
        self.pos = pos
        self._resting = resting

    def resting(self):
        return self._resting


class TestCordonBarWalkway(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.POST_A_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.POST_B_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.POST_A_FRICTION, 1.2)
        self.assertAlmostEqual(geometry.POST_B_FRICTION, 1.2)
        self.assertAlmostEqual(geometry.BAR_PAD_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.BAR_MASS_KG, 0.3)

    def test_start_state_zero(self):
        score, ok, reason = logic.evaluate_state(
            geometry.POST_A_POS_WORLD,
            geometry.POST_B_POS_WORLD,
            geometry.BAR_START_POS,
            resting=True,
        )
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_scoring_ladder(self):
        p_a = geometry.POST_A_POS_WORLD
        p_b = geometry.POST_B_POS_WORLD

        # Step 1: Bar lifted from pad (z >= TABLE_TOP + 0.05)
        bar_lifted = (0.18, 0.0, geometry.TABLE_TOP + 0.08)
        s1, ok1, _ = logic.evaluate_state(p_a, p_b, bar_lifted, resting=True)
        self.assertEqual(s1, 0.25)
        self.assertFalse(ok1)

        # Step 2: Bar resting in one cradle (asymmetric offset in y)
        bar_one_cradle = (0.28, 0.06, geometry.TABLE_TOP + 0.18)
        s2, ok2, _ = logic.evaluate_state(p_a, p_b, bar_one_cradle, resting=True)
        self.assertEqual(s2, 0.50)
        self.assertFalse(ok2)

        # Step 3: Bar near both cradles, minor offset
        bar_near_both = (0.28, 0.02, geometry.TABLE_TOP + 0.18)
        s3, ok3, _ = logic.evaluate_state(p_a, p_b, bar_near_both, resting=True)
        self.assertEqual(s3, 0.75)
        self.assertFalse(ok3)

        # Step 4: Securely resting in both cradles
        bar_seated = geometry.BAR_TARGET_POS
        s4, ok4, _ = logic.evaluate_state(p_a, p_b, bar_seated, resting=True)
        self.assertEqual(s4, 1.00)
        self.assertTrue(ok4)

    def test_dual_solution(self):
        p_a = geometry.POST_A_POS_WORLD
        p_b = geometry.POST_B_POS_WORLD

        # Solution 1: nominal target position
        s1, ok1, _ = logic.evaluate_state(
            p_a, p_b, geometry.BAR_TARGET_POS, resting=True
        )
        self.assertEqual(s1, 1.00)
        self.assertTrue(ok1)

        # Solution 2: slight offset within 15 mm tolerance
        alt_bar = (
            geometry.BAR_TARGET_POS[0] + 0.005,
            geometry.BAR_TARGET_POS[1] - 0.005,
            geometry.BAR_TARGET_POS[2] + 0.003,
        )
        s2, ok2, _ = logic.evaluate_state(p_a, p_b, alt_bar, resting=True)
        self.assertEqual(s2, 1.00)
        self.assertTrue(ok2)

    def test_drift_gates(self):
        # Post A drift > 5 mm
        drift_a = (
            geometry.POST_A_POS_WORLD[0] + 0.008,
            geometry.POST_A_POS_WORLD[1],
            geometry.POST_A_POS_WORLD[2],
        )
        s, ok, r = logic.evaluate_state(
            drift_a, geometry.POST_B_POS_WORLD, geometry.BAR_TARGET_POS, resting=True
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("Gate", r)

        # Post B drift > 5 mm
        drift_b = (
            geometry.POST_B_POS_WORLD[0],
            geometry.POST_B_POS_WORLD[1] - 0.008,
            geometry.POST_B_POS_WORLD[2],
        )
        s, ok, r = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, drift_b, geometry.BAR_TARGET_POS, resting=True
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("Gate", r)

    def test_drop_gate(self):
        dropped_bar = (0.18, 0.0, geometry.TABLE_TOP - 0.08)
        s, ok, r = logic.evaluate_state(
            geometry.POST_A_POS_WORLD, geometry.POST_B_POS_WORLD, dropped_bar, resting=True
        )
        self.assertEqual(s, 0.0)
        self.assertFalse(ok)
        self.assertIn("Gate", r)

    def test_scoring_module(self):
        objs = {
            geometry.POST_A_NAME: DummyObj(geometry.POST_A_POS_WORLD),
            geometry.POST_B_NAME: DummyObj(geometry.POST_B_POS_WORLD),
            geometry.BAR_NAME: DummyObj(geometry.BAR_TARGET_POS),
        }
        self.assertTrue(scoring.success(objs))
        self.assertEqual(scoring.score(objs), 1.0)


if __name__ == "__main__":
    unittest.main()
