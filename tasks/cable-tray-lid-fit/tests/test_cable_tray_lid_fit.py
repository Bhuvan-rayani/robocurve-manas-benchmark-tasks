"""Unit tests for cable_tray_lid_fit (T13)."""
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

class TestCableTrayLidFit(unittest.TestCase):
    def test_constants(self):
        self.assertAlmostEqual(geometry.TABLE_TOP, 0.7475)
        self.assertAlmostEqual(geometry.TRAY_MASS_KG, 25.0)
        self.assertAlmostEqual(geometry.TRAY_FRICTION, 1.2)
        self.assertEqual(geometry.HANDLE_DIMS_M, (0.040, 0.080, 0.010))
        # Gripper opening is 94 mm; handle width (40 mm) must easily fit within gripper span
        self.assertLess(geometry.HANDLE_DIMS_M[0], 0.094)
        # Check compound box structure
        self.assertEqual(len(geometry.LID_BOXES), 2)
        base_box = geometry.LID_BOXES[0]
        handle_box = geometry.LID_BOXES[1]
        self.assertEqual(base_box[1], geometry.LID_DIMS_M)
        self.assertEqual(handle_box[1], geometry.HANDLE_DIMS_M)
        self.assertAlmostEqual(base_box[0][2] + base_box[1][2] / 2.0, handle_box[0][2] - handle_box[1][2] / 2.0)

    def test_start_state_zero(self):
        score, ok, _ = logic.evaluate_state(geometry.TRAY_POS_WORLD, geometry.LID_START_POS, resting=True)
        self.assertEqual(score, 0.0)
        self.assertFalse(ok)

    def test_scoring_ladder(self):
        t_pos = geometry.TRAY_POS_WORLD
        l_poses = dict(geometry.LID_START_POS)
        # Left lid on rails
        l_poses[geometry.LID_LEFT_NAME] = (0.30, 0.20, geometry.TABLE_TOP + 0.060)
        s1, ok1, _ = logic.evaluate_state(t_pos, l_poses, resting=True)
        self.assertEqual(s1, 0.25)
        self.assertFalse(ok1)
        # Both lids on rails but far apart
        l_poses[geometry.LID_RIGHT_NAME] = (0.30, -0.20, geometry.TABLE_TOP + 0.060)
        s2, ok2, _ = logic.evaluate_state(t_pos, l_poses, resting=True)
        self.assertEqual(s2, 0.50)
        self.assertFalse(ok2)
        # Both near center (gap ~2 cm)
        l_poses[geometry.LID_LEFT_NAME] = (0.30, 0.110, geometry.TABLE_TOP + 0.060)
        l_poses[geometry.LID_RIGHT_NAME] = (0.30, -0.110, geometry.TABLE_TOP + 0.060)
        s3, ok3, _ = logic.evaluate_state(t_pos, l_poses, resting=True)
        self.assertEqual(s3, 0.75)
        self.assertFalse(ok3)
        # Both flush in middle (gap <= 5 mm)
        l_poses[geometry.LID_LEFT_NAME] = geometry.LID_TARGET_POS[geometry.LID_LEFT_NAME]
        l_poses[geometry.LID_RIGHT_NAME] = geometry.LID_TARGET_POS[geometry.LID_RIGHT_NAME]
        s4, ok4, _ = logic.evaluate_state(t_pos, l_poses, resting=True)
        self.assertEqual(s4, 1.00)
        self.assertTrue(ok4)

    def test_drift_gate(self):
        t_pos = (geometry.TRAY_POS_WORLD[0] + 0.010, 0.0, geometry.TABLE_TOP)
        score, ok, reason = logic.evaluate_state(t_pos, geometry.LID_TARGET_POS, resting=True)
        self.assertEqual(score, 0.0)
        self.assertIn("Gate", reason)

    def test_scoring_module(self):
        objs = {
            geometry.TRAY_NAME: DummyObj(geometry.TRAY_POS_WORLD),
            geometry.LID_LEFT_NAME: DummyObj(geometry.LID_TARGET_POS[geometry.LID_LEFT_NAME]),
            geometry.LID_RIGHT_NAME: DummyObj(geometry.LID_TARGET_POS[geometry.LID_RIGHT_NAME]),
        }
        self.assertTrue(scoring.success(objs))
        self.assertEqual(scoring.score(objs), 1.0)

if __name__ == "__main__":
    unittest.main()
