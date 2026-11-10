# Press three safety caps into the sockets of a wall plate

Instruction: "Press a red safety cap into each of the three empty sockets of the cream wall plate."

## What it tests
Fitting childproof safety caps into a wall plate while holding the plate still. Three red caps stand in a row at the near side of the table; each has to be carried
to its own socket on the plate and dropped in. The demo uses both arms: one arm braces the plate at its end pad while the other carries a cap, and the arms swap roles
for the middle cap. The sockets are 7 mm wider per side than the caps because the open-loop hand wobbles by about 6 mm.

## Files
`task.py` (task file), `geometry.py` (every dimension), `logic.py` (scoring maths), `scoring.py` (scorer wrappers and the optional trace),
`demo_plan.py` (scripted demo, every tunable is a `DEMO_*` environment variable; `SETTLE_ONLY` and `ABLATION` select the other modes), `parts.py` (compound parts for yam_arena),
`tracekit.py` (debug trace), `check_reach.py`, `check_collisions.py`, `run.sh`, `tests/`.

## Run
Needs the Isaac Lab-Arena environment from the program's launchable (`source <ARENA_DIR>/yam.env`).

    ./run.sh settle      200-step hold, expected score 0
    ./run.sh demo        scripted full-score demo
    ./run.sh ablation    scripted run with the left arm idle
    ./run.sh dream       Dream-1, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline checks (no simulator):

    python -m unittest discover -s tests      (set PYTHONPATH to the yam-arena source)
    python check_reach.py ; python check_collisions.py

The demo plan is about 880 control steps (44 s at 20 Hz); a run with the simulator takes about 7 minutes on an L40S. `TASK_TRACE=<file>` writes one JSON line per scorer call
(with every cap position) and `<file>.hands.jsonl` with both grippers and the plate.

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Wall plate: cream 12 x 26 x 2 cm base at (30, 0), 25 kg; raised 1.8 cm walls form three square sockets 5.4 x 5.4 cm at y +7, 0, -7 (7 cm pitch). Darker end pads (hold zones) at y +12.5 and -12.5.
- Caps: red cylinders 4 cm diameter x 3 cm, 20 g, at (15, +12), (15, 0), (15, -12).
- Left arm works at y > 0, right arm at y < 0.

## Scoring
Gates (score 0): plate more than 6 cm from its start, or anything off the table.
Ladder: 0.25 one cap seated; 0.5 two; 0.75 three seated but the plate moved 15 mm or more; 1.0 three seated, plate moved under 15 mm, everything still for 1 s.
A cap is seated when its centre is within 20 mm of a socket centre and its top is 4 to 20 mm above the plate face. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
An idle policy scores 0. Dropping a cap on top of a wall instead of in the socket leaves its top about 3 cm above the plate face, which is not seated. Pushing the plate more than 15 mm caps the score at 0.75.
The scripted demo knows the layout, so it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-10)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | all three caps seated within 1 mm of the socket centres, plate moved 0 mm |
| Dream-1 (2,400 steps) | 0.0 | no cap and not the plate moved (all four positions unchanged) |
Earlier runs of this task scored 0.5: the middle cap was dragged out of the gripper and ended on top of a wall. Two changes fixed it: the sockets are 7 cm apart instead of 6 cm
(the 85 mm gripper body touched the caps already seated next door), and the cap is released 2 cm above the socket so the finger pads stay above the walls.

## Honest limits
The plate is a 25 kg body, so it never slides: holding it is demonstrated, not enforced. The caps are dropped into open wells and stay by gravity (no press fit, no chamfer).
