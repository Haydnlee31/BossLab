# V12 independent geometry-first QA

**Coarse static geometry gate passed; UV foldover gate failed; overall art needs work.** Initial plus at most two geometry corrections. Matching front/side/back design sheet is reference direction, not built evidence. Chest/shoulder base must pass actual multiangle clay/turntable review before UV/projection scope proceeds. No front-texture illusion or primitive-count quality pass.

Baseline 206 immutable V10/V11 files snapshotted; 28/28 gameplay files unchanged. [Baseline](character-v12-qa-baseline.json). No heavy jobs by QA;10GB unreal/24GiB reserve retained.

Review gates: coherent front-to-side-to-back silhouette and volumes; seated collar/chest/shoulder relationships; plausible plate thickness/overlap without supporting solids protruding; actual clay substantiates claimed relief; source/scene/view consistency. If geometry passes, UV/projection requires separate validation and source/baked-light distinction. No rig, physics, Unreal, FPS, AI or production-quality inference.

## Initial clay candidate

All five actual views independently inspected: front, side, back, three-quarter and neck. Genuine wraparound torso/back, open armholes and hollow neck improve the V11 shallow-slab failure. No conspicuous neutral support breakthrough is visible. However repeated noisy bands occur across both shoulder stacks in front/side/back, consistent with coplanar/intersecting lames; current clean-overlap gate fails. Correct actual nesting and thickness separation, not texture concealment. This is a useful coarse volumetric blockout, not reference likeness/art acceptance. Actual corrected turntable remains required before projection.

## Correction1 / attempt02 still review

All five actual clay views independently reviewed. Noisy coplanar-looking bands are resolved; connected wraparound torso/back and hollow neck persist. No obvious support penetration in sampled stills. Broad barrel-like chest, rounded oval caps and plain lames are coarse artistic limits, not evidence of broken geometry. A dark open area at the far shoulder top/root is visible in oblique/high views; turntable review must distinguish intentional arm articulation space from a floating cap. No additional correction requested from this isolated observation. Geometry gate remains pending actual turntable.

## Attempt02 technical overlap finding

After the still review, artist ray-parity checking reports 63 lower-lame vertices inside the preceding shell in each of four pairs. This supersedes the absence of an obvious visible break in sampled stills: attempt02 does not pass the geometry gate. Earlier nearest-normal negative signs and the later parity-confirmed overlaps are distinct evidence, not interchangeable failure counts. Final geometry correction03 must recess the full overlap tongues and be followed by actual audit/turntable review; no fourth candidate under the cap.

## Final geometry correction03: scoped base gate passes

Independently inspected five final clay stills and 12 evenly spaced actual orbit frames000,003,…033 out of36. Front/side/back volumes stay coherent; no conspicuous support protrusion or shoulder interference appears. The far shoulder opening reads as articulation space with visible underbody, not the V11 detached-slab construction. This passes a **coarse static multiview base** gate, not reference likeness, production art or animation clearance. UV/projection may be assessed separately; no further geometry candidate is required within this cap.

Source audit read: lower-shell vertices use majority vote of three non-axis-aligned ray-parity queries, epsilon1e-7m, against the preceding shell. Final six pairs report zero contained samples. Eleven mesh shells report finite vertices/zero boundary or nonmanifold edges; body nearest-vertex minimum2.944mm. Legacy nearest-normal negative signs beyond thin-shell ends are explicitly not containment. These checks do not exhaustively test triangle intersections or motion. The orbit is a static camera rotation, not rig animation; QA visually sampled12/36 source frames, not all decoded video frames.

## Derived UV/material study

Approved derived cleanup merged four confirmed near-coincident cuirass vertex pairs (100nm tolerance, maximum old-to-clean vertex distance15.56nm),1503→1499vertices,1231faces unchanged,zero nonmanifold edges afterward. Frozen attempt03 is retained separately: geometry/topology digests differ and are not described as identical. This is microscopic UV preparation, not a fourth visual design candidate.

Independently inspected final four checker views and six material views including alternate-light three-quarter and1400detail. The former automatic-island patchwork is substantially reduced; mapped detail remains across front/side/back, and highlights shift with the changed key light. Checker still shows local scale/direction changes, curved cells and a rear seam. Final audit has zero degenerate triangles but425cuirass and1404/1409shoulder-cup strict-interior overlap pixels at1024. **No clean or production UV pass.** Pixel-center raster sampling does not certify exact/subpixel coverage. Previous automatic-map and sliver failures remain preserved.

The generated flat steel image is an explicitly synthetic source color sample with documented prompt/provenance, repeated at illustrative tile scale through actual per-piece UVs. Readback reports explicit V12 packed piece UV nodes, packed image/color links and unchanged cleaned geometry digest between UV and material scenes. Roughness is an illustrative inverse-luminance mapping, not measured roughness. No image-derived bump/displacement or recovered metal relief. Two-light response supports a functioning shader study, not calibrated PBR. It remains generic scuffed material on a coarse base, substantially below desired character craft/reference likeness. V10 remains the authoritative complete studio outfit; no game integration, rig, runtime optimization or AI work.


## Frozen independent integrity

206/206 immutable V10/V11 files and28/28 gameplay files unchanged. All 76 manifest entries match exact hashes, including15 canonical stills (5clay,4checker,6material),36orbit source frames, scene/source/texture/readback files. QA visually reviewed all15 canonical stills and12 evenly spaced orbit frames; no claim of watching every video frame. [Final check](character-v12-qa-final-check.json).

Final source SHA256 `526ae1220670127234e7714b8f084221fa26deef1b8a182d1d39172098009000`; material scene `e33596c9d5faaba16393a66bc25d5e3bcac010cf8769a13ea370a384c5e009c3`. Allocated unreal storage 4159991808 bytes; free 27006205952 bytes, within10GB/24GiB limits at check time. No heavy jobs or new game tests run by QA. Three geometry candidates/one UV continuity correction completed; no further corrections claimed. **V10 remains authoritative; boss AI gate remains closed.**
