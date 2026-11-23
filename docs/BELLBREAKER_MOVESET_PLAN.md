# The Bellbreaker: moveset plan (draft for owner review), 2026-11-18

**Built so far (2026-11-18):** Hammer Fall, Forge Sweep, Bell Quake (with the Twin Quake) and The Bell Breaks are playable as a greybox; see [BELLBREAKER_GREYBOX.md](BELLBREAKER_GREYBOX.md). Everything else here is still a plan.

This is a plan only. No move is implemented, and nothing here is AI. When it is built, it follows the Regent's rules: moves are engine-owned rows in `WardenRules::Strike`, they play in a fixed and labelled sequence, and the boss is opt-in, editor-game only, in Hearth A2.

All numbers are first guesses for a greybox, to be tuned by feel. Times are in 60 Hz ticks. **Telegraph** is the time from the first visible wind-up to first contact.

## Who he is, and what the fight should feel like

He is a giant smith, 4.6 m tall (about 2.5× the player), with a cracked bronze bell on an iron-banded haft. He should feel **slow, heavy and honest**: long, readable wind-ups and huge reach. His hits punish greed rather than trick you, and the long recoveries give you real openings.

- **The Regent contrasts with him.** The Regent's danger came from rhythm breaks and magic. The Bellbreaker's comes from space: big arcs, shockwaves and a floor that gets hotter.
- **The bell is the telegraph.** Before his big hits it rings: the clapper swings, there is a bronze shimmer, and a low tone. When he skips the ring, that is a delayed hit, used sparingly.
- **The forge is his ally.** Moves use the arena's real fixtures: the molten channel along the furnace wall, the quench cistern's steam and the hanging chains.

## Numbers he has to respect

These come from the current player rules (`WardenCombat.h`, `docs/SOULS_CONTROLS.md`):

| Player rule | Value | What it means for him |
|---|---|---|
| Roll i-frames | ticks 2–28 of a 40-tick roll (about 0.43 s) | Active windows of 8 ticks or less can always be rolled through. Long shockwaves must be outrun instead, or rolled through at their thin edge. |
| Roll distance | 320 cm | His sweeps reach about 5–6 m, so rolling away is often wrong and rolling **into** him is right. |
| Held input buffer | 64 ticks | A delayed hit should be at least 20 ticks later than the normal one. Otherwise the buffered roll still lands in time. |
| Walk / sprint | 420 / 630 cm/s | A boss walking at 260 cm/s (×2.5 stride) must not be outrun easily. Plan about 300 cm/s for his walk and about 700 cm/s for his charge. |
| Field | A2 walkable field ±800 × ±900 cm | His sweeps cover about a third of the field. Leave room to be outside them. |

## Phase one: the smith at work

| # | Move | Kind | Telegraph | Active | Damage | Recovery | Reads as |
|---|---|---|---|---|---|---|---|
| 20 | **Hammer Fall** | overhead | 54 | 6 | 34 | 70 | Two hands lift the bell high behind his head, the clapper rings, then a vertical slam 4.2 m ahead. The bell embeds for a moment: **the main punish**. Roll sideways or into him. |
| 21 | **Forge Sweep** | horizontal | 46 | 10 | 28 | 52 | Bell dragged low across the floor, about 200° at 5.2 m, throwing sparks. Roll through it toward him; rolling away is too short. |
| 22 | **Return Sweep** | horizontal follow-up | 22 (from Sweep) | 10 | 26 | 60 | Backhand the other way after some Sweeps. It is chosen by the fixed sequence, so learnable. Its flatter, faster telegraph is the "second roll" check. |
| 23 | **Tolling Stamp** | shockwave | 40 | ring 6 / tick | 18 | 40 | He stamps and rings the bell against the floor. A bronze ring expands from 1 m to 7 m at 1100 cm/s. The ring passes the player in about 3 ticks of contact, so a well-timed roll beats it, and so does being further than 7 m away. |
| 24 | **Anvil Shoulder** | charge | 38 | 14 | 24 | 48 | He drops the bell and barrels 9 m shoulder-first, bell trailing, aim locked 14 ticks before contact. He skids and then turns slowly: the back-attack window. |
| 25 | **Quench** | arena | 60 | — | 6 per 0.5 s | 30 | He dips the bell in the quench cistern. Steam blooms around the cistern for about 6 s, hiding his next telegraph (the screen grade cools, and his eyes or the bell still glow). Only when he is near the cistern. It sets up mixups and deals no direct damage. |
| 26 | **Hook and Haul** | grab | 50 | 8 | 40 (grab) | 64 | He hooks a hanging chain with the haft and hauls it in an arc. The chain is the hitbox, swept along the ceiling chain's line. If it connects: a scripted throw (no cut-scene), the player is knocked prone and stands up after a fixed delay. |

### Signature move (owner request, 2026-11-18): Bell Quake, slot 32

He slams the bell straight down into the floor and sends a shockwave across the hall. A player who neither jumps nor rolls through it is **stunned**.

| Beat | Ticks from start | What happens |
|---|---|---|
| Tell | 0 | The clapper rings inside the bell, then he raises it high in both hands. |
| Hop | about 54 | A small heavy hop that commits him. |
| Impact | 70 | The bell slams 3.2 m ahead. Dust, cracks, a camera kick and the ground-slam sound. |
| Shockwave | 70 onward | A bronze dust ring travels along the floor from 1.2 m out to 10 m at 850 cm/s. Its crest is 60 cm wide and 40 cm high. |
| Recovery | 70 + 80 | The bell is embedded and he heaves it free. This is the punish window. |

**How the shockwave resolves:**

| Player state when the crest passes | Result |
|---|---|
| Inside 2.4 m at impact (the blast) | 30 damage and a knockdown. Only the roll's i-frames avoid it, and jumping does not help. |
| Airborne (jump lift above 30 cm) | Unharmed. |
| Roll i-frames active (ticks 2–28) | Unharmed. |
| Further than 10 m away | Unharmed. |
| Anything else (standing, walking, attacking, healing, landing) | 10 damage and a **stun for 84 ticks (1.4 s)**. |

The crest is 60 cm wide at 850 cm/s, so it passes a player in about 4 ticks. A roll needs normal timing, and a jump's long airborne window (above 30 cm for about ticks 6–40 of 46) makes it the more forgiving answer. That makes it the fight's jump check.

**Stun rules** (new and engine-owned, alongside `HurtTicks`; to be added to `WardenCombat`):

- **Effect:** no movement, attack, roll or heal. Stamina regeneration pauses, and buffered input is dropped.
- **Breaking out:** any blow landing during the stun breaks it at once. It deals normal damage plus the usual flinch, so a stun can never chain into a guaranteed combo.
- **Immunity:** after a stun ends, the player cannot be stunned again for 300 ticks (5 s).
- **Phase two (Twin Quake):** a second crest follows the first. It was planned at 30 ticks and **built at 45**: at 30, no second answer could come out in time. At 45, roll-roll, jump-jump, jump-roll and roll-jump all work.

**Assets, 2026-11-18:**

- **His slam:** HY `bell_quake` (s0/s1). The hand-speed peak is at 1.1 s and the impact is at about 1.18 s.
- **Player stun:** HY `stun` (dazed stagger with a hand to the head) for the shockwave stun, and `stun_kneel` (drops to one knee) for the blast knockdown.
- **Sounds:** generated with Stable Audio Open. The tell is `clapper_tell`, the impact `bell_slam_ground`, the ring `shockwave` and the stunned player's ears `stun_ring`.
- **Preview:** `BOSSLAB_BELLBREAKER_PREVIEW=quake` shows it in A2 with sound, a ring and a stunned mannequin. It has no rules, damage or input.

### Phase-one rehearsal sequence

Hammer Fall, Sweep, Stamp, Sweep → Return, Shoulder, Hammer Fall, Quench (only when near the cistern; otherwise Stamp), Haul.

Pauses follow the Regent pattern:

| After | Pause |
|---|---|
| Fall, Shoulder | 40 ticks (main punish windows) |
| Sweep | 24 ticks |
| Return | 32 ticks |
| Stamp, Haul | 28 ticks |
| Quench | 0 ticks (it chains into the next move under cover of steam) |

## Phase two (from 50% health): the bell cracks open

- **Transition, "The Bell Breaks":** about 90 ticks, untargetable for the first 30. He smashes the bell against the anvil and the crack splits wide. Molten bronze now glows inside it, and the slag drips leave short burning trails. Damage is 30 if you are close when it cracks (ring 4 m). This is the 50%-health beat the concept's name promises.
- **The molten channel overflows.** One slow pool per Hammer Fall (2.4 m, burns 5 per 0.5 s, as the Regent's pools, at most 4 at once).

| # | Move | Kind | Telegraph | Damage | Reads as |
|---|---|---|---|---|---|
| 27 | **Molten Fall** | overhead | 54 (same as Fall) | 34 + pool | The phase-one Fall, now leaving a burning pool at impact. |
| 28 | **Slag Fling** | ranged | 36 | 14 ×3 | He swings the open bell and flings three molten globs in a fan. Each lands and leaves a 1 m puddle for 3 s. It punishes staying far away, the safe zone for the Stamp. |
| 29 | **Death Knell** | delayed overhead | 54 + 28 hold | 38 | The Fall's wind-up, held at the top with the bell **silent** (no ring), then the slam. It is the deliberate rhythm check: 28 extra ticks is more than the held-input buffer's early roll. |
| 30 | **Peal of Ruin** | combo | 46 / 22 / 60 | 26 / 26 / 40 | Sweep, Return, then a leaping Hammer Fall that tracks the player up to 6 m. The finisher's long recovery (90) is the reward. |
| 31 | **Great Toll** | arena-wide | 90 | 24 | He plants the haft, lifts the bell overhead and rings it three times. Three expanding rings follow at 30-tick intervals; each needs a roll or a gap. On the third ring, every chain in the hall shakes loose dust, purely visual. |

### Phase-two sequence

Molten Fall, Slag Fling, Peal of Ruin, Stamp, Death Knell, Sweep, Shoulder, Great Toll, Molten Fall.

Phase two uses 60% of the phase-one pauses, as the Regent does.

## Health, stance and size

| Rule | Value | Why |
|---|---|---|
| Health | 900 | The Regent's 600 already aims at a fight measured in minutes. He is slower, so he has more openings per minute. |
| Phase two | 450 | |
| Poise / stance | 8 | Stance breaks drop him to one knee, using the HY kneel retargeted (BossHurtTicks 84, ×2.5 critical). |
| Scale | Mesh is 4.6 m. The capsule half-height is 95 × 2.55, with a much wider capsule radius. | Hit volumes run along the haft and the bell (two spheres plus a capsule), not the hand bone alone. |
| Lock-on camera | Lower and further than the Regent's | Already done for the Regent's 1.5 scale. He needs about 1.7× that distance. |

## Animation sources (needs the retarget pass)

The retarget (`ue_retarget_bellbreaker.py`) creates `BB_*` copies of 16 mannequin, UAL and HY clips on his skeleton. These are good for locomotion, hits, stagger and death. **None of them is a two-handed hammer**, so his attacks need new HY-Motion takes. The Space is text-to-motion, and the outputs stay local.

- **Overhead:** "a giant raises a huge hammer with both hands high behind his head, holds, then slams it down to the ground in front".
- **Sweeps:** "a heavy two-handed horizontal swing low across the floor from right to left" and its mirror.
- **Stamp:** "stomps one foot hard and strikes the ground beside him".
- **Shoulder charge:** "lowers his shoulder and charges forward, then skids to a stop".
- **Phase two:** "smashes a weapon against an anvil, staggering back", "plants the hammer and rings it overhead three times", and a fling throw.

His **contact timing stays engine-owned**, as for the player's cuts. Clips are time-warped so their contact frame lands on the move's contact tick. The haft and bell hitboxes follow the engine's path, not the clip.

**Generated, 2026-11-18:** all ten clips above, two seeds each, are retarget-reviewed with the hammer in hand (`artifacts/art/bellbreaker-boss-2026-11-18/README.md`). The left hand still needs IK onto the haft.

## Build order (once the owner approves this plan)

1. Retargeted idle, walk and stalk play on the preview boss in A2. This is the current pass, which is waiting for disk space.
2. Generate and retarget the HY hammer clips listed above, then review them side-on (`capture` study).
3. Greybox phase one: rows 20–26, bell hitboxes, a fixed sequence and the native tests (roll beats every attack, as for the Regent).
4. Phase two: rows 27–31, the transition, pools and fling.
5. Arena hooks: steam (Quench), chains (Haul), molten channel overflow.
6. Audio: bell tones from the existing procedural layer (`make_regent_audio.py` pattern) plus Kenney impacts.

## Open questions for the owner

- **Hook and Haul** is a grab with a forced knockdown. Keep it, or swap it for a plain chain sweep (no grab)?
- **Quench** hides his telegraphs behind steam. Fun, or does it read as unfair?
- Should he drop his weapon for the charge and pick it up again (as in the concept's lower panel)? The alternative is to keep it in hand.
- Is 900 health right for the first greybox?
