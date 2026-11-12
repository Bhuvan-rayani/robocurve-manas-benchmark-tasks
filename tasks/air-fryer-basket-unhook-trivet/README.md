# Slide a hot air-fryer basket out from under its two retaining hooks, lift it by its handle and set it on the heat-proof mat (air_fryer_basket_unhook_trivet)

## Task Overview

The chips are done. Take the basket out of the air fryer and set it on the green mat; let go and keep both fingers at least 3 cm from the basket.

Taking a hot basket out of an air fryer is an everyday kitchen job; its walls and the housing are at frying temperature (the red lamp is lit), so only the black handle may be touched, and the basket must go down on a heat-proof mat. The ability tested is a keyed release (slide the basket 3 cm toward you until its flanges leave the retaining hooks, then lift) done through the handle. Manual source: Instant Vortex Air Fryer User Manual, Section 'Care, Cleaning and Storage - Handling the Fryer Basket': 'Always use the basket handle to remove and carry the basket; surfaces remain hot during and after cooking.' URL: https://www.instanthome.com. Closest on the board: TK-PSHKS8 (p) Set down a hot pot, TK-RSPMXH (a) Release a two-latch lid, TK-YVSVN2 (r) Press the slot latch; new here: hooks decide the removal direction and a touch of any hot surface scores 0.

## Setup & Starting Configuration

Positions are object centres in cm from the midpoint between the arm bases (x forward, y left), z above the table top (z = 0.7475 m, smooth laminate, friction 0.5). Air fryer housing (fixed, graphite painted steel, 25 kg stand-in, friction 1.2): 22 x 28 x 26 cm at (57, 0), front face at x 46; a red lamp (2 x 2 cm on the front face, 3 x 3 cm on the top face) is lit. Drawer plate (fixed, grey steel, 25 kg, friction 1.2): 18 x 23 x 3.6 cm at (37, 0), x 28 to 46, against the housing; the drawer is shown pulled out to its stop and its side walls are omitted. Two hook assemblies (fixed, same plate): a post 2 x 1 x 7.6 cm at y +/-10.7 (x 43.7 to 45.7) and an overhang 2 x 1.6 x 0.8 cm at y +/-9.4 whose underside is at z 10.4 cm; each overhang reaches over a basket flange. Basket (loose, orange-painted steel, 450 g, friction 0.32, handle black): floor 17 x 17 cm, walls 0.5 cm thick and 6 cm tall, floor centre at (37.2, 0), floor underside on the plate (z 3.6 cm), so it spans x 28.7 to 45.7. Two rear flanges, each 3 x 0.9 x 0.5 cm (x 42.7 to 45.7, y +/-8.5 to +/-9.4, z 9.1 to 9.6), sit under the hook overhangs with 8 mm vertical and 8 mm lateral clearance. Handle: two posts 3.7 x 2 x 3 cm at y +/-4.5 standing off the front wall (x 25 to 28.7) and a bar 4 x 12 x 2 cm across their ends (x 21 to 25, z 7.6 to 9.6; bar centre at x 23, z 8.6); the basket with handle is 24.7 x 18.8 x 6 cm. The basket must be pulled at least 2.0 cm toward the robot for the flanges to clear the overhangs, 2.8 cm with margin. Heat-proof mat (fixed, green silicone, 25 kg stand-in, friction 1.2): 20 x 20 x 1.0 cm at (35, -22) (x 25 to 45, y -32 to -12). Both arms start open at their ready poses. The layout is the same in every trial. Real build: the housing and drawer plate are 3D-printed PLA blocks bolted to the table (this replaces the 25 kg fixed mass), the hooks are printed PLA with 8 mm clearances, the basket is a 17 x 17 x 6 cm sheet-steel or printed box with printed handle and flanges, and the mat is a 1 cm silicone or foam pad bolted to the table. Material as modelled: every object is a rigid body with only the size, mass and friction stated here; nothing deforms and nothing heats.

## Reset

Push the basket fully back against the housing with its flanges under the hooks (floor centre at x 37.2 cm, y 0); put the mat at (35, -22); both grippers open and clear at ready. The first frame shows the red lamp lit and the basket in the drawer.

## Scoring

Final state plus faults. ON MAT: the basket's floor centre within 10 mm of the mat's centre, its floor underside within 3 mm of the mat's top (z 1.0 cm), tilt at most 3 degrees, turned at most 10 degrees. RELEASED: both gripper centres at least 3 cm from every part of the basket and both grippers at least 90% open. STILL: the basket moves slower than 1 cm/s at the end (1 s hold). UNHOOKED: the basket's floor centre has been at least 2.0 cm toward the robot of its start, so both flanges are clear of the hook overhangs, and it has been lifted at least 2 cm in that state. Permanent zero, even if recovered: at any time a gripper's pad bottom comes within 12 mm of an orange wall, the basket floor, a flange, the housing, the drawer plate or a hook (hot surfaces; only the black handle may be touched). 1.0: ON MAT, no fault, RELEASED, STILL. 0.75: ON MAT, no fault, but RELEASED or STILL fails. 0.5: UNHOOKED and lifted, no fault, but the basket ends elsewhere than on the mat. 0.25: the basket was slid at least 2.8 cm toward the robot at some time, no fault. Else 0. Doing nothing scores 0; a held or hovering basket does not count as on the mat. Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0. Real trial: tape (2.8 cm slide, 1 cm centring), a photo of the end state, and a video for hot-surface contact.

## Fidelity

No heat is simulated: hot surfaces are identified by the lit lamp and orange color, enforced by contact scoring. Two hooks over flanges provide a keyed slide-then-lift release with 8 mm clearances. Drawer side walls are omitted for lateral transit, basket is 6 cm deep for arm lift reach, and the handle stands 6.2 cm proud to admit gripper fingers. The drawer plate is fixed. Hot contact is checked from gripper geometry. The simulator scores end state, so demo leaves grippers open.

## Execution

```bash
bash run.sh settle     # 10 s hold at ready pose (200 steps)
bash run.sh demo       # scripted single-arm demo, 1,500 steps
bash run.sh ablation   # hold at ready pose, 1,200 steps
bash run.sh dream      # Dream-1 policy
```

Run limit: 2,400 steps (120 seconds at 20 Hz). The scripted demo takes about 22 s (about 432 control steps at 20 Hz). Object jitter is disabled (object_jitter=0), so there are no random seeds.
