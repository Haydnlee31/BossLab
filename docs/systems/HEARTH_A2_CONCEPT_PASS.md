# Hearth A2: concept pass, 2026-11-17

This pass moves the playable A2 room toward the approved board, *A — The Master Smith's Hearth*. It keeps A2's layout, collision, walkable field and camera envelope unchanged. Every change is presentation only and applies to A2 alone.

## Changes

1. **Materials** (`unreal/art-studio/source/hearth_a2/ue_concept_grade.py`, then `ue_concept_grade_walls.py`). These wrap the existing base colour and roughness inputs; they do not rebuild the materials. 29 materials are wrapped.
   - **Walls, vault and generated modules:** world-space soot that deepens with height and around the furnace mouth, plus some desaturation. The stone now reads dark and smoke-stained instead of clean beige.
   - **Floor:** darker, cooler stone with blotchy grime and damp patches (roughness about 0.34). The forge and lanterns now leave highlights on it.
   - **Oak:** darkened.
   - **Backups:** the original `.uasset` files are in `artifacts/art/hearth-a2-dressing-2026-11-17/material-backup/`. To restore a material, copy its backup over the file.
2. **Hot metal and forge fire** (`ue_concept_fire.py`).
   - **Molten material:** `M_A2_contained_molten_metal` is now mostly glowing metal crossed by dark crust veins.
   - **Forge fire:** the new additive `M_A2_ForgeFire` is placed in both furnace mouths, at the layout's `hearth_effect_anchors_cm`.
   - **Molten channel:** the imported hot-metal plate sits inside the furnace footprint and never showed. A new channel runs along the left wall at x ≈ 915 cm, outside the walkable field. It is a slab of molten material between stone rims, with one shadowless orange line light.
3. **Lighting and grade** (`WardenSmeltery.cpp`, A2 branch).
   - **Directional fill:** the two shadowless directional lights drop from 0.22/0.35 to 0.07/0.13. They had lit every face evenly.
   - **Furnace:** the furnace point light goes to 3200 lumens with a 2400 cm radius.
   - **Window:** the window spot goes to 4200 lumens, with volumetric scattering 2.2 so it forms a cool shaft.
   - **Fog:** denser, warm smoky fog.
   - **Grade:** an unbound post-process grade with warm highlights, cool shadows, firmer contrast, bloom and a vignette.
   - **Before values:** the layout before this pass is in `artifacts/art/hearth-a2-dressing-2026-11-17/layout-before.json`.
4. **Generated dressing.** The pipeline was FLUX.1-schnell inputs, then TRELLIS.2, then `prep_arena_gen.py`, then `ue_import_hearth_gen.py`, into `/Game/BossLab/HearthA2/Gen` (local).
   - **Bell:** a bronze bell on an oak stand, placed in the window bay.
   - **Coal:** three coal bins along the channel.
   - **Rack:** a sword rack between the coal and the ore storage.
   - **Ingots:** an ingot pallet by the entry-side channel end.
   - **Placement:** all of these are NoCollision layout instances outside the walkable field.
   - **Triangles:** about 165k added in total (bell 40k, coal 20k ×3, rack 25k, ingots 20k).
   - **Provenance:** the inputs and prompts are in `artifacts/art/hearth-a2-dressing-2026-11-17/inputs/`.
5. **Review views:** `BOSSLAB_HEARTH_VIEWS=1 ./scripts/bosslab-smeltery study` puts the player at 8 fixed spots facing each wall. It only affects scripted capture runs.

## Checks

- **Native suite:** 45/45.
- **`WardenAssetTrial.HearthA2.RuntimeCollision`:** 1/1.
- **Timing:** one screenshot-free run on a shared machine gave 2342 frames, a mean of 38.38 FPS, a median of 25.23 ms, a p95 of 42.06 ms, and 189 frames over 33.3 ms. Earlier A2 runs gave 28.5–33.1 FPS. This shows no regression; it is not proof of an optimisation.
- **Evidence:** in `artifacts/art/hearth-a2-dressing-2026-11-17/evidence/`: a before/after sheet, the route study and the fixed views.

## Still short of the board

- **Floor:** the flagstones are about 1.5 m, versus the board's small worn flags. Changing this needs new geometry.
- **Vault:** the board has deep shadowed arches with hanging chains, lanterns and banners. These are still missing.
- **Clutter:** foreground timber posts and clutter are still missing.
- **Steam:** the quench cistern has no steam.
- **Furnace:** the stone is still pale; the board's hood is darker and sootier.
- **Generated wood:** it is still bright and new-looking.
- **Owner review:** not done.

## Detail pass (same day, owner: "as detailed as possible")

This pass works through every gap in the list above. Everything is presentation only: no collision, walkable-field, camera or rules change.

- **Measured plan.** I rasterised all the A2 export meshes top-down; the mapping is Unreal = (100·bx, −100·by) cm. The plan gives the wall faces as x ≈ ±1080 and entry y ≈ −1370, and these drive every placement. The upper walls stand proud of that 0.4–2.2 m slice, so the banners hang in front of the wall rails.
- **Kit** (`unreal/art-studio/source/hearth_a2_kit/build_kit.py`, then `ue_import_kit.py`, into `/Game/BossLab/HearthA2/Kit`, local):
  - **Floor:** `SM_Kit_Floor` replaces the visual `SM_A2_floor`; the separate hidden collision floor is unchanged. It has 2,796 flagstones in running courses, 32–54 × 42–98 cm, each with a bevelled edge, slight tilt and a worn dished top. About 7% are cracked into two pieces and about 18% have a chipped corner. Each stone takes one of the six worn-floor materials with randomised UV offset and rotation, over a charcoal mortar bed. 58k triangles.
  - **Chains:** `SM_Kit_Chains` has 11 iron chains made of individual links, ending in J-hooks, rings or lantern mounts. Four of the room's own lantern meshes hang from them, each with a shadowless warm light. 45k triangles.
  - **Timber:** `SM_Kit_Timber` adds gallery frames along both side walls: oak posts on stone plinths, with iron bands, Y-braces and long beams, plus a high tie beam with iron straps across the entry bay.
  - **Banners:** `SM_Kit_Banners` adds six tattered, folded banners on iron rods. The emblem artwork comes from FLUX; I aged it, darkened it and cut its tattered edge in PIL, and the material is masked and two-sided.
- **Steam:** `M_A2_Steam` is a translucent rising noise drawn on three crossed planes over the quench cistern (`quench_steam_cm`). It is subtle in game, a soft haze. `ue_steam_tune.py` re-applies its values.
- **Furnace:** its graded material gets extra soot (×0.42 away from the mouth band). The furnace light moved down and forward to (420, 780, 70) at 2600 lumens, so the hood reads dark and the glow comes from the mouths and the floor.
- **More clutter:** TRELLIS.2 from FLUX inputs (`inputs2/`):
  - firewood stack;
  - barrel cluster;
  - grindstone;
  - two tool boards (tongs, hammers, chisels);
  - crate-and-sack pile.

  The importer now ages every generated prop: 40% desaturation, a grey-brown shift, ×0.46, and height soot.
- **Review views:** `BOSSLAB_HEARTH_VIEWS=1` views now include the entry wall.

### Checks

- **Native suite:** 45/45.
- **`WardenAssetTrial.HearthA2.RuntimeCollision`:** 1/1.
- **Timing:** one screenshot-free run on a shared machine gave 2436 frames, a mean of 40.32 FPS, a median of 24.6 ms, a p95 of 32.77 ms, and 115 frames over 33.3 ms. This shows no regression; it is not a claimed optimisation.
- **Evidence:** in `evidence/`: `before-after-detail.png`, `detail-views/`, `detail-study/` and `detail-timing-report.json`.

### Still open

- **Steam:** faint.
- **Banners:** the emblem doesn't read at gameplay distance.
- **Chains:** they go up into the vault; their anchor points are not modelled.
- **Wood finish:** the generated props' textures are still the TRELLIS bake, not hand-painted.
- **Owner review:** not done.

## Pass 3 (2026-11-17, owner: refine the imperfections, real fire, start the boss)

- **Forge fire:** the orange sphere is gone.
  - **Source:** LTX-Video (HF Space `Lightricks/ltx-video-distilled`) generated a 4 s clip of forge fire on black (`fire/fire-1.mp4` with its prompt `.json`).
  - **Flipbook:** 64 frames became an 8×8 flipbook (`T_A2_ForgeFlipbook.png`), with a 12-frame cross-fade so it loops seamlessly.
  - **Material:** `ue_forge_fire.py` creates `/Game/BossLab/HearthA2/Fire/M_A2_ForgeFlipbook`: additive, frame-blended at about 24 fps, a per-mouth phase, and soft edges.
  - **Placement:** three crossed planes per furnace mouth, over a low, flattened ember-bed glow.
- **Chains:** the vault underside above each chain was measured from the vault mesh (`kit/chain_ceiling.json`, 590–1061 cm). Each chain now starts there, hanging from a riveted iron anchor plate with an eye bolt, with at least about 1 m of chain under low vault.
- **Banner:** the emblem was enlarged about 1.55× (inked shield, hammer and anvil, with a tarnished-gold rim) on brighter cloth. It now reads at gameplay distance.
- **Steam:** five crossed planes, taller, denser and brighter, with a shorter depth fade. It now reads as a column of haze in front of the window.
- **Generated props:** a world-space grime layer over the TRELLIS bake: soot blotches, darker crevices from the bake's own darks, and dirt along the floor line. The surfaces are still generated, not hand-painted.
- **Boss:** the static Bellbreaker study and its bell-hammer. See `artifacts/art/bellbreaker-boss-2026-11-17/README.md`; the mannequin rig was rejected and a custom skeleton is next.
- **Checks:**
  - **Native suite:** 45/45.
  - **`WardenAssetTrial.HearthA2.RuntimeCollision`:** 1/1.
  - **Timing:** 2374 frames, a mean of 38.37 FPS, a median of 24.83 ms, a p95 of 42.88 ms (shared machine; noise within the earlier 38–40 range).
  - **Evidence:** `evidence/pass3-views`, `pass3-boss-preview` and `pass3-timing-report.json`.
