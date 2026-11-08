# Character V8 independent QA

**Needs work; V8 regional proportion gains verified in actual renders.** Owner identifies bulk versus reference. Priority is region-specific fitted anatomy/armor proportions, judged in comparable full-figure clay and material views. No camera/overall-scale trick, material expansion, rig, gameplay or AI work.

Baseline125 immutable V7 files snapshotted in [baseline JSON](character-v8-qa-baseline.json);28/28 game hashes match. Shared evolving docs excluded. Free space30,893,993,984 bytes at snapshot;10GB unreal/24GiB reserve retained.

Review actual silhouette against V7/reference with unchanged framing or explicit camera metadata. Confirm region edits preserve attached plates/straps/cloth/weapon relationships and avoid new gaps/intersections. Counts or smaller bounding boxes alone do not establish correct proportions. Final freeze audit compares125files/game28 and records exact geometry/clearance exclusions, images/source/storage. Prior33visor UV degenerates and unintegrated glove study remain unless explicitly corrected; no inference of new UV/rig/runtime readiness from proportion edits.

## First actual proportion sample

Inspected hero/front/side/clay_hero. Torso/waist and shoulder silhouette visibly leaner. Upper-arm cylinders/elbow cups remain disproportionately broad relative to narrowed torso/shoulders; boots still visually heavy. Routed region-coherent arm girth review, without arbitrarily shifting limb centerlines. Skirt now reads as narrow hanging rectangles; artist identified/preserved detached legacy binding mismatch and correction is underway. Side torso still projects strongly forward. No other gross new plate break visible in these samples; no global fit pass. Reject before/after width statistics with changing x-window membership; require stable named groups and explicit camera/height comparison.

## Corrected regional fit and audit issue

Latest hero/front/side/clay show more coherent arm/elbow and boot girth; garment bindings appear attached in front. No new gross fit break in sampled views. Overall art remains stylized and owner proportion acceptance pending.

Read regional-fit/source: named armor grouping is improved over x-window selection, but world-height bands still select different counts (waist2680→2340, shoulders7502→7725); this is not identical vertex sampling. More importantly, protected_state initially records identical matrix_world for every camera view despite actual different render viewpoints, likely stale dependency evaluation after camera(view). Before/after equality of stale matrices does not prove camera preservation. Routed update/evaluated transform or explicit location/rotation capture and preservation of invalid audit. No camera-trick accusation; evidence-quality defect must be corrected before that claim.


## Frozen V8 final review

Reviewed all 12 final views across this increment: hero, front, side, back, clay_hero, clay_front, clay_side, torso, shoulder, head, headside, and 1400×1800 hero-detail; also inspected the three actual V7 clay baselines. Exact final evidence hashes are recorded in [final check](character-v8-qa-final-check.json). Eleven final views are 720×920; one is 1400×1800.

The comparison shows a genuinely narrower torso/waist and shoulder envelope, followed by more coherent arm/elbow girth and slimmer boots. This is useful visible progress on the owner's bulk criticism. Garment edge bindings now follow the reshaped skirt, and no new gross rear cape breakthrough is visible in the sampled back view. The shoulder closeup shows underlayers between lames rather than a clear new penetration. These are sampled static observations, not complete fit or motion certification.

Overall verdict remains **needs work**. The high-resolution hero still reads as smooth stylized armor: broad featureless breastplate and helmet, nearly cylindrical arm/thigh sections, strongly projecting chest in side clay, rigid rectangular skirt panels, and a broad carpet-like mantle. Joint cups and hands remain mechanical. The leaner silhouette does not establish the requested realism or owner acceptance. Further work should retain this proportion gain while developing credible garment/body forms and surface construction; adding more ornaments alone will not resolve those issues.

The camera evidence defect is closed: source now updates the view layer after each camera assignment; fresh saved V7/V8 readback contains six distinct matrices and exact corresponding matrix/lens/root-scale/sword-signature equality. The invalid initial readback is preserved as regional-fit-initial-camera-audit.json. This was an audit correction, not a camera or geometry change. Named-region bounds describe the same object groups, but height-band membership still changes; they are not identical-vertex deformation measurements. Bilateral upper-arm width is not individual arm diameter.

Final independent preservation: **125/125 V7 files and 28/28 gameplay files unchanged**; all listed final source/scene/image hashes match the delivery manifest. Source SHA256 `8251f9acff26b39d0859eb0960dadea13f29d63c78ab03b35b6f9cffb479275f`; scene `2491ed67d9c248214b2a9b8df5f9712fe8ade8f202da4161531d896a1ff6ba23`. Allocated unreal storage 2,887,725,056 bytes; free disk 29,708,701,696 bytes at independent check, within 10 GB / 24 GiB limits.

Producer reload evidence reports 354 renderable objects, 1,064,128 evaluated vertices, 1,933,572 triangles and 25 packed images. Static cape audit: 24,144 body-ray hits, minimum 37.229 mm clearance, zero negative samples. Scope excludes top attachments above 1.515 m, mantle/yoke and curves; vertex rays do not cover arbitrary triangle intersections or cloth motion. Six slot-center rays reach backing; this is not manifold proof. QA inspected evidence and source but did not rerun Blender or gameplay tests.

Previous 33 visor projected UV degenerates and unintegrated glove unwrap limitations remain. No new clean UV, production anatomy/rig, cape simulation, Unreal integration, optimization/FPS, or gameplay validation claim is supported by this offline increment. **Boss AI gate remains closed.**
