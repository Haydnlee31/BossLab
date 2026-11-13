# Image-to-3D run sheet, 2026-11-13: estoc first, then skeleton

The free ZeroGPU quota allows about one TRELLIS.2 run a day. It resets at about 10:04 +08. A TRELLIS call asks for 120 s, and a FLUX call takes about 8 s. The token is given only inline as `HF_TOKEN=... <command>` and is never written to a file, the shell history or git. All paths below are relative to the repo root. `B=unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender`, `PY=.venv-gen3d/bin/python`.

## 1. Estoc (today's TRELLIS run)

1. **Input:** `artifacts/art/estoc-2026-11-13/inputs/estoc-input-clean.png`. One straight one-handed sword on a flat background, pommel up: a ball pommel, a wrapped grip, a short straight cross with ball ends, and a long tapering blade.
2. **Generate:**
   ```
   HF_TOKEN=… $PY unreal/art-studio/source/gen3d/trellis2_generate.py artifacts/art/estoc-2026-11-13/inputs/estoc-input-clean.png artifacts/art/estoc-2026-11-13/trellis2 3 1024
   ```
   Use seed 3 and resolution 1024, the same settings that gave the censer in 35 s.
3. **Check:** run `render_glb.py` or the prep previews. Look for:
   - a single straight blade, not bent or fused into a slab;
   - a thin edge profile;
   - a guard that reads as a cross.
4. **Prep:**
   ```
   $B -b --python unreal/art-studio/source/regent/prep_estoc_trellis.py -- artifacts/art/estoc-2026-11-13/trellis2/model.glb artifacts/art/estoc-2026-11-13/prep
   ```
   This makes about 9k triangles, with the pommel at the origin, the point toward +Z, an overall length of 1.49 m and the guard along X. These match the interim CC0 `SM_Estoc` (37.2 × 14.9 × 149.2 cm, guard along X). `estoc-gen.json` reports `guard_m`. The script was checked on a synthetic tilted sword: guard 0.211 m reported, 0.211 m expected, with the correct handedness and the pommel end detected.
5. **Import:** take `editor.lock`, then run
   ```
   ./scripts/bosslab-unreal editor unreal/art-studio/source/regent/ue_import_estoc_gen.py
   ```
   It writes `/Game/BossLab/Regent/Estoc` (local). Exit 1 is expected because the script quits the editor.
6. **Game:** in `DressRegentWeapon()` (`WardenRegent.cpp`), prefer `/Game/BossLab/Regent/Estoc/SM_RegentEstocGen` and keep `SM_Estoc` and the primitive as fallbacks.
   - **Seating:** keep the guard where the interim guard is in game, about 17.2 cm along `SwordRoot` (`-22 + 35×1.12`). That gives `Z = 17.2 − guard_m×100×1.12` at scale 1.12, so the point stays at the same reach of about 145 cm.
   - **Rules:** presentation only. Reach, hitboxes and timing are unchanged.
   - **Effects:** glint, dash fire and the trail follow the tip. Check that they still sit on the new blade's point.
7. **Verify:**
   - `./scripts/bosslab-unreal test`: native 35/35;
   - `BOSSLAB_OUTFIT=revamp BOSSLAB_BOSS=regent ./scripts/bosslab-unreal capture regent-study`: check the close-up crops of the grip in the hand, the guard and the point.
   - Then delete the frames and write a README like `censer-2026-11-12/README.md`.

## 2. Skeleton (raised dead), the next model

**Current state:** each raised skeleton is a gaunt mannequin with `M_RegentDead` and the generated skull ×1.45. It is animated by `MF_Unarmed_Walk_Fwd` (65% speed) and `MM_Attack_02`, both played directly on the mannequin skeleton (`WardenRegent.cpp`, about line 733).

**Plan:**

1. **FLUX input:** this is cheap at about 8 s per image. Make 4 seeds, then choose one where:
   - the body is whole and symmetrical;
   - the arms are clear of the ribs;
   - the feet are visible.

   ```
   HF_TOKEN=… $PY unreal/art-studio/source/gen3d/flux_generate.py artifacts/art/skeleton-2026-11-13/inputs/skeleton-<seed>.png <seed> \
   A single standing human skeleton, complete full body from skull to feet, front view, symmetrical A-pose with both arms held clearly away from the ribcage and legs slightly apart, dark aged brown bone with cracks and soot, whole ribcage, pelvis and spine visible, isolated on a plain flat light grey background, centered, entire body in frame, studio product photograph, soft even diffuse lighting, no shadows, sharp detail, no clothing, no weapon, no text
   ```

   Use seeds 3, 7, 11 and 19. The A-pose roughly matches the mannequin's rest arms, so the `rig_fit.py` `pose` re-rest stays small.
2. **TRELLIS:** the next daily run after the estoc, unless today's quota has room left. Use `trellis2_generate.py` on the chosen input with seed 3 and resolution 1024 (or 1536 for thin bones).
3. **Rig:** `rig_fit.py <skeleton-fit.json>`. Copy `artifacts/art/claude-revamp-2026-11-09/rig/regent-fit.json` and set:
   - no `chains` (no cloth);
   - a small `voxel` (about 0.01 m), so the thin limbs and ribs get a closed weighting proxy;
   - `target_tris` about 20k.

   Bone order and translations stay identical to the mannequin. Check with `fit_overlay.py`, `weight_view.py` and `pose_test.py`.
4. **Import:** import as a skeletal mesh **on the existing mannequin `USkeleton`** (`SK_Mannequin`), not on a new skeleton. The current walk and attack clips then play on it directly. Rest rotations may differ only through the rotations-only re-rest. Target folder: `/Game/BossLab/Regent/Dead` (local).
5. **Game:** the dead slots prefer the skeleton mesh. Hide the separate skull, or keep the skull's eye and crown fire anchored to the `head` bone. Raise-the-Dead rules (speed, telegraph, 3 blows, 14 damage) are unchanged.

**Known risk:** image-to-3D can fill the gaps between ribs and between limbs and the body with solid material. Choose an input with clear gaps, and expect to cut fused regions with `cut_segments`/`cut_islands`, as on the Regent costume.

## Guards

- Keep at least 15 GiB free (`scripts/bosslab-unreal RESERVE`) and at most 10 GB under `unreal/`.
- Run one heavy job at a time.
- Delete capture frames after inspection.
- No paid services and no stored token.
