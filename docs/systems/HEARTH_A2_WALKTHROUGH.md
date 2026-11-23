# Hearth A2 — playable review candidate

2026-11-16. The new workshop is integrated and verified as a no-boss human walkthrough. Root accepted the actual final views for review, not as finished reference-quality art. **Performance remains poor: approximately 29–33 FPS in the current full720p runs.** Original Hearth A, original Smeltery, the Regent game and the packaged application remain available.

## Launch and controls

From the project root: `./scripts/bosslab-smeltery`.

The wrapper now selects `hearth-a2`, AO level1 / max quality50, performance shadows and1280 × 720 at100% internal resolution. Normal A2/AO1 play was verified and exited0; the wrapper's subsequent default-selection change passed shell/Python syntax checks without another engine launch. The visibility-scheduling experiment is **not** the default.

Fallbacks: `BOSSLAB_SMELTERY_VARIANT=hearth-a ./scripts/bosslab-smeltery` and `BOSSLAB_SMELTERY_VARIANT=original ./scripts/bosslab-smeltery`. No A2 packaging was attempted; it remains an editor-game scene.

WASD moves; mouse looks; Shift sprints; Space rolls; F jumps; Esc/P opens the pause menu. The menu provides Resume, Settings and Quit. Physical mouse/camera and Shift acceptance remain unverified in this pass.

## What is implemented

The compact16 × 18 m outer field contains foreground anvil/stock work islands and a central route, with a stepped furnace, oak bellows, Gothic window, quench cistern, ore storage, detailed lanterns, asymmetric vault, galleries, stonework, cloth, logs and shallow irregular flagstones. There is no visible rectangular perimeter fence. Three authored invisible prop boxes block Pawn and Camera; separate outer camera proxies allow the rear apron. Visual meshes remain NoCollision. The room is not an unobstructed combat rectangle and has no boss-fairness claim.

Actual import:21 meshes / 32 materials,889,236 environment triangles (889,316 source), each module placed once. Maximum signed-bound deviation0.252576 cm on StockWorkbay; all other modules within0.000279 cm. Generated sources declare basecolor and metallic-roughness G/B, **no normal maps or AO textures**. Unused packed R is not wired to AO. Stone relief comes from geometry. Six floor variants preserve tint/dry roughness and reflected damp paths; water ripple and molten presentation remain approximations, not fluid simulation or calibrated PBR.

Runtime correction uses five motivated lights plus one explicitly approximate rear bounce point; only the window spot casts shadows. Furnace/bellows sources moved forward, window brightness/scattering reduced, and oak grain narrowed to±10%. Source/soft radii apply to A2 only. Frozen Blender/export geometry is unchanged; the runtime deviations are recorded and reproducible through `unreal/art-studio/source/hearth_a2/ue_runtime_tuning.py` after the base import. No global renderer configuration changed.

No boss, encounter progression, combat HUD/music, adaptation, RL or local-model connection was added. No API key or model server is needed to play this scene.

## Actual verification

| Check | Result |
|---|---|
| Full native suite, before final lighting additions |45/45, zero warnings/failures, exit0|
| Final focused arena/parser suite |4/4, zero warnings/failures, exit0|
| Final imported-room collision trial |1/1, zero warnings/failures, exit0|
| Final actual-player visual study |14 frames;11,043.5cm actual travel;21 arrivals across6 waypoints;coverage complete;zero boss/combat ticks;exit0|
| Normal A2/AO1 play |Native8s entry capture before CUA;manual review;exit0 after231.33s|

The explicit asset test (`BOSSLAB_TEST_FILTER=WardenAssetTrial.HearthA2 ./scripts/bosslab-unreal test`) loads the real imported scene and checks all three work-island pawn sweeps and camera sphere hits, rolls and100-tick jump/landing overlap cases, selected outer edge/corner sweeps and pause. No intrusion reproduced in these cases; no tall exclusion or global jump change was introduced. These checks do not prove every movement/camera combination safe.

Actual desktop review observed W movement after a viewport focus click; Esc pause; keyboard Settings→Esc Back→Return Resume; and selected Quit→Return, followed by clean exit. Initial short Esc/P presses and a mouse Settings click did not register. Keyboard navigation worked after focus. The camera changed sharply during CUA interaction; physical mouse/camera limits and Shift remain unverified. No closed-app binding was queried to relaunch it.

## Normal camera evidence

`normal-entry/entry-before-cua.png` shows the full human before CUA touched focus. Bounded logs record intended initialization pitch−12/yaw113.962489, then first-focused-frame raw turn129.253738 and raw look3.091358 at1.675s. The camera subsequently stabilized at pitch−4.271605/yaw77.096827,500 cm arm and511.88 cm actual eye-to-pawn distance through the8.016s capture. Incoming mouse axes explain this run's orientation change; OS focus/cursor warping versus physical input is not established. No input suppression or speculative camera fix was added, and the earlier steep-camera issue is not claimed universally resolved.

## Performance and diagnosis

All clean runs below used1280 × 720 at100% internal resolution, no screenshots, and the normal fixed simulation. Sequential shared-machine observations are not isolated causal experiments. The old room has a different layout/route.

| Run |Mean FPS|Median ms|p95 ms|p99 ms|Frames>33.3ms|Frames>50ms|
|---|---:|---:|---:|---:|---:|---:|
|A2, AO off|28.54|25.89|77.71|159.82|580/1808|237|
|A2, AO on|32.35|25.50|61.49|111.80|487/1997|171|
|A2, AO on, visibility0 diagnostic|33.09|25.20|63.69|109.38|449/2035|193|
|Current old A, AO off|45.34|17.87|36.37|60.46|160/2761|56|

AO-on's better noisy run does not mean AO speeds rendering. Visibility0 did not improve performance convincingly and was not retained as default. Each A2 timing traversed25,403.7cm with51arrivals and complete coverage. Engine delta-time maxima reached400ms; screenshot-study timing is retained separately and is not clean FPS evidence. Historical A59.65FPS does not validate the new scene or current conditions.

One1200-frame CSV diagnostic, excluding its first300frames, measured GameThread4.98 ms, RenderThread26.98 ms and GPU18.35 ms means. Render-thread visibility wait averaged8.55ms; GPU basepass3.47ms, lights3.17ms, volumetricfog3.07ms and SSAO0.55ms. Profiling overhead applies. The unsuccessful scheduling trial means the wait scope does not establish scheduling itself as the cause.

Only one Unreal instance was observed. System swap occupancy was about10.5GB. During diagnostic/analysis, system counters recorded844,778decompressions (~13.84GB page-equivalent),966,944compressions and5,398swap-ins (~88MB). These counters cannot be attributed solely to Unreal. The faster current old-A run suggests scene workload also matters. No unrelated apps were closed, no machine settings changed and no further optimization success is claimed.

## Failures and limits retained

The base importer and the two-material tuning editor saved assets/receipts, then each exited1 during ICU `ubidi_close_64` / Slate text-layout shutdown. Independent native/game reloads and normal Quit exited0. Both failed editor runs and crash evidence are retained.

The first full test run crashed in the newly added parser fixture because it appended an element from the same reallocating array. Copying the shared pointer before appending corrected the fixture; rebuild and fresh tests passed. The stale old report was rejected, never counted as a fresh pass.

Cold views exposed dark generated facets, harsh lights, white window glare and striped wood. Canonical/FBX normals matched almost exactly; angle-limited normal trials did not justify a rewrite. Lighting/material corrections improved the inspected views, but some generated facets, bright window framing, repetitive masonry, simplified source surfaces and incomplete incidental detail remain. This is a visual review candidate with a significant performance limitation, not finished art or a ready boss arena.

## Artifacts and process state

Evidence: `artifacts/unreal/hearth-a2-walkthrough-2026-11-16/` contains full/focused native reports, actual collision trial, cold/tuned/final studies, all timing regressions, CSV/memory diagnostics, normal-entry image/log/process receipt, build/import failures and runtime tuning receipts. Base art/manifest: `artifacts/art/hearth-a2-2026-11-16/`. Integration schema: `docs/systems/HEARTH_A2_INTEGRATION.md`.

Final owned session exited0; scoped process query found no UnrealEditor process and `editor.lock` is unassigned. Final audit:31.421 GB free,6.051 GB allocated under `unreal/`, within the10 GB budget and current15 GiB reserve. No new package, deployment, model download or persistence mechanism was added by this integration pass. Exact next action: owner review of the new room and physical controls; future performance work should target measured rendering/streaming costs before any boss or AI work.
