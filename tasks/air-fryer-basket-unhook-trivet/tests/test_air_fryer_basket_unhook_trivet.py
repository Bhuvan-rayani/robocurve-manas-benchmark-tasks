import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from geometry import MAT_CENTRE_XY, TABLE_TOP, UNHOOK_ORIGIN_X_M  # noqa: E402
from logic import evaluate_state, on_mat, tilt_deg, turn_deg  # noqa: E402

FLAT = (0.0, 0.0, 0.0, 1.0)
MAT_POS = (MAT_CENTRE_XY[0], MAT_CENTRE_XY[1], TABLE_TOP + 0.01)
START = (0.372, 0.0, TABLE_TOP + 0.036)
OFF = (0.35, 0.0, TABLE_TOP + 0.036)


def quat_z(deg):
    h = math.radians(deg) / 2
    return (0.0, 0.0, math.sin(h), math.cos(h))


def quat_x(deg):
    h = math.radians(deg) / 2
    return (math.sin(h), 0.0, 0.0, math.cos(h))


class Logic(unittest.TestCase):
    def test_full(self):
        self.assertEqual(evaluate_state(MAT_POS, FLAT, 0.34, 0.03, False, True, True)[0], 1.0)

    def test_not_released_or_not_still(self):
        self.assertEqual(evaluate_state(MAT_POS, FLAT, 0.34, 0.03, False, False, True)[0], 0.75)
        self.assertEqual(evaluate_state(MAT_POS, FLAT, 0.34, 0.03, False, True, False)[0], 0.75)

    def test_fault_is_zero(self):
        self.assertEqual(evaluate_state(MAT_POS, FLAT, 0.34, 0.03, True, True, True)[0], 0.0)

    def test_off_mat_levels(self):
        self.assertEqual(evaluate_state(OFF, FLAT, 0.34, 0.03, False, True, True)[0], 0.5)
        self.assertEqual(evaluate_state(OFF, FLAT, 0.34, 0.0, False, True, True)[0], 0.25)
        self.assertEqual(evaluate_state(OFF, FLAT, 0.36, 0.0, False, True, True)[0], 0.0)
        self.assertEqual(evaluate_state(START, FLAT, 0.372, 0.0, False, True, True)[0], 0.0)

    def test_slide_thresholds(self):
        self.assertEqual(evaluate_state(START, FLAT, 0.343, 0.0, False, True, True)[0], 0.25)
        self.assertEqual(evaluate_state(START, FLAT, 0.35, 0.0, False, True, True)[0], 0.0)
        # a lift without being clear of the hooks does not give 0.5
        self.assertEqual(evaluate_state(OFF, FLAT, UNHOOK_ORIGIN_X_M + 0.001, 0.03, False, True, True)[0], 0.0)

    def test_mat_tolerances(self):
        self.assertTrue(on_mat(MAT_POS, FLAT))
        self.assertFalse(on_mat((MAT_POS[0] + 0.011, MAT_POS[1], MAT_POS[2]), FLAT))
        self.assertFalse(on_mat((MAT_POS[0], MAT_POS[1], MAT_POS[2] + 0.004), FLAT))   # hovering
        self.assertFalse(on_mat((MAT_POS[0], MAT_POS[1], MAT_POS[2] - 0.004), FLAT))
        self.assertFalse(on_mat(MAT_POS, quat_x(4.0)))
        self.assertFalse(on_mat(MAT_POS, quat_z(12.0)))
        self.assertTrue(on_mat(MAT_POS, quat_z(8.0)))

    def test_angles(self):
        self.assertAlmostEqual(tilt_deg(quat_x(10.0)), 10.0, places=4)
        self.assertAlmostEqual(turn_deg(quat_z(-30.0)), 30.0, places=4)


if __name__ == "__main__":
    unittest.main()
