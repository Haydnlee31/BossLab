# BossLab — Autonomous Build Brief

## Mission

Act as the implementation engineer for **BossLab: The Warden**, an original, single-arena Soulslike duel. Build and validate the project in the current workspace. This is an implementation assignment, not a request for another proposal.

The owner is building a portfolio project to demonstrate on LinkedIn and discuss with employers. They are interested in reinforcement learning, opponent modeling, Laya/Jev-style fast decision models, and an optional LLM strategist. Their immediate priority is a playable, visually compelling, technically honest first version.

The core experience is:

> The player repeats a combat habit. The boss gathers observable evidence and changes its attack selection. The player changes their habit. The boss's old expectations become less useful and its estimates adjust.

The boss must not read raw player input, change its hitboxes, eliminate recovery, or secretly raise its stats. The player must be able to outsmart it.

Build an original game inspired by deliberate positioning, attack commitment, and readable counterplay. Do not reproduce Dark Souls characters, maps, branding, music, animations, or extracted assets.

**A polished playable fight with genuine, disclosed statistical adaptation is more valuable than a collection of unfinished model integrations.** That first controller is a baseline, not a substitute for the longer-term RL/model research. Implement the baseline, instrumentation, and replaceable interfaces now; attempt genuine training and model integration only after the game works.

---

## 1. Operating boundaries and execution discipline

### Workspace and permissions

1. Read existing project instructions, including applicable `AGENTS.md` files, before editing. Inspect the current repository, branch, and uncommitted changes. Preserve unrelated user work. Do not reset, clean, force-checkout, force-push, or delete unrelated files.
2. Work only in the selected project/worktree and explicitly permitted project-local dependency/cache directories. Inspect normal executable locations as needed, but do not browse unrelated personal projects, email, credentials, or cloud accounts.
3. Respect the actual sandbox, approval policy, network permissions, and available tools. This brief does not authorize bypassing a denied action. If an optional dependency is blocked, record the blocker and continue through a permitted alternative.
4. Do not publish, deploy publicly, push to a remote, create paid resources, or call paid model APIs. Do not search for API keys. An existing key is not permission to spend money. Do not modify machine-wide security settings, sleep settings, shell startup files, or global tool configurations.
5. Prefer project-local installations and pinned dependencies. No `sudo`, broad system installations, security/quarantine bypasses, or unexplained download-and-execute scripts. Use official sources for permitted downloads and record versions.
6. No multi-gigabyte model downloads in this run. Use already available authorized local models only, or leave the model adapter unavailable with a precise explanation.
7. Run finite, bounded tests and training jobs. Do not leave unbounded training, agent relaunch loops, scheduled jobs, or public listeners behind. Bind any model/control service to loopback by default. Identify commands to start and stop project services.
8. Make reversible implementation decisions rather than asking about routine ambiguity. Stop for genuinely required approval, destructive operations, or a blocking conflict that cannot be resolved safely. Continue independent work when an optional task is blocked.

### Durable working state

Create or update the following without overwriting existing project instructions:

- `docs/EXECPLAN.md`: ordered milestones, acceptance criteria, checkboxes, dependencies, and scope cuts.
- `docs/STATUS.md`: current state, implemented features, validation evidence, exact restart commands, blockers, and next action.
- `docs/DECISIONS.md`: short consequential decisions and rejected alternatives.
- `docs/CLAIMS.md`: what this build demonstrably does, what is rule-based, what is trained, and what is not connected.

Add a concise project-scoped `AGENTS.md` only where appropriate, referencing these files and the verified validation commands. Do not replace a user's existing instructions with a competing generic guide.

After each milestone: run its checks, fix failures, update status, and proceed. Do not stop after planning, scaffolding, writing TODOs, or one successful test. Do not keep adding architecture after a working simpler component would meet the requirement.

If limits prevent completion, leave a cleanly runnable partial result, save exact state, and report what remains. Never imply an interrupted process is still working. Do not defeat platform limits or manufacture persistence.

If delegation is available, use it only for bounded independent tasks after interfaces are stable. Keep one integration owner. Parallel work must not compete to redesign combat or write the same files.

---

## 2. Priority contract

### P0 — Must be working before model experiments

- One original, coherent arena; one player; one boss.
- Responsive movement, dash/dodge, melee attack, limited healing, health, win/loss, and fast restart.
- Three distinct, fully authored boss attacks with readable preparation, aiming commitment, active hit windows, cooldowns, and punishable recovery.
- A fixed/history-free baseline and a statistical adaptive utility controller.
- A permitted-observation boundary; the opponent model uses only observed combat events.
- Online habit estimates that change from real events, not elapsed time or a scripted story flag.
- Inspector showing actual observations, sufficient/insufficient evidence, estimates, active controller, and selected action.
- Meaningful automated combat, adaptation, and fairness tests.
- A verified local launch procedure. The core game requires no Python server, API key, or large model.

### P1 — Complete the showcase and evidence

- Human-play mode and a clearly labeled scripted-player demonstration mode.
- Early-dodge, late-dodge, and strategy-switch evaluation scenarios.
- Matched baseline/adaptive evaluations with real JSON/CSV results.
- A clean recording mode, coherent visual effects, usable menus, and encounter recap.
- Event logging, reproducible scenario configuration, and a replay or event viewer.
- Actual screenshots or recording when supported; no fabricated proof images.

### P2 — Only after P0/P1 remain stable

- Headless RL environment backed by the same combat implementation.
- A small masked-action PPO baseline, a bounded training smoke run, and checkpoint evaluation.
- A Laya-compatible decision-service contract; connect a real local model only if it is available and its interface is verified.
- A bounded strategist interface, disabled by default; a local rule-based planner is labeled as such.

### P3 — Explicitly deferred

Full 3D RPG, multiple levels/bosses, multiplayer, arbitrary generated attacks, generated animation pipelines, in-fight large-model weight updates, large sweeps, cloud model services, commercial game mods, authentication, accounts, payments, and a general game-agent SDK.

Do not sacrifice the playable fight to deliver P2/P3 scaffolding.

---

## 3. Stack and preflight

Inspect the environment first. Record OS/architecture, relevant installed tool versions, repository status, available rendering/headless tools, and Python/ML availability without collecting unrelated machine information.

**Default for a new repository:** Godot 4.x, GDScript, original procedural/vector 2D visuals, and a later optional Python training/model service. Use the installed compatible stable version and verify APIs against that version's official documentation. Do not choose C# for the new default build.

If an existing usable implementation already chooses another engine, preserve it unless there is a concrete blocker.

If Godot cannot be installed or executed within permissions, make one documented fallback decision early: use an available TypeScript/Canvas or Phaser toolchain with an authoritative fixed-step simulation that also runs headlessly. Do not build both engines or spend the session fighting installation. A fallback must preserve behavior, controller boundaries, tests, and honest reporting. Document the architectural deviation prominently.

Favor a project-local command wrapper such as `./scripts/bosslab` with `doctor`, `play`, `test`, `demo`, and `evaluate` subcommands, or equivalent idiomatic commands. Only document commands that exist and were exercised; distinguish unavailable commands from working ones.

For Godot, support discovery via an explicit `GODOT_BIN` override and ordinary executable lookup. Missing prerequisites must produce an actionable error rather than a silent failure. Do not require the user to repair scripts or guess absolute paths.

Keep one authoritative combat core. Prefer explicit fixed-tick kinematic geometry and data-driven actions over uncontrolled rigid-body behavior. Rendering mirrors core state. Headless testing/training invokes that same core. Do not recreate a slightly different simulator in Python for convenience.

Proposed structure, adjusted to existing conventions:

```text
bosslab/
  game/
    project.godot
    core/                 # fixed-tick combat, geometry, state, action contracts
    presentation/         # rendered actors, arena, UI, effects, audio
    ai/                   # observation filter, habits, baseline controllers
    bridge/               # optional asynchronous policy service
    headless/             # test and evaluation entrypoints
    configs/              # attacks, balance, scenarios
  ai/                     # optional Python trainer/model adapters
  tests/
  scripts/
  docs/
  artifacts/              # actual small test/evaluation/demo outputs
```

Avoid overengineering the structure: use as few modules as necessary while preserving the hard boundaries below.

---

## 4. Visual identity and game feel

Working title: **BossLab: The Warden**.

Presentation: a top-down dark-fantasy duel in a ruined circular sanctuary. Original stylized silhouettes, charcoal stone, warm amber warning cues, and a contrasting player accent. The boss has a readable armored body, shoulders, a visible weapon, and a distinct facing direction. The player is a smaller cloaked fighter.

Create the appearance with procedural geometry, gradients, sprites/SVGs authored for this project, shadows, and restrained particles. Primitive shapes are acceptable construction tools, but the final scene should not resemble two debug circles on a flat grid. No web-dashboard aesthetic, wall of diagnostic cards, or excessive neon UI.

Keep the arena spacious and collision geometry readable. Decorative pillars or rubble should be outside the playable area unless their collision is clearly indicated and tested.

Add a compact title screen, control hints, pause, death/victory overlay, and immediate restart. Keep most of the screen for the fight. Include a boss name/health bar and a player health/stamina display. The inspector is optional and collapsible.

Effects must support mechanics: weapon anticipation, visible wind-up, slash trail, contact flash, recovery pose, dash trail, modest impact particles, and optional small camera shake. Offer reduced-motion/shake-off and mute controls. Prefer procedural sound only if it can be made and tested without derailing the build; otherwise make a coherent silent build and disclose it.

Do not use presentation time manipulation to falsify policy latency. Any hit-stop or slow-motion effect must have explicit simulation semantics, apply consistently, and remain disabled or standardized in evaluation.

Target a 16:9 composition legible at 1280x720 and 1920x1080. Do not report frame-rate claims without measurement on the actual runtime.

---

## 5. Controls and combat mechanics

Suggested defaults; adapt carefully to the engine/input environment and show actual bindings:

- WASD: movement.
- Mouse: facing/aim; a usable keyboard-only fallback is desirable.
- Left mouse or J: light attack.
- Space: dodge in movement direction, otherwise a documented fallback direction.
- E: limited heal with a visible, committed animation.
- Escape: pause.
- R: restart after confirmation where appropriate; no accidental mid-fight data loss.
- Tab: inspector toggle.
- F1 or menu control: recording mode.

The player needs visible attack commitment and recovery, a finite dodge cost, stamina regeneration, a finite invulnerability window separate from dash movement duration, and a limited heal supply. Heavy attack is optional after the core light-attack fight feels coherent.

Prevent actions during incompatible states. Do not let attacking, dodging, or healing cancel each other arbitrarily. Clamp health/stamina; define simultaneous-hit ordering; keep a dead actor from issuing or receiving nonsensical subsequent actions.

Use a fixed 60-tick simulation initially. Choose readable initial timing values and tune with actual play/simulation. These are provisional design values, not claims about a commercial game:

| Boss move | Wind-up | Active | Recovery | Purpose |
|---|---:|---:|---:|---|
| Quick cut | 22 ticks | 5 ticks | 28 ticks | Close-range pressure |
| Delayed overhead | 50 ticks | 6 ticks | 40 ticks | Challenge premature dodges |
| Advancing thrust | 32 ticks | 7 ticks | 36 ticks | Pressure retreat, vulnerable to lateral movement |

Define each attack in data: ID, wind-up/active/recovery, aiming-lock point, turn-rate limit before lock, geometry, damage, cooldown, movement, cancel rules, and legal follow-ups. A wide sweep is optional after the first three attacks work.

The state machine is explicit:

`READY -> WINDUP -> AIM_LOCKED -> ACTIVE -> RECOVERY -> READY`

Some phases may overlap in implementation, but aiming and damage timing must be testable. An attack's active hitbox must agree with its displayed weapon path. Deduplicate damage per target per attack instance unless an explicitly authored multi-hit move says otherwise.

After aiming locks, do not rotate the hitbox toward a newly dodging player. After an attack begins, do not replace it with a different attack because a new model response arrived. Include enough recovery and counterplay for a careful player to punish a miss.

Non-attack choices should include approach, reposition, and wait. Bound repeated waiting and make approach physically plausible; do not teleport to solve pathing. Cooldowns and action-compatibility belong to the engine, not the model.

Validate that the quick cut and delayed overhead actually create different timing problems. Do not compensate for an uninteresting move set by artificially changing damage during play.

---

## 6. Observation boundary and fairness

Separate privileged world state from the policy input. Pass an immutable snapshot or serialized DTO into the controller; never hand it a reference to the entire world or player object.

Permitted information: the boss's own state; visible positions, movement, attack/dodge/heal animations; observable outcomes; past permitted events; elapsed encounter time; and authored arena geometry.

Excluded information: raw key/button events, queued future actions, the simulated player's behavior-class ID, its random seed, hidden strategy-switch schedule, future trajectory, undisclosed resources, or evaluation scenario labels. Avoid tracking labels that accidentally reveal an early/late-dodge player class.

Introduce a configurable observation delay, initially 12 ticks, for newly observable player events/state. Train and evaluate using the same configured boundary. This is a proposed gameplay rule, not a benchmark claim. Keep a clear distinction between delayed tactical observation and current engine validation of action legality.

The boss can anticipate from past observations. It cannot use a new event before its permitted arrival tick. A statistical guess that happens to be correct is not access to future state; keep the evidence trace that distinguishes these cases.

Fairness constraints enforced in engine code:

- Fixed versioned damage, hitboxes, cooldowns, invulnerability rules, and recovery.
- No mid-attack retargeting after aim lock.
- No arbitrary cancel or infinite untelegraphed combination.
- No hidden health scaling or rubber-banding based on player success.
- No model-controlled mutation of attack definitions.
- No expired/stale action applied to a new encounter or decision window.

The same constraints apply to baseline, adaptive, and learned controllers.

---

## 7. Event-based opponent model

Implement the first opponent model locally without an LLM. Update it from observed exchanges, not every animation frame.

Define a response opportunity from a visible boss attack cue. Classify the first relevant observed response in a finite window. Record boss attack family, spacing, response timing, dodge direction relative to the boss, and the outcome. One dodge produces one response sample, not twenty samples because it lasted twenty ticks.

Track at least:

- Early/late/no-dodge response in comparable attack contexts.
- Inward/outward/lateral dodge preference when there is sufficient evidence.
- Recent versus longer-window tendencies.
- Effective sample count and an insufficient-evidence state.

Optional later: immediate post-swing aggression, retreat tendency, and healing context.

Do not classify an occluded, terminated, or incomplete response window as a definite no-dodge. Distinguish censored/unknown from observed inaction. Match samples to attack instances so delayed observation arrival cannot misattribute a response.

Use smoothed decayed counts, for example:

`counts[k] = decay * counts[k] + indicator(response == k)`

`p[k] = (counts[k] + prior[k]) / sum(counts + prior)`

Apply decay with clearly documented units; do not decay once per rendered frame while updating once per exchange. Maintain short/long summaries or a bounded recent window to adapt after a strategy switch. Back off from sparse attack-specific contexts to broader estimates rather than treating one example as certainty.

Initial tuning target: after roughly 6-10 valid comparable exchanges, a repeated habit should influence decisions visibly; the influence should diminish when contrary evidence accumulates. This is a playtesting target, not a hardcoded story trigger. Never force the controller to change after a counter regardless of observations.

Inspector wording must reflect uncertainty: “Early dodge tendency; 8 comparable observations” or “Insufficient evidence.” Do not invent confidence percentages, psychological labels, or claims about future actions.

---

## 8. Controller interface and genuine adaptive baseline

Use a single interface with explicit inputs:

`decide(permitted_observation, opponent_summary, bounded_plan, legal_actions, policy_rng) -> decision`

The result identifies the selected action and controller version; include actual utility scores or policy probabilities when available. A reason-code/evidence-ID explanation may describe the rule that fired. Do not generate fictional private thoughts.

Implement two working controllers first:

### Static / history-free baseline

A competent fixed or utility-based policy using current permitted spacing and legal actions, but no learned habit summary. It must move and fight properly; do not intentionally cripple it to exaggerate improvement.

### Statistical adaptive utility policy

The same action repertoire and combat rules, with utilities conditioned on smoothed opponent estimates. For example, early dodges may increase the relative utility of delayed attacks in suitable contexts, while later dodges reduce that preference. Range and cooldown still matter.

Use bounded utility changes and seeded stochastic selection or another varied rule, rather than always choosing one move. Record the actual utility contributions. A cap intended to avoid unreadable repetition must be disclosed and applied consistently to the relevant comparisons; it cannot secretly choose the winning move.

This is **rule-based attack selection conditioned on online statistical opponent modeling**. Label it exactly that in the UI, report, and demo. It is not RL, Laya, or an LLM.

History-counterfactual tests must verify that relevant histories can change the decision distribution for the same current observation. End-to-end evaluations then test whether this change helps; distribution change alone is not proof of better gameplay.

Keep response estimates and attack outcome statistics contextual. Do not infer a universal playstyle from the boss's own highly selective attack history.

---

## 9. Demonstration modes and evidence

Implement:

1. **Play:** human player versus selected available boss controller.
2. **Watch a controlled demonstration:** an explicitly labeled scripted player uses early dodges, then switches to later timing, while the boss observes only normal gameplay.
3. **Compare:** run fixed/history-free and adaptive policies against matched reactive scripted-player configurations and initial seeds. Side-by-side playback is optional; paired results and sequential playback are sufficient.

A demonstration's player behavior is scripted, not its outcomes. The boss must not receive stage names, the script type, the next switch tick, or a direct “change attack now” instruction.

Choose a documented strategy-switch schedule independent of boss success, such as a simulation-time threshold. Labels displayed by the presentation layer may show the scenario stage, but those labels must not enter policy inputs.

Normal play retains real health, damage, and death. A long-running practice scenario may use explicit round resets or a clearly marked training/sandbox mode. Never conceal invulnerability or silently reset health to keep a video going. Record resets and mode changes.

Evaluation should include early-dodge, late-dodge, mixed/strategy-switch, and a small amount of parameter variation. Keep validation and held-out evaluation seeds distinct. Tune on development scenarios; do not adjust hidden test scripts to manufacture success.

Generate actual JSON/CSV for completed encounters, outcomes, damage exchange, attacks selected, opponent estimates, effective sample counts, and latency/fallback metrics. Include engine/controller/config versions and seeds. Report failures as findings.

For the first build, real results from a modest seed set are acceptable. Do not imply statistical certainty or broad human generalization from a handful of scripted runs. A win rate without encounter counts and scenario details is incomplete.

Record append-only events with tick, encounter ID, attack instance, observation availability, decision input version, selected/accepted action, controller identity, outcome, and plan/model version where applicable. Exclude secrets.

Provide an event/recap viewer. Exact action replay is optional unless validated. Do not claim seeds alone guarantee cross-platform physics replay. Save initial configuration and periodic state snapshots where feasible; document replay fidelity and limitations.

---

## 10. Automated checks — required, not aspirational

Use the simplest functioning test runner for the selected stack. For Godot, a headless GDScript test entrypoint is acceptable if an external test framework is unavailable. A failing assertion must produce a failing process exit status.

At minimum test:

1. Game/core loads; scene references and scripts parse; an encounter can start, end, restart, and end again.
2. Attack phase durations, cooldowns, and legal action transitions.
3. No damage during wind-up/recovery; no duplicate hit per attack instance.
4. Invulnerability applies only during the configured portion of a dodge.
5. Aim lock prevents late retargeting; attack commitment prevents switching moves midway.
6. Damage, hitboxes, and recovery remain invariant across controller modes and encounter history.
7. Delayed observations cannot expose an event before its delivery tick.
8. Hidden-input invariance: with identical permitted observations, history, policy state, and RNG, changing hidden queued player inputs/class IDs does not change the policy result/distribution.
9. One observed response yields one sample; censored windows do not masquerade as no-dodge evidence.
10. Synthetic early-dodge event sequences change estimates; later contradictory sequences reduce that estimate. These are estimator tests, not fabricated gameplay demonstrations.
11. Cold-start/sparse evidence remains conservative; estimates are finite and normalized.
12. Relevant history changes an action distribution while an unrelated hidden scenario label does not.
13. Dead/stunned/restarted boss rejects invalid or stale proposed actions.
14. At least one seeded headless encounter produces a parseable report with consistent metrics.
15. Inspector values agree with emitted events and controller mode, including missing-model status.

Add an end-to-end test using the real simulation, not only hand-constructed feature vectors. Verify the demonstrated attack-selection changes arise from real observed behavior.

Use available visual tools to inspect the running game at representative sizes. Capture genuine rendered screenshots if possible. Test controls, death/restart, pause, UI overflow, and recording mode. Headless tests do not establish graphical usability. If GUI/recording tools are unavailable, disclose exactly what was and was not visually checked; do not fabricate a screenshot or claim manual playtesting.

Keep test expectations meaningful. Do not delete failing fairness tests or loosen them simply to make the build green. Repair the implementation or document a genuine design revision.

---

## 11. Optional RL milestone: small, real, and bounded

Attempt only after P0 and P1 are healthy. Protect the working game.

Use the same headless combat core behind a reset/step adapter. Do not use an approximate second simulator. Distinguish game termination from trainer-imposed truncation. Fixed-duration control steps are the initial default; return “continue” during committed actions where appropriate.

Train a small CPU-friendly masked-action PPO policy first. Use a maintained compatible implementation when practical and verify its capabilities. Do not assume a recurrent implementation and invalid-action masking can be combined without integration work.

The actor receives only permitted numeric observations and opponent estimates. A simpler actor without history is a useful ablation. Do not leak opponent class IDs or hidden switch timing. Initially use a frozen population of parameterized scripted players, not simultaneous learning of all participants.

Reward should use actual damage and win/loss outcomes with documented weights. Do not reward issuing attacks, confidence, decorative messages, or indefinite survival. Bound each encounter and inspect for stalling or reward farming. Keep actual win/damage metrics separate from shaped reward.

PPO updates require differentiable action log-probabilities from the current rollout policy. Do not call a JSON model API and call it gradient training. Do not reuse arbitrary historic logs as on-policy PPO data. Keep evaluation separate from updates.

First prove one small rollout/update/checkpoint/reload cycle. Verify finite losses and nonzero parameter change. Save config, seed, training steps, environment version, and optimizer/checkpoint metadata. Parameter change proves an update occurred, not that the policy improved.

Run one bounded smoke experiment: initial cap of 25,000 transitions or 20 minutes of training wall time, whichever occurs first, with no more than two environment processes by default. This is a resource limit, not an expectation of convergence. If tool/runtime limits are smaller, use them. Do not spend the rest of the build on a hyperparameter sweep.

Evaluate the actual saved checkpoint against an untrained reference and the baseline on a small held-out set. Report results honestly, including poor performance. A checkpoint is selectable in the game only when loading and inference have been exercised. Otherwise keep the learned-controller control disabled with a precise status.

A successful RL integration is a later milestone, not a requirement to falsely relabel the adaptive baseline. If dependencies or integration are blocked, report that training did not run and preserve a working game with documented extension points.

---

## 12. Optional local model and strategist integration

Keep the model adapter separate from the mandatory game loop. Never turn a missing model into a silent call to the utility controller while labeling the result Laya/Jev/CLM.

Define a versioned local decision request containing:

- Encounter and decision-window IDs.
- Observation tick and permitted compact state.
- Opponent estimates with sample counts.
- Bounded validated plan, if any.
- Legal candidate action IDs and policy/checkpoint identity.
- A request deadline.

Response: matching IDs, candidate scores/probabilities where supported, selected action, model/checkpoint identity, and actual timing.

Use one in-flight request per boss; discard stale responses. Do not queue obsolete attacks. Continue rendering and already committed actions during inference. Use a disclosed bounded wait/fallback if no valid response arrives. Log policy proposal, engine acceptance/rejection, fallback reason, and actual executing controller separately.

Validate malformed JSON, NaNs, unknown actions, out-of-range scores, timeout, disconnect, encounter reset, and model-unavailable cases with an explicitly labeled test double. Test doubles validate the interface; they do not prove a real model works.

The default game must remain fully offline with optional network/model features disabled.

If a local Laya runtime/checkpoint is present and permitted, inspect its real documentation and adapter shape. Use compact structured/text state and a single mutually exclusive action choice. Record the upstream revision, weights identity, and workload timing. Do not assume base checkpoint competence or claim to have trained it without an executed training job.

For the LLM strategist, define a small plan schema with allowed tactic IDs, evidence IDs, and expiration. It may influence strategy but never mutate combat constants or authorize new attacks. Validate evidence references. Apply plans at a neutral boundary, not midway through a committed attack.

No paid API use in this run. A deterministic planner is allowed but must be called a deterministic planner. Missing LLM inference should read “Not connected,” not a convincing fabricated strategic transcript. LLM/model wiring is lower priority than working gameplay and evidence.

---

## 13. Honest inspector and presentation

The inspector should answer:

- Which controller is actually running?
- What can the boss currently observe?
- What habit evidence has accumulated, and in which attack contexts?
- What are the current estimates and sample counts?
- Which action was proposed and accepted?
- Was a fallback used?
- Are policy weights frozen during this encounter?

Use labels such as:

- `Static baseline`
- `Adaptive utility — statistical opponent model`
- `PPO policy — checkpoint <id>` only when loaded and exercised
- `Laya — checkpoint <id>` only for actual verified inference
- `Strategist: disabled / deterministic / actual model ID`

An action-selection probability is not a hit probability. A rendered explanation is not hidden chain-of-thought. UI values must be derived from real state. Cosmetic boss dialogue must be marked as authored flavor rather than evidence of reasoning.

Add a truthful encounter recap: move distribution, observed player response distribution, comparable sample count, outcome, and controller version. Leave unavailable metrics absent or explicitly unavailable, not filled with placeholders.

Provide `docs/DEMO.md` with exact controls, recommended scenario commands, and a 60–90 second storyboard based on the implemented build. Suggested story:

1. Show a recurring dodge habit.
2. Show the boss's actual estimate and changed attack preference.
3. Show the player switching timing.
4. Show whether the earlier estimate loses influence.
5. Reveal the active controller type and one real comparison.

Never script the boss's success, hide deaths, invent training progress, or label statistical adaptation as reinforcement learning. A demo can be edited for length, but should identify controller/checkpoint changes and resets.

---

## 14. Milestone sequence and completion gates

### M0 — Preflight and durable plan

Inspect, choose one stack, record versions and scope, establish run/test commands. Keep planning short and start implementation.

### M1 — Playable fight

Create core state, player, three attacks, arena, collision, HUD, win/loss, restart, and a competent static controller. Run core tests and visually inspect when possible.

**Gate:** a complete fight can be played. Do not begin ML integration while this is broken.

### M2 — Fair observation and real adaptation

Implement filtered events, response opportunities, smoothed habit estimates, adaptive utility policy, inspector, and fairness tests.

**Gate:** genuine events change estimates and decisions; hidden-input invariance passes. The UI labels rule-based/statistical adaptation accurately.

### M3 — Demonstration and evaluation

Implement scripted player scenarios, independent strategy switching, comparison commands, reports, encounter logging, and recap/event viewer.

**Gate:** completed simulations generate inspectable evidence. Show unfavorable findings instead of altering reports.

### M4 — Polish and recording readiness

Refine silhouettes, weapon cues, feedback, menus, controls, recording layout, accessibility toggles, and demo instructions. Capture genuine outputs where tools support it.

**Gate:** the local game is coherent and demonstrable, not just testable.

### M5 — Optional trained/model policies

Attempt the bounded PPO milestone, then local model integration only if prerequisites permit. Do not break the default offline game. Keep disabled capabilities explicitly disabled.

### M6 — Final audit

Run the verified checks again from a clean start. Review diffs for secrets, accidental user-file changes, misleading claims, generated junk, stale documentation, and placeholder outputs. Record final status and stop owned background processes unless an explicitly documented preview is appropriate.

If capacity is tight, finish M1–M4 and M6 before M5. Complete acceptance criteria rather than adding features indefinitely.

---

## 15. Final handoff

Deliver the implemented files plus:

- `README.md`: actual setup, launch, controls, test/demo/evaluation commands, architecture, versions, and prerequisites.
- `docs/STATUS.md`: milestone status and next exact action.
- `docs/CLAIMS.md`: implemented/verified/unverified/unavailable matrix, including every model/training claim.
- `docs/DEMO.md`: truthful showcase procedure and storyboard.
- `docs/VALIDATION.md`: commands run, outcomes, artifact paths, and visual validation limitations.
- `docs/NEXT_STEPS.md`: a short prioritized follow-on plan, not a replacement for completed implementation.
- Real small evaluation outputs and actual screenshots/video when captured.
- `.env.example` only for optional settings; never credentials.
- Appropriate dependency lock/config files and ignores for caches, secrets, large runs, and model weights.

In your final response, state:

1. What is playable now and the exact launch command.
2. The actual boss adaptation mechanism.
3. Which tests and evaluations ran, with result paths.
4. Whether RL training ran, whether weights changed, and whether improvement was measured.
5. Which real models are connected versus disabled.
6. Any setup/visual/tool limitations and the highest-priority next step.

Do not say “fully complete” when optional models are stubs or a graphical run was never tested. Do not claim the project needs no setup when prerequisites were installed only in your execution environment.

**Begin by inspecting the workspace, recording the first milestone, and implementing the playable core. Continue through validation and handoff rather than returning another plan.**

---

## Reference starting points

Verify current interfaces and versions rather than relying on memory. These are implementation references, not permission to broaden scope or install everything.

- Godot documentation: https://docs.godotengine.org/en/stable/
- Godot RL Agents: https://github.com/edbeeching/godot_rl_agents
- Gymnasium environment API: https://gymnasium.farama.org/api/env/
- MaskablePPO: https://sb3-contrib.readthedocs.io/en/master/modules/ppo_mask.html
- Laya-MLX: https://github.com/mizorewww/laya-mlx
- Upstream Laya: https://github.com/NandhaKishorM/laya
- Jev documentation: https://docs.typesafe.ai/models
- CLM: https://github.com/Contrastive-LM/CLM
- Long-running Codex workflow guidance: https://developers.openai.com/blog/run-long-horizon-tasks-with-codex
- Durable execution plans: https://developers.openai.com/cookbook/articles/codex_exec_plans

The game's core does not depend on availability of these model repositories or external services. Validate the main experience with the honest local baseline first.
