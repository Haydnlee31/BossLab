# Elden Ring combat and movement: research and recommendations, 2026-11-14

Research only, written overnight. No code was changed and nothing was built or run. Read with [SOULS_CONTROLS.md](../SOULS_CONTROLS.md), [ANIMATION_FEEL.md](../ANIMATION_FEEL.md) and [REGENT_MOVESET.md](../REGENT_MOVESET.md).

## Summary

- **Timing is already close to Elden Ring.** Our roll, stamina, buffering and cancel rules are near Elden Ring's numbers, and several are more lenient. The rules are not the main reason the fight feels stiff.
- **The gap is the motion itself.** Elden Ring's player moves are motion-captured. One article names the mocap group Katsugekiza and actor Akira Sugihara across Dark Souls III, Sekiro and Elden Ring ([Automaton](https://automaton-media.com/en/wp-json/wp/v2/posts/13270)). Our player has three weaknesses here:
  - only Epic's *unarmed* walk/jog clips (`/Game/Characters/Mannequins/Anims/Unarmed`), with nothing for sprint, start, stop or pivot;
  - procedural key poses for every attack;
  - a roll that rotates the whole mesh 360° around one axis ([WardenSword.cpp](../../unreal/BossLabWarden/Source/BossLabWarden/WardenSword.cpp), the `Dodge` branch and the `DirectionalRoll` root rotation).

  Layering (carry, lean, bank, foot lock) has been pushed a long way. The next real gain needs authored clips.
- **The camera is the cheapest win.** Elden Ring's camera follows smoothly and re-centres behind you while you move. Ours is rigidly attached to the capsule, with no lag and no re-centring. That makes every hard stop and reversal read as a jolt.
- **Hit feel.** Elden Ring's hit-stop is a brief pause of the weapon on contact. Ours freezes the whole fight for 4–6 ticks. Keeping the camera, particles and cloth moving during the freeze is a presentation-only fix.

**Reliability.** FromSoftware publishes no frame data. Everything below comes from community measurement (30 fps frames; ×2 gives 60 Hz ticks) or paramdef listings. Values I could not verify are marked **unverified**.

## Elden Ring vs BossLab: parameters

A tick is 1/60 s, and one Elden Ring frame at 30 fps is 2 ticks.

| Parameter | Elden Ring | BossLab now | Source / notes |
|---|---|---|---|
| Roll i-frames, light or medium load | 13 frames (0.43 s); wiki.gg says 14 | 26 ticks (0.43 s), ticks 2–28 | [PvP Lexicon](https://docs.google.com/document/d/1dTJsUb28vCvyTeQZPOMY5KFei4MG9TfLqHzkrvPzvXQ/mobilebasic); [wiki.gg](https://eldenring.wiki.gg/wiki/Invincibility_Frames). **Match.** |
| Roll startup before i-frames | 0 frames | 2 ticks | PvP Lexicon. A small difference. |
| Roll recovery after i-frames, light or medium | 8 frames to roll (16 ticks); 6–7 frames to a weapon art | Re-roll at 32, 4 ticks after the i-frames; roll attack at 28; walk out at 34 | PvP Lexicon; [gamertagmythras](https://gamertagmythras.com/blog/elden-ring/elden-ring-equip-load-guide). **Ours chains rolls about 12 ticks sooner**, so roll spam is cheaper and lighter. |
| Heavy roll | 12 i-frames, 16 frames recovery | n/a (single load) | Same sources. |
| Roll stamina | 12 flat, against an 80–170 bar | 14 of 100 | gamertagmythras; [Fextralife Stamina](https://eldenring.wiki.fextralife.com/Stamina). Equivalent. |
| Stamina regen | About 45/s base | 45/s after 0.5 s (30 ticks) | Forum figure shared with the Dark Souls series; delay **unverified**. [Dark Souls wiki](https://darksouls.fandom.com/wiki/Stamina): attacking stops recovery until the animation ends. |
| Backstep (dodge with no stick input) | Exists. The official guide says "minor i-frames"; wiki.gg lists 7–8 i-frames only with the Shadow of the Erdtree talismans | None. A neutral dodge rolls | [Bandai Namco combat guide](https://www.bandainamcoent.com/news/elden-ring-introduction-part-4-combat-guide); wiki.gg. The two sources conflict. |
| Jump i-frames | 25 frames, lower body only (arms and head can be hit) | Capsule rises; no i-frames | wiki.gg. Our jump clears fire pools geometrically, which is similar in practice. |
| Greatsword 2H R1, recovery to dodge | 10 frames = 20 ticks after active frames (Claymore) | 8 ticks after contact | PvP Lexicon. **Ours is 12 ticks more lenient.** Keep it for now, since the owner struggled to win. |
| Greatsword 2H R2, recovery to dodge | 11 frames = 22 ticks | No heavy attack | PvP Lexicon. |
| Greatsword 2H jump R1 | 15 frames = 30 ticks to dodge | 24 ticks after landing (roll); move-cancel at +28 | PvP Lexicon. **Close.** |
| Greatsword 2H running R1 | 10 frames | Running cut: roll 8 after contact | PvP Lexicon (BR1). |
| Attack startup (wind-up) | Not found in any community table | Cuts 20–28 ticks; running cut 16; rolling thrust 12 | **Unverified**, so no recommendation rests on it. |
| Input buffer | Official: a pressed action is "queued and performed at the next available chance". Players report it is not a fixed timer: the input is kept while the action runs | Held up to 64 ticks while committed, then 18 | Bandai Namco guide; [Steam thread](https://steamcommunity.com/app/1245620/discussions/0/4361250968410661652). **Match in behaviour.** |
| Roll input trigger | Fires on button *release*, because hold is sprint on the same button; adds 1–4 frames | Press, on a separate key (Space, with sprint on Shift) | [Nexus mod note](https://www.nexusmods.com/eldenring/mods/101). Ours is more responsive. Keep it. |
| Jump attack | Large stance damage, "comparable to a fully-charged heavy"; brief crouch after landing | 52 damage, 2 stance (a cut does 1) | [Fextralife Attacks](https://eldenring.wiki.fextralife.com/Attacks); [Fextralife Stance](https://eldenring.wiki.fextralife.com/Stance). |
| Stance damage ranking | Charged heavy ≈ guard counter > jump heavy > heavy > light; two-handing adds +30% to lights | Light 1, finisher / jump 2 | Fextralife Stance. We have no heavy, charged or guard-counter moves. |
| Boss stance regen | Starts after (base poise ÷ 13) s, then 13 poise/s. Bosses have 80–120 base poise, about 6–9 s before regen starts | Full reset 300 ticks (5 s) after the last stance hit (`PoiseReset`, WardenCombat.cpp) | [wiki.gg Stance](https://eldenring.wiki.gg/wiki/Stance); [Fextralife Poise](https://eldenring.wiki.fextralife.com/poise) gives 6–15 s. |
| Stance-broken window | "Stunned for a significant amount of time"; a frontal R1 critical (riposte) ends it | 84 ticks; blows deal ×2.5 | wiki.gg Stance; exact duration **unverified**. We have no dedicated critical animation. |
| Hit-stop | Every melee weapon pauses briefly on contact, for weight; the duration is not published | Whole fight frozen 4 ticks (light) / 6 (heavy) | Zullie the Witch, via a [summary article](https://lightyellowelegant.pages.dev/posts/elden-ring-dataminer-investigates-laggy-death-s-poker-weapon). Whether it is attacker-only is **unverified**. |
| Camera distance (lock param) | `camDistTarget` 4.0 m | 5.0 m unlocked, up to 6.2 m close-locked (`500+120*Separation`) | [libER LOCK_CAM_PARAM_ST](https://dasaav-dsv.github.io/libER/dd/dab/structfrom_1_1paramdef_1_1LOCK__CAM__PARAM__ST.html). These are paramdef defaults, not confirmed game rows. |
| Camera FOV | `camFovY` 43° vertical, about 70° horizontal at 16:9 | 75° horizontal | libER (default value). |
| Camera pivot height | `chrOrgOffset_Y` 1.42 m | Capsule centre (90 cm) + 100 cm socket = about 1.9 m, plus 45 cm to the right shoulder | libER. Ours sits higher and off-centre. |
| Lock-on range | 15 m; the lock is kept 2 s after the condition fails | Breaks at 24 m | libER. |
| Locked-camera player control | The locked camera cannot be rotated (mods add it) | ±25° yaw / ±12° pitch nudge | [FreeLockOnCamera](https://github.com/SchuhBaum/FreeLockOnCamera). Ours is more flexible. Fine. |
| Unlocked camera | Auto-rotates (re-centres) behind the player while moving; patch 1.04 added an option to turn it off | No re-centring | [DSOGaming 1.04 notes](https://www.dsogaming.com/patches/elden-ring-update-1-04-released-adds-option-to-disable-camera-auto-rotate-full-patch-notes/). |
| Run / sprint speed | No measured m/s found. A mod's defaults treat sprint as about 1.5× | 420 / 630 cm/s | [Nexus mod 8408](https://www.nexusmods.com/eldenring/mods/8408). **Unverified.** |
| Locomotion acceleration | Not found | 2400 cm/s² to speed, 3600 to stop (0.18 s to run speed) | WardenEncounter.cpp `VInterpConstantTo`. |

**Reading the table.** Our rules are at or beyond Elden Ring's generosity everywhere except the missing move types: heavy or charged attacks, guard counter, backstep and critical. The "doesn't feel like Elden Ring" complaint is about motion and camera, as the owner said.

## What makes Elden Ring movement feel fluid

Elden Ring's exact animation graph is not public. Its behaviour is in Havok behaviour files, and the cancel windows are TAE "JumpTable" events. The techniques below come from modding notes, general locomotion practice, and what we can measure in our own build.

1. **Authored, weapon-specific clips, then layering.** Elden Ring cancel windows are per-animation events. One mod extends a turn animation's "JumpTable Cancel – Dodge" event so the turn can be rolled out of ([Nexus 3049](https://www.nexusmods.com/eldenring/mods/3049)). Every move, turns included, is its own authored clip with its own cancel window. We layer procedural poses over unarmed clips. Our layering is good, but it cannot supply what an authored clip has:
   - weight shift;
   - anticipation;
   - overlapping action in the shoulders and hips.
2. **Root motion for committed actions, code velocity for locomotion.** This is common third-person practice ([locomotion overview](https://mocaponline.com/blogs/mocap-news/locomotion-system-design-guide)). In Elden Ring, attacks and rolls carry their own displacement curves. We already do this procedurally: `DodgeDistance`, the strike `Advance` and `EntryBrake`.
3. **Starts, stops and pivots.** A pivot should read as plant, rotate, push off. Without one, the character "snaps instantly to the new direction, which looks mechanical and weightless" (same source). Turning in place is usually driven by a root yaw offset that the turn animation consumes and then blends out ([Epic, Lyra animation](https://www.unrealengine.com/tech-blog/adapting-lyra-animation-to-your-ue5-game); the page refused automated fetch, so this is from the search summary).
   - **What we do now:** reversals pass through zero speed (`VInterpConstantTo`), and the body turns at 540°/s with an eased end. There is no plant-and-push pose, which is exactly the "weightless snap" described.
4. **Upper body against planted feet.** Strong foot planting makes the upper body over-rotate around the planted foot. The head and chest need their own counter-motion ([Game Developer, upper-body movement](https://gamedeveloper.com/art/head-over-heels-upper-body-movement-in-gameplay)). Round three's head-leads-turn and the chest-ride hands are the right idea.
5. **Commitment with readable cause and effect.** Souls attacks and enemy attacks run "on a similar timescale", while "defensive options are instant" ([critpoints](https://critpoints.net/2016/02/12/the-joy-of-souls-combat)). Commitment only feels good when the wind-up is readable. Control feels mushy when moves look alike or start later than expected ([iTechGuides](https://www.itechguides.com/what-makes-a-melee-combat-system-feel-satisfying/)).
   - **Our cuts:** they differ in direction, but their timing curves look alike. Every cut eases in and out symmetrically over a 14–18-tick contact window.
6. **Weighty swing shape (common animation practice; specific frame counts unverified).** A heavy swing has:
   - a long wind-up with a visible coil and a short hang at the top;
   - a fast sweep that covers most of the arc early;
   - a long, decelerating follow-through that sells the mass.

   The 2026-11-10 pass lengthened our contact to remove "snaps", which risks the opposite: a floaty, constant-speed arc. A front-loaded sweep with a trail and motion blur reads as a heavy weapon, not a snap.
7. **Camera smoothing.** Elden Ring's camera follows with lag and re-centres behind you while moving (the auto-rotate above). A rigidly attached spring arm (`bEnableCameraLag` is off; [WardenPrototype.cpp](../../unreal/BossLabWarden/Source/BossLabWarden/WardenPrototype.cpp) constructor) shows every velocity discontinuity: a 3600 cm/s² stop, a 4200 cm/s² entry brake, a roll's push. Render interpolation removed judder, but it cannot smooth the motion itself.
8. **Hit-stop as weight, not a pause button.** The weapon pausing on contact sells collision (Zullie, above). Freezing everything, including the camera and effects, reads as a hitch.

## Prioritised recommendations (top 10)

"Engine rule" means it changes `WardenRules`, `FWardenFighterState` or the fixed step. Those need native tests and owner approval. "Presentation" means drawing, camera or audio only; run the native suite anyway, because animation tests measure poses.

### 1. Authored greatsword locomotion clips

- **What:** run and sprint loops with the blade carried, run start, run stop with a plant, a 180° pivot and turn-in-place, retargeted to SK_Mannequin.
- **Sourcing:** free candidates.
  - Mixamo: free with an Adobe account, embed-only licence ([Adobe FAQ](https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/td-p/13234775)). Whether a greatsword set exists there is **unverified**.
  - [MoCap Online free sword pack](https://mocaponline.itch.io/free-3d-sword-animation-pack): 55 MB; licence not stated on the page.
  - Epic's Game Animation Sample (motion matching, 500+ clips, UE-only licence) is about 10 GB after creation ([uhiyama-lab](https://uhiyama-lab.com/en/notes/ue/motion-matching-game-animation-sample/)). **That breaks the 10 GB unreal/ budget.** Do not install it into the project.
- **Where:** a new import script under `unreal/art-studio/source`. Then [WardenSword.cpp](../../unreal/BossLabWarden/Source/BossLabWarden/WardenSword.cpp) needs a start/stop/pivot selector next to `Locomotion`, keeping the existing carry, lean and foot-lock layers on top.
- **Impact:** highest. It is the single biggest difference from Elden Ring.
- **Risk:** medium. Needs an owner OK for the download and licence; retarget and foot-lock tuning; animation tests will move.
- **Rule change:** presentation only. Speeds, acceleration and the capsule are unchanged.

### 2. Replace the rigid-tumble roll

- **What:** an authored forward/side roll clip, or failing that a shoulder-led procedural roll, timed to the existing 40-tick curve. The procedural version would:
  - lead with the shoulder;
  - tuck the spine;
  - leave the root at a fixed orientation;
  - keep the head up on exit, landing into the run.
- **Where:** today the whole `VisualBody` rotates 360° about one axis (WardenSword.cpp, the `Dodge` branch and `DirectionalRoll`).
- **Impact:** high. The roll is the most-used action, and a turntable tumble reads as mechanical.
- **Risk:** medium. Roll tests check the floor contact solve.
- **Rule change:** presentation only. `DodgeDistance` and the i-frames are unchanged.

### 3. Camera follow lag and gentle re-centring

- **What:**
  - `Arm->bEnableCameraLag = true`, with `CameraLagSpeed` about 10–12 and `CameraLagMaxDistance` about 60 cm, as a starting point to tune;
  - lighter rotation smoothing while unlocked;
  - when unlocked and moving with no mouse or stick look input for about 1 s, ease the yaw behind the heading at about 60–90°/s, behind a setting (Elden Ring has a toggle).
- **Where:** [WardenPrototype.cpp](../../unreal/BossLabWarden/Source/BossLabWarden/WardenPrototype.cpp), the constructor and the camera tick around lines 160–185.
- **Impact:** high for perceived smoothness: stops, reversals and rolls stop jolting the view.
- **Risk:** low. It must also work with render interpolation, since the lag runs on the rendered frame, and with arena wall retraction (the spring-arm collision test). Check `BossLab.Fundamentals.CloseCameraFullBodyFraming`.
- **Rule change:** presentation only. **Quick, tonight-sized.**

### 4. Front-loaded, weighty swing curves

- **What:** keep `Windup`, `Active` and `Recovery` exactly.
  - In the last 4–6 wind-up ticks, add a deeper coil and a short hang.
  - During contact, ease the arc so about 70% is covered in the first third, instead of a symmetric `Smooth`.
  - Add a 2–4° follow-through overshoot that settles in recovery.
  - Optionally strengthen the existing blade trail during the fast part.
- **Where:** WardenSword.cpp, the strike keys (`Wind`/`Follow`/`Carry`, using `Smooth(...)` around lines 280–311).
- **Impact:** high on "swing doesn't feel good".
- **Risk:** medium. Hits come from the blade sweep, so this moves *when inside the active window* a hit lands. The window itself does not change. Re-run `TwoHandGripAndAuthoredArc` (blade-tip speed limits will need re-thinking) and `ReactiveBotCanWin`.
- **Rule change:** presentation by rule; hit timing inside the window shifts. Treat it as needing tests.

### 5. Pivot pose on hard reversals

- **What:** when the stick reverses more than about 120° at run speed, play a 6–10-tick plant: outside foot locked, pelvis dropped 4–6 cm, torso leaning against the old velocity, then a push-off lean into the new direction. The sword carry is held.
- **Where:** WardenSword.cpp, the feel layer (`FeelAccel`/`FeelLean`/`FeelBank`) and the foot lock.
- **Impact:** medium-high. It removes the "weightless snap" on reversals.
- **Risk:** low-medium. Watch the foot-slip tests.
- **Rule change:** presentation only. **Feasible tonight** if it is kept procedural.

### 6. Hit-stop that keeps the world alive

- **What:** during the existing `HitStop` freeze, keep the camera shake, blood, sparks, cloth and fire updating, plus a 1–2 cm high-frequency shake on the struck body.
- **Engine-rule follow-up (later):** consider attacker-weighted hit-stop, freezing the attacker's blade while the victim's recoil plays, instead of freezing both.
- **Where:** [WardenEncounter.cpp](../../unreal/BossLabWarden/Source/BossLabWarden/WardenEncounter.cpp) `FixedStep` (`if(HitStop>0) { --HitStop; return; }`) and its frame tick (shake); WardenEffects.cpp.
- **Impact:** medium. Hits feel heavy instead of like a hitch.
- **Risk:** low for the presentation part. Determinism is untouched if only drawing continues.
- **Rule change:** presentation only for the first part; engine rule for the attacker-weighted variant.

### 7. Elden Ring-like camera framing

- **What:**
  - a centred or slight shoulder offset (Y 45 → about 15 cm);
  - a pivot at about 1.45 m, i.e. socket Z about 55 instead of 100;
  - about 70° FOV;
  - a lock-on distance of about 4–4.5 m.
- **Where:** WardenPrototype.cpp camera values.
- **Impact:** medium. The character reads larger and the boss looms.
- **Risk:** low-medium. `CloseCameraFullBodyFraming` asserts an unlocked arm of exactly 500, so that test must change. This is an owner-visible look change: offer it as an option first.
- **Rule change:** presentation only.

### 8. Roll recovery spacing closer to Elden Ring

- **What:** re-roll from about tick 40 instead of 32 (Elden Ring: 16 ticks after the i-frames), with the roll attack and walk-out unchanged.
- **Where:** `RollChainOpen` in [WardenCombat.h](../../unreal/BossLabWarden/Source/BossLabWarden/WardenCombat.h).
- **Impact:** medium. Rolls feel weightier and less spammable.
- **Risk:** it changes difficulty. Re-run `ReactiveBotCanWin` and the owner must test it. Do it only after items 1–3, because the owner has struggled with the boss.
- **Rule change:** **engine rule.**

### 9. Heavy and charged heavy attack (R2), then a guard counter

- **What:** a heavy attack, chargeable, that becomes the main stance-break tool, as in Elden Ring. Guarding and a guard counter would follow.
- **Where:** `EPlayerMove` and the strike table in WardenCombat.cpp; input binding; tests.
- **Impact:** medium-high on "plays like Elden Ring". It is low on stiffness.
- **Risk:** medium. New rules, tests, balance and animation keys.
- **Rule change:** **engine rule.** Needs owner approval.

### 10. Backstep on a neutral dodge and a critical-hit animation on stance break

- **What:**
  - a short backstep when Space is pressed with no stick input;
  - an R1 in front of a staggered boss plays a riposte instead of a ×2.5 normal cut.
- **Where:** `FWardenFighterState::Request`, `NextPlayerMove`, WardenSword.cpp.
- **Impact:** medium. Both are recognisable Elden Ring beats.
- **Risk:** medium.
- **Rule change:** **engine rule.**

### Not recommended

- **Tighter recovery-to-dodge.** Ours is 8 ticks; Elden Ring's greatsword R1 is 20. Matching it would make the game harder without making it look better.
- **Release-triggered roll.** It only exists in Elden Ring because the roll and sprint share a button.
- **Installing the full Game Animation Sample.** It breaks the storage budget.

## Unverified items to measure later

- Attack startup frames for greatsword and colossal-sword R1 and R2.
- Hit-stop duration, and whether it applies to the attacker only.
- Run and sprint speeds in m/s.
- Locomotion acceleration.
- Stance-break stun duration.
- Whether the camera paramdef defaults equal the shipped rows.

All need either in-game frame stepping by the owner or a reliable datamined table. None should be tuned on held-out evaluation seeds.
