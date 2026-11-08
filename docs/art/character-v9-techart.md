# V9 — actual cloth drape and cut-pattern study

Status: cloth branch stopped after failed structural collider trial; V8 remains the working art checkpoint. No V9 cloth integration. Separate Blender study preserving V8. This workflow uses Blender's actual cloth solver to author a static garment; it is not a gameplay cloth implementation, combat motion test, rig or AI capability. No external software/assets were installed or purchased.

## Method

Two disconnected cut patterns share one low-resolution cloth mesh: 21×45 vertices each, 1,890 total vertices and1,760 quad faces. Gravity is−9.81m/s²;100 frames at30fps. Top-row vertices alone have virtual under-belt pin constraints. A shape-key-driven attachment gathers the cut over frames1–16. Existing rigid tassets remain separate and unchanged. Cloth quality8, collision quality5, tension/compression35, shear15, bending0.35; mass setting0.35, air damping3. These settings are an authoring trial, not calibrated wool properties.

Original analytic front boards and their unattached seam/binding curves are hidden in the new scene, preserved in V8. The result is extracted from actual evaluated frame100 positions into a separate static candidate with2.5mm thickness and subdivision. The solver scene and its disk cache remain separate evidence. Old cape physics and gameplay tests do not validate this new cloth.

## Declared gates

Before accepting later trial results: finite coordinates; maximum structural-edge stretch≤1.10 across the complete solve; maximum per-frame vertex motion in the final10frames≤1mm; pin-target error≤1mm; sampled closed-proxy clearance≥−1mm; cloth midsurface at least1.5mm behind each ray-hit actual tasset rear surface. These are local engineering heuristics, not textile calibration or complete collision proof. Total initial-to-final deformation and frame90→100 net drift are distinct metrics.

Nearest signed distances refer only to closed proxy surfaces/normals. Tasset y-rays test only cloth vertices whose x/z rays hit a rigid plate, omitting edge-to-edge, triangle intersections and shell thickness. Final visual fit remains required even when these gates pass.

## Preserved failures and diagnosis

1. Initial full-tasset solve catastrophically bunched: maximum edge stretch7.033× and final10-frame step25.987mm. It is a failed solve, despite exit0. Scene/cache/source/renders are retained in `iteration-01-unstable-tasset-contact`.
2. Removing tasset collisions alone isolated the cause: body-only diagnostic became stable, stretch1.01322 and final10-step0.719mm. It was not a final obstacle-free integration. Initial visible tasset-back gap3.54mm was smaller than combined configured contact envelopes (about5mm), consistent with contact-envelope interference without a hard initial mesh crossing; the test does not prove this explains every later failure. This variant remains `iteration-02-stable-body-only`.
3. Moving the attachment/pattern21mm rearward and restoring all six actual tasset colliders restored stability: stretch1.01868, final10-step0.714mm, initial plate gap24.54mm. Actual renders revealed the old mail underlayer penetrating the inward cloth. The collider gates did not cover that layer; this visual failure is retained as `iteration-03-mail-layer-breakthrough`.
4. Mail rings were translated intact toward the actual padded-thigh/cuisse front envelope, rather than pushing fabric forward to conceal the defect.360 of374 rings in each mesh found a fitting ray;14 unsampled rings per side remain at their prior positions. Closed convex envelopes are built from the entire resulting mail geometry, including retained rings; both have two faces per edge. This is deliberate mail-layer movement, not an assertion that every old armor layer stayed unchanged. Two measured thigh proxies and both mail-envelope proxies accompany all six rigid tasset colliders. Wider194mm cut gathered to169.26mm attachment span produced12.75% ease and stable shallow folds: stretch1.02083, final10-step0.657mm. Mail penetration disappeared in reviewed views, but rectangular ribbon-like shape remained artistically inadequate. Preserved as `iteration-04-stable-mail-and-ease`.

The latest trial changes the actual cut:194mm top width tapering to145mm below the armor, outer lower corner35mm higher, opposite panel20mm shorter; outer top attachment returns25mm toward the belt arc. It retains the proven layer/collider setup rather than inventing analytic wrinkles. Actual solver results and visual review determine acceptance.

## Scope and remaining work

V8 body proportions, rigid tasset surfaces, sword, camera framing, lights and existing materials are retained. Mail fitting is explicitly changed. Overall realism, mantle/groom, helmet/steel craftsmanship, gloves/UVs and production topology remain unresolved. Source relies on frozen V8/V7 utilities; the saved static scene is editable separately. No game/FPS, rig, cloth-combat, shipping, adaptation, RL or model-integration claims.

All runs use the existing foreground CPU launcher with10GB total Unreal budget,24GiB free reserve and20-minute limit. Failed evidence and caches are preserved. Final frozen files, hashes, exact audit values, image list and resource receipts will be added after review.

## Final rejected trials and retained handoff

The tailored cut with a curved pin return failed: maximum stretch3.238×, final10-step15.004mm, net90→100 drift79.265mm. Restoring straight pins while retaining the tailored cut and extending to200frames also failed: stretch8.402×, step15.097mm, net190→200 drift32.027mm. This disproves the curved return as the sole explanation. Both scenes/caches/evidence are retained (iterations05/06).

Final structural trial replaced six thin overlapping collision meshes with two closed convex coverage proxies made from the actual evaluated tasset stacks; visible plates were unchanged. A real before-bake setup check passed for initial proxy nonpenetration and constrained pin goals clearing contact envelopes within1mm. Nevertheless the200-frame simulation failed: maximum stretch1.759826, final10-step12.402mm and net190→200 drift61.883mm. One panel still bunches upward. This is a rejected solve, not artistic asymmetry or a passing cloth implementation. Exit0 means Blender completed its operations; it does not mean the declared numerical/art gates passed. No further parameter loops were attempted.

The initial and final diagnostics explicitly distinguish gate coverage: proxy nearest-surface distances and actual tasset y-rays are incomplete collision samples. A setup check passing does not guarantee a stable later solve. The final before-bake report is preserved separately from retrospective reload verification.

The best stable partial remains iteration04 (100frames, shallow ribbon-like design, not accepted as finished art). A separate copy is `unreal/art-studio/revision-v9-2026-11-07/last-vigil-v9-best-stable-partial.blend`. Main V9 solver/candidate files are the final REJECTED diagnostic, not replacements for V8. Root failure pixels remain in place for independent hashes; historic frame001/025 files refer to earlier patterns and are not presented as final tailored progression.

A compact neutral local handoff is provided at `unreal/art-studio/revision-v9-2026-11-07/neutral-handoff/`: actual solver rest-panel OBJ, measured collision-proxy OBJ, unchanged rigid-tasset OBJ, earlier stable-partial OBJ clearly labeled unapproved, pin-target JSON, manifest and README. Coordinates are meters, +X right,−Y front,+Z up. These are portable geometry files, not an uploaded service connection or certified production sewing patterns. OBJ coordinate finiteness and face indices were validated. No materials/rigging/application-specific constraints or clean-UV claim is implied. Another DCC must still correct drape/contact and verify the actual layered outfit.

The cloth source now includes a pre-bake setup gate for future reproductions and suppresses final material suites when numerical strain/step gates fail. This guard was added after earlier trials, not retroactively claimed for them. No source cache has been installed as a runtime/persistent process.
