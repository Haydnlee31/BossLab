# The Warden of the Unquiet — next-stage proposal

2026-11-08. Planning and generated concept illustrations only. User confirmed the V13 launch works; this does not constitute player art acceptance. No new boss meshes, abilities, animations, tests or benchmarks were implemented in this stage. Adaptive selection, statistical learning, RL and model connections remain deferred.

## Selected creative direction: B — Funeral Regent

The Warden once held three condemned witnesses alive until judgment. The court died first. His prison outlasted its kingdom, and he now treats every living visitor as an escaped soul. He fights with the patient, practiced motions of a jailer, then sudden committed bursts. He remains grounded; three blue-flame skulls float behind his shoulders.

Three original visual options are in the concept sheet:

- **A — Ossuary Gaoler (unselected alternative):** barred skull visor, fitted blackened steel, narrow ribbed cuirass, worn brass prisoner tags, articulated shoulders and a split coat. Strongest prison identity and clearest arms/legs for animation.
- **B — Funeral Regent (owner selected):** ivory death mask, narrow crown, engraved silver ribs and an embroidered mourning mantle. More regal; the long fabric shown in the sketch adds rigging and collision work. Preserve its long mourning silhouette; use separated back panels, open arm paths and a clear front stride opening, with hem length resolved in pose tests.
- **C — Chainbound Penitent:** exposed jaw, iron collar, burial linen and broken armor. Strongest horror silhouette, but exposed anatomy and layered wraps need careful deformation and cannot be hidden under surface noise.

Owner selected B on 2026-11-08, superseding the earlier A recommendation. Keep the ivory death mask, narrow damaged crown, ribbed silver armor and dark indigo embroidered mourning mantle as the identity. Do not substitute A's barred visor or prison coat. Seat the chain reel under a fitted ceremonial left bracer, with the wrist exit and casting shoulder unobstructed. Preserve the long mantle through weighted split panels and authored motion; shorten only where actual pose review demonstrates a need. Target a lean, tall silhouette; confirm apparent scale and lock-on framing against the current arena before changing combat dimensions. Sketch scale is not approval to enlarge collision or reach.

## Objects with a purpose

- **Return:** the left-bracer chain ends in an open hooked manacle. Its wear tells the story: polished inner links, worn reel guides, repaired cuff. It retrieves escaped prisoners.
- **The Last Sentence:** a straight thrust-capable execution sword, with a dark fuller and worn funerary tally marks near the guard. Its silhouette must support both cutting and stabbing; decoration cannot obscure the edge or grip.
- **The Witnesses:** three condemned witnesses whose skulls preserve the unfinished judgment. Give them distinct silhouette defects, such as a split brow, damaged jaw and sealed eye socket. Blue flames are restrained and secondary to the weapon tells. They are passive between explicitly declared casts.

## Signature move: Gaoler's Claim

1. Plant foot, turn torso and lift chain arm; give a distinct chain-rattle cue. Skulls retreat behind shoulders, leaving the attack lane clear.
2. Commit aim before releasing a straight swept hook. No homing after commitment, input reading or damaging chain shaft.
3. A protected roll defeats the contact using the existing invulnerability interval. A miss exposes the Warden while he retrieves slack chain.
4. A valid catch deals no initial damage and briefly reels the player to a safe standoff point. The player visibly stumbles/drags; no teleport or idle sliding.
5. Release the player before a separate, readable thrust wind-up. Restore movement; allow sidestepping even without roll stamina. The sword deals damage only on actual vulnerable contact.
6. A blocked route, unsafe arrival, death, reset or interruption breaks the tether and cancels the stab. Never drag through walls. No skull hazards during the sequence.

The combat proposal starts with a 1.1s throw tell, a maximum 0.75s pull and a separate 0.8s stab tell. These are untested tuning hypotheses at 60Hz. Actual safe escape and greatsword punishment must be demonstrated; the player's existing rules stay unchanged. The initial storyboard illustrates the threat and branches, not an approved guaranteed execution or exact trajectories.

## Moveset and bounded scope

| Move | Identity and counterplay | Delivery order |
|---|---|---|
| Gravewarden's Cut | Clear torso coil into one broad cut; roll through or leave the arc | First melee study |
| Headman's Sentence | Tall overhead pose into planted chop; sidestep, then punish | First melee study |
| Gaoler's Claim | Chain throw, bounded pull, release and avoidable stab; large miss recovery | Signature prototype |
| Witness Bolt | One skull aligns, flares and fires one straight projectile; sidestep or roll | First offensive skull move, after hook works |
| Ossuary Backhand | Explicit elbow tell into short spacing strike; never instant retaliation | Optional expansion |
| Three Witnesses / Ashen Verdict | Three-lane fan OR one expanding ring with no simultaneous melee | Later alternative, not both in first build |

The combat specialist's wider six-move proposal is a candidate bank. This consolidated plan narrows first delivery to two melee moves, the signature chain ability and one simple skull shot. No independent skull AI, summons, phase-two transformation or autonomous adaptive selection yet. Use manual triggers and a fixed rehearsal with explicit idle gaps.

## Production gates — avoid repeating the minor-detail loop

1. **Develop selected B silhouette.** Front, side, rear and gameplay-distance clay views with sword/chain. No surface polish until the proportions and outfit read correctly. Review the actual model beside the concept, not another beauty image alone.
2. **Prove motion and mechanics.** Parallel graybox branch for chain collision/cancel states, plus authored whole-body cast, brace, reel, miss, release and stab poses. Player dragged reactions are part of the work. Start with weighted anatomy and localized armor weights; no final rigid skirt/glove substitute.
3. **Fit and material proof.** Shoulder/elbow/hip stress poses, deliberate hands/grips, cloth splits and boot clearance. Proper UVs and authored steel, bone, leather and fabric response. Review one representative helmet/torso material patch before expanding detail across the character.
4. **Integrate restrained effects.** Three shared skull meshes, bounded blue flame, visual-only chain driven by engine endpoints. Begin without dynamic shadow lights or per-link physics. Keep existing boss as fallback.
5. **Review actual fight.** Fixed rehearsal at gameplay camera; hook hit/miss/roll/wall/reset cases, usable greatsword punish, control restoration, low-FPS contact, and same-build performance comparison. No claim of 60 FPS from recorded video. Human review before any AI stage.

Each visual gate gets an initial candidate and at most two targeted corrections. If the comparison still fails, stop ornament work, document the structural failure and change the authoring approach. Do not turn repeated procedural detail into supposed progress. Generated images are targets, never proof of build quality.

Provisional geometry targets: boss 60–100k visible triangles, skulls together below 10k, chain below 5k; validate actual material/overdraw and frame time, not polygon counts alone. Preserve the 10GB project budget and 24GiB free-space reserve. Rebuilding removed compiler caches needs roughly 0.9GB plus transient headroom; no rendering/build was attempted for this planning pass.

## Team handoffs

- [Art direction](warden-undead-art-plan.md): silhouette, lore, materials and visual acceptance.
- [Animation/technical art](warden-undead-animation-plan.md): weighted construction and pose branches.
- [Combat design and QA](warden-undead-combat-plan.md): candidate frame data, counterplay and failure tests.
- [Unreal feasibility](warden-undead-engine-plan.md): current source constraints and dedicated ability state.
- Root synthesis: this document resolves first-scope and release-before-stab decisions. All numbers are provisional; no tests were run because gameplay was unchanged.

Concepts and exact generation prompts: `artifacts/art/warden-undead-concepts-2026-11-08/`. Built-in image tool; no external model downloads or paid API workflow. B is selected. Next deliverable is a consistent front/side/back construction sheet and mantle/chain-arm pose plan; implementation remains a subsequent stage.
