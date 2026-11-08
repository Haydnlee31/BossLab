# Character V3 QA — 2026-11-07

Owner: qa-balance. Task QA-03. Independent read-only art/evidence review; only this report and optional final-check JSON are QA-owned. No source edits, Blender/game launches or heavy tests. Inputs: latest status/plan/decisions/claims, QA role guide, actual V2 clay/material evidence, and the owner-approved generated concept target. The concept is visual direction only, not built geometry or a quality result.

## Initial verdict

**Needs work — final V3 clay/material/mask views reviewed.** Owner resumes implementation. Existing coherent mesh improvements are preserved, but the V2 baseline remains below the approved realistic target. Boss AI, rigging/motion and gameplay integration remain outside this art increment.

## Three highest-priority findings routed to art/tech-art

1. **Helmet plate form:** actual V2 clay shows broad polygon bands, a flattened crown cap and globe-like lower face. Shape continuous curved plate fields between intended crown ridge/cheek breaks. Preserve front-only eye aperture and fitted neck overlap; compare side and three-quarter clay views before materials.
2. **Glove anatomy:** actual V2 clay has a padded broad palm and cylindrical fingers with simplified root/web transitions. Author wrist narrowing, an unequal knuckle root arc, thenar saddle and finger taper. A connected manifold mesh is necessary integrity evidence, not convincing anatomy by itself.
3. **Localized material sample:** author one verifiable steel/leather/wool region with appropriate UVs and intentional masks. Steel polish at contact edges and grime in recesses; leather compressed around seams/fastenings. Global mottling, more surface ornaments or darker lighting do not close the target gap.

## Acceptance and evidence boundaries

Inspect actual V3 clay/material views, with comparable light and adequate framing. Confirm local targeted defects separately from overall artistic quality. Do not require another expensive full-body render loop before focal construction is sound. Report unchanged regions honestly.

Separate three levels of evidence:

- Mesh integrity: finite coordinates, connectivity/manifold checks and known topology limits. These do not prove anatomical or deformation quality.
- Actual surface quality: visible form continuity, construction, scale and material response in rendered clay/material samples. This is visual assessment with identified view scope.
- UV/material implementation: actual UV layer, mask/image/channel identities and mapping evidence. Packed images alone do not prove useful UV layout or localized wear; source/audit and actual result must agree.

Generated concept, static studio render, simulated cloth, rigged motion and real-time gameplay remain distinct. No rig, motion, runtime FPS, boss AI or training claim can follow from this pass. No new combat/frame-data/balance test is appropriate without gameplay changes. Preserve prior evidence and the existing28-file game hash baseline; perform final storage/preservation checks only after source freeze.

## V3 review log

Review history follows. Final scoped result is below; no overall art pass is claimed.

### First V3 focal probes

Inspected actual720×920 `head`, `clay_head`, `clay_headside`, `palm`, `clay_palm` images in `artifacts/art/last-vigil-v3/`. Crown/jaw fields are smoother and the earlier transverse palm roll is reduced. Two priority construction/continuity issues remain before the localized material sample:

- Clay side shows a wavering thin raised/slivered edge extending down from the temple hinge. It reads as unintended overlap/edge continuity, rather than a clean attached plate seam. Route to animation-techart for source/topology diagnosis; image alone does not identify its precise cause.
- Distal palm roots still form a nearly straight ledge with square patchy knuckle-pad transitions. Requested an unequal smooth root arc and saddle rather than a hard horizontal band.

Both were sent to the artist and producer. Broader anatomical/forged-form quality remains unaccepted. Materials were intentionally unchanged for this form review; no UV/material result yet claimed.

### Initial localized material sample audit

Read shader and UV authoring source without editing it. Image Color outputs feed Principled Base Color/Roughness; relief feeds Bump Height and then Normal. Per-loop UVs are authored, but initial image Vector inputs were unconnected and relied on the active render UV. The glove could retain an inherited UVMap, so writing a new layer and packing images alone was insufficient proof that the intended coordinates were sampled. Tech-art identified that inherited-layer issue and reports adding an explicit `ShaderNodeUVMap` named `Authored sample UV` to every image Vector input; re-render/link audit pending.

Initial actual head/side/palm views read as almost uniform black metal and flat brown leather. Artist also identified misplaced cuff stitches and scratches in rear UV sectors, now correcting coordinate placement. QA requested a mask-on-mesh diagnostic and link/active-layer evidence, then a modest steel value/roughness correction under unchanged lighting. Final assessment must use corrected actual views, not the presence of map files.

The current UV coverage implementation rasterizes the union of projected triangles and clips to one tile. This is finite/occupied mapping evidence only; it does not establish no overlap or distortion. Glove planar projection overlaps dorsal/palmar areas and compresses side edges; it remains a localized sample, not a production unwrap/atlas.


## Final V3 review after source freeze

Inspected all11 actual final720×920 views: hero; material head/headside/hand/palm; clay head/headside/hand/palm; mask_head/mask_palm. Final image identities are in [character-v3-qa-final-check.json](character-v3-qa-final-check.json). **Local form and mapped-material progress verified; overall realistic-art verdict remains needs work.**

Observed corrections: crown/cheek shading fields smoother, wavering temple sliver reduced to a clean plate boundary, front-only eye opening retained, and the palm transverse roll/notches softened. Palm/finger-root anatomy remains simplified and the helmet remains broadly rounded; these are improvements, not final anatomical or forged-form acceptance.

The final mask-on-mesh views visibly place steel rim/recess masks along the helmet opening/lower plate bounds and selected scratches on front-facing plate fields. Palm diagnostic places contact over thumb/index/pads, a crease region across the palm and a dotted side-seam stitch mask below the cuff. In actual material views the helmet is readable steel rather than the initial nearly black field, sparse scratches are faintly visible, and a small stitch line is visible on the glove. Local wear and material character remain understated/simplified; the result does not match the approved concept's craftsmanship. Diagnostic colors are channel visualization only, not final artistic material.

Read-only source inspection confirms `ShaderNodeUVMap('Authored sample UV')` explicitly feeds image Vector inputs; color and roughness feed their Principled inputs and relief feeds Bump/Normal. The reloaded-scene audit reports the named layers/nodes and eight packed authored1024 maps. Thus this is actual coordinate-driven sampling, not merely map file presence. Geometry audit reports ten packed images total, including two inherited original maps; do not call all ten newly authored V3 maps.

Limitations are substantive: glove projection overlaps front/back and compresses side edges; audit reports997 left and993 right degenerate projected UV triangles and about50.99% occupied-grid union. Helmet fields are cylindrical/periodic, not unique production UV islands. These numbers are disclosed sample limits, not a successful production unwrap or distortion test. No wool material sample was implemented; existing cloth remains unchanged. Static glove topology audit reports20854 vertices per glove, one component and no non-two-face edges; QA read this producer audit without rerunning Blender. It is not skinning/deformation evidence.

Remaining priority: deliberate helmet silhouette/cheek construction, glove knuckle/web shaping, then production-aware localized materials and broader mantle/cloth work. The unchanged coarse mantle, generic large armor forms and old surrounding material variation continue to limit the assembled character. No more ornament or darker lighting should be used to imply a quality pass. Owner concept approval is still distinct from built-model acceptance.

Final independent lightweight checks: **28/28** game source/config/binary hashes and **111/111** selected immutable V2 source/scene/evidence hashes match their prior baselines. Unreal directory **2,901,815,296 bytes**, free disk **28,341,686,272 bytes**, within unchanged10GB/24GiB guards. No gameplay tests were rerun because gameplay is unchanged; no rig, motion, runtime FPS, boss-AI, training or model connection claims. QA files frozen for checkpointing.
