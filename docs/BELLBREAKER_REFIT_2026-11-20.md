# Bellbreaker model and fight, 20 November 2026

## What prompted the pass

The previous attack study measured weapon contact. It did not measure whether the boots touched the floor or whether an elbow could suddenly change sides while the bell stayed still. In a controlled replay the actual lower boot surface was above the floor by a median 14.06 cm, reaching 31.45 cm. Both boots were more than 5 cm clear on 646 of 662 poses. The wrist-and-shoulder trace also revealed a 121 cm change of elbow position across adjacent phase-transition samples. This baseline already included the first new guide-hand and source-pose corrections and used the prior repaired ForgeSkin mesh.

## Generative authoring

We submitted four original movement prompts with nine seeds in total to Tencent HY-Motion on Hugging Face. Two full-body heaves put both toes too far above the floor for the encounter. Three deliberately planted press alternatives had inadequate downward travel. Casting and bone readbacks informed a six-bone upper-body performance from ForgeHeave seed 26 and a central two-step loop from ForgeStride seed 61. The lower body, hand seating and damaging hammer path are constrained by the native animation/gameplay implementation. The study outputs and exact prompts are under `artifacts/unreal/bellbreaker-refit-20261120/motion`.

Three FLUX Kontext edits used project-owned Bellbreaker reference art. Two edited references went through Microsoft TRELLIS.2 at resolution 1536 with 2048-square textures. The first result lost the soot, sash and shoulder armour character of the original. The second was selected for a weathered model study. Its raw generated mesh has 278,661 triangles. Its preview is a software rasterization of actual textured geometry viewed from three angles. Neither a generated still nor an unrigged GLB establishes in-game deformation quality. The design options, actual GLBs, preview renders and generation records are under `artifacts/unreal/bellbreaker-refit-20261120/sculpt`.

## Fitted costume

The ForgeShoulder sibling changes the skin weights of 3,609 shoulder vertices while retaining all 92,450 triangles, rest geometry, UVs, skeleton and material slots. On 5,423 shoulder-region triangles in the reconstructed Quake pose, the count stretched beyond twice resting area falls from 409 to 105. The count compressed below half falls from 532 to 26. Three separate synthetic poses also improved on both measures. These are controlled pose comparisons on the mesh, independent of subsequent changes to how the fight moves. Matched Blender renders, the reopened editable scene, the FBX and detailed evaluation live in `artifacts/art/bellbreaker-shoulder-2026-11-20/`.

## Four-attack replay in Unreal

Tested Hammer Fall, Forge Sweep, Bell Quake and The Bell Breaks. The bell follows a two-handed grip with a sliding guide hand. The elbows have a bounded swivel, and attack transitions blend from the source pose before the rig applies its adjustments. Hammer Fall uses the generated heave through the upper body. The big downstrokes distribute shoulder travel over more frames while keeping the original damage tick. The fitted boot sole is sampled from the installed mesh to place the lower boot against the floor.

On the default ForgeShoulder model, both hands touched the shaft in all 662 measured poses. At active samples the furthest reported offset between the visible bell and the melee trace was 0.0 cm to logging precision. The lower sole ranged from −0.56 to +0.60 cm. Across the four attacks there were zero sampled head, torso or leg contacts, 11 poses with upper-arm contact and 112 with forearm contact. These count sampled surface intersections and do not measure penetration depth. The largest adjacent elbow displacement fell from 121 to about 56.5 cm. The earlier replay contained 12 elbow displacements greater than 60 cm. The revised replay contained zero.

The weathered variant uses the new body and transferred donor hands after the first automatic hand fit broke apart on flexion. It has 84,037 triangles. In the same rehearsal both hands touched in 662 poses, but the shaft contacted the torso in one pose and the forearms in 134. Wrist transitions and softer facial and garment detail remain visible. ForgeShoulder is the default. To try the sibling, run `BOSSLAB_BB_SKIN=weathered ./scripts/bosslab-game` and select The Bellbreaker in Challenge. Use `./scripts/bosslab-game` for the default.

## Walking approach

The first normal-camera study showed that the generated gait moved the lower toe diagonally across the floor. The revised gait advances with actual distance travelled, guides each foot down its own lane and holds the supporting toe at a world-space position until the other foot takes over. Source knee flexion, toe lift and ankle rotations remain in the pose.

Across the same 57 walking samples and two cycle wraps, measured horizontal travel of the lower toe fell from 528.92 cm over 429.33 cm of actor advance (50 eligible pairs) to 21.65 cm over 440.67 cm (51 eligible pairs). The initial five pairs account for 20.79 cm of the remaining drift. After entry the lower toe travelled 0.86 cm over 398.67 cm of advance. This measurement covers a straight approach, weighted by path length. It does not establish performance during arbitrary sharp turns. The pre-correction clip is `gameplay.mp4`; the corrected player-camera clip is `planted.mp4`.

## Verification and evidence

Local Mac editor-game tests passed 54/54 native (one engine HTTP connectivity warning) and 2/2 forge. The 720p performance-preset run captured 3,446 active wall-clock frames after warmup, 16.71 ms mean (59.8 FPS) and 16.77 ms p95. This is a single run on this Mac.

Evidence is under `artifacts/unreal/bellbreaker-refit-20261120`. The player-camera movie `planted.mp4` decoded 270 frames. The stationary attacks movies `attacks.mp4` and `weathered-final.mp4` each decoded 600 frames. The former precedes the walking-only correction; an independent stationary replay after the correction reproduced all reported contact and boot statistics. `costumes-in-forge.jpg` shows a matched frame. These clips are silent, fixed-timestep Unreal output. Real-time performance is recorded separately in `performance.json`.
