# Bellbreaker gait remediation — 2026-11-20

The ninth normal-speed pursuit replay verifies a substantial contact and vertical-posture correction. The gait source is frozen; independent final visual review accepts a local gait gain; shared hand/combat validation remains separate. This is not overall artistic acceptance or a performance benchmark.

The previous presentation reset to phase 0.25 on walk entry, placing the source midway through a stance/swing exchange. Its feet latched synthetic lane positions instead of their current positions. Ground distance drove the cycle, but a stationary turn could rotate the body without advancing a step. Stance retained the source's moving ankle rotation and source toe height.

The candidate starts from the actual toes at phase zero. A 60% support interval produces brief double support; the free foot follows a bounded 16 cm swing arc. Stance stores world toe position and foot rotation, with a 0.22-second entry blend. Angular travel at a 90 cm boot radius also advances gait. Small presentation offsets move the pelvis toward the supporting leg, lower it 7 cm, and brace the thorax 5 degrees; turn lag is limited to 5 degrees. Combat translation, facing, rules, timing and weapon pose remain unchanged.

The first candidate capture measured 81 consecutive post-entry stance pairs: median toe XY displacement 0.74 cm, p95 3.81 cm, maximum 6.62 cm. It also spent substantial intervals behind the room wall, so it is retained as failed evidence rather than a clean motion demonstration. The diagnosed ankle-offset correction is now implemented: the ankle target accounts for the rotated ankle-to-toe lever arm before the leg solve. New approach telemetry reports actual target residual to detect unreachable foot goals. The shared next capture enables actual per-boot skinned surface minima; visible hovering is not declared fixed from toe positions. Stops and entry/exit transitions must also be reviewed, rather than concluding from a straight-walk strip.

Technical art owns only gait state/pose sections in `WardenBellbreaker.cpp` and the corresponding walk fields in `WardenBellbreaker.h`. `rig_check` owns hands, all Unreal execution, and shared tests/captures. Evidence is being collected under `artifacts/unreal/bellbreaker-human-motion-20261120`; gait analysis and the preserved prior gait source block are under `artifacts/unreal/bellbreaker-gait-20261120`. The read-only `measure_gait.py` reports rendered ball-joint XY slip during consecutive stance samples after entry blending. It is not a sole-surface contact/collision test or a real-time performance benchmark.

## Pursuit-only intermediate evidence

`sixth-walk-study.log` separates sustained pursuit from attacks. Same-frame full skinned-boot measurements reveal why global grounding was insufficient: among 295 established single-support samples, 30 designated support soles rose above 5 cm (maximum 26.47 cm), although the lowest of the two boots never exceeded 0.6 cm. Double support also failed in 28/118 sole samples. Target reach residual exceeded 5 cm in 157/413 support samples, maximum 32.813 cm. These are retained failures, not a grounded-gait pass.

The staged correction measures cached actual skinned tread landmarks separately by leg ancestry after the foot solve. Two bounded vertical re-solves bring the designated support tread toward floor +0.6 cm and the free tread through a 16 cm arc. XY anchoring and foot orientation remain intact. The independent full-vertex sole audit, rather than the solver's cached samples, will decide whether this correction works. A normal-speed side view with both soles in frame is required alongside the player-camera film.

Moving carry now follows the weight transfer with a small lower hold and counter-sway, rather than keeping an entirely fixed weapon across the moving torso. It eases out during the first six anticipation ticks and is exactly absent during active strike samples; combat reach and timing are unchanged. Shared hand validation remains necessary.

## Seventh side replay: contact gain, vertical-trunk failure retained

The sixth and seventh pursuit captures have **542 identical logged actor path/yaw records**; the camera changed to a side view. On the same 295 established single-support samples, sole heights above 5 cm fell from 30 to zero; maximum height fell from 26.47 to 0.60 cm. Double-support exceptions fell from 28/118 to 1/118 (remaining maximum 6.29 cm). Across 385 consecutive planted-toe pairs, XY displacement p95 fell from 2.663 cm to about **0.01 cm**, near the precision of the logged joint positions. The largest remaining transition sample is 6.32 cm; this is not a universal zero-slip claim.

The separate ordinary combat replay includes ready-facing changes up to 18 degrees per recorded frame. It has 69 established single-support samples, all at or below 0.57 cm, but retains one double-support height exception and stance-slip p95 2.99 cm. Do not generalize the pursuit result to every rapid combat pivot.

Independent side-view review confirmed improved visible planting but identified a rapid vertical posture change. It was not an idle/stop reset: speed stayed 260 cm/s while the pelvis rose 179.78→209.45 cm in three recorded intervals (0.10 seconds at 30 Hz). Worst established-gait three-interval change is 31.71 cm. This intermediate replay remains a failed smooth-trunk result despite its contact improvement.

The owner authorized reopening only that defect. The staged correction derives neutral pelvis height from the fitted model's grounded standing pose, keeps a small bounded fraction of the clip's vertical excursion, and damps it using the previously rendered pelvis height before solving the legs. It introduces no new bobbing waveform. The previous 7 cm braced lowering is included once. Phase, stride, foot contact goals and active combat pose are otherwise retained; early strike settling ends within six windup ticks. Verification is pending.

## Ninth pursuit: bounded pelvis verified

Actual evidence: `artifacts/unreal/bellbreaker-human-motion-20261120/ninth-walk.mp4` (480 decoded frames, 30 fps, 16 seconds) and `ninth-walk-study.log`. The before/after actor XY and yaw records are identical across all 542 logged poses; six gait starts remain. All measurements below use the rendered final pose, after grounding and leg solving.

The worst established-gait pelvis change across three recorded intervals fell from **31.71 to 2.95 cm**; p95 fell from **28.29 to 2.56 cm** (336 windows). The 295 single-support sole minima range −0.27 to +0.57 cm; all 118 double-support minima range −0.26 to +0.74 cm. Neither set has a sample above 5 cm. Maximum support IK residual is now 1.293 cm, down from 31.223 cm. These are minimum boot-surface heights, not a claim that the whole sole patch lies flat.

Across 385 consecutive stance-toe pairs, maximum XY displacement is 0.904 cm, p95 0.0093 cm (near logged-position precision), and summed slip/root travel is 0.118%. Thus the pelvis stabilization preserves the calibrated support and improves the previous transition spike. Analysis receipts: `ninth-walk-gait.json`, `ninth-support.json`, and `ninth-matched-path.json` under `artifacts/unreal/bellbreaker-gait-20261120`.

The ninth pursuit covers ready-facing changes up to 4.216 degrees per recorded frame. The faster 18-degree combat pivots were covered by the seventh ordinary-combat replay before this pelvis-only correction, so their earlier 2.99 cm p95 slip remains historical rather than a new ninth result. Final shared combat coverage belongs to the rig-check capture. The torso/weapon still has procedural stiffness and apron/finger deformation remains outside this gait-only fix. Root's floor-contact shadow visibility change is separate from the actual skinned-sole correction.

Independent art-direction review sampled 32 chronological ninth frames plus the dense 3.5–5.5 s turn. The prior 4.067→4.167 s chest/head pop is visibly suppressed while lead-sole seating remains. Verdict: meaningful local gait improvement; wide/repetitive stance, stiff two-handed carry and apron fan/stretch remain. No new gross turning/framing break was observed.
