# Preserved historical status — superseded by fundamentals revision


## Working build and verified results

- U0–U6 implemented: native Epic MCP proof; complete animated third-person duel; committed strike/dodge/heal, stamina, three boss moves and actual animated-limb collision; original sanctuary/armor; static/statistical controllers; delayed observations, inspector/events/export, controlled switch demo and real evaluation.
- Final native/editor suite: **13 passed, zero failures/warnings** (`artifacts/unreal/u7-editor-tests.json`). Complete encounter at 30/60 render Hz ended identically at tick 3,607, player/boss HP 100/0. Initial test setup failures and diagnostics retained.
- Packaged suite: **10 combat/fairness tests passed, zero test failures/warnings** (`u7-packaged-tests.json`). The package log reports a missing optional HTML template; JSON results are valid. Launcher now validates fresh JSON rather than trusting Unreal's exit code alone.
- Real packaged manual controls: movement/lock/strike gave boss 216 HP, received kick left player 72 HP; heal restored 100 HP and consumed one charge. Actual PNG/state captures are in `artifacts/unreal/packaged-runtime/Saved/BossLabEvidence/`.
- Packaged labeled development fight won at tick **3,027**, player HP **76**, boss HP **0**, moves **9/6/6**. Recap shows 240 damage dealt / 24 taken. Source/controller/rules remain identical to the evaluated core.
- Actual development reversal: early estimate **.580243 → .118542**, 6,000 ticks, two disclosed resets, 11→39 valid samples. This is statistical adaptation, **not RL**.
- Held-out evaluation: **64 real encounters**, static/adaptive boss wins **16/32 each**, zero timeouts. No advantage established. All switching encounters ended before tick 1,800; held-out reversal is therefore untested. Scenarios were not retuned.
- Editor-game 1080p benchmark: 2,278 samples, mean **23.467 ms (~42.6 FPS)**, p95 **52.1445 ms**. 60 FPS target not met. **Packaged benchmark has not run.**
- Real gameplay footage: 180 unique engine frames, 6 seconds at 1280×720, encoded and independently decoded; fixed 30 Hz capture, not real-time FPS evidence, no audio track.

## Exact checkpoint boundary / known packaging issue

U7 is **not complete**. The current Development package builds and plays with editor/MCP closed. Manual verification discovered inherited Unreal debug key bindings: F1–F5 and F9 also trigger engine debug commands. In particular F5 changed the view to shader complexity while switching controllers, hiding the rendered scene. The victory screenshot `combat-20261103-100035-3027.png` records this actual defect; do not use it as polished scene evidence.

A project-only fix is now saved in `unreal/BossLabWarden/Config/DefaultInput.ini`: subtract the six conflicting `DebugExecBindings` from `/Script/Engine.PlayerInput`. **This last configuration change has NOT been recooked, packaged or manually verified.** The existing packaged executable/content still predates this fix. C++ source is compiled/tested; combat and policy definitions were not changed.

Packaged app sandbox remains enabled. Runtime logs/exports use `~/Library/Containers/com.YourCompany.BossLabWarden/Data/Library/Caches/BossLabVerification/`; the bounded launcher copies them into `artifacts/unreal/packaged-runtime/` on exit. First project-directed export failed and is retained as evidence; corrected container exports succeeded. No sandbox weakening or machine-wide setting change.

Audio assets load, but packaged CoreAudio logged unknown device/sample-rate and timeout/underrun warnings. Auditory quality/output remains unverified. Earlier editor Python shutdown intermittently crashed in Slate/ICU; diagnostics retained. Latest packaged game exited 0 on the requested bounded stop.

## Exact next action after owner resumes

1. Read AGENTS.md, STATUS.md, EXECPLAN.md, DECISIONS.md and CLAIMS.md.
2. Run `./scripts/bosslab-unreal doctor`; retain the **6 GiB under unreal/** ceiling and **24 GiB free** reserve. Latest measured project size about **4.1 GiB**, free **25.2 GiB** before checkpoint. Do not delete personal files or download assets.
3. Run `./scripts/bosslab-unreal package` to recook the saved input-binding fix. Then run `./scripts/bosslab-unreal package-test` and require a fresh passing JSON report.
4. Run `./scripts/bosslab-unreal package-play`; manually verify F1/F2/F3/F4/F5/F9 preserve the intended lit scene while performing their game actions. Inspect a real PNG, controller reset, inspector and export. Do not infer this from a successful build.
5. Close that game. Run `./scripts/bosslab-unreal package-benchmark` with no simultaneous compilation/capture; inspect actual 1920×1080 frame-times CSV/JSON and report the result without claiming 60 FPS unless established.
6. Finish U7 claim/status audit and final checkpoint, retain unfavorable evidence, stop owned processes, and provide final launch/controls/results/limitations handoff.

Verified launch: `./scripts/bosslab-unreal package-play` (known shortcut conflict pending recook); editor fallback `./scripts/bosslab-unreal play`. Complete controls: docs/UNREAL_RUN.md. No API key/model server required. Native RL/Laya/LLM remain unavailable. Historical browser PPO remains headless-only and cannot control Unreal. No public deployment, downloads, paid calls, new training or persistence mechanisms.

Human feel sessions, gamepad/mobile, notarized distribution and sound-quality assessment remain outside verified results.

---

## Preserved 2026-10-04 handoff

M0–M4 and M6 complete. M5 completed a real bounded PPO experiment and optional contract tests; actual Laya/Jev/CLM/LLM integration remains unavailable. No task or training continues in the background. Owned preview servers stopped; browser tab closed and viewport restored.

## Runnable build

From `/Users/haydn/Documents/BossLab`:

```sh
./scripts/bosslab doctor
./scripts/bosslab play
```

Open http://127.0.0.1:5173. Stop Ctrl-C. Node 22+ and a modern browser required. No install, Python server, API key or model needed for the game. `./scripts/bosslab demo` prints http://127.0.0.1:5173/?demo=1. Both launchers verified. Sandbox loopback binding required explicit approval; normal Terminal launch uses the same commands.

Implemented: original Canvas sanctuary, three authored locked-aim attacks, committed player attack/dodge/heal, health/stamina, win/loss/restart/pause, static and statistical adaptive controllers, 12-tick observation boundary, event estimator, truthful inspector, scripted timing switch with disclosed resets, recording layout/reduced motion, recap, export/event viewer and saved comparison.

## Evidence

- `./scripts/bosslab test`: **24 passed, zero failed/skipped**, saved in artifacts/test-results.txt.
- `./scripts/bosslab evaluate`: 36 held-out matches; both baseline/adaptive bosses won **6/18**. No win-rate improvement. JSON/CSV and switch logs in artifacts/.
- `node scripts/demo-evidence.mjs`: real early response estimate .584 before switch → .141 at 60s → .117 at 90s. Utility changes follow actual delivered events.
- Actual Chrome inspection at 1280×720 and 1920×1080: title, play, attack/dodge, commitment, pause, death/restart, reduced motion, live inspector, demo switch/reset, event/comparison viewer, F1 layout; zero inspected warning/error console entries. Four real screenshots in artifacts/.
- `python3 ai/train_ppo.py`: **4096 transitions**, 8 PPO updates, finite losses, actor L1 change **3.367934**, saved checkpoint/reloaded exactly. Trained/untrained each win **2/9**; static/adaptive each **3/9** on separate seeds. No improvement established.
- `python3 ai/verify_checkpoint.py`: finite parameters, exact reload/logits, zero masked-action probability. Updated bounded subprocess timeout also smoke-checked without retraining.

## Availability and limitations

Canvas/JavaScript fallback chosen because Godot was unavailable; no engine download attempted. macOS arm64, Node 26.5.0, Python 3.13.1, installed PyTorch 2.14.0. No Git repository existed; original build kit preserved. No global installs, paid calls, credential searches or persistence mechanisms.

PPO is **headless-only**; game selection disabled until browser inference is implemented and parity-tested. It is a custom PyTorch PPO smoke implementation, not SB3. Laya/Jev/CLM are **not connected**, strategist **disabled**; only generic bridge/schema test doubles exist. No supplied authorized runtime/checkpoint was available. Silent build; no video/FPS benchmark, mobile/gamepad testing, exact replay guarantee, or extensive human playtesting.

## Exact next action

For the owner: run `./scripts/bosslab play`, complete several human fights, and record readability/stamina feedback. For continued implementation: read AGENTS.md and docs/CLAIMS.md, run `./scripts/bosslab test`, then improve from those human observations using development seeds. Do not tune on held-out reports or label statistical utility as RL. Optional future model work is in docs/NEXT_STEPS.md.
