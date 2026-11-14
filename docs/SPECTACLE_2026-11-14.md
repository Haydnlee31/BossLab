# Spectacle pass, 2026-11-14

This pass is modelled on the owner's reference clip, a Morgott no-hit Short. The owner asked for all eight items from the analysis, plus generated props to fill out the arena. Everything is on by default.

| Switch | Turns off |
|---|---|
| `BOSSLAB_GRAPHICS=-spectacle` | the presentation effects in `WardenSpectacle.cpp` |
| `BOSSLAB_GRAPHICS=-warmth` | the warm fire and grade |
| `BOSSLAB_GRAPHICS=off` | everything in the two rows above, plus the earlier graphics features |

## Rules changes (owner-approved in "do all of them")

- **THE SENTENCE (Regent move 17, `BossMoveCount` 18).**
  - **Timing:** wind-up 110 ticks, active 10, recovery 60, 30 damage, advance 420 cm.
  - **The hold:** the estoc is raised high over the shoulder for almost 2 s. Soul-fire embers gather on it, a blue light grows, and the blade trembles.
  - **Stalking:** from tick 24 until 16 ticks before contact, the Regent walks in at 75 cm/s (`SentenceStalk`), so backing away does not escape it.
  - **The release:** the blade covers its arc in 3 ticks and lunges 4.2 m, followed by a long recovery to punish. The aim locks 14 ticks before contact, like the other thrusts.
  - **Sequence:** after Grave Bell in phase one and after Censer Arc in phase two.
  - **Tests:** `RollBeatsEveryAttack` case: standing still takes 30, a roll at age 106 takes 0.
- **A bigger Regent:** `WardenRegent::Scale` is 1.5 (it was 1.35, like the Warden).
  - **Height:** stand height is 95 × scale, used for reset, the study and the tests.
  - **Reach:** hit-sample radii and blade reach scale with the body.
  - **Tests:** every Regent move still hurts a player who stands still and is beaten by one timed roll at the new size (`RollBeatsEveryAttack`, run through `EnableRegent`).
- **Lock-on camera (revised the same day after owner feedback: "too rigid, too low").** It now behaves like the reference clip, with a raised camera looking down over the shoulder.
  - **Height:** the socket is at 125 cm, or 150 cm against the Regent. It was 100 cm, and 78 cm in the first version of this pass.
  - **Distance:** 560 cm from the Regent, 500 cm otherwise.
  - **Aim:** at the Regent's body, 60 cm below the target point. The view always looks down at least 12° (20° at contact).
  - **Follow:** softer, with an interpolation speed of 4.5 (it was 8).
  - **Mouse nudges:** wider, ±40° yaw and −18°/+14° pitch at 0.8× sensitivity. They relax back to centre after 0.8 s without look input.

## Presentation (`WardenSpectacle.cpp`, plus the materials from `ue_import_spectacle.py`)

- **Boss weapon trails:** `M_BossTrail` is a soul-fire ribbon behind the estoc or sword in contact and behind the censer through its sweep. Fast blades are filled in with extra samples so the ribbon follows the arc.
- **Sentence charge:** embers on the raised blade, a growing blue light, and a burst of embers plus a flash off the point on release.
- **Phase two:** 120 soul embers, a 40-chip floor shockwave with 16 dust puffs, a flash, a heavy shake, 0.7 s at 0.35× speed and a wider view.
- **Felled:**
  - 1.6 s at 0.3× speed, a punch-in and a flash;
  - the boss's soul streams up as embers from eight bones for about 4.5 s, under the existing "GREAT ENEMY FELLED" banner;
  - the results panel waits 3.4 s.
- **Floor debris:** grit chips and dust puffs on roll starts, landings, boss lunges and releases, Grave Bell and Pyre slams, and while the censer drags.
- **Critical blows:** a 13° field-of-view punch-in and 0.32 s at 0.35× speed.
- **How slow motion works:** it only scales how fast real time feeds the fixed 60 Hz step. The step itself is unchanged, and slow motion is off in automation and with reduced motion. All other camera effects are also off with reduced motion.
- **Warm hall (dungeon):** more amber fire (1, .5, .17) at 1.35× brazier and torch intensity, warm midtone and highlight gain over the cool shadows, and saturation 0.98.

## Arena: generated props (TRELLIS.2 on HF Pro, `artifacts/art/arena-props-2026-11-14`)

- **Models:** six FLUX inputs, each a 1024 TRELLIS run: throne, sarcophagus, mourning angel, ossuary, candelabrum and bier.
- **Pipeline:** `prep_arena_gen.py` (Blender: decimate, base pivot, height) then `ue_import_arena_gen.py` (editor mode) into `/Game/BossLab/Dungeon/Gen` (local).
- **Layout** (`WardenDungeon.cpp`, `NoCollision`):
  - the funeral throne and two candelabra on the dais before the sealed boss door;
  - mourning angels on the gallery in the even bays;
  - sarcophagi, biers and bone heaps on the gallery in the odd bays.
- **Rejected:** bone heaps at the pillar bases. `DungeonIsPresentationOnly` forbids raised dressing inside the wall line, so they were removed and the test was not changed.
- **Not added:** trench and cell props, because the 2.6 m parapet hides them from the fight floor.

## Review commands

- `capture spectacle` (new, capture only): phase two at tick 60, a critical at 420 and the fall at 600, on a fixed schedule.
- `BOSSLAB_STUDY_FROM=17 capture regent-study`: the Sentence.
- `BOSSLAB_ARENA=dungeon capture tour`: the hall and props.
- **Evidence:** `artifacts/art/spectacle-2026-11-14/` and `artifacts/art/arena-props-2026-11-14/`.

## Verified

- **Tests:** native suite 39/39. One test logs the usual unrelated HTTP-timeout warning.
- **Captures:** 0 material compile failures.

## Not verified and known issues

- **Feel:** not owner-tested. Slow motion and the camera effects need playing at real frame rate.
- **Trail segments:** the release trail still shows faint segment steps.
- **Critical punch-in:** hard to read in 30 fps captures.
- **Gallery props:** they sit in dim light.
- **Performance:** not measured. Embers and puffs are instanced and the two lights only switch on when used, but the props add about 99k triangles.
