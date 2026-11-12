# Generated soul-fire censer, 2026-11-12

- **Generation:** TRELLIS.2 on the FLUX input [censer-5.png](../hf-leftover-2026-11-10/inputs/censer-5.png), with seed 3 and resolution 1024, after the free quota reset at about 10:04 +08. A first attempt at 09:52 was refused: "Try again in 0:11:44", with 178 s left against 120 s requested. The run took 35 s. The owner's token was passed only as an environment variable.
- **Result:** a fully round octagonal lantern, with a blackened iron cage, gothic arched panes, bronze bands, a spire cap and a hanging ring. Its extents are 0.34 × 1.0 × 0.34, with equal width and depth. It has 291k faces. See `censer-trellis2-views.png`, a quick face-splat render.
- **Blender:** [prep_censer_trellis.py](../../../unreal/art-studio/source/regent/prep_censer_trellis.py) `<glb> prep 0.24`:
  - decimates to 14,000 triangles;
  - puts the pivot at the top centre (the hanging point, like the interim lantern);
  - sets the height to 24 cm (58 cm in game at ×2.4; the interim lantern is 15.2 cm);
  - writes textures as real PNGs (`censer-prepared-previews.png`).
- **Unreal:** [ue_import_censer_gen.py](../../../unreal/art-studio/source/regent/ue_import_censer_gen.py), run in editor mode, imports into `/Game/BossLab/Regent/Censer` (local). This folder is kept separate from `/Props`.
  - **Mesh:** 13,985 triangles, 8.2 × 8.1 × 24.0 cm.
  - **Material:** `M_RegentCenserGen` uses the generated albedo darkened ×.85, roughness from G (at least .3) and metallic from B.
  - **Glass:** the generator baked the panes as opaque near-white panels, so bright, unsaturated albedo is treated as glass lit from inside: a flickering blue emissive.
- **Game:** `WardenRegent.cpp` prefers `SM_RegentCenserGen` over the interim lantern when it is present. The soul-fire card and point light move to the cage (34 cm below the hang point, against 18 cm before). This is presentation only; the chain path and combat are unchanged.
- **Verification:**
  - **Tests:** native suite 33/33.
  - **Capture:** a Regent study capture from Rite (dungeon, revamp), 0 material compile failures. `censer-in-game-closeups.png` shows 3× crops; `regent-study-censer-sheet.png` shows the whole study.
  - **Not verified:** the study camera is far away, so the censer has not been seen close up in play and has not been owner-tested.
- **Local only:** `trellis2/model.glb` (11 MB) and the prepared FBX and textures stay local.
- **Next free run:** the Regent's estoc (`artifacts/art/claude-revamp-2026-11-09/inputs/regent-sword-input.png`).
