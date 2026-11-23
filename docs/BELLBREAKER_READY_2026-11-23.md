# Bellbreaker readiness pass, 23 November 2026

The owner asked for three things: fix the unnatural twisting of the Bellbreaker model, give him about as many moves as the Funeral Regent (each with a cooldown, none allowed to degrade the model), and spend Hugging Face quota on refining the boss, improving the arena and performance. Launch as before: `./scripts/bosslab-game` → Challenge → The Bellbreaker, or `BOSSLAB_BOSS=bellbreaker BOSSLAB_ARENA=forge ./scripts/bosslab-unreal play`.

## Why the model twisted

The close three-quarter study camera (`BOSSLAB_BB_BODY_CAMERA=1 ./scripts/bosslab-unreal capture bellbreaker-study`, new this pass) showed three distinct faults:

1. **Waist wringing.** The retargeted HY clips spin the shoulder girdle far from the hips, and the presentation added up to 52° of chest turn plus 34° of impact brace on a single bone (`spine_02`). Measured chest-versus-hip twist reached 47° (Hammer Fall, Quake) and 61° (Forge Sweep), all concentrated at one joint, so the apron and waist skin wrapped like a candy wrapper.
2. **Buried head.** Head pitch reached 79° from level in the slams; the face disappeared behind the shoulders and arms.
3. **Folded squat.** The slam crouch brought the hips down to 56% of standing height; thighs folded past 90° and the apron/thigh skin smeared into streaks.

## The anatomy governor

`GovernBellbreakerAnatomy` (WardenBellbreaker.cpp, step 3b) runs on every frame after the clip, stance layering and turns, and before the floor, hammer and hand solvers. Every move, old and new, passes through it, so no move can exceed these limits:

| Limit | Value |
|---|---|
| Hips relative to facing (outside the walk; hips lead 40% of a big chest turn) | ≤ 28° |
| Chest twist relative to hips, spread 14/20/22/22/22% over `spine_01`–`spine_05` | ≤ 32° |
| Head yaw from facing / neck turn from chest | ≤ 18° / ≤ 40° |
| Head pitch (down / up) | ≤ 22° / ≤ 18° |
| Hip height above the lower ankle (legs re-solved to the same ankles) | ≥ 78% of standing |

Study log after the change (four original moves): chest twist in 47–61° → out 32° (spread over five bones instead of one), head pitch in 42–79° → out 22°. The close camera shows the face visible through the Sweep and the Quake crouch, the torso upright over the hips, and much less apron smearing. Hands still reach the haft (worst left-hand gap 4.5 cm in the Quake, 0 cm elsewhere); no body or floor intrusions. The overhead hoist still turns the back toward a front-left camera, which is the natural hoist silhouette rather than a twist.

## Fourteen moves, each with a cooldown

Moves are engine-owned rows of `WardenRules::Strike` (Bellbreaker 20–33, `BossMoveCount` 34). Every row has a repeat lock (`RepeatLock`, enforced by `FWardenFighterState::Affordable`), a distance band and a punish pause. The fixed, labelled rehearsal (no learning, no input reading) walks a 14-step sequence per phase; a step whose move is still cooling down is skipped at once, and a step that needs room (Charge, Fling, Striding Fall) is skipped after half a second when the player is too close.

| # | Move | Windup/active/recovery (ticks @60) | Cooldown | Answer |
|---|---|---|---|---|
| 20 | Hammer Fall | 84/12/94 | 10 s | roll |
| 21 | Forge Sweep | 68/18/80 | 8 s | roll, back off |
| 22 | Bell Quake | 106/4/108 | 16 s | jump or roll the crest |
| 23 | The Bell Breaks (phase change) | 90/4/88 | — | blast |
| 24 | **Backhand Toll** (sweep from the left) | 50/16/78 | 9 s | roll |
| 25 | **Anvil Stamp** (300 cm boot blast, anti-hugging) | 44/4/62 | 12 s | step out, roll or jump |
| 26 | **Shoulder Charge** (6.4 m ram) | 58/28/72 | 14 s | roll sideways |
| 27 | **Rising Toll** (bell dragged low, upswing) | 56/14/84 | 10 s | roll |
| 28 | **The Toll** (sound ring at body height) | 72/4/76 | 20 s | **roll only** — jumping does not clear it |
| 29 | **Slag Fling** (three molten globs on glowing marks) | 60/6/72 | 15 s | leave the marks |
| 30 | **Held Note** (delayed overhead) | 132/12/94 | 14 s | do not roll early |
| 31 | **Forge Cyclone** (phase two, one full turn) | 62/48/96 | 22 s | back off |
| 32 | **Death Knell** (phase two, three slams then a crest) | 76/64/110 | 26 s | stay off the mark, jump/roll the crest |
| 33 | **Striding Fall** (lunging overhead, 3.8 m) | 70/12/96 | 12 s | roll |

The weapon path for each new move is one function (`NewMovePose`) that is both the drawn hammer and the engine hit path, so what you see is what hits. The body takes existing retargeted takes (sweep_lr, stamp, shoulder_charge, cut_heavy, toll, fling, overhead, quake) layered over the planted stance, then the governor, then the two-handed grip solver; the Cyclone turns the whole body with the bell by the same engine angle (`CycloneSpin`).

## Hugging Face work (free Spaces, token inline only)

* **Sound:** 15 effects in 8 families from Stable Audio Open (toll ring, stamp quake, slag fling/land, cyclone whoosh, charge rumble, upswing scrape, triple knell), trimmed from the Space's 47 s padding to their length with a 0.35 s fade, peak −1 dBFS. Prompts and timing: `artifacts/audio-bellbreaker-moves-2026-11-23/*.json`.
* **Arena:** FLUX.1-schnell concept images → TRELLIS.2 meshes (≈300k triangles each) → `prep_arena_prop.py` decimation to 12–16k triangles → `ue_import_readiness.py`. A fallen cracked bell, a clay casting mould and an oak frame with a hanging test bell stand at the edges of the forge floor, no collision. Inputs, previews and reports: `artifacts/art/bellbreaker-arena-props-2026-11-23`.
* **Performance:** the Bellfounder skin had a single 180k-triangle LOD; `ue_import_readiness.py` generated three LODs (reversible with `regenerate_lod(mesh, 1)`). Arena props were decimated ~95% before import.

## Verification

* Native Bellbreaker suite 10/10, including the new `BossLab.Bellbreaker.ReadinessMoves` (14 rows, each with a cooldown longer than the move, sane bell paths for every age, Toll hit when standing or jumping and avoided by a roll, Stamp radius, Slag landing, Knell blasts) and `RehearsalUsesEveryMove` (all 14 moves commit, phase two reached, nothing outside the Bellbreaker's rows).
* Full native suite 55/55 (one engine HTTP connectivity warning); forge trials `WardenAssetTrial.BellbreakerForge*` 2/2.
* Close-camera captures of all moves; governor statistics logged per move (`BOSSLAB BELLBREAKER governor after …`). Before/after close-ups, the new-move sheet, the wide prop check and the study logs are in `artifacts/unreal/bellbreaker-ready-20261123` (capture frames deleted after inspection).
* Study intrusion results after the Charge grip fix: no floor intrusion on any move; body intrusion 0 cm on all moves except Anvil Stamp 3.8 cm and Death Knell 6.1 cm; left-hand gap ≤ 11.5 cm on every move.
* **Cyclone guide-hand fix (same day).** The body and bell spin together, but two steps still aimed by the unspun actor facing: the weapon/grip solver (elbow poles, haft mount, clearances) and the chest-turn step that lines the shoulders up with "his front". Mid-turn the chest was twisted back toward the old facing and the left hand slid ~55 cm along the haft past the right hand (logged as a 65.5 cm socket gap). Both now use the spun body facing (`WYaw`, actor yaw + `CycloneSpin`). Worst left-hand gap in the Cyclone: 65.5 → 0.1 cm; both hands stay on the haft through the turn (`cyclone-grip-fixed.jpg`). Native 55/55, forge 2/2.
* Five forge props placed (cracked bell, casting mould, bell frame, shard pile, crucible; 62k triangles total). A generated bell rack was rejected (no legs; it would float).

## Performance (not a valid measurement this pass)

Two 720p performance-preset forge benchmarks: 24.04 ms mean / 48.87 ms p95 (2,323 frames) and 26.10 ms / 52.05 ms (2,141 frames). Both ran while a stale BossLab `CrashReportClient` from 20 November (pid 28339) held a core at 100% and macOS `mobileassetd`/`modelcatalogd` were busy (load average 14.6). The auto-mode permission check refused to close that reporter, so these numbers are confounded and are not compared with the 20 November 51–59 FPS runs. Close the stale reporter(s) and re-run `BOSSLAB_BOSS=bellbreaker BOSSLAB_ARENA=forge BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal benchmark 720p` to measure the LOD and prop-decimation changes.

## Not yet done / known limits

* Not owner-played. Move timings, cooldowns and damage are first-pass values.
* The new moves reuse existing HY takes for the body; Charge and Cyclone slide the planted feet with the capsule (no stepping) and the Fling/Toll takes are not bespoke.
* Generated sounds were not listened to by a person.
* Performance numbers below are single local runs on a loaded Mac.
