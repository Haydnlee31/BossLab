# Generated Regent estoc, 2026-11-13

## Generation

- **Space and settings:** TRELLIS.2 on `inputs/estoc-input-clean.png`, seed 3, resolution 1024.
- **Run:** started at about 10:06 +08, after the free quota reset, and took 43 s. The owner's token was passed only as an inline environment variable and was not stored.
- **Result:** one straight sword with a ball pommel, a wrapped dark grip, a cross guard with ball ends, and an aged steel blade with a central ridge. The source has 295k triangles.

## Blender prep

- **Script:** `prep_estoc_trellis.py`.
- **Mesh:** decimated to 16,000 smooth-shaded triangles.
- **Placement:** pommel at the origin, point toward +Z, overall length 1.49 m, guard along X (the same as the interim `SM_Estoc`).
- **Guard:** detected at 0.286 m.
- **Textures:** saved as PNGs.
- **Previews:** `estoc-prepared-previews.png`.

## Unreal

- **Import:** `ue_import_estoc_gen.py`, run in editor mode.
- **Asset:** `/Game/BossLab/Regent/Estoc/SM_RegentEstocGen` (local only), 25.9 × 6.4 × 148.8 cm, 15,999 triangles.
- **Material:** `M_RegentEstocGen` uses the albedo, roughness from G (at least 0.28) and metallic from B.

## Game

- `DressRegentWeapon()` prefers this mesh. `SM_Estoc` and then the primitive blade remain as fallbacks.
- **Seating:** at scale 1.12 and location Z = 17.2 − 28.6 × 1.12 cm, the guard sits where the interim guard did and the point keeps the same reach.
- **Scope:** presentation only. Reach, hitboxes and timing are unchanged.

## Verification

- **Tests:** native suite 35/35.
- **Capture:** `capture regent-study` (revamp, Regent) ran with 0 material errors. See `regent-study-estoc-sheet.png` and `estoc-in-game-closeups.png`. The thrusts read as a long, thin textured blade, and the guard and pommel sit at the hand.
- **Not verified:**
  - an extreme close-up of the grip;
  - the generated texture looks patchy when viewed far closer than the game camera;
  - the owner has not tested it.

## Same day: skeleton inputs

- **FLUX images:** four FLUX.1-schnell skeleton inputs, `../skeleton-2026-11-13/inputs`, seeds 3, 7, 11 and 19, with the prompt in each `.json`. The sheet is `../skeleton-2026-11-13/skeleton-input-candidates.png`.
- **Choice:** seed 3, because its arms are held clearly away from the ribs and every gap is open.
- **Alternate:** seed 7, which has cleaner anatomy but hands beside the thighs, where the generator may fuse them.
- **TRELLIS:** the skeleton run was refused ("120s requested vs. 0s left"). It is the next daily run, with seed 3 and resolution 1536.
