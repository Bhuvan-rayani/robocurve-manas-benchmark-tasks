"""Unit tests for finger_guard_then_start (T20)."""
from __future__ import annotations
import pathlib, sys, unittest
_TASK_DIR = pathlib.Path(__file__).resolve().parent.parent
_UPSTREAM = _TASK_DIR.parents[2] / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
for p in (_TASK_DIR, _UPSTREAM):
    if str(p) not in sys.path: sys.path.insert(0, str(p))
import geometry, logic, scoring

class DummyMachine:
    def __init__(self, pos, sliders=None, resting=True):
        self.pos = pos
        self.sliders = sliders or {}
        self._resting = resting
    def resting(self): return self._resting

class TestFingerGuardThenStart(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.MACHINE_MASS_KG, 25.0)

    def test_start_state_zero(self):
        score, ok, _ = logic.evaluate_state(geometry.MACHINE_POS_WORLD, 0.0, 0.0, resting=True)
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_scoring_ladder(self):
        m_pos = geometry.MACHINE_POS_WORLD
        # Guard closed 7 cm
        s1, ok1, _ = logic.evaluate_state(m_pos, 0.070, 0.0, resting=True)
        self.assertEqual(s1, 0.25)
        self.assertFalse(ok1)
        # Guard closed 13 cm
        s2, ok2, _ = logic.evaluate_state(m_pos, 0.130, 0.0, resting=True)
        self.assertEqual(s2, 0.50)
        self.assertFalse(ok2)
        # Button pressed with guard open -> fault capped at 0.25
        sf, okf, _ = logic.evaluate_state(m_pos, 0.050, 0.007, resting=True)
        self.assertEqual(sf, 0.25)
        self.assertFalse(okf)
        # Button pressed >= 6.4 mm while guard closed
        s3, ok3, _ = logic.evaluate_state(m_pos, 0.130, 0.007, resting=True)
        self.assertEqual(s3, 1.00)
        self.assertTrue(ok3)

    def test_drift_gate(self):
        m_pos = (geometry.MACHINE_POS_WORLD[0] + 0.010, 0.0, geometry.TABLE_TOP)
        score, ok, reason = logic.evaluate_state(m_pos, 0.130, 0.007, resting=True)
        self.assertEqual(score, 0.0)
        self.assertIn("Gate", reason)

    def test_scoring_module(self):
        obj = DummyMachine(geometry.MACHINE_POS_WORLD, sliders={"guard": -0.130, "button": -0.007})
        self.assertTrue(scoring.success({geometry.MACHINE_NAME: obj}))
        self.assertEqual(scoring.score({geometry.MACHINE_NAME: obj}), 1.0)

if __name__ == "__main__":
    unittest.main()
