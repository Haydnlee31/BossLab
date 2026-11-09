# Animation feel pass, 2026-11-09

The owner said the boss animation "still feels a bit weird in how it moves, players as well", and asked me to optimise it. The pass measured the motion first, then fixed how motion is fed to the existing clips and poses. No new animation clips were authored, and combat timing, reach and hit detection are unchanged.

## What was wrong (measured)

New native tests in [AnimationTests.cpp](../unreal/BossLabWarden/Source/BossLabWarden/AnimationTests.cpp) found three problems:

1. **Skating feet.** While walking, the planted foot slid at **65–70% of body speed**, for both the player and the boss. Three causes:
   - a permanent 28% pose low-pass, which damped every stride;
   - the boss's speed fed to the blendspace without its 1.35× scale;
   - below the walk samples (300 cm/s), the blendspace mixing idle into walk, which gives a short stride at full cadence.
2. **Bosses turning their back.** The bosses faced their direction of travel, so to back off or circle they turned round and walked away.
3. **Judder.** Bodies, blades and the follow camera only moved on the 60 Hz combat step. At 45 rendered fps, frames alternately carried one or two steps, so the drawn speed varied **35% frame to frame**.

## Fixes (all presentation or facing; combat rules unchanged)

- **Speed warping** ([WardenSword.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenSword.cpp)):
  - the blendspace speed is divided by the actor's scale;
  - below 300 cm/s the full walk stride plays with a slower clock instead of blending toward idle, and the last 60 cm/s fade to idle;
  - the clip play rate is 1.1, chosen from a sweep across 1.0–1.4 (below).
- **Pose smoothing only around changes of action.** The smoothing now applies only around walk, stop and commit transitions (10 ticks easing from 0.28 to 1), not on every frame.
- **Bosses face the player.** They now backpedal and strafe on the directional clips. The Warden's target is the player, used for facing only.
- **Turning on the spot steps.** When a boss rotates without walking, the rotation feeds the side-step clips as small shuffle steps, instead of spinning the idle pose like a turntable.
- **Render interpolation** ([WardenRenderBlend.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenRenderBlend.cpp)). Between fixed steps, the drawn root, bone pose, blade and follow camera blend from the previous step to the current one by the leftover accumulator time.
  - **Before each step:** the exact step state is restored, so hit sweeps, foot anchors and determinism are untouched.
  - **Not blended:** teleports and resets.
  - **Cost:** at most one step (16.7 ms) of visual latency, which is standard fixed-timestep practice.

## Results (native suite 29/29)

- **`BossLab.Animation.PlantedFeetHoldWhileWalking`**: planted-foot slip as a fraction of travel speed.

  | Case | Before | After |
  |---|---|---|
  | Player forward | 0.65 | 0.07 |
  | Boss forward | 0.65 | 0.10 |
  | Boss backward | 0.70 | 0.10 |
  | Boss sideways | 0.70 | 0.20 |

  The boss now keeps facing its target in every direction: yaw 0 instead of 180 or 90.
- **Play-rate sweep:**

  | Rate | Player | Boss forward | Boss backward | Boss sideways |
  |---|---|---|---|---|
  | 1.0 | 0.14 | 0.09 | 0.09 | 0.23 |
  | **1.1** | **0.07** | **0.10** | **0.10** | **0.20** |
  | 1.2 | 0.08 | 0.16 | 0.16 | 0.28 |
  | 1.3 | 0.15 | 0.28 | 0.22 | 0.32 |
  | 1.4 | 0.23 | 0.35 | 0.32 | 0.39 |

- **`BossLab.Animation.SmoothBetweenFixedSteps`**: at 45 fps the drawn boss advances at an even 260 cm/s, with per-frame speed variation 0.000. The fixed-step actor varies by 0.354.
- **`BossLab.Animation.TurningOnTheSpotSteps`**: turning at up to 90°/s, both feet step, with at least 20 cm of lift at boss scale. A first version used 30 cm (a full walking stride) and was reduced.
- **Regressions:** every existing test still passes, including frame-partition determinism (60 vs 30 fps give an identical fight), the Regent roll and pose tests, and the dungeon test.
- **Captures:** 24 s Regent exchange captures (`artifacts/art/animation-feel-2026-11-09/`) were inspected and show nothing broken. The scripted fighters stay pressed together, though, so the stills say little about gait; the measurements above are the evidence.

## Limits

- **Feel.** Not owner-tested. Feel is the real acceptance test.
- **Clips.** Strike, roll and Regent poses are still procedural keys. These fixes improve how motion is fed, not authored animation quality.
- **Sideways foot slip.** The boss's sideways slip (0.20) is the weakest case. The strafe clips' natural speed differs from the forward clips'.
- **Default Warden behaviour.** The default Warden now faces the player while repositioning. That changes its look in the default rehearsal, but not its move order, timing or damage; the determinism and rehearsal tests still pass.
