# Keeper of the Last Vigil — original 3D character study

Owner rejected the first runtime polygon costume and requested a realistic, richly constructed character based on the supplied armor/cape references. This study is an editable Blender asset, separate from the preserved Unreal build. Studio renders are actual geometry/material renders, not generated concept images or gameplay evidence. Artistic acceptance is not implied by geometry counts or technical checks.

## Character and material language

The keeper was a sanctuary custodian before becoming its last guard. Fitted blackened steel and worn silver relief preserve the ceremonial origin. A narrow waist, articulated fauld/tassets, split surcoat, mail, leather retention straps and a field-repaired pouch give the equipment a plausible construction order. Tarnished electrum is reserved for fastenings, memorial details and the oath motif. A short silvered fur collar softens the helmet/shoulder transition. The long wine-colored cape carries a seven-lantern tree and worn thread borders.

The references inform layered construction, weathered material contrast and the importance of the rear silhouette. Their pixels are not textures in this asset. No armor mesh, texture library or external character asset was downloaded.

## Oathwake — lore expressed in construction

Seven keepers swore to keep the sanctuary gate. When the Warden turned against them, the last keeper broke the sword inside the gate's locking seal. The blade was later reforged around that fracture rather than ground back to pristine steel.

- Seven small gate-shaped oath marks lie along a recessed fuller.
- A thin electrum-brazed fracture crosses the blade above the marks.
- The incomplete reliquary ring is structurally attached behind the swept crossguard; its missing segment was left inside the seal.
- Lantern-shaped quillon terminals and a fluted pommel repeat the sanctuary motif.
- A long leather-bound grip with narrow ivory splints makes the two-handed construction explicit.
- Bright cutting bevels contrast with the darker forged blade and etched shoulder ornament. This is a ceremonial weapon maintained for use, not a uniformly glowing prop.

This is original fictional lore and design, not an assertion about the reference game's equipment.

## Authoring and revisions

Project-local official Blender4.5.15 LTS, Apple Silicon. Installer checksum and application signature verified; installer removed after extraction. No global installation or background service. All modeling tools and sources count under the unchanged10GB allowance; the24GiB free reserve is enforced by `scripts/bosslab-art`.

The first studio render exposed overly round joints, an elongated exposed neck, incorrect boot coverage, overly bright metal and insufficient garment layers. Subsequent renders corrected these and added shaped joint wings, rolled plate edges, retention straps, a split surcoat, repair stitches, memorial tags and a layered fiber mantle. Close-ups exposed floating shoulder relief, stretched blade material coordinates and satin-like cloth. Corrected surface placement, physical texture coordinates, matte fabric response and localized hem abrasion; added modeled acanthus leaf relief rather than relying solely on drawn lines.

Original procedural steel/leather/weave shaders and original raster embroidery/abrasion maps are packed in the editable scene. Full production UV atlases, sculpt/bake workflow, retopology and gameplay LODs remain separate work. Surface patterning is procedural, not hand-sculpted scan detail.

## Cape and movement scope

The cape has3,185 simulation vertices, shoulder pinning, body collision proxies and self-collision. A bounded authored root turn tests cloth inertia/folding. The first wrapped study exposed greave breakthrough and startup edge stretch up to1.77993×. Added hidden lower-body collision stand-ins and fitted the initial cape pattern outside the upper sleeves. The same100-frame audit now measures maximum1.04549× edge stretch, minimum0.13052m above the floor and maximum0.03245m vertex step; the sampled views no longer show the earlier greave breakthrough. These are measured geometry facts, not a guarantee of zero clipping across combat. The character itself is not walking or performing a new attack in this study: there is no production body rig or skinning here. This does not replace or validate the game's movement, combat animation or cloth performance. Source and actual bake/render evidence are kept separately.

## Working files and commands

- `unreal/art-studio/source/last_vigil.py`: original editable construction script.
- `unreal/art-studio/last-vigil.blend`: material/geometry studio scene.
- `unreal/art-studio/last-vigil-motion.blend`: shoulder-turn cloth study.
- `unreal/art-studio/blendcache_last-vigil-motion/`: baked cloth cache; keep beside the motion scene.
- `artifacts/art/last-vigil/`: actual renders, intermediate views, logs and audit evidence.
- `./scripts/bosslab-art draft`: regenerate the source scene and hero render.
- `./scripts/bosslab-art render front back armor hilt sword`: render review angles.
- `./scripts/bosslab-art cloth`: bake and render the100-frame study.

Do not regenerate over retained final evidence without first preserving it. All heavy jobs run sequentially, in the foreground, with a20-minute deadline and storage checks. A later GPU probe stopped at the24GiB reserve; the unchanged guard terminated it and preserved its files. Verified duplicate BossLab capture frames and round-trip-verified compressed logs restored headroom. CPU rendering is now the default to avoid the observed GPU memory/swap pressure; no guard was weakened. Blender is a modeling tool, not a model inference connection. No AI/RL/training, paid calls or public deployment.

## Technical references

Official [Blender4.5 LTS](https://www.blender.org/releases/4-5/) and [release files](https://download.blender.org/release/Blender4.5/); [cloth cache](https://docs.blender.org/manual/en/4.5/physics/cloth/settings/cache.html), [collision settings](https://docs.blender.org/manual/en/4.5/physics/cloth/settings/collisions.html), [physics disk-cache behavior](https://docs.blender.org/UATEST/manual/en/4.5/physics/baking.html) and [point-cache bake API](https://docs.blender.org/api/5.0/bpy.ops.ptcache.html). Searchable official documentation informed cache/collision setup; direct web-open requests returned errors, so only retrieved excerpts and actual local API execution are treated as verified.

## Acceptance still required

The target is the reference's believable material/construction richness. This study does not establish equivalent production quality. Evaluate the actual silhouette, surfaces, cape and sword before choosing what to integrate. Fingers, cloth attachment/lining, bespoke texture painting, full rig/skin weights and combat-range deformation need further authoring. The current Unreal costume is unchanged; its earlier21/18 tests and59.07FPS result do not validate this higher-detail asset.

## Preserved interruptions

The first final-render run hit the configured20-minute deadline after a large wall-clock stall; actual launcher elapsed time was1530.82seconds before termination. It left41 complete image files (including earlier probe samples). The resume skips existing complete frames and uses the same baked cache; no startup service, auto-retry loop or longer deadline was added. Do not infer continuous active rendering from wall-clock elapsed time.

## Delivered review artifacts and exact remaining gap

The local [review board](../artifacts/art/last-vigil/index.html) contains six final1400×1800 stills, including front/back, armor relief and complete sword/hilt views. All six inspected at full image resolution. [Cape clip](../artifacts/art/last-vigil/cape-motion.mp4):100 unique720×900 frames,30fps,3.333seconds, no audio; independent decoder reads100 frames.25 evenly spaced chronological samples and additional full-size extremes inspected. Cloth motion is modest lag/folding during a rigid shoulder/root turn; no new walk/attack/roll performance is demonstrated.

Final stills/scenes close small shoulder-cap holes and expose the sword's seven oath marks and brazed fracture. Motion clip predates these cosmetic corrections; cape geometry, physics solver and cache are identical. Preserve `pre-final-detail/` for comparison. Six corrected stills were rendered with Metal in116.74seconds; CPU is saved as the default for future scene renders.100 motion frames use CPU rendering. Final evaluated master:795 renderable objects,546458 vertices,985044 triangles,2 packed original raster maps, finite geometry. This is a studio master, not a runtime budget.

The result still falls short of the supplied realistic references. Large plate/helmet forms are generic and symmetrical; repeated relief and procedural mottling read too uniformly. Hands and collar fibers lack convincing anatomical/clump variation; cloth needs richer sewn folds/lining and wear painted around actual use. These are observed art weaknesses, not storage limitations. Next authoring pass should address these at the mesh/sculpt and localized material level before adding more ornament. Production rigging, skin weights, retopology, UV bakes, LODs and real combat-pose cloth tests remain required before game integration.

All28 selected Unreal source/config/binary hashes match the previous playable checkpoint. No gameplay tests rerun because gameplay is unchanged; earlier21/18 test counts and59.07FPS do not validate this asset. Final artifact integrity/checkpoint results: `artifacts/art/last-vigil/final-audit.json`; archive: `artifacts/art/checkpoint-last-vigil-2026-11-06.tar.gz`. Tool/source/scenes fit within10GB and reserve remains24GiB. Open the motion scene with project-local `unreal/art-studio/tools/Blender.app`; retain its cache folder beside it.

A second CPU finish run hit its20-minute deadline after completing100 motion frames and a hero view. Both deadline receipts are retained. Recovered free space allowed an explicit Metal still-render pass behind an additional3.5GB launch-headroom gate; guards remained unchanged. The final corrected pass completed successfully. No service, automatic retry, game rebuild or model connection was introduced.
