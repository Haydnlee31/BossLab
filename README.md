# BossLab: The Warden

**Arena branch:** [Court of the Last Witness](docs/ARENA_DESIGN_01.md) is a new editable Blender draft for the Funeral Regent. [Actual preview](artifacts/art/arena-design-01/candidate-03/hero-entry.png) · [Floor plan](artifacts/art/arena-design-01/candidate-03/annotated-plan.png). It is not integrated into Unreal yet; this branch also retains the newer [Claude revamp](docs/CLAUDE_REVAMP.md) work.

An original boss-duel prototype. **The active project is the Unreal third-person arena**; the dependency-free browser version is an earlier, runnable reference.

## Current handoff —2026-11-09

Read [HANDOFF.md](HANDOFF.md) first, then [STATUS](docs/STATUS.md), [execution plan](docs/EXECPLAN.md), [decisions](docs/DECISIONS.md) and [claims](docs/CLAIMS.md).

- Existing local Unreal build: greatsword combat, directional dodge, target lock, sprint and pause/quit; optional V13 Blender player costume trial.
- New boss direction: **B — Funeral Regent**, with blue-flame skulls and a proposed chain pull followed by an avoidable stab. These new boss abilities are **not implemented**.
- Current boss clay/focal studies failed visual acceptance. Included scenes and renders are honest work-in-progress evidence, not production-ready assets.
- Boss AI/adaptation remains deferred in Unreal. Browser statistical adaptation, historical headless PPO and unavailable model adapters are separate systems.

## Run the browser reference from a clone

Requires Node.js22+; no npm install or API key:

```sh
./scripts/bosslab test
./scripts/bosslab play
```

Open http://127.0.0.1:5173 and stop the foreground server with Ctrl-C. This is the older top-down reference, not the Unreal 3D game. Handoff verification:24/24 browser tests passed and doctor succeeded on the original Mac; see [handoff](HANDOFF.md).

## Unreal setup and launch

Follow [UNREAL_RESTORE.md](docs/UNREAL_RESTORE.md). The source checkout excludes Epic mannequin files, installed tools, compiled binaries and packages. Restore the manifest-listed dependencies from your own compatible UE installation, then build. The verified local environment was macOS arm64, UE5.8.4, Xcode26.1.1. A fresh-clone Unreal build has not been verified.

After dependencies and the editor target are built:

```sh
BOSSLAB_OUTFIT=v13 BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

Controls: Enter starts; WASD moves; mouse looks; Tab locks target; Space rolls; left-click/J attacks; Shift sprints; Esc/P opens the pause menu. Quit through the menu or Q while paused. Omit `BOSSLAB_OUTFIT` for the original costume. `package-play` requires a separately built local package, which is not in Git.

The project retains a10GB Unreal allocation limit and24GiB free-space guard. No public game deployment or model connection is included. See [publication scope](docs/PUBLICATION_SCOPE.md) for retained checkpoints, excluded dependencies and known historical links. No open-source license has been assigned by this handoff; third-party rights remain separate.

---

## Browser reference

An original top-down Soulslike duel in a ruined sanctuary. The Warden observes combat responses, estimates habits, and changes attack selection. You can change your timing to undermine those estimates.

**Playable offline.** The default game needs Node.js 22+ and a modern desktop browser, with no npm install, Python service, API key, or model server. Tested on macOS arm64, Node 26.5.0, Chrome. This is the brief's **Canvas fallback**: Godot was not installed. Native JavaScript ES modules replace a TypeScript build dependency.

From this directory:

```sh
./scripts/bosslab play
```

Open **http://127.0.0.1:5173**. Stop the server with **Ctrl-C**. It binds only to loopback. If port 5173 is occupied, use `PORT=5174 ./scripts/bosslab play` and open that port. Sandboxed agents may require permission to bind the local port; ordinary Terminal use does not require changing project files.

## Controls

| Input | Action |
|---|---|
| WASD | Move |
| Mouse | Aim |
| K | Restore keyboard-only aim toward the boss; mouse movement resumes mouse aim |
| Left click / J | Committed light attack |
| Space | Dodge in movement direction; without movement, dodge in facing direction |
| E | Heal, three vials; committed 72 ticks |
| Escape / pause button | Pause/resume |
| R | After death, restart; during combat, open pause to confirm a new encounter |
| Tab | Toggle observation inspector |
| F1 | Recording layout; hides inspector/control hints, retains demo disclosure |

Attack and dodge require stamina. Dodge movement lasts 14 ticks; the dodge state lasts 26, with invulnerability only at ages 2–15. Read the amber preparation, dodge near impact, and attack during recovery. Attacks, dodges, and healing cannot freely cancel one another. Reduced motion is in the pause menu. This is a **silent build** with no camera shake or hit-stop.

## Implemented

- One circular arena; original procedural stonework, cloaked player, armored boss, weapon cues, trails, particles, health/stamina, healing, victory/defeat and restart.
- Quick cut, delayed overhead and advancing thrust with authored wind-up, aim lock, active geometry, cooldown and recovery.
- Static history-free utility controller and statistical adaptive utility controller, sharing all combat rules.
- Immutable delayed observation DTOs; events/state arrive after 12 ticks. No raw keys, script labels, switch schedules or hidden resources enter the controller.
- Event-based early/late/no-dodge estimates, direction preferences, short/long decay, attack-family contexts, sample counts, sparse-evidence backoff and censored windows.
- Inspector, scripted early-to-late demo, explicit round resets, JSON export, event viewer and saved comparison viewer.

The adaptive controller is **rule-based attack selection conditioned on online statistical opponent modeling**. Its utility coefficients stay fixed; decayed evidence counts update once per completed exchange. It is not RL or an LLM.

## Commands and evidence

```sh
./scripts/bosslab doctor
./scripts/bosslab test
./scripts/bosslab evaluate
node scripts/demo-evidence.mjs
./scripts/bosslab demo
```

`demo` starts the same server and prints the `/?demo=1` URL. The browser does not open automatically. The scripted demo uses real damage/death and visibly resets rounds while retaining evidence; its stage switches at 40 simulation seconds regardless of success.

The test suite contains 24 passing tests. The matched evaluation runs 36 encounters across early, late and switching scripts. Both static and adaptive bosses won 6/18; **no win-rate improvement was demonstrated**. Reports, event traces and genuine screenshots are in `artifacts/`. See [validation](docs/VALIDATION.md) and the [showcase instructions](docs/DEMO.md).

## Optional research

A real **masked-action PPO smoke experiment** uses installed PyTorch 2.14.0 and the same Node combat core through stdin/stdout. It ran 4,096 transitions, made nonzero actor updates, saved/reloaded a checkpoint and evaluated it. Trained and untrained policies both won 2/9; static and adaptive each won 3/9 on that separate evaluation. This proves the training pipeline runs, not policy improvement.

```sh
python3 ai/verify_checkpoint.py
# Optional finite retraining; overwrites only the project's PPO smoke artifacts:
python3 ai/train_ppo.py
```

Python/PyTorch are **not needed to play**. Their installation is not automated or tested here. PPO is headless-only; its game menu entry stays disabled. Laya/Jev/CLM are not connected. The optional decision contract and bounded strategist schema have test-double validation, not real-model inference. See [RL details](docs/RL.md) and [claims](docs/CLAIMS.md).

## Layout

`game/core/` owns simulation and geometry; `game/ai/` owns permitted-policy logic, estimates, scripts and optional contracts; `game/presentation/` renders state; `ai/` holds the optional Python trainer and shared-core adapter. `scripts/` contains loopback serving and finite evaluation commands. `tests/` uses Node's built-in test runner. `docs/STATUS.md` is the durable restart point.

No action replay fidelity, sustained human playtesting, mobile/gamepad support, FPS target, broad model competence or statistically significant advantage is claimed. This is a complete playable first arena, with a small honest research experiment alongside it.
