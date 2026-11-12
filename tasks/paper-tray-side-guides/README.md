# Load paper tray, adjust side guides, and close tray

## Task Overview

Load the paper block into the feed tray with side guides snug and tray pushed shut.

Office technicians and clerical workers load paper reams into printer feed trays, adjust side guides to prevent skew and paper jams, and close the tray before initiating print jobs (O*NET 43-9071.00, 49-2011.00).

## Setup & Starting Configuration

Dual YAM embodiment at ready on station tabletop (z=747.5 mm). A grey PLA printer frame (340x400x120 mm, 25.0 kg, friction 1.2) is taped at (28, 0) cm from the arm baseline with a front tray slot. Inside the slot rests a sky-blue PLA feed tray (240x320x30 mm, 350 g, friction 0.2) starting open at (12, 0, 1.0) cm with 120 mm travel along +x to closed stop at x=24 cm. Mounted inside the tray are two grey PLA side guides (200x10x30 mm, 40 g each, 25 mm travel along y) starting at y=+13.5 cm and y=-13.5 cm (26 cm inner face spacing). A white PLA paper block (150x210x30 mm, 250 g, friction 0.2) rests on a grey staging pad (170x230x5 mm, 120 g) at (14, 32) cm outside the printer. Material as modelled: every object is a rigid body with only the size, mass and friction stated here; nothing deforms, and nothing snaps or latches except through contact and the listed slider springs.

## Reset

Open feed tray to x=12 cm, pull both side guides apart to starting spacing of 26 cm (y=+13.5 cm and y=-13.5 cm), place paper block on staging pad outline at (14, 32) cm.

## Scoring

Gates: 0 if the printer frame moves > 5 mm or paper block falls off table. Ladder: 0.25 for paper block placed inside the tray outline; 0.50 for block resting flat with at least one side guide touching (within 1.5 mm of paper side); 0.75 for both side guides touching (within 1.5 mm) and block centred within 3 mm of tray midline; 1.00 for both guides touching, block centred, and feed tray pushed shut (within 3 mm of its stop at x=24 cm), held still for 1.0 s. Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0.

## Fidelity

Compound feed tray body with two independent detented prismatic sliders (25 mm travel along y) and loose feed tray slider along x inside fixed printer frame channel implemented via parts.py articulation. Paper block is a rigid solid body. Real-world printers link side guides with a rack-and-pinion gear; here they slide independently. Scorer reads object 3D poses and slider joint coordinates.

## Execution & Evaluation

Run the commands via `run.sh` in the Isaac Lab-Arena environment:

```bash
# Settle verification (8 s hold at ready)
bash run.sh settle

# Coordinated bimanual demo (scores 1.00 on Isaac)
bash run.sh demo

# Single-arm ablation (right arm idle, scores below 1.00)
bash run.sh ablation

# Evaluation with Dream policy
bash run.sh dream
```

Runtime per trial: ~45.5 seconds (911 control steps at 20 Hz, within 2,400 step limit). Object jitter is disabled (`object_jitter=0`) for deterministic evaluation.
