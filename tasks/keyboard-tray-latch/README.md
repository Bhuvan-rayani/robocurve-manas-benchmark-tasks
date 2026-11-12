# Slide keyboard tray under desk until purple latch engages

Instruction: "Stow the grey keyboard tray under the desk and secure it."

## What it tests
Office ergonomics technicians and facilities installers assemble and adjust under-desk articulated keyboard mechanisms and slides (O*NET 49-9071.00).

## Setup & Starting Configuration
Dual YAM embodiment at ready on station tabletop (z=747.5 mm). A beige desk fixture (200x360x60 mm: a 20 mm top plate and two 20 mm wide, 40 mm high side rails, 25 kg, friction 1.2, fixed in place) stands at x=30 cm, y=0. A grey keyboard tray (200x300x20 mm) with a 40x70x20 mm side lug and a 40x40x40 mm pull block on its -y edge rests under it with its centre at x=16 cm, y=0 and slides 280 mm along +x to a stop; it stays where it is left (spring 0.001 N/m, damping 20 N s/m). A purple latch block (20x20x20 mm) sits at x=44 cm, y=0, 30 mm above the tabletop on an 8 mm vertical slider (spring 100 N/m, damping 10 N s/m) that the tray presses down as it arrives. Real build: the desk is 18 mm plywood on a steel frame bolted to the table; the tray is a 3D-printed PLA plate on two ball-bearing drawer slides; the latch is a printed PLA block on a compression spring. Material as modelled: every object is a rigid body with only the size, mass and friction stated here; nothing deforms, and nothing snaps or latches except through contact and the listed slider springs.

## Reset
Pull the tray back out to its starting position (centre at x=16 cm), let the latch block spring back up, and allow 0.5 s to settle.

## Scoring
Gate: 0 if the desk moves more than 5 mm. Ladder by how far the tray has slid in: 0.25 at 5 cm or more, 0.50 at 15 cm or more, 0.75 at 26 cm or more, 1.00 at 27.8 cm or more (the tray stops at 28 cm) with the latch counted as engaged and everything still for 1.0 s. The latch counts as engaged when its slider is pressed down at least 6 mm or the tray has slid at least 27.8 cm. Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0.

## Fidelity
The tray and the latch are rigid prismatic sliders: the tray stays where it is left (almost no spring, damped) and the latch is a spring-loaded block. Nothing holds the tray in place once it is at the stop, so the latch is detected by position, not by a mechanical catch. Contact and friction come from the simulator; the scorer reads the slider travels and the desk position.

## Files
`task.py` (task file), `geometry.py` (geometric constants, dimensions, masses, colors), `logic.py` (scoring ladder evaluation), `scoring.py` (scorer wrappers and TASK_TRACE logger)

## Run
Needs the Isaac Lab-Arena environment from the program's launchable (`source /data/IsaacLab-Arena/yam.env`).

    ./run.sh settle      200-step hold, scores 0
    ./run.sh demo        scripted full-score demo (1,500 steps)
    ./run.sh ablation    scripted run with the left arm idle (scores below 1.0)
    ./run.sh dream       Dream-1 policy, 2,400 steps

All runs use `-E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 --scorer task_score`. Offline verification checks (no simulator):

    python -m unittest discover -s tests
    python check_reach.py
    python check_collisions.py

Runtime per trial: the demo plan runs for 532 steps (26.6 s at 20 Hz); a complete Isaac Lab-Arena trial takes approximately 4-5 minutes wall time on an L40S GPU. `TASK_TRACE=<file>` writes JSON lines per scorer call.

