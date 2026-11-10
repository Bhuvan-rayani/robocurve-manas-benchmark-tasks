# Pick the brown-black-red resistor and seat it in a spring-covered socket

Instruction: "Pick the resistor with brown, black and red bands from the tray and drop it into the socket while the other hand holds the sliding cover aside."

## What it tests
Reading a colour code and installing a component into a protected socket. Six resistors differ only in their three bands; the target is brown-black-red (1 kOhm). A spring-loaded cover closes the socket, so one arm holds the cover open
while the other carries the resistor to the hole and drops it in. Releasing the cover too early shuts it on the resistor.

## Files
`task.py`, `geometry.py` (every dimension and the band colours), `logic.py` (scoring maths), `scoring.py` (scorer wrappers and optional trace with the target's position and the cover joint),
`demo_plan.py` (scripted demo; `SETTLE_ONLY` and `ABLATION` select the other modes), `parts.py`, `tracekit.py`, `check_reach.py`, `check_collisions.py`, `run.sh`, `tests/`.

## Run
Needs the Isaac Lab-Arena environment from the program's launchable (`source <ARENA_DIR>/yam.env`).

    ./run.sh settle      200-step hold, expected score 0
    ./run.sh demo        scripted full-score demo
    ./run.sh ablation    scripted run with the right arm idle
    ./run.sh dream       Dream-1, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline: `python -m unittest discover -s tests` (set PYTHONPATH to the yam-arena source), `python check_reach.py`, `python check_collisions.py`.

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Tray: 20 x 30 x 3 cm at (24, +18); resistors 3 cm dia x 7 cm at x 29 and 19, y +28, +18, +8. Target brown-black-red at (29, +8).
- Socket board: 24 x 16 cm at (26, -6), 25 kg; collar 8 cm tall around a 4.6 cm square hole.
- Cover: grey bar over the hole, slides 4 cm along +x, spring 10 N/m. The right arm pushes it at y -22; the left arm carries the resistor; the working points are about 16 cm apart.

## Scoring
Gates (score 0): board moved more than 5 mm, or a wrong resistor in the socket.
Ladder: 0.25 any resistor lifted over 2 cm; 0.5 the target lifted; 0.75 the target over the socket within 12 mm; 1.0 the target seated at least 6 cm deep, cover closed within 3 mm, still for 1 s. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
An idle policy scores 0. Picking the wrong resistor never gets past 0.25. Dropping the resistor on the closed cover never seats it. The scripted demo knows the layout, so it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-10)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | target seated on the table inside the hole, cover closed (1 mm), board moved 0 mm |
| Dream-1 (2,400 steps) | 0.0 | no resistor was lifted and the cover stayed closed |
Earlier runs: 0.5 (the left arm could not reach the socket while the hanging resistor hit the cover's edge), then 0.75 (the resistor rested on the collar rim because the hole was only 1 mm wider than it), then 0.0 (the resistor stopped under the cover, which could not close).
Fixes: the hole is 4.6 cm, the cover sits above the collar, the socket board moved to x 26, and the cover spring is 10 N/m.

## Honest limits
Resistors have no leads and the socket has no contacts; gravity keeps the resistor in the well. The board is a 25 kg body so it never moves.
