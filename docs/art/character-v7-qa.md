# Character V7 independent QA

**Needs work; final V7 actual evidence independently reviewed.** Scoped helmet/shoulder construction and forged-surface sample. No DCC edits/heavy launches, gameplay tests or AI work by QA.

Preflight [baseline](character-v7-qa-baseline.json) snapshots96 immutable V6 source/scene/evidence files and verifies28/28 game baseline hashes. Shared evolving docs excluded. Storage:2,756,161,536 allocated bytes under unreal,31,492,349,952 bytes free.10GB/24GiB guards retained.

Acceptance requires visible coherent helmet/shoulder form improvements in actual clay/material views, no new major fit defects, and real surface assignment/placement. Procedural material or packed texture presence is not an authored whole-character atlas or realism pass. Distinguish new torso/helmet samples from unchanged projected gloves; V5 glove study remains unintegrated unless explicitly verified otherwise. Preserve failed iterations and route concrete visual defects.

Final freeze audit will compare96 V6 files/game28, record final source/scene/image identities and current storage, and retain clearance sampling limits. No rig/motion/cloth/runtime/FPS claims. Boss AI gate remains closed.

## First actual V7 sample review

Inspected head, clay_head and headside. Reprofiled forehead slope and cheek angularity are visible form improvements; six breathing slots remain visible in clay as actual geometry. New surface sample shows repeated faint horizontal dimples down crown/visor center and repeated gorget areas, reading as mapped stamping rather than plausible forging. Side shoulder lower edge shows two parallel bright rails, giving doubled-wire trim appearance. Routed source/placement and duplicate-return/trim inspection to artist. Small bright gorget tips remain historical. No broad artistic pass; high-resolution sample pending.

## Corrected surface/shoulder sample

Inspected corrected head/headside/shoulder. Repeated stamped rows largely absent; shoulder now reads as one returned edge with dark interior rather than two unrelated rails. Actual response remains smoothly manufactured/chrome-like; subtle patina at720 does not establish forged craftsmanship. No broad art pass.

Read producer material/reload audits: three localized families with explicit `V7 forged UV`, real color/roughness/height connections, and six slot-center rays reaching recessed backing. These verify assignment and centered openings only, not all-edge manifold quality or realistic surface finish. Reload reports33 degenerate projected triangles on Boolean-cut visor, other listed fields zero; cylindrical/planar mapping is explicitly not production unwrap/overlap certification. Glove integration unchanged/deferred. Final details and freeze pending.


## Final frozen review

All12 final actual images inspected:10 at720×920 (hero/front/back/side/head/headside/clay_head/shoulder/mask_head/mask_shoulder) plus1400×1800 head-detail and shoulder-detail. Forehead/cheek silhouette, six physical breathing slots and curved returned shoulder edges are real local gains. Stamped-row/doubled-rail regressions were corrected in inspected final views. Broad smooth reflections still dominate and subtle local patina does not reach reference craftsmanship. High-resolution views expose repeated arcing groom fibers and broad backing; simple garments/hands and global material hierarchy remain unresolved. **Overall needs-work, no reference-level pass.**

Read-only source confirms explicit `V7 forged UV` feeds actual color/roughness/height image nodes, height feeds bump and inherited micro-normal combines into surface normal. Final saved-scene probe reproduces diagnostic masks after correcting their persistence;9shader maps were retained and3diagnostic maps now persist,12V7 maps total. Do not count these as12independent materials or a production atlas. Three families apply to crown/visor/shoulder fields.33Boolean-visor projected triangles remain degenerate; cylindrical/planar mapping is not a clean unwrap/overlap certificate. Glove study remains deferred/unintegrated. Six centered rays reaching slot backing verify openings at those locations only.

Final cape audit:24982 body-ray hits/min34.584mm/zero negatives, unchanged3mm threshold and declared mantle/yoke/top/curve/arbitrary-intersection exclusions. Static geometry only; no cloth motion, full collision or deformation claim.

Independent preservation: **28/28 gameplay and96/96 immutable V6 snapshot hashes unchanged**. All12 image hashes match technical delivery. Source `a2fe6366f22745bb4755c35b12da5f5b8d84b35795aaddeed4ea04fe8b68092f`; scene `d695f788c55e26c2e57f8f9e6b4636e99fe576c65c9f1d91bcf5ed60eee663d9`. [Final QA JSON](character-v7-qa-final-check.json) records exact files.

Storage:2,825,297,920 allocated bytes under unreal;30,045,720,576 bytes free, within10GB/24GiB limits. No heavy QA launch or new gameplay tests/FPS. Boss AI remains closed; no production rig/runtime integration/training claims. Report and JSON frozen for checkpoint.
