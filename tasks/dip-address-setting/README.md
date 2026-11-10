# Set four address switches to a dot pattern and press commit

Instruction: "Set the four blue switches on the violet module to match the dark and light squares on the white card (dark = pushed to the far end,
light = pushed to the near end), then press the lime button."

## What it tests
Commissioning a small module: read a pattern from a card, set four sliding switches to it, then press a commit button. The card shows four squares
(dark, light, light, dark); the switches start in the opposite state (near, far, far, near), so all four have to be moved. Pressing the button before
the pattern is right scores 0. The demo uses both arms: one arm braces the module at its end while the other pushes switches, then they swap, and the
last step presses the button.

## Files
`task.py` (task file), `geometry.py` (every dimension), `logic.py` (scoring maths), `scoring.py` (scorer wrappers and the optional trace),
`demo_plan.py` (scripted demo, `SETTLE_ONLY` and `ABLATION` select the other modes), `parts.py` (compound parts and sliders for yam_arena),
`tracekit.py` (debug trace), `check_reach.py`, `check_collisions.py`, `run.sh`, `tests/`.

## Run
Needs the Isaac Lab-Arena environment from the program's launchable (`source <ARENA_DIR>/yam.env`).

    ./run.sh settle      200-step hold, expected score 0
    ./run.sh demo        scripted full-score demo
    ./run.sh ablation    scripted run with the right arm only
    ./run.sh dream       Dream-1, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline checks (no simulator):

    python -m unittest discover -s tests      (set PYTHONPATH to the yam-arena source)
    python check_reach.py ; python check_collisions.py

The demo plan is about 900 control steps (45 s at 20 Hz). `TASK_TRACE=<file>` writes one JSON line per scorer call and `<file>.hands.jsonl` with both grippers and every part.

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Module: violet 14 x 26 x 3 cm block, centre (30, 0), 25 kg (stands in for a bolted module).
- Switches: four blue knobs 1.2 x 1.6 x 1.4 cm, 4 g, at x 33.5 and y +7.5, +2.5, -2.5, -7.5; 1.5 cm of travel along x, no return spring (damping 20 N s/m).
  Start: switches 1 and 4 at the near end, 2 and 3 at the far end.
- Button: lime, 3.6 cm diameter, 1.2 cm tall, 8 g, at (25.3, 0); 0.8 cm of travel, return spring 100 N/m.
- Card: white 6 x 22 x 0.24 cm at (22, +26) with 2.4 cm squares at the switch pitch: dark, light, light, dark (target far, near, near, far).
- Left arm works at y > 0, right arm at y < 0; the two working points are at least 15 cm apart.

## Scoring
Gates (score 0): module more than 5 cm from its start, button pressed in (6.4 mm or more) with fewer than four switches correct, or module more than 15 mm from its start.
Ladder: 0.25 one switch correct; 0.5 two or three correct; 0.75 all four correct; 1.0 all four correct, button pressed in at least 6.4 mm, everything still for 1 s.
A switch counts when it has moved at least 10 mm. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
Pressing the button first scores 0 (gate). An idle policy scores 0 and so does a run that moves the module. Moving only the two switches that happen to need pushing the same way
gives at most 0.5. The scripted demo knows the layout, so it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-10)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | all four switches moved the full 15 mm, button pressed in 8 mm, module moved 0 mm |
| Dream-1 (2,400 steps) | 0.0 | no switch or button moved and the module stayed at its start position |
Offline screening before the GPU runs found two defects that are fixed in this version: the scorer read the two switches that move toward the arms with the wrong sign, and the settle and
ablation modes were not wired to the demo plan.

## Honest limits
The module is a 25 kg body, so it never slides: the bracing arm is demonstrated, not enforced (the score only requires the module to end within 15 mm of its start).
The switches have no detents. The squares on the card stand in for printed dots.
