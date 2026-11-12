# Fit cyan stop block into window track for 100 mm sash restriction

## Task Overview

Fit the cyan stop block so the window sash cannot open more than 100 mm, and open the sash as far as it will go.

The window frame (250 x 380 x 30 mm; modelled as a 25 kg fixed body that stands in for a bolted frame) has a 340 mm track channel along Y and three 30 x 30 mm floor pockets at Y = 28, 78 and 128 mm. The white sash pane (220 x 140 x 20 mm, 150 g, 120 mm travel along +Y) starts closed. It stays wherever it is pushed (spring 0.001 N/m, damping 50 N s/m) and has a 45 mm proud rear push tab. The cyan stop block (30 x 30 x 30 mm body on a 16 mm round, 6 mm long peg, 20 g) rests on a grey datum pad at (14, +20) cm. A pocket leaves 7 mm of peg clearance per side, and once the sash pushes the block against the pocket's +Y wall the sash opening is 50, 100 or 150 mm for the three pockets.

The left arm (y > 0) grips the block, carries it to the 100 mm pocket (Y = 78 mm), releases it about 28 mm above the floor and returns to its ready pose. The right arm (y < 0) then pushes the sash open from behind by its tab until the block stops it. The hands stay at least 150 mm apart in y throughout (screen: 277 mm).

## Setup & Starting Configuration

- **Robot**: Dual YAM bimanual manipulator mounted on station table (`TABLE_TOP = 0.7475 m`), left arm base at `(0.0, +0.305, 0.75) m`, right arm base at `(0.0, -0.305, 0.75) m`.
- **Window Frame**: Brown frame at `(0.30, 0.0, 0.7475) m`, 6 mm floor with three 30 x 30 mm pockets, rails and end walls 24 mm high.
- **Sash Pane**: White pane at rest at Y = -0.10 m with a rear tab (80 x 20 mm, top 61 mm above the floor).
- **Datum Pad**: Grey pad (60 x 60 x 5 mm) at `(0.14, +0.20) m`; the block's peg bottom rests on it.
- **Stop Block**: Cyan block, body 30 x 30 x 30 mm, peg radius 8 mm, 20 g, friction 1.2.

## Scoring

- **Gates**: score 0 if the frame drifts more than 5 mm or the block falls below the tabletop.
- **Ladder**:
  - `0.25`: block lifted off the pad (>= 8 mm up or >= 20 mm along the table).
  - `0.50`: block seated in a pocket (x within 10 mm, y within 10 mm of the pocket centre, body bottom within 2 mm of the floor).
  - `0.75`: sash pushed open (20 mm to 119 mm) and stopped by the seated block (sash front within 6 mm of the block face).
  - `1.00`: block in the 100 mm pocket, sash opening 95 to 105 mm, held still for 1.0 s.
- Idle (nothing moved) and the ablation (block never placed) score 0.

## Execution & Evaluation

```bash
bash run.sh settle     # 8 s hold at ready
bash run.sh demo       # scripted two-arm demo, 1500 steps
bash run.sh ablation   # left arm idle, right arm still pushes the sash: score 0
bash run.sh dream      # Dream policy, 2400 steps
```

Object jitter is disabled (`object_jitter=0`). Offline screen: demo score 1.0, 12 of 12 randomised runs at 1.0, ablation 0.
