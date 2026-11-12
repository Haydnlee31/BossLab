# Raise the Dead and censer floor contact, 2026-11-12

The owner asked for a summon move (two slow skeletons, killable in three hits) using the whispers sound (#1) as its casting spell, and for the censer to touch the ground with friction effects and sound, slowing while it drags.

## Raise the Dead (Regent move 16)

- **Rules** (engine-owned, `WardenRegent.h/.cpp`):
  - **Cast:** a 70-tick wind-up (1.17 s) with no direct damage. It is in both phase sequences and is skipped while any skeleton stands.
  - **Spawning:** rune circles draw in at two points 230 cm either side of the Regent, and the skeletons rise from them at the release (54 ticks).
  - **Movement:** they walk at 95 cm/s and turn at 3° a tick.
  - **Attack:** within 150 cm they wind up for 42 ticks, then strike for 14 damage within ±60° of their facing. A roll beats the swing.
  - **Taking hits:** any three separate player blows fell one, and each earlier blow staggers it for 20 ticks.
  - **Ending:** they crumble after 30 s or when the boss dies.
- **Sound:**
  - `RegentRaise`, the cast: the whispers recording in two voices (one 5 semitones lower), +6 dB treble, a smeared tail, a rising ghost drone and a ground crack at 1.17 s. It has no scream on top, so the whispers stay audible.
  - Skeleton rise, step, swing, hit and fall: bone clatter built from synthesised resonant "knocks" (1.4–3.2 kHz) over pitched wood grains. The Kenney wood recordings have almost no energy above 2.5 kHz.
- **Look (greybox):**
  - **Body:** a gaunt mannequin (×0.72 width).
  - **Material:** `M_RegentDead` gives charred, dark bone, rib gaps with a faint soul-fire glow and a cold rim. Paler bone read as bare skin under the warm torches.
  - **Head:** the generated skull, ×1.45, with soul-fire eyes and a crown flame.
  - **Animation:** the walk clip at 65% speed; the attack clip is scrubbed to the swing beats.
  - **Status:** a real skeleton model, for example from TRELLIS and the revamp rig pipeline, is the next art step.
- **Evidence:** `skeletons-rise-and-fight.png`.

## Censer floor contact

- **Censer Arc:** mid-sweep the censer dips 54 cm onto the floor and drags at about 40% speed, through a progress warp `p = s − 0.6·sin(2π(s − 0.5))/2π`, then speeds back up. The active window and total duration are unchanged. It is on the floor for 8 ticks.
- **Grave Bell:** after the slam the censer grinds 110 cm back along the floor over 35% of the recovery (30 ticks), then lifts.
- **`CenserGround()`** (0–1) drives both the path and the effects.
- **Sound:** `CenserScrape` plays once at contact: a heavy metal clang, a stone knock, 60 fine metal grains for grit, a rough 2.6 kHz friction band and a chain jingle.
- **Sparks:** an orange-white streak spray (`M_RegentSpark`, up to 48 live) from the lantern base while it is on the floor. Evidence: `censer-floor-sparks.png`, with the Arc on the top row and the Bell on the bottom.

## Verification

- **Tests:** native suite 35/35. The new `BossLab.Regent.RaisedSkeletonsWalkSwingAndFallInThreeBlows` test checks:
  - two skeletons rise and are slow;
  - a skeleton swing deals 14 to a standing player and 0 after a timed roll;
  - the first two blows stagger, and the third fells it;
  - the Arc is on the floor 8 ticks and the Bell 30.
- **Sequence:** all 14 Regent moves occur in the long sequence test, and `ReactiveBotCanWin` still passes.
- **Not yet done:** the result has not been owner-tested, and nothing has been listened to.
