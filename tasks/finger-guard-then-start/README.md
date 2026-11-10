# Close the machine's finger guard, then press the start button

Instruction: "Slide the yellow guard all the way across the grey machine, then press the green start button."

## What it tests
An interlocked machine guard. The yellow guard has a return spring, so it springs back open as soon as it is released; a second hand has to press the start button while the first holds the guard closed.
Pressing the button with the guard open scores at most 0.25. Both arms are needed: one holds the guard closed, the other presses the button.

## Files
`task.py` (task file), `geometry.py` (dimensions), `logic.py` (scoring maths), `scoring.py` (scorer wrappers and optional trace), `demo_plan.py` (scripted demo; `SETTLE_ONLY` and `ABLATION` select the other modes),
`parts.py` (compound parts for yam_arena), `tracekit.py` (debug trace), `check_reach.py`, `check_collisions.py`, `run.sh`, `tests/`.

## Run
Needs the Isaac Lab-Arena environment from the program's launchable (`source <ARENA_DIR>/yam.env`).

    ./run.sh settle      200-step hold, expected score 0
    ./run.sh demo        scripted full-score demo
    ./run.sh ablation    scripted run with the left arm idle
    ./run.sh dream       Dream-1, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline checks: `python -m unittest discover -s tests` (set PYTHONPATH to the yam-arena source), `python check_reach.py`, `python check_collisions.py`.
`TASK_TRACE=<file>` writes one JSON line per scorer call (guard travel, button travel) and `<file>.hands.jsonl` with both grippers and the machine.

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Machine: grey 20 x 32 x 8 cm, 25 kg, centre (30, 0).
- Guard: yellow 12 x 10 x 3 cm at y +12, rests at x 23, slides 14 cm along +x, spring 10 N/m, damping 20 N s/m.
- Button: green 4 x 4 x 1.5 cm at (30, -12), 0.8 cm travel, spring 100 N/m.
- Left arm works at y > 0 (guard), right arm at y < 0 (button): the working points are 24 cm apart.

## Scoring
Gate (score 0): the machine moved more than 5 mm. Pressing the button (6.4 mm or more) with the guard open less than 12 cm scores at most 0.25.
Ladder: 0.25 guard slid 6 cm or more; 0.5 guard slid 12 cm or more; 0.75 button also pressed but not yet still; 1.0 guard 12 cm or more, button 6.4 mm or more, still for 1 s. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
An idle policy scores 0. Pressing the button first scores at most 0.25. Releasing the guard lets it spring open, so the button must be pressed while it is held. The scripted demo knows the layout, so it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-10)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | guard slid 14 cm, button pressed the full 8 mm, machine moved 0 mm |
| Dream-1 (2,400 steps) | 0.0 | the guard did not move and the button was not pressed |
The first simulator run scored 0.25: with an 80 N/m spring the arm could only hold the guard 9 cm across (the 12 cm needed 9.6 N). The spring was reduced to 10 N/m.

## Honest limits
The interlock exists only in the scorer. The machine is a fixed 25 kg body. There is no latch: the guard springs open when released.
