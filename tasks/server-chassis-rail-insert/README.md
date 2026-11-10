# Slide a server chassis into rack rails until its ears are flush

Instruction: "Slide the silver server chassis into the rack rails until its front ears are flush with the teal posts."

## What it tests
Pushing a chassis squarely into a rack. The chassis is wide and sits on a plate; if the two hands push unevenly it yaws and jams at the rail entrance, so the task needs both arms pushing at once
at the two sides of the front face. The hands must also stay at least 19 cm apart near the arm bases, otherwise the arms collide.

## Files
`task.py` (task file), `geometry.py` (every dimension), `logic.py` (scoring maths), `scoring.py` (scorer wrappers and the optional trace),
`demo_plan.py` (scripted demo; `SETTLE_ONLY` and `ABLATION` select the other modes), `parts.py` (compound parts for yam_arena),
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

`TASK_TRACE=<file>` writes one JSON line per scorer call and `<file>.hands.jsonl` with both grippers and the chassis.

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Staging plate: grey 27 x 12 x 6 cm, fixed, centre (28.5, 0).
- Chassis: silver 24 x 23 x 4.4 cm, 700 g, friction 0.3, centre (29, 0) on the plate; ear tabs 0.4 x 5 x 4.4 cm on the front face at y +16 and -16.
- Rails: 24 cm long (x 42 to 66), walls at y +13.3 and -13.3, ledges at +12.3 and -12.3 (top 6 cm above the table); 1.2 cm clearance per side.
- Posts: teal 3 x 3 x 20 cm, fixed, x 40.5, y +19.5 and -19.5; front faces at x 39.0.
- Both hands push the front face of the chassis at y +9.5 and -9.5.

## Scoring
Gates (score 0): a post moved more than 5 mm, chassis tilted more than 15 degrees, fell below the table, or ended more than 5 cm to the side.
Ladder: 0.25 lifted over 2 cm or advanced 2 cm; 0.5 rear end 6 cm into the rails; 0.75 15 cm into the rails; 1.0 ears within 3 mm of the post faces, tilt under 5 degrees, still for 1 s. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
An idle policy scores 0. Pushing with one hand drives the chassis off-centre and into a wall (partial credit only). The scripted demo knows the layout, so it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-10)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | chassis pushed 21.6 cm into the rails, ears flush with the posts, no tilt |
| Dream-1 (2,400 steps) | 0.0 | the chassis did not move (0.0 mm) |
Earlier versions of this task failed in the simulator: with the hands 13 cm apart the two arms collided near their bases and never reached the chassis; with the hands 14 cm apart the palms hit the posts 2 cm short of the goal.
The rack was then moved 12 cm further out, the chassis widened to 23 cm so the hands can push 19 cm apart, the posts moved out to y +-19.5 cm, and the chassis friction lowered from 1.2 to 0.3.

## Honest limits
Friction 0.3 is lower than a real chassis on a bare ledge would need to be pushed by hand; the rails are wider than a real rack's (1.2 cm per side). The ears stop on the posts, so the final flush position is partly enforced by contact.
