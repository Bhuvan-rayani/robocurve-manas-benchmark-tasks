"""Unit tests for zero_linear_axis (v2): geometry, scoring ladder and gates, task file contract, demo modes, blind review."""

from __future__ import annotations

import math
import os
import re
import sys
import unittest
from pathlib import Path

import numpy as np

_TASK_DIR = Path(__file__).resolve().parent.parent
_UPSTREAM = None
for parent in _TASK_DIR.parents:
    cand = parent / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
    if cand.exists():
        _UPSTREAM = cand
        break
for p in (_TASK_DIR, _UPSTREAM):
    if p is not None and str(p) not in sys.path:
        sys.path.insert(0, str(p))

import demo_plan  # noqa: E402
import geometry as g  # noqa: E402
import logic  # noqa: E402
import scoring  # noqa: E402

UPRIGHT = (0.0, 0.0, 0.0, 1.0)
BASE0 = g.BASE_POS_WORLD
PIN_FAR = (0.20, 0.20, g.TABLE_TOP + g.PIN_HEIGHT_M / 2)  # pin standing on the table at its start


def pin_in_hole(disp: float, dy: float = 0.0):
    hx, hy = logic.hole_world_xy(BASE0, disp)
    return (hx, hy + dy, g.TABLE_TOP + g.PIN_HEIGHT_M / 2)


def ev(disp, pin=PIN_FAR, pin_quat=UPRIGHT, base=BASE0, base_quat=UPRIGHT, resting=True):
    return logic.evaluate_state(base, base_quat, disp, pin, pin_quat, resting=resting)


class State:
    def __init__(self, pos, quat=UPRIGHT, sliders=None, still=True):
        self.pos, self.quat_xyzw, self.sliders, self._still = pos, quat, sliders or {}, still

    def resting(self):
        return self._still


class TestGeometry(unittest.TestCase):
    def test_marks_align_after_40mm(self):
        # base mark at y -0.060 (base frame), carriage mark at rest -0.100: a 40 mm push aligns them
        self.assertAlmostEqual(-0.100 + g.CARRIAGE_TARGET_DISP_M, -0.060)

    def test_hole_is_wider_than_pin(self):
        self.assertGreaterEqual(g.HOLE_HALF_WIDTH_M - g.PIN_RADIUS_M, 0.003 - 1e-9)  # 3 mm per side

    def test_working_points_are_far_apart(self):
        self.assertGreaterEqual(demo_plan.L_BRACE_Y - demo_plan.R_CONTACT_Y, 0.15)

    def test_pin_fits_in_open_gripper(self):
        self.assertLess(2 * g.PIN_RADIUS_M, 0.094 - 0.04)

    def test_everything_in_reach(self):
        for name, (x, y) in {"base hold": (demo_plan.L_BRACE_X, demo_plan.L_BRACE_Y), "pin": g.PIN_START_XY,
                             "hole": (g.HOLE_WORLD_X, demo_plan.HOLE_Y)}.items():
            d = math.hypot(x - 0.0, y - 0.305)  # left arm
            self.assertLess(d, 0.50, f"{name} out of left-arm reach: {d:.2f} m")
        d = math.hypot(demo_plan.R_X, demo_plan.R_CONTACT_Y + 0.305)
        self.assertLess(d, 0.50)


class TestScoring(unittest.TestCase):
    def test_first_update_is_zero(self):
        s, ok, _ = ev(0.0)
        self.assertEqual((s, ok), (0.0, False))

    def test_idle_policy_scores_zero(self):
        # the pin cannot be through the hole without a robot: it starts far away
        self.assertEqual(ev(0.0)[0], 0.0)

    def test_ladder_levels(self):
        self.assertEqual(ev(0.025)[0], 0.25)          # pushed 25 mm: partial credit
        self.assertEqual(ev(0.019)[0], 0.0)           # below 20 mm
        self.assertEqual(ev(0.035)[0], 0.5)           # offset 5 mm
        self.assertEqual(ev(0.0375)[0], 0.75)         # offset 2.5 mm
        self.assertEqual(ev(0.040)[0], 0.75)          # aligned, no pin
        self.assertEqual(ev(0.043)[0], 0.75)          # offset 3 mm
        self.assertEqual(ev(0.0455)[0], 0.5)          # offset 5.5 mm
        self.assertEqual(ev(0.052)[0], 0.25)          # overshoot of 12 mm keeps the 0.25 credit (moved >= 20 mm)
        self.assertEqual(ev(0.095)[0], 0.0)           # pushed far past the datum (offset 55 mm): no credit

    def test_full_score(self):
        s, ok, _ = ev(0.040, pin=pin_in_hole(0.040))
        self.assertEqual((s, ok), (1.0, True))

    def test_two_valid_solutions(self):
        a = ev(0.040, pin=pin_in_hole(0.040))
        b = ev(0.0385, pin=pin_in_hole(0.0385, dy=0.003))
        self.assertEqual((a[0], b[0]), (1.0, 1.0))

    def test_pin_must_be_in_hole(self):
        self.assertEqual(ev(0.040, pin=pin_in_hole(0.040, dy=0.020))[0], 0.75)

    def test_pin_must_be_through(self):
        hx, hy = logic.hole_world_xy(BASE0, 0.04)
        high = (hx, hy, g.TABLE_TOP + 0.075)  # resting on top of the lug
        self.assertEqual(ev(0.040, pin=high)[0], 0.75)

    def test_pin_must_be_upright(self):
        a = math.radians(30) / 2
        tilted = (math.sin(a), 0.0, 0.0, math.cos(a))
        self.assertEqual(ev(0.040, pin=pin_in_hole(0.040), pin_quat=tilted)[0], 0.75)

    def test_unheld_base_cannot_reach_full_score(self):
        drifted = (BASE0[0], BASE0[1] - 0.012, BASE0[2])
        s, ok, _ = ev(0.040, pin=pin_in_hole(0.040), base=drifted)
        # hole moved with the base: pin in the (moved) hole still, but drift 12 mm > 8 mm
        self.assertLess(s, 1.0)

    def test_gates(self):
        self.assertEqual(ev(0.040, base=(BASE0[0], BASE0[1] - 0.06, BASE0[2]))[0], 0.0)
        self.assertEqual(ev(0.040, base=(BASE0[0], BASE0[1], BASE0[2] - 0.05))[0], 0.0)
        a = math.radians(30) / 2
        self.assertEqual(ev(0.040, base_quat=(math.sin(a), 0.0, 0.0, math.cos(a)))[0], 0.0)

    def test_must_be_still(self):
        self.assertEqual(ev(0.040, pin=pin_in_hole(0.040), resting=False)[0], 0.75)

    def test_fuzz(self):
        rng = np.random.default_rng(7)
        for _ in range(500):
            s, ok, why = ev(float(rng.uniform(-0.02, 0.14)),
                            pin=tuple(float(v) for v in rng.uniform([0.1, -0.3, 0.7], [0.4, 0.3, 0.9])),
                            base=tuple(float(v) for v in rng.uniform([0.2, -0.1, 0.7], [0.3, 0.1, 0.8])),
                            resting=bool(rng.integers(2)))
            self.assertTrue(0.0 <= s <= 1.0)
            self.assertIsInstance(why, str)
            self.assertEqual(ok, s == 1.0)


class TestTaskFile(unittest.TestCase):
    def test_loads(self):
        import yam_arena.task_file as tf

        t = tf.load(str(_TASK_DIR / "task.py"))
        self.assertEqual(t.scene, "station")
        self.assertEqual(t.success_hold_s, 1.0)
        self.assertEqual([o.name for o in t.objects], ["axis_base", "lock_pin"])

    def test_score_wrapper_first_update(self):
        objs = {g.BASE_NAME: State(BASE0, sliders={g.CARRIAGE_NAME: 0.0}), g.PIN_NAME: State(PIN_FAR)}
        self.assertEqual(scoring.score(objs), 0.0)
        self.assertFalse(scoring.success(objs))

    def test_score_wrapper_full(self):
        objs = {g.BASE_NAME: State(BASE0, sliders={g.CARRIAGE_NAME: 0.040}), g.PIN_NAME: State(pin_in_hole(0.040))}
        self.assertEqual(scoring.score(objs), 1.0)
        self.assertTrue(scoring.success(objs))


class TestPlans(unittest.TestCase):
    def test_modes(self):
        for var in ("SETTLE_ONLY", "ABLATION"):
            os.environ[var] = "1"
            p = demo_plan.plans()
            del os.environ[var]
            self.assertEqual(set(p), {"left", "right"})
        p = demo_plan.plans()
        self.assertGreater(sum(w.duration for w in p["left"]), 20)

    def test_settle_is_an_explicit_hold(self):
        os.environ["SETTLE_ONLY"] = "1"
        p = demo_plan.plans()
        del os.environ["SETTLE_ONLY"]
        self.assertTrue(all(len(v) >= 1 for v in p.values()))

    def test_plan_length_within_run_limit(self):
        p = demo_plan.plans()
        steps = max(sum(w.duration for w in v) for v in p.values()) * 20
        self.assertLess(steps, 1200)

    def test_env_vars_are_read(self):
        src = (_TASK_DIR / "demo_plan.py").read_text()
        for name in re.findall(r"DEMO_[A-Z_]+", (_TASK_DIR / "run.sh").read_text()):
            self.assertIn(name, src)


class TestBlindReview(unittest.TestCase):
    def test_no_identifying_strings(self):
        bad = ["c:\\users", "c:/users", "github.com/", "/home/"]
        email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
        words = [w.strip().lower() for w in os.getenv("TEAM_WORDS", "").split(",") if w.strip()]
        for f in _TASK_DIR.rglob("*"):
            if f.suffix not in {".py", ".md", ".json", ".sh"} or "tests" in f.parts or f.name == "VM_NOTES.md":
                continue
            text = f.read_text(encoding="utf-8", errors="ignore").lower()
            for b in bad:
                self.assertNotIn(b, text, f"{b!r} in {f.name}")
            self.assertIsNone(email.search(text), f"email in {f.name}")
            for w in words:
                self.assertNotIn(w, text, f"team word in {f.name}")


if __name__ == "__main__":
    unittest.main()
