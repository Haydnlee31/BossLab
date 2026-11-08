# Character V4 independent QA — 2026-11-07

## Scope and current verdict

**Needs work — final V4 independently reviewed; actual silhouette/material progress, overall concept fidelity unmet.** Owner-approved generated concept is direction only. This pass judges substantial concept-to-3D fidelity, not physics or a numerical integrity certificate. No gameplay, engine, AI, model, rig or animation work is authorized by this art review. QA owns this report; source remains technical artist-owned.

## Observed V3 baseline versus approved target

Compared actual `artifacts/art/last-vigil-v3/hero.png` with `artifacts/art/last-vigil-concept-2026-11-07/concept-target-not-built.png`.

1. **Major — shoulder construction/silhouette:** current oval cushion caps and rounded repeated bands read as soft shells. Target plates descend in defined angular lames with thinner edges and a coherent shoulder-to-arm taper. Owner: animation-techart with art-director.
2. **Major — cuirass identity:** broad smooth front and small narrow plaque leave a blank cylindrical mass. Target fitted waist, central breast ridge/side sweep and substantial integrated gate detail communicate purpose-built armor. Author primary planes and fitted layers before extra ornament. Owner: animation-techart.
3. **Major — mantle silhouette:** regular brush-like hanging strips form a stiff collar ring. Target irregular low fur masses drape onto shoulders and interrupt edges. Need believable clump scale/orientation and coverage, not additional repeated strips. Owner: animation-techart.
4. **Major — material hierarchy:** broad smooth blue-silver highlights dominate the actual figure. Target separates dark forged steel, worn edges, leather retention, mail recesses and matte fabric. Local V3 UV samples do not establish this whole-character material quality. Owner: animation-techart/art-director.

These are whole-figure differences; another isolated finger adjustment cannot establish a major visible improvement. Helmet proportion, palm anatomy, skirt folds and surrounding repeated tubes remain secondary defects, not resolved by this prioritization.

## Acceptance rubric for actual V4 review

- Compare actual front/three-quarter views at comparable framing; inspect clay to distinguish constructed planes from texture/lighting changes.
- Shoulder and torso silhouettes must visibly move toward the approved target, with fitted layered construction and no new conspicuous intersections or floating trim.
- Mantle must lose the regular brush-ring reading at full-body scale, if included in this increment.
- Material differences must be visible in actual renders; verify any changed UV/image wiring and diagnostic placement separately. Map presence or union coverage alone is insufficient.
- Report each corrected defect separately from overall realism. A manifold mesh, high polygon count, successful render or generated concept cannot pass the art gate.
- Review final frozen evidence before a preservation/storage audit; no repeated gameplay tests for unchanged gameplay. Preserve game28 baseline and immutable V3 evidence.

## Evidence and exclusions

Baseline visual inspection completed; actionable priorities routed to art-director and animation-techart. V4 actual render review and final source-freeze audit pending. No new frame-data, fairness, balance or FPS results. AI gate remains closed until all other readiness gates are met. Existing V3 planar glove UV limitations remain historical baseline evidence, not assumed corrected.

## First actual V4 draft review

Inspected actual hero, clay_hero, head and clay_head draft views. Flattened shoulder caps and opened mantle front visibly change construction, but do not yet establish a major fidelity improvement.

**Major new defects, routed to technical artist:** mantle is two broad naked smooth tan panels with isolated claw-like tufts at outer tips; exposed dark gorget has bright trapezoid-shaped surface breakthroughs/seam patches down the center; chest cord terminates beside shoulders in thin projecting bright rods. Correct these before final evidence. Shoulder lames remain smooth rounded horizontal plates and helmet remains bowl-like. Needs-work verdict retained. These observations describe the first draft, not a frozen delivery; final image identities will be recorded after source freeze.

## Second corrective draft

Actual hero/head/clay_head show the central gorget breakthroughs and projecting shoulder cord rods corrected in these front samples. Front visor now has a more intentional planar field. A small bright triangular sliver at the viewer-left upper gorget edge was routed for inspection; cause not independently established. Mantle still reads as rigid pads sprinkled with sparse flecks, a remaining major silhouette/material failure already under correction. No full-body quality pass or global intersection pass; final audit remains held until source freeze.

## Third corrective draft

Actual hero/head show strand coverage substantially correcting the exposed-pad/isolated-claw defect. The shoulder drape is a useful silhouette change from the original regular brush ring. Close-up still reads as pale crisscross straw on dark hard backing rather than varied soft fur clumps. Broad smooth silver-blue armor remains the dominant whole-figure mismatch; a bounded material hierarchy pass is warranted, separating steel/leather/cloth and placing restrained edge/recess variation rather than blanket noise or darkening. Small viewer-left upper gorget sliver remains visible. No new major geometry defect in these two views; final audit still pending.

## Fourth material/construction draft

Actual hero/head show neutral darker steel, quieter edge highlights and a shaped gate arch improving material hierarchy. Fur is now grouped more coherently but remains repeated comb tufts on visible dark backing. Rounded cushion-like shoulder caps remain conspicuous; a bounded actual cap replacement targets a larger visual mismatch than additional surface decoration. Smooth schematic armor, plain skirt and cylindrical limb construction remain below target. No reference-level success or whole-character acceptance. Final views/source freeze and preservation audit pending.

## Final angular-cap visual review (awaiting source freeze)

Inspected eight current actual material/clay views: hero, head, headside, palm and clay counterparts. Replacing pillow caps with descending angular plates creates a meaningful visible shoulder-silhouette improvement, verified in clay as geometry rather than lighting alone. Remaining plates are flat/sheet-like; the side mantle exposes hard backing and regularly repeated tufts; helmet/torso and limb construction remain smooth and schematic; palm remains simplified. These are unresolved major quality gaps, not a reference-level success. No global clipping claim follows from these views.

Read-only source inspection confirms named `Authored sample UV` nodes feed focal image vectors and color/roughness/relief are connected to their actual shader inputs. Broad armor steel instead uses object-coordinate procedural grain/roughness and restrained color variation; it is not a newly authored whole-body UV atlas. Current producer UV audit reports 934/932 degenerate projected glove triangles and approximately51.14% union coverage, with explicit front/back overlap and side compression. Eight packed focal maps plus inherited images are not eight newly independent material achievements. Counts/UV validity remain separate from artistic judgement. Source freeze and final preservation/storage identities still pending.


## Frozen delivery verdict and preservation audit

All **13 final actual720×920 images** inspected: hero, head, headside, palm, clay_hero, clay_head, clay_headside, clay_palm, front, back, side, mask_head and mask_palm. Final front/side confirms descending shoulder plates and visible underlying upper-arm shell; no clear new penetration in these samples. Back shows no visible cape breakthrough. This is not a global collision certificate. Mask diagnostics visibly place selected rim/scratch regions on helmet and thumb/index/contact/crease/stitch regions on glove, corroborating source shader wiring.

**Verdict: needs work.** Angular shoulder geometry, open-front mantle, fitted visible gorget, more planar visor and quieter neutral material hierarchy are actual progress. Flat sheet-like plates, exposed mantle backing/repeated tufts, smooth schematic armor, plain skirt/cape construction, simplified hand anatomy and limited localized wear remain below approved target. Next meaningful work is coherent constructed cuirass/garment/material surface authoring and irregular mantle mass, not another count-driven polish certificate. Reference-level acceptance, production UVs, rig, deformation, cloth motion and runtime validation remain open. Boss AI gate remains closed.

Frozen source SHA256: `d773d38db8503c18bb734d3ef961524aa99e688b57e95eda7a6f1c600b50ef62`.
Frozen scene SHA256: `506d06ed68b754e6b5b6756177a0b55f69756a403055c927bb374f31bec03d77`.

Independent read-only hash check: **28/28 gameplay source/config/binary files unchanged** against Ashbound final audit; **111/111 selected immutable V3 source/scene/evidence files unchanged** against V3 session audit. Shared evolving docs/status excluded. All13 reviewed final image hashes match technical delivery audit. Full identities/checks: [QA final check JSON](character-v4-qa-final-check.json).

Storage at check: **2,954,203,136 allocated bytes under unreal**, **29,025,906,688 bytes free**. Both10,000,000,000-byte ceiling and25,769,803,776-byte reserve respected. No game/Blender launch or new gameplay tests by QA. Earlier game tests/FPS do not validate this studio asset. Static producer geometry counts323objects/751071vertices/1385762triangles and closed glove topology are integrity evidence, not realism or runtime readiness.

Actual evidence: `artifacts/art/last-vigil-v4/`; editable scene: `unreal/art-studio/revision-v4-2026-11-07/last-vigil-v4.blend`. Earlier failed draft observations above are historical and superseded only for explicitly corrected defects. Final QA report and JSON frozen for orchestrator checkpoint.
