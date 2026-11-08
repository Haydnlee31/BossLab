# V11 independent projection-study QA

**Rejected multiview study; V10 remains authoritative.** Scope: one chest/shoulder/collar image-projection study, initial plus at most two corrections. Judge actual reference-view, three-quarter, side and clay views. Separate painted/source-image detail and baked lighting from real geometry, surface response and multi-view consistency. A convincing front image alone cannot pass the asset.

Baseline 160 immutable V10 files and 28/28 gameplay files preserved; [baseline](character-v11-qa-baseline.json). No heavy jobs by QA. Preserve 10GB unreal ceiling/24GiB reserve, no game/rig/AI claims.

Acceptance questions: Does projection visibly improve the intended region? Where does it stretch, repeat or break at silhouettes/occlusion? Do clay views substantiate relief? Does texture contain fixed shadows/highlights that misrepresent material? Is the projected region and source provenance clearly labeled? Preserve failed iterations and stop within bounded trial count.

## Attempt01: multiview failure

Independently inspected actual reference, three-quarter, side, clay-reference and clay-side. Front appearance gains are source-image detail. The clavicle has a large dark gap; three-quarter reveals white untextured backing; side reveals detached shallow slabs and an egg-shaped proxy. Clay confirms the apparent rivets, fur and fabrication relief are not built. Reject as a multiview asset. Correction1 may connect upper chest/collar and wrap shoulder sections; unknown rear coverage must stay honestly labeled, not disguised by stretching the front image. Attempt budget remains initial plus at most two corrections.

## Attempts02–03 and final visual verdict

Attempt02 reference/three-quarter/side, clay-reference/clay-side and UV-reference independently inspected. The clavicle is more connected and source-angle appearance is the strongest of the three, but oblique views stretch source details across shelf-like shoulder layers, expose pale returns and reveal insufficient physical construction. A regular source-view checker proves coordinate placement, not an acceptable unwrap or multiview shape.

Attempt03 reference/three-quarter/side and both clay views independently inspected. Neutral arm-root solids protrude through or occlude shoulder layers even in the front image; side views retain crude returns and stretched imagery. Clay makes these failures explicit. **Reject V11 as a replacement asset. Stop at the initial attempt plus two corrections; no further candidate or PBR conversion is warranted in this bounded study.** V10 remains the authoritative working studio asset.

This particular implementation failed the multiview gate; this is not evidence that image projection universally cannot work. Apparent rivets, engraving, fur, wear and many highlights/shadows come from the approved generated concept image, with baked lighting emitted through the material. They are not newly sculpted detail, relightable PBR surfaces or recovered physical geometry. Source provenance and render labels correctly disclose the distinction. No game/rig/physics/AI claim follows; AI gate remains closed.


## Frozen integrity and limits

All18 actual images across3attempts independently inspected, including3 UV diagnostics. Budget exhausted exactly: initial+2corrections. All manifest file hashes match;160/160 V10 files and28/28 gameplay files remain unchanged. [Final integrity check](character-v11-qa-final-check.json). Final source SHA256 `b88ac36347e4c246256368592654dfbf458be0b657df86e081b7ad7306108ba9`; attempt03scene `ab54fa322ce2537ba485f0f2ebaef6a72aecacbb6f72b94c6552187252a673bc`.

Reload evidence reports15meshes/1073vertices/2090triangles with finite geometry/UV and exact packed source-image bytes; none establishes artistic or physical correctness. Image source is the previously approved generated concept, not a newly built/scanned asset. Physics is off. No DCC/game tests were rerun by QA. Allocated unreal storage 4135428096 bytes; free 28311195648 bytes at final check, within10GB/24GiB limits. No promotion, integration, PBR conversion, runtime or AI claim.
