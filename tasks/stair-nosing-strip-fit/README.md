# Fit Stair Nosing Anti-Slip Strip

## Benchmark Information
- **Category:** Societal relevance
- **Instruction:** "Fit the yellow anti-slip strip along the edge of the grey step."
- **Embodiment:** Dual YAM station tabletop (z = 747.5 mm)

## Component Setup Table
| Object | Type | Size (mm) | Material | Mass (kg) | Colour (sRGB) | Nominal Pos (m) | Friction | Function & Grasp |
|---|---|---|---|---|---|---|---|---|
| `stair_step` | Fixed | 140 x 400 x 60 | PLA | 25.0 | #8A9099 | (0.36, 0.00, 0.7475) | 1.2 / 1.0 | Fixed concrete step section; tread top at z = 807.5 mm |
| `strip_pad` | Fixed | 60 x 440 x 10 | PLA | 25.0 | #5A6068 | (0.18, 0.00, 0.7475) | 1.2 / 1.0 | Fixed staging pad on table |
| `nosing_strip` | Loose | 40 x 380 x 40 | PLA | 0.15 | #F5C400 | (0.18, 0.00, 0.7575) | 1.2 / 1.0 | L-section anti-slip strip (15 mm lip); carry at y = +/-16 cm |

## Scoring Rules & Ladder
- **Gates:**
  - `stair_step` or `strip_pad` displacement > 5.0 mm zeroes score.
  - `nosing_strip` dropped below table or overturned (tilt > 45 deg) zeroes score.
- **Ladder:**
  - `0.00`: Initial staging pose on pad.
  - `0.25`: Strip lifted off pad by at least 30 mm (z >= 787.5 mm).
  - `0.50`: Strip brought over step front edge (x in [0.260, 0.330] m).
  - `0.75`: Front lip engaged over step front face (flange z <= 822.5 mm, tilt <= 6 deg).
  - `1.00`: Strip fully seated flush on tread (|dz| <= 2.5 mm, |dx| <= 3.0 mm, |dy| <= 4.0 mm, tilt <= 3 deg), grippers clear, motionless for 1.0 s.
- **Possible scores:** 0.0, 0.25, 0.5, 0.75, 1.0.

## Physical Mechanism & Fidelity
The task models true bimanual dual carry of an elongated lightweight extrusion. The nosing strip is represented with compound collision boxes capturing both the vertical front lip (15 mm thick) and the horizontal top flange (40 mm wide). Grasping at $y = \pm 16.0$ cm enforces a wide 320 mm bimanual separation ($\gg 150$ mm design target). The scorer evaluates physical 3D flush contact on the tread, front face lip overlap, and lateral symmetry.

## Real-World Rig & Reset
To reset the physical cell, return the yellow nosing strip to its initial position on the staging pad centered at x = 18.0 cm with the front lip hanging off the -X edge. Confirm the fixed concrete step remains securely bolted at x = 36.0 cm.

## Run Commands
```bash
./run.sh settle    # 200 steps static stability test
./run.sh demo      # 1,500 steps coordinated bimanual demo
./run.sh ablation  # 1,500 steps single-arm ablation
./run.sh dream     # 2,400 steps policy evaluation
```

## Measured in the simulator (Isaac Lab-Arena on an L40S, 2026-11-10)
| Run | Score | Notes |
|---|---|---|
| demo (scripted) | 1.0 | strip lifted, carried over the step and seated: dx 1.9 mm, dy 0.1 mm, dz 0.0 mm, tilt 0.7 degrees |
| Dream-1 (2,400 steps) | 0.0 | the strip stayed on the pad at its start position |
The first simulator run scored 0.0: the strip is 38 cm long, and with the fingers closing along its length they could not hold it. The grippers are now turned 90 degrees so the fingers close across the 4 cm strip.

## Honest limits
The step and pad are fixed 25 kg bodies, and the strip is a rigid L-profile that sits on the tread by gravity: there is no adhesive, screw or clip.
