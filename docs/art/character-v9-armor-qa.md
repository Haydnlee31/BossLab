# V9 armor independent QA

**Retain the local shoulder construction improvement; overall character remains needs work.** This is a separate V8-derived armor candidate. The failed V9 cloth study is not incorporated. Its findings remain in [cloth QA](character-v9-qa.md) and [neutral handoff check](character-v9-qa-handoff-check.json).

## Actual visual review

Inspected eight final images: hero, front, back, side, shoulder, clay_shoulder, clay_shoulder_side (720×920), and shoulder-detail (1400×1800), plus two actual V8 clay shoulder baselines. The three lower lames per side now form a smoother descending cover with consistent overlapping edges. The former large open mouths and pointed side projections are reduced. The narrow V8 silhouette and original skirt remain visible; no new gross shoulder break or rear cape breakthrough is apparent in these sampled static views.

This is a meaningful local form repair, not reference-level realism or owner acceptance. High-resolution detail still shows smooth almost chrome-like plates, repeated fine looping mantle fibers over broad backing, simplified torso/limb construction and rigid skirt panels. Articulated shoulder mechanics, movement clearance, textile quality and hand anatomy remain unproven.

## Source and measurement review

Source opens the frozen V8 scene, replaces six lower lames and associated old perimeter hardware, and keeps the upper caps. It does not load the V9 cloth scene. Saved-scene producer audit reports 311 retained original objects with unchanged base geometry/material-name/transform hashes, zero unexpected missing objects, matching protected camera/sword/root states, and no V9 solver/extracted-cloth objects. Hash scope does not certify every modifier, shader value or full appearance; actual views and source inspection complement it.

Six evaluated new lames each have 2,262 sampled vertices checked against nearest evaluated arming-sleeve/rerebrace surfaces. Minimum signed distance is 4.809 mm, with no sample below −1 mm. This is a nearest-surface normal test, not global inside/outside, plate-to-plate intersection, articulation or arbitrary triangle clearance certification. Nominal overlap/thickness values are construction parameters, not independent measurements of every overlap.

Producer asset audit reports 348 renderable objects, 1,068,040 evaluated vertices, 1,941,420 triangles and 25 packed images. Static cape evidence remains 24,144 body-ray hits, minimum 37.229 mm, zero negative samples, excluding top attachments above1.515m, mantle/yoke and curves. No cloth motion or global collision pass follows.

No new finish/UV improvement is claimed. Previous visor projected UV degenerates and unintegrated glove study remain. No gameplay tests or heavy jobs were run by QA; no rig, Unreal integration, FPS or runtime cloth evidence was added. **Boss AI gate remains closed.**

## Frozen preservation check

Independent final check: 86/86 V8 files and 28/28 game files checked with zero mismatches. All eight final images, two baseline images and source/script/scene hashes match the delivery manifest. See [final audit](character-v9-armor-qa-final-check.json).

Source SHA256 `5b393b37e8d64f3dab176c8cc78f4303e96c5a05cd68e9079ea08c139f3abecf`; scene `12ce88ea72e823282fedcbba37fbfe382bef8a7c01eca4eff60bdbd27731c9b7`. Allocated unreal storage 4077260800 bytes; free disk 29185224704 bytes, within the 10 GB ceiling and 24 GiB reserve at check time. Cloth neutral handoff was independently verified separately; no other DCC import or platform migration occurred.
