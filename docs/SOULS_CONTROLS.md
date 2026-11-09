# Souls-style controls calibration, 2026-11-10

The owner asked for Elden Ring-style controls. They reported they "can't beat the boss at all", "can't jump attack", the roll "feels a little weird", and the sword swing doesn't feel good. They asked me to research how Elden Ring tunes sprint, stamina and swing feel, and emulate it, before any 3D work.

## What the research found

These numbers are from community wikis and guides. Elden Ring's frame data is measured by players, not published, so treat them as approximate.

| Topic | Elden Ring (community data) | BossLab before | BossLab now |
|---|---|---|---|
| Roll invincibility | 13–14 frames at 30 fps, about 0.43–0.47 s ([wiki.gg](https://eldenring.wiki.gg/wiki/Invincibility_Frames)) | 14 ticks at 60 Hz = 0.23 s | **26 ticks = 0.43 s** (2–28 of a 40-tick roll) |
| Roll cost | A flat 12 stamina against an 80–170 bar ([Fextralife Equip Load](https://eldenring.wiki.fextralife.com/Equip_Load)) | 28 of 100 | **14 of 100** (7 rolls from full) |
| Stamina regeneration | About 45/s base (Souls-series figure) | 26/s after 0.7 s | **45/s after 0.5 s** (player) |
| Stamina pool | 80 to 170 by Endurance ([Fextralife Stamina](https://eldenring.wiki.fextralife.com/Stamina)) | 100 | 100 |
| Sprint vs run | Sprint is the faster tier; a movement mod's defaults treat it as about 50% faster | 360 / 540 cm/s | **420 / 630 cm/s** (1.5×) |
| Light attacks | Chain; later hits often faster; final hit stronger ([Fextralife Attacks](https://eldenring.wiki.fextralife.com/Attacks)) | One cut | **Three-cut chain**; the third is a heavy finisher, then it loops |
| Jump attacks | Jump then attack; extra stance damage; not part of a combo; open after landing (same source) | None | **F jumps**; attack in the air = **jump attack** (52 damage, 2 stance) |
| Contextual attacks | Running, lunge and roll-follow attacks (same source) | None | **Rolling thrust** (attack after a roll), **running cut** (attack while sprinting) |

Not found: per-attack stamina costs and startup or recovery frame tables for greatswords. Those values below are tuned, not copied.

## The player rules ([WardenCombat.h](../unreal/BossLabWarden/Source/BossLabWarden/WardenCombat.h))

| Move | Wind-up / contact / recovery (ticks) | Damage | Stance | Stamina | Step |
|---|---|---|---|---|---|
| Cut I (right-to-left diagonal) | 24 / 16 / 28 | 30 | 1 | 18 | 22 cm |
| Cut II (backhand) | 20 / 16 / 28 | 30 | 1 | 18 | 20 cm |
| Cut III (overhead finisher) | 28 / 18 / 38 | 46 | 2 | 22 | 36 cm |
| Jump attack | 22 / 14 / 40 | 52 | 2 | 12 jump + 14 | 60 cm, glides |
| Rolling thrust | 12 / 10 / 32 | 24 | 1 | 16 | 80 cm, glides |
| Running cut | 16 / 16 / 34 | 36 | 1 | 20 | 120 cm, glides |

**Timing windows:**
- **Chain.** The next cut opens 2 ticks after contact ends. Inputs buffer for 18 ticks (was 12), so pressing during the swing carries into the next cut.
- **Roll cancel.** You can roll out of an attack's recovery from 8 ticks after contact, or from 24 after a jump attack's landing, which leaves you open as in Elden Ring. No cancel during wind-up or contact.
- **Roll.** 40 ticks and 320 cm. The rolling thrust opens at age 28, after the protected frames; a second roll opens at 32.
- **Jump.** 44 ticks with a 75 cm arc. The capsule really rises, so fire pools can be jumped. The jump attack window runs from age 4 to 30, and the attack descends to land exactly at contact.

**Impact:**
- **Hit-stop.** The fight freezes for 4 ticks on a light hit and 6 on a heavy one, both fighters and hazards alike.
- **Camera shake.** A small shake on landed blows, turned off by the reduced-motion setting.
- **Pose continuity.** A cancel winds up from the interrupted pose, so the chain flows without snapping to guard.

**Boss stance (poise):**
- **Damage.** Each hit removes stance points, and heavy finishers and jump attacks remove 2.
- **Warden.** 4 points, 240 hp. It stays the easy practice boss.
- **Regent.** 6 points, 600 hp, with phase two at 300.
- **Why the Regent changed.** A disciplined test bot beat the old 240 hp Regent in 26 s under the new player rules. Boss rules and timing are otherwise unchanged.

## Verified

The native suite passes **31/31**. The existing fundamentals tests were updated to the new values: roll 320 cm and 14 stamina, 26 protected ticks, run 420 cm/s, poise 4. Their structural checks are unchanged. New or extended tests:

- **`BossLab.Controls.ChainCancelsAndJump`:**
  - the chain only continues in order, and only after contact;
  - three cuts cost their sum;
  - roll cancel is allowed only from contact + 8, checked tick by tick;
  - the jump attack window is exactly 4–30, and a jump attack needs a jump;
  - 7 rolls from full stamina, and 45 stamina per second;
  - the jump rises 56 cm in 12 ticks, the jump attack lands at contact (0.00 cm) and the player ends on the floor;
  - hit-stop holds the fight clock.
- **`BossLab.Controls.ReactiveBotCanWin`:** a test bot that rolls just before contact, sidesteps hazards, punishes recovery with up to two cuts and heals when low.

  | Boss | Result | Fight length | Bot health at end |
  |---|---|---|---|
  | Warden | 6 of 6 wins | 18 s | 100 hp |
  | Regent | 6 of 6 wins | 78–80 s | 56–88 hp, using 2–3 heals |

  The bot reacts frame-perfectly, so a human should take longer.
- **`BossLab.Fundamentals.TwoHandGripAndAuthoredArc`** now covers every player move. Peak blade-tip speed is 54–79 cm per tick, against 42–55 for the boss.
  - **Contact windows lengthened:** with 10–12-tick contact windows the cuts peaked at up to 108 cm per tick and read as snaps, so contact is now 14–18 ticks.
  - **Steps shortened:** a 50 cm step made the planted rear foot drag 33 cm. The cuts now step 20–36 cm, and the foot holds at 0.000 cm.
- **Motion-study capture** (the player kit in one take, inspected):
  - `chain-three-cuts-sheet.png` shows three distinct, continuous cuts;
  - `jump-attack-sheet.png` shows the rise and the overhead slam.

  Both are in `artifacts/art/souls-controls-2026-11-10/`.

## Jump attack and flask pass (2026-11-10, later)

The owner said the jump attack still didn't feel like Elden Ring, and asked for a flask-drinking heal with red particles.

- **Jump.**
  - **Arc:** snappier and higher, 40 ticks and 90 cm (was 44 ticks and 75 cm). It rises 72 cm in its first 12 ticks (was 56).
  - **Jump attack:** it hangs for 4 ticks with the blade raised, then plunges with a gravity ease-in to land exactly at contact. It keeps the jump's momentum, so a running jump attack covers ground. Wind-up is 18 ticks (was 22).
  - **Impact:** a dust burst at the blade's landing point and a strong camera kick (0.65), even on a miss. A plain jump landing gets a small puff and a light kick.
  - **Camera:** the follow camera rises only 40% of a jump's height, so the view doesn't bob.
- **Flask.** Healing is now a drink:
  - the sword drops to the right hand alone, low and pointing down;
  - the left hand brings a glowing crimson flask from the hip to just below the mouth (arm IK) and holds it while the head tips back (neck and head bones), then lowers it;
  - a dim red light glows while drinking;
  - when the heal lands, 48 crimson motes swirl up the body over about 1.5 s with a red light flash.

  It is presentation only: heal timing (78 ticks, applied at 60) and the amount (+45) are unchanged.
- **Materials.** [ue_import_effects.py](../unreal/art-studio/source/effects/ue_import_effects.py) builds three materials in `/Game/BossLab/Effects` (local):
  - `M_HealMote`, additive crimson motes;
  - `M_FlaskGlass`, the flask's glow;
  - `M_ImpactDust`, translucent dust puffs.

  [WardenEffects.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenEffects.cpp) draws the effects from the fighter state every frame.
- **Problems found in the captures, and fixes:**
  - The motes read gold-white. Fix: a redder palette, below white.
  - The flask core bloomed to white. Fix: a dimmer emissive.
  - The motion-study camera ignored the front view requested for the drink, because the player's tick forced a fixed view. Fix: a `MotionStudyView` setting.
- **Evidence:** `heal-flask-front-sheet.png` (front view: raise, drink, lower, mote burst) and `jump-attack-plunge-sheet.png` (rise, raised blade, plunge, dust).
- **Tests:** native suite 31/31; the jump tests use the new constants.

## Limits

- **Feel.** Not owner-tested. These are first-pass values for tuning by hand.
- **Animation.** Attack and jump poses are procedural keys on the mannequin. There is no new animation clip.
- **Not built:** heavy (R2) or charged attacks, guarding, parrying, backsteps, ripostes or stance-break criticals.
- **Bot fairness.** The beatability bot is frame-perfect. It shows the fight can be won; it does not measure how hard it is for a person.
