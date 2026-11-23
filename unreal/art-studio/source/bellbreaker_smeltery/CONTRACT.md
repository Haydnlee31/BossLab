# Smeltery modular handoff

New opt-in environment only. Blender metres; verified FBX convention imports at 100× into Unreal centimetres. +Y rear forge, origin floor centre. `layout.json` instances carry asset path, location_cm, rotation_deg [pitch,yaw,roll], scale. Visuals NoCollision; builder owns separate rectangular floor/perimeter collision.

Flat walk rectangle X±14m/Y±18m. Revised high-vault supports at X±18.1m (feet min|X|≈16.95m), explicitly approved after warehouse-form rejection. This sacrifices the former six-metre decorative reserve locally while preserving the entire walk rectangle; actual camera behavior remains to test. Outer walls remain beyond X±24m. LOW anvil/toolbench groups intentionally closer at X16–17m; entire bounds must remain ≥0.5m beyond walk rectangle. This supersedes the former all-machinery-beyond-reserve statement. Molten channels outside walking region, stone copings, scenic only. Camera reserve is a proposal, not tested camera behaviour.

Four source HF GLBs preserved. Derived copies decimated and exact-zero-area faces removed; textures extracted; no calibrated PBR claim. Importer creates only /Game/BossLab/Smeltery assets; no existing arena deletion. Optional max4 shadowless warm lights in manifest. No boss in walkthrough.

## FBX coordinate compensation

ActualUEimport proved BlenderFBXYreflection despite matching dimensions. Run guardedaxis export afterfinal/finish: copyvertexYnegation+reversewinding, positiveidentitytransforms. Originalpieces.bounds_m stay authorcoordinates; importerasserts signedbounds. Never negateactor scale. `export-axis-correction.json` binds each correctedFBXhash to frozenstudioscene.
