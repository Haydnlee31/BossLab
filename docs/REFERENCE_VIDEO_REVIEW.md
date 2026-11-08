# Godfrey / Hoarah Loux reference review — 2026-11-03

The owner supplied the full local Shirrako recording after the earlier YouTube access failure. This review informs the existing fundamentals-first Unreal prototype. It does not approve new AI, final models, a second phase or a new combat ruleset.

## What was actually reviewed

Source: `/Users/haydn/Downloads/Elden Ring - Godfrey, The First Elden Lord Hoarah Loux Boss Fight (4K 60FPS) - Shirrako (1080p).mp4`.

Actual file: 1920×1080, nominal 59.94006 fps, duration 466.1861 seconds (7:46.186). The title mentions 4K, but this supplied file is 1080p. Source identity and metadata are saved under `artifacts/reference/godfrey/`.

Review method: sequential timestamped frame contact sheets across the entire timeline at four-second intervals; both combat sections additionally inspected at one-second intervals; selected axe, leap, grab and stomp sequences inspected at eight samples per second; locomotion and a backward roll examined at twenty samples per second. Final seconds were sampled separately. All generated contact sheets were visually inspected. This is a visual sampled-frame review, not continuous audiovisual playback or inspection of every source frame. Audio was not assessed. Small/occluded joints remain uncertain. Times below are approximate video positions, not engine action timestamps.

The original MP4 remains in Downloads and was not duplicated into the project. Extracted JPEGs are local reference material only, not shipped game assets. The saved Swift extractor uses installed AVFoundation; no package/model/asset download was required. Requested and actual presentation timestamps are retained in each `frames.json`.

## Timeline and visible evidence

| Video position | Visible event | Relevance to BossLab |
|---|---|---|
| 0:00–1:51 | Fog entrance and introduction: immense armored axe wielder, spectral lion, slow close-ups and monumental architecture | Establish scale through silhouette and staging. This long cinematic is separate from combat and unnecessary for our prototype. |
| 1:52–1:58 | Player approaches across a broad stone floor; boss remains readable against distant architecture | An enclosed arena needs open fighting space and visible boundaries. Decoration belongs mainly around the perimeter. |
| 1:58–2:02 | Boss coils, leaps forward and lands heavily; camera pitches upward, briefly loses the boss above frame, then rotates to reacquire | Study commitment, landing compression and camera stress. Do not deliberately reproduce the loss of visibility. |
| 2:02–2:05 | Player closes and attacks at the boss's legs; boss raises axe, cuts and continues into another strike | Attacks are connected through body poses. A first impact is not necessarily the end of a combo. |
| 2:06–2:24 | Repeated wide axe arcs, overhead preparations and close circling; player attacks, dodges and also takes damage | The encounter combines spacing and timing. The recording is not a flawless-play demonstration. |
| 2:25–2:33 | Player opens distance, heals and repositions while boss advances | Healing has visible commitment and uses space; transitions out of combat poses matter. |
| 2:34–2:45 | Foot/weapon impacts throw stone and dust; a bright ground fissure precedes a larger eruption around 2:43–2:44 | Separate initial contact, ground warning and secondary impact. Effects communicate distinct stages. |
| 2:46–3:10 | More close exchanges and player punishment of openings; boss health reaches the transition | Preserve ordinary readable strikes as the foundation even when spectacle exists. |
| 3:10–4:44 | Phase-change cinematic: lion removed, armor/weapon presentation gives way to unarmed Hoarah Loux | Phase identity is conveyed through stance and silhouette. This is future inspiration, not current scope. |
| 4:45–4:57 | Arms-up preparation, outward pulse, leap and ground slam; glowing ground develops before another eruption | A large attack can be a multi-stage sequence with several readable moments. |
| 4:58–5:03 | Low forward approach with open arms, catch, player throw, airborne follow-up and slam | Grab choreography requires a distinct tell and synchronized bodies. Too much scope for the next fundamentals pass. |
| 5:05–5:34 | Advancing hand strikes, leaps, stomps and short player counterattacks | Phase two changes movement vocabulary and pressure, not merely weapon appearance. |
| 5:35–5:39 | Boss raises a knee and holds it; player rolls backward, returns and jumps; stomp finally releases and player takes damage | Particularly clear contrast between anticipation and release. An early dodge does not automatically cover the later impact. |
| 5:43–5:52 | Pulse, leap, slam, glowing ground, delayed eruption | The sequence repeats recognizably. Repetition lets the viewer learn the visual pattern. |
| 5:53–6:04 | Charging grab and aerial slam near the railing, then separation and healing | Boundary proximity stresses camera and positioning. Test our corner behavior explicitly. |
| 6:05–6:38 | Close hand combinations, stomps and another ground eruption; boss crowds the camera | Tall enemies must remain legible at melee range; effects and bodies sometimes obscure the player here. |
| 6:39–7:13 | Further repeated attacks, slam/eruption and short openings | Readability must survive repeated exchanges and low boss health. |
| 7:13–7:18 | Player runs laterally/backward around the approaching boss; camera orbits with the encounter | This segment is locomotion, not a full roll. Useful for separating travel direction from target-facing behavior. |
| 7:19–7:28 | Final exchange, boss defeat reaction and dissolution | Defeat has clear physical and visual resolution. |
| 7:29–7:46 | Reward presentation, player movement and site-of-grace interaction | End-state feedback is explicit; no further combat. |

## Motion observations

**Weight comes from sequencing.** In the close axe sequence at 2:17–2:24, wide planted stances, torso rotation and changing hand positions support the weapon arc. The weapon travels quickly during release, then carries through before the body recovers or prepares the next strike. A constant-speed sweep or whole-body rotation would miss this distinction. The recommended application is stronger support-leg loading, hip/shoulder sequencing, blade follow-through and recovery in our own animation.

**The reference player uses two separate blades.** Their independent hands, paired cuts and jumping attacks are not a direct two-handed greatsword animation reference. Preserve the owner's approved deliberate greatsword pace and single shared hilt. Borrow the whole-body commitment and transitions; author the greatsword mechanics for our weapon. The boss's two-handed axe is useful for studying weight, but its proportions, grip and trajectories are also different.

**The held stomp is unusually clear.** Around 5:35.5 the raised-knee pose is established; it remains visible until about 5:38.5, followed by a rapid downward release and dust/impact around 5:38.6–5:38.9. These are approximate visible landmarks, not exact wind-up/hitbox durations. The footage cannot establish why the boss held the pose or whether its controller observed an input. BossLab must continue to use engine-owned fixed timing and permitted observations.

**A roll is articulated travel.** The backward dodge around 5:36 shows the torso lowering, a compact tumble, a low landing and rise back toward the opponent. The camera does not roll with the body. Hair/cloak obscure parts of the skeleton, so this is a silhouette/phase reference rather than a joint reconstruction. Our roll should read as push-off → tuck → travel/contact → planted recovery, with feet and body height agreeing with root displacement.

**Movement and camera belong together.** Most combat uses a rear third-person view with the player low in frame and the target ahead. Close circling changes the view around the boss; large leaps cause steep pitch changes. At 7:13–7:18 the player repositions laterally/backward while the encounter remains framed. Preserve the approved camera's basic framing, then test melee overlap, flank crossings, leaps and walls. Smooth target framing must not obscure the incoming weapon or snap the player's facing on roll exit.

**Tells are primarily physical.** Raised arms, a lifted knee, open-handed forward posture and an axe drawn overhead distinguish attack families before impact effects. Ground cracks/glow help distinguish a delayed eruption from the first slam. These are better motion references than relying entirely on colored UI warnings. Retain accessibility cues, but make poses readable without them.

**The arena supports the fight.** Large unobstructed stone surfaces, strong perimeter silhouettes and warm distant light provide scale. The playable floor remains comparatively simple. Dust, hair, cloth and debris sometimes obscure contact; our smaller prototype should protect visibility and frame time rather than reproduce that density.

## Concrete application to the existing prototype

These are proposed priorities for the next implementation pass, not changes made by this review:

1. Preserve approved basic greatsword timing. Refine body loading, support-foot placement, hip/shoulder turn, hand spacing and follow-through within that timing. Keep the visible blade and engine-owned contact sweep aligned; do not create a misleading fast visual hit followed by lingering invisible damage.
2. Refine directional roll silhouette, height and planted recovery. Check forward/back/side rolls, locked/unlocked, near walls, and transition into the next allowed action. Keep the camera upright and confirm the hilt/weapon stays coherent through the tumble.
3. Improve locomotion-to-attack/roll and recovery-to-locomotion blends. Test diagonal circling and backing away while locked. Avoid foot skating, abrupt facing changes and a floaty upright body during a heavy action.
4. Polish the current fixed boss attacks: stronger distinct anticipation silhouettes, deliberate hold versus release, believable follow-through and clear end-of-sequence recovery. Keep adaptation disabled. Only then consider an original stomp/ground attack with an explicit separate warning for any secondary impact.
5. Capture comparable packaged footage at normal speed and slow inspection, including both fighters and ground contact; run combat tests after changes and re-profile in a quieter session. Animation/contact tests alone cannot establish convincing weight or sustained 60 FPS.

Our current runtime-keyed poses and grip tests establish a functional prototype; they do not establish reference-level animation quality. This review supplies direction, not a claim that the current game matches the reference. Final characters, cinematics, grabs, phase changes, adaptive selection, RL and model integration remain deferred.

## Limits and evidence

The recording cannot reveal raw inputs, button mappings, input latency, invulnerability windows, collision shapes, stamina formulas, camera parameters, animation implementation or the boss's internal decision logic. No such values were reverse-engineered here. Tab targeting and Space rolling remain the owner's BossLab requirements, not deductions from this footage. No audio timing or sound-quality assessment was made.

Evidence directory: `artifacts/reference/godfrey/`. `review-coverage.json` lists sampled ranges/counts and reviewed sheets; `source-identity.json` identifies the unchanged supplied video. This is external reference evidence, not gameplay evidence of BossLab. No game source, package, combat tests, evaluation scenarios or training artifacts changed during this review.
