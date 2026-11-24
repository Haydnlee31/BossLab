# Bellbreaker play freeze (2026-11-24)

**Report:** the owner played the forge fight and the game lagged "until I can't play".

**What the play log showed (artifacts/unreal/play.log, 17:52-17:54 UTC):**
- The fight ran normally until about 16 s after the Bell Breaks started phase two (17:53:39).
- Around then the log recorded 100 PSO creation hitches (none precached) and a STUCK-STATE line.
- After that the frame counter advanced roughly one frame per 10 s until the owner quit.

**Cause:** a spiral of death in the fixed-step catch-up (`WardenEncounter.cpp`). The loop had no cap, so one long frame queued hundreds of 60 Hz steps, which made the next frame longer again.

**Fix:**
- At most 8 steps (133 ms of fight) run per rendered frame outside automation. The remainder is dropped, so a stall slows the fight briefly instead of freezing it.
- Each step is unchanged. Automation keeps the uncapped loop.
- A `BOSSLAB frame budget` line every 2 s records fps, worst frame, steps per frame, step cost, presentation cost and dropped time, as a witness for future reports.

**Measurements (all 720p, all on the same loaded machine):**

| Setup | Mean frame | p95 |
|---|---|---|
| Forge, phase-two start, balanced quality | 79.0 ms | 191.6 ms |
| Forge, phase two, performance preset | 60.0 ms | 150.3 ms |
| Same, spectacle effects off | 68.8 ms | 160.9 ms |
| Original boss and arena, performance preset | 32.4 ms | 79.3 ms |

- Game code is cheap in every run: about 0.5-1 ms per step and 1-2 ms per frame for all presentation (Bellbreaker view, effects, spectacle).
- The spectacle pass does not explain the slowdown.
- The original boss and arena normally runs at about 16.7 ms, so the machine itself was about 2x slower than usual. Throughout these runs an unrelated UnrealEditor (another project, open for over 12 hours) used 45-60% CPU, along with macOS background jobs.
- None of these runs is an isolated performance claim.

**Still open:**
- First-use shader/PSO hitches. Play runs with a single shader worker, so new effect materials compile during the fight.
- The Hearth A2 forge's render cost on this Mac.

Native 55/55 (engine HTTP warning in two), forge trials 2/2.

## Follow-up: first-use shader/PSO hitches (2026-11-24)

**Cause:** play runs in the editor binary, where Unreal hard-disables PSO precaching (`PipelineStateCache::IsPSOPrecachingEnabled()` returns false under `WITH_EDITOR`). Each effect material built its pipeline the first time it was drawn. Pooled effects (empty instanced meshes, hidden props, the raised dead) are never drawn until their move. Each sound family also loaded synchronously on its first play.

**Fix (`WardenWarmup.cpp`):**
- **Mesh/material warm-up.** One full-size copy of every distinct (component kind, mesh, materials, shadow, custom data) is drawn 1.2 m ahead of the camera. In play this happens behind the opaque home/boss-select menu; capture and benchmark use a black camera fade for at most 50 frames.
- Copies are added 48 per frame, jiggle so the velocity pass draws, and stay until the shader compile queue has been empty for 10 frames. Caps: 30 s, or the fight starting.
- **Canvas warm-up.** The HUD draws a near-invisible sample of each canvas element it uses (translucent rect, text at every scale, thin and thick lines) for the same window.
- **Sounds.** The whole `/Game/BossLab/Sound` bank is preloaded at BeginPlay. The roster filter in `SfxVariations` is unchanged.
- **Switches.** `BOSSLAB_WARMUP=0` disables the warm-up for A/B runs. `BOSSLAB_PSO_LOG=1` (launcher) logs each runtime PSO hitch over 20 ms.
- Presentation only. Combat rules and steps are unchanged.

**Evidence:** forge, phase-two start, performance preset, 720p benchmark, single BossLab instance.
- **First run with warm-up:** 113 sources, finished in 19 frames / 5.0 s. All 10 scene PSO hitches fell inside the warm-up window (frames 9-15). Without the warm-up, these pipelines would have been built when their effects first appeared.
- **Canvas pipelines:** 4 hitches still appeared mid-fight in that run (and 1 in the run without warm-up). After adding the canvas warm-up there were none mid-fight; the only hitch was at frame 0, during start-up.
- **Sync loads:** no mid-fight `FlushAsyncLoading` in any run.
- **Caveat:** macOS keeps its own on-disk Metal cache, so repeated runs on the same machine are warm. A later run with the warm-up off also showed 0 hitches. The A/B is therefore not a cold-cache measurement.

**Frame rate:**
- With a stray, project-less UnrealEditor closed (open about 21 h, about 9.6 GB of memory, 14 GB of swap on a 16 GB Mac), forge phase two measured 16.67 ms mean / 16.80 ms p95, against 60 ms mean in the earlier runs on the loaded machine.
- That editor's memory pressure was the main cause of the lag the owner saw. Not an isolated optimisation claim.
- It ignored a normal quit for 30 s and was force-closed at the owner's request.
- The project's compiler object files (1.2 GB, regenerable) were cleared during this pass while swap held the disk below the reserve; the next build after that was a full rebuild.

Native 55/55, forge trials 2/2.
