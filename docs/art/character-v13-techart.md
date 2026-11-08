# V13 static character construction delivery

This is a separate static Blender studio assembly. No game, boss AI, rig or combat changes. V10 remains the preserved full-character fallback; V12 remains the preserved geometry/texture study. No failed V9 cloth solve or V11 concept-projection scene is imported.

## Implemented milestones (not final acceptance)

- Actual tapered hollow cuirass, sternum keel/side fields, thinner swept shoulder plates and fitted three-part gorget. Seven real seated studs and a surface-sampled pointed-arch reliquary frame replace a failed penetrating triangle-fan field.
- Full-character assembly from V10 with declared fitted doublet, shoulder-pose adjustment, collar replacement and common steel preview. Existing generated V12 steel image is packed, explicitly object-space box mapped; this is neither a clean UV delivery nor calibrated PBR. No concept image is projected.
- Closed sewn collar with compressed ends, shallow seam valleys, actual stitches and grouped curved fibers. Earlier shelves/flotation-ring trials are preserved. Current fur still reads as coarse fringe, not target-quality fur.
- Dorsal-plane/tapered forearms and shield-shaped elbow/knee cops replace initial bean-like failed variants. Forearm end disks were removed to make actual hollow sleeves. Joint centers and hand size remain unchanged in these milestones.
- Static authored split wool panels, unequal hems and broad folds; retained cape and all its seams receive a common flank/length warp. No cloth simulation or motion validity claim. Actual upper mail attachment is fitted inward under the belt; covered thigh straps/buckles remain preserved hidden objects. Abrupt mail envelope and embedded hardware failures are preserved; context08 resolves the conspicuous protrusions in the inspected garment view.
- Actual overlapping dark leather ribbon on Oathwake; flat swept terminal plates replace round buttons. Blade shoulder transitions are chamfered into the ricasso. Existing lower blade/tip, tang, grip/pommel endpoints, repaired-fracture and seven-oath lore are preserved. No new ornament lore invented.

## Evidence and reproducibility

Source: `unreal/art-studio/source/last_vigil_v13.py`; guarded launcher: `scripts/bosslab-art-v13`. Each heavy launch records a timestamped exact source snapshot, log and process receipt under `artifacts/art/last-vigil-v13`. Context images are explicitly versioned, not overwritten to hide failures. Current canonical working scene is `unreal/art-studio/revision-v13-2026-11-07/last-vigil-v13-context.blend`.

Context01–08 represent progressive, sometimes rejected, assemblies; they are not a mixed final gallery. Context07 garment has known mail breakthrough and is failed evidence. Context08 fixes that transition. The fractional-power context04 failure receipt is retained. Guards remain 10 GB total under Unreal and 24 GiB free, CPU foreground only. No external download or new generated image was needed for V13.

## Outstanding at the earlier checkpoint

Active refinement continues: head/gauntlet construction review, coherent final same-scene views, saved-scene scoped clearance/material/provenance readback, final source/scene hashes, and independent QA preservation. Current control-point ray gap numbers do not establish whole-triangle intersection freedom, animation clearance or production topology. No overall reference-quality, runtime-ready, clean UV, physics or game-performance claim.

## Historical resource stop: saved context12, prepared context13

The current saved scene is context12, SHA-256 `1d3deca502d7ff634fa0ed106268ede8eb2c4aaebecaec0e185917a125b1fa41`. Its exact construction source is `artifacts/art/last-vigil-v13/context-1794047661.py`, SHA-256 `96305b01764038b1fa9d8abb2ded5f3174c1a968a49c69de37368017ca34297d`. Current editable source contains **unrendered context13**: a longer, smoothly bounded lower-mail envelope transition intended to remove remaining cloth ledges. It does not reproduce the saved scene until that new build is run. No final freeze is claimed.

Context09–12 added actual three-part metacarpal plates, measured rigid reseating of inherited dorsal finger plates, continuous swept quillons (replacing separate terminal plaques), and a modest monotonic crown taper. The palm remains simplified; metallic finger shell response remains subdued. A visible oval behind the palm was ray-identified as the field pouch intersecting the cape, then corrected by a broad upper side-return constraint. This introduced a conspicuous cape leading-edge kink that remains a review concern. The cloth has residual shelf-like constraints, coarse mantle fibers and heavy smooth fabric; reference-quality realism is **not achieved**.

During context12, free space fell from26.093GB to25.020GB, below24GiB. The wrapper attempted termination but `os.killpg` returned `PermissionError`; an immediate escalated process inventory confirmed no Blender or launcher remained. Child log ends `Blender quit` and four requested images exist, but the wrapper failed and this is **not a successful guarded run**. Context13 was then blocked at preflight (24.998GB free). No further heavy processes launched. Exact receipt: `artifacts/art/last-vigil-v13/context-12-reserve-stop.json`; it records hashes, source/scene mismatch and actual process outcome. Last measured free24.996GB; Unreal4.2277GB.

Next action after headroom returns: inspect the known cape kink and cloth constraint transition in source, run `./scripts/bosslab-art-v13 context garment` behind the unchanged reserve guard, inspect actual result, then produce coherent final views and saved-scene audit. The audit/final-render code is prepared but not yet run. No large checkpoint copy was made below reserve. Parent owns status/checkpoint and user communication.

Launcher follow-up: the denied-signal error path now always records the owned child PID/process group, each signal result and whether the child still appears live. It explicitly requests process inspection if termination was denied; it does not bypass permissions or report a false stop. The original launcher is preserved as `launcher-before-signal-receipt-fix.py`. Two mocks executed the actual parsed exception-handler code (denied signal/live child, already-exited child):2/2 passed without spawning a process or sending a signal. Python syntax checks passed. Evidence: `launcher-signal-handler-mock.json`. No further Blender launch was attempted.

## Recovery checkpoint: context13 now built and singly inspected

Free space recovered externally to26,041,286,656bytes; parent authorized only one guarded CPU garment probe. `./scripts/bosslab-art-v13 context garment` completed exit0 in14.55s, no signals, afterfree26,040,242,176bytes. Actual `context-13-garment.png` shows softer broad mid-thigh transitions; residual hem notches and heavy smooth cloth remain. This does not constitute final multiview or artistic acceptance.

Canonical scene is now context13, SHA-256 `8c07abf17315b3ba3523d44700299dc9196b80306230c8573e0af2b6b80df8f4`. Exact source and timestamp snapshot `context-1794048084.py` both SHA-256 `f731799d34fc1ae9c9c70fbc798e6c84521fd561f842bcb922b1722fd7a1a866`. Scene/source mismatch is resolved for this build. Historical context12 stop/source/render evidence remains unchanged; do not use its old canonical-scene hash as the current scene identity. New receipt: `context-13-recovery-checkpoint.json`.

Next: independent review of the actual garment correction, then permitted same-scene final views and saved-scene readback under fresh guards. No final freeze, broad render or large archive has occurred at this checkpoint.

## Superseded interim context13 evidence and verification

All11 canonical images are freshly rendered from the same saved context13 scene: `final-hero.png`, `final-front.png`, `final-side.png`, `final-back.png`, `final-head.png`, `final-hand.png`, `final-palm.png`, `final-hilt.png`, `final-garment.png`, `final-clay-front.png`, `final-clay-side.png`. Every image is720×920,16samples; nine material views and two neutral-clay proofs. No1400 image or motion sequence is part of this delivery. The entire batch completed exit0 in85.04s with the reserve intact. Saved-scene readback completed exit0 in2.14s. No heavy helper remains after completion.

Actual readback:143 visible control meshes,170,009 control vertices,166,984 control faces; all control coordinates finite. These exclude curves and are **not evaluated triangle/runtime counts**. Packed steel image and actual BOX projection wiring are recorded. Actual evaluated camera matrices are recorded after view-layer updates. Source/scene hashes remain `f731799d34fc1ae9c9c70fbc798e6c84521fd561f842bcb922b1722fd7a1a866` / `8c07abf17315b3ba3523d44700299dc9196b80306230c8573e0af2b6b80df8f4`.

Current cloth control-point ray envelopes:0 infeasible body/tasset intervals; left/right body-front minimum6.000/10.007mm and tasset-back minimum9.506/8.585mm. These are construction constraints, not all-triangle collision tests. Actual cape control minimumZ0.100065m; collar control width358.864mm. Counts/bounds do not validate cloth simulation, animation, anatomical clearance or production retopology. The broad cape return was corrected after a ray hit identified the pouch intrusion. Remaining silhouette kinks and rigid upper cape attachment are disclosed, not hidden by a numerical pass.

Final outcome: a substantial static construction/material-hierarchy increment over the preserved assembly, including fitted chest/shoulders/gorget, real reliquary mounting, coordinated limb/joint armor, longer layered textile silhouette, improved hilt and dorsal hand construction. **Still below the approved concept and supplied realistic reference.** Cloth remains heavy/smooth with residual hem notches, cape upper attachment is rectangular, fur looks coarse/brushed, palm/fingers remain simplified, and metal is not bespoke production-painted PBR. Further scripted density/ornament tweaks would not honestly close this sculpt/garment/groom-authoring gap. No AI, rigging, Unreal import or game acceptance is claimed.

Reproduce construction with `./scripts/bosslab-art-v13 context`; reproduce canonical renders with `./scripts/bosslab-art-v13 context-final hero front side back garment hand palm head hilt clay_front clay_side`; reload audit with `./scripts/bosslab-art-v13 context-audit`. Dependencies are preserved V10 full scene, V13 focal attempt04, and packed original V12 generated steel asset. No concept texture or failed V9 solver is imported. Exact hashes and canonical files are in `artifacts/art/last-vigil-v13/techart-delivery-audit.json`. Parent owns final gallery and project checkpoint; independent QA owns preservation checks.

## Final cape attachment correction (context16)

The context13 freeze was explicitly retracted before project delivery. Its11 images were moved without duplication to `interim-context13/`, with a superseded manifest. Context14 softened the side-return constraint but exposed tall unsupported upper tabs; context15 fitted the top row to the collar arc, exposing a pale patch. A real scene ray identified that patch as the new cuirass (world−0.146842,0.069178,1.521136m). Context16 added a smooth upper rear-shell envelope, removing the actual overlap without repainting the patch. Its back and side views were inspected and independently accepted as a local attachment correction, not an artistic pass.

Final cape construction uses a bowed, narrowed yoke blended into the first150mm of cape, seated below the collar; a broad smooth side return stays behind the pouch and replaces the prior dogleg. Lower length/silhouette is retained. Source-cloth, bound edges and seams receive the same warp. No physics/rig validity is implied. Context16 is now the canonical saved assembly; all final images/readback are regenerated from this same version. No image from context13 is silently reused as context16 evidence.

## Definitive frozen delivery: context16

All11 `final-*.png` images have now been regenerated from context16,720×920/16samples, in one successful guarded batch (exit0,126.61s). The saved-scene audit then completed exit0 in4.22s. The earlier context13 counts happen to remain unchanged because the final correction only moved cape/edge vertices:143 visible control meshes,170,009 vertices,166,984 faces, all finite. These remain control counts, not evaluated triangle counts. The upper cape rear-shell constraint sampled877 mesh/curve points, maximum correction30.905mm; this is a scoped envelope correction, not universal intersection certification.

Definitive source SHA-256: `503d9daf84854e0249cd4782c97c5ca21ddb66bef4d5432f7628cb171b644ce7`.
Definitive scene SHA-256: `2457b527d43ceea7bf94f16d3fb15fcda230a302253956c36d9c2cbd4ed00839`.

The previous exposed rectangular cape top and sharp side dogleg are superseded by the reviewed curved attachment/continuous return. Remaining sparse folds, heavy cloth, hem irregularities, coarse collar fringe, simplified hands and preview-metal craftsmanship still prevent a reference-quality pass. No further geometry or surface changes are planned for this frozen increment. Last guarded readback free25,988,579,328bytes, Unreal4,227,735,552bytes. Parent should prefer a lightweight manifest checkpoint rather than duplicate large archives given narrow headroom.
