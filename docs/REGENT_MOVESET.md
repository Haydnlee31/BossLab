# Funeral Regent moveset (greybox), 2026-11-09

The owner picked **weapon A**: an estoc in the right hand, plus a soul-fire censer on a chain from the left forearm. They also asked for magic "as diversified as possible" and a second phase.

This is a playable greybox for feel testing. Its visuals are placeholders, and it has no AI: the boss follows a fixed, labelled sequence. The default Warden rehearsal, its tests and the packaged app are unchanged.

## Play it

```sh
BOSSLAB_BOSS=regent BOSSLAB_ARENA=dungeon BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

- **Start in the second phase:** add `BOSSLAB_REGENT_PHASE=2`. The boss opens at the phase threshold, so the transition plays first.
- **Where it runs:** editor game only (`play`, `capture`, `benchmark`). Package modes reject `BOSSLAB_BOSS=regent`. The native tests turn the Regent on themselves.
- **Arena:** the dungeon is optional. Phase two turns the dungeon's fire blue only when the dungeon is on.

## Moves

Timings are in 60 Hz ticks. "Telegraph" is the time from the start of the visible wind-up to the first contact.

| Move | Kind | Telegraph | Damage | Notes |
|---|---|---|---|---|
| Mourner's Thrust | estoc | 36 | 22 | Lunges 1.2 m. |
| Triple Rite | estoc | 30 | 12 ×3 | Two quick thrusts, then a held beat before the third. Rolling on rhythm loses. |
| Censer Arc | chain | 54 | 24 | The censer whirls overhead, then sweeps about 195° at 4 m. The whole chain is the hitbox. |
| Grave Bell | chain | 66 | 30 | Overhead slam 3.6 m ahead. It leaves a 2.5 m soul-fire pool that ignites 18 ticks later and burns 5 every 0.5 s, without flinching. |
| Witness Volley | skulls | 40 | 16 each | Throws 2 skulls (3 in phase two) from orbit. They home at 2°/tick and stop turning within 3.5 m. A protected roll lets a skull pass through. Spent skulls re-form after 8 s (5 s in phase two). The HUD shows SKULLS n/3. |
| Drift Step | movement | — | — | Glides 3.2 m backwards. |
| Procession Dash | estoc | 48 | 26 | Crouched wind-up, then a 7.6 m charge that ends in a thrust. The aim locks 12 ticks before contact. |
| Ashen Furrow | ground | 44 + 30 per mark | 20 | Eight marks run from the boss toward the player. Each warms up for 30 ticks, then erupts once. |
| Held Thrust | estoc | 58 | 22 | Added in the refinement pass. The same lunge, held coiled and drawn back for an extra beat, to punish players who roll on the usual rhythm. |
| **Phase two** (from 50% health) | | | | |
| The Pyre Wakes | transition | — | — | Ring of soul fire. The hall's fire and lights turn blue. Unlocks the two moves below. |
| Ash Step | blink | 24 after reappearing | 24 | Vanishes for 24 ticks (untargetable). The destination beside or behind the player is marked first. It then reappears and thrusts. |
| Funeral Pyre | ring | 72 | 28 | A 4.8 m blast circle is drawn around the boss during the wind-up. Roll out of it, or roll through it. Leaves 3 pools. |

### Shared rules

- **Tracking:** telegraphed moves track the player until 14 ticks before contact (12 for the dash), then lock.
- **Pools:** at most 4 at once, which is at most 12.8% of the floor. The oldest burns out first.
- **Movement and stamina:** the boss walks at the usual 260 cm/s, pays the normal stamina for each move, and is subject to the existing poise rule.

### Sequence

The fixed rehearsal sequence is:

- **Phase one:** Thrust, Arc, Volley, Rite, Held Thrust, Drift, Dash, Bell, Furrow.
- **Phase two:** Ash Step, Rite, Pyre, Held Thrust, Volley, Dash, Arc, Furrow, Bell, Thrust, Drift.

After each move the boss pauses for a set time before the next one (`WardenRegent::Pause`):

| After | Pause |
|---|---|
| Drift Step | none, so it flows straight into the dash |
| Volley, Ash Step | 8 ticks |
| Thrust, Held Thrust | 18 ticks |
| Arc, Furrow, Wakes | 24 ticks |
| Bell, Dash | 32 ticks |
| Rite, Pyre | 40 ticks: the main punish windows |

Phase two uses 60% of these pauses.

Each step walks into the move's distance band and then commits. If the player stays too close for a ranged move, the boss backs off for 0.75 s and then commits from where it stands. If the player is out of range for 4 s, it skips the step.

## Code

- [WardenRegent.h](../unreal/BossLabWarden/Source/BossLabWarden/WardenRegent.h) and [WardenRegent.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenRegent.cpp) hold the move table, the censer path, the fixed-step resolution (skulls, pools, furrow, blink, ring) and the read-only view.
- **Shared boss table:** Regent moves are boss indices 3–13 in `WardenRules::Strike`, so they stay engine-owned like the original three. Default encounters and policies only ever use indices 0–2.
- **Changes to existing combat code:**
  - `FWardenFighterState` gains Regent contact windows, a three-hit re-arm for Rite, invulnerability while vanished, and `Damage(Amount, Flinch=false)` for pool chip damage.
  - `ResolveStrike` sweeps the chain instead of the blade for censer moves.
- **Pose code** (`WardenSword.cpp`):
  - The estoc is held in one hand.
  - Pose keys cover the thrust, the triple, the crouched dash, the low-carry censer and cast work, and the pyre's raise and slam.
  - The left arm aims at the censer or follows a cast path.
  - The feet glide during the drift, dash and blink, instead of staying planted.
- **Assets:**
  - The estoc uses the CC0 Poly Haven `antique_estoc` prop already imported for the dungeon. A primitive blade is used when it is missing.
  - The censer, chain, skulls and floor circles are engine primitives.
  - Materials come from [ue_import_regent.py](../unreal/art-studio/source/regent/ue_import_regent.py) and are written to `/Game/BossLab/Regent`, which is local and not committed:
    - `M_RegentFlame`, blue soul fire;
    - `M_RegentRune`, a floor circle whose radius, intensity and tint are parameters;
    - `M_RegentBone`.

  Rebuild them with `./scripts/bosslab-unreal python unreal/art-studio/source/regent/ue_import_regent.py`.

## Verified (2026-11-09)

- **Native suite: 25/25.** That is the default 22 plus three new tests:
  - `BossLab.Regent.MoveTableAndTelegraphs`:
    - every damaging telegraph is at least 24 ticks;
    - Rite lands as three separate hits;
    - the pool budget is at most 15% of the floor;
    - pool damage doesn't flinch;
    - the default move names are unchanged.
  - `BossLab.Regent.RollBeatsEveryAttack`: each of the 9 damaging moves hurts a player who stands still (20–60 damage) and does **0** damage to a player who rolls once on time (Volley: a roll as each skull arrives).
  - `BossLab.Regent.SequenceBudgetAndDeterminism`:
    - the same fight at 60 and 30 rendered fps;
    - 9,000 ticks through both phases with all 11 moves used;
    - at most 2 skulls in flight;
    - at most 6.1% pool cover;
    - the boss stays within 12.6 m of the centre.
- **Bugs the tests found, now fixed:**
  - The Bell pool burned a player who had already rolled out. Fix: an 18-tick ignition.
  - A player staying close locked out Volley, Dash, Bell and Furrow. Fix: the close-range commit described above.
  - One test bug: the volley's "stand still" case was also rolling.
- **Captures.** Two 24 s captures (fixed 30 fps): dungeon, revamp characters, scripted test player. The phase-one capture played its whole sequence and reached the transition; the phase-two capture covered Ash Step, Pyre and Volley. Sheets are in `artifacts/art/regent-moveset-2026-11-09/` and were inspected:
  - `phase1-{arc,volley,rite,dash,bell,furrow,wakes}-sheet.png`;
  - `phase2-{ashstep,pyre,volley}-sheet.png`.
- **Problems found in the captures:**
  - The transition burst was blinding. Fix: lower and wider.
  - The pyre circle was an opaque lavender sheet. Fix: a dim fill plus rim. The rejected sheet is kept as `phase2-pyre-rejected-bright-mark-sheet.png`.

## Refinement pass (2026-11-09, later)

The owner asked to "rectify all the problems, gradually refine the moves". The other session's staff/manacle draft was ignored, as instructed.

- **Real props instead of primitives.** Prepared by [prep_regent_props.py](../unreal/art-studio/source/regent/prep_regent_props.py) in project-local Blender and imported in editor mode by [ue_import_regent_props.py](../unreal/art-studio/source/regent/ue_import_regent_props.py) into `/Game/BossLab/Regent/Props` (local):
  - **Censer:** the CC0 Poly Haven `brass_diya_lantern`, a hanging brass lantern (1.9 MB, downloaded to `artifacts/.../props/`). Its PBR textures are darkened. It hangs along the chain direction with a dim blue core and glass.
  - **Chain:** the lantern's own chain is made of flat 0.4 mm rings, which are too thin at boss scale, so I modelled an oval torus link instead. Up to 72 links follow the sagging chain path.
  - **Skull:** an interim model built in Blender from blended volumes, voxel remesh and carved sockets, nose and mouth, plus a tooth row (`skull-interim-previews.png`). I capped it at three attempts plus one placement correction. It is stylised, not a reference sculpt, and should be replaced by the generated skull once the free GPU quota resets. It gets glowing eye points.
- **Sound.** Eight original procedural cues come from [make_regent_audio.py](../unreal/art-studio/source/regent/make_regent_audio.py) (no samples):
  - `RegentBell`: an inharmonic funeral bell for Grave Bell;
  - `RegentWhoosh`: censer whirl, sweep and drift;
  - `RegentThrust`: every estoc contact, and each Rite window;
  - `RegentSkull`: a wail on each skull launch;
  - `RegentEruption`: each furrow burst;
  - `RegentBlink`: ash-step vanish and reappearance;
  - `RegentPyre`: the pyre blast;
  - `RegentWakes`: a drone for the phase change.

  They play spatialised at the boss, censer, skull or mark and respect mute. They have not been listened to here, only level-checked.
- **Readability.**
  - **Blade glint:** a star flash on the estoc point 16 to 4 ticks before every estoc or ash-step contact.
  - **Censer flare:** the censer's flame and light rise during censer wind-ups.
  - **Flames:** cards turn to face the camera, so they never show an edge.
  - **Pools:** they smoulder dimly until they ignite.
- **Pacing.** Held Thrust added, plus the per-move pauses above. The Drift Step flows straight into the Procession Dash.
- **Review tool.** `BOSSLAB_BOSS=regent ./scripts/bosslab-unreal capture regent-study` plays every move once against a stationary player, filmed side-on by a fixed camera (30 s).
- **Problems the study capture found, and their fixes:**
  - **Lunges tipped the body backwards.** Thrust, Held Thrust, Dash and Ash Step moved the body 1.2–1.5 m while the feet stayed planted, so the rear leg stretched and dragged the robe into a backward slope (`study1-held-contact-rejected-backward-tilt.png`). Fix: the Regent now glides under its robe on every lunge of 1 m or more, plus Ash Step.
  - **New test `BossLab.Regent.LungesLeanIntoTheThrust`** measures the head's lead over the pelvis in the facing direction. Guard is 14.2 cm. At contact, every lunge leans forward: 27.4 cm, and 44.9 cm for the dash. Through the whole contact window the lead never drops below 23.4 cm (41.6 cm for the dash).
  - **The lantern core bloomed into a white blob, and soul fire read as white candles.** Fix: dimmer core, glass and light; flame glow 6 → 3.5; a bluer core palette. Pool circles are dimmer too.
- **Tests.** Native suite **26/26**:
  - the roll test now covers 10 damaging moves, and each still takes 0 damage after a timed roll;
  - the sequence test uses all 12 moves.
- **Performance.** 720p, performance preset, dungeon and revamp characters, run back to back. The machine was heavily loaded by other apps (load average 14 → 54 during the runs):

  | Run | Regent mean / p95 | Warden mean / p95 |
  |---|---|---|
  | Pair 1 | 23.46 / 35.47 ms | 27.57 / 45.07 ms |
  | Pair 2 | 26.15 / 40.34 ms | 27.02 / 46.50 ms |

  Pair 2 ran in reverse order (Warden first). Across both pairs the Regent showed no measurable extra cost, but this is not an isolated measurement and makes no 60 FPS claim. Reports: `benchmark-{regent,warden}-dungeon{,-run2}.json`.

## Limits

- **Feel.** Not owner-tested. Every timing above is a first guess for tuning.
- **Placeholder visuals.**
  - The skull is an interim stylised model.
  - The flames are camera-facing cards; the phase-change ring still reads a little like ice spikes.
  - The sounds have not been listened to.
- **Poses.** Procedural keys, not authored animation. The revamp Regent mesh still has its generated robe, and the chain clips through it in places.
- **Performance:** only measured on a loaded machine (above).
- **AI.** None: fixed sequence only. No learning, model or adaptation is connected.

## Raise the Dead and censer floor contact (2026-11-12)

- **Raise the Dead:** a new move (index 16, in both phases) raises two slow skeletons that fall in three blows.
- **Censer:** the Censer Arc dips onto the floor and drags slowly, and the Grave Bell grinds back after its slam. Both use the same timing as before, with sparks and a scrape.

See [artifacts/art/raise-censer-2026-11-12/README.md](../artifacts/art/raise-censer-2026-11-12/README.md).
