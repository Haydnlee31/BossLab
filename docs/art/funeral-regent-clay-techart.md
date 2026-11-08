# Funeral Regent weighted clay study — rejected construction gate

2026-11-09. Actual Blender implementation, saved scenes and renders completed; **the asset does not pass the selected B construction/pose gate**. Initial attempt plus two targeted corrections exhausted. No fourth correction, material expansion or game integration. Existing player/game assets were not edited.

## Actual delivery

Source: `unreal/art-studio/source/funeral_regent_clay.py`. Guarded launcher: `python3 scripts/bosslab-funeral-clay 3`. This reproduces the final rejected study, not a recommended production build. Editable scenes: `unreal/art-studio/funeral-regent-clay-2026-11-09/regent-attempt-02.blend` and `regent-attempt-03.blend` (latest two retained; attempt01 scene pruned with hash receipt after final readback, all its stills/source/log retained). Evidence/source snapshots/process receipts: `artifacts/art/funeral-regent-clay-2026-11-09/`.

The final scene contains a real 19-bone armature, 46 armature-modified mesh objects and seven keyed pose snapshots: idle1, anticipation21, fullcast41, reel61, release81, thrust101, miss121. Frames are pose identifiers, **not approved combat timings or validated interpolation**. Four long cloth panels have normalized spine/panel-control blends; other shells have localized weights. Three skull cores and visual-only chain/hook paths exist. Chain snapshots use keyed visibility and are not a continuous rope simulation or gameplay authority. No flames obscure the clay evidence.

Final nine640×800 renders: idle front/side/back; anticipation, fullcast, reel, release, thrust and miss three-quarter. All are in `attempt-03/`. Attempt01 has three neutral renders; attempt02 has nine actual renders. All failures remain. No external assets/downloads, physics simulation, Unreal changes or AI work.

## What failed and why

- Attempt01 exposed disconnected limb shells, floating oval boots, absent hood, ladder-like ribs and narrow straight cloth strips. It was rejected rather than promoted to detail work.
- Attempt02 added hood/nape, curved ribs, a voxel-union underbody and posed chain paths. However proximity weights confused nearby arm/thigh regions, producing stray deformed anatomy. The open source limb shells were unsuitable union inputs. The script saved/rendered all nine views but exited1 during manifest creation because a deleted joined object remained in a Python list. Its log/receipt is retained; this was a reporting failure as well as an artistic failure.
- Attempt03 corrected anatomical handedness using a whole-character X-reflection parent (negative determinant is explicit; not a production applied-transform export), constrained arm weighting and hid intersecting duplicate shells. This exposed missing lower-arm volume. The supposed connected union has **19 connected components**, not one. Hands remain visibly detached. The label `connected weighted anatomical underbody` describes the intended construction and must not be mistaken for a passed result.
- Mask changes produced dark underlayer intrusions rather than convincing nose/cheek planes. The long mantle remains narrow separate strap/curtain masses, insufficiently wrapped over shoulders/flanks. Skull proxies are generic, not detailed bone anatomy.
- Boot subdivisions leave the evaluated sole7.222mm above the ground in every sampled pose. There is no planted-foot pass. Visible pose changes do not prove acceptable anatomy, deformation, balance or transitions.

This failure is in the current authoring method, not evidence that Blender cannot make the character. A fresh construction approach needs closed, explicitly connected anatomical cages with deliberate deformation loops; a sewn wraparound mantle pattern with side gores; and a mask constructed from real facial planes. Do not resume with more ornament, voxel density or shader noise.

## Saved readback and limits

Final guarded run exited0 in51.90seconds including nine renders and reopening the saved scene. `attempt-03/reload-audit.json` records actual saved-scene identity, each weighted control mesh's component count and normalized weights, seven bone matrices and evaluated foot minima. Maximum weight-sum error2.98e-8, zero unweighted vertices on the audited meshes. These narrow integrity results do not override the19-component underbody, missing forearms or visual rejection. Hidden duplicate shells remain editable in the scene and are included in the46-object weight count; this is not a count of all visible assets.

No full mesh collision, runtime scale/retarget, animation transitions, material, performance or production topology tests were performed. Source coordinates are meters and generic proportions; current boss skeleton/capsule has not been imported or fitted. The handedness reflection makes left reel screen-right in front view, but still requires proper applied-transform handling before any future export.

Post-run storage:26,742,763,520bytes free (above unchanged24GiB reserve);2,741,444,608bytes under Unreal (below10GB). CPU two threads; all owned child processes exited, no persistent jobs. Independent art/QA review requested. Exact hashes and file list are in `delivery-manifest.json`.
