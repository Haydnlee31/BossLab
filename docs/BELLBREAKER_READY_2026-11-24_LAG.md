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
