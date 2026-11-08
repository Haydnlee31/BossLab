# BossLab: The Warden — Unreal implementation plan

Date: 2026-11-03. Status: **approved by owner; implementation in progress**. Owner requests conservative storage use. Initial measured free space 31.6 GiB; cap new workspace data at 6 GiB and preserve 24 GiB free. This replaces the proposed 50 GiB starting buffer for a measured minimal first pass.

## 1. Intended experience and definition of success

Build an original, third-person 3D Soulslike boss duel: a grounded armored challenger enters a ruined circular sanctuary and fights the Warden. The player reads physical anticipation, commits to attacks, dodges through danger, manages stamina and healing, and punishes recovery. The boss observes repeated responses and changes attack preferences without changing combat rules or reading input.

The initial deliverable is a locally playable **macOS desktop prototype**, one arena and one boss. It must look and feel like a third-person action game: orbit/lock-on camera, animated humanoids, readable weapon motion, spatial audio cues, and a coherent environment. A screenshot of unanimated primitives does not satisfy the presentation milestone. Elden Ring is a reference for deliberate combat and camera perspective, not a source of characters, assets, branding or copied environments.

Success requires a complete fight, visible and reversible statistical adaptation, credible evidence, and a repeatable build. A higher boss win rate is an experiment outcome, not a release requirement to manufacture. The initial game runs with no Aura subscription, API key, model service or network inference.

## 2. What has actually been checked

Read-only inspection found:

- Unreal **5.8.4**, changelist 58902052, at `/Users/Shared/Epic Games/UE_5.8/UE_5.8`.
- `Engine/Binaries/Mac/UnrealEditor.app` and an installed-build marker.
- `ModelContextProtocol`, `ToolsetRegistry` and `AllToolsets` plugin descriptors in that installation.
- Full Xcode **26.1.1**, build 17B100, selected at `/Applications/Xcode.app/Contents/Developer`.
- macOS **26.6.2**. Epic lists Xcode 26.1.1 as recommended for UE 5.8; local launch/compile compatibility remains to be tested.
- Approximately **17 GiB available** on the project volume. Memory query was denied by the sandbox; no hardware performance conclusion follows.
- No Unreal project in this workspace and no connected Unreal MCP tools in this session.

The editor has not been launched, plugins have not been enabled, and no connection or Unreal compilation is claimed. Existing Canvas tests/results remain historical evidence for that implementation only.

**Storage gate:** before substantial build/cache/asset work, establish a working buffer. Proposed target: at least 50 GiB free, an engineering allowance rather than an Epic minimum. If unavailable, review a smaller measured budget or an owner-selected external work volume. Do not remove personal files, relocate the engine, or change global caches automatically.

## 3. Scope and cost boundaries

Included: third-person movement; free-look and lock-on; one light attack, dodge and limited heal; health/stamina; three distinct boss moves; static/adaptive modes; title/pause/win/loss/restart; compact optional inspector; controlled demonstration; logs/recap; original arena; modest effects and sound; local packaging.

Excluded from the first release: open world, quests, inventory/equipment progression, multiple weapons/bosses, multiplayer, parry/guard/posture systems, procedural levels, AAA photorealism, cinematic production, runtime LLM integration, new RL training, Windows distribution and browser streaming.

Default additional spending is **zero**: no Aura, paid APIs, paid plugins/assets, cloud GPU hosting, or ML-weight downloads. Use engine-provided content, simple authored geometry, and a small number of appropriately licensed free 3D/animation/audio assets if needed. Record source, license, attribution and modifications before importing. Do not assume free access implies redistribution rights. Purchases or new license/account agreements are separate decisions.

## 4. Preservation and project layout

Keep `BossLab_Codex_Build_Kit/`, the working browser build, existing tests and artifacts intact. Create the proposed project at `unreal/BossLabWarden/`; use `artifacts/unreal/` for fresh evidence. Do not move the whole workspace or silently replace the old implementation.

Before migration begins, update project instructions to explicitly distinguish the frozen JavaScript reference from the Unreal game's new authority. The current AGENTS.md names the JavaScript core; this proposed migration must be reflected there after approval. Old reports/checkpoints are not Unreal validation and will not be relabeled.

Proposed compact layout:

```text
unreal/BossLabWarden/
  BossLabWarden.uproject
  Source/BossLabWarden/       # combat, observation, policies, tests
  Content/BossLab/            # maps, characters, animation, UI, attack data
  Plugins/BossLabTools/       # only if project-specific editor tools are needed
  Config/
artifacts/unreal/             # logs, reports, screenshots and captures
docs/                        # plan, decisions, status, validation, licenses
```

Exclude generated binaries, Intermediate, Saved caches and DerivedDataCache from version control. Establish a project-local checkpoint/backup method before major edits; Git initialization is a proposed implementation step, with no remote push. Preserve Unreal assets in bounded backups or LFS if available; do not blindly commit huge binaries. Asset/import sizes must respect the storage gate.

## 5. Architecture

**C++ owns rules; Blueprints and animation assets present them.** Keep the system small: actor/components for player and Warden, data assets for attack definitions, an encounter coordinator, observation filter, opponent estimator, and a shared controller interface. Avoid a full Gameplay Ability System dependency for three moves unless a concrete requirement justifies it.

- One authoritative combat implementation inside Unreal serves human play, scripted demonstrations and evaluation. Port the existing rule concepts and estimator; never run a second approximate Python simulator.
- Combat transitions use a fixed 60 Hz clock. Movement/collision use the actual Unreal world; initially use a flat arena and engine-owned kinematic movement. Explicitly bridge render delta, movement and combat ticks, and test ordering at different frame rates. Do not claim cross-platform physics determinism.
- Movement, facing and attacks remain controlled by gameplay code. Use authored in-place locomotion/montages initially; any attack displacement is bounded data-driven movement. Avoid unrestricted animation root motion silently changing ranges or timing.
- Attack definitions include cue, aim-lock, active and recovery intervals, turn-rate cap, geometry, damage, cooldown, stamina/compatibility and permitted movement. Animation curves/notifies provide synchronization and effects, not independent authority to deal damage.
- Use a documented attack-volume representation that agrees with weapon motion. Show debug volumes during QA; test active-only hits, per-instance deduplication, locked orientation and recovery. No fixed invisible attack sector unrelated to the shown swing.
- Scope the first vertical slice to a grounded duel without jumping or uneven combat terrain. Vertical camera/animation/geometry are genuinely 3D; avoid pretending the old 2D renderer has simply been replaced without gameplay integration work.
- Pause, reset, simultaneous damage and death ordering are explicit. Input buffering, if included, gets a bounded window and cannot cancel committed actions; queued inputs never enter the opponent model.

**Editor tooling is separate from the runtime boss.** MCP can inspect privileged state for development/testing, but boss policies receive only filtered permitted observations. The packaged game works with the editor/MCP service closed.

## 6. MCP approach and proposed narrow tools

Use Epic's installed MCP server first, started manually on loopback. Discover the actual tools exposed by this installed version; do not assume every documented tool is available. Keep engine calls sequential, return real results/errors, and verify saved changes. Preserve existing client settings. Any configuration outside the project follows actual permission requirements.

Connection proof: report engine/project identity, inspect actors, create a disposable actor, modify/read its transform, save/reload, run an automation check and inspect its result. Clean up only the explicitly disposable test actor. Stop/restart the connection once to verify recovery. No auto-start agent, watchdog or scheduled process.

Only add a `BossLabTools` editor plugin if native tools lack a required operation. Candidate **proposed, not existing** operations:

| Tool | Purpose |
|---|---|
| `bosslab_get_encounter_state` | Return typed health/stamina/phase/attack IDs and observation diagnostics |
| `bosslab_reset_encounter` | Reset a named test encounter with new generation ID |
| `bosslab_run_scenario` | Start a bounded scripted run; return a job ID rather than block editor ticks |
| `bosslab_get_scenario_result` | Poll completion and retrieve actual report/artifact paths |
| `bosslab_capture_evidence` | Capture a frame and associated simulation tick/state |
| `bosslab_validate_combat_data` | Check timing, geometry, costs and animation/data alignment |

Retain ordinary code editing/build tools for C++ changes. Do not construct a universal arbitrary-Blueprint-generation platform. If Epic's experimental bridge is unusable after a reproducible diagnostic attempt, document the missing operation and consider a minimal local Remote Control/Python adapter. Avoid maintaining two bridges concurrently or rebuilding Aura.

## 7. Ordered milestones and acceptance gates

All milestones below are **approved for implementation**. Each ends with a saved runnable state, recorded checks and an updated status. Technical gates must pass before dependent work; designated visual review points invite owner feedback before heavy polish.

| Milestone | Work and deliverable | Acceptance gate |
|---|---|---|
| U0 — Environment and connection | Confirm storage budget; launch UE; create minimal C++ project; build/reopen; prove native MCP; document start/stop/config | Small project compiles and runs, read/write/read-back check succeeds, real test output returns, original build preserved |
| U1 — Third-person movement and camera | Third-person template/mannequin; collision; camera-relative movement; orbit, lock-on, target release, wall collision; minimal greybox arena | Controllable character at normal speed, stable lock-on at close range, no wall clipping or lost target; first playable 3D capture for owner review |
| U2 — One convincing exchange | Player light strike, stamina, dodge/i-frames, healing; one boss attack with a real animation, readable anticipation and punishable miss; health/death/reset | Complete attack/dodge/punish sequence feels deliberate; hit geometry matches weapon motion; costs/commitment/death tests pass; short clip exposes timing and camera issues |
| U3 — Complete static fight | Three boss moves, approach/reposition/wait, cooldowns, competent history-free selection; complete UI and restart; calibrate difficulty using development scenarios | Full win and loss possible without cheats; each move has distinct counterplay; attacks cannot retarget/cancel illegally; owner can play a complete fight |
| U4 — Visual and audio identity | Selected character rigs/animations, original armor/material treatment, sanctuary dressing, lighting, fog, trails, impact/footstep/heal audio; accessibility settings | A coherent 3D encounter rather than a mannequin test map; readable silhouettes/telegraphs; no asset-license uncertainty; capture on actual Mac; visual review before further scope |
| U5 — Fair statistical adaptation | Filtered delayed observations, event opportunities, smoothed estimates/context backoff, adaptive utilities and truthful inspector | Real behavior changes evidence and action distribution; strategy switch reduces previous expectation; hidden-input, delay and combat-invariance tests pass |
| U6 — Demonstration and evaluation | Labeled scripts, matched scenario runs, held-out seeds, event/recap viewer, logging, recording layout; human testing and performance pass | Reproducible real JSON/CSV, honest favorable/unfavorable findings, captures show resets/controller labels; no fabricated confidence, learning curves or gameplay evidence |
| U7 — Package and handoff | Local macOS Development package, launch outside editor, repeat smoke/fairness checks, docs and final claim audit | Packaged fight works with MCP closed; controls/run/test instructions verified; real footage/screenshots and limitations delivered; owned services stopped |

U4 assets can be scoped/researched once U1 establishes camera/framing, but bulk importing and final dressing wait for the U2/U3 combat gates. A usable animation is required already in U2; final fidelity is not deferred until after AI work.

## 8. Combat and presentation targets

Initial player kit: movement, light attack, directional dodge, three committed heals, health/stamina. Defaults: WASD movement, mouse camera, left-click/J attack, Space dodge, E heal, middle-click/Q lock-on, Escape pause, Tab inspector. Confirm conflicts and show the actual bindings; controls remain provisional until U1/U2 review.

Initial boss repertoire: quick cut (close pressure), delayed overhead (punish premature dodge), advancing thrust (pressure retreat, vulnerable to lateral evasion). Start from the old timing data only as a reference; tune against real 3D animation and camera readability. Once a rules version is evaluated, freeze its constants across controller comparisons.

Camera/feel checklist: adjustable sensitivity, sensible pitch limits, no wall penetration, target remains readable during close circling/dodging, no mandatory camera shake, no forced slow motion. Gameplay-critical attacks must stay legible without relying entirely on warning overlays. Provide reduced motion, mute/volume and clear UI contrast.

Art direction: original charcoal-stone sanctuary, amber embers and warm boss cues, restrained contrasting player accent. Grounded stylized realism, not a promise of AAA fidelity. Use a small compatible skeleton/animation set early; retargeting and animation quality are explicit risks. No giant environment pack or hundreds of unrelated assets.

Performance **target, not measured claim**: 60 FPS at 1080p on the actual machine using a sensible scalability preset. Record mean and p95 frame times in a bounded, repeatable encounter capture, editor and packaged separately. Reduce expensive lighting/effects first if needed; if the target cannot be met, report the measured result and proposed trade-off. Do not change combat timing or conceal dropped simulation time to improve a reported FPS number.

## 9. Observation, adaptation and evaluation contract

Preserve the fundamental boundary: boss inputs may include its own state, delayed visible transforms/animations, arena geometry and permitted past events. Exclude raw input, buffered actions, script classes/seeds, future switch schedules, future trajectory and hidden player resources. Initial event/state delay is 12 combat ticks; turn/aim logic must use the same filtered view, not a direct player pointer.

One response opportunity per authored attack cue. Match by encounter and attack-instance IDs. Record first relevant dodge, early/late/no response, direction, family/spacing and observed result; censor incomplete/interrupted/unobservable windows. Short and long decay operate per valid exchange. Use priors, finite normalized estimates, effective count and insufficient-evidence labels. Adaptation affects bounded action utility only, with normal legality and cooldown enforcement.

The first policy pair is static vs statistical adaptive utility with identical repertoire and rules. This is **not RL**. Neural/LLM controls remain unavailable unless separately implemented and exercised. The old PPO checkpoint is not valid evidence of an Unreal-trained policy.

Testing layers:

1. C++ core/automation tests: state timing, costs, i-frames, recovery, hit deduplication, cooldowns, aim lock, commitment, delayed delivery, evidence counts/censorship, priors and hidden-input/history counterfactuals.
2. Real Unreal functional encounters: geometry/animation alignment, movement and camera, heal/death ordering, reset/stale actions, complete victories/defeats, scripted behavior-driven adaptation and reversal. Test several render-frame rates without changing the 60 Hz combat contract.
3. Matched evaluation: early, late, lateral/retreat and switching scripts with small timing/spacing variation. Predeclare development and held-out seeds/configurations in a manifest before evaluation; run a modest initial 8 paired seeds per scenario (64 encounters across two controllers), bounded duration. Report termination and timeout separately. Do not tune scripts after seeing held-out results to manufacture improvement.
4. Human review: aim for at least three short owner sessions covering camera, readability and difficulty. Agent scripted verification cannot certify human enjoyment. If unavailable, mark that gap explicitly.

Metrics: encounter outcome/duration, damage both ways, move distribution, observed response counts/estimates, contextual sample counts, missed/censored windows, decision timings/fallbacks, rules/controller/engine versions, seeds and actual test failures. Deaths are real. A longer demonstration may visibly reset rounds and retain evidence only with explicit UI/log disclosure and an independent switch schedule. Save config/events and periodic snapshots; do not call this exact replay until replay fidelity is tested.

## 10. Risks, fallback decisions and spending control

| Risk | Planned response |
|---|---|
| Insufficient disk headroom | Resolve storage before heavy builds; small asset subset and bounded caches; no automatic deletion |
| Experimental MCP tool missing/unreliable | Inspect installed tools/logs; use native workflow first; add only a required narrow tool |
| Compiler/editor incompatibility | Prove minimal build early; pin working versions; do not blindly upgrade Xcode or engine |
| Poor animations or retargeting | Test one combat exchange with selected skeleton before bulk import/polish |
| Camera feels wrong despite working rules | Owner play checkpoint at U1/U2; fix camera before expanding mechanics |
| Excessive GPU cost on Mac | Measure and reduce lighting/shadow/effect expense; avoid making Nanite/Lumen mandatory |
| Port loses fairness or diverges from evaluation | All game/evaluation calls invoke Unreal authority; test observation boundaries and invariant data |
| Adaptive policy is not stronger | Publish the finding; demonstrate behavioral response, not an unsupported superiority claim |
| Training distracts from playable game | Keep RL/model work outside U0–U7; preserve existing experiments as historical reference |

Do not buy tools, create cloud resources, expose a public editor endpoint, or add persistent background services. An owner review of this plan does not authorize unrelated machine configuration changes or override actual tool permissions.

## 11. Delivery and later research

First delivery: Unreal source/assets with license manifest, local Mac build, exact verified commands, current controls, inspector/demo, real reports and gameplay captures, and updated status/claims/validation. Packaging is local; signing/notarization for public distribution and Windows builds are separate validated tasks.

Sites remains a later **portfolio/showcase page** for footage, architecture and results/download instructions. Publishing requires its own request; an Unreal binary is not a static browser game. Pixel Streaming is deferred because it needs separately running GPU infrastructure and changes latency/cost requirements.

After the packaged arena and evaluations are stable, optionally propose a new bounded PPO run using this same Unreal implementation. Redesign/revalidate observation/action contracts as needed, train fresh weights, evaluate against frozen references and keep training separate from gameplay. Laya/LLM experiments remain separately scoped and disconnected by default.

## 12. Review decision and first approved action

Review these proposed defaults: **UE 5.8.4; Mac desktop first; one complete original 3D arena; no Aura or paid dependencies; native MCP before custom tools; C++ authority with Blueprint presentation; preserve the browser reference; statistical adaptation before new RL; no deployment.**

Once approved, begin U0 only after the storage budget is workable. The first implementation deliverable is a compiled minimal project with a demonstrated read/write/test MCP connection, not another planning document. Continue through technical gates with durable checkpoints; take owner visual feedback at the designated points before expensive polish.

References checked during planning:

- [Epic: Unreal MCP and custom toolsets](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- [Epic: macOS development requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/macos-development-requirements-for-unreal-engine)
- [Epic: Remote Control HTTP API](https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-http-reference-for-unreal-engine)
- [Epic: Pixel Streaming architecture](https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-pixel-streaming-in-unreal-engine)
