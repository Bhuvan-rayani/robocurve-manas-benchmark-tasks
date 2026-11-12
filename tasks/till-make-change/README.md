# Make change from till into customer tray

## Task Overview

The sale is 7 and the customer gave 10: put the correct change in the navy tray.

Cashiers and checkout clerks open the till drawer and count out exact change for customer transactions (O*NET 43-3071.00).

## Setup & Starting Configuration

Dual YAM embodiment at ready on station tabletop (z=747.5 mm). A gold till body (200x240x80 mm, 25 kg, friction 1.2, fixed in place) sits at x=30 cm, y=+14 cm. Its drawer (195x220x50 mm, 250 g) slides 100 mm toward the robot along -x; it stays where it is left (spring 0.001 N/m, damping 50 N s/m) and has a pull knob on its front (24 mm wide, 35 mm proud, 32 mm tall). Tokens stand on the table on the right side as two stacks of four gold discs: 1-unit discs (40 mm dia x 14 mm, 16 g) at x=17 cm, y=-10 cm, and 2-unit discs (50 mm dia x 14 mm, 25 g) at x=17 cm, y=-22 cm. A navy customer tray (open box 80x120x20 mm with a 4 mm floor and 6 mm walls 16 mm high, 80 g, friction 1.0) rests at x=28 cm, y=-16 cm. Real build: the till body is 4 mm aluminium sheet bolted to the table; the drawer is a 3D-printed PLA box (3 mm walls) on ball-bearing slides; the tokens are solid PLA discs; the tray is 3D-printed PLA. Material as modelled: every object is a rigid body with only the size, mass and friction stated here; nothing deforms, and nothing snaps or latches except through contact and the listed slider.

## Reset

Restack the four 1-unit discs and the four 2-unit discs at their stack positions, push the drawer fully closed, and empty the navy tray. Allow 0.5 s to settle.

## Scoring

Gates: 0 if the till body moves more than 5 mm, if any token falls below the tabletop by more than 2 cm, or if any token ends loose (more than 4.5 cm from its own stack centre and not inside the tray). Change only counts once the drawer is open at least 6 cm, so a drawer left open less than 6 cm scores 0. Ladder: 0.25 drawer open at least 6 cm; 0.50 any token inside the tray; 0.75 tray total of 2 or 4 units (1-unit disc = 1, 2-unit disc = 2); 1.00 tray total of exactly 3 units, no loose tokens, drawer still open at least 6 cm, and everything still for 1.0 s. Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0.

## Fidelity

The drawer is a rigid prismatic slider with viscous damping and almost no spring, so it stays where it is left. Tokens, tray and till are rigid bodies; contact and friction come from the simulator. The scorer reads body positions and the drawer slider travel at each step; it does not model a cash register, coin counting or a lock.

## Execution & Evaluation

Run the commands via `run.sh`:

```bash
# Settle verification (8 s hold at ready)
bash run.sh settle

# Coordinated bimanual demo (predicted score: 1.00)
bash run.sh demo

# Unheld drawer ablation (drawer remains closed, predicted score: 0.00)
bash run.sh ablation

# Evaluation with Dream policy
bash run.sh dream
```

Runtime per trial: ~59 seconds (1,181 control steps at 20 Hz, within 2,400 step limit). Object jitter is disabled (`object_jitter=0`) for deterministic evaluation.
