# Animation refinement — 2026-11-03

Historical first pass: owner subsequently found this motion too stiff. Current packaged correction and evidence: [ANIMATION_FLUIDITY.md](ANIMATION_FLUIDITY.md).

Implemented, rebuilt, packaged and visually sampled after the owner's local reference review. Approved deliberate greatsword pace is unchanged. Final models and adaptive AI remain deferred.

## Changes

- Independent hip loading, forward drive and settling; rear support foot compensates attack displacement and feet lift/reposition at staggered recovery points.
- Brief carried sword follow-through before returning to the shared two-hand guard.
- Continuous leg tuck/extension during directional rolls, separate hand tuck, landing compression and return to standing.
- Roll blade carries parallel to the roll rotation axis, fixing sideways blade penetration. A presentation-only head-clearance offset keeps the helmet above this flat arena floor. Capsule travel and invulnerability are unchanged; this is not general terrain IK.
- Explicit `package-capture motion` diagnostic: two normal sword requests, side roll and backward roll against a passive dummy. Normal costs/commitment, actual trace, disclosed label, stable three-quarter diagnostic camera and unobstructed feet. Normal gameplay camera remains unchanged.

Rules remain 30/20/36 strike ticks, 32 damage and 22 stamina; roll 36 ticks, 300 cm maximum before collision, 14 protected ticks and 28 stamina. Eight-tick recovery/input-buffer rules and fixed boss rehearsal remain unchanged. Visible blade trajectories changed, so contact/wall and full encounter tests were repeated.

## Actual validation and retained failures

Final native **11/11**, final cooked **8/8**, zero test warnings/failures. JSON reports are authoritative; the optional Unreal HTML report template remains unavailable. Pose diagnostics: maximum four-direction joint step 31.008 cm, standing-transition jump 0.000 cm, lowest sampled head 20.000 cm, lowest sampled blade 31.941 cm. Maximum tested grip error rounds to 0.000 cm; maximum sword-tip step 57.518 cm.

The first pose suite passed before clearance assertions existed. Stricter assertions then failed **10/11**: head minimum 4.411 cm and blade minimum -88.667 cm. Corrected motion passes the same stricter thresholds; failed JSON/logs remain. These sampled bone/blade measurements do not prove every mesh vertex clear or artistic quality.

The 24 GiB free-space guard stopped an intermediate build. Owner freed space; subsequent builds/runs passed with the reserve unchanged. In-progress checkpoint and storage-stop evidence remain historical. No personal-file deletion, downloads, global cache changes or persistent jobs.

## Visual evidence

- [Isolated motion clip](../artifacts/unreal/warden-animation-refined.mp4): two swings, side roll, backward roll. Trace confirms normal action acceptance at ticks 125, 230, 290, 400 and both 300 cm rolls.
- [Combat clip](../artifacts/unreal/warden-animation-combat.mp4): fixed rehearsal, normal camera, actual hits/damage and boss sweep/overhead tells.
- Both clips: 180 fresh unique actual packaged frames, independently encoded/decoded, six seconds at 1280×720, fixed 30 Hz, no audio. **Not real-time FPS evidence.**
- Visually inspected all three chronological contact sheets per final clip (48 sampled frames per clip, plus selected larger motion frames). Weight shift, step/recovery and roll tuck/landing are visible; no severe roll floor penetration in the inspected final samples. This is sampled visual review, not continuous audiovisual playback.
- Combat samples confirm a remaining close-range silhouette/camera overlap problem. Provisional armor/fingers/cape remain rigid/simple; motion does not match commercial reference fidelity. Only the earlier greatsword pace has owner approval.

## Performance

Fresh standalone balanced 720p run: **59.7 FPS mean, 16.7482 ms mean frame interval, p95 17.5266 ms (3,269 samples)**. Actual wall-clock active frame intervals after 180 warmup frames, 60 simulated seconds, labeled test pilot/disclosed resets. No simultaneous compiler/capture/encoder. This shared machine is not an isolated benchmark. Prior 720p run was 39.7 FPS mean / p95 56.4095 ms; background load differs, so this comparison does not establish a causal optimization. **Sustained 60 FPS remains unverified.** No new rendering optimization was claimed for this pose pass.

## Evidence index and next action

Under `artifacts/unreal/`: `animation-final-native-tests.json`, `animation-final-packaged-tests.json`, corresponding process reports, `animation-clearance-failure-tests.json`, both final capture manifests/raw frame directories, `animation-final-motion-study.csv`, both MP4 encoding/decode reports, `animation-motion-review/`, `animation-combat-review/`, `animation-final-benchmark.json`, `animation-final-frame-times.csv`, and `animation-final-audit.json`. Source/config/docs checkpoint: `checkpoint-2026-11-03-animation-refinement.tar.gz`; binary/assets are in the existing project/package, not duplicated in this source checkpoint.

Launch: `./scripts/bosslab-unreal package-play`. Next development action: review roll feel in the playable build, then address close-range silhouette/camera overlap and locomotion-to-action blending before final models or AI. Keep this pass's tests/footage as dated evidence. No adaptation, RL training or local-model connection added; historical browser PPO remains headless-only.
