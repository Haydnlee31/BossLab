# Greatsword fundamentals — 2026-11-03

This is the preserved fundamentals baseline. The current packaged animation pass and fresh evidence are in [ANIMATION_REFINEMENT.md](ANIMATION_REFINEMENT.md).

A playable native arena revision for owner review: controls and animation first, final models and adaptive AI later. No API key, Aura subscription, model server or external asset download. Budget is 10 GB for Unreal work, retaining 24 GiB free. Launch and complete controls: [UNREAL_RUN.md](UNREAL_RUN.md).

## Motion and controls

Tab locks the boss. Space commits a directional roll (backwards with no movement input). WASD/mouse move and look; LMB/J commits the two-handed greatsword cut. E heals; P/Escape pauses; R resets. I opens actual controls/grip diagnostics; F5 confirms a switch between fixed attack rehearsal and passive dummy. F6 is an explicitly labeled test pilot, not learned behavior.

The temporary Epic mannequin retains installed locomotion/idle. WardenSword.cpp authors original full-body anticipation, release, follow-through and recovery, with a planted lead step, rear-foot recovery, torso rotation and analytic two-bone IK. Both hands constrain one reachable shared hilt. Roll poses tuck and rotate around the committed travel axis, then return without a facing snap. These are runtime keyed poses, not mocap, a relabeled punch or finalized character animation. Owner approved the deliberate basic greatsword pace. Finger detail, roll feel and broader animation review remain open.

Five swept samples follow the same transform as the rendered blade, with wall occlusion and at most one damage event per swing. Engine-owned rules: player cut 30/20/36 ticks, 32 damage, 22 stamina; roll 36 ticks, 300 cm before collision, 14 protected ticks, 28 stamina; eight-tick recovery gap and bounded eight-tick late-input buffer. No free cancel or input-reading attack selection. The boss repeats sweep → overhead → rising cleave with fixed timing and committed aim.

## Actual verification

| Check | Result / artifact |
|---|---|
| Native/editor tests | 10/10, zero test warnings/failures; fundamentals-third-tests.json |
| Final cooked executable | 7/7, zero test warnings/failures; fundamentals-final-packaged-tests.json |
| Grip / arc | Max tested grip error rounds to 0.000 cm; max tip travel 57.518 cm/tick |
| Actual controls | Tab marker, 32-damage hit (240→208), 300 cm neutral Space roll, lit F1–F5/F9 shortcuts; fundamentals-manual-controls.json |
| Final state export | Actual combat-20261103-112250-64 PNG/JSON reports fixed-rehearsal |
| Final footage | warden-greatsword-balanced.mp4, 180 distinct actual packaged frames, 6 s, 1280×720; independent decode verified all 180 |

Native tests precede only the metadata/evidence-label correction; final cooked tests validate that final executable. The earlier 7/9 and 9/10 failures remain: shared reachable hilt constraints, quaternion interpolation and slower active arcs corrected the observed reach/teleport failures without weakening their thresholds. Historical unarmed tests are archived separately. Current tests also cover input expiration, action commitment/costs, actual wall-blocked blade contact, roll protection, healing/death, inactive statistics, passive dummy and matching combat under 30/60 Hz render partition.

Final balanced-shadow footage is fixed 30 Hz capture, **not real-time FPS evidence**, with no audio. Actual frames 60/120 were inspected for lit contact/recovery and overhead poses; earlier frames also showed tucked roll. The six-second clip does not cover every boss family or replace sustained human play. Frame hashes: fundamentals-balanced-video-manifest.json. Prior editor clip and unarmed footage remain preserved; old raw unarmed frames were moved to unreal/.cache/unreal-user/Saved/CaptureFrames-unarmed-20261103/.

## Performance, including failures

All runs used the shared Apple M3/16 GB machine; no compilation/capture ran alongside the unprofiled benchmarks. Active wall-clock intervals exclude the first 180 active frames and inactive/dead periods. Scripted benchmark rounds and resets are disclosed. Different workloads and background contention prevent isolated causal comparisons.

| Run | Resolution | Samples | Mean ms / FPS | p95 ms |
|---|---:|---:|---:|---:|
| Historical unarmed package | 1920×1080 | 3271 | 16.7199 / 59.8 | 17.3918 |
| First greatsword | 1920×1080 | 1871 | 27.906 / 35.8 | 62.2447 |
| Greatsword with CSV profiler | 1920×1080 | 2208 | 24.1328 / 41.4 | 52.4439 |
| Balanced shadows | 1920×1080 | 2236 | 23.5732 / 42.4 | 49.3637 |
| Balanced default window | 1280×720 | 2254 | 25.158 / 39.7 | 56.4095 |

**Sustained 60 FPS is not established.** Detailed 1,020-frame profile after startup: game thread 2.741 ms mean, actor updates 0.464 ms, rendering 24.059 ms including waits, GPU 16.522 ms. Heavy background load was observed; unrelated apps and system settings were untouched. Lower resolution did not solve the session's frame pacing. Quieter-session profiling is still needed before attributing a cause or claiming stable optimization.

Implemented cost reductions: hidden locomotion mesh postprocessing disabled; the installed locomotion asset is evaluated only while moving; reversible process-level balanced shadows use 1024 maps, two maximum cascades, reduced distance and filter quality. No combat rule change or resolution scaling. Default launch uses balanced; `BOSSLAB_QUALITY=original` restores original shadow settings for that process. Final real frames retain lit scene and contact shadows. This does not prove the entire observed FPS difference came from the preset.

Full runs/CSV/profile and caveats: fundamentals-performance-comparison.json, fundamentals-profile-summary.json, fundamentals-unreal-profile.csv and named frame-times CSVs in artifacts/unreal/.

## Boundaries

During implementation, the supplied YouTube reference could not be visually accessed: web fetch failed and browser hosts were unavailable. The implementation therefore followed the owner's written knight/greatsword/enclosed-arena direction. Subsequently the owner supplied the full local MP4; a timestamped sampled-frame visual review is now complete in [REFERENCE_VIDEO_REVIEW.md](REFERENCE_VIDEO_REVIEW.md). This later analysis does not establish that the existing animation matches the video. No game source/package changed for the review. Native UI worked for controls, then became unavailable during later profiling; engine PNGs/CSV were used instead.

Owner selected "Keep this deliberate greatsword pace" after the first clip. Preserve that basic-attack timing. Roll feel, finger detail, close-range silhouettes, final models, sound quality and sustained human combat feel remain open. No gamepad/mobile, open world, public deployment or new AI. Statistical adaptation, RL and real model connections remain distinct: historical statistics inactive, browser PPO headless-only, native RL/Laya/LLM unavailable. No held-out scenario was retuned.
