# Checkpoint retention recommendation —2026-11-09

Read-only inventory and source-dependency inspection. **No deletion or Git operation performed by this task.** Paths below are exact project-relative paths. Do not treat this document as a claim that old evidence remains after a later cleanup; orchestrator should record every actual deletion with size/hash.

## Keep: active checkpoints and rebuild exceptions

- `unreal/art-studio/revision-v13-2026-11-07/last-vigil-v13-context.blend` — 31,762,157 bytes.
- `unreal/art-studio/revision-v13-2026-11-07/v13-attempt-04.blend` — 2,607,725 bytes.
- `unreal/art-studio/revision-v10-2026-11-07/last-vigil-v10.blend` — 24,778,507 bytes.
- `unreal/art-studio/revision-v12-2026-11-07/v12-attempt-03.blend` — 1,672,359 bytes.
- `unreal/art-studio/revision-v12-2026-11-07/v12-uv-checker.blend` — 2,319,357 bytes.
- `unreal/art-studio/revision-v12-2026-11-07/v12-material-study.blend` — 4,588,874 bytes.
- `unreal/art-studio/regent-focal-2026-11-09/regent-focal-02.blend` — 698,227 bytes.
- `unreal/art-studio/regent-focal-2026-11-09/regent-focal-03.blend` — 713,075 bytes.
- `unreal/art-studio/regent-cage-2026-11-09/regent-cage-03.blend` — 943,520 bytes.
- `unreal/art-studio/regent-cage-2026-11-09/regent-cage-02.blend` — 940,493 bytes.

Player latest meaningful pair is the final V13 context and its authored focal04 input, not context.blend1 plus the context. Source `last_vigil_v13.py` fixes A=4/C=16 and `context_build()` explicitly loads V10 canonical and v13-attempt-04. Its actual other external inputs are `artifacts/art/last-vigil-v12/design/shared-landmarks.json` and `artifacts/art/last-vigil-v12/texture-study/generated-aged-steel-albedo.png`. Preserve those paths, texture provenance and all source scripts. V13 attempts01–03 are obsolete inputs; current A4 context does not read them.

V12 stage exceptions: geometry03 is the base for UV preparation; final checker is the input for material study; final material is the reviewable output. Retain all three stage dependencies, despite a simple two-file cutoff. V12 source generates geometry independently from its design JSON. V13 does not directly load V12 blend files.

V10 canonical is a **required packed input**, not optional historical clutter. Rebuilding V10 itself from its historical script would require V9-armor.blend, already removed by prior authorized cleanup. Thus keeping V10 canonical avoids depending on the incomplete historical rebuild chain. Do not claim every V1–V10 historical script is presently reproducible.

Boss latest focal pair02/03 must stay, both explicitly rejected. Cage03 stays as required technical base; cage02 is its latest alternate for readable comparison. No current focal script loads either cage, but the approved next workflow depends on retaining cage03 unchanged.

## Candidate checkpoint deletions

- `unreal/art-studio/funeral-regent-clay-2026-11-09/regent-attempt-02.blend` — 2,778,153 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/funeral-regent-clay-2026-11-09/regent-attempt-03.blend` — 2,749,805 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v12-2026-11-07/v12-attempt-01.blend` — 1,672,359 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v12-2026-11-07/v12-attempt-02.blend` — 1,672,359 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v12-2026-11-07/v12-material-study-automatic-discontinuity.blend` — 4,559,660 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v12-2026-11-07/v12-material-study.blend1` — 4,559,660 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v12-2026-11-07/v12-uv-checker-automatic-discontinuity.blend` — 2,290,143 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v12-2026-11-07/v12-uv-checker.blend1` — 2,290,143 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v12-2026-11-07/v12-uv-initial-slivers.blend` — 2,290,423 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v13-2026-11-07/last-vigil-v13-context.blend1` — 27,493,145 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v13-2026-11-07/v13-attempt-01.blend` — 1,698,017 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v13-2026-11-07/v13-attempt-02.blend` — 1,873,525 bytes; obsolete study or automatic backup, not read by current V13/focal source.
- `unreal/art-studio/revision-v13-2026-11-07/v13-attempt-03.blend` — 2,047,238 bytes; obsolete study or automatic backup, not read by current V13/focal source.

Exact above checkpoint candidates total **57,974,630 bytes**. The old weighted-clay02/03 pair is superseded by the explicit cage and current focal line; retain its reports/source/stills as rejected evidence even if removing its scene checkpoints.

## Candidate obsolete simulation caches

- `unreal/art-studio/revision-v9-2026-11-07/blendcache_last-vigil-v9-solver/` — 13,612,000 bytes.
- `unreal/art-studio/revision-v9-2026-11-07/iteration-01-unstable-tasset-contact/blendcache_last-vigil-v9-solver/` — 6,806,000 bytes.
- `unreal/art-studio/revision-v9-2026-11-07/iteration-02-stable-body-only/blendcache_last-vigil-v9-solver/` — 6,806,000 bytes.
- `unreal/art-studio/revision-v9-2026-11-07/iteration-03-mail-layer-breakthrough/blendcache_last-vigil-v9-solver/` — 6,806,000 bytes.
- `unreal/art-studio/revision-v9-2026-11-07/iteration-04-stable-mail-and-ease/blendcache_last-vigil-v9-solver/` — 6,806,000 bytes.
- `unreal/art-studio/revision-v9-2026-11-07/iteration-05-unsafe-curved-attachment/blendcache_last-vigil-v9-solver/` — 6,806,000 bytes.
- `unreal/art-studio/revision-v9-2026-11-07/iteration-06-layered-collider-failure/blendcache_last-vigil-v9-solver/` — 13,612,000 bytes.
- `unreal/art-studio/revision-v9-2026-11-07/iteration-07-rejected-closed-proxy-trial/blendcache_last-vigil-v9-solver/` — 13,612,000 bytes.

These eight V9 rejected cloth caches total **74,866,000 bytes**. Current V13 context uses static authored cape/skirt; no active source path loads this V9 solver/cache. Their solver scenes were already pruned. Preserve V9 failure logs/reports, README-STATUS and `neutral-handoff/` OBJ/attachment/export provenance. Do not delete the entire V9 directory blindly.

## Old V3–V9 directories and archives

- V3–V7 contain small authored PNG texture sets and occasional README files; no remaining `.blend` checkpoints. They are not required as external paths by current V13 code, whose V10 input was reported packed. However these PNGs are authored originals, not unnecessary checkpoints. Recommend retaining them under this checkpoint-only cleanup unless a separate asset-prune decision explicitly permits removal. No new Blender unpack validation was run.
- V8 and V9-armor directories are empty at inventory time. Removing empty directories saves negligible bytes. V11 contains only its rejected-status README; retain it.
- `artifacts/art/checkpoint-character-v12-geometry-study-2026-11-07.tar.gz` is a historical duplicate archive, not a runtime/rebuild input. Optional removal after the orchestrator inventories its contents and confirms no unique payload is being lost; this task has not inspected archive contents, so it is **not in the unconditional deletion list**.
- Preserve `artifacts/unreal/pre-animation-refinement-source.tar.gz` and `artifacts/unreal/u0-verified-source.tar.gz` pending owner/orchestrator source-history assessment; this DCC task did not assess their unique game history.
- Never delete Blender.app bundled `.blend` brushes/startup files, the active Unreal project, V13 runtime JSON, exported audit/provenance, concept targets or source/role documents as art checkpoints.

## Git handoff caveat

This is local retention guidance, not a public redistribution/licensing approval. The orchestrator must separately assess third-party engine/assets, binaries, large files, ignored paths and secrets before the requested public push. No new DCC launch, game edit, cleanup command or Git push was performed here.
