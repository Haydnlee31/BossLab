# Undead Warden — engine feasibility and implementation plan

Planning only, 2026-11-08. No gameplay, asset, configuration or binary changes were made for this proposal. This assessment uses the current local C++ source; it is not a claim that the abilities already exist. Boss AI/adaptation/RL/model integration remain deferred. First presentation uses a practice dummy and explicit fixed rehearsal sequence.

## Recommendation

The undead armor, a small escort of floating blue-flame skulls, and a chain-hook pull into a stab are feasible in the current Unreal prototype. They are not equally small changes. Costume/skull presentation can be isolated; the hook requires a new deterministic ability and capture/release state, swept collision, coordinated two-character animation, cancellation rules and fairness tests. It should not be implemented by pulling the player with a physics rope or by inserting another sword pose into the current three-move array.

Make one readable signature sequence first: the Warden braces, the skulls pull back and flare, a hook fires down a committed lane, a successful hit briefly reels the player toward a safe standoff point, then the Warden releases the tether and thrusts. The hook's chain is visual; engine-owned state determines the pull. If the hook misses, the Warden must visibly retrieve it and remain punishable. The skulls initially supply silhouette, anticipation and recovery cues rather than additional projectiles obscuring the new mechanic.

## What the current code actually supports

- `WardenCombat.h/.cpp`: 60Hz fixed simulation, six action states, three boss sword definitions, `Cooldowns[3]`, `CanStrike` bounded to three moves. Dodge protection is ages4–17 inclusive, with a36-tick roll. Damage handles invulnerability, death, hurt and boss poise. There is no captured/tethered state, projectile state or synchronized grab.
- `WardenEncounter.cpp`: the rehearsal explicitly cycles sword moves0,1,2; player and boss movement/poses run before swept blade hits. Aim is committed when an action begins. `ResolveStrike` uses five previous/current blade points, environment occlusion and one-hit consumption. Reset/death/pause paths already exist but do not own special ability cleanup.
- `AWardenChallenger` is an `APawn` with a capsule and explicit `MoveSwept`, not CharacterMovement. `MoveSwept` performs capsule movement then wall sliding. A hook pull needs its own swept, no-slide rule; ordinary wall sliding would create sideways dragging around obstacles.
- `WardenSword.cpp`: original authored keyed poses and IK drive a poseable Epic skeleton; locomotion uses the installed blendspace. There is no existing montage-driven boss grab system. New hook throw/reel/thrust poses must share the same fixed phase clock as collision. Animation notifies may decorate effects but must not become a second timing authority.
- Existing costume import proves geometry can follow bones, not that cloth/finger skinning is solved. V13 remains an opt-in player trial with visible cape intersections and approximate grip. The boss costume must be separate, with the current boss/default player preserved.
- Module dependencies do not currently include Niagara, CableComponent or GameplayAbilities. No need to add a large gameplay framework for one bounded prototype ability. Any future effect plugin addition needs an explicit small implementation decision and measured shader/build cost.

## Proposed engine structure

Keep current sword definitions and IDs unchanged for regression comparison. Add a typed special-ability definition/state, instead of calling the hook a fourth sword index and overrunning the many three-element arrays. Append any new action enum values so historical numeric logs remain interpretable; version new encounter evidence explicitly. A small `FWardenSpecialAbilityState` can own ability ID, phase, phase tick, instance ID, committed launch direction, projectile position/previous position, target weak handle, reel start/end, timeout and release reason. Add an explicit captured/restrained fighter state with a bounded duration and ownership token. Do not reuse `Hurt`, which automatically clears after18 ticks.

Suggested separation when implementation is authorized:

- `WardenAbilities.h/.cpp`: engine-owned definitions and deterministic phase transitions; pure calculations where practical.
- Encounter integration: advance special states in a documented fixed-step order, resolve sweeps, apply accepted damage/capture, then advance action clocks. One hit/capture per ability instance.
- `WardenBossPresentation.cpp`: costume, hook/chain/skull transforms and effects, consuming read-only phase data.
- Dedicated native ability tests plus a graphical rehearsal/capture. Extend inspector/logging with ability phase, committed aim, collision result, release reason and captured duration.

Historical policy/statistics arrays and learned-model code must not silently receive new indices. During this milestone, the explicit rehearsal requests known actions; old adaptive/evaluation modes stay disabled and historical evidence remains historical.

## Chain sequence and collision contract

These are design proposals, not final balanced timings; the combat designer should freeze a single table before implementation.

1. **Tell/brace:** audible chain lift, distinct silhouette, skulls gather behind the throwing shoulder. Track only permitted observable world position until the declared aim commitment point; thereafter the throw lane stays fixed. Never inspect pressed keys, queued roll input or future scripted actions.
2. **Flight:** move a hook head along the committed lane at a fixed speed with maximum range/lifetime. Sweep its previous-to-current volume every simulation tick, using collision responses that include the arena and intended target. An arena hit stops the projectile. The decorative chain links have no damaging collision.
3. **Hit acceptance:** apply the same alive/invulnerable rules as other attacks. A protected roll must not become a grab. A valid hit claims one target with the ability-instance token. Do not apply damage first and then accidentally overwrite a lethal/dead state with a capture.
4. **Reel:** store a safe endpoint outside the boss capsule and within authored thrust reach. Move the player capsule toward it with swept increments; no teleport, no ordinary wall-slide, no physical spring. Keep line-of-sight and maximum separation checks. Any wall/obstruction, lost ownership, target death, boss interruption/death, reset or timeout releases both states immediately. Failure to reach the endpoint aborts the guaranteed close-range continuation.
5. **Release and stab:** recommended prototype rule is a visible short release/brace beat before the thrust, long enough for a fresh roll request to be accepted. This gives an understandable second response opportunity and avoids an opaque unavoidable damage chain while the mechanic is being tuned. A designer may later choose a true guaranteed combo after a caught hook, but that is an explicit combat-rule decision, not an animation side effect. No repeated recapture within one sequence.
6. **Miss/recovery:** retract hook, slacken chain, extinguish the offensive flare; clearly longer recovery than an ordinary swing. Restore normal player controls and camera on every terminal path.

Do not tween actor roots straight into matching animation poses. Reeling owns root displacement; pose/IK conforms to the actual swept positions. The boss cannot stab through a wall because two poses happen to be aligned. Hook contact volume and thrust blade sweep must remain inspectable separately.

## Animation and art integration

Use the existing boss skeleton to avoid a new retargeting dependency, but author a distinct undead posture and silhouette. Preserve the capsule as combat authority until a separate reviewed change justifies different scale/reach. An asymmetrical damaged cuirass, exposed neck/skull, chain-bearing arm and restrained hanging fabric can read as a different character without copying the player's outfit. Armor can begin as rigid attachments; elbows, shoulder overlap, robe/loincloth and fingers need actual deformation/pose review. Do not repeat the V13 palette-only trial and present it as finished material fidelity.

Required animation clips/pose studies are idle, locomotion/turn, hook anticipation, release/follow-through, reel brace, successful reel recovery, miss retrieval, stab anticipation/contact/recovery, interruption and death. Include player catch/reel/release reactions; merely rotating an upright idle body through the pull would look like a sliding mannequin. Hand/hook alignment and chain origin must be inspected from front, side and gameplay camera at real swing speed. Normal movement, sprint, eight-direction rolls and pause/quit still need regression review with the new costume.

## Blue-flame skulls without unnecessary cost

Start with three small skulls, each sharing one modest mesh and material, with authored orbit offsets driven by the combat clock. Pause freezes them; reset/death retires them; they never become targetable or damaging by accident. Blue flame should use a small emissive opaque/masked core and tightly bounded flame cards. Begin without shadow-casting point lights, volumetric fog or a separate expensive particle simulation per skull. Blue must remain readable against the arena; preserve a neutral/quiet silhouette around hook contact and the player's roll lane.

Chain visuals can use one pooled instanced link mesh along an analytic slack curve between wrist and hook, capped around24–32 visible links with distance-based simplification. No physics constraints or per-link tick/collision. Do not regenerate static meshes each frame. If later skull projectile attacks are approved, make them a separate mechanic with explicit launch tells, capped active count, finite lifetime, swept collision and the same invulnerability rules—not cosmetic orbit actors suddenly becoming damaging.

## Resource/performance limits

Current completed V13 trial is about2.736GB allocated under `unreal/`; the hard budget is10GB with at least24GiB free. Latest free space was only about0.6GB above the reserve, and compiler intermediates were reclaimed. The next C++ build must regenerate roughly0.9GB of intermediates and may cause further transient memory/swap growth. Do not treat the nominal unused Unreal allocation as available disk headroom. Obtain practical headroom before any build/render; retain guards and one heavy job at a time.

Provisional targets to validate, not promises: boss visible geometry roughly60–100k triangles, three skulls together below10k, chain below5k, shared materials with few sections; one or two modest shared texture sets after UV work, rather than many4K maps. Prefer a compact working source plus the last two checkpoints and selected proof, not new full archives. Start with the existing renderer/preset. Measure the actual boss costume alone, skull effects alone and the full chain sequence; baseline and candidate must use the same build,720p preset and single-instance test. Existing original58.55/V1359.03FPS short runs do not establish spare performance for a new boss. Record p95/p99 and stutters as well as mean FPS.

## Sequence and acceptance gates

1. Freeze a small original boss silhouette sheet and hook/skull readability plan; graybox one chain pose sequence without new AI or damage.
2. Prove the hook state machine with debug shapes and native tests before detailed effects. Freeze timings and hit/capture/release semantics in engine definitions.
3. Graphically verify throw, hit, miss, obstruction, release and interruption with the actual two-character poses. Fix root sliding, hands and collision/visual mismatch before ornament.
4. Author/import the boss costume and restrained blue flames. Inspect all angles and movement; keep the old boss selectable as fallback.
5. Run deterministic fixed rehearsal and human control review, then matched performance tests. Any multiplayer/replication support is outside this prototype scope.
6. Only after fundamentals, animation/aesthetics and human review pass should attack selection/adaptation be considered as a separately authorized milestone. Statistical adaptation, RL and real model adapters remain distinct and absent here.

Essential failure tests: hook miss; wall hit; player protected roll; overlapping/duplicate contacts; obstacle during pull; insufficient standoff space; boss poise break/death; target death; reset while captured; pause/resume mid-flight/reel; timeout; unusual frame rate with fixed-step catch-up; repeated requests while busy; no stale input suppression after release; no input-dependent aim/selection; shader/effect failure cannot change damage. Test hook damage and any stab damage separately so the one-hit sword flag does not accidentally swallow or duplicate either event.

## Principal risks

The largest risk is animation/contact quality, not the chain's rendering: the current pose system can express the sequence but a believable two-body catch and reel requires deliberate authoring and visual iteration. Cloth and fingers already show weaknesses in the player trial. Capture control can easily introduce unfair or stuck states unless cancellation is designed first. Skull translucency can consume fill rate despite low polygon count. Tight free space remains an operational blocker for implementation, not something this planning exercise resolves.
