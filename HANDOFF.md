# BossLab handoff —2026-11-09

## Start here

The playable work is the Unreal third-person arena prototype. Current player controls and V13 costume trial work locally; the owner confirmed launch. The new Funeral Regent boss art remains below the selected reference, and the new chain/skull attacks exist as proposals only. Do not mistake generated concept images, successful script execution or mesh audits for an accepted character.

Read `docs/STATUS.md`, `docs/EXECPLAN.md`, `docs/DECISIONS.md`, `docs/CLAIMS.md` and `AGENTS.md`. Older entries are dated history; newer owner directions supersede them. The original build brief is preserved unchanged under `BossLab_Codex_Build_Kit/`.

## Run

Browser reference, immediately available with Node22+:

```sh
./scripts/bosslab doctor
./scripts/bosslab test
./scripts/bosslab play
```

Unreal, on the original workstation with its compiled editor module:

```sh
BOSSLAB_OUTFIT=v13 BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

A clone requires the excluded Epic assets and an editor build first: follow `docs/UNREAL_RESTORE.md`. The Mac launcher supports `BOSSLAB_UE_ROOT`; Windows/Linux launching has not been implemented/verified. No packaged executable or tool installation is in this repository.

Unreal controls: Enter start, WASD move, mouse look, Tab target, Space directional roll, left-click/J attack, Shift sprint, Esc/P pause, menu Quit or Q while paused. The browser uses its own controls documented in README; its Tab inspector is not Unreal's targeting control.

## Verified evidence and limits

- New handoff checks: browser24/24 tests passed; browser doctor exit0; no model adapter connected. These do not test Unreal.
- Latest existing Unreal trial evidence:21 baseline native checks plus3 separate V13 transfer/fallback checks passed. Two actual gameplay clips each encoded/decoded180frames. No new Unreal rebuild, packaging or FPS run was performed for this handoff.
- Historical matched720p editor runs: original58.55FPS/V1359.03FPS, one sequential run each, with stalls. Not locked60 or proof that a new boss fits the frame budget.
- V13 player transfer is rigid attachment plus eight palette materials. Cape/leg clipping, approximate grip and missing Blender material fidelity remain. Default costume and old packaged local game remain preserved.
- New Funeral Regent: first weighted clay failed; new unrigged cage passes scoped closed-body topology/sole checks but fails visual quality; shared-landmark focal mask improves eye/nose geometry but fails lip form and hood/yoke fit. Current focal stage has15actualrenders, not a finished boss.

## Resume the art work

Selected design is **B — Funeral Regent**: ivory funerary mask, narrow damaged crown, fitted silver ribs, long embroidered indigo mantle, anatomical-left chain bracer, right pointed sword, exactly3floating blue-flame skulls. Do not substitute the simpler barred-visored A design.

Authoritative current resources:

- `artifacts/art/funeral-regent-construction-2026-11-08/`: generated targets, with documented illustration inconsistencies.
- `unreal/art-studio/regent-cage-2026-11-09/regent-cage-03.blend`: unrigged connected technical body, not accepted visual foundation.
- `unreal/art-studio/regent-focal-2026-11-09/regent-focal-03.blend`: rejected actual focal study.
- `unreal/art-studio/source/regent_focal_landmarks.json`: shared authored constraints, not reconstructed anatomy.
- `docs/art/funeral-regent-focal-techart.md` and `docs/art/regent-focal-qa-2026-11-09.md`: exact failures and integrity evidence.

Exact next modeling action: preserve the body; construct deliberate quad facial patches around eyelids/nose/lips without global depth-field smoothing. Fit a closed hood to the actual cranial envelope and verify front/side/back clearance before adding joined shoulder-yoke pattern surfaces. Do not repeat whole-character procedural regeneration, add texture noise to hide shape failure, or infer art acceptance from numeric tests. The current procedural workflow has not demonstrated reference-quality craftsmanship.

Only after neutral shape/fit passes should localized arm/cloth weights and motion be tested. Then author whole-body cast, pull, release, stab and distinct missed-chain retrieval. Keep the long mantle; use real panel cuts rather than a rigid cape.

## Combat and AI boundary

Proposed hook: committed straight throw, ordinary roll invulnerability, bounded swept pull, release before separately avoidable stab, obstacle/reset/death cancellation and no simultaneous skull damage. It is not implemented. Preserve engine-owned timing/contact and existing player rules; no input reading or adaptive tuning of hit rules.

Unreal currently uses fixed rehearsal; new boss AI remains deferred until fundamentals/art are ready. The browser's statistical adaptation is not RL. Historical PPO smoke checkpoints are headless-only, excluded from Git, and not Unreal controllers. Laya/LLM/local-model adapters are not connected. Missing models must stay visibly unavailable.

## Retention and working rules

The requested cleanup removed1113obsolete scene/cache files totaling132,840,630bytes; exact hashes are in `artifacts/maintenance/handoff-prune-2026-11-09/manifest.json`. Keep latest2current focal scenes and latest2cage scenes, the meaningful V13 player pair, and required V10/V12 dependency exceptions documented in `docs/art/checkpoint-retention-2026-11-09.md`. Old evidence can refer to pruned files; it is historical, not an assertion of present availability.

No installed tools, working package, original build kit, active source or required dependencies were removed. Public exclusions remain on the original workstation; excluded historical media may be unavailable to a clone. See `docs/PUBLICATION_SCOPE.md`.

Single DCC writer/heavy job; single Unreal binary writer via editor.lock. Keep10GB allocated under unreal/ and24GiB free during heavy work. No paid calls, external model downloads, machine-wide modifications or persistent background jobs. Scope permission for this GitHub handoff does not authorize unrelated deployment or messaging.
