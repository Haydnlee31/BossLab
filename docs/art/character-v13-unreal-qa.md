# V13 opt-in Unreal trial — independent QA

**Opt-in editor-game trial verified for human technical review; production/art work remains.** Owner explicitly authorizes testing the Blender character in Unreal; prior artistic acceptance gate does not prohibit this opt-in trial. Reference realism and production rigging remain unaccepted. No boss AI work.

Baseline: [source/config and canonical art hashes](character-v13-unreal-qa-baseline.json), 27 Source/Config files plus frozen V13 source/scene. No source/config differences from the prior game baseline at capture. Root owns checkpoint-copy cleanup and its manifest; this baseline does not imply copies must be retained against the new cleanup authorization.

## Acceptance for the trial

- Establish actual V13 identity in export/import/runtime evidence: exact source scene, selected parts, vertex/triangle/material counts, units/axis transforms, excluded groom/hidden objects and any reduction. A screenshot alone does not establish which mesh loaded.
- Opt-in flag must be explicit and reversible. Default original outfit remains usable; unavailable/invalid trial assets produce a clear safe fallback without duplicate/invisible body or sword. Exercise startup/reset ordering.
- Review source/config changes against baseline. Engine-owned combat definitions, committed swing path/contact endpoints, attack/roll timing, invulnerability, stamina and controller behavior remain invariant. Visual attachment changes must not silently change reach/capsule/combat collision.
- Inspect real normal-light arena attack and directional roll footage, plus stand/run/sprint/death/reset as feasible. Check hand/grip, blade alignment, shoulder intersections, cloth rigidity, body exposure, floor penetration and lock-on silhouette. Eight-heading floor test must cover the new geometry, not only old bounds.
- Graphical cooked startup/material/streaming check; no headless rendering success claim. Verify trial is actually selected during tests and captures. Shipping remains unvalidated unless explicitly built and tested.
- Measure same-build, same720p/preset, one game instance with trial off/on. Record frame counts, mean/p95/p99 and frames over33.3ms, with startup exclusion and host conditions. Preserve regressions. Fixed-step footage is animation evidence, not FPS evidence; old59.07FPS does not validate new outfit.

## Claim boundaries

Bone-attached rigid pieces are not a new skinned/production character rig. Static cape movement driven by existing presentation is not cloth simulation. Existing glove UV and box-mapped steel limitations persist unless explicitly corrected and verified. Export reduction alone is not runtime optimization proof. No learning, RL, model connection or new boss adaptation is part of this test.

No build/tests or DCC processes run by QA. Results will be added after actual builder/artist evidence; no passing status inferred from plans.

## Export and source review

[Independent export check](character-v13-unreal-qa-export-check.json): actual JSON hash matches exporter audit;18 rigid groups,60,240 vertices,104,012 triangles and8 palette materials. All vertex/normal/UV arrays are finite and correctly sized; triangle/material indices valid. Source scene identity matches frozen context16. This validates serialized data, not Unreal fitting or visual quality. Export samples every18th fur spline, then decimates; the reported pre-decimation count is already after groom reduction. Texture/shader graphs and cape graphic do not transfer: palette-only materials and inherited UVs are explicit limitations.

Initial source review finds only presentation/HUD/header changes among baseline files, plus new loader/test sources. Combat/sword/encounter/controller/config hashes remain unchanged at review. Loader rejects missing/oversize/invalid-index/unknown-bone data before replacing presentation, creates noncolliding pieces, and retains original outfit fallback. Actual fallback execution is requested; code inspection alone is not a passing fallback test. Dedicated selected-costume test samples all imported vertices across eight roll headings and seven phases; engine grip constraint is expressly not glove-fit proof. Sword maxZ test alone does not prove all visual contact alignment, and merely posing death is not a death-floor assertion.

Builder uses editor `-game` for this opt-in trial. Existing staged packaged game remains untouched; no new cooked verification is implied. Prior requirement for graphical cooked coverage is a future acceptance item, not a result or blocker to the authorized editor trial.

## Actual native checks and palette correction

Independently read baseline-native.json and valid/missing/malformed pass-index reports:21/21 default native,1/1 selected V13,1/1 missing-file fallback,1/1 malformed negative-index fallback; each reports zero failures/warnings. These are native/editor tests, not new cooked verification. Initial selected test failure is retained: actual decorative blade tip148.115906cm exceeded an overly strict148±0.02cm assertion. Corrected cosmetic tolerance is±0.2cm, without changing combat reach; do not claim exact endpoint identity. Runtime skips656 degenerate exported triangles, leaving103,356 rendered triangles in18 parts/48 sections. Reported sampled roll minimum0.490cm, death minimum1.367cm, engine grip0cm remain scoped pose samples, not imported glove-fit or full collision certification.

Initial graphical shader startup hit reserve before frames and is preserved as failure. Later actual outfit footage exposed a gold cape: material-name classification had mistaken gold embroidery wording for metal. Independent comparison of preserved old JSON against corrected JSON confirms exactly2,370 triangle material indices changed, with all other JSON data identical after removing face material indices; all3,138 cape faces now use cloth. Corrected JSON SHA53d5415d57f2a69df25c03dbfa35df98ffea0a957bfc5273ee78d4269c7dd7fa. Initial export check refers to the preserved pre-fix payload. Corrected visual and performance evidence remain pending QA inspection.

## Corrected runtime review and final verdict

**Ready for opt-in human technical review; needs work for production/art acceptance.** Independently inspected all13 preserved corrected motion frames:0,20,44,56,64,65,76,96,110,132,144,155,176. Actual imported costume and sword follow the existing attack/roll/recovery poses; oxblood cape is corrected. Frame110 clearly shows shin/cape penetration. Roll frames show rigid folded/collapsed cloth and approximate fingers/grip; these are visible fitting defects despite passing floor/engine-grip checks. Owner can evaluate the trial, but these defects remain assigned to future garment/hand fitting work. No human control-feel acceptance, new death footage, cooked trial, production skinning or cloth simulation claim.

Motion log identifies frozen scene2457b527…; corrected payload53d5415d… and clip hash are recorded in [final independent check](character-v13-unreal-qa-final-check.json). Decode receipt reports180 frames. QA inspected13 selected source PNGs, not every decoded video frame; the clip is fixed30Hz animation evidence, not measured FPS.

Independently recomputed actual wall-clock CSV results (nearest-rank percentiles):

| Same editor build/preset | Samples | Mean FPS | p95 ms | p99 ms | >33.3ms | >50ms |
|---|---:|---:|---:|---:|---:|---:|
| Original |3213|58.5534|17.04154|25.53258|11|5|
| Corrected V13 |3244|59.0318|16.80725|17.60817|7|7|

Both are720p performance-preset sequential short shared-machine runs, with180 warmup frames excluded upstream. No obvious large V13 regression appears; this is not evidence the outfit improves performance, nor locked60FPS. Maximum stalls343.49ms original/263.37ms V13 remain. This comparison does not replace historical packaged metrics.

Final baseline recheck: only WardenPresentation.cpp, WardenPrototype.cpp and WardenPrototype.h changed among27 original Source/Config files. Remaining24 match, including combat rules, sword contact implementation, encounter/controller code and configuration. New loader/test files implement the opt-in trial. Frozen studio source and scene also match. No AI policy/training/model integration added. Free space at QA measurement26,354,077,696 bytes; future heavy work still requires guards. Root owns separate authorized cleanup and packaged-binary preservation evidence.

Final corrected outfit orbit `v13-outfit-final.mp4` was subsequently supplied with180-frame decode receipt. QA independently inspected all9 retained samples0/20/44/65/88/110/132/155/176: actual front/side/back costume, red cape and imported sword are visible; flat palette and approximate hand/armor fit remain. Primary outfit clip is this corrected file; earlier `v13-outfit.mp4` remains failed-palette evidence. Launcher now explicitly rejects V13 with package modes before launching; actual rejection receipt has exit1/expected diagnostic. Use editor `play` for V13; unchanged package is original outfit.
