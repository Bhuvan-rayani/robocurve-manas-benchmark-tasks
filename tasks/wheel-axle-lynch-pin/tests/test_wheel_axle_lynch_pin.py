"""Unit tests for wheel_axle_lynch_pin (T18)."""
from __future__ import annotations
import pathlib, sys, unittest
_TASK_DIR = pathlib.Path(__file__).resolve().parent.parent
_UPSTREAM = _TASK_DIR.parents[2] / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
for p in (_TASK_DIR, _UPSTREAM):
    if str(p) not in sys.path: sys.path.insert(0, str(p))
import geometry, logic, scoring

class DummyObj:
    def __init__(self, pos, resting=True):
        self.pos = pos
        self._resting = resting
    def resting(self): return self._resting

class TestWheelAxleLynchPin(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.STAND_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.STAND_FRICTION, 1.2)

    def test_start_state_zero(self):
        score, ok, _ = logic.evaluate_state(geometry.STAND_POS_WORLD, geometry.WHEEL_START_POS, geometry.PIN_START_POS, resting=True)
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_scoring_ladder(self):
        s_pos = geometry.STAND_POS_WORLD
        # Wheel lifted
        s1, ok1, _ = logic.evaluate_state(s_pos, (0.16, -0.18, geometry.WHEEL_START_POS[2] + 0.04), geometry.PIN_START_POS, resting=True)
        self.assertEqual(s1, 0.25)
        self.assertFalse(ok1)
        # Wheel on axle >= 2 cm (y = -0.12)
        s2, ok2, _ = logic.evaluate_state(s_pos, (0.30, -0.12, geometry.TABLE_TOP + 0.08), geometry.PIN_START_POS, resting=True)
        self.assertEqual(s2, 0.50)
        self.assertFalse(ok2)
        # Wheel fully against stop (y = -0.06)
        s3, ok3, _ = logic.evaluate_state(s_pos, geometry.WHEEL_TARGET_POS, geometry.PIN_START_POS, resting=True)
        self.assertEqual(s3, 0.75)
        self.assertFalse(ok3)
        # Pin inserted through hole
        s4, ok4, _ = logic.evaluate_state(s_pos, geometry.WHEEL_TARGET_POS, geometry.PIN_TARGET_POS, resting=True)
        self.assertEqual(s4, 1.00)
        self.assertTrue(ok4)

    def test_drift_gate(self):
        s_pos = (geometry.STAND_POS_WORLD[0] + 0.010, 0.0, geometry.TABLE_TOP)
        score, ok, reason = logic.evaluate_state(s_pos, geometry.WHEEL_TARGET_POS, geometry.PIN_TARGET_POS, resting=True)
        self.assertEqual(score, 0.0)
        self.assertIn("Gate", reason)

    def test_scoring_module(self):
        objs = {
            geometry.STAND_NAME: DummyObj(geometry.STAND_POS_WORLD),
            geometry.WHEEL_NAME: DummyObj(geometry.WHEEL_TARGET_POS),
            geometry.PIN_NAME: DummyObj(geometry.PIN_TARGET_POS),
        }
        self.assertTrue(scoring.success(objs))
        self.assertEqual(scoring.score(objs), 1.0)

if __name__ == "__main__":
    unittest.main()
