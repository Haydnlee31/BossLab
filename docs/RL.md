# Bounded RL experiment

The default boss is statistical utility, separate from this experiment. **PPO training actually ran**, but PPO remains disabled in the browser. No Laya/LLM inference ran.

Implementation: small custom clipped PPO using PyTorch 2.14.0 primitives. Gymnasium/SB3 were absent, so no claim of using MaskablePPO/SB3 is made. Official references consulted: [PyTorch Categorical distribution](https://docs.pytorch.org/docs/stable/distributions.html) and [PyTorch PPO tutorial](https://docs.pytorch.org/tutorials/intermediate/reinforcement_ppo.html). This implementation has not had an independent RL review.

`ai/environment.mjs` invokes the actual `Combat` class. `ai/bridge.mjs` carries newline-delimited JSON over stdin/stdout; no socket/server or second simulator. Each step advances up to 12 combat ticks. The actor gets 16 numeric features: delayed relative position, boss position/facing/health, observation time, response/direction estimates, effective count and sufficient-evidence flag. Script ID, seed, future timing and player resources are excluded. Legal actions are engine validated; only `continue` is legal while committed or during decision spacing. Death is termination; a 7,200-tick limit is truncation, with value bootstrap for truncation.

The frozen script population cycles early/late/switch and small timing offsets. Training uses development seeds 1–20. Evaluation uses separate seeds 3001/3011/3023 and all three scenarios; no updates occur during evaluation. Neural policies sample their masked distributions with paired RNG seeds; baselines retain their own seeded stochastic utility selection. PPO's 12-tick decision cadence differs from the baselines' every-tick readiness check; do not interpret this as an isolated algorithm-only ablation.

Reward is `damage_to_player / 120 − damage_to_boss / 420`, plus +1 for a boss win or −1 for a boss loss. No reward for issuing attacks, estimates, waiting, or decorative messages. Healing permits total damage above initial HP. Truncations are separately reported; none occurred in this saved evaluation. Stalling remains a research risk requiring broader tests.

Actor and critic are independent 16→32→7 / 16→32→1 tanh MLPs. Categorical logits are masked before sampling and log-probability calculation. On-policy batches of 512 transitions use GAE (.99 discount, .95 lambda), three epochs, minibatches 128, clipping .2, value coefficient .5, entropy coefficient .01, Adam .0003 and gradient norm cap .5. Old rollout log-probabilities are detached; new log-probabilities are differentiable. Truncated rollouts bootstrap; GAE does not cross episode boundaries. Historical evaluation logs are not used for updates.

Run: `python3 ai/train_ppo.py`. Bound: 4,096 transitions (below the brief's 25,000 cap), one environment process, 20-minute training wall limit. No downloads or global configuration. Checkpoints include state dictionaries, optimizer state, config, steps and library version. `python3 ai/verify_checkpoint.py` exercises reload/inference/masking without training.

Actual results in `artifacts/ppo-training.json`: 4,096 transitions, 8 PPO updates, 23 completed training episodes, finite losses, total parameter L1 change 12.296806 and actor L1 change 3.367934. Saved checkpoint reloaded exactly. Training timer was 0.835 seconds in this local run (excludes imports and evaluation); no FPS or general speed claim follows from it.

| Evaluation policy | Encounters | Boss wins | Player wins | Truncations |
|---|---:|---:|---:|---:|
| Saved PPO smoke | 9 | 2 | 7 | 0 |
| Saved untrained reference | 9 | 2 | 7 | 0 |
| Static utility | 9 | 3 | 6 | 0 |
| Statistical adaptive utility | 9 | 3 | 6 | 0 |

**No improvement established.** Mean damage to the player was 111.67 for trained vs 113.67 for untrained. Parameter change proves a gradient update, not learning a superior policy. The saved diagnostics are actual rollout/update results, not an invented learning curve.

Checkpoints: `artifacts/ppo-smoke.pt`, `artifacts/ppo-untrained.pt` (small local artifacts, ignored by Git). Browser inference has not been implemented, so menu/inspector say headless-only. No real Laya, Jev, CLM or strategist model was supplied/connected; no personal model directories or credentials were searched.
