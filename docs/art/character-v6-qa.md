# Character V6 independent QA

## Baseline and scope

**Needs work; final V6 actual evidence independently reviewed.** Read current project status, execution plan/decisions/claims and retained QA role. Scope is offline character-art fidelity and truthful evidence, not gameplay balance. No DCC source edits/heavy processes or engine/AI work by QA.

Preflight snapshot: [baseline JSON](character-v6-qa-baseline.json) records234 frozen V5 main/study source/scene/evidence file hashes. All233 selected entries from prior V5 session ledger match, and28/28 gameplay source/config/binary hashes match Ashbound baseline. Shared evolving status/docs excluded. Storage at preflight:2,691,629,056 allocated bytes under unreal;31,812,055,040 bytes free. Guards remain10GB total/24GiB free; snapshot is not an ongoing guarantee.

## Review gates

- Inspect actual V6 whole-figure and focal clay/material views; compare large visible gains with approved concept. Shape/craft quality remains separate from integrity metrics.
- Route new geometry/fit/art defects directly to artist/director and retain failed iterations.
- If isolated V5 glove UV study is transferred, verify remaining overlaps resolved, actual UV layer/material assignment and repaint/mask placement in reloaded main scene. A successful study or texture file alone does not establish integration. Prior study retains2R/1L sampled overlaps and is unintegrated.
- Clearance tests must declare collider selection and sampling exclusions. Preserve prior mantle-yoke mask diagnosis; no arbitrary exclusions to create passes. Static rays/topology do not establish cloth motion or production deformation.
- Final source-freeze audit checks snapshot234 files, game28 baseline, current storage and final reviewed image/source identities. No new gameplay tests/FPS required for unchanged gameplay.

Boss AI gate remains closed. No reference-quality, production rig, new cloth motion, runtime integration or learning claims without corresponding evidence.

## First actual V6 mantle review

Inspected actual hero/head/headside. Curling longer hem fibers visibly break the former hard backing edge. New major defect: pale oval exposed patch on viewer-right mantle immediately above bright pauldron, visible even at hero scale. Source/object diagnosis needed to distinguish armor/backing penetration from uncovered groom; routed to technical artist. Broad smooth hide-like top field and small bright neck/gorget tips remain. No full mantle/realism pass; UV work explicitly deferred by artist for this increment, so previous isolated study remains unintegrated.

## Corrected mantle and torso-field review

Actual head/hero/torso/clay_torso/mask_torso inspected. Pale oval mantle patch is absent in corrected samples; neckline is clearer. Three-field torso gives a more fitted architectural shape, confirmed in clay. Diagnostic mask visibly follows edges and strap-contact zones, while material render still reads relatively uniform. Conspicuous pale crescent at viewer-left waist above fauld confirmed and routed; small bright gorget tips persist. No other major new attachment break in these front crops. Source/material audit and final view identities await freeze; no overall art pass.

## Final low-resolution set and panel mapping review

Inspected all16 current720×920 views: hero/front/back/side, head/headside, torso/clay_torso, palm/clay_palm, garment, sword, bare_headside and three masks. Prior waist crescent is corrected to a thin hollow rim; producer camera-ray diagnosis identified solid fauld cap, not liner. No other new major breakthrough visible in these samples. This does not establish global collision-free geometry.

Read actual panel source and audit. Each constructed panel has its own normalized `V6 panel UV` grid and packed512×512 construction mask; explicit UV node feeds image. Red rim, green recess and blue strap-contact channels modify shader roughness; base color is fixed, with inherited procedural grain. Actual mask_torso shows placement along borders/contact zones. This verifies a localized constructed-panel sample, not a painted whole-body atlas, bake quality or glove integration. Producer panel audit finite/zero UV degenerates applies to those base grids only. Gloves remain prior projected sample; V5 isolated study remains unintegrated.

Static cape body-envelope audit:24976 ray hits/min34.584mm/zero negatives at unchanged3mm threshold, with mantle/yoke/top/curves/triangle-intersection exclusions retained. No motion/production collision claim. All views remain stylized: broad smooth armor, flat garment drape, simplified hands and carpet-like mantle backing.1400 head detail additionally exposes repeated arcing fibers; finer resolution is evidence of remaining limits, not quality acceptance. Await second detail and final freeze for preservation audit.


## Final source freeze and preservation

All18 final actual images reviewed:16 at720×920 plus1400×1800 head-detail and torso-detail. The high-resolution torso confirms distinct fitted fields, retention tabs and corrected hollow fauld rim, while smooth near-uniform metal and repeated arcing fibers remain apparent. No reference-quality acceptance. Three-panel maps are genuinely integrated roughness controls; glove UV study remains deferred/unintegrated, not silently transferred.

Final reloaded cape audit supersedes earlier24976-count snapshot: **24982 body-ray hits, minimum34.584mm, zero negatives**, with unchanged3mm threshold and explicit exclusions above. Producer reload exit0 confirms audit completion; QA did not launch Blender. No global triangle-collision, mantle clearance, motion, skinning or cloth-simulation pass.

Independent preservation: **28/28 gameplay baseline hashes and234/234 frozen V5 snapshot hashes unchanged**. All18 reviewed image hashes match final technical delivery audit. Source SHA256 `bed76d4c3ee695a00b489706d27be57d1e0d395fb1ef2c7d254e653cfab0ebb2`; scene SHA256 `12a5395147d9271f64e73f90d4e16f100ef0e3270864d9cfe9467d16e7c25e26`. [Final QA JSON](character-v6-qa-final-check.json) records exact identities and scoped results.

Storage at final preservation check:2,756,161,536 allocated bytes under unreal;29,454,639,104 bytes free. Both10GB ceiling and24GiB reserve respected. No new gameplay tests, benchmark, rig, runtime integration or AI work. Approximately1.924million offline triangles are not an optimization or production-readiness result.

**Final verdict: needs work.** Real local gains in torso construction, groom edging, actual panel-mask assignment and fauld cap correction; remaining smooth generic armor, carpet-like backing/repeated grooming, stiff garment construction, simplified hands and unresolved isolated glove UV study prevent overall acceptance. Next work should target visible craftsmanship and coherent garment/fur mass before runtime/AI gates. Report and JSON frozen for orchestrator checkpoint.
