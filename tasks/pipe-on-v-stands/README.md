# Carry a long pipe with both hands and lay it in two V stands

Instruction: "Carry the green pipe with both hands and lay it in both wooden V stands."

## What it tests
Carrying a long, heavy-looking object with both hands. The 60 cm pipe lies on a pad; one hand holds it near each end, both lift it together, carry it forward and lower it into two V stands 42 cm apart. The grippers are turned 90 degrees so the fingers close across the 6 cm pipe.

## Files
`task.py`, `geometry.py` (every dimension), `logic.py` (scoring maths), `scoring.py`, `demo_plan.py` (`SETTLE_ONLY` and `ABLATION` select the other modes), `parts.py`, `tracekit.py`, `check_reach.py`, `check_collisions.py`, `run.sh`, `tests/`.

## Run
Needs the Isaac Lab-Arena environment (`source <ARENA_DIR>/yam.env`).

    ./run.sh settle      200-step hold, expected score 0
    ./run.sh demo        scripted full-score demo
    ./run.sh ablation    scripted run with the right arm idle
    ./run.sh dream       Dream-1, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline: `python -m unittest discover -s tests` (PYTHONPATH = yam-arena source), `python check_reach.py`, `python check_collisions.py`. `TASK_TRACE=<file>` writes one JSON line per scorer call and `<file>.hands.jsonl`.

## Layout (cm from the midpoint between the arm bases; x forward, y left; table top z 74.75)
- Pad 8 x 50 x 2 at (18, 0), 25 kg. Pipe 6 cm dia x 60 cm, 1 kg, on the pad.
- V stands at (34, +21) and (34, -21), 10 x 6 x 12 cm, vertex 8 cm above the table, 25 kg.
- Hands at y +22 and -22.

## Scoring
Gate (score 0): a stand moved more than 5 mm, or the pipe fell off the table.
Ladder: 0.25 lifted over 5 cm; 0.5 over the stands; 0.75 in at least one notch; 1.0 in both notches, centred, axis within 5 degrees, still for 1 s. Possible scores: 0, 0.25, 0.5, 0.75, 1.0.

## Why shortcuts fail
An idle policy scores 0. Pushing the pipe along the table never lifts it. Moving a stand more than 5 mm zeroes the score. The scripted demo knows the layout, so it is only a feasibility proof.

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-11)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | pipe lifted 9 cm, carried and seated in both stands, stands moved 0 mm |
| Dream-1 (2,400 steps) | 0.0 | the pipe stayed on the pad (nothing moved) |
Earlier runs: 0.0 (with the default grip the fingers closed along the pipe and could not hold it); 0.5 and 0.75 (the pipe overshot the notches by 21 mm; the carry target was moved 14 mm back).

## Honest limits
The V notches are built from boxes, not a true V. The stands are 25 kg bodies. The pipe is a rigid cylinder.
