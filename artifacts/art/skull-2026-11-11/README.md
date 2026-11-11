# Generated witness skull, 2026-11-11

- **Generation:** TRELLIS.2 on [skull-side-7.png](../hf-leftover-2026-11-10/inputs/skull-side-7.png), the 45° FLUX input, with seed 3 and resolution 1024. It took 72 s and used one free daily run. The owner's token was passed only as an environment variable.
- **Result:** a fully volumetric skull, with a cranium, sockets, nose, teeth and a separate jaw line. The thinnest dimension is 0.68 of the largest; the rejected overnight skull was a flat relief. It has 284k faces, so it must be decimated.
- **Evidence:** `skull-trellis2-views.png` shows eight orthographic views (front, sides, back, three-quarters, top and below), rendered as a quick face splat without Blender.
- **Local only:** `trellis2/model.glb` (10 MB) stays local, like the other generated assets.
- **Remaining quota:** spent on one censer input, [censer-5.png](../hf-leftover-2026-11-10/inputs/censer-5.png), for the next TRELLIS run.
- **Integration pending.** It was not started because free disk space was 21.2 GiB, below the 24 GiB reserve.
  1. Blender: `prep_skull_trellis.py <model.glb> <out_dir> [yaw]`, which decimates to about 9k triangles, sizes the skull to 22 cm and exports FBX.
  2. Unreal: `ue_import_regent_props.py` in editor mode.

## Integration (same day)

The owner lowered the free-space minimum to 15 GiB (`RESERVE` in `scripts/bosslab-unreal`) and asked for integration.

- **Blender prep.** `prep_skull_trellis.py <glb> prep 90`, two fixes made along the way:
  - **Rotation:** the glTF import leaves objects in quaternion mode, so the yaw was silently ignored. The script now switches to XYZ first.
  - **Textures:** `image.save()` wrote WebP data under `.png` names, which Unreal rejected. The script now copies the pixels into true PNGs.
  - **Result:** 284,035 triangles reduced to 9,000, with the face along +X (`skull-prepared-previews.png`).
- **Unreal import.** [ue_import_skull_gen.py](../../../unreal/art-studio/source/regent/ue_import_skull_gen.py), run in editor mode, imports into `/Game/BossLab/Regent/Skull` (local). This folder is separate from `/Props`, which `ue_import_regent_props.py` deletes.
  - **Mesh:** `SM_RegentSkullGen`, 8,997 triangles, 22.0 × 15.0 × 19.3 cm (the interim skull is 19.9 × 13.5 × 18.0).
  - **Material:** `M_RegentSkullGen` uses the generated albedo cooled ×(.78,.78,.82), roughness ≥ .55 from the G channel, specular .35, and no metal.
- **Game.** `WardenRegent.cpp` prefers `SM_RegentSkullGen` when it is present, scaled ×1.27 so it is the same size on screen as the interim ×1.4. Otherwise it falls back to the interim skull, then to the primitive. The eye glows, flames and trails are unchanged. Presentation only, so combat is untouched.
- **Verification:**
  - **Tests:** native suite 33/33.
  - **Capture:** a Regent study capture from the Witness Volley (dungeon, revamp, performance). `skull-in-game-volley-closeups.png` shows the skulls in flight with readable cranium, jaw and teeth; `regent-study-from-volley-sheet.png` shows the full study.
  - **Not verified:** the eye glows are hard to see at study-camera distance, and the skull has not been owner-tested.
