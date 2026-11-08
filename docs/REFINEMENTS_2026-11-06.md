# Fundamentals refinement — 2026-11-06

Owner closed most unused apps and authorized continued refinement. Preserve the approved greatsword timing, all existing combat rules, fixed rehearsal and provisional art. No AI, downloads or machine-wide changes.

## Baseline

Unchanged packaged build, performance preset, 1280×720: 3,208 active samples after warmup; mean 17.0961 ms (58.49 FPS), p95 16.9203 ms. This is substantially steadier than the November 4 runs, but not proof of an isolated causal change or sustained 60 FPS. Evidence: `artifacts/unreal/refinements-2026-11-06/baseline-*`.

## Implemented changes

- Close lock-on framing shifts toward the fighters' midpoint, lowers the high shoulder socket, eases the arm from 500 to 620 cm and introduces a 35-degree close orbit. Baseline unlocked/distant framing returns smoothly; wall collision and bounded mouse trim remain. Diagnostic motion-study framing stays separate.
- A strike begun mid-stride carries the actual foot positions into its windup. The supporting foot keeps its world position horizontally; raised feet settle before the cut. Recovery repositions each foot through a lifted step. No strike timing, damage, cost or authored root travel changes.
- New regression checks inspect actual camera projection at 80/170/300 cm and support-foot drift over four walking phases. Existing contact, grip, roll and frame-partition tests remain unchanged.

Before-change source checkpoint: `artifacts/unreal/checkpoint-2026-11-06-before-framing.tar.gz`. All planned checks completed; results follow. This document does not claim owner acceptance.

First native run:16 passed /2 new checks failed. Close camera trace started inside the boss capsule and retracted into the pair. Fighters now ignore only the Camera query channel; gameplay collision and wall blocking remain. The new foot test incorrectly assumed ankle bone height below10 cm; measured ankle was12.076 cm, so its landing assertion now checks deviation from the same rig's actual standing ankle height (1.5 cm tolerance). Horizontal plant assertion remains below3 cm; measured2.733 cm. Existing tests/thresholds were unchanged. Failure report: `refinements-2026-11-06/first-test-failures/`.

Second native run:17/18 passed. The corrected ankle-height comparison still failed by3.930 cm: a wide inherited stride exceeded leg reach. Lowering the pelvis only as required by the support-leg geometry corrects the actual pose. Final native18/18, zero test warnings/failures; four moving-entry support-foot drift0.000 cm and height deviation0.002 cm. Camera max vertical NDC0.751, minimum center separation61.466 pixels at720p; this is a projection/separation check, not proof of no silhouette overlap. Wall retraction and unlocked baseline restoration pass. Second failure retained in `second-test-failure/`; a transient compiler shadow-name error was corrected before the final build. Cooked, visual and performance results follow.

## Final verification

Native18/18 and cooked15/15 pass, zero test warnings/failures. Native build and standalone packaging exit0. Packaging still emits the pre-existing MetalShaderConverter include warning and an ExampleDeviceProfileSelector warning; zero test warnings is not a claim of a warning-free build.

The [packaged exchange](../artifacts/unreal/warden-refined-fundamentals.mp4) contains720 unique actual engine frames, independently decoded. Inspected96 chronological quarter-second samples across24 seconds. Both bodies remain visible, the windup/cut/recovery and roll tuck/unfold read clearly enough for focused control review. Brief contact overlap remains; the fixed pilot repeatedly crowds the boss. Shoulders/guard and rigid cape/fingers still look provisional. Sampling is not exhaustive per-frame inspection. Capture is fixed30Hz, no audio, not a performance measurement. Same pilot and normal rules; final trace player57HP/boss144HP at tick1562, no victory claim.

Actual standalone desktop input confirmed Enter/start, F5/practice switch, movement, Tab lock/unlock, J contact (boss240→208HP, stamina100→78), Space roll/recovery, P resume and F10 capture. Cmd-Q exits cleanly and app inventory confirms game stopped. This is agent operation, not owner feel approval. Full eight-direction/iframe claims come from native/cooked tests.

| Performance preset,1280×720 | Samples | MeanFPS | Meanms | p95ms | p99ms | Maxms | Frames>33.3ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Unchanged baseline |3208|58.49|17.0961|16.9203|25.7225|133.4556|20|
| Final refined package |3253|59.44|16.8227|16.8215|20.7646|91.4088|6|

Both measure actual wall-clock active gameplay after180 warmup frames,60 simulated seconds with disclosed round resets. No overlapping build/capture during benchmark. Closing other apps preceded both runs; no isolated-cause optimization proof or locked60/long-session guarantee. Previous November4 poor runs remain retained in GAMEPLAY_REWORK.md. Final frame pacing supports a focused human review candidate.

## Artifacts and limits

Evidence directory `artifacts/unreal/refinements-2026-11-06/` contains final native/cooked reports and process receipts, both initial failing reports, baseline/final frame CSVs and distributions, capture hash manifest, per-tick review trace,96 visual samples, manual PNG/JSON and review records. Duplicate generated raw frame directories were hash-verified against the manifest, then removed after full video decode; video/samples/trace retained. Cleanup record identifies exact paths and bytes. No personal files removed.

Source/docs checkpoint: `artifacts/unreal/checkpoint-2026-11-06-refined-fundamentals.tar.gz`; final audit: `artifacts/unreal/refinements-2026-11-06/final-audit.json`. Package remains locally playable; no persistent process. Unreal directory remains4.52GB of10GB budget;24GiB free reserve enforced. No downloads, machine settings, paid calls or deployment.

**Next:** owner review of controls, camera comfort and sword weight/recovery using the verified performance-preset launch. Continue targeted fundamentals fixes from concrete feedback before visual enhancements or AI. Overall motion is still provisional; no Elden Ring quality, audio approval, human victory or artistic acceptance claimed. No statistical adaptation, RL training, or Laya/LLM integration active in this fight; browser statistics/PPO are historical/headless-only and missing models remain unavailable.
