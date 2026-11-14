# Funeral Regent — weapon and moveset draft

2026-11-09. Design proposal for owner review, not implemented or balance-tested. Owner set aside the arena draft; preserve existing arena work and local assets. B — Funeral Regent remains the outfit direction. No AI, training, model connection or game changes.

## Combat identity

An undead sovereign still carrying out sentences in an empty court. Slow, composed walking; sudden but visibly prepared bursts; long, deliberate punishment windows. His threat is controlling distance, not filling the screen with simultaneous hazards. Three blue-flame skulls are witnesses under his command, never independent turrets.

## Weapon options and recommendation

| Option | Identity | Trade-off |
|---|---|---|
| Execution sword + left-hand chain | Direct prison executioner; clearest continuation of current sword poses | Strong melee identity, less distinctive ceremonial silhouette |
| Pure funerary staff | Regal necromancer; simple casting gestures | Risks making the encounter mostly a projectile chase and weakens hook-to-stab identity |
| **Execution staff + separate chain manacle** | **Recommended: sovereign, jailer and executioner in one coherent silhouette** | Requires fresh polearm grip/stance/strike animation; cannot reuse sword motion unchanged |

**The Last Writ:** approximately 2.2 m overall as a starting art proportion, adjusted to the actual Regent rig. Blackened steel shaft, worn silver grip collars and a narrow ivory-coloured steel spear blade held within a broken crown. A small blue ember sits below the blade, not a giant glowing orb. The crown has one missing prong; tally notches and repaired bindings show centuries of use. Keep its head narrow so it does not conceal anticipation poses. The blade is metal, not literal brittle bone. Geometry length does not silently determine gameplay reach.

**The Return:** separate left-bracer reel and open, hooked manacle attached to a chain. The staff stays in the right hand during the throw, braced beside the hip. The head of the staff does not detach or transform. Chain deploys outside the left sleeve; no free-spinning flail or live rigid-body chain as combat authority. This separates the catching silhouette from staff thrusts and skull casts.

**Three Witnesses:** small skulls behind the shoulders. One comes forward for a single shot; all three forming a line announces the later fan. Their glow drops during melee so the weapon remains legible.

Lore: the Regent used the staff to pronounce sentences, the manacle to return fugitives, and the witnesses to remember their names. He has forgotten who issued his own orders.

## First complete kit: five attacks and one movement

All timings below are starting hypotheses, not measured or accepted frame data. Keep player greatsword, roll and stamina rules unchanged. Validate each opening with actual approach and remaining roll recovery.

| Move | Pose and action | Player response / commitment |
|---|---|---|
| **Crown Sweep** | Both hands on staff; low lateral chamber, then one broad waist-height sweep. About 0.8 s tell, 1.2 s recovery. | Roll through or leave the arc. No hidden return swing; fixed facing through the final portion of the tell. |
| **Final Sentence** | Staff draws vertically above the crown, then one planted downward strike. About 1.2 s tell, 1.6 s recovery. | Sidestep or lateral roll; principal close-range greatsword punish. No ground explosion in the first version. |
| **The Return** | Raised left elbow and audible reel release announce a straight manacle throw. Staff held low and still. Successful catch pulls toward a safe stop, then releases before a separately telegraphed staff thrust. | Lateral movement or roll avoids catch. Catch itself deals no damage. Released player can sidestep the thrust even without roll stamina. Miss leaves a long retrieval opening. |
| **Witness Ember** | One skull moves beside the staff head, jaws open, a compact blue core forms; one fireball launches along a fixed line. About 1.0 s tell, 1.2 s recovery. | Strafe or roll through. No homing, lingering floor fire, proximity burst or immediate melee cover. Projectile consumed by first valid contact or wall. |
| **Threefold Verdict** | All three skulls form a clear horizontal row and flare together; three simultaneous fireballs spread in a fan. About 1.3 s tell, 1.6 s recovery. | Walk a deliberate gap or dodge one lane. Gap width must be tested at useful distances. One damage event maximum per cast. Later extension after the single shot works. |
| **Mourning Step** (movement) | Visible crouch/weight shift, cloak gathers, then a short low glide with a restrained ash trail. Starting study: 0.45 s tell, 2–3 m over 0.35 s, 0.6 s settling. | Direction commits before motion. Boss remains visible and vulnerable, stops at obstacles, and cannot pass through the player. No contact damage or attack hitbox on the dash. |

## Chain sequence contract

Retain the prior planning contract: 66-tick cast tell at 60 Hz, aim locks for its final 24 ticks; initial 6.5 m range / 12 m/s speed; miss recovery 90 ticks. These are proposed values only. Hook-tip contact during player invulnerability consumes the interaction rather than catching after invulnerability expires. Decorative chain links have no hitboxes.

Pull is capsule-swept, bounded to 45 ticks, and ends outside boss collision. First obstruction breaks tether and cancels the follow-up; no wall-slide dragging, teleport or pulling through a pillar. Release restores normal movement before a separate 48-tick thrust tell, with aim fixed for its last 24 ticks. The thrust can miss and requires actual blade contact. Cancel it if the destination does not provide a movement escape. No guaranteed cinematic stab, camera cut or button-mashing escape. Start with an 8 s minimum chain cooldown, independent of controller.

## Movement and encounter rhythm

Normal walk turns chest and feet coherently; no perpetual sideways skating. Mourning Step may close space or move laterally, with no chained dashes, lock-on break, invisibility or invulnerability. It cannot cancel attack recovery or erase a missed-attack punish window. Prototype one forward direction first, then lateral variants after camera and footwork review. Do not add a special damaging dash-thrust initially: after settling, every attack still plays its full tell.

First rehearsal: sweep → pause → overhead → pause → single ember → pause → dash/settle → pause → hook sequence. This is a fixed demonstration, not adaptive AI. Boss cannot cast while a chain capture is active; skull attacks cannot cover melee recovery. Fireballs expire before another attack starts in the first version. Introduce the three-shot fan only after single-shot readability and safe gaps pass review. Any later phase transition waits until recovery ends; it does not cancel an earned punish.

## Build order and review gates

1. Staff/chain weapon silhouette sheet, front/side grip drawings, and actual greybox proportions against current rig and camera. This is the next action, not detailed texturing.
2. Staff idle, sweep and overhead as pose studies. Verify hand placement, shoulder/robe clearance, foot contact, blade path and real greatsword punish.
3. Mourning Step with root/capsule alignment, wall stopping and readable tell at normal camera distance.
4. Single skull fireball: finite swept projectile, roll-boundary checks, wall collision and normal-camera VFX readability.
5. Hook/pull/release/thrust as a dedicated fixed test. Verify all directions, near-wall cases, zero stamina escape, death/reset/pause cleanup and no unavoidable damage.
6. Three-shot fan only after the basic kit succeeds. Paired same-preset performance capture and human review before more spectacle or adaptive behaviour.

Excluded from first kit: teleport, independent skull firing, ground-fire carpets, giant AoE ring, aerial grab, chain whirlwind, weapon transformations and animation-driven rule changes. Actual current build still has its existing moves; none of this document proves these proposals are implemented.
