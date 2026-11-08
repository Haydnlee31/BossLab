> Historical unarmed adaptation evaluation. The active greatsword fundamentals revision has no adaptive evaluation or training; current tests/performance are in [FUNDAMENTALS.md](FUNDAMENTALS.md). Original held-out scenarios/results below are preserved unchanged.

# Native evaluation — 2026-11-03

Predeclared 64 real Unreal encounters: four styles × eight held-out seeds × two controllers. All observations satisfied the 12-tick filter; all outcomes terminated without timeout. Both static and statistical bosses won **16/32**. No win-rate improvement was established. Early and switching scripts lost all eight per controller; late and lateral scripts won all eight per controller. These are scripted scenarios, not human performance or generalization evidence.

The comparison used the same native animation, collision and fixed-step combat authority as gameplay. Each pair shares its seed and the declared reaction offset. Reports contain per-encounter damage, health, duration, move distribution, family counts, recent estimates and actual response events. No rules or scripts were tuned after seeing these outcomes.

Files: `artifacts/unreal/evaluation-manifest.json`, `evaluation-source-hashes.json`, `held-out-evaluation.json`, `held-out-evaluation.csv`, `evaluation-automation/index.json`.

Separate development evidence: seed 202, early→late at 1,800 simulation ticks. Over 6,000 ticks with two disclosed round resets, recent early probability changed .580243→.118542; 11 samples before and 39 after, one censored window. This shows statistical adaptation, not RL or stronger play. The demo preserves evidence across displayed resets; ordinary restarts clear evidence.

Performance and package checks are recorded separately. Headless execution duration is not a rendering benchmark.

**Scenario limitation:** every held-out switching-script encounter ended at tick 1,056–1,218, before the scheduled switch at 1,800. Thus that scenario tests its early phase only and contributes no held-out reversal evidence. It is retained unchanged; the separately labeled development demo supplies the actual switch demonstration with disclosed resets. A future preregistered scenario should ensure the switch is observable without weakening combat rules.

The first actual editor-game benchmark used a 1920×1080 viewport for 60 simulated seconds. After excluding 180 active warmup frames: 2,278 measured frame intervals, mean **23.467 ms** (~42.6 FPS), p95 **52.1445 ms**. The 60 FPS target was **not met**. This was the actual shared Mac, not an isolated GPU benchmark; no screenshot capture or compilation ran during the measured encounter. Packaged performance is not inferred from this result. Artifact: `editor-game-benchmark.json`.
