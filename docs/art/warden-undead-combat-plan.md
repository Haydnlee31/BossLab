# Undead Warden — combat design and QA proposal

Planning only, 2026-11-08. No implementation, animation, balance or performance results claimed. Undead armored jailer, floating blue-flame skulls and chain-hook retrieval are the visual/mechanical identity. Start with authored fixed rehearsal; no adaptive AI, RL or model work. The sketches should illustrate distinct body poses and chain paths, not promise new implemented systems.

## Existing player constraints

Actual engine definitions remain authoritative: greatsword30-tick windup/20 active/36 recovery (86 ticks total,1.433s),22 stamina; roll36 ticks,28 stamina, invulnerable ages4–17 inclusive (`[4,18)`), followed by existing8-tick recovery gap. Healing commits at60 ticks within78. These are not to be changed to accommodate boss spectacle. All proposed boss numbers below are first tuning hypotheses at60Hz, not measured frame data. After a successful dodge, an opening must account for remaining roll recovery, approach, greatsword startup and safe withdrawal—not merely exceed30 ticks.

## Six attacks with distinct silhouettes

| Attack | Readable tell and shape | Initial timing proposal | Counter and intended opening |
|---|---|---|---|
| **Gravewarden's Cut** | Weapon drawn across opposite hip; torso twists before one broad horizontal cut. Skull flames dim so steel is the focus. |48 windup/18 active/72 recovery; aim locks18 ticks before contact. | Roll through the blade or leave its arc. One-cut punish when already close; verify at both sides, not assumed from table. |
| **Headman's Sentence** | Both hands raise weapon vertically, ribs stretch and one long inhale precedes a narrow downward chop. No fake release followed by a second hidden delay. |72/16/96; final aim locked24 ticks before contact. | Sidestep or late lateral roll. Committed planted miss is the principal safe greatsword punish. |
| **Ossuary Backhand** | Boss exposes elbow, hook hand retracts to chest; short metallic scrape differs from sword tell. One close-range backhand, no automatic combo follow-up. |42/12/66; lock18 before contact. | Dodge toward its outside or back away. Spacing reset; do not promise a full free hit from every angle. Never an instant rear-player detector response. |
| **Gaoler's Claim** | Hook held above left shoulder; blue flame runs down a visibly slack chain and the boss plants a foot. Throws a straight hook, then attempts pull and separately telegraphed stab. |66 windup, lock at tick42; projectile speed/range fixed (start1200cm/s,max650cm);90-tick recovery on miss. | Lateral movement or roll through hook; later evade the stab even after being caught. Detailed contract below. |
| **Three Witnesses** | Exactly3 skulls leave orbit and form a visible horizontal fan; all three flare once before simultaneous straight flight. Boss remains planted. |72 windup; directions lock24 before launch; finite range/lifetime;96 recovery after launch. | Move through an intentional gap or roll through one lane. No homing after release, no staggered volley demanding several rolls. Cannot overlap hook or melee in first prototype. |
| **Ashen Verdict** | Skulls descend into a floor ring, flame briefly gutters, then one thin expanding blue ring crosses the arena. |90 windup; one ring lasting at most90 ticks; boss stays inactive until it expires, then72 recovery. | Walk beyond its finite radius if close to boundary, or roll across ring; no jump requirement. Ground marker encodes propagation, not an instant unavoidable area explosion. |

Damage provisional: cut24, overhead32, backhand16, skull volley18 maximum per cast, ring20. Hook0 on catch, stab28 only if its actual contact succeeds. Set per-instance hit consumption so three skulls cannot stack54 damage on one overlap. Keep skulls decorative/passive between explicit casts: no independent auto-attacks, camera occlusion or unannounced chip damage.

## Hook/pull/stab fairness contract

1. **Throw:** capture target world position at tick42 from observable world state; no raw input, future action or hidden stamina lookup. Final24 windup ticks and projectile travel never retarget. Hook has a visible tip and narrow swept hit capsule, not a wide invisible chain collider. Range and speed are fixed, not changed by distance or whether player rolls.
2. **Dodge:** evaluate projectile contact against the same engine-owned roll invulnerability as melee. Contact during ages4–17 consumes that projectile interaction and passes through harmlessly; it cannot linger inside the body and catch on age18. The visual tether itself never damages/grabs. Other spells use the same principle. A separate fresh hit outside iframes may legitimately land.
3. **Catch:** only a valid vulnerable hook-tip contact may create a tether. Catch deals no damage. Enter an explicit bounded cosmetic/forced-move state; no button mash or unexplained input failure. Proposed maximum pull45 ticks. Buffer the existing dodge intent; do not spend its stamina until normal action acceptance. No automatic heal cancel before an actual hit.
4. **Pull:** sweep the player capsule continuously toward a fixed safe stop outside boss collision, never teleport or move through pillars/walls/other geometry. Limit displacement/speed; stop on first obstacle, snap the tether, release immediately and cancel the stab. Reject an initially obstructed route. Cancel on either actor death/reset, target invalidation or timeout. Never move either actor outside the arena or into a navigation-dead pocket.
5. **Release then stab:** end the restraint before the stab tell begins. Restore movement immediately and allow normal buffered actions; do not leave hidden hurt/input lock active. Give a new fixed48-tick windup, with aim locked for its final24 ticks,12 active ticks and96 recovery. Players may sidestep even at insufficient roll stamina. There is no guaranteed cinematic stab, tracking teleport, forced facing/camera cut or damage on a timer. Use actual weapon contact.
6. **Interruption:** any wall cancellation or defeated boss clears both tether endpoints and all pending callbacks. A missed throw cannot become a proximity grab on return. Repeated catches have a fixed minimum cooldown (initial8s) and cannot chain directly from stab recovery; the same cooldown applies to every controller. Cancellation must not silently restart a throw.

The48-tick release window is a proposed minimum to verify in arena geometry, not proof that escape exists. If a wall blocks both movement directions, cancel the stab rather than shortening windup or demanding a roll without stamina. Keep the first prototype free of simultaneous skull hazards during the whole hook sequence and release window.

## Rehearsal and phases

Build and review cut/overhead first, then hook as its own deterministic test scene, then one skull attack at a time. Only add all six after each has readable actual poses and tested escape. Fixed rehearsal sequence uses explicit idle gaps; no input-triggered reaction selector. A later low-health presentation can expose the skull chorus with a safe, damage-free transition, but it must not speed up existing moves or change roll/contact rules. Treat any new move as a new declared definition. Do not turn health phase into an attack-cancel that erases the player's earned punish window.

## Independent QA gates before human fight review

- **Timing/contact:** log attack instance, tell start, aim lock, each active frame, contact, recovery and action readiness; compare engine timing to actual rendered weapon/hook paths at60Hz. Test under low FPS and large delta time for sweep tunneling. No collision from fading flames/returning chain.
- **Iframes:** test hook contacts at roll ages3/4/17/18, near/far ranges and8 roll directions. Ages4/17 reject catch; age3/18 may catch if actual tip intersects. Verify one consumed projectile cannot reacquire after iframe expiry. Skull cast caps damage at one hit across simultaneous contacts.
- **Catch state:** exercise max-range and point-blank throws, near-wall/corner/pillar pulls, obstruction appearing mid-pull, player/boss death, pause/resume, reset and repeated invalid references. Assert finite bounded transforms, no overlap with blocking geometry and all input/tether state released. No unbounded tick callback or dangling target.
- **Stab counterplay:** replay catch with zero stamina, ordinary stamina, previous attack recovery and buffered dodge; prove at least one movement escape from legal destinations. Verify no fresh skull or melee overlap during the release window. Any unavoidable catch-to-damage sequence fails the proposed design.
- **Greatsword punish:** run real player strike after correctly dodging each declared punish move at practical ranges; include approach time, remaining roll duration and8-tick gap. Demonstrate at least one full safe hit after overhead/hook miss. Do not tune the player's timings to hide insufficient openings.
- **Readability:** inspect normal gameplay camera at720p with sound off; each move distinguishable by pose/trajectory, not blue intensity alone. Show distinct protected/vulnerable feedback without obscuring character. Blue flame must retain silhouette against dark backgrounds and not hide weapon contact.
- **Performance:** same-build/preset paired run with skull VFX off/on, one game instance, real wall-clock CSV and spike review. Budget cheap finite emitters/limited dynamic lights; never use capture FPS as performance evidence. No benchmark targets claimed passed yet.
- **Scope:** no model/adaptation work. Preserve the default rehearsal and immutable combat definitions during prototyping; changes become explicit engine-owned boss move definitions, not controller-side exceptions.

## Sketch prompts for the art director

A: side silhouette of planted throw pose—high hook elbow, slack chain behind shoulder, three silent skulls above back; contrasting grounded player stance and obvious lateral dodge lane.

B: three-panel interaction strip—hook passes through a protected roll; tether stops at pillar and breaks; released player sidesteps separately wound-up stab. Show the counterplay, not an unavoidable execution.

C: skull fan attack in normal third-person framing—three separated lanes, readable gaps, dim boss torso, no screen-filling flame wall. Each is concept only, never gameplay evidence.
