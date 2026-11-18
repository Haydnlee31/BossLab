# Bellbreaker greybox fight, 2026-11-18

The owner asked for a playable greybox fight built around the **Bell Quake**: the boss slams his bell into the floor and sends out a shockwave. A player who neither jumps nor rolls through the shockwave is stunned.

The boss follows a fixed, labelled sequence and has no AI. It is opt-in and runs in the editor game only, like the Regent. The default Warden fight, its tests and the packaged app are unchanged.

## Play it

```sh
# In the Hearth A2 forge (recommended):
BOSSLAB_BOSS=bellbreaker BOSSLAB_ARENA=forge BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance BOSSLAB_HEARTH_AO=1 ./scripts/bosslab-unreal play
# In the default ring arena:
BOSSLAB_BOSS=bellbreaker BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

From the title screen choose **Challenge**, then **Begin challenge**; the select screen now names the Bellbreaker. **Creative** works the same way.

- **Start at the phase-two threshold:** add `BOSSLAB_BB_PHASE=2`. The Bell Breaks plays first, then every Quake sends two crests.
- **Where it runs:** `play`, `capture` and `benchmark`. Package modes reject the flag.
- **Arena:** the **Hearth A2 forge** with `BOSSLAB_ARENA=forge`, or the default ring arena without it. See [In the forge](#in-the-forge-hearth-a2).
- **Assets:** the boss rig, clips, sounds and ring material are local imports. The scripts are listed in `artifacts/art/bellbreaker-boss-2026-11-18/README.md`. Without the rig the capsule fights unseen, and a warning is logged.

## In the forge (Hearth A2)

`BOSSLAB_ARENA=forge` (`-BossLabForgeFight`) builds the forge using the A2 walkthrough builder. That includes the art, invisible field walls, work-island and camera collision, lights, fog, colour grade, forge fire, molten channel and steam.

The mode then turns the walkthrough state off and runs the normal encounter setup in it. It skips the default ring arena, its lights and its sky.

- **Start positions:** the player starts at (0, −5 m) facing the furnace; the Bellbreaker stands at (0, +4 m) in front of it.
- **Launcher checks:** the launcher requires `BOSSLAB_BOSS=bellbreaker` and refuses to start unless every mesh in the A2 manifest has been imported.
- **The A2 walkthrough** (`./scripts/bosslab-smeltery`) is unchanged.
- **Menu fix:** the menu's **Begin challenge** called `StartRegentSession`, which turned the Regent on whenever it was off. With the Bellbreaker that would have enabled both bosses. It now keeps the Bellbreaker, in either arena.

## Moves

Moves are engine-owned rows 20–23 of `WardenRules::Strike`, defined in [WardenBellbreaker.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenBellbreaker.cpp). Times are 60 Hz ticks.

| # | Move | Wind-up | Active | Recovery | Damage | Notes |
|---|---|---|---|---|---|---|
| 20 | Hammer Fall | 54 | 6 | 70 | 34 | Overhead slam. The bell stays embedded for 40 ticks: the main punish window. |
| 21 | Forge Sweep | 46 | 10 | 52 | 28 | A low arc from his right round to his left, about 4.7 m out. |
| 22 | **Bell Quake** | 70 | 4 | 80 | blast 30 / crest 10 | See below. The bell stays embedded for 60 ticks. |
| 23 | The Bell Breaks | 60 | 4 | 56 | 30 within 4 m | The 50% health transition. It turns on phase two. |

- **Tracking:** every move tracks the player until 14 ticks before contact, then the aim locks.
- **Phase one sequence:** Fall, Sweep, Quake, Sweep, Fall, Quake.
- **Phase two sequence:** Quake, Fall, Sweep, Quake, Sweep, Fall.
- **Pauses:** 40 ticks after the slams and 24 after the Sweep. Phase two uses 60% of each.
- **Boss stats:** 900 health with phase two at 450; stance 8; scale 2.55 (4.6 m).
- **Capsule:** radius 48 × 2.55 = 122 cm. The default radius let the player stand inside his apron.

### Bell Quake

1. **Impact:** at contact the bell lands about 3.8 m ahead of him.
2. **Blast:** a player within 2.4 m of the impact takes **30 damage and a knockdown**, a kneeling stun of 66 ticks. Only roll i-frames avoid it; a jump does not.
3. **Crest:** a crest then runs along the floor from 1.2 m to 10 m at 850 cm/s, about 4 ticks to pass a player. A player it passes is **stunned for 84 ticks and takes 10 damage**, unless they are airborne (more than 30 cm up) or inside roll i-frames for *every* tick of the crossing.
4. **Twin Quake (phase two):** a second crest starts 45 ticks after the first. The plan said 30, but at 30 no second jump or roll could come out in time. At 45, all four answers work: roll-roll (through the roll chain), jump-jump, jump-roll and roll-jump.

### Stun rule

The stun is new and engine-owned: `FWardenFighterState::Stun`, in `WardenCombat`. It is the same for every controller.

- **What it is:** a long, committed `Hurt`. The player cannot move, attack, roll or heal, stamina does not regenerate, and buffered input is dropped.
- **Breaking it:** any flinching blow ends it at once and becomes the ordinary 18-tick hurt, so a stun never guarantees a combo.
- **Immunity:** after a stun ends or is broken, the player cannot be stunned again for 300 ticks.
- **No extensions:** a stun already running cannot be restarted, so the second crest only chips.
- **Refused when:** the player is dead, invulnerable (roll i-frames) or immune.
- **Presentation:** the player plays the HY `stun` clip (a dazed stagger with a hand to the head), or `stun_kneel` after the blast, over the whole body. The HUD shows STUNNED or KNOCKED DOWN.

## Presentation (no rules)

- **His body:** the rigged TRELLIS model (`SKM_BellbreakerRig`) as a separate actor. It follows the hidden combat capsule and holds the bell hammer through the solved grip.
- **Clips:** the retargeted HY clips are time-warped so the clip's slam frame lands on the engine's contact tick: `hammer_overhead`, `sweep_rl`, `bell_quake` and `hammer_overhead_s1`. Idle and walk loop with the hammer; stance breaks use `stagger` and death uses `death`.
- **Hit path:** the hammer's reach comes from an **analytic, engine-owned** path (grip to bell, five swept samples), never from the clip. In the captures the visible bell lands close to the hit path at contact, but somewhat to his right of it.
- **Rings and sounds:**
  - The crest rings use the engine's radius, so what you see is what resolves.
  - The sounds come from the generated Stable Audio set: clapper tell, swing whoosh, floor scrape, ground slam, shockwave, bell crack, body hit and ear ringing.
- **HUD and camera:** the HUD reads THE BELLBREAKER, Founder of the Cracked Peal, with GREYBOX and the phase. The lock-on camera sits higher and further back (socket 210, arm 720).

## Checks

**Native suite: 50/50.** That is the 45 existing tests (the Regent table test now checks that the Regent rows end where the Bellbreaker's begin) plus 5 new ones:

| Test | What it shows |
|---|---|
| `BossLab.Bellbreaker.StunRules` | Stun length, no actions, no stamina regeneration, break on hit, immunity, no restart, roll i-frames refuse it, readable telegraphs. |
| `BossLab.Bellbreaker.QuakeJumpOrRollOrStun` | At 5 m: standing gives 10 damage and 1 stun, and mashing roll does nothing. A jump 18 steps early or a side roll 12 steps early gives 0. A jump far too early lands and is stunned. At 12 m nothing happens. Under the bell, standing or jumping takes 30 plus the knockdown; a timed roll avoids it. |
| `BossLab.Bellbreaker.TwinQuake` | Standing gives 20 damage and 1 stun. Answering only the first crest still gets stunned. All four answer pairs come out clean. |
| `BossLab.Bellbreaker.RollBeatsHammer` | Hammer Fall does 34 standing and 0 with a timed roll; Forge Sweep does 28 and 0. |
| `BossLab.Bellbreaker.RehearsalUsesEveryMove` | All 4 moves commit, phase two arrives, and only Bellbreaker rows are used. |

`WardenAssetTrial.HearthA2` also passes (1/1). **`WardenAssetTrial.BellbreakerForge`** (1/1, needs the local A2 and Bellbreaker imports) builds the forge fight and checks four things:

- it runs in encounter mode with all 56 A2 dressing actors and none of the default ring walls;
- the start positions are correct;
- in 60 s of rehearsal he commits 20 times and uses all 4 moves (1 stun, 7 crests avoided), never getting stuck on the work islands, and both fighters stay inside the field;
- the menu's Begin challenge keeps the Bellbreaker.

A 24 s capture of the forge fight was inspected and saved as `evidence/greybox-forge-fight.png`; the raw frames were deleted.

**Captures.** Two 24 s fixed-30 fps captures with the scripted practice player were inspected; the evidence is in `artifacts/art/bellbreaker-boss-2026-11-18/evidence/greybox-*.png`, and the raw frames were deleted.

- **Phase two:** the transition, then a Twin Quake. The bot rolled the first crest, was stunned by the second, and recovered after the full stun.
- **Phase one:** Fall, Sweep, then Quake. With the wider capsule the closest approach is 156 cm, capsule to capsule.

## Known gaps

- **Not played by a person yet**, so feel, timing, camera and difficulty are unverified.
- **Camera:** the lock-on camera crops his head during the overhead wind-ups at close range.
- **Visible bell vs hit path:** the visible bell and the engine's hit path differ by up to about a metre sideways.
- **Left hand:** it is not on the haft (no IK).
- **Clip transitions:** clips switch without blending, which can pop.
- **Camera in the forge:** at capsule contact, which is where the practice bot fights, he fills the screen. The camera may also be pulled in by the forge's camera collision behind the player. This needs a human playing at normal spacing to judge.
- **Audio:** the generated sounds have not been listened to.
- **Moves left out:** the other planned moves (Tolling Stamp, Anvil Shoulder, Quench, Hook and Haul, Slag Fling, Death Knell, Peal of Ruin, Great Toll) are not built. The owner's open questions in `BELLBREAKER_MOVESET_PLAN.md` still apply.

## Animation quality pass (owner request, 2026-11-18)

The owner reported glitches: parts of the boss went into his own model and into the ground, and the bell made no sparks or metal-friction sound when it swept the floor. All the fixes below are presentation only, in `AnimateBellbreakerView` ([WardenBellbreaker.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenBellbreaker.cpp)). Rules, timing and hit volumes are unchanged.

**New pipeline:** the clip is sampled on a hidden skeletal mesh. The rendered body is a `UPoseableMeshComponent` that receives a corrected pose each frame, in this order:

1. **Crossfade:** a 0.2 s blend from the last shown pose whenever the clip changes, instead of a pop. Death uses 0.3 s.
2. **Sweep layering:** the HY sweep takes spun and splayed his whole body: a lunge for a 1.8 m figure, flailing at 4.6 m. Over his planted idle stance, the legs keep 35% of the clip, the hips 45% and the spine 60%; the arms keep the full clip. Take s1 is used, because s0 sprawled almost flat.
3. **Grounding:** the HY hops became leaps of about 1 m at 2.55× scale. The Quake wind-up lifted both feet about 40 cm (mannequin) off the floor, with the pelvis at 128 against 96 standing. Now, whenever both feet are off the floor the pelvis comes down by the gap, so his lowest foot stays planted. Stepping and crouches are unchanged.
4. **Arms out of the belly:** two-bone IK keeps his hands at least 27 cm and his elbows at least 23 cm (mannequin) from the torso axis. The clips were made for a slim mannequin.
5. **Floor lift:** if knees, hands, elbows, hips or head would go below the floor (kneels, the death fall), the whole body rises. It rises at once and settles slowly.
6. **Hammer solve:** the hammer is no longer glued to the fist.
   - **Grip:** it sits in the right palm.
   - **Aim:** during attacks it aims along the engine's own bell path, so the visible bell and the hit agree. The aim blends in over 10 ticks and out over the last 22 ticks of recovery.
   - **Clearance:** the haft and bell are pushed out of a 1.05 m body capsule around him, and the bell's lowest rim point is kept at or above the floor.
7. **Left hand on the haft:** two-bone IK puts the left hand 70 cm below the right hand on the haft. It fades out when the target is beyond reach, and stays off during stagger and death.
8. **Bell on stone:** these trigger when the bell rim comes within 14 cm of the floor.
   - **Dragging:** a stream of sparks is thrown back from the motion (`M_RegentSpark`, 128 instanced streaks with gravity). The generated `bell_scrape` sound plays, alternating takes, at most once every 1.1 s.
   - **Landing hard:** a radial spark burst plus the `bell_hit_anvil` clang.
   - **Removed:** the old move-timed scrape sound.

**Review tool:** `BOSSLAB_BOSS=bellbreaker ./scripts/bosslab-unreal capture bellbreaker-study` captures each move once, side-on, with the player standing in reach. It logs the worst remaining intrusions per move. Final numbers:

| Move | Floor | Body capsule |
|---|---|---|
| Hammer Fall | 0 cm | 15.5 cm |
| Forge Sweep | 0 cm | 12.8 cm |
| Bell Quake | 0 cm | 22.3 cm |
| The Bell Breaks | 0 cm | 7.5 cm |

The body capsule is deliberately generous, so those residual figures mean the haft grazes his silhouette rather than passes through it.

**Evidence** is in `artifacts/art/bellbreaker-boss-2026-11-18/evidence/anim-*.png`: the Quake before and after grounding, the layered Sweep, and the forge fight afterwards. All raw frames were deleted.

**Checks:** native 50/50 (one engine HTTP-connectivity warning, not a test), `WardenAssetTrial.BellbreakerForge` 1/1 and `HearthA2` 1/1.

**Still open:**

- His motion is still generated, not authored; the pushes are corrections, not keyframed polish.
- The right hand is not rotated to wrap the haft.
- The spark and scrape sounds have not been listened to.
- The camera at close range has not been tuned.

## Hands pass (owner request, 2026-11-18)

A close-range study (`BOSSLAB_BB_STUDY_DIST=560 … capture bellbreaker-study`) showed three hand problems:

- open, clawing fingers that never closed on the haft;
- the left arm letting go and flailing whenever the haft was out of reach;
- wrists keeping the clip's angle, so the haft did not run through the fist.

### Root cause in the rig: his hands barely followed the hand skeleton

| Measure | Value |
|---|---|
| Hand-region weight on the **forearm** | about 40% |
| Hand-region weight on the fingers | almost none |
| Vertices dominated by the hand at all | 35 |

The mannequin's finger bones pointed forward and down, outside his much larger hanging mesh fingers.

### The rig fix: `rig/c8.json`, re-imported and retargeted (42 clips)

`rig_fit.py` gained two opt-in options:

- **`bone_scale`:** scales a bone's subtree about its head. Both hands use 1.15.
- **`wrist_cut`:** past each wrist plane, nothing follows the forearm or upper arm.

Also in c8:

- **Hand bones** re-rested 50° about the lateral axis, so the fingers run down the mesh fingers.
- **Hand bone tightened:** radius 0.045 and core 0.10.
- **Finger radius:** 0.035.
- **Fanning:** middle, ring and pinky moved 2.25, 4.5 and 6.5 cm toward the back of the hand to fan across his four mesh fingers. This was measured from a bone-overlay render; see `evidence/hand-rig-c8-finger-bones.png`.

**Result:** about 800 hand vertices, the forearm's share down to about 4%, and the pinky, ring and middle chains weighted.

### Presentation fixes (`AnimateBellbreakerView`)

- **Grip orientation:** each hand turns so its knuckle line runs along the haft. Its thumb side faces whichever end needs the smaller turn, with hysteresis, and the turn is capped at 100°.
- **Fists:** the fingers rest-reset and then curl 50°, 58° and 38° per joint, with the thumb at 22°.
  - **Palm side:** the right hand's palm side comes from its rest curl. The left hand uses the mirrored, negated sign; testing the left hand on its own had curled it backward into a claw.
- **Two hands share the haft:** if the left hand would fall short, the right hand moves toward it by the shortfall (up to 80 cm, eased).
  - **In reach:** the left hand takes the reachable haft point nearest its shoulder, 30–110 cm below the right hand.
  - **Otherwise:** it blends over about 0.2 s into a relaxed hang at his side.
  - **Grip easing:** the curl and the wrist turn scale with the blend, so the hand closes as it arrives.

### Results

**Study log:** the worst left-palm-to-haft gap while gripping is 3.5–6.9 cm (it was up to 1.1 m). Body intrusion is now 1.5–14.3 cm, and floor intrusion 0 cm.

**Evidence:** `evidence/hands-before.png` and `evidence/hands-after.png`.

**Tests:** native 50/50, the BellbreakerForge trial 1/1 and the HearthA2 trial 1/1.

**Still open:**

- The index finger and thumb are still approximate on the mesh (bone overlay).
- The TRELLIS fingers are coarse, so a closed fist is a rough shape, not a sculpted grip.
- Not yet tested by the owner.

## Camera and model v3 (owner request, 2026-11-18)

### Camera in the forge: giant framing

The human-scale lock-on rules made a 4.6 m boss fill the screen with his head cropped:

- at contact the camera socket and pitch collapsed toward the player;
- it always pitched down;
- it aimed at his capsule centre.

For the Bellbreaker only (`WardenPrototype.cpp`, `Giant`), the camera now does this:

| Setting | Behaviour |
|---|---|
| Arm length | 780 cm, rising to 1000 cm as you close in |
| Socket | (0, 70, 165), rising to 205 cm as you close in |
| Pair framing | a 32% midpoint offset keeps both fighters in frame |
| Aim | his chest, about 3.3 m up |
| Pitch | `0.55 × aim − 11 + 11 × closeness`, clamped to −28…+10, so it can tilt up under him |

In the forge captures he stays fully in frame from boots to raised hammer, with the player in front (`evidence/v3-forge-fight-camera.png`). At very close range the boss health bar still overlaps the player's legs.

### Model v3

The owner reported the head looked like a sponge and the arm proportions were off.

- **Head:** the v2 mesh had a tall block of hair that TRELLIS rendered as porous (`evidence/v2-head-sponge.png`).
- **Arms:** v2's oversized forearms came from my own "make him bulkier" edit.

**Input image.** I re-edited the original clothed A-pose with FLUX.1-Kontext, using the prompt saved in `inputs/v3-*.png.json`. It asked for a shaved head, a realistic weathered face with a short beard, natural strongman proportions, normal hands and arms 30° out, and kept the outfit.

- **Chosen:** seed 12 (`inputs/v3-12.png`). It keeps the pauldron, sash, apron, harness, holster and knee plates.
- **Brow band:** four attempts to add one back all produced helmets or caps (`v3band*`), so he is bald.

**Mesh.** TRELLIS.2 at resolution 1536 gives `trellis/boss-v3/model.glb`, shown in `evidence/v3-model-sheet.png`.

**Rig `rig-v3/v1.json`.** It uses the c8 approach with offsets re-measured for v3:

- **Arm joint offsets:** shoulder (±7.25, 0, −2.25) cm, elbow (∓4.75, 0, 0) cm, wrist (0, 0, −4.75) cm.
- **Hands:** scaled 1.05, because his hands are now normal-sized.

With the same finger fanning and 50° hand re-rest, the finger weights spread across index, middle, ring and thumb. The pose test is clean apart from one strap sliver (`evidence/v3-rig-*`).

`ue_import_bellbreaker_rig.py` now imports `rig-v3/out` by default. Set `BOSSLAB_BB_RIG_OUT=rig/out` for v2. All 42 clips were retargeted.

**Collision and clearance:**

- **Capsule:** radius 40 × 2.55 = 102 cm; v3 is slimmer.
- **Hammer clearance:** now an ellipse in his own facing frame, deep 55–60, wide 85–90, with a 38 cm head zone above 380 cm, and up to 8 passes. The old circle had flagged a haft held in front of his chest.

**Study, 640 cm camera:**

| Move | Body intrusion | Floor | Left-hand gap |
|---|---|---|---|
| Hammer Fall | 0 cm | 0 cm | 4.7 cm |
| Forge Sweep | 0.5 cm | 0 cm | 4.7 cm |
| Bell Quake | 0 cm | 0 cm | 5.9 cm |
| The Bell Breaks | 0.5 cm | 0 cm | 5.1 cm |

**Tests:** native 50/50, `BellbreakerForge` 1/1 and `HearthA2` 1/1.

**Still open:**

- The concept's iron brow band is missing.
- The beard is white rather than grey.
- The face is still TRELLIS-coarse up close.
- Not yet tested by the owner.

## Head, headband and stun length (owner request, 2026-11-18)

### Squashed head

The owner's in-game photo showed a squashed, tilted head.

- **Cause:** distance weighting gave the v3 face and beard 21–55% to the chest bone (`spine_05`), with almost nothing on the neck bones. Any head turn left half the face with the torso.
- **Fix:** `rig_fit.py` gained `head_own`. Inside a box around the head bone (±16 cm sideways, 32 cm forward, 20 cm back):
  - everything above 1.57 m (mannequin scale) and everything in front of the neck (the beard) goes to the head;
  - the neck itself blends `spine_05` → `neck_01` → `neck_02` → `head` from 1.47 to 1.57 m.

  The face and beard are now 98–100% head. In the head-turn test (`evidence/head-turn-before-after.png`) the head turns as one piece, where before the face smeared.
- **Clip caps:** the HY clips also throw the head far back. `AnimateBellbreakerView` now caps each of `neck_01` and `neck_02` at 14° from rest and `head` at 22°.

### Headband, modelled

`rig_fit.py` gained `headband`. Image-to-3D kept turning the band into a helmet, so it is modelled instead:

- **Fit:** for each of 64 angles around the head, the band's bottom and top edges are fitted separately to the measured skull, 3.5 mm out. The bottom edge is clamped to ignore the ear tops and the brow ridge, and the result is smoothed.
- **Shape:** it is tilted from the brow (1.738 m) to the back (1.745 m), 3 cm tall and 7 mm thick, with rounded edges and 14 domed rivets.
- **Skinning:** it is joined into the mesh, 100% on the head bone, in its own `Band` slot.
- **Material:** the importer gives that slot `M_BellbreakerBand`, a dark forged iron with world-space mottling, metallic 0.85 and roughness 0.46.
- **Config:** `rig-v3/v3.json`. The rig is re-imported (3 slots) and all 42 clips are retargeted.

Evidence: `evidence/headband-fit.png` and `evidence/forge-head-band.png`.

### Stun length

The owner wants a stun to last 1–2 s at most, after which the player moves.

- **Durations:** the shockwave stun is now 60 ticks (1.0 s, was 1.4 s) and the blast knockdown 72 ticks (1.2 s).
- **Walk-out:** in a stun's last 15 ticks (`WardenRules::StunWalkOut`), movement input ends it, as with late recovery. The 300-tick immunity still follows.
- **Tests:** `StunRules` checks both limits and the walk-out.

### Checks

| Check | Result |
|---|---|
| Native suite | 50/50 |
| `BellbreakerForge` trial | 1/1 |
| `HearthA2` trial | 1/1 |
| Study: body intrusion | ≤ 0.5 cm |
| Study: floor | 0 cm |
| Study: left-hand gap | ≤ 5.9 cm |

## Camera tilt, and the "can roll but not walk" report (2026-11-18)

### Camera

The owner said the camera still looked up too much. The giant lock-on camera now:

- sits at a raised socket (230 cm, rising to 290 cm up close);
- aims at his belt, about 2 m up;
- keeps the pitch between −30° and 0°, so it never tilts up.

Distance and height fit him in frame instead of tilt (`evidence/camera-look-down.png`).

### Movement bug, not reproduced

The owner reported that after a stun or other effects they could roll but not walk.

**Tests.** Two new tests could not reproduce it:

| Test | Path | Result |
|---|---|---|
| `MoveAfterStunAndHits` | Shockwave stun, blast knockdown, hammer hit and sweep hit, then the stick held | Walks 387 cm in 1 s every time |
| `RealInputAfterStun` | Real play path: a possessed player controller, lock-on, the menu-started challenge, roll mashed while stunned, `MoveIntent` input, stick back and sideways, in the ring and in the forge | Free in 0.75–1.03 s, then moves 290–450 cm in 1 s |

**Stuck guard** (`WardenEncounter.cpp`):

- **Logging:** if the stick is held and the player has not moved for 30 ticks, it logs `BOSSLAB STUCK-STATE` with the action, age, stun ticks, gap, hit-stop, pending input, sprint, time scale and lock.
- **Blocker check:** when the player is free to act, it also sweeps the capsule and logs `BOSSLAB STUCK`, naming the blocking actor and component, whether the player started inside it, and the penetration depth.
- **Push-out:** if the player started inside something, it pushes them out along the contact normal.
- **If it happens again:** read those lines from `artifacts/unreal/play.log`.

**Checks:** native 52/52 (one engine HTTP-connectivity warning), `BellbreakerForge` 1/1 and `HearthA2` 1/1.

## Stuck-after-stun: root cause found and fixed; souls-style camera (2026-11-18)

### The bug

The owner's `play.log` stuck lines all named the same blocker: `StaticMeshActor_68`, which the player's capsule started 1 cm inside, normal straight up. The blocker's top is at 6 cm. A real-game capture logged the actor names: **`StaticMeshActor_68` is the first shockwave ring**, a floor plane placed at z = 6 cm.

**Why it trapped the player:**

- After a Quake the ring stays where the last crest left it, only hidden, and at up to 20 m across.
- In the real game it still collided, despite `SetCollisionEnabled(NoCollision)`. The automation world honoured that setting, so the tests never reproduced the bug.
- With the capsule's bottom (5 cm) inside the plane, every horizontal walk and roll sweep was refused. Rolls animated in place.
- An in-game restart doesn't respawn the rings, so the bug survived it.

**Fix: `WardenNeverCollide`.**

- **Collision off by every switch:** actor collision off, the `NoCollision` profile, ignore all channels, no overlaps, no navigation.
- **Ignored by the fighters:** every fighter's capsule also ignores the actor when moving, via `IgnoreActorWhenMoving`.
- **Applied to:** both rings, the boss's presentation actor (body, hammer, sparks) and all forge dressing in the forge fight.

**Stuck guard.** It now makes the player's capsule ignore any actor it finds itself starting inside (except the boss) and pushes out of horizontal overlaps.

**New tests:**

- **`WardenAssetTrial.BellbreakerForgeOverlap`:** no overlaps at spawn when fresh, after a Quake or after a reset. A 20 m ring placed under the player's feet doesn't block walking (210 of 210 cm).
- **Real-game capture:** no stuck events.

### Camera

The owner found the camera too high and too rigid, and asked for medium height with an elevation the player can adjust.

**Research** (community sources; FromSoftware publishes no numbers):

- Souls lock-on keeps a comfortable medium distance and aims at the target.
- Big bosses are its known weak spot, because a tall lock point drags the view up.
- Players' main complaint is that Elden Ring doesn't let you adjust the camera while locked on; mods add free orbit.

**Implementation:**

- **Position:** socket (0, 55, 120 → 145 when close), arm 620 → 780 when close, with a 22% midpoint offset.
- **Aim:** his capsule centre (about 2.4 m) blended 30% toward your chest when close. Pitch is `0.6 × natural − 6 + your offset`, clamped to −32…+12°.
- **Smoothing:** softer follow (`RInterp` 3.2).
- **Your elevation:** mouse or stick Y while locked sets an offset of −20…+15° that is **kept**, including across lock toggles. The yaw nudge still relaxes back.
- **Giant detection:** the camera now recognises the Bellbreaker from the locked target itself.

**Test:** `CameraElevationHolds`. At 6.5 m the default view is −7.8°; a +10° nudge holds at +2.2° after 5 s idle. Evidence: `evidence/camera-medium-height.png`.

**Checks:** native 53/53, `BellbreakerForge` 2/2, `BellbreakerForgeOverlap` 1/1 and `HearthA2` 1/1.
