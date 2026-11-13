"""Unit tests for utility_knife_retract_then_stow benchmark task."""

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
    """Verify geometry constants, dimensions, masses, and physical parameters."""

    def test_object_counts_and_names(self):
        """Task must specify exactly 3 Mechs: the knife, its holster and the cutting mat it lies on."""
        self.assertEqual(len(OBJECTS), 3)
        names = {o.name for o in OBJECTS}
        self.assertEqual(names, {"ku_knife", "ku_holder", "ku_mat"})

    def test_knife_dimensions_mass_friction(self):
        """Knife handle must be 3.2 x 19.0 x 1.8 cm, 90 g, friction 0.6."""
        self.assertEqual(g.KNIFE_MASS, 0.09)
        self.assertEqual(g.KNIFE_FRICTION, 0.6)
        handle_size = g.KNIFE_HANDLE_BOX[1]
        self.assertEqual(handle_size, (0.032, 0.190, 0.018))

    def test_blade_slider_joint_properties(self):
        """Blade slider must have 25 mm travel, no spring (friction lock), 100 Ns/m damping, 20 g mass."""
        self.assertEqual(g.SLIDER_TRAVEL_M, 0.025)
        self.assertEqual(g.SLIDER_RATE_N_M, 0.0)
        self.assertEqual(g.SLIDER_DAMPING_NS_M, 100.0)
        self.assertEqual(g.SLIDER_MASS, 0.02)

    def test_blade_box_is_one_point_five_mm(self):
        """Blade box thickness must be 1.5 mm (0.0015 m, simulator thinnest box limit)."""
        blade_size = g.BLADE_BOX[1]
        self.assertEqual(blade_size, (0.018, 0.055, 0.0015))
        self.assertAlmostEqual(blade_size[2], 0.0015)

    def test_holster_pocket_dimensions(self):
        """Holster pocket inside must be 3.8 x 19.8 x 2.6 cm with floor at z=4 mm."""
        self.assertEqual(len(g.HOLDER_BOXES), 5)
        floor_box = g.HOLDER_BOXES[0]
        self.assertAlmostEqual(floor_box[1][2], 0.004)  # 4 mm floor
        self.assertAlmostEqual(g.HOLDER_MASS, 25.0)
        self.assertEqual(g.HOLDER_FRICTION, 1.2)

    def test_pad_dimensions_and_inflation(self):
        """Fingertip pad is 12 mm cube, blade inflation is 3 mm, active threshold is 24 mm."""
        self.assertEqual(g.PAD_BOX_SIZE, (0.012, 0.012, 0.012))
        self.assertEqual(g.PAD_BOX_HALF, (0.006, 0.006, 0.006))
        self.assertEqual(g.BLADE_INFLATION_M, 0.003)
        self.assertEqual(g.KEEPOUT_ACTIVE_DISP_M, 0.024)


class TestLogicBladeKeepout(unittest.TestCase):
    """Test blade keep-out zone activation and fingertip pad overlap checks."""

    def setUp(self):
        self.k_pos = (0.220, 0.000, g.TABLE_TOP)
        self.k_quat = (0.0, 0.0, 0.0, 1.0)

    def test_blade_zone_active_when_blade_out(self):
        """Pad directly in the exposed blade region registers contact while slide < 24 mm."""
        pad_in_blade = [(0.220, -0.100, g.TABLE_TOP + 0.009)]
        self.assertTrue(l.blade_zone_contact(pad_in_blade, self.k_pos, self.k_quat, slider_disp=0.000))
        self.assertTrue(l.blade_zone_contact(pad_in_blade, self.k_pos, self.k_quat, slider_disp=0.020))

    def test_blade_zone_inactive_when_retracted(self):
        """When slider displacement >= 24 mm, blade is inside handle and zone is inactive."""
        pad_in_blade = [(0.220, -0.100, g.TABLE_TOP + 0.009)]
        self.assertFalse(l.blade_zone_contact(pad_in_blade, self.k_pos, self.k_quat, slider_disp=0.024))
        self.assertFalse(l.blade_zone_contact(pad_in_blade, self.k_pos, self.k_quat, slider_disp=0.025))

    def test_pad_at_pushing_tcp_does_not_trigger_blade_zone(self):
        """Pushing pad at TCP z=0.040 (pad z=0.027) is 8+ mm above blade zone and clear."""
        push_pad = [(0.220, -0.076, g.TABLE_TOP + 0.027)]
        self.assertFalse(l.blade_zone_contact(push_pad, self.k_pos, self.k_quat, slider_disp=0.000))
        self.assertFalse(l.blade_zone_contact(push_pad, self.k_pos, self.k_quat, slider_disp=0.015))

    def test_left_pinch_location_clear_of_blade_zone(self):
        """Left arm pinch at y=0.092 is on +y end of handle, far from blade zone."""
        pinch_pad = [(0.220, 0.092, g.TABLE_TOP + 0.009)]
        self.assertFalse(l.blade_zone_contact(pinch_pad, self.k_pos, self.k_quat, slider_disp=0.000))


class TestLogicRetractAndStow(unittest.TestCase):
    """Test retraction threshold, holster containment, and refusal of exposed blade."""

    def test_is_retracted_threshold(self):
        """RETRACTED requires displacement >= 22.5 mm (90% of 25 mm)."""
        self.assertTrue(l.is_retracted(0.0250))
        self.assertTrue(l.is_retracted(0.0225))
        self.assertFalse(l.is_retracted(0.0224))
        self.assertFalse(l.is_retracted(0.0000))

    def test_is_stowed_knife_with_blade_retracted(self):
        """Stowed knife resting flat on pocket floor (z = TABLE_TOP + 4 mm)."""
        stowed_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.004)
        flat_quat = (0.0, 0.0, 0.0, 1.0)
        self.assertTrue(l.is_stowed(stowed_pos, flat_quat))

    def test_holster_refuses_knife_with_blade_out(self):
        """Knife with blade out is 21.5 cm and cannot lie in 19.8 cm pocket (sits on rim z=30 mm or tilts)."""
        # Perched on rim: z = TABLE_TOP + 0.030 m > STOWED_BASE_Z_MAX (0.009 m)
        rim_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.030)
        self.assertFalse(l.is_stowed(rim_pos, (0.0, 0.0, 0.0, 1.0)))

        # Wedged tilted > 5 degrees
        tilt_angle = math.radians(6.0)
        tilted_quat = (math.sin(tilt_angle / 2), 0.0, 0.0, math.cos(tilt_angle / 2))
        tilted_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.006)
        self.assertFalse(l.is_stowed(tilted_pos, tilted_quat))

    def test_stowed_out_of_x_or_y_bounds_fails(self):
        """Exceeding 10 mm in x or 15 mm in y fails is_stowed."""
        pos_bad_x = (g.POCKET_CENTRE[0] + 0.011, g.POCKET_CENTRE[1], g.TABLE_TOP + 0.004)
        pos_bad_y = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1] + 0.016, g.TABLE_TOP + 0.004)
        self.assertFalse(l.is_stowed(pos_bad_x, (0, 0, 0, 1)))
        self.assertFalse(l.is_stowed(pos_bad_y, (0, 0, 0, 1)))

    def test_excessive_tilt_fails_stowed(self):
        """Tilt greater than 5 degrees fails stowed check."""
        stowed_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.004)
        angle = math.radians(5.5)
        tilt_quat = (0.0, math.sin(angle / 2), 0.0, math.cos(angle / 2))
        self.assertFalse(l.is_stowed(stowed_pos, tilt_quat))

    def test_is_resting_on_holster(self):
        """Knife resting across holster rim is detected by is_resting_on_holster."""
        rim_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.030)
        self.assertTrue(l.is_resting_on_holster(rim_pos))
        bench_pos = (0.220, 0.000, g.TABLE_TOP)
        self.assertFalse(l.is_resting_on_holster(bench_pos))


class TestScoringLevels(unittest.TestCase):
    """Test state evaluation across all scoring tiers (1.0, 0.75, 0.5, 0.25, 0.0)."""

    def setUp(self):
        self.stowed_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.004)
        self.bench_pos = (0.220, 0.000, g.TABLE_TOP)
        self.rim_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.030)
        self.flat_quat = (0.0, 0.0, 0.0, 1.0)

    def test_full_success_is_one(self):
        """Retracted, stowed, released, still, no blade contact -> 1.0."""
        s, reason = l.evaluate_state(
            knife_pos=self.stowed_pos,
            knife_quat=self.flat_quat,
            slider_disp=0.025,
            blade_contact_ever=False,
            grippers_released=True,
            knife_still=True,
        )
        self.assertEqual(s, 1.0)
        self.assertIn("knife retracted, stowed in holster", reason)

    def test_permanent_zero_on_blade_zone_contact(self):
        """Any contact with the blade zone latches permanent 0.0."""
        s, reason = l.evaluate_state(
            knife_pos=self.stowed_pos,
            knife_quat=self.flat_quat,
            slider_disp=0.025,
            blade_contact_ever=True,
            grippers_released=True,
            knife_still=True,
        )
        self.assertEqual(s, 0.0)
        self.assertIn("permanent zero", reason)

    def test_unreleased_or_unstill_is_three_quarters(self):
        """Retracted and stowed, but unreleased or not still -> 0.75."""
        s_unrel, _ = l.evaluate_state(
            knife_pos=self.stowed_pos,
            knife_quat=self.flat_quat,
            slider_disp=0.025,
            blade_contact_ever=False,
            grippers_released=False,
            knife_still=True,
        )
        self.assertEqual(s_unrel, 0.75)

        s_unstill, _ = l.evaluate_state(
            knife_pos=self.stowed_pos,
            knife_quat=self.flat_quat,
            slider_disp=0.025,
            blade_contact_ever=False,
            grippers_released=True,
            knife_still=False,
        )
        self.assertEqual(s_unstill, 0.75)

    def test_retracted_not_stowed_is_half(self):
        """Retracted, but left on bench (not stowed) -> 0.5."""
        s, reason = l.evaluate_state(
            knife_pos=self.bench_pos,
            knife_quat=self.flat_quat,
            slider_disp=0.025,
            blade_contact_ever=False,
            grippers_released=True,
            knife_still=True,
        )
        self.assertEqual(s, 0.5)
        self.assertIn("not stowed", reason)

    def test_knife_stowed_or_on_holster_with_blade_out_is_quarter(self):
        """Knife resting on holster with blade still out -> 0.25."""
        s, reason = l.evaluate_state(
            knife_pos=self.rim_pos,
            knife_quat=self.flat_quat,
            slider_disp=0.000,
            blade_contact_ever=False,
            grippers_released=True,
            knife_still=True,
        )
        self.assertEqual(s, 0.25)
        self.assertIn("blade still out", reason)

    def test_knife_unmoved_is_zero(self):
        """Knife on bench with blade out, untouched -> 0.0."""
        s, reason = l.evaluate_state(
            knife_pos=self.bench_pos,
            knife_quat=self.flat_quat,
            slider_disp=0.000,
            blade_contact_ever=False,
            grippers_released=True,
            knife_still=True,
        )
        self.assertEqual(s, 0.0)


class TestAblations(unittest.TestCase):
    """Test ablation modes: right idle and left idle both score < 1.0."""

    def test_ablation_right_idle_plan_and_score(self):
        """When right arm is idle, blade stays out; score is at most 0.25 (< 1.0)."""
        os.environ["ABLATION"] = "1"
        try:
            p = plans()
            # Ablation: the same hand skips the retract steps and goes straight to stowing, so the blade stays out
            labels = [w.label for w in p["right"]]
            self.assertNotIn("slide blade home", labels)
            self.assertIn("grip handle", labels)
            # Blade displacement remains 0.0
            s, _ = l.evaluate_state(
                knife_pos=(g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.030),
                knife_quat=(0, 0, 0, 1),
                slider_disp=0.000,
                blade_contact_ever=False,
                grippers_released=True,
                knife_still=True,
            )
            self.assertLess(s, 1.0)
            self.assertLessEqual(s, 0.25)
        finally:
            os.environ.pop("ABLATION", None)

    def test_ablation_left_idle_plan_and_score(self):
        """When left arm is idle, knife slides away without holding; blade stays out and knife is not stowed (score 0.0)."""
        os.environ["ABLATION_LEFT"] = "1"
        try:
            p = plans()
            self.assertEqual(len(p["left"]), 1)
            self.assertIn("idle", p["left"][0].label)
            # Knife slides on table to e.g. (0.220, -0.050, TABLE_TOP), blade out
            s, _ = l.evaluate_state(
                knife_pos=(0.220, -0.050, g.TABLE_TOP),
                knife_quat=(0, 0, 0, 1),
                slider_disp=0.000,
                blade_contact_ever=False,
                grippers_released=True,
                knife_still=True,
            )
            self.assertLess(s, 1.0)
            self.assertEqual(s, 0.0)
        finally:
            os.environ.pop("ABLATION_LEFT", None)


class TestDemoPlanAndReach(unittest.TestCase):
    """Verify demo reach limits, arm clearance, and release/stillness mechanics."""

    def test_demo_reach_hard_limits(self):
        """Every TCP waypoint must satisfy x <= 0.30 and z above bench <= 0.16 (hard limit <= 0.19), and work <= 0.120."""
        p = plans()
        for arm in ("left", "right"):
            for wp in p[arm]:
                self.assertLessEqual(wp.pos[0], 0.30 + 1e-4, f"{arm} waypoint x exceeds 0.30: {wp.pos}")
                z_above_bench = wp.pos[2] - g.TABLE_TOP
                self.assertLessEqual(z_above_bench, 0.16 + 1e-4, f"{arm} waypoint z exceeds hard limit 0.16: {wp.pos}")
                # Operational manipulation waypoints over the bench stay <= 0.120 (GPU-measured reach is exact to 0.19)
                if wp.pos[0] > 0.15:
                    self.assertLessEqual(z_above_bench, 0.120 + 1e-4, f"{arm} work z exceeds 0.120: {wp.pos}")

    def test_demo_left_arm_idle_and_single_hand_in_reach(self):
        """One hand does the task in front of the right arm: the left arm only idles at ready, and the knife lane keeps
        the right hand at least 8 cm to the right of the right base's centre line limit (y <= -0.08)."""
        p = plans()
        self.assertEqual(len(p["left"]), 1)
        self.assertIn("idle", p["left"][0].label)
        for w in p["right"]:
            self.assertLessEqual(w.pos[1], -0.08, w.label)

    def test_demo_slide_commanded_past_stop(self):
        """The pinched button is commanded 8 to 15 mm past its 25 mm stop."""
        p = plans()
        r_pinch = next(w for w in p["right"] if "pinch slider button" in w.label)
        r_slide = next(w for w in p["right"] if "slide blade home" in w.label)
        past = (r_slide.pos[1] - r_pinch.pos[1]) - g.SLIDER_TRAVEL_M
        self.assertGreaterEqual(past, 0.008)
        self.assertLessEqual(past, 0.015)

    def test_release_condition_requires_clearance(self):
        """Grippers closer than 3 cm fail released check."""
        stowed_pos = (g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.004)
        # TCP placed 1 cm from knife
        close_tcps = [(g.POCKET_CENTRE[0], g.POCKET_CENTRE[1], g.TABLE_TOP + 0.025)]
        clear_tcps = [g.L_READY, g.R_READY]
        pads = []
        self.assertFalse(l.released(close_tcps, pads, stowed_pos, (0, 0, 0, 1)))
        self.assertTrue(l.released(clear_tcps, pads, stowed_pos, (0, 0, 0, 1)))

    def test_stillness_condition(self):
        """Peak-to-peak motion <= 1 mm over 20 steps passes stillness; > 1 mm fails."""
        still_hist = [(0.290, 0.000, 0.7515)] * 20
        moving_hist = [(0.290, 0.000 + 0.0001 * i, 0.7515) for i in range(20)]  # 1.9 mm motion
        self.assertTrue(l.still(still_hist))
        self.assertFalse(l.still(moving_hist))


if __name__ == "__main__":
    unittest.main()
