# Gameplay review — 2026-11-04

## Assessment and scope

The current build is not ready for further visual enhancement. The main issue is coherence between movement, full-body animation, action acceptance, impact feedback and encounter spacing. More arena decoration or detailed character models would expose these weaknesses rather than resolve them. Mechanical verification has been given too much weight as a delivery gate; it does not establish convincing motion or enjoyable combat.

This is a review, not a gameplay revision. Inspected current C++ and existing actual engine contact sheets: `fluid-combat-review/sheet-000.jpg` (previous stiffness revision, before the latest roll orientation change) and `rolls-cardinal-review/sheet-000.jpg` (latest directional-roll revision). No new Unreal session, real-time playtest, audio review, build, full test suite or FPS measurement. Visual observations are sampled frames, not a new continuous-video assessment. All approved timing and previous evidence remain intact.

## 1. Movement and animation do not describe the same physical action — highest priority

Confirmed: `WardenEncounter.cpp:59` moves the capsule directly. Walking immediately uses up to 360 cm/s; rolling uses 720 cm/s for 20 ticks, then 360 cm/s for 10, then zero for six. The rendered roll independently rotates the entire mesh around an offset pivot (`WardenSword.cpp:255`), turns it toward travel and back, and raises it if its head would fall below a clearance threshold. The base locomotion asset is unarmed, with procedural greatsword/body corrections layered over it. Strike aim also sets actor rotation immediately (`WardenEncounter.cpp:48`).

Observed: the latest roll samples look suspended during the tumble, with weak visible push-off and landing. The older combat samples show upright, rigid-looking exchanges. Inference: disconnected travel, body rotation and foot support are a major source of the floating/sliding impression. Solving hand reach and head clearance numerically cannot establish weight transfer. Procedural animation is not inherently unsuitable; this implementation lacks a coherent full-body foundation.

Recommended direction: construct one complete grounded roll and one complete sword action, including entry and exit, with body and foot motion matched to engine-owned displacement. Use IK to correct contact and grip. Preserve the approved deliberate sword pace; do not substitute faster playback for better motion. Whole-body animation assets or authored sequences may help, but no download or engine workflow change has been performed.

## 2. Apparent readiness and actual control acceptance disagree

Confirmed: the player cut lasts 86 ticks (1.433 s) and is followed by an additional eight-tick action gap (0.133 s). Ready-state locomotion can resume during that gap, while another attack or roll cannot. The queued action expires after nine failed attempts (`WardenEncounter.cpp:275`; `WardenCombat.cpp:48`). Insufficient-stamina requests made while ready are cleared without a dedicated rejection cue.

Isolated reproduction compiled the actual `WardenCombat.cpp` against a minimal type/math shim and copied the encounter's queue condition. A dodge queued at strike age 85 expires with one gap tick remaining. Queued one tick later, after the strike ends, it survives and is accepted when the gap reaches zero. This confirms the state/queue boundary, not a physical keyboard latency measurement or an Unreal runtime test. It may be intentional finite-buffer policy, but the visual transition and buffer together are poor feedback for a committed weapon.

Evidence, source hashes and reproduction harness: `artifacts/unreal/gameplay-review-buffer-check.json`. Recommended follow-up: define and test late-recovery buffering and visible recovery consistently before changing approved attack timing. Test with human input, not only scripted requests.

## 3. Hits lack a convincing physical response

Confirmed: nonlethal `FWardenFighterState::Damage` subtracts health without affecting the current action. Contact adds a flash and sound (`WardenEncounter.cpp:89`). There is no flinch/stagger/poise state. On death the encounter stops stepping, leaving the last pose rather than playing a death action.

Observed: the fighters remain largely upright through contact, with health changes doing much of the explanatory work. Inference: the sword lacks resistance and the player lacks a readable consequence for being struck. A boss need not flinch after every hit; it needs intentional armor/poise behavior and visible impact responses. Player hurt/recovery and eventual death motion are also fundamentals. Any new stagger or impact-pause rule would require explicit engine-owned timing and fairness tests, not presentation secretly changing combat.

## 4. Close-range readability is weak

Confirmed: locked camera ignores mouse look and interpolates toward a target direction calculated from the player position (`WardenPrototype.cpp:116`). It does not explicitly frame both silhouettes. Observed in the older combat sheet: fighters overlap heavily from behind during exchanges, obscuring weapon travel and tells.

Caveat: the recorded reactive pilot approaches within roughly 140 cm and sometimes rolls toward the boss (`WardenScript.cpp`), making overlap worse. This is not proof that every human exchange has the same problem. Follow-up should preserve the approved general camera framing while testing close-range separation, wall handling and locked/unlocked transitions under real controls. Fixing the diagnostic camera alone would not fix gameplay.

## 5. The rehearsal is a sequence of attacks, not yet a strong encounter

Confirmed: the boss cycles three independent attacks, approaches at about 143 cm/s versus the player's 360 cm/s, and counts down 65 ready ticks between attacks (`WardenEncounter.cpp:218`). This is deliberately fixed rehearsal, not adaptive AI. Its current spacing and long isolated actions offer little choreography or sustained pressure.

Inference: the fight can feel like approaching a moving practice target, rather than reading and answering an opponent. This does not require adding AI now. One deterministic, readable approach–tell–dodge–punish exchange, with sensible spacing and recovery, is the next useful encounter unit. Extra attack variety should wait until that exchange works.

## 6. Performance and validation are contributing limits

The last historical runtime benchmark was 53.9 FPS mean with 29.6155 ms p95 frame interval on the shared machine. Stable 60 FPS remains unproven. Fixed-step actor/pose updates have no evident render interpolation in the reviewed path. Frame pacing can worsen perceived stiffness, but it does not explain missing hit responses or floating ground contact. The six-second, fixed-30-Hz captures are not runtime FPS or long-form usability evidence.

The existing 13/13 native and 10/10 packaged results remain valid for their tested mechanics. They do not validate natural animation, forgiving input transitions, camera readability or enjoyable play. No new full-suite result is claimed here.

## Exact recommended next milestone

Rework one greybox exchange before further art or AI: walk/stop/turn → approach → readable committed sword attack → visible hit response → recover → directional roll → grounded landing. First resolve the input/recovery contract and establish coherent body/travel motion; then evaluate impact, close-range framing and a fixed boss exchange together. Preserve the deliberate greatsword pace unless the owner changes that preference.

Acceptance must include ordinary human control: all eight roll directions locked/unlocked, late-recovery input, low stamina, misses and hits, close-range and wall encounters, plus several minutes of normal fighting. Use actual uncapped frame timing for performance and capture full exchanges separately. Keep rule/contact tests as correctness gates, not substitutes for feel review. Current game source and package were left unchanged. No downloads, training, deployment or persistent processes.
