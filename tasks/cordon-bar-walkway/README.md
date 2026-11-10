# Carry a long bar to two posts and rest it in their cradles

Instruction: "Carry the white bar with both hands and rest it on the tops of the two yellow posts."

## What it tests
A two-handed carry of a long object. The 46 cm bar lies along y on a pad; one hand holds it on each side of its middle, both lift it together, carry it forward and lower it across the two posts. One hand alone tips the bar.
The grippers are turned 90 degrees so the fingers close across the 3 cm bar (with the default grip they close along its length and cannot hold it).

## Files
`task.py`, `geometry.py` (every dimension), `logic.py` (scoring maths), `scoring.py` (wrappers and optional trace), `demo_plan.py` (scripted demo; `SETTLE_ONLY` and `ABLATION` select the other modes), `parts.py`, `tracekit.py`, `check_reach.py`, `check_collisions.py`, `run.sh`, `tests/`.

## Run
Needs the Isaac Lab-Arena environment from the program's launchable (`source <ARENA_DIR>/yam.env`).

    ./run.sh settle      200-step hold, expected score 0
    ./run.sh demo        scripted full-score demo
    ./run.sh ablation    scripted run with the right arm idle
    ./run.sh dream       Dream-1, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline: `python -m unittest discover -s tests` (set PYTHONPATH to the yam-arena source), `python check_reach.py`, `python check_collisions.py`.

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Pad: grey 6 x 50 x 1 cm at (18, 0), 25 kg. Bar: white 3.1 x 46 x 3.1 cm, 300 g, on the pad.
- Posts at (28, +20) and (28, -20): 12 x 12 x 2 cm base, 4 x 4 x 10.5 cm column, 5.6 x 4 x 1 cm cradle plate; cradle tops at 11.5 cm; 25 kg.
- Hands at y +12 and -12 (24 cm apart).

## Scoring
Gate (score 0): a post moved more than 5 mm, or the bar fell below the table.
Ladder: 0.25 bar lifted over 4 cm; 0.5 one end on a cradle; 0.75 bar within 30 mm of the target; 1.0 within 15 mm in x, y and height and still for 1 s. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
An idle policy scores 0. Dragging the bar leaves it near the pad. Pushing a post more than 5 mm zeroes the score. The scripted demo knows the layout, so it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-11)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | bar on both cradles within 1 cm of the target, posts moved 0 mm |
| Dream-1 (2,400 steps) | 0.0 | the bar stayed on the pad (nothing moved) |
Earlier runs: 0.0 (the fingers closed along the bar's length and could not hold it), then posts were knocked over by the bar and the arms, then 0.25 and 0.75 (the hands cannot lift the bar higher than about 12 cm at 12 cm from the middle, so the posts were lowered from 40 cm to 11.5 cm; the bar's origin is at its base, so the target height was corrected).

## Honest limits
The cradles are flat plates without a notch, so the bar stays by friction. The posts are 25 kg bodies. The bar is a loose rigid box, not a real cordon.
