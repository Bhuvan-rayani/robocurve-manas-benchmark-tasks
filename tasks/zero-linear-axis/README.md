# Zero a linear axis: push the carriage to its datum and pin it

Instruction: "Slide the carriage until its white mark is level with the white mark on the base, then drop the yellow pin into the hole
in the carriage's lug while holding the base still."

## What it tests
Setting the home datum of a linear axis. The carriage is pushed 40 mm along +y, which reacts through a loose, very low friction base,
so a real rig needs one arm to hold the base while the other pushes (in this simulation the base did not slide when unheld, see the ablation). After the marks line up, the yellow pin has to be carried to the lug and dropped
through its hole, which locks the carriage at the datum. The task needs both arms (hold the base, push the carriage) and a pick and place.

## Files
`task.py` (task file), `geometry.py` (every dimension), `logic.py` (scoring maths), `scoring.py` (scorer wrappers and the optional trace),
`demo_plan.py` (scripted demo, every tunable is a `DEMO_*` environment variable), `parts.py` (compound parts and sliders for yam_arena),
`tracekit.py` (debug trace), `check_reach.py`, `check_collisions.py`, `run.sh`, `tests/`.

## Run
Needs the Isaac Lab-Arena environment from the program's launchable (`source <ARENA_DIR>/yam.env`).

    ./run.sh settle      200-step hold, expected score 0
    ./run.sh demo        scripted full-score demo
    ./run.sh ablation    scripted run without holding the base
    ./run.sh dream       Dream-1, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline checks (no simulator):

    python -m unittest discover -s tests      (set PYTHONPATH to the yam-arena source)
    python check_reach.py ; python check_collisions.py

Runtime per trial: the demo plan is about 1,020 control steps (about 51 s at 20 Hz); a run with the simulator takes about 7 minutes wall time on an L40S.
`TASK_TRACE=<file>` writes one JSON line per scorer call (and `<file>.hands.jsonl` with both grippers and every part).

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Axis base: grey 8 x 32 x 4 cm block, 600 g, centre (26, 0), friction 0.02 (loose). Hold patch at y +13, white strip at (23, -6).
- Carriage: silver body 8 x 6 x 3 cm, centre y -10, +y slider, travel 12 cm, no return spring, damping 150 N s/m. Lug 5.4 x 5.4 x 2.5 cm with a 3 x 3 cm hole,
  underside 4 cm above the table; white strip at (23, -10).
- Pin: yellow cylinder 1.6 cm dia x 6 cm, 30 g, at (20, +20).
- Left arm works at y > 0 (holds the base at y +13, carries the pin), right arm at y < 0 (pushes the carriage); the two working points are at least 28 cm apart.

## Scoring
Gates (score 0): base more than 5 cm from its start, tilted more than 20 degrees, or off the table.
Ladder: 0.25 carriage pushed at least 2 cm toward the datum; 0.5 strip offset at most 6 mm; 0.75 offset at most 3 mm;
1.0 offset at most 3 mm, pin standing in the lug hole (axis within 9 mm of the hole centre, lower end at least 5 mm below the lug underside, tilt at most 15 degrees),
base moved under 8 mm, everything still for 1 s. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
Holding the base is demonstrated in the demo but is not physically enforced: in the simulated ablation the unheld base did not move (0.0 mm). Dropping the pin without pushing the carriage
leaves the strips 40 mm apart (offset above 6 mm: no more than 0.25). Putting the pin through the hole at the wrong carriage position gives the offset-based score only.
An idle policy scores 0. The scripted demo knows the layout, which is why it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-10)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | marks aligned within 0.2 mm, base moved 0 mm, pin standing in the hole |
| ablation (left arm idle, no pin placed) | 0.75 | carriage pushed to 40.6 mm and the marks aligned; no pin was placed (the left arm carries the pin); the unheld base moved 0.0 mm |
| Dream-1 (2,400 steps) | 0.0 | no part moved: carriage, pin and base all stayed at their start positions |
Earlier tuning runs of this task: 0.0 (hand reached too short), 0.75 (carriage at the datum), 0.25 (pin clipped the hole, then the finger pads rested on the lug).

## Changes made after the first simulator runs
- The first design used a spring-less sliding pin: it fell to its lower limit under gravity in 30 steps, so "pin seated" was true at the start. The pin is now a loose cylinder.
- The carriage return spring was removed (the carriage stays where it is pushed); base friction was lowered to 0.02 and carriage damping raised to 150 N s/m to try to make an unheld base slide (it still did not move).
- Measured contact: the finger touches the carriage when the tool point is about 6 mm short of the carriage face; the push is planned from that.
- The lug hole grew from 18 to 30 mm (7 mm per side) because the open-loop hand wobbles by about 6 mm; the pin is released 20 mm above the lug so the finger pads never touch it.


