# V9 armor — independent rigid shoulder construction branch

Status: frozen reviewed local structural gain; overall reference-quality gate remains open. This branch loads frozen V8 directly. It contains the original V8 garment, mail, body, sword and materials; none of the rejected V9 cloth simulations or fitted mail enters it. It is a static studio candidate, not Unreal integration or production rigging.

## Actual change

Retained each upper shoulder cap and replaced the three lower lames with strips sampled from one continuous fitted support loft. Cross-sections derive from the actual V8 sleeve/rerebrace envelope. Nominal strip overlap14mm, sheet thickness2mm, integral lower return2mm. Upper strips sit slightly farther outward than lower strips so overlapped thickness does not occupy the same plane. The front/back boundaries wrap around the upper arm with shorter ends, replacing the former detached scoop/teeth appearance.

Removed exactly12 old lower-sheet/return objects. The old-rivet filter selected no separate rivets in the final build; retained original hardware is hash-identical. Apparent loose/jagged artifacts disappeared with the corrected surfaces, rather than a separately verified rivet deletion. Reused existing shoulder shader/maps and the same local planar UV sampling convention; no new material-quality claim. Body proportions and camera framing were not changed.

## Failed probes preserved

The first direct per-point body-ray fit reproduced sleeve/rerebrace surface steps as jagged plate fields, with old unsupported rivets. It is preserved under `iteration-01-stepped-support`.

The smoother measured loft initially overestimated its outer radius: taking absolute center distance incorrectly included the inner sleeve edge as outer clearance. That result was too bulky and is preserved under `iteration-02-outer-radius-measurement-bug`. Correcting the measurement sign produces the reviewed seated version; this is an actual geometry correction, not a camera or shader trick.

Independent actual clay three-quarter/side and material hero review finds clearer continuous overlap, no prominent jagged fields or detached hardware. The small lower rim opening and repetitive boundaries remain; overall realism is still below the approved target. No broader design loop or surface treatment followed this bounded change.

## Verification scope

Final reload compares retained original character mesh/curve coordinates, material names and transforms with V8, allowing only explicitly removed old plate hardware. Six camera transforms/lenses, root scale and sword digest are compared after dependency-graph updates. Sampled signed nearest-arm distances and the existing cape/body back-envelope check are local static diagnostics, not complete triangle intersections or animation clearance.

Final files/hashes/actual image list and receipts are in `artifacts/art/last-vigil-v9-armor/techart-delivery-audit.json`. The separate rejected cloth branch and portable neutral handoff remain at `artifacts/art/last-vigil-v9` and `unreal/art-studio/revision-v9-2026-11-07/neutral-handoff`; they are not a working garment replacement. No game/FPS, AI, RL, model-server, rig or runtime-cloth change.

## Final evidence and scoped results

Eight actual final views (seven720×920/16-sample, one1400×1800/48-sample shoulder detail), plus two matched actual V8 clay baselines. Reload: 348 renderable objects, 1068040 evaluated vertices, 1941420 triangles; finite,25 packed images. 311 retained original character objects are hash-identical; exactly12 old lower sheets/returns removed and six new lames added. Protected camera/lens/root/sword state matches, and no V9 cloth objects exist.

13,572 evaluated new-lame vertex samples have minimum4.809mm signed nearest-arm clearance; zero below−1mm. This is sampled static geometry, not complete triangle or deformation proof. Cape/body sampled check: 24144 hits, minimum 37.229mm, zero negatives within inherited exclusions.

Reproduce locally with `./scripts/bosslab-art-v9-armor draft clay_shoulder clay_shoulder_side hero`, inspect saved scene with `./scripts/bosslab-art-v9-armor audit`. Project-local Blender and frozen V8/source utilities are the dependencies; no other DCC is required to open this scene.
