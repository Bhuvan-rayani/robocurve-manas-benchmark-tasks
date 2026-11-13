# Put a utility knife away in its holder, retracting the blade first and keeping both fingertips clear of it

## Instruction

Put the utility knife away in its holder and release it.

## Context

A utility knife left with its blade out is a cut hazard to the next person; it is safe to store only once the blade is retracted (UCF Environmental Health and Safety, 'Safe Use of Utility Knives'). The ability tested: notice the exposed blade, push the blade slider home with the slider button, keep both fingertips off the blade, and stow the knife in its holder (the holder takes the knife only with the blade in). Occupations: Packers and Packagers (O*NET 53-7064.00) and Construction Laborers (47-2061.00). Closest cards: TK-UQBJUF (trim card on guillotine cutter), TK-BRZCAY (sharpen kitchen knife on whetstone), TK-5Y7J8Y (rat trap set safely). New here: a retract-before-stowing precondition with a physical consequence, a friction-lock slider on a loose knife, a blade keep-out checked with both pads.

## Setup

Positions are object centres in cm from the midpoint between the arm bases (x forward, y left), z above the bench (hardwood, friction 0.5). Material as modelled: rigid bodies with only the size, mass and friction stated here; knife is yellow ABS with rubber grip (90 g), blade slider is steel (20 g), holster is PLA (25 kg stand-in), and cutting mat is rubber (fixed). Layout is identical in every trial. Utility knife (loose, 90 g, friction 0.6/0.5): handle 3.2 x 19.0 x 1.8 cm at (22, -20) lying along y on the cutting mat (handle z 2.0 to 3.8), blade OUT: blade carrier 1.8 x 5.5 x 0.15 cm at y -12.0 to -6.5, z 2.83 to 2.98 (25 mm exposed); button 1.4 x 2.0 x 1.2 cm at y -6.0 on the handle top (z 3.85 to 5.05). Blade slider (slide on knife, 20 g): axis +y, travel 25 mm, no return spring (friction lock), damping 100 N s/m; fully retracted at +y the blade is inside handle (y -9.5 to -4.0) and button at y -3.5. Holster (fixed, 25 kg, friction 1.2): block 8.4 x 23.6 x 3 cm at (30, -20); pocket 5.2 x 20.6 x 2.6 cm (floor z 0.4), 1 cm play each side of the handle; with blade out knife is 21.5 cm and cannot lie in pocket. Cutting mat (fixed): green rubber, 7 x 26 x 2 cm at (22, -20), its +x edge 3 mm from the holster. Both grippers start open at ready poses; the layout is in front of the right arm.

## Scoring

End state plus latched facts. BLADE_ZONE = blade box (1.8 x 5.5 x 0.15 cm) inflated 3 mm, active while slider displacement < 24 mm. PADS = 12 mm boxes on both fingers of each hand, at the tool point and the fingertip, at the measured finger opening. RETRACTED = slider displacement >= 22.5 mm (90 %). STOWED = knife centre within 10 mm of pocket centre (30, -20) in x and 15 mm in y, base z <= 0.9 cm, tilt <= 5 deg. RELEASED = gripper centres and pad boxes at least 3 cm from knife and holster. STILL = knife moves less than 1 mm in last 1 s. Permanent zero: any pad overlaps BLADE_ZONE at any step. Ladder: 1.0: RETRACTED, STOWED, RELEASED, STILL, no fault. 0.75: RETRACTED and STOWED, but RELEASED or STILL fails. 0.5: RETRACTED but knife not stowed. 0.25: knife stowed or resting on holster with blade still out, no pad in zone. Else 0. Possible scores: 0.0, 0.25, 0.5, 0.75, 1.0.

## Fidelity

Real-size utility knife (about 19 x 3.2 x 1.8 cm, 90 g) on a cutting mat, and a holster. The blade is a 1.5 mm box (the simulator's thinnest), blade out only 2.5 cm (real 3 to 6), and it cuts nothing; the slider is a friction-lock slide (real knives add a lock notch or button); the holster is an open pocket with 1 cm side play (real holsters are belt pouches). Pads are checked against a 3 mm zone round the blade. Friction as modelled.

## Execution

```bash
bash run.sh settle     # 8 s hold at ready pose (200 steps)
bash run.sh demo       # scripted two-arm demo, 1,200 steps
bash run.sh ablation   # the hand skips the blade retraction and tries to stow with the blade out; 1,200 steps
bash run.sh dream      # Dream-1 policy, 1,200 steps
```

Run limit: 1,200 control steps (60 seconds at 20 Hz). The scripted demo takes about 21.0 s (about 420 control steps at 20 Hz). Object jitter is disabled (object_jitter=0), so there are no random seeds.
