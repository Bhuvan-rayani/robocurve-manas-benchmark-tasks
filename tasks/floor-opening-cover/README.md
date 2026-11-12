# Cover floor opening with plate and wedge pins

## Task Overview

Make the open floor hatch safe: cover it with the red plate and secure it with the yellow wedge pins.

Construction laborers and safety technicians inspect and securely cover hazardous floor holes and roof openings with fastened protective plates to prevent worker falls (O*NET 47-2061.00, 47-4011.00).

## Setup & Starting Configuration

Dual YAM embodiment at ready on station tabletop (z=747.5 mm). A grey PLA floor board (340x440x50 mm, fixed 25 kg) is centered at (30, 0) cm with a central 160x160 mm opening and two 26x26 mm locking slots (15 mm deep) at x=24 cm, y=+13 cm and y=-13 cm. A red PLA cover plate (220x220x10 mm, 400 g) with a 40x80x20 mm grip handle at its centre rests on a grey stand (180x180x30 mm, fixed) at (16, 33) cm. Two yellow PLA wedge pins (12x12x40 mm, 15 g each) stand on fixed racks: pin A on a left rack (80x80x25 mm) at (30, 33) cm, pin B on a right rack (80x160x25 mm) at (16, -33) cm. Real build: the floor board is a 50 mm thick PLA print (or laminated plywood) bolted to the table; the cover plate is 10 mm PLA with a printed grip handle; the wedge pins are printed PLA; the stands and racks are fixed PLA blocks. Material as modelled: every object is a rigid body with only the size, mass and friction stated here; nothing deforms, and nothing snaps or latches except through contact and the listed slider springs.

## Reset

Return red cover plate to stand at (16, 33) cm, return yellow wedge pin A to left rack at (30, 33) cm and pin B to right rack at (16, -33) cm, ensure floor opening is unobstructed.

## Scoring

Gates: 0 if the floor board moves > 5 mm, if any object falls off table, or if the cover plate or either pin drops into the opening pit below the board top. Ladder: 0.25 for cover plate lifted > 2 cm from stand; 0.50 for plate placed over opening with overhang >= 20 mm on all four sides; 0.75 for plate over opening and one wedge pin seated >= 10 mm in a slot; 1.00 for plate over opening, both wedge pins seated >= 10 mm in their respective slots, plate flat within 3 degrees, held still for 1.0 s. Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0.

## Fidelity

Floor board is a multi-box compound static fixture built with parts.py. The cover plate (with handle) is a rigid compound body and the wedge pins are loose rigid bodies, 1.2 static friction. Scorer evaluates object poses, overhang boundaries and vertical slot seating depth (pin within 16 mm of the slot centre in x and y).

## Execution & Evaluation

Run the commands via `run.sh`:

```bash
# Settle verification (8 s hold at ready)
bash run.sh settle

# Coordinated bimanual demo (scores 1.00 on Isaac)
bash run.sh demo

# Unheld/unbraced ablation (scores 0.00 on Isaac)
bash run.sh ablation

# Evaluation with Dream policy
bash run.sh dream
```

Runtime per trial: about 1,300 simulated steps for the scripted demo at 20 Hz (run limit 2,400). Object jitter is disabled (`object_jitter=0`).
