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
   - Checks: `fit_overlay.py`/`overlay.sh` (joint overlay), `weight_view.py` (dominant-bone colours), `pose_test.py` (stride/raised-arm deform).
5. **Unreal import** — `./scripts/bosslab-unreal python unreal/art-studio/source/gen3d/ue_import_revamp.py`: skeletal meshes on `SK_Mannequin`, textures, one masked material per character (base colour, roughness G, metallic B, opacity from base alpha, `used_with_skeletal_mesh`). Assets: `/Game/BossLab/Revamp/`.
6. **Game** — `WardenRevamp.cpp`: with `-BossLabRevamp`, `DressRevamp()` swaps the visible poseable mesh to the player or Regent asset after checking bone count, names, parents and local translations against the mannequin; any mismatch logs a warning and keeps the original outfit. Both fighters keep the engine sword; primitive boss crown/shoulders/mantle are hidden. Combat timing, reach and collision are unchanged.

## Verified results (2026-11-09)

- Default native suite **21/21**; dedicated `RevampTrial.SkinnedCharactersAndMotion` **1/1** (asset selection both ways, no duplicate components on reset, bones finite through 8-direction rolls for both fighters, feet ≥ −2 cm, engine grip error 0.000 cm). Run with `BOSSLAB_OUTFIT=revamp BOSSLAB_TEST_FILTER=RevampTrial ./scripts/bosslab-unreal test`.
- Actual in-game captures (fixed 30 fps): outfit turntable and motion study keyframes in `artifacts/art/claude-revamp-2026-11-09/unreal/` (`outfit-sheet.png`, `motion-sheet.png`, `boss-zoom.png`). Knight renders textured, attacks and rolls; Regent stands in as the boss.
- One 720p performance-preset editor run, revamp characters: **16.9451 ms mean (59.0 FPS), 17.3113 ms p95**, 3211 samples. Single shared-machine run; comparable to the recorded original 58.55 / V13 59.03 FPS runs, not a locked-60 claim. Report: `unreal/revamp-benchmark.json`.

## Known limits

- Generated, not hand-authored: single-view generation guessed unseen sides; texture lighting is partly baked; armour albedo is darker and less worn than the concept.
- No cloth simulation. Capes/robes ride the spine/pelvis and parts of the lower cape follow the calves; expect clipping in rolls and wide strides. Pauldrons follow the spine, not the arm.
- Both fighters hold the primitive engine sword. Generated swords and the three skulls are not done: the free ZeroGPU daily quota ran out (inputs `greatsword-input.png`, `regent-sword-input.png` are ready).
- The Unreal assets (`Content/BossLab/Revamp/`, ~72 MB) and the rig FBX/PNG sources are local and not committed; rerun steps 4–5 to rebuild them.

## Next

1. Generate the greatsword and Regent sword when quota resets, attach as cosmetic meshes on `SwordRoot` scaled to the existing 148 cm reach.
2. Generate the three skulls; float them as cosmetic components (no damage; chain/skull abilities remain unimplemented proposals).
3. Cape/robe: add a few chain bones or Unreal cloth for the mantle and cape instead of rigid spine weights.
4. Material pass: brighten/wear the knight's steel toward the concept.
5. Boss AI work can resume in parallel now that the characters are playable.
