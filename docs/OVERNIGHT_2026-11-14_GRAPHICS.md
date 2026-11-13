# Overnight graphics pass (2026-11-14)

This pass was made by the graphics agent. It changes presentation only: combat rules, timing and collision are unchanged. Each feature is its own commit, so the owner can keep or revert each one. Not owner-reviewed.

## Toggle

`BOSSLAB_GRAPHICS` (read in `WardenGraphics.h`):

- unset: every feature on (default).
- `off`: every feature off (the previous look).
- a comma list of `-name` entries turns single features off, e.g. `BOSSLAB_GRAPHICS=-volumetric,-rim`. Names: `volumetric`, `grade`, `rim`, `sparks`.

Review setup: `BOSSLAB_OUTFIT=revamp BOSSLAB_BOSS=regent BOSSLAB_ARENA=dungeon ./scripts/bosslab-unreal capture regent-study` (or `play`). Add `BOSSLAB_GRAPHICS=off` to compare.

## Commits

| Commit | Feature | Where | Scope |
|---|---|---|---|
| 210fe7f | Volumetric fog light shaft | WardenDungeon.cpp, WardenGraphics.h | Dungeon only. The height fog turns on volumetric fog (scattering .55, extinction 2.2, 42 m). The oculus moonlight key scatters at 4x, so it becomes a real shaft through the haze. The shadowless brazier lights scatter at .35, which gives a faint warm haze. |
| 91e7f33 | Filmic grade, bloom, contact shadows | WardenDungeon.cpp | Dungeon only. Film toe .57, shoulder .24, slope .9. Bloom 0.95 with threshold 1.2 and size 3.2, so the bloom favours fire and soul fire over lit stone. Warm highlight gain over the existing cool shadows. Vignette .55 to .68. Light chromatic fringe .35. Screen-space contact shadows (length .035) on the key light. Exposure is unchanged: eye adaptation is already off project-wide. |
| 63f609d | Rim lights | WardenEffects.cpp | All arenas. Each fighter gets one shadowless cool spot behind it, opposite the camera, raised and aimed at the chest. The spot is on lighting channel 1 only. The fighters' meshes are switched to channels 0 and 1, so the rim never lights the floor or walls. Two extra movable lights. |
| 26d5b8c | Hit sparks | WardenEffects.cpp | All arenas. Each blood burst throws 16 camera-facing streaks, stretched along their velocity. They fall under gravity and bounce once on the floor. Material: `M_RegentSpark`, falling back to the heal mote. The sparks are driven from the existing blood burst ring, so they add no new state and no header change. |

## Evidence

The evidence is in `artifacts/art/overnight-2026-11-14/graphics/` (local, gitignored):

- `ab-{060,240,450,640,820}.jpg`: matching regent-study frames, `BOSSLAB_GRAPHICS=off` on top and the first "on" tuning below. Rim, fog and grade were raised after this pass; `on2/` holds the final frames.
- `on2-sheet.jpg`: every 30th frame of the final regent-study capture.
- `on2-hits.jpg`: frames 600 to 660, cropped, around a landed blow with sparks and blood.
- `feet-640.jpg`: shows that the bright spot at the player's feet was already there before this pass. It is not caused by the rim light.
- `bench/`: benchmark JSONs, described below.

All capture frames were deleted after inspection.

## Measured cost

These were `benchmark 720p` runs with `BOSSLAB_QUALITY=performance` and the revamp outfit, regent boss and dungeon arena. They ran back to back on a shared machine (load average 6 to 10, with the QoL agent active), so they are not isolated. Reports are in `bench/`.

| Run | Frames | Mean | p95 |
|---|---|---|---|
| all on (`on-1`) | 2731 | 20.66 ms | 31.03 ms |
| all on (`on-5`) | 2682 | 21.01 ms | 34.65 ms |
| off (`off-5`) | 3289 | 17.11 ms | 17.29 ms |
| all on except volumetric (`no-volumetric-6`) | 2980 | 18.92 ms | 26.78 ms |
| `off-2`, `on-3`, `off-4` | 987 to 3341 | 16.8 to 24.5 ms | |

The `off-2`, `on-3` and `off-4` runs are not usable for comparison. They overlapped a mis-scripted copy loop, and two of them ended early (demo_tick 1625).

The estimated cost of the full pass is about 3.5 to 4 ms per frame at 720p. About 2 ms of that is volumetric fog. Grade, contact shadows, rim lights and sparks together cost about 1.8 ms; the two extra movable rim lights are the likely main part of that. Both estimates are noisy. If performance matters, use `BOSSLAB_GRAPHICS=-volumetric` first; a lower-cost alternative is to raise `r.VolumetricFog.GridPixelSize` (coarser froxels) in the performance preset, but that was not tried.

## What looks different and what is unverified

- The grade and volumetric fog are subtle in captures. The hall reads a little deeper and hazier, and the shaft is softer. The existing additive cone mesh still does most of the visible shaft. Removing that cone now that the fog scatters is a possible follow-up, but it was not tried.
- The rim light is modest on the dark revamp costumes: it brightens the edges of the back and shoulders. It may want to be stronger or warmer. This needs owner review in motion.
- Sparks are small and fast. In 30 fps captures they show only on one or two frames per hit. Not reviewed at real frame rate.
- Not owner-tested. No 60 FPS claim. The benchmarks ran on a shared machine while another agent was working.
- The native suite passed at 38/38 with all four features on. The QoL agent added tests in the same night.
