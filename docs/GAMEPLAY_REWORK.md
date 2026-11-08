# Gameplay rework — 2026-11-04

Owner authorized continuing until a credible human-review candidate. This is a fundamentals revision; art, adaptive AI, downloads and training remain deferred. Source checkpoint: `artifacts/unreal/checkpoint-2026-11-04-before-gameplay-rework.tar.gz`.

## Implemented changes

- Twelve-tick/200 ms bounded input buffer. Last four sword-recovery ticks now queue through the eight-tick action gap; early inputs still expire and cannot cancel commitment. Rejection feedback explains low stamina/unavailable healing.
- Engine-owned acceleration/braking and integrated roll velocity: six-tick push, twelve-tick carry, eighteen-tick landing. Total remains 300 cm / 36 ticks / 28 stamina, invulnerability ages 4–17. Current approved greatsword timing remains 30/20/36, 32 damage / 22 stamina.
- Roll rotation follows the committed direction without backward yaw whipping. Body-support contact solve and earlier unfolding replace the helmet-only lift/late stand-up. Original procedural animation, not motion capture or a downloaded animation pack.
- Player nonlethal damage interrupts into 18-tick hurt; boss withstands two hits, then the third breaks poise for 36 ticks. Eight-tick action gap follows either hurt state. Boss poise replenishes after 300 ticks without damage. Health loss and protection use the same engine code for all controllers. These are explicit new rules, not AI.
- Visible torso recoil, hurt pose and death collapse; state/poise HUD. No added impact time warp.
- Smooth close-range shoulder offset and limited mouse trim while target-locked. Existing baseline camera, wall collision and upright horizon retained.
- Fixed boss approach speed/spacing and shorter ready interval. Three attack definitions and fixed order retained; no statistical or learned selection.
- Optional `capture exchange` / `package-capture exchange`: 24-second actual engine frame sequence, fixed 30 Hz, plus actual combat trace. This is not real-time FPS evidence.

## Evidence so far

First compile failed on a shadowed variable; corrected, log retained as `gameplay-rework-build-first-failure.log`. First native pass: 15/15, no warnings/failures; report retained under `gameplay-rework-first-native/`. First roll pilot clip is `warden-gameplay-rework-roll-pilot.mp4`: 180 actual engine frames; three chronological contact sheets / 48 samples inspected. It exposed a late crouch-to-stand transition, now refined. AVFoundation decode first failed under the sandbox; decoder succeeded with approved local execution. No failed decode is presented as footage evidence.

Final native source and cooked package now pass 16/16 and 13/13 respectively, zero test warnings/failures. All tests use existing thresholds. Package/build succeeded; engine packaging still reports the pre-existing missing MetalShaderConverter include-directory warning. No human acceptance or finished animation claim.

## Confirmed locomotion bug found during this pass

The old locomotion path used `SetPosition(...)` followed by `TickAnimation(0)`. Unreal's blendspace sample/filter update requires elapsed time; directly moving its clock did not advance the cached pose correctly. A new test measured only **0.052 cm** of forward foot excursion over sustained travel, failing a >20 cm stride criterion while the other 15 tests passed. The installed blendspace was inspected: Direction [-180,180] and Speed [0,600], so the axis mapping was correct. Failure report and full log are preserved in `artifacts/unreal/gameplay-rework-gait-failure/`.

The source now advances the locomotion instance by the authoritative 1/60-second step, letting its own normalized sample clocks and speed/direction blend operate. Verified by the same test and inspected live walking. This is a material root cause missed by the earlier pose-only checks, not a cosmetic enhancement.

The first 24-second exchange pilot is preserved as `warden-gameplay-rework-exchange-pilot.mp4` (720 actual frames) and `gameplay-rework-exchange-pilot-trace.csv`. Three chronological sheets/48 samples inspected. It showed continued close-range stacking and the frozen gait, so it is explicitly a **pre-fix pilot**, not the handoff footage. It includes real hurt, healing and 96 boss damage; no resets. Close-range camera pitch and HUD overlap have since been corrected in source, awaiting inspection.

## Gait fix and live verification

The same stride assertion now measures **92.149 cm** of foot excursion. Native **16/16** passed, zero warnings/failures. Eight-direction max joint step 43.413 cm, exit jump 0.555 cm, minimum head 20.000 cm, blade 7.286 cm; existing thresholds retained. These are correctness constraints, not proof of artistic quality.

Agent-operated desktop session lasted 461 seconds including pauses/inspection. Normal controls exercised walking/turning, lock on/off, miss versus actual 32-damage hit, right-direction and default-back rolls, healing, low-stamina rejection, death/reset and wall-camera recovery. One actual active-boss round ended at tick 1032 / 17.2 seconds: player dealt 96 and took 145 including one 45-point heal. No win or long human playtest claimed. Details and real capture paths: `artifacts/unreal/gameplay-rework-live-checks.json`. Direct multi-key chord syntax was rejected by the desktop tool; overlapping single-key calls were usable but do not establish a complete physical-keyboard direction matrix.

Close-range camera pitch made both fighters more readable in the inspected live view. A final HUD cleanup removes stale rejection messages and the incorrect Ready label after death. Full contact remains inherently occluded at some camera angles; human review is still required.

## Final standalone footage

[24-second actual packaged exchange](../artifacts/unreal/warden-gameplay-review.mp4): 720 unique raw frames, 720 encoded and independently decoded, 1280×720 at fixed 30 Hz, no audio. All 96 chronological samples at 0.25-second intervals inspected across six sheets in `artifacts/unreal/gameplay-review-samples/`. This is sampled visual inspection, not a claim of continuous real-time video watching. The visible test pilot is unchanged; it crowds the opponent and is not a human skill demonstration. At tick 1562, player HP57, boss HP144, zero heals remaining; no victory or reset. Trace and raw-frame hashes are saved as `gameplay-review-trace.csv` and `gameplay-review-frames.json`.

The exchange shows the corrected gait, continuous carried sword motion, grounded roll, recoil, healing and readable state changes. At capsule contact, bodies still obscure each other, particularly during a forward roll toward the boss. The closer shoulder/pitch adjustment helps at normal spacing but does not eliminate this. This remains an explicit human-review item. No final character/art quality or source-game parity is claimed.

Native: `artifacts/unreal/gameplay-rework-native/index.json`; cooked: `artifacts/unreal/gameplay-rework-cooked/index.json`. The failing gait report and both pre-fix pilots remain alongside the final evidence.

## Performance investigation and standalone verification

Fresh balanced 720p: **25.23 FPS mean**, 39.6307 ms mean /110.481 ms p95,1396 active samples after180 warmup frames. This failed the intended smooth-review target. A separate profiled run was worse:13.13 FPS,76.1659 ms mean /201.082 ms p95. Its requested1200 CSV frames did not finish before the benchmark ended; the preserved partial profile has609 usable post-warmup rows for the initial columns. Mean actor tick2.45 ms, GPU47.04 ms, render69.61 ms. Concurrent desktop load was substantial; neither a pure gameplay-code regression nor an isolated hardware limit can be inferred. The balanced run also logged audio-buffer underruns; audio quality remains unassessed.

A new opt-in `BOSSLAB_QUALITY=performance` preset lowers internal render scale to75%, shadow resolution to512 with one cascade, disables AO, lowers AA and caps rendering at60. Combat and fixed-step simulation stay unchanged. First actual720p run: **40.95 FPS mean**,24.4178 ms mean /49.8608 ms p95,2278 samples. This is better observed performance on the shared machine, not an isolated causal speedup or stable60 claim. All failing/profiled measurements are preserved under `artifacts/unreal/gameplay-review-*benchmark*.json` with frame-time CSVs.

Final normal standalone controls were checked again after packaging: Enter/start, Tab, W movement, J committed cut (78 stamina), backward roll (72 stamina), death/FALLEN HUD, R restart, confirmed F5 practice mode, pause/resume, F9 export, clean quit. Records: `gameplay-review-standalone-checks.json` and `gameplay-review-play-process.json`. This supplements the broader editor controls session; neither is owner acceptance. Duplicate reusable rawPNG caches were reclaimed only after matching all hashes to the final decoded720-frame video; video,96 samples,trace and manifests remain. Cleanup manifest records947174778 bytes reclaimed.

The unchanged performance preset repeated at **26.53 FPS mean**,37.6874 ms mean /114.549 ms p95 (1467 samples). A further `minimal` diagnostic removed dynamic shadows,AA and bloom and reduced internal scale to50%: **31.61 FPS mean**,31.6385 ms mean /92.1997 ms p95 (1800 samples). It still stuttered and visibly harmed grounding. Neither is accepted as a smooth-review solution. Balanced remains the default; performance is optional, minimal diagnostic only. Full comparison: `gameplay-review-performance-summary.json`.

## Handoff gate and exact next action

**Gameplay implementation/correctness and provisional footage review are complete; smooth human-play readiness is NOT cleared.** The owner has not accepted animation, and the session did not establish reliable30/60 FPS. No further art or AI work should start. A request to close unused heavy apps was sent; no response was received before this checkpoint. This does not authorize closing them ourselves.

Next action after machine load is reduced: run `BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-benchmark 720p`, preserve its fresh report under a new name, and compare frame-time spikes. If the problem persists, collect a complete shorter CSV profile and investigate render stalls before asking the owner to judge combat feel. Do not reuse fixed30Hz video as performance evidence or keep retrying identical runs without a changed condition.

For provisional controls review once timing is suitable: first use F5 practice mode to assess walking, all-direction rolls, sword commitment and late queued actions; then the fixed boss to assess tell/contact/recovery, dodge protection, hit reaction and close-camera readability. Reject the candidate if input feels swallowed, rolling visually tumbles sideways relative to travel, or contact cannot be read. Human approval remains a separate gate.
