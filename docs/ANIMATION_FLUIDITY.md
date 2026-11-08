# Animation stiffness correction — 2026-11-03 (packaged for review)

Owner feedback: the previous packaged refinement still feels stiff. Its passing tests establish combat/pose constraints, not artistic acceptance. Preserve the previous source checkpoint, footage, failed clearance tests and performance evidence.

## Diagnosed and changed

The active swing used two separately eased segments. Each reached zero interpolation velocity at the shared release pose, creating a perceptible braking point in the middle of the cut. It now follows a single quadratic grip/direction arc with one acceleration/deceleration envelope. The approved 30/20/36 action windows, damage, stamina, movement and protection rules remain unchanged. Actual blade paths changed and require renewed contact tests.

The old guard was a frozen idle sample and locomotion switched immediately to that sample on commitment. The ready state now evaluates the installed idle/locomotion blendspace on fixed-step time. A short blend of unmodified base poses softens walk/stop/action changes; procedural IK is never fed back into its own input. This is a deterministic fixed-step presentation state, not render-time damping of collision geometry.

Lowered/asymmetric guard, stronger hip turn, delayed chest turn relative to hip drive, head counterbalance, articulated clavicles and changing elbow pole targets reduce the mechanically unified upper body. The shared reachable hilt and exact palm placement remain. This is original procedural animation, not mocap, imported sword assets or a claim of Elden Ring fidelity.

## Actual validation

Final native 11/11 passed, zero test warnings/failures. Added a middle-of-cut continuity assertion to the existing authored-arc test: minimum tested blade travel through the middle of all four cuts is 20.037 cm/tick. Maximum per-tick tip travel 64.538 cm; rounded grip error 0.000 cm. Roll continuity: maximum joint step 31.099 cm, final transition 0.558 cm, minimum head 20.000 cm and blade 31.738 cm above flat floor. Test thresholds were not loosened. Existing visible contact, occlusion, rule and render-partition tests pass.

Standalone package tests **8/8 passed**, zero test warnings/failures. Both native and packaged reports include the new continuous-cut assertion. Existing optional Unreal HTML report template remains absent; fresh JSON reports are validated.

## Actual recordings and limits

[Updated motion clip](../artifacts/unreal/warden-fluid-motion.mp4) and [combat clip](../artifacts/unreal/warden-fluid-combat.mp4). Each has 180 fresh unique actual engine frames, independently encoded/decoded, six seconds at 720p, fixed 30 Hz, no audio. These captures do not measure real-time FPS. All three chronological contact sheets per clip (48 frames each) and selected larger old/new motion frames were visually inspected. Continuous blade progression, shoulder/chest changes and preserved roll clearance are visible in these samples. This is sampled-frame review, not continuous audiovisual playback or owner acceptance.

The motion study preserves the same normal requests at ticks 125/230/290/400, exact ordinary costs and two 300 cm rolls, enabling comparison with [the prior recording](../artifacts/unreal/warden-animation-refined.mp4). It does not demonstrate every walking transition. Combat still has close-range silhouette overlap. The revised visible blade paths also alter hit timing/outcomes (the scripted player takes hits in this clip); unchanged rule windows do not imply identical collision outcomes or established balance. Rigid cape, simple fingers, procedural pose quality and broader locomotion review remain open. This pass does not establish reference-quality motion; owner feedback is pending. Greatsword pace remains as approved.

## Performance and continuation

Fresh separate balanced 720p benchmark: **53.9 FPS mean; 18.539 ms mean / 29.6155 ms p95 (2,957 frames)**, 60 simulated seconds, 180 warmup frames excluded. CSV independently recomputed. Previous pass measured 59.7 FPS mean; different shared-machine load prevents causal improvement/regression claims. Sustained 60 FPS is unverified. No compiler/capture/encoder ran concurrently with this benchmark.

Launch `./scripts/bosslab-unreal package-play`. Controls unchanged: Enter start; WASD/mouse; Tab target; Space roll; LMB/J sword; E heal; P/Escape pause; R reset. Offline; no downloads, new models, adaptive AI or RL training.

Exact next action: incorporate the owner's assessment of the new clip. If still too stiff, focus the next authored-pose pass on full-body support/weight transfer and locomotion transitions; do not treat the numerical continuity checks as artistic approval or add AI yet.

Evidence: `artifacts/unreal/fluid-native-tests.json`, `fluid-packaged-tests.json`, corresponding process reports, both capture manifests and raw-frame directories, `fluid-motion-study.csv`, both MP4 encoding/decode reports, `fluid-motion-review/`, `fluid-combat-review/`, `fluid-benchmark.json`, `fluid-frame-times.csv`, `fluid-final-audit.json`. Source/config/docs checkpoint: `checkpoint-2026-11-03-fluidity.tar.gz`. Previous checkpoint and failed clearance tests remain intact.
