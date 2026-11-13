import json
import math
import pathlib
import re
import sys
import unittest

TASK_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TASK_DIR))

import numpy as np  # noqa: E402

from geometry import (  # noqa: E402
    BREW_STEPS,
    BUTTON_NAME,
    HANDLE_BOXES,
    KEEPOUT_FINGER_MARGIN_M,
    KEEPOUT_RADIUS_M,
    MUG_GRIP_Z,
    MUG_RADIUS_M,
    NOZZLE_XY,
    PLATE_TOP_Z,
    RING_INNER_HALF_M,
    SAUCER_CRACKED_XY,
    SAUCER_GOOD_XY,
    SAUCER_HEIGHT_M,
    SAUCER_MAX_OFFCENTRE_M,
    SHELF_NAME,
    SHELF_REST_TOL_M,
    TABLE_TOP,
)
from logic import (  # noqa: E402
    CRACKED,
    GOOD,
    advance,
    evaluate_state,
    fault_reasons,
    hands_clear,
    in_stream_zone,
    mug_under_nozzle,
    new_ledger,
    on_own_saucer,
    still,
    touches_hot_wall,
)
from display import LAYERS, display_plan  # noqa: E402

FLAT = (0.0, 0.0, 0.0, 1.0)
PLATE_TOP = TABLE_TOP + PLATE_TOP_Z
SAUCER_POS = (SAUCER_GOOD_XY[0], SAUCER_GOOD_XY[1], TABLE_TOP + SAUCER_HEIGHT_M)
CRACKED_POS = (SAUCER_CRACKED_XY[0], SAUCER_CRACKED_XY[1], TABLE_TOP + SAUCER_HEIGHT_M)
MACHINE = (NOZZLE_XY[0], NOZZLE_XY[1], TABLE_TOP)
READY = [(0.10, 0.14, TABLE_TOP + 0.12), (0.10, -0.14, TABLE_TOP + 0.12)]
OUT = 0.12


def tilted(deg):
    h = math.radians(deg) / 2
    return (math.sin(h), 0.0, 0.0, math.cos(h))


def ring_pos(out, dx=0.0, dy=0.0, z=PLATE_TOP):
    return (NOZZLE_XY[0] - out + dx, NOZZLE_XY[1] + dy, z)


def mugs_at(good, cracked=None):
    return {GOOD: (good, FLAT), CRACKED: (cracked or CRACKED_POS, FLAT)}


def run(ledger, steps, shelf=0.0, button=0.0, good=None, cracked=None, tcps=READY, machine=MACHINE):
    good = good or ring_pos(0.0)
    for _ in range(steps):
        advance(ledger, shelf, button, mugs_at(good, cracked), machine, tcps)


def loaded_ledger(good=None, cracked=None):
    """A ledger in which the intact mug has been set in the ring with the shelf out 12 cm and the shelf has come home."""
    ledger = new_ledger()
    run(ledger, 3, shelf=-OUT, good=ring_pos(OUT), cracked=cracked)
    run(ledger, 3, shelf=0.0, good=good or ring_pos(0.0, 0.004, -0.003), cracked=cracked)
    return ledger


def brewed_ledger(steps=BREW_STEPS + 2, tcps=READY):
    ledger = loaded_ledger()
    run(ledger, steps, button=0.008, tcps=tcps, good=ring_pos(0.0, 0.004, -0.003))
    return ledger


def score(pos=SAUCER_POS, quat=FLAT, level=0.9, tiles=0, shelf=0.0, faults=(), released=True, is_still=True):
    return evaluate_state(pos, quat, level, tiles, shelf, faults, released, is_still)[0]


class Ladder(unittest.TestCase):
    def test_full(self):
        self.assertEqual(score(), 1.0)

    def test_idle_scores_zero(self):
        ledger = new_ledger()
        run(ledger, 200, good=SAUCER_POS)
        self.assertEqual(ledger["level"][GOOD], 0.0)
        self.assertEqual(ledger["brews"], 0)
        self.assertEqual(score(level=ledger["level"][GOOD]), 0.0)

    def test_released_and_still_are_required(self):
        self.assertEqual(score(released=False), 0.75)
        self.assertEqual(score(is_still=False), 0.75)

    def test_spill_limit(self):
        self.assertEqual(score(tiles=10), 1.0)
        self.assertEqual(score(tiles=11), 0.75)
        self.assertEqual(score(tiles=40), 0.75)

    def test_shelf_must_be_home(self):
        self.assertEqual(score(shelf=-SHELF_REST_TOL_M), 1.0)
        self.assertEqual(score(shelf=-(SHELF_REST_TOL_M + 0.002)), 0.75)

    def test_filled_but_elsewhere_is_half(self):
        self.assertEqual(score(pos=(0.30, -0.10, PLATE_TOP)), 0.5)
        self.assertEqual(score(pos=(SAUCER_POS[0], SAUCER_POS[1], SAUCER_POS[2] + 0.02)), 0.5)   # held above the saucer

    def test_partial_levels(self):
        self.assertEqual(score(level=0.84), 0.25)
        self.assertEqual(score(level=0.85), 1.0)
        self.assertEqual(score(level=0.10), 0.25)
        self.assertEqual(score(level=0.09), 0.0)

    def test_saucer_tolerances(self):
        x, y, z = SAUCER_POS
        self.assertTrue(on_own_saucer((x + 0.019, y, z), FLAT))
        self.assertFalse(on_own_saucer((x + 0.021, y, z), FLAT))
        self.assertTrue(on_own_saucer((x, y, z + 0.0029), FLAT))
        self.assertFalse(on_own_saucer((x, y, z + 0.004), FLAT))      # hovering
        self.assertTrue(on_own_saucer((x, y, z), tilted(2.9)))
        self.assertFalse(on_own_saucer((x, y, z), tilted(3.5)))
        # the other mug's saucer is not its own
        self.assertFalse(on_own_saucer((CRACKED_POS[0], CRACKED_POS[1], z), FLAT))


class Brew(unittest.TestCase):
    def test_full_brew_fills_to_ninety_percent(self):
        ledger = brewed_ledger()
        self.assertAlmostEqual(ledger["level"][GOOD], 0.9, places=6)
        self.assertEqual(ledger["good_steps"], BREW_STEPS)
        self.assertEqual(ledger["brews"], 1)
        self.assertEqual(len(ledger["tiles"]), 0)
        self.assertEqual(fault_reasons(ledger), [])
        self.assertIsNone(ledger["brew_step"])
        self.assertGreater(ledger["steam_until"], ledger["step"])

    def test_stream_runs_8_seconds(self):
        ledger = loaded_ledger()
        shown = 0
        for _ in range(BREW_STEPS + 40):
            advance(ledger, 0.0, 0.008, mugs_at(ring_pos(0.0)), MACHINE, READY)
            shown += ledger["brew_step"] is not None or ledger["target"] is not None
        self.assertEqual(shown, BREW_STEPS)

    def test_button_needs_6_mm(self):
        ledger = loaded_ledger()
        run(ledger, 50, button=0.0059)
        self.assertEqual(ledger["brews"], 0)
        run(ledger, 1, button=0.006)
        self.assertEqual(ledger["brews"], 1)

    def test_holding_the_button_does_not_restart_the_brew(self):
        ledger = brewed_ledger(steps=BREW_STEPS * 3)
        self.assertEqual(ledger["brews"], 1)
        # a new press on the full mug overflows: spill tiles, no more coffee
        run(ledger, 3, button=0.0)
        run(ledger, BREW_STEPS, button=0.008)
        self.assertEqual(ledger["brews"], 2)
        self.assertAlmostEqual(ledger["level"][GOOD], 0.9, places=6)
        self.assertEqual(len(ledger["tiles"]), 40)

    def test_pulling_the_shelf_out_mid_brew_stops_the_fill(self):
        ledger = loaded_ledger()
        run(ledger, 60, button=0.008, good=ring_pos(0.0))
        run(ledger, 100, button=0.008, shelf=-0.05, good=ring_pos(0.05))
        self.assertLess(ledger["level"][GOOD], 0.85)
        self.assertGreaterEqual(ledger["level"][GOOD], 0.3)
        self.assertGreater(len(ledger["tiles"]), 10)
        self.assertEqual(score(level=ledger["level"][GOOD], tiles=len(ledger["tiles"])), 0.25)

    def test_pressing_with_the_shelf_out_only_spills(self):
        ledger = new_ledger()
        run(ledger, 3, shelf=-OUT, good=ring_pos(OUT))
        run(ledger, BREW_STEPS + 5, shelf=-OUT, button=0.008, good=ring_pos(OUT))
        self.assertEqual(ledger["level"][GOOD], 0.0)
        self.assertEqual(len(ledger["tiles"]), 40)
        self.assertEqual(set(ledger["tiles"]), {"base"})

    def test_dry_brew_without_a_mug_spills_on_the_plate(self):
        ledger = new_ledger()
        run(ledger, 3, good=SAUCER_POS)
        run(ledger, BREW_STEPS, button=0.008, good=SAUCER_POS)
        self.assertEqual(set(ledger["tiles"]), {"plate"})
        self.assertEqual(len(ledger["tiles"]), 40)

    def test_mug_under_nozzle_tolerances(self):
        z = PLATE_TOP
        self.assertTrue(mug_under_nozzle((NOZZLE_XY[0] + 0.024, NOZZLE_XY[1], z), FLAT, 0.0))
        self.assertFalse(mug_under_nozzle((NOZZLE_XY[0] + 0.026, NOZZLE_XY[1], z), FLAT, 0.0))
        self.assertFalse(mug_under_nozzle((NOZZLE_XY[0], NOZZLE_XY[1], z + 0.02), FLAT, 0.0))     # held in the air
        self.assertFalse(mug_under_nozzle((NOZZLE_XY[0], NOZZLE_XY[1], z), tilted(12), 0.0))
        self.assertFalse(mug_under_nozzle((NOZZLE_XY[0], NOZZLE_XY[1], z), FLAT, -0.01))          # shelf not home


class Bypass(unittest.TestCase):
    def test_mug_set_under_the_head_with_the_shelf_home_gets_no_coffee(self):
        """Ablation, left arm idle: the right arm can only put the mug under the nozzle by hand; the stream falls past it."""
        ledger = new_ledger()
        run(ledger, 3, good=ring_pos(0.0))
        run(ledger, BREW_STEPS + 5, button=0.008, good=ring_pos(0.0))
        self.assertEqual(ledger["level"][GOOD], 0.0)
        self.assertFalse(ledger["loaded"][GOOD])
        self.assertEqual(score(level=ledger["level"][GOOD], tiles=len(ledger["tiles"])), 0.0)

    def test_loading_rules(self):
        ledger = new_ledger()
        run(ledger, 2, shelf=-0.03, good=ring_pos(0.03))
        self.assertFalse(ledger["loaded"][GOOD])                      # shelf out only 3 cm
        run(ledger, 2, shelf=-0.06, good=ring_pos(0.06))
        self.assertTrue(ledger["loaded"][GOOD])
        run(ledger, 2, shelf=0.0, good=ring_pos(0.0, 0.004, 0.0))
        self.assertTrue(ledger["loaded"][GOOD])                       # it rides the shelf home
        run(ledger, 2, shelf=-OUT, good=ring_pos(OUT, 0.0, 0.0, PLATE_TOP + 0.04))
        self.assertFalse(ledger["loaded"][GOOD])                      # lifted off the plate: must be loaded again

    def test_right_arm_idle_does_nothing(self):
        """Ablation, right arm idle: the shelf is pulled out and held, nothing is set, nothing is brewed."""
        ledger = new_ledger()
        run(ledger, 400, shelf=-OUT, good=SAUCER_POS)
        self.assertEqual(ledger["brews"], 0)
        self.assertEqual(score(pos=SAUCER_POS, level=0.0), 0.0)


class Faults(unittest.TestCase):
    def test_cracked_mug_brew_is_a_permanent_zero(self):
        ledger = new_ledger()
        # the cracked mug set in the ring and brewed into, while the intact mug is elsewhere
        run(ledger, 3, shelf=-OUT, good=SAUCER_POS, cracked=ring_pos(OUT))
        run(ledger, 3, shelf=0.0, good=SAUCER_POS, cracked=ring_pos(0.0))
        run(ledger, BREW_STEPS + 2, button=0.008, good=SAUCER_POS, cracked=ring_pos(0.0))
        self.assertTrue(ledger["crack_brewed"])
        self.assertIn("cracked", " ".join(fault_reasons(ledger)))
        self.assertEqual(score(faults=fault_reasons(ledger)), 0.0)

    def test_cracked_mug_fault_is_not_undone_by_a_good_brew_later(self):
        ledger = new_ledger()
        run(ledger, 3, shelf=-OUT, good=SAUCER_POS, cracked=ring_pos(OUT))
        run(ledger, 3, shelf=0.0, good=SAUCER_POS, cracked=ring_pos(0.0))
        run(ledger, 20, button=0.008, good=SAUCER_POS, cracked=ring_pos(0.0))
        run(ledger, 5, button=0.0, good=SAUCER_POS, cracked=ring_pos(0.0))
        self.assertTrue(ledger["crack_brewed"])
        self.assertEqual(score(level=0.9, faults=fault_reasons(ledger)), 0.0)

    def test_hand_in_the_stream_is_a_permanent_zero(self):
        in_zone = (NOZZLE_XY[0] - 0.05, 0.0, TABLE_TOP + 0.12)
        self.assertTrue(in_stream_zone(in_zone))
        ledger = loaded_ledger()
        run(ledger, 20, button=0.008, good=ring_pos(0.0, 0.004, -0.003), tcps=[READY[0], in_zone])
        self.assertTrue(ledger["zone_fault"])
        self.assertEqual(score(faults=fault_reasons(ledger)), 0.0)

    def test_stream_zone_geometry(self):
        z = TABLE_TOP + 0.12
        edge = KEEPOUT_RADIUS_M + KEEPOUT_FINGER_MARGIN_M
        self.assertTrue(in_stream_zone((NOZZLE_XY[0] - edge + 0.002, 0.0, z)))
        self.assertFalse(in_stream_zone((NOZZLE_XY[0] - edge - 0.002, 0.0, z)))
        self.assertFalse(in_stream_zone((NOZZLE_XY[0], 0.0, TABLE_TOP + 0.02)))                  # below the zone
        self.assertFalse(in_stream_zone((NOZZLE_XY[0], 0.0, TABLE_TOP + 0.30)))                  # above it
        button_press = (0.295, -0.05, TABLE_TOP + 0.04)
        self.assertFalse(in_stream_zone(button_press))                                            # pressing brew is allowed

    def test_hand_in_the_zone_when_no_stream_is_shown_is_fine(self):
        in_zone = (NOZZLE_XY[0] - 0.05, 0.0, TABLE_TOP + 0.12)
        ledger = loaded_ledger()
        run(ledger, 20, button=0.0, good=ring_pos(0.0, 0.004, -0.003), tcps=[READY[0], in_zone])    # before pressing
        self.assertFalse(ledger["zone_fault"])
        ledger = brewed_ledger()
        run(ledger, 20, good=ring_pos(0.0, 0.004, -0.003), tcps=[READY[0], in_zone])                # after the stream has stopped
        self.assertFalse(ledger["zone_fault"])

    def test_hot_wall_touch_is_a_permanent_zero_but_the_handle_is_fine(self):
        mug = ring_pos(0.0, 0.004, -0.003)
        wall_pad = (mug[0] - MUG_RADIUS_M - 0.02, mug[1], mug[2] + 0.05)        # pad zone 5 mm from the wall
        self.assertTrue(touches_hot_wall(wall_pad, mug))
        handle_grip = (mug[0] - 0.105, mug[1], mug[2] + MUG_GRIP_Z)
        self.assertFalse(touches_hot_wall(handle_grip, mug))
        self.assertFalse(touches_hot_wall((mug[0] - 0.105 + 0.012, mug[1], mug[2] + MUG_GRIP_Z), mug))   # 12 mm off toward the wall
        ledger = brewed_ledger()
        run(ledger, 10, good=mug, tcps=[READY[0], handle_grip])
        self.assertFalse(ledger["wall_fault"])
        run(ledger, 10, good=mug, tcps=[READY[0], wall_pad])
        self.assertTrue(ledger["wall_fault"])
        self.assertEqual(score(faults=fault_reasons(ledger)), 0.0)

    def test_the_wall_cools_after_60_seconds(self):
        mug = ring_pos(0.0, 0.004, -0.003)
        wall_pad = (mug[0] - MUG_RADIUS_M - 0.02, mug[1], mug[2] + 0.05)
        ledger = brewed_ledger()
        run(ledger, 1201, good=mug)
        run(ledger, 5, good=mug, tcps=[READY[0], wall_pad])
        self.assertFalse(ledger["wall_fault"])

    def test_an_empty_mug_is_not_hot(self):
        ledger = new_ledger()
        mug = SAUCER_POS
        run(ledger, 5, good=mug, tcps=[READY[0], (mug[0] - MUG_RADIUS_M - 0.02, mug[1], mug[2] + 0.05)])
        self.assertFalse(ledger["wall_fault"])

    def test_machine_moving_is_a_permanent_zero(self):
        ledger = new_ledger()
        run(ledger, 2, good=SAUCER_POS)
        run(ledger, 2, good=SAUCER_POS, machine=(MACHINE[0] + 0.004, MACHINE[1], MACHINE[2]))
        self.assertFalse(ledger["machine_moved"])
        run(ledger, 1, good=SAUCER_POS, machine=(MACHINE[0] + 0.006, MACHINE[1], MACHINE[2]))
        self.assertTrue(ledger["machine_moved"])
        self.assertEqual(score(faults=fault_reasons(ledger)), 0.0)


class Release(unittest.TestCase):
    def clear(self, tcps, shelf_out=0.0, press=0.0, mug=SAUCER_POS):
        return hands_clear(tcps, mug, FLAT, MACHINE, shelf_out, press)

    def test_ready_poses_are_clear(self):
        self.assertTrue(self.clear(READY))

    def test_close_to_the_mug_is_not_clear(self):
        near = (SAUCER_POS[0], SAUCER_POS[1], SAUCER_POS[2] + 0.12)        # just above the rim
        self.assertFalse(self.clear([near, READY[1]]))
        handle = (SAUCER_POS[0] - 0.105, SAUCER_POS[1], SAUCER_POS[2] + 0.05)
        self.assertFalse(self.clear([READY[0], handle]))

    def test_close_to_the_button_or_the_shelf_is_not_clear(self):
        button = (0.28, -0.05, TABLE_TOP + 0.04)
        self.assertFalse(self.clear([READY[0], button]))
        bar = (NOZZLE_XY[0] - 0.145, 0.17, TABLE_TOP + 0.09)
        self.assertFalse(self.clear([bar, READY[1]]))
        self.assertTrue(self.clear([(bar[0] - OUT - 0.1, bar[1], bar[2] + 0.04), READY[1]], shelf_out=OUT))

    def test_still_needs_a_second_without_movement(self):
        ledger = new_ledger()
        run(ledger, 10, good=SAUCER_POS)
        self.assertFalse(still(ledger))
        run(ledger, 30, good=SAUCER_POS)
        self.assertTrue(still(ledger))
        run(ledger, 1, good=(SAUCER_POS[0] + 0.002, SAUCER_POS[1], SAUCER_POS[2]))
        self.assertFalse(still(ledger))
        ledger = new_ledger()
        run(ledger, 30, shelf=-0.02, good=SAUCER_POS)
        run(ledger, 10, shelf=-0.016, good=SAUCER_POS)                                             # shelf still creeping home
        self.assertFalse(still(ledger))


class Display(unittest.TestCase):
    def test_idle_state_shows_only_the_green_lamp(self):
        plan = display_plan(new_ledger(), {}, True)
        shown = {k: sum(r is not None for r in rows) for k, rows in plan.items()}
        self.assertEqual(shown, {"stream": 0, "level": 0, "steam": 0, "spill": 0, "lamp_green": 1, "lamp_amber": 0})

    def test_brewing_shows_stream_level_and_the_amber_lamp(self):
        ledger = loaded_ledger()
        mug = ring_pos(0.0, 0.004, -0.003)
        run(ledger, 80, button=0.008, good=mug)
        plan = display_plan(ledger, mugs_at(mug), True)
        self.assertIsNotNone(plan["stream"][0])
        self.assertIsNotNone(plan["level"][0])
        self.assertIsNone(plan["level"][1])
        self.assertIsNotNone(plan["lamp_amber"][0])
        self.assertIsNone(plan["lamp_green"][0])
        # the stream's lower end is the liquid surface in the mug
        (x, y, z), (_, _, length) = plan["stream"][0]
        self.assertAlmostEqual((x, y), NOZZLE_XY)
        self.assertGreater(z - length / 2, mug[2])

    def test_after_the_brew_steam_shows_for_20_seconds_then_everything_is_parked(self):
        ledger = brewed_ledger()
        mug = ring_pos(0.0, 0.004, -0.003)
        plan = display_plan(ledger, mugs_at(mug), True)
        self.assertEqual(sum(r is not None for r in plan["steam"]), 5)
        self.assertIsNone(plan["stream"][0])
        self.assertIsNotNone(plan["lamp_green"][0])
        run(ledger, 401, good=mug)
        plan = display_plan(ledger, mugs_at(mug), True)
        self.assertEqual(sum(r is not None for r in plan["steam"]), 0)
        self.assertIsNotNone(plan["level"][0])                    # the coffee stays in the mug

    def test_spill_tiles_follow_the_ledger(self):
        ledger = new_ledger()
        run(ledger, BREW_STEPS, button=0.008, good=SAUCER_POS)
        plan = display_plan(ledger, mugs_at(SAUCER_POS), True)
        self.assertEqual(sum(r is not None for r in plan["spill"]), 40)
        self.assertEqual(set(plan.keys()), set(LAYERS))

    def test_markers_are_only_moved_never_toggled(self):
        src = (TASK_DIR / "display.py").read_text(encoding="utf-8")
        code = "\n".join(line for line in src.splitlines() if not line.strip().startswith("#"))
        self.assertNotRegex(code, r"set_visibility\s*\(")
        self.assertNotRegex(code, r"\.visible\s*=")
        self.assertIn("PARK_Z = -10.0", src)
        self.assertEqual(src.count("VisualizationMarkers(cfg)"), 1)          # created in one place, once per layer, at reset


class Consistency(unittest.TestCase):
    def setUp(self):
        self.tj = json.loads((TASK_DIR / "task.json").read_text(encoding="utf-8"))

    def test_precision_rules(self):
        clearance = (2 * RING_INNER_HALF_M - 2 * MUG_RADIUS_M) / 2
        self.assertGreaterEqual(clearance, 0.014)
        self.assertGreaterEqual(SAUCER_MAX_OFFCENTRE_M, 0.008)
        self.assertIn("drip-tray ring", self.tj["fidelity"])
        self.assertIn(f"{clearance * 1000:.1f} mm", self.tj["setup"])

    def test_handle_is_a_lug_with_a_window(self):
        bar, arm_l, arm_r = HANDLE_BOXES
        window = (arm_l[0][1] - arm_l[1][1] / 2) - (arm_r[0][1] + arm_r[1][1] / 2)
        self.assertGreater(window, 0.05)                                      # the 25 mm pad fits with 19 mm to spare each side

    def test_task_json_limits_and_text(self):
        tj = self.tj
        self.assertLessEqual(len(tj["title"]), 120)
        self.assertTrue(20 <= len(tj["instruction"]) <= 540)
        self.assertLessEqual(len(tj["context"]), 900)
        self.assertLessEqual(len(tj["fidelity"]), 500)
        self.assertTrue((TASK_DIR / "task.json").read_bytes().decode("ascii"))
        self.assertIn("possible scores:", tj["scoring"].lower())
        for needle in ("35-3023.00", "TK-DF9CF5"):
            self.assertIn(needle, tj["context"])

    def test_numbers_in_the_text_match_the_geometry(self):
        text = self.tj["setup"] + " " + self.tj["scoring"]
        for needle in ("120 mm", "8 N/m", "100 N/m", "8 s", "85 %", "6 mm", "25 mm", "20 mm", "4 cm", "5 mm", "60 s", "20 s"):
            self.assertIn(needle, text, needle)
        self.assertEqual(BREW_STEPS, 160)
        self.assertEqual(SHELF_NAME, "shelf")
        self.assertEqual(BUTTON_NAME, "button")

    def test_readme_equals_task_json(self):
        readme = (TASK_DIR / "README.md").read_text(encoding="utf-8")
        paragraphs = readme.split("\n\n")
        self.assertEqual(paragraphs[0], "# " + self.tj["title"])
        for key in ("instruction", "context", "setup", "reset_notes", "scoring", "fidelity"):
            self.assertIn(self.tj[key], paragraphs, key)

    def test_run_sh_instruction_and_modes(self):
        run_sh = (TASK_DIR / "run.sh").read_bytes().decode("utf-8")
        self.assertNotIn("\r\n", run_sh)
        self.assertIn(self.tj["instruction"], run_sh)
        for mode in ("settle)", "demo)", "ablation)", "dream)"):
            self.assertIn(mode, run_sh)
        limit = int(re.search(r"([\d,]+) steps", self.tj["run_limit"]).group(1).replace(",", ""))
        for steps in re.findall(r"steps=(\d+)", run_sh):
            self.assertLessEqual(int(steps), limit)


def _import_yam():
    try:
        import yam_arena  # noqa: F401
        return True
    except ImportError:
        pass
    root = TASK_DIR.parents[2]
    cand = root / "robocurve-windows-transfer-2026-11-05" / "project" / "robocurve" / "tmp" / "yam-upstream"
    if (cand / "yam_arena").exists():
        sys.path.insert(0, str(cand))
        try:
            import yam_arena  # noqa: F401
            return True
        except ImportError:
            return False
    return False


HAVE_YAM = _import_yam()


@unittest.skipUnless(HAVE_YAM, "yam_arena is not importable here")
class Demo(unittest.TestCase):
    def setUp(self):
        import demo_plan

        self.demo_plan = demo_plan
        self.plan = demo_plan.make_demo_plan(None)

    def test_both_arms_are_in_step_and_fit_the_run_limit(self):
        left, right = (sum(w.duration for w in self.plan[k]) for k in ("left", "right"))
        self.assertAlmostEqual(left, right, places=3)
        self.assertLessEqual(left * 20, 2400 - 200)

    def test_every_target_is_inside_the_reach_limits(self):
        top = self.demo_plan.TOP
        for arm, wps in self.plan.items():
            for w in wps:
                x, y, z = w.pos
                self.assertLessEqual(x, 0.30, (arm, w.label))
                self.assertLessEqual(z - top, 0.16, (arm, w.label))
                self.assertGreaterEqual(z - top, 0.03, (arm, w.label))
                self.assertLessEqual(abs(y), 0.22, (arm, w.label))

    def test_hands_stay_at_least_120_mm_apart_in_y(self):
        def sample(wps, t):
            acc = 0.0
            prev = (wps[0].pos[0], wps[0].pos[1])
            for w in wps:
                if t < acc + w.duration:
                    u = (t - acc) / w.duration
                    u = u * u * (3 - 2 * u)
                    return prev[0] + (w.pos[0] - prev[0]) * u, prev[1] + (w.pos[1] - prev[1]) * u
                acc += w.duration
                prev = (w.pos[0], w.pos[1])
            return prev

        total = sum(w.duration for w in self.plan["left"])
        worst = 9.0
        for k in range(int(total * 20)):
            lx, ly = sample(self.plan["left"], k / 20)
            rx, ry = sample(self.plan["right"], k / 20)
            need = 0.12 + float(np.clip((0.20 - max(lx, rx)) / 0.08, 0.0, 1.0)) * 0.07
            worst = min(worst, (ly - ry) - need)
        self.assertGreaterEqual(worst, 0.0)

    def test_the_demo_is_reachable_by_both_arms(self):
        """The arms' own IK reaches every demo pose (residual under 1 mm and 1 degree); the right wrist yaw stays inside its range."""
        from yam_arena import demo as yam_demo
        from yam_arena.constants import LEFT_BASE_POS, RIGHT_BASE_POS

        for arm, base in (("left", LEFT_BASE_POS), ("right", RIGHT_BASE_POS)):
            plan = yam_demo.ArmPlan(self.plan[arm], base)
            t = 0.0
            while t < plan.duration:
                plan.action7(t)
                t += 0.05
            self.assertLess(plan.worst_ik_mm, 1.0, arm)
            self.assertLess(plan.worst_ik_deg, 1.0, arm)
        for w in self.plan["right"]:
            self.assertTrue(math.radians(-71) <= w.yaw <= math.radians(165), w.label)

    def test_left_idle_ablation_stays_within_the_right_arms_reach(self):
        """The left-idle ablation runs the right arm's main-plan sequence unchanged, so it is exactly as reachable."""
        from yam_arena import demo as yam_demo
        from yam_arena.constants import RIGHT_BASE_POS

        plan = yam_demo.ArmPlan(self.demo_plan.make_demo_plan("left")["right"], RIGHT_BASE_POS)
        t = 0.0
        while t < plan.duration:
            plan.action7(t)
            t += 0.05
        self.assertLess(plan.worst_ik_mm, 1.0)

    def test_ablation_plans_idle_one_arm(self):
        left_idle = self.demo_plan.make_demo_plan("left")
        self.assertEqual({w.pos for w in left_idle["left"]}, {self.demo_plan.L_READY})
        right_idle = self.demo_plan.make_demo_plan("right")
        self.assertEqual({w.pos for w in right_idle["right"]}, {self.demo_plan.R_READY})

    def test_demo_ends_with_both_grippers_open_at_ready(self):
        from yam_arena.constants import FINGER_OPEN

        for arm, ready in (("left", self.demo_plan.L_READY), ("right", self.demo_plan.R_READY)):
            last = self.plan[arm][-1]
            self.assertEqual(last.finger, FINGER_OPEN)
            self.assertEqual(last.pos, ready)

    def test_demo_never_reads_the_simulator(self):
        src = (TASK_DIR / "demo_plan.py").read_text(encoding="utf-8")
        for pat in ("object_states", ".sliders", "root_pos", "get_state", "env.scene", "PartState"):
            self.assertNotIn(pat, src)


@unittest.skipUnless(HAVE_YAM, "yam_arena is not importable here")
class Parts(unittest.TestCase):
    def test_every_part_has_a_box_and_a_positive_mass(self):
        import task

        parts = [o for o in task.OBJECTS if hasattr(o, "boxes")]
        self.assertEqual({p.name for p in parts}, {"cm_machine", "cm_mug_good", "cm_mug_cracked"})
        for p in parts:
            self.assertGreaterEqual(len(p.boxes), 1, p.name)
            self.assertGreater(p.mass, 0)
            self.assertTrue(p.collision)
        machine = next(p for p in parts if p.name == "cm_machine")
        self.assertEqual([s.name for s in machine.sliders], ["shelf", "button"])
        shelf, button = machine.sliders
        self.assertEqual((shelf.travel, shelf.rate, shelf.damping, shelf.axis), (0.12, 8.0, 5.0, "X"))
        self.assertEqual((button.travel, button.rate, button.axis), (0.008, 100.0, "+X"))
        for p in parts:
            p._check()
            for s in p.sliders:
                s._check(p.name)

    def test_the_loader_accepts_the_task_hooks(self):
        import task

        for hook in ("success", "score", "distance", "demo"):
            self.assertTrue(callable(getattr(task, hook)), hook)


if __name__ == "__main__":
    unittest.main()
