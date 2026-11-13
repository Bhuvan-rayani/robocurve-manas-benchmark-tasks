"""Unit tests for air_fryer_basket_release_button_v2 benchmark task."""

from __future__ import annotations

import math
import os
import pathlib
import sys
import unittest

import numpy as np

# Set up import paths
HERE = pathlib.Path(__file__).resolve()
TASK_DIR = HERE.parents[1]
sys.path.insert(0, str(TASK_DIR))

# Ensure yam_arena can be imported
_ROOT = HERE.parents[3].parent
_KNOWN = _ROOT / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
for cand in [_KNOWN] if (_KNOWN / "yam_arena").is_dir() else _ROOT.rglob("yam-upstream"):
    if (cand / "yam_arena").is_dir():
        sys.path.insert(0, str(cand))
        break

import geometry as g
import logic as l
from demo_plan import plans
from scoring import distance, score, success
from task import OBJECTS


class TestGeometry(unittest.TestCase):
    """Verify geometry constants, collision box counts, and physical properties."""

    def test_hot_box_count_is_nineteen(self):
        """Must have exactly 19 hot collision boxes (5 housing, 9 drawer, 5 basket)."""
        housing_hot = [b for b in g.HOUSING_BOXES if b[2]]
        drawer_hot = [b for b in g.DRAWER_BOXES if b[2]]
        basket_hot = [b for b in g.BASKET_BODY_BOXES if b[2]]
        self.assertEqual(len(housing_hot), 5)
        self.assertEqual(len(drawer_hot), 9)
        self.assertEqual(len(basket_hot), 5)
        self.assertEqual(len(housing_hot) + len(drawer_hot) + len(basket_hot), 19)

    def test_touchable_boxes_are_not_hot(self):
        """Handle, button, and mat boxes must NOT be marked hot."""
        for b in g.BASKET_HANDLE_BOXES:
            self.assertFalse(b[2])
        for b in g.BUTTON_BOXES:
            self.assertFalse(b[2])
        for b in g.MAT_BOXES:
            self.assertFalse(b[2])

    def test_slide_properties(self):
        """Drawer and button slides must match design specifications."""
        self.assertAlmostEqual(g.DRAWER_TRAVEL_M, 0.255)
        self.assertAlmostEqual(g.DRAWER_RATE_N_M, 4.0)
        self.assertAlmostEqual(g.DRAWER_DAMPING_NS_M, 30.0)

        self.assertAlmostEqual(g.BUTTON_TRAVEL_M, 0.014)
        self.assertAlmostEqual(g.BUTTON_RATE_N_M, 8.0)
        self.assertLessEqual(g.BUTTON_RATE_N_M, 10.0)  # Arm-held <= 10 N/m limit
        self.assertAlmostEqual(g.BUTTON_DAMPING_NS_M, 5.0)

    def test_pad_dimensions_and_tolerances(self):
        """Fingertip pad is 12 mm cube and hot inflation is 2 mm."""
        self.assertEqual(g.PAD_BOX_SIZE, (0.012, 0.012, 0.012))
        self.assertEqual(g.PAD_BOX_HALF, (0.006, 0.006, 0.006))
        self.assertAlmostEqual(g.HOT_INFLATION_M, 0.002)
        self.assertGreaterEqual(g.MAT_Z_TOL, 0.005)


class TestLogicCatchesAndButtons(unittest.TestCase):
    """Test physical release latch logic and button extension thresholds."""

    def test_catches_hold_basket_until_pressed(self):
        """Catches physically engage for displacements < 6 mm, withdraw at >= 6 mm."""
        self.assertTrue(l.catches_hold_basket(0.000))
        self.assertTrue(l.catches_hold_basket(0.003))
        self.assertTrue(l.catches_hold_basket(0.0059))
        self.assertFalse(l.catches_hold_basket(0.0060))
        self.assertFalse(l.catches_hold_basket(0.0090))

    def test_button_out_threshold(self):
        """BUTTON_OUT requires button >= 90% extended (displacement <= 0.9 mm)."""
        self.assertTrue(l.button_out(0.000))
        self.assertTrue(l.button_out(0.0005))
        self.assertTrue(l.button_out(0.0009))
        self.assertFalse(l.button_out(0.0010))
        self.assertFalse(l.button_out(0.0090))


class TestLogicOnMat(unittest.TestCase):
    """Test ON_MAT corner containment, underside elevation, and tilt tolerances."""

    def setUp(self):
        # Basket centered perfectly on the mat at resting height
        self.mat_b_pos = (g.MAT_CENTRE[0], g.MAT_CENTRE[1], g.MAT_TOP_Z + 0.005)
        self.mat_b_quat = (0.0, 0.0, 0.0, 1.0)

    def test_perfect_placement_on_mat(self):
        self.assertTrue(l.on_mat(self.mat_b_pos, self.mat_b_quat))

    def test_corner_out_of_x_bounds_fails(self):
        pos_too_far_x = (g.MAT_X_MAX - g.BASKET_FLOOR_BACK_X + 0.010, g.MAT_CENTRE[1], self.mat_b_pos[2])  # back edge 10 mm off
        self.assertFalse(l.on_mat(pos_too_far_x, self.mat_b_quat))
        pos_front_off = (g.MAT_X_MIN + g.BASKET_FLOOR_HALF_X - 0.010, g.MAT_CENTRE[1], self.mat_b_pos[2])  # front edge 10 mm off
        self.assertFalse(l.on_mat(pos_front_off, self.mat_b_quat))

    def test_corner_out_of_y_bounds_fails(self):
        pos_too_far_y = (g.MAT_CENTRE[0], g.MAT_Y_MIN + g.BASKET_FLOOR_HALF_Y - 0.010, self.mat_b_pos[2])
        self.assertFalse(l.on_mat(pos_too_far_y, self.mat_b_quat))

    def test_elevation_too_high_or_low_fails(self):
        pos_too_high = (self.mat_b_pos[0], self.mat_b_pos[1], self.mat_b_pos[2] + 0.006)
        pos_too_low = (self.mat_b_pos[0], self.mat_b_pos[1], self.mat_b_pos[2] - 0.006)
        self.assertFalse(l.on_mat(pos_too_high, self.mat_b_quat))
        self.assertFalse(l.on_mat(pos_too_low, self.mat_b_quat))

    def test_excessive_tilt_fails(self):
        # Tilt > 5 degrees
        angle = math.radians(6.0)
        tilt_quat = (math.sin(angle / 2), 0.0, 0.0, math.cos(angle / 2))
        self.assertFalse(l.on_mat(self.mat_b_pos, tilt_quat))


class TestLogicHotContact(unittest.TestCase):
    """Test fingertip pad hot collision detection on all 19 hot boxes."""

    def test_housing_hot_contact(self):
        """Pad touching housing floor or walls registers hot contact."""
        h_origin = np.array(g.HOUSING_POS)
        # Pad placed at housing back wall
        pad_at_housing = [h_origin + np.array([0.122, 0.000, 0.047])]
        self.assertTrue(l.hot_contact(pad_at_housing, g.BASKET_START_POS, (0, 0, 0, 1)))

    def test_drawer_hot_contact(self):
        """Pad touching drawer floor or walls registers hot contact."""
        d_origin = np.array(g.HOUSING_POS) + np.array(g.DRAWER_AT)
        pad_at_drawer_floor = [d_origin + np.array([0.000, 0.000, 0.003])]
        self.assertTrue(l.hot_contact(pad_at_drawer_floor, g.BASKET_START_POS, (0, 0, 0, 1)))

    def test_basket_body_hot_contact(self):
        """Pad touching orange basket body floor or side walls registers hot contact."""
        b_origin = np.array(g.BASKET_START_POS)
        # Right wall of basket
        pad_at_basket_wall = [b_origin + np.array([0.000, -0.100, 0.035])]
        self.assertTrue(l.hot_contact(pad_at_basket_wall, g.BASKET_START_POS, (0, 0, 0, 1)))

    def test_touchable_handle_contact_is_not_hot(self):
        """Pad touching cool-touch handle bar or button cap does NOT trigger hot contact."""
        b_origin = np.array(g.BASKET_START_POS)
        # Left overhang of cool-touch handle bar: x = -0.1615, y = 0.070, z = 0.0355
        pad_at_handle = [b_origin + np.array([-0.1615, 0.070, 0.0355])]
        # Button cap: x = -0.1815, y = -0.070, z = 0.038
        pad_at_button = [b_origin + np.array([-0.1815, -0.070, 0.038])]
        self.assertFalse(l.hot_contact(pad_at_handle, g.BASKET_START_POS, (0, 0, 0, 1)))
        self.assertFalse(l.hot_contact(pad_at_button, g.BASKET_START_POS, (0, 0, 0, 1)))


class TestScoringLevels(unittest.TestCase):
    """Test evaluation and full scoring levels (1.0, 0.75, 0.5, 0.25, 0.0)."""

    def setUp(self):
        self.mat_pos = (g.MAT_CENTRE[0], g.MAT_CENTRE[1], g.MAT_TOP_Z + 0.005)
        self.mat_quat = (0.0, 0.0, 0.0, 1.0)

    def test_full_success_is_one(self):
        score, reason = l.evaluate_state(
            basket_pos=self.mat_pos,
            basket_quat=self.mat_quat,
            button_disp=0.000,
            hot_contact_ever=False,
            cleared_drawer_ever=True,
            unhook_lift_ever=True,
            grippers_released=True,
            basket_still=True,
        )
        self.assertEqual(score, 1.0)

    def test_not_released_or_not_still_is_three_quarters(self):
        score_unreleased, _ = l.evaluate_state(
            basket_pos=self.mat_pos,
            basket_quat=self.mat_quat,
            button_disp=0.000,
            hot_contact_ever=False,
            cleared_drawer_ever=True,
            unhook_lift_ever=True,
            grippers_released=False,
            basket_still=True,
        )
        self.assertEqual(score_unreleased, 0.75)

        score_unstill, _ = l.evaluate_state(
            basket_pos=self.mat_pos,
            basket_quat=self.mat_quat,
            button_disp=0.000,
            hot_contact_ever=False,
            cleared_drawer_ever=True,
            unhook_lift_ever=True,
            grippers_released=True,
            basket_still=False,
        )
        self.assertEqual(score_unstill, 0.75)

    def test_button_held_at_end_is_three_quarters(self):
        score_button_held, _ = l.evaluate_state(
            basket_pos=self.mat_pos,
            basket_quat=self.mat_quat,
            button_disp=0.005,  # Still held
            hot_contact_ever=False,
            cleared_drawer_ever=True,
            unhook_lift_ever=True,
            grippers_released=True,
            basket_still=True,
        )
        self.assertEqual(score_button_held, 0.75)

    def test_cleared_drawer_not_on_mat_is_half(self):
        bench_pos = (0.25, 0.0, g.TABLE_TOP + 0.010)
        score_cleared, _ = l.evaluate_state(
            basket_pos=bench_pos,
            basket_quat=self.mat_quat,
            button_disp=0.000,
            hot_contact_ever=False,
            cleared_drawer_ever=True,
            unhook_lift_ever=True,
            grippers_released=True,
            basket_still=True,
        )
        self.assertEqual(score_cleared, 0.5)

    def test_unhook_lift_in_drawer_is_quarter(self):
        score_quarter, _ = l.evaluate_state(
            basket_pos=g.BASKET_START_POS,
            basket_quat=self.mat_quat,
            button_disp=0.000,
            hot_contact_ever=False,
            cleared_drawer_ever=False,
            unhook_lift_ever=True,
            grippers_released=True,
            basket_still=True,
        )
        self.assertEqual(score_quarter, 0.25)

    def test_hot_contact_is_permanent_zero(self):
        """Any hot contact by either pad at any step latches permanent zero."""
        score_hot, _ = l.evaluate_state(
            basket_pos=self.mat_pos,
            basket_quat=self.mat_quat,
            button_disp=0.000,
            hot_contact_ever=True,  # Hot contact latched!
            cleared_drawer_ever=True,
            unhook_lift_ever=True,
            grippers_released=True,
            basket_still=True,
        )
        self.assertEqual(score_hot, 0.0)


class TestAblationAndReach(unittest.TestCase):
    """Test ablation mode, TCP reach limits, and arm separation."""

    def test_ablation_mode_plan(self):
        """Ablation: the same hand grips the bar between the posts, away from the release cap, so the catches stay hooked."""
        import demo_plan as dp
        os.environ["ABLATION"] = "1"
        try:
            pinch = next(w for w in plans()["right"] if "pinch" in w.label)
            self.assertAlmostEqual(pinch.pos[1], dp.BAR_ONLY_GRIP[1])
            cap_y0 = g.BASKET_START_POS[1] + g.BUTTON_AT[1] + g.BUTTON_BOXES[0][0][1] - g.BUTTON_BOXES[0][1][1] / 2
            cap_y1 = cap_y0 + g.BUTTON_BOXES[0][1][1]
            self.assertTrue(pinch.pos[1] - 0.015 > cap_y1 or pinch.pos[1] + 0.015 < cap_y0)  # 15 mm finger half-width clear of the cap
        finally:
            os.environ.pop("ABLATION", None)

    def test_demo_reach_limits(self):
        """Every TCP waypoint must satisfy x <= 0.30 and z <= 0.19 relative to table (IK is exact to 0.20)."""
        demo_plans = plans()
        for arm in ("left", "right"):
            for wp in demo_plans[arm]:
                self.assertLessEqual(wp.pos[0], 0.30, f"{arm} waypoint x exceeds 0.30: {wp.pos}")
                self.assertLessEqual(wp.pos[2] - g.TABLE_TOP, 0.19 + 1e-4, f"{arm} waypoint z exceeds 0.19: {wp.pos}")

    def test_demo_pinch_presses_cap_and_clears_hot_boxes(self):
        """The pinch spans the release cap face to the bar's back face; closing pushes the cap to its stop, and the open
        fingers' pads stay out of the inflated hot zones of the drawer front and the basket front wall."""
        import demo_plan as dp
        gx = dp.CAP_GRIP[0]
        cap_face = g.BASKET_START_POS[0] + g.BUTTON_AT[0] + g.BUTTON_BOXES[0][0][0] - g.BUTTON_BOXES[0][1][0] / 2
        bar_back = g.BASKET_START_POS[0] + g.BASKET_HANDLE_BOXES[2][0][0] + g.BASKET_HANDLE_BOXES[2][1][0] / 2
        half_open = abs(dp.GRIP_OPEN)
        self.assertLess(gx - half_open, cap_face)          # front finger starts in front of the cap
        self.assertGreater(gx + half_open, bar_back)       # back finger starts behind the bar
        self.assertAlmostEqual(gx, (cap_face + g.BUTTON_TRAVEL_M + bar_back) / 2, places=3)  # closed: cap pressed fully
        rear_pad = gx + half_open + 0.006
        basket_front = g.BASKET_START_POS[0] + g.BASKET_BODY_BOXES[4][0][0] - g.BASKET_BODY_BOXES[4][1][0] / 2
        drawer_front = g.HOUSING_POS[0] + g.DRAWER_AT[0] + g.DRAWER_BOXES[4][0][0] - g.DRAWER_BOXES[4][1][0] / 2
        zone = g.HOT_INFLATION_M + g.PAD_BOX_HALF[0]
        self.assertLess(rear_pad, basket_front - zone)
        # the drawer front strip is cleared in height: its inflated top is below the pad tips
        strip_top = g.HOUSING_POS[2] + g.DRAWER_AT[2] + g.DRAWER_BOXES[4][0][2] + g.DRAWER_BOXES[4][1][2] / 2
        tip_pad_z = g.TABLE_TOP + dp.PINCH_Z - 0.013
        self.assertGreater(tip_pad_z, strip_top + zone)
        self.assertGreater(drawer_front, 0.0)


class TestTaskSpec(unittest.TestCase):
    """Test yam task specification objects and structure."""

    def test_task_objects_structure(self):
        self.assertEqual(len(OBJECTS), 3)
        names = {o.name for o in OBJECTS}
        self.assertEqual(names, {"af2_housing", "af2_basket", "af2_mat"})

    def test_display_lamp_and_tiles_positions(self):
        """Verify lamp and vent tiles are located on housing."""
        self.assertEqual(len(g.VENT_GLOW_TILES_LOCAL), 4)
        for tile in g.VENT_GLOW_TILES_LOCAL:
            self.assertAlmostEqual(tile[2], 0.281)
        self.assertAlmostEqual(g.LAMP_TILE_LOCAL[2], 0.281)


if __name__ == "__main__":
    unittest.main()


class TestCatchGeometry(unittest.TestCase):
    """The catch lugs physically hold the basket until the button is pressed (computed from the world boxes)."""

    def _x_ranges(self, travel):
        lugs, ledges = [], []
        for c, s, _ in g.BUTTON_BOXES[1:]:
            x = g.BASKET_START_POS[0] + g.BUTTON_AT[0] + c[0] + travel
            z = g.BASKET_START_POS[2] + g.BUTTON_AT[2] + c[2]
            lugs.append((x - s[0] / 2, x + s[0] / 2, z - s[2] / 2, z + s[2] / 2))
        drawer_x = g.HOUSING_POS[0] + g.DRAWER_AT[0]
        drawer_z = g.HOUSING_POS[2] + g.DRAWER_AT[2]
        for c, s, _ in g.DRAWER_BOXES[-2:]:
            ledges.append((drawer_x + c[0] - s[0] / 2, drawer_x + c[0] + s[0] / 2, drawer_z + c[2] - s[2] / 2, drawer_z + c[2] + s[2] / 2))
        return lugs, ledges

    def test_catch_lugs_hold_then_clear(self):
        lugs, ledges = self._x_ranges(0.0)
        for lug, ledge in zip(lugs, ledges):
            self.assertGreaterEqual(min(lug[1], ledge[1]) - max(lug[0], ledge[0]), 0.005)  # >= 5 mm under the ledge at rest
            self.assertLess(lug[3], ledge[2])  # below the ledge: a lift catches it
        lugs, ledges = self._x_ranges(g.BUTTON_TRAVEL_M)
        for lug, ledge in zip(lugs, ledges):
            self.assertGreaterEqual(lug[0] - ledge[1], 0.002)  # >= 2 mm past the ledge at full travel: the basket lifts free
