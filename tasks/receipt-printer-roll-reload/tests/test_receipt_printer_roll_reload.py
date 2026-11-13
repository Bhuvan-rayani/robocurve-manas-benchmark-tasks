import json
import math
import pathlib
import re
import sys
import types
import unittest

HERE = pathlib.Path(__file__).resolve()
TASK = HERE.parents[1]
sys.path.insert(0, str(TASK))
# The demo plan imports yam_arena (numpy only). It sits in the project's yam-upstream copy when it is not installed.
_ROOT = HERE.parents[3].parent
_KNOWN = _ROOT / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
for cand in [_KNOWN] if (_KNOWN / "yam_arena").is_dir() else _ROOT.rglob("yam-upstream"):
    if (cand / "yam_arena").is_dir():
        sys.path.insert(0, str(cand))
        break

import numpy as np  # noqa: E402

import geometry as g  # noqa: E402
from logic import (  # noqa: E402
    axis_off_y_deg,
    evaluate_state,
    feeds,
    lamp_state,
    on_stand,
    roll_centre,
    seated,
    tail_points_back,
    tail_tip,
    tilt_deg,
)

try:
    import demo_plan  # noqa: E402
    import scoring  # noqa: E402

    HAVE_SIM_API = True
except Exception:  # pragma: no cover - no yam_arena anywhere
    HAVE_SIM_API = False


def quat_z(deg):
    h = math.radians(deg) / 2
    return (0.0, 0.0, math.sin(h), math.cos(h))


def quat_y(deg):
    h = math.radians(deg) / 2
    return (0.0, math.sin(h), 0.0, math.cos(h))


def quat_x(deg):
    h = math.radians(deg) / 2
    return (math.sin(h), 0.0, 0.0, math.cos(h))


FLIP = quat_z(180.0)           # free end toward -x: correct
WRONG = quat_z(0.0)            # free end toward +x: wrong way round
SEAT_POS = (g.SEAT_XY[0], g.SEAT_XY[1], g.TABLE_TOP + g.SEAT_ORIGIN_Z)
START_POS = (g.ROLL_START_XY[0], g.ROLL_START_XY[1], g.TABLE_TOP + g.ROLL_START_ORIGIN_Z)
START_QUAT = quat_z(-90.0)
SPEED = 0.01


def full(slide=0.0, open_run=25, lift=0.2, fixture=False, released=True, still=True, pos=SEAT_POS, quat=FLIP):
    return evaluate_state(pos, quat, slide, open_run, lift, fixture, released, still)[0]


class Logic(unittest.TestCase):
    def test_full(self):
        self.assertEqual(full(), 1.0)

    def test_not_released_or_not_still(self):
        self.assertEqual(full(released=False), 0.75)
        self.assertEqual(full(still=False), 0.75)

    def test_cover_not_closed_is_half(self):
        self.assertEqual(full(slide=0.12), 0.5)
        self.assertEqual(full(slide=0.003), 0.5)       # 3 mm: not closed
        self.assertEqual(full(slide=0.0019), 1.0)

    def test_wrong_orientation_is_zero(self):
        # seated in position but the free end runs toward the rear wall: zero even with everything else perfect
        self.assertEqual(full(quat=WRONG), 0.0)
        self.assertEqual(full(quat=WRONG, slide=0.12), 0.0)
        self.assertTrue(tail_points_back(WRONG))
        self.assertFalse(tail_points_back(FLIP))

    def test_hovering_or_tilted_roll_is_not_seated(self):
        up = (SEAT_POS[0], SEAT_POS[1], SEAT_POS[2] + 0.005)
        down = (SEAT_POS[0], SEAT_POS[1], SEAT_POS[2] - 0.005)
        self.assertFalse(seated(up, FLIP))
        self.assertFalse(seated(down, FLIP))
        self.assertEqual(full(pos=up, lift=0.0, open_run=0), 0.0)
        self.assertFalse(seated(SEAT_POS, quat_x(7.0)))
        self.assertGreaterEqual(tilt_deg(quat_x(7.0)), 6.9)

    def test_seat_tolerances(self):
        def at(dx=0.0, dy=0.0, dz=0.0):
            return (SEAT_POS[0] + dx, SEAT_POS[1] + dy, SEAT_POS[2] + dz)

        self.assertTrue(seated(at(0.011), FLIP))
        self.assertFalse(seated(at(0.013), FLIP))
        self.assertTrue(seated(at(dy=0.007), FLIP))
        self.assertFalse(seated(at(dy=0.009), FLIP))
        self.assertTrue(seated(at(dz=0.0025), FLIP))
        self.assertFalse(seated(at(dz=0.0035), FLIP))
        self.assertTrue(seated(SEAT_POS, quat_z(180.0 + 4.0)))
        self.assertFalse(seated(SEAT_POS, quat_z(180.0 + 6.0)))
        self.assertFalse(seated(SEAT_POS, quat_z(90.0)))       # axis along x: across the wrong way

    def test_feeds_needs_the_free_end_through_the_exit(self):
        self.assertTrue(feeds(SEAT_POS, FLIP))
        tip = tail_tip(SEAT_POS, FLIP)
        self.assertAlmostEqual(float(tip[0]), g.SEAT_XY[0] - g.TAIL_LEN_M, places=6)
        self.assertLess(float(tip[0]), g.FRONT_FACE_X - 0.02)
        # a tail that does not reach 2 cm outside the front face
        shifted = (SEAT_POS[0] + 0.045, SEAT_POS[1], SEAT_POS[2])
        self.assertFalse(feeds(shifted, FLIP))
        # a tail lifted off the chute (roll turned about its own axis)
        self.assertFalse(feeds(SEAT_POS, quat_y(30.0)))
        # tail off to the side of the exit
        self.assertFalse(feeds((SEAT_POS[0], SEAT_POS[1] + 0.03, SEAT_POS[2]), FLIP))

    def test_quarter_turn_the_wrong_way_ends_toward_the_rear(self):
        # the roll starts with its free end toward -y; +90 deg (counter-clockwise from above) points it toward +x, -90 toward -x
        for deg, back in ((90.0, True), (-90.0, False)):
            q = quat_z(-90.0 + deg)
            self.assertEqual(tail_points_back(q), back)

    def test_start_pose_is_on_the_stand_and_scores_zero(self):
        self.assertTrue(on_stand(START_POS, START_QUAT))
        c = roll_centre(START_POS, START_QUAT)
        self.assertAlmostEqual(float(c[2]) - g.TABLE_TOP, g.ROLL_START_CENTRE_Z, places=6)
        self.assertEqual(evaluate_state(START_POS, START_QUAT, 0.0, 0, 0.0, False, True, True)[0], 0.0)
        # axis of the start pose runs along x, so it is not a valid seat
        self.assertAlmostEqual(axis_off_y_deg(START_QUAT), 90.0, places=4)

    def test_quarter_level(self):
        # cover held open for 1 s and the roll lifted 3 cm, roll back on the stand: 0.25
        self.assertEqual(evaluate_state(START_POS, START_QUAT, 0.0, 20, 0.05, False, True, True)[0], 0.25)
        self.assertEqual(evaluate_state(START_POS, START_QUAT, 0.0, 19, 0.05, False, True, True)[0], 0.0)    # open under 1 s
        self.assertEqual(evaluate_state(START_POS, START_QUAT, 0.0, 20, 0.029, False, True, True)[0], 0.0)   # lifted under 3 cm
        # the roll ends on the bench in front of the printer: zero
        bench = (0.20, -0.02, g.TABLE_TOP + 0.013)
        self.assertEqual(evaluate_state(bench, START_QUAT, 0.0, 30, 0.1, False, True, True)[0], 0.0)

    def test_fixture_moved_is_zero(self):
        self.assertEqual(full(fixture=True), 0.0)

    def test_lamp(self):
        self.assertEqual(lamp_state(START_POS, START_QUAT, 0.0), "red")
        self.assertEqual(lamp_state(SEAT_POS, FLIP, 0.0), "green")
        self.assertEqual(lamp_state(SEAT_POS, FLIP, 0.1), "red")                # cover open
        self.assertEqual(lamp_state(SEAT_POS, WRONG, 0.0), "amber")             # seated, free end not feeding


class Geometry(unittest.TestCase):
    def test_roll_is_a_real_thermal_roll(self):
        self.assertEqual(g.ROLL_WIDTH_M, 0.058)
        self.assertEqual(2 * g.ROLL_RADIUS_M, 0.060)
        self.assertEqual(g.PAPER_ROLL_MASS_KG, 0.09)
        self.assertEqual(2 * g.ROLL_CORE_RADIUS_M, 0.025)
        self.assertGreater(0.094 - g.ROLL_WIDTH_M, 0.035)                      # 18 mm per side in the 94 mm gripper

    def test_printer_moved_three_cm_toward_the_robot(self):
        self.assertEqual(g.PRINTER_XY[0], 0.26)
        self.assertAlmostEqual(g.FRONT_FACE_X, 0.19)
        self.assertEqual(g.SEAT_XY[0], 0.251)
        self.assertAlmostEqual(g.BAY_X_RANGE[0] + (g.BAY_X_RANGE[1] - g.BAY_X_RANGE[0]) / 2, g.SEAT_XY[0], places=3)

    def test_bay_and_chocks_match_the_roll(self):
        self.assertAlmostEqual(2 * g.CRADLE_HALF_WIDTH_M, 0.068)
        self.assertAlmostEqual(g.CRADLE_HALF_WIDTH_M - g.ROLL_WIDTH_M / 2, 0.005)
        chock_inner = g.STAND_CHOCK[0][1] - g.STAND_CHOCK[1][1] / 2
        self.assertAlmostEqual(chock_inner - g.ROLL_RADIUS_M, 0.0085)           # 8.5 mm behind the roll
        self.assertLess(g.STAND_CHOCK[1][0], g.ROLL_WIDTH_M)                    # chock narrower than the roll
        # the paper strip (58 wide) passes the exit notch with room, the roll sits in an 8.2 cm bay with 11 mm per side
        self.assertGreater(2 * g.NOTCH_HALF_WIDTH_M - g.ROLL_WIDTH_M, 0.03)
        self.assertAlmostEqual((g.BAY_X_RANGE[1] - g.BAY_X_RANGE[0] - 2 * g.ROLL_RADIUS_M) / 2, 0.011, places=3)

    def test_cover_spring_and_travel(self):
        self.assertLessEqual(g.COVER_SPRING_N_PER_M, 10.0)                      # arm-held spring limit
        self.assertLessEqual(g.COVER_SPRING_N_PER_M * g.COVER_TRAVEL_M, 1.0 + 1e-9)
        self.assertEqual(g.COVER_TRAVEL_M, 0.125)

    def test_bay_open_threshold_clears_roll_and_palm(self):
        near_edge = g.FRONT_FACE_X + g.BAY_OPEN_M                               # cover's near edge when open
        self.assertGreater(near_edge, g.BAY_X_RANGE[1])
        palm_max_x = g.SEAT_XY[0] + 0.030                                       # 60 mm deep hand body, centred on the TCP
        self.assertGreater(near_edge - palm_max_x, 0.010)

    def test_seated_roll_fits_under_the_closed_cover_and_over_the_shoulders(self):
        roll_top = g.SEAT_CENTRE_Z + g.ROLL_RADIUS_M
        self.assertAlmostEqual(g.COVER_REST[2] - roll_top, 0.007, places=4)
        # pads reach 13 mm below the commanded centre; at the lowest waypoint they stay above the cradle shoulders
        z_pad_bottom = g.SEAT_CENTRE_Z + 0.008 + 0.002 - 0.013
        self.assertGreater(z_pad_bottom - g.SHOULDER_TOP_Z, 0.010)

    def test_all_part_boxes_are_ordinary(self):
        for name, boxes in (("printer", g.PRINTER_BOXES), ("cover", g.COVER_BOXES), ("stand", (g.STAND_PLATE, g.STAND_CHOCK)), ("tail", (g.ROLL_TAIL,))):
            for c, s, col in boxes:
                self.assertTrue(all(v > 0 for v in s), (name, s))
                self.assertTrue(all(0.0 <= v <= 1.0 for v in col), (name, col))

    def test_stand_and_printer_do_not_overlap(self):
        stand_x1 = g.STAND_XY[0] + g.STAND_PLATE[1][0] / 2
        self.assertLess(stand_x1, g.FRONT_FACE_X - 0.003)


@unittest.skipUnless(HAVE_SIM_API, "yam_arena not importable")
class Demo(unittest.TestCase):
    TOP = g.TABLE_TOP

    @staticmethod
    def _track(plan, ready, dt=0.05):
        """Sampled (t, x, y, z, yaw) along a waypoint list, straight lines between waypoints from the ready pose."""
        out, t, prev, prev_yaw = [], 0.0, np.array(ready, dtype=float), 0.0
        for w in plan:
            goal = np.array(w.pos, dtype=float)
            n = max(1, int(round(w.duration / dt)))
            for i in range(1, n + 1):
                u = i / n
                out.append((t + w.duration * u, *(prev + (goal - prev) * u), prev_yaw + (w.yaw - prev_yaw) * u))
            t += w.duration
            prev, prev_yaw = goal, w.yaw
        return out

    def _plans(self):
        plan = demo_plan.make_demo_plan()
        return plan, self._track(plan["left"], demo_plan.L_READY), self._track(plan["right"], demo_plan.R_READY)

    def test_every_waypoint_is_inside_the_reach_limits(self):
        plan, _, _ = self._plans()
        for side in ("left", "right"):
            for w in plan[side]:
                x, y, z = w.pos
                self.assertLessEqual(x, 0.30, (side, w.label))
                self.assertLessEqual(abs(y), 0.22, (side, w.label))
                self.assertLessEqual(z - self.TOP, 0.1601, (side, w.label))
                self.assertGreaterEqual(z - self.TOP, 0.04, (side, w.label))
                self.assertTrue(math.isfinite(w.yaw))

    def test_final_push_is_about_x_0285_and_opens_the_bay(self):
        self.assertAlmostEqual(demo_plan.PUSH_X_FAR, 0.286, places=3)
        face = demo_plan.PUSH_X_FAR + 0.010                                     # finger front is 10 mm ahead of the commanded centre
        slide = face - g.TAB_FRONT_X
        self.assertGreater(slide, g.BAY_OPEN_M + 0.010)                         # 13 mm for the arm's lag
        self.assertLessEqual(slide, g.COVER_TRAVEL_M)

    def test_hands_stay_at_least_120_mm_apart_in_y(self):
        _, left, right = self._plans()
        n = min(len(left), len(right))
        worst = 9.0
        for i in range(n):
            ysep = left[i][2] - right[i][2]
            xmin = min(left[i][1], right[i][1])
            need = 0.19 if xmin <= 0.12 else 0.12
            self.assertGreaterEqual(ysep, need - 1e-9, (left[i][0], ysep))
            worst = min(worst, ysep)
        self.assertGreaterEqual(worst, 0.125)

    def test_roll_grip_and_carry_heights(self):
        # commanded centre 8 mm above the roll's axis: pad bottom (13 mm below) 5 mm under the axis, palm 8 mm over the roll's top
        self.assertAlmostEqual(demo_plan.GRASP[2] - self.TOP, g.ROLL_START_CENTRE_Z + 0.008, places=6)
        centre = demo_plan.GRASP[2] - self.TOP - 0.008
        self.assertGreaterEqual((demo_plan.GRASP[2] - self.TOP + 0.030) - (centre + g.ROLL_RADIUS_M), 0.0079)   # palm 8 mm over the roll's top
        roll_bottom = demo_plan.CARRY_Z - 0.008 - g.ROLL_RADIUS_M
        tail_bottom = roll_bottom - g.TAIL_T_M
        ribs_top = g.COVER_REST[2] + 0.013
        self.assertGreater(tail_bottom - self.TOP - ribs_top, 0.005)            # clears a CLOSED cover too: no shoving it open with the roll
        self.assertGreater(tail_bottom - self.TOP - g.PRINTER_SIZE[2], 0.015)   # and the front posts
        self.assertAlmostEqual(demo_plan.FINGER_GRIP, -0.027, places=6)         # 2 mm squeeze per side on the 58 mm width

    def test_quarter_turn_direction(self):
        plan, _, _ = self._plans()
        yaws = [w.yaw for w in plan["right"]]
        self.assertAlmostEqual(max(yaws), 1.5708, places=4)
        self.assertAlmostEqual(yaws[-1], 0.0)
        for w in plan["right"]:
            self.assertIn(round(w.yaw, 4), (0.0, 1.5708))

    def test_left_holds_the_cover_until_the_right_has_lifted_clear(self):
        plan = demo_plan.make_demo_plan()
        t = 0.0
        t_release_left = None
        for w in plan["left"]:
            if w.label == "let the cover go":
                t_release_left = t
            t += w.duration
        t, t_lift_right = 0.0, None
        for w in plan["right"]:
            t += w.duration
            if w.label == "lift straight up":
                t_lift_right = t
        self.assertIsNotNone(t_release_left)
        self.assertGreater(t_release_left, t_lift_right)

    def test_demo_fits_the_run_limit(self):
        plan = demo_plan.make_demo_plan()
        steps = max(sum(w.duration for w in v) for v in plan.values()) * 20
        self.assertLess(steps, 1500 * 0.5)

    def test_ablation_plans_leave_one_arm_at_ready(self):
        left_idle = demo_plan.make_demo_plan(ablation="left")
        right_idle = demo_plan.make_demo_plan(ablation="right")
        self.assertEqual(len(left_idle["left"]), 1)
        self.assertEqual(tuple(left_idle["left"][0].pos), demo_plan.L_READY)
        self.assertEqual(len(right_idle["right"]), 1)
        self.assertGreater(len(left_idle["right"]), 5)
        self.assertGreater(len(right_idle["left"]), 5)


class Ablation(unittest.TestCase):
    def test_left_idle_cover_blocks_the_bay(self):
        # the cover never opens: the roll ends on top of the cover or on the bench; never seated, never above 0.25
        on_cover = (g.SEAT_XY[0], g.SEAT_XY[1], g.TABLE_TOP + g.COVER_REST[2] + 0.013 + 0.003)
        self.assertEqual(evaluate_state(on_cover, FLIP, 0.0, 0, 0.12, False, True, True)[0], 0.0)
        self.assertEqual(evaluate_state(START_POS, START_QUAT, 0.0, 0, 0.0, False, True, True)[0], 0.0)

    def test_right_idle_nothing_loaded(self):
        # the cover is held open and nothing else happens: the roll never leaves the stand
        self.assertEqual(evaluate_state(START_POS, START_QUAT, 0.0, 400, 0.0, False, True, True)[0], 0.0)
        self.assertEqual(evaluate_state(START_POS, START_QUAT, 0.118, 400, 0.0, False, False, True)[0], 0.0)

    def test_neither_arm_alone_reaches_one(self):
        # full credit needs the cover open for 1 s AND the roll lifted: with either latched fact missing the state cannot be 1.0 here
        for open_run, lift in ((0, 0.2), (400, 0.0)):
            self.assertLess(evaluate_state(START_POS, START_QUAT, 0.0, open_run, lift, False, True, True)[0], 1.0)


@unittest.skipUnless(HAVE_SIM_API, "yam_arena not importable")
class Bookkeeping(unittest.TestCase):
    @staticmethod
    def _state(pos, slide=0.0):
        return types.SimpleNamespace(pos=np.array(pos, dtype=float), sliders={g.COVER_NAME: slide})

    def setUp(self):
        scoring._reset_run()
        self.printer = (g.PRINTER_XY[0], g.PRINTER_XY[1], g.TABLE_TOP)
        self.stand = (g.STAND_XY[0], g.STAND_XY[1], g.TABLE_TOP)

    def _step(self, slide=0.0, roll=START_POS, printer=None, stand=None):
        scoring.advance(self._state(printer or self.printer, slide), self._state(roll), self._state(stand or self.stand))

    def test_open_run_counts_consecutive_steps(self):
        for _ in range(19):
            self._step(slide=0.11)
        self._step(slide=0.05)                      # the run is broken
        for _ in range(19):
            self._step(slide=0.11)
        self.assertEqual(scoring._RUN["open_run_max"], 19)
        self._step(slide=0.11)
        self.assertEqual(scoring._RUN["open_run_max"], 20)

    def test_lift_and_fixture_latches(self):
        self._step(roll=(START_POS[0], START_POS[1], START_POS[2] + 0.04))
        self._step()
        self.assertAlmostEqual(scoring._RUN["max_lift"], 0.04, places=6)
        self.assertFalse(scoring._RUN["fixture_moved"])
        self._step(printer=(self.printer[0] + 0.006, self.printer[1], self.printer[2]))
        self.assertTrue(scoring._RUN["fixture_moved"])
        self._step()
        self.assertTrue(scoring._RUN["fixture_moved"])                          # permanent

    def test_stillness_window(self):
        for i in range(25):
            self._step(slide=0.0, roll=SEAT_POS)
        self.assertTrue(scoring.window_still())
        for i in range(25):                          # the cover creeps 5 mm in the window
            self._step(slide=0.0002 * i, roll=SEAT_POS)
        self.assertFalse(scoring.window_still())
        scoring._reset_run()
        for i in range(25):                          # the roll creeps 3 mm in the window
            self._step(roll=(SEAT_POS[0] + 0.00012 * i, SEAT_POS[1], SEAT_POS[2]))
        self.assertFalse(scoring.window_still())

    def test_release_distance_rule(self):
        roll_pos = np.array(SEAT_POS)
        far = np.array([0.10, -0.14, g.TABLE_TOP + 0.12])
        near_roll = np.array([g.SEAT_XY[0], g.SEAT_XY[1], g.TABLE_TOP + 0.063 + 0.040])   # 10 mm above the roll's top
        near_printer = np.array([g.FRONT_FACE_X - 0.02, 0.0, g.TABLE_TOP + 0.02])
        self.assertTrue(scoring.hands_clear([far, far * np.array([1, -1, 1]) + np.array([0, 0, 0])], roll_pos, FLIP, 0.0))
        self.assertFalse(scoring.hands_clear([far, near_roll], roll_pos, FLIP, 0.0))
        self.assertFalse(scoring.hands_clear([far, near_printer], roll_pos, FLIP, 0.0))
        # the left gripper left at the pushed-back tab is within 3 cm of the cover
        tab = np.array([g.TAB_CENTRE_XYZ[0] - 0.02, g.TAB_CENTRE_XYZ[1], g.TABLE_TOP + g.TAB_CENTRE_XYZ[2]])
        self.assertFalse(scoring.hands_clear([tab], roll_pos, FLIP, 0.0))
        # the ready poses are clear of everything
        self.assertTrue(scoring.hands_clear([np.array([0.10, 0.14, g.TABLE_TOP + 0.12]), np.array([0.10, -0.14, g.TABLE_TOP + 0.12])], roll_pos, FLIP, 0.0))


class Text(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tj = json.loads((TASK / "task.json").read_text(encoding="ascii"))
        cls.readme = (TASK / "README.md").read_text(encoding="ascii")

    def test_limits(self):
        t = self.tj
        self.assertLessEqual(len(t["title"]), 120)
        self.assertTrue(20 <= len(t["instruction"]) <= 540)
        self.assertLessEqual(len(t["context"]), 900)
        self.assertLessEqual(len(t["fidelity"]), 500)
        self.assertEqual(t["category"], "Impact on jobs")
        self.assertIn("41-2011.00", t["context"])
        self.assertIn("Epson TM-T20II", t["context"])                           # the verified manual source
        self.assertIn("Possible scores:", t["scoring"])

    def test_readme_paragraphs_equal_task_json(self):
        paras = [p.strip() for p in self.readme.split("\n\n")]
        self.assertEqual(paras[0], "# " + self.tj["title"])
        for key in ("instruction", "context", "setup", "reset_notes", "scoring", "fidelity"):
            self.assertIn(self.tj[key].strip(), paras, key)

    def test_numbers_in_the_text_match_the_code(self):
        s = self.tj["setup"] + " " + self.tj["scoring"]
        for needle in ("(26, 0)", "58 mm wide, 60 mm across, 25 mm core", "90 g", "8 N/m", "12.5 cm", "10.5 cm", "6.8 cm", "(14, -14)",
                       "within 12 mm in x, 8 mm in y and 3 mm in z", "x <= 17.0 cm", "(25.1, 0, z 6.3)", "5 mm"):
            self.assertIn(needle, s, needle)
        self.assertAlmostEqual(g.PRINTER_XY[0], 0.26)
        self.assertAlmostEqual(g.SEAT_TOL_X_M, 0.012)
        self.assertAlmostEqual(g.SEAT_TOL_Y_M, 0.008)
        self.assertAlmostEqual(g.SEAT_TOL_Z_M, 0.003)
        self.assertAlmostEqual(g.FEED_TIP_MAX_X, 0.17)
        self.assertAlmostEqual(g.BAY_OPEN_M, 0.105)
        self.assertAlmostEqual(g.FIXTURE_MOVE_M, 0.005)

    def test_ascii_and_run_sh_instruction(self):
        raw = (TASK / "task.json").read_bytes()
        raw.decode("ascii")
        run = (TASK / "run.sh").read_bytes()
        self.assertNotIn(b"\r\n", run)
        self.assertIn(self.tj["instruction"], run.decode("ascii"))
        for mode in ("settle", "demo", "ablation", "dream"):
            self.assertIn(mode + ")", run.decode("ascii"))


@unittest.skipUnless(HAVE_SIM_API, "yam_arena not importable")
class Parts(unittest.TestCase):
    def test_parts_validate(self):
        import task

        self.assertEqual([o.name for o in task.OBJECTS], [g.PRINTER_NAME, g.ROLL_NAME, g.STAND_NAME])
        for o in task.OBJECTS:
            o._check()
            self.assertGreaterEqual(len(o.boxes), 1)                            # one box per Part: a cylinder carries a 1 mm box
        printer = task.OBJECTS[0]
        self.assertEqual([s.name for s in printer.sliders], [g.COVER_NAME])
        self.assertEqual(printer.sliders[0].axis, "+X")
        self.assertEqual(printer.sliders[0].rate, 8.0)
        self.assertEqual(task.OBJECTS[1].mass, 0.09)

    def test_markers_are_created_once_and_only_moved(self):
        text = (TASK / "display.py").read_text(encoding="ascii")
        code = "\n".join(line for line in text.splitlines() if not line.strip().startswith("#"))
        self.assertNotIn(".set_visibility(", code)                              # never toggled mid-episode
        self.assertIn("-10.0", code)                                            # unused markers are parked 10 m under the floor
        self.assertIn(".visualize(", code)


if __name__ == "__main__":
    unittest.main()
