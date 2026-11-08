# Character revision — specialist brief, 2026-11-07

## Shared goal and inputs

Owner explicitly requests delegated development and rejects the current character design as insufficiently realistic. Improve the original Keeper of the Last Vigil / Oathwake studio master through actual 3D work. Read AGENTS.md, docs/STATUS.md, docs/EXECPLAN.md, docs/DECISIONS.md, docs/CLAIMS.md, docs/LAST_VIGIL_ART_STUDY.md and the applicable copied role guide in docs/agent_roles. Inspect actual hero/front/back/armor/hilt/sword PNGs under artifacts/art/last-vigil. The source is unreal/art-studio/source/last_vigil.py and editable static master is unreal/art-studio/last-vigil.blend. Prior technical integrity is not artistic acceptance.

## ART-02 — art_director

Own docs/style_bible.md and docs/art/character-revision-2026-11-07.md. Diagnose large forms, construction, materials and motif hierarchy. Specify original implementable changes and a short visible acceptance rubric. Give the technical artist an early direction, then a complete written handoff before final implementation. Cite researched sources; no asset downloads. Review actual v2 renders and route specific defects. Done when the written handoff and actual-render review exist; overall art acceptance may still fail.

## ART-03 — animation_techart

Own unreal/art-studio/source/last_vigil_v2.py, scripts/bosslab-art-v2, unreal/art-studio/revision-2026-11-07/, artifacts/art/last-vigil-v2/, docs/art/character-v2-techart.md. Implement the art handoff using separate, reproducible editable geometry/material assets. Substantial silhouette/construction changes take precedence over added repeated ornament. Render representative front/back/detail views; inspect and correct visible defects. Preserve failures and prior source/scenes/evidence. Report whether any cape geometry/cache changed; no reuse of prior simulation claims for changed cloth. No game integration before visual/readiness gates. Done when actual implemented assets, review views, provenance and limits exist and QA has inspected them.

## QA-02 — qa_balance

Own docs/art/character-v2-qa.md and optional independent evidence JSON. Read-only access to art/game; do not fix source. Inspect baseline and v2 images at matching angles and judge explicit visual/construction/material criteria. Verify unchanged gameplay hashes and resource guards through lightweight checks. Report ready/needs work/blocked with observed defects and reproduction paths; no artistic pass inferred from counts. No gameplay benchmarks/tests required if gameplay unchanged. Send actionable defects to the technical artist and inspect corrections.

## Constraints and handoff

No new boss AI, statistical adaptation, RL, model integration or training until all other readiness gates are met. No new combat mechanics or timing changes, source/config/build edits, external asset downloads, paid calls, global changes, persistence, or deletion of prior work. Keep unreal/ below10GB and at least24GiB free; bounded foreground heavy jobs only. One heavy renderer, owned by animation_techart and coordinated with orchestrator. editor.lock stays unassigned because no Unreal binary writes are needed. Root reads outputs, maintains board/status/claims/decisions, verifies review artifacts exist and saves checkpoint. User-facing dates use Asia/Singapore.
