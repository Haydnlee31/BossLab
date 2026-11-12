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

## Second round: foot locking and gait review (2026-11-09, later)

The owner said to keep refining wherever I saw room.

- **Per-direction play-rate trims** (`GaitTrim`). A sweep showed rate 1.0 was already the best sideways (0.20) and backwards (0.09). The leftover slide was built into the clips, so the trims stay at 1.0.
- **Foot locking while ready** ([WardenSword.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenSword.cpp)):
  - **Plant:** a foot locks when the clip's own foot is nearly still over the floor (horizontal speed under 60% of travel) and low. The lock pins it in world space with leg IK while the ankle height and foot rotation stay the clip's.
  - **Release:** when the clip lifts or moves the foot, it eases back onto the clip over 6 ticks. A 28 cm × scale stretch limit forces a release if needed.
  - **Detection, first try:** plant was detected by height alone. With the boss's slowed full stride, that kept feet "planted" into the swing and gave 5 forced releases and foot-speed spikes of 4.5× travel. Plant is now detected by foot speed.
  - **Results:**

    | Case | Planted-foot slip | Peak foot speed | Forced releases |
    |---|---|---|---|
    | Player forward | 0.01 | 2.79× | 0 |
    | Player locked-on strafe | 0.00 | 2.79× | 0 |
    | Boss forward | 0.04 | 3.14× | 0 |
    | Boss backward | 0.00 | 2.79× | 0 |
    | Boss diagonal | 0.03 | 3.13× | 0 |
    | Boss sideways | 0.13 | 3.24× | 0 |

    The boss strafe clip shuffles low, so part of each step eases along the floor. The test thresholds are under 15% slip, peak foot speed under 4×, and at most 2 forced releases.
- **Gait review capture.** `./scripts/bosslab-unreal capture gait` scripts locomotion with a camera that tracks side-on to the line between the fighters:
  - the boss walks in, backpedals and circles;
  - the player walks in, strafes while locked on and backs off;
  - the boss turns on the spot.

  A first version used a fixed, far camera and was replaced; the fighters were tiny and walked out of frame. Inspected sheets: `gait-boss-walk-sheet.png`, `gait-player-strafe-sheet.png`, `gait-boss-legs-closeup.png` (in `artifacts/art/animation-feel-2026-11-09/`). They show stepping, planted feet, and the boss facing the player while backpedalling and circling.
- **Regent phase-change ring.** Now a low, uneven ring of 18 flames spreading outward, replacing 10 tall narrow cards that read as ice spikes (`study3-wakes-ring-sheet.png`).
- **Tests:** native suite 29/29 after this round.

## Limits

- **Feel.** Not owner-tested. Feel is the real acceptance test.
- **Clips.** Strike, roll and Regent poses are still procedural keys. These fixes improve how motion is fed, not authored animation quality.
- **Sideways foot slip.** The boss's sideways walk is still the weakest case (0.13 after foot locking), because its strafe clip shuffles low.
- **Default Warden behaviour.** The default Warden now faces the player while repositioning. That changes its look in the default rehearsal, but not its move order, timing or damage; the determinism and rehearsal tests still pass.

## Third round: player locomotion feel (2026-11-13)

The owner said combat still felt stiff compared with Elden Ring, mostly because of the player's movement animation. I added a scripted review capture and made three passes of fixes, each checked against a new capture.

**Review capture:** `BOSSLAB_OUTFIT=revamp BOSSLAB_BOSS=regent ./scripts/bosslab-unreal capture feel` films the player side-on for 24 s. The sequence is:
- a run in a circle;
- two hard 180° reversals;
- a sprint and a stop;
- two rolls;
- the three-cut chain;
- a sprint into a running cut;
- a jump.

It uses the normal action acceptance and costs. Sheets are in `artifacts/art/feel-2026-11-13/`.

### What was stiff

- **The sword was fixed in place.** While walking, running or sprinting, both hands were IK-pinned to one fixed guard point in mesh space. The torso bobbed under a blade that never moved.
- **No body response to movement.** There was no lean on starts or stops and no bank into turns.
- **Sprint looked like walking.** The sprint used the same upright guard as the walk.
- **The idle was nearly frozen.** Standing still, the idle clip ran at 0.2× speed, because the slow stopping clock also applied at zero speed. The stance barely breathed.

### Fixes

All of these are in `WardenSword.cpp`. They are presentation only: no capsule, speed, timing or hitbox change.

- **Speed-driven sword carry.**
  - Running lowers the greatsword to a low forward guard.
  - Sprinting trails it low behind at the right side, two-handed.
  - The blend runs Guard → Low → Trail, so the blade swings past the outside of the body, never through the head.
  - The carry holds for 0.3 s before falling, so a quick reversal keeps the blade low instead of flapping it up to the guard.
- **Body response.**
  - Smoothed acceleration gives a forward lean on starts and a lean back on hard stops.
  - Speed adds a lean of up to 6° in a sprint.
  - Sideways acceleration banks the pelvis and spine into turns (up to 11°), with the hips shifting toward the inside of the turn.
  - The feet are re-solved to the clip, so they stay planted.
- **Hands ride the chest.** While ready, the hilt follows the chest bone's movement from the rest pose: stride bob, sway, lean and bank. Idle breathing now moves the arms.
- **Blade inertia.** A spring (stiffness 160, damping 17) offsets the hilt and tilts the blade against acceleration.
- **Head leads turns.** The head turns up to 22° into the turn rate.
- **Idle at its natural rate.** The idle clip now plays at 1.0×. The slow clock only applies through the last 60 cm/s of a stop.
- **Swings start from the pose you are in.** The player always winds up from the drawn ready pose (`bPoseFromLast`), so a cut from a sprint starts from the trailing carry without a snap to guard.

### Results

- **Native suite:** 35/35.
- **Player:** forward slip 0.00 and locked-on strafe slip 0.00.
- **Grip error:** 0.000 cm on all sword poses.
- **Not owner-tested.** Feel is the real acceptance test.
- **Unchanged:** new strike, roll or locomotion clips are still needed for authored-quality motion. These fixes change how the existing motion is layered.
