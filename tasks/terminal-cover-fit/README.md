# Lower protective cover over high-voltage terminals (terminal_cover_fit)

## Task Overview
Lower the clear-grey cover over the two live terminals so both are enclosed.

## Hardware & Embodiment
- Embodiment: Dual YAM manipulators mounted on station tabletop (table top z = 0.7475 m).
- Base separation: Base centers at y = +0.305 m (Left) and y = -0.305 m (Right).
- Workspace: Single-arm left transfer along midline, assembly height z = TABLE_TOP + 0.050 m.

## Components & Staging
- `terminal_block`: Fixed 25.0 kg white terminal fixture (140 x 200 x 30 mm, friction 1.2) at [0.30, 0.0, TABLE_TOP] m with red (+y) and blue (-y) terminal posts (height 35 mm).
- `cover_pad`: Fixed 25.0 kg grey staging pad (140 x 200 x 10 mm) at [0.14, 0.0, TABLE_TOP] m.
- `terminal_cover`: Loose 0.30 kg clear-grey cover (120 x 180 x 40 mm, friction 0.8) with top center handle (20 x 60 x 15 mm) starting on pad at [0.14, 0.0, TABLE_TOP + 0.010] m.

## Kinematics & Manipulation Strategy
1. **Approach & Grasp:** Left arm moves from ready pose to hover over top handle at [0.14, 0.0, TABLE_TOP + 0.120] m, descends to grasp handle at [0.14, 0.0, TABLE_TOP + 0.060] m, and lifts vertically to TABLE_TOP + 0.150 m.
2. **Transfer & Seating:** Left arm carries cover levelly along x to [0.30, 0.0, TABLE_TOP + 0.150] m, lowers onto the terminal block rim at [0.30, 0.0, TABLE_TOP + 0.075] m, releases, and lifts straight up (Rule 17) to clear rim before retracting to ready. Right arm holds standby at [0.20, -0.25, TABLE_TOP + 0.160] m.
3. **Motionless Hold:** Cover rests flush on block rim for >= 1.0 s motionless hold.

## Scoring Ladder
- 0.00: Initial staging state.
- 0.25: Cover lifted > 30 mm off staging pad.
- 0.50: Cover positioned over terminals within 30 mm.
- 0.75: Cover within 10 mm of terminals and level (tilt < 8 deg).
- 1.00: Cover seated on terminal block rim within 8 mm horizontal and 3 mm vertical, motionless for 1.0 s.
- Gate: Terminal block drift > 5 mm or drop below table zeroes score.
