# Native statistical controller contract

Implementation target: the engine samples visible positions, visible action/age, and its own attack identity/age into value records. Records arrive 12 fixed ticks later. No input, pending commands, player resources, script identity, seed, switch schedule, future trajectory or actor reference enters the policy.

An opportunity spans each boss cue through the final active tick. Only the first visible dodge onset inside that interval counts. Early means before 55% of windup; otherwise late; no onset is no response. Movement direction is classified toward, away, or lateral relative to the boss. Incomplete windows on death/reset are censored, never converted to no response. Encounter and attack IDs prevent double counting and stale delivery.

Recent and long response weights decay by .82 and .97 per valid exchange. One symmetric prior per category keeps estimates finite. Six valid pooled samples are required for utility conditioning; six family samples enable family context, otherwise pooled estimates are used. Bounded adjustments change selection probabilities only. Timing, legality, resources, aim locking, motion and collision remain engine owned. Statistics are not reinforcement learning.

The inspector must show actual delivered ticks, sample counts, estimates, utility adjustments, probabilities, proposals and engine acceptance. It must mark insufficient evidence and distinguish selection probability from hit probability. RL and Laya/LLM status remain unavailable in this native build.

The held-out manifest is artifacts/unreal/evaluation-manifest.json, declared before adaptive implementation. Development uses seeds 101/202/303. Outcomes do not justify tuning on held-out cases.
