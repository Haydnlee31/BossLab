# Claude revamp — 2026-11-09

Branch `Claude-revamp`. Owner direction (2026-11-09): reach the approved player and Funeral Regent concept targets; free models and free services are allowed, paid services are not. Owner then said to proceed to rigging and game integration without a separate review stop.

## Play it

```sh
BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

Editor-game only, like the V13 trial; package modes reject `revamp`. Omit `BOSSLAB_OUTFIT` for the original costumes. The HUD shows `REVAMP TEST`.

## Why the method changed

V1–V13 and the Regent clay/cage/focal studies were built by Python scripts placing and smoothing primitives in Blender. That plateaued well below the targets, which depend on sculpted forms, cloth and painted textures. The revamp generates the characters from the approved concept images instead, then rigs them onto the existing mannequin skeleton.

## Pipeline (all scripts in `unreal/art-studio/source/gen3d/`)

1. **Generate** — `trellis2_generate.py <input.png> <out_dir>` calls the free `microsoft/TRELLIS.2` Hugging Face Space. Token only via the `HF_TOKEN` environment variable. Inputs in `artifacts/art/claude-revamp-2026-11-09/inputs/` (title text, the separate player sword and the floating skulls painted out).
2. **Review** — `review.sh <model.glb> <out_dir>` renders front/three-quarter/side/back.
3. **Mannequin export** — `ue_export_manny.py`, run with `./scripts/bosslab-unreal editor <script>` (FBX skeletal export asserts in headless commandlets).
4. **Fit and skin** — `rig_fit.py <fit.json>` in project-local Blender. Configs: `artifacts/art/claude-revamp-2026-11-09/rig/{player,regent}-fit.json`.
   - Welds UV-seam splits, scales to the mannequin, cuts the Regent's fused sword (segment + hilt box), decimates 296k/286k → 100k triangles.
   - Re-rests the mannequin arms with **rotations only** (`pose`), so every local bone translation and the bone order stay identical to `SKM_Manny_Simple`. The game copies poses from the hidden mannequin by bone index; this is what makes that valid.
   - Skin weights are distance-to-bone-segment with per-limb radii. Arm bones ignore anything >9 cm behind the arm and leg bones anything >15 cm in front/behind, so capes, robes and stoles fall back to spine/pelvis. Bone-heat on a voxel proxy failed outright (61k/61k proxy vertices unweighted) and is not used.
   - Swing chains (`chains` in the fit config): parentless `cape_<group><c>_<k>` bones (plus an unweighted `_end`) placed on the cloth surface, appended after every mannequin bone so mannequin indices are unchanged. Cloth = the outermost back/front layer within `layer` of the surface in each 3 cm cell, inside `x_extent`; it blends from the body bones onto the chains below the chain top. Check with `weight_view.py` (magenta = chains; `rig/swing-chain-weights.png`).
   - Material split: faces whose base-colour alpha drops below `cutout_alpha` (.98) anywhere get the `Cloth` slot; the rest are `Solid`.
   - Checks: `fit_overlay.py`/`overlay.sh` (joint overlay), `weight_view.py` (dominant-bone colours), `pose_test.py` (stride/raised-arm deform).
5. **Unreal import** — `./scripts/bosslab-unreal editor unreal/art-studio/source/gen3d/ue_import_revamp.py` (editor mode: creating a skeleton makes the FBX importer report via Slate, which asserts headless; the script quits the editor, launcher exit 1 is expected). Each mesh gets its own `SKM_*_Skeleton` (the shared `SK_Mannequin` is not modified); delete the old `SKM_Revamp*.uasset` first if a reimport reuses it. Two materials per character, both two-sided (generated cloth is often a single sheet): opaque `M_Revamp*` and masked `M_Revamp*Cloth` (opacity from base alpha); roughness G, metallic B, `used_with_skeletal_mesh`. Assets: `/Game/BossLab/Revamp/`.
6. **Game** — `WardenRevamp.cpp`: with `-BossLabRevamp`, `DressRevamp()` swaps the visible poseable mesh to the player or Regent asset after checking the mannequin bones' names, parents and local translations and that any extra bones are appended `cape_*` chains; any mismatch logs a warning and keeps the original outfit. Both fighters keep the engine sword; primitive boss crown/shoulders/mantle are hidden. Combat timing, reach and collision are unchanged.
7. **Swing chains** — `SwingCloth()` runs after each fixed-step pose (60 Hz, deterministic): Verlet particles pulled toward the rigid cape pose (30% per step at the top to 7% at the hem; 55%/30% while rolling or dead so the cloth wraps instead of sheeting out), exact bone length, pushed out of pelvis/spine/thigh/calf spheres (never further than at rest), slid along the floor; tops are clamped to the floor too. Each segment's rotation aims at its simulated child. No physics scene or cloth asset; presentation only.

## Verified results (2026-11-09)

- Default native suite **21/21**; dedicated `RevampTrial.SkinnedCharactersAndMotion` **1/1** (asset selection both ways, no duplicate components on reset, bones finite through 8-direction rolls for both fighters, feet ≥ −2 cm, engine grip error 0.000 cm). Run with `BOSSLAB_OUTFIT=revamp BOSSLAB_TEST_FILTER=RevampTrial ./scripts/bosslab-unreal test`.
- Actual in-game captures (fixed 30 fps): outfit turntable and motion study keyframes in `artifacts/art/claude-revamp-2026-11-09/unreal/` (`outfit-sheet.png`, `motion-sheet.png`, `boss-zoom.png`). Knight renders textured, attacks and rolls; Regent stands in as the boss.
- One 720p performance-preset editor run, revamp characters: **16.9451 ms mean (59.0 FPS), 17.3113 ms p95**, 3211 samples. Single shared-machine run; comparable to the recorded original 58.55 / V13 59.03 FPS runs, not a locked-60 claim. Report: `unreal/revamp-benchmark.json`.

### Swing chains and material split (2026-11-09, later the same day)

- Default 21/21; `RevampTrial` 1/1 with new checks: chains present (knight 4, Regent 6), max chain stretch 0.0000 across 8-direction rolls for both fighters, chain minZ 2.000 cm (an earlier version stretched 37% and sank tips 70 cm; both fixed). Index: `unreal/swing-chain-trial-index.json`.
- Actual captures (fixed 30 fps) inspected: `unreal/cape-strike-sheet.png` (cape hangs and trails through strikes), `unreal/cape-roll-sheet.png`, `unreal/cape-midroll-closeup.png`, `unreal/exchange-regent-sheet.png` (24 s fight; Regent robes swing and stay attached).
- Material split: knight 35,203/100,000 faces masked, Regent 5/100,000 (its texture alpha is almost all opaque).
- Back-to-back 720p performance runs on a shared machine (`unreal/swing-chain-benchmarks.json`): original 16.85 ms mean / 16.84 p95; revamp 17.42 / 22.36 while load average rose 10→17. A first revamp run at 22.23 ms was confounded by two leftover CrashReportClient processes (~88% CPU each, from a crashed headless import), which were stopped. Not isolated; no locked-60 or optimisation claim.

## Known limits

- Generated, not hand-authored: single-view generation guessed unseen sides; texture lighting is partly baked; armour albedo is darker and less worn than the concept.
- Swing chains, not cloth simulation: 4–6 chains per character, no self-collision, sphere collision only. Mid-roll (about 5 frames) the knight's coat skirt, which is skinned to the legs rather than the chains, stands up with the legs while the body is inverted. Small patches inside the cape stay on leg/pelvis weights. Pauldrons follow the spine, not the arm.
- Both fighters hold the primitive engine sword. Generated swords and the three skulls are not done: the free ZeroGPU daily quota ran out (inputs `greatsword-input.png`, `regent-sword-input.png` are ready).
- The Unreal assets (`Content/BossLab/Revamp/`, ~72 MB) and the rig FBX/PNG sources are local and not committed; rerun steps 4–5 to rebuild them.

## Next

1. Generate the greatsword and Regent sword when quota resets, attach as cosmetic meshes on `SwordRoot` scaled to the existing 148 cm reach.
2. Generate the three skulls; float them as cosmetic components (no damage; chain/skull abilities remain unimplemented proposals).
3. Coat skirt: side/front skirt chains for the knight (and Regent sides) so the leg-skinned skirt stops standing up mid-roll.
4. Material pass: brighten/wear the knight's steel toward the concept.
5. Boss AI work can resume in parallel now that the characters are playable.
