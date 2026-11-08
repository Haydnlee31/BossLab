# Validation record — 2026-10-04

Environment: Darwin arm64; Node 26.5.0, npm 11.17.0, Python 3.13.1, PyTorch 2.14.0. Godot absent from normal lookup/Applications. Workspace was not a Git repository. No dependency downloads, paid services, model downloads or global changes.

## Commands actually run

| Command | Result |
|---|---|
| `./scripts/bosslab doctor` | Core/version/prerequisites reported |
| `./scripts/bosslab test` | 24/24 Node tests pass, zero skipped; development failures repaired |
| `./scripts/bosslab play` | Loopback preview exercised through Chrome; initial sandbox EPERM resolved by explicit approval |
| `./scripts/bosslab demo` | Fresh server launch prints correct `/?demo=1` URL; loopback permission approved; stopped after audit |
| `./scripts/bosslab evaluate` | 36 completed encounters; `artifacts/evaluation.json` and `.csv` |
| `node scripts/demo-evidence.mjs` | Actual 90-second simulation, early-to-late evidence reversal |
| `python3 ai/train_ppo.py` | 4,096 transitions / 8 updates / 23 completed episodes; checkpoint and 36-row research evaluation |
| `python3 ai/verify_checkpoint.py` | Exact reload/inference, finite parameters, zero masked-action probability |
| `node --check game/presentation/main.js` and `renderer.js` | Syntax passes |

Tests cover start/end/restart, phase lengths, cooldown/readiness, damage windows/deduplication, dodge invulnerability, commitment, aim lock, fixed definitions, arena/resource clamps, healing/lethal ordering, delayed immutable observations, hidden-input invariance, one response per instance, censorship, conservative priors, contradictory history, real-game reversal, inspector/report consistency, dead/stale rejection, bounded contracts, RL masking/termination/truncation.

A development strategy-switch test failed because the script exhausted stamina and marked attempted dodges as issued. Repaired its action reservation and stamina checks; did not loosen the test. Added lethal-healing regression coverage and enforced the eight-tick decision gap for external policies.

## Actual evaluation

Final paired seeds: 1001, 1201, 1409, 1601, 1801, 2003. Timing offset `seed % 3 − 1`; early/late/switch; switch tick 900; ceiling 7,200 ticks; matched configurations across controllers. Policy input never contains scenario labels. Development uses 1–20 and pilot 101/203/307/409/503/607; pilot seeds are not held-out.

| Scenario | Static boss wins | Adaptive boss wins | Static mean damage to player | Adaptive mean damage to player |
|---|---:|---:|---:|---:|
| Early | 6/6 | 6/6 | 250.00 | 250.17 |
| Late | 0/6 | 0/6 | 10.67 | 8.00 |
| Switch | 0/6 | 0/6 | 118.00 | 141.33 |

No timeouts. Damage may exceed starting HP because of three real heals. Both modes win 6/18: no win-rate improvement. Adaptive inflicted more damage in switching encounters and less in late encounters; this is a small scripted sample.

`demo-evidence.json`: early estimate .584 immediately before 40s switch, .141 at 60s, .117 at 90s. Overhead contribution +1.493 before and −.650 after. Actual delivered response events, real outcomes and reset boundaries; headless demo excludes the browser's two-second inter-round pause.

RL results, checkpoint identity/configuration and limitations: [RL.md](RL.md), `artifacts/ppo-training.json`. Mask/reload checks: `artifacts/ppo-verification.json`.

## Browser inspection

Actual Chrome tab at 1280×720 and 1920×1080. Checked title, human combat entry and keys, actual idle defeat at 0 HP, recap, restart to 120 HP/three vials, pause/resume, reduced motion, live scripted demo with reset/switch, inspector, saved comparison and F1 recording. No warning/error console entries during inspection. Inspector intentionally scrolls; menus/controls readable at both sizes.

Genuine screenshots: `title-1280x720.jpg`, `demo-inspector-1280x720.jpg`, `recording-1920x1080.jpg`, `defeat-1920x1080.jpg`. No generated proof images. No video, browser regression suite, touch/gamepad testing, calibrated latency or sustained FPS measurement. Key checks do not establish skilled manual completion. Victory is validated by real scripted headless encounters.

Event viewer is not exact reconstructed playback. Seeds reproduce this JavaScript simulation here; cross-platform replay is not asserted. Local utility timing uses `performance.now`, not neural-service latency.

Final audit: fresh preview launch and current-source browser reload passed. Final menu correctly labels PPO headless-only and models disconnected. J input appeared as a real player-attack event; Space appeared as a delayed visible dodge, including commitment preventing an immediate heal cancel. Event viewer and comparison loaded without console errors. Both owned preview processes were stopped; the test tab was closed and temporary viewport override reset. Core/model source and artifact hashes are recorded in `artifacts/manifest.json`. Build-kit files were never edited. No Git diff is available because this workspace has no Git metadata.
