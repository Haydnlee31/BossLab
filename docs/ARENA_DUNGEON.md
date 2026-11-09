# Dungeon arena — 2026-11-09

Owner direction (2026-11-09): "a dark dungeon with flames". Built directly in Unreal as an opt-in arena on branch `arena-design-01`, around the unchanged fight floor. The earlier ivory **Court of the Last Witness** Blender draft ([ARENA_DESIGN_01.md](ARENA_DESIGN_01.md)) is preserved as a separate studio study.

## Play it

```sh
BOSSLAB_ARENA=dungeon BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

Editor-game only (`play`, `capture`, `benchmark`, `test`); package modes reject `BOSSLAB_ARENA=dungeon`. Omit it for the original arena. `BOSSLAB_OUTFIT` is independent (original costumes work too).

## What it is

- **Fight space unchanged.** The floor (R14 m), the 32 parapet blocks (R13.6 m, 2.6 m high) and the 8 pillars keep their transforms and `BlockAll` collision; only their materials change. Every added component is `NoCollision`, so movement, camera collision, lock-on and combat behave exactly as in the original arena.
- **Hall.** A 13.5 m masonry ring wall at R15.6 m with 16 piers, a cornice, pointed arches between piers, ribs rising to a dark ceiling, and barred cells in alternate bays. All of it is outside the parapet or overhead.
- **Fire.** A coal trench burns between the parapet and the hall wall, with flame tongues licking over the parapet. There are great braziers on the 8 pillar tops, 16 wall torches, and an iron candle chandelier over the centre. Embers rise from the braziers.
- **Light.** The sun and fill directional lights are switched off.
  - **Fighter key:** one shadowed downward spot from the chandelier pools warm light on the duel. It is the only shadow-casting light.
  - **Fire:** 8 unshadowed brazier lights and 8 short-reach torch lights. All lights flicker at presentation time.
  - **Ambient:** a faint cool sky fill keeps dark costumes readable against the warm fire.
  - **Atmosphere:** height fog, vignette and bloom.
- **Floor.** The bronze inlay rings at R3.6 m and R12.1 m are kept.

## Assets and pipeline

- **Textures.** CC0 [Poly Haven](https://polyhaven.com) 2K maps (diffuse, DirectX normal, AO/rough/metal):
  - `cobblestone_pavement` for the floor;
  - `castle_wall_slates` for the walls;
  - `castle_wall_varriation` for the piers and pillars.

  They were downloaded to `artifacts/art/arena-dungeon-2026-11-09/textures/` (about 23 MB, local and not committed). Fetch them again with `https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/<name>/<name>_{diff,nor_dx,arm}_2k.jpg`.
- **Materials.** Built by `./scripts/bosslab-unreal python unreal/art-studio/source/arena/ue_import_dungeon.py` into `/Game/BossLab/Dungeon/` (about 22 MB, local and not committed, like the Revamp assets).
  - **Stone:** world-projected stone, top-down on floors and along the wall on vertical faces, so scaled engine cubes tile at a fixed real size. It has a matching world-space normal frame. Pillars use a cylindrical wrap (`M_DungeonColumn`).
  - **Flame:** `M_DungeonFlame` is an unlit additive card with 4-octave procedural noise fire, desynchronised per instance. There is no texture and no particle system.
- **Code.** [WardenDungeon.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenDungeon.cpp) contains `BuildDungeon` and `AnimateDungeon`. `DressArena` selects it with `-BossLabArena=dungeon`. Flicker and embers run on game-mode Tick and never touch the fixed combat step.

## Verified (2026-11-09)

- **Tests.**
  - The default native suite passes **22/22**: the original 21, plus the new `BossLab.Arena.DungeonIsPresentationOnly`. That test confirms the dressing adds 0 colliding components and no raised geometry inside the wall line below 4 m, that a collision block keeps its transform and `BlockAll`, that materials load, and that lights and embers exist. It reports 921 scenery instances and 17 flickering lights.
  - `RevampTrial` passes 1/1 with the dungeon enabled.
- **Captures.** Actual 24 s exchange captures (fixed 30 fps) were inspected:
  - `exchange-sheet.png`, `gameplay-frame-250.png`, `gameplay-frame-470.png` (final);
  - `early-iteration-dark-frame.png`, `rejected-too-dark-sheet.png` (rejected lighting passes, kept for reference).
- **Performance.** This was a shared machine: load average 40–110 from other apps (Chrome, Bluetooth, the animated wallpaper, indexing). Results are 720p, performance preset, revamp characters, back to back:

  | Run | Mean | p95 | Approx. FPS |
  |---|---|---|---|
  | Dungeon | 26.40 ms | 48.73 ms | ~38 |
  | Original arena | 18.35 ms | 25.82 ms | ~55 |

  Reports: `benchmark-final-{dungeon,original}.json`. Diagnostic runs showed nearly all of the extra cost is the dynamic lights. With lights removed the dungeon matched the original arena (17.8 ms). The flame cards cost about 3 ms. Two changes cut the cost: removing 8 cube-shadowed brazier lights (48 shadow views per frame) and stopping scenery from casting into the key light's shadow. This is not isolated and makes no 60 FPS claim.

## Props and souls-style pass (2026-11-09, later)

Owner asked for more props, more refinement and a more souls-like feel.

- **Modelled CC0 props** from [Poly Haven](https://polyhaven.com), about 50 MB of glTF in `artifacts/art/arena-dungeon-2026-11-09/props/` (local):
  - `gothic_statue`, `large_castle_door`, `large_iron_gate`;
  - `kite_shield`, `ornate_medieval_mace`, `ornate_war_hammer`;
  - `brass_candleholders`, `rock_moss_set_01`.

  `antique_estoc` was downloaded and prepared too, but nothing places it yet.

  The project disables engine plugins by default, so Unreal has no glTF importer. [prep_props.py](../unreal/art-studio/source/arena/prep_props.py) therefore converts the props in project-local Blender:
  - joins parts and sets each pivot at the base centre;
  - decimates the heavy pieces (gate 38k to 20k triangles, candelabra 32k to 12k, rocks to 4k);
  - exports FBX plus a material-to-texture map.

  [ue_import_props.py](../unreal/art-studio/source/arena/ue_import_props.py) runs in editor mode. It imports at 100× scale (Blender metres; at 1/100 scale the importer's vertex weld collapsed thin parts) and deletes the folder first, because a replace import reuses the old scale. It builds one PBR material per texture set; glTF normal maps are OpenGL, so their green channel is flipped.
- **Layout.** The front of each prop faces +Y, so yaw = bay angle + 90° turns it toward the arena.
  - **Doors:** bay 0 (+X, behind the boss) holds a sealed great door in a stone portal. Bay 8 (−X, the entry) holds the same door behind a fog wall.
  - **Cells:** even bays hold iron-gated cells; bays 4 and 12 are collapsed into mossy rubble.
  - **Statues:** odd bays hold 3.2 m guardian statues on plinths, with a dropped shield and mace or war hammer.
  - **Candle shrines:** sit on the parapet top in front of each statue.
  - **Banners:** every bay has a tattered banner on an iron rod.
- **Procedural materials:**
  - `M_DungeonBanner`: masked dark wool with a weave, soot, a torn hem, moth holes and a slow world-position sway.
  - `M_DungeonFogGate`: translucent swirling mist. Colour and opacity are separate custom nodes; a float4 split through component masks left opacity unconnected, so the wall rendered opaque.
  - `M_DungeonShaft`: an additive cone that fades by world height.
  - `M_DungeonDust`: dim unlit motes.
- **Light and grade.**
  - **Key light:** now cool moonlight (2,000,000 unitless) through a ceiling oculus, still the only shadow caster, with a visible shaft and 90 drifting dust motes.
  - **Braziers:** reduced to 60,000.
  - **Grade:** muted (saturation 0.86, contrast 1.12, cool shadow gain, grain 0.18, bloom 0.75).
- **Capture.** `./scripts/bosslab-unreal capture tour` is a new capture-only mode: the motion-study setup with the camera yawing 1.6° per frame, pitched up 10°.
- **Mistakes found by inspecting captures and fixed:**
  - banners and fog wall rendered edge-on;
  - opaque fog wall;
  - materials looked up in the wrong folder;
  - rock roughness sampler type;
  - glare from close braziers;
  - oversized dust.

### Verified

- **Tests:** the default suite passes 22/22. `BossLab.Arena.DungeonIsPresentationOnly` reports 1,030 instances, 17 lights, 0 colliding and nothing raised inside the wall line; additive light effects and sub-5 cm motes are excluded from that check. `RevampTrial` passes 1/1 in the dungeon.
- **Captures inspected:** `props-tour-sheet.png`, `props-tour-frame-{023,046,115,161}.png`, `props-exchange-sheet.png`, `props-gameplay-frame-250.png`.
- **Benchmark:** 720p, performance preset, revamp characters, back to back, with load average about 12–17 (much quieter than the earlier runs):

  | Run | Mean | p95 | Approx. FPS |
  |---|---|---|---|
  | Dungeon | 18.17 ms | 25.48 ms | ~55 |
  | Original arena | 16.70 ms | 16.77 ms | 60 |

  Reports: `props-benchmark-{dungeon,original}.json`. This is a shared machine, not isolated, and makes no locked-60 claim. Most of the earlier 26 vs 18 ms gap was machine load.
- **Storage:** one capture was stopped by the 24 GiB reserve guard. Work resumed after the owner freed space.

### Remaining limits

- The fight camera rarely shows the banners, ceiling or entry fog wall; the tour capture does.
- The arch struts are still straight primitive beams, and the braziers are cones.
- The props are generic CC0 pieces, not bespoke to the Regent. The statue reads golden in firelight.
- The fog wall is decoration only, with no gate behaviour.

## Limits and next steps

- **Light cost.** The remaining cost is about 8 ms, from the 17 lights. The options trade look for frames:
  - light only 4 of the 8 braziers;
  - bake the static wall lighting into the stone material as emissive or vertex colour;
  - add a quality preset that drops the torch lights.
- **Geometry.** It is primitive-based: engine cubes, cylinders and cones with real stone textures. The arches are straight struts, and the braziers are a cone with a rim. Modelled props (braziers, sconces, arches, chains) would be the next quality step, through the image-to-3D pipeline or free CC0 models.
- **Fire.** The flames are crossed cards. They read well from gameplay height but are visibly planar from above, and there is no smoke.
- **Unseen in gameplay.** The ceiling and chandelier sit high, and the default gameplay camera rarely shows them.
- **Behaviour.** Collision, camera and lock-on behaviour are unchanged by construction, and the native test checks this. Near-wall camera framing in the new look was not separately reviewed.
