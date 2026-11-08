# V11 — bounded image-projection experiment, rejected for asset use

The authorized reset used the approved concept image on an isolated chest–shoulder–collar study. It made a large **source-angle appearance change through image projection**, but did not produce a coherent multiangle character surface. The initial attempt and two allowed corrections are exhausted. No fourth candidate or proper-material conversion was performed. V10 remains the authoritative editable costume checkpoint.

## Actual method and provenance

The unchanged source is `artifacts/art/last-vigil-concept-2026-11-07/concept-target-not-built.png`. Its bytes are packed into each editable scene. The image includes baked lighting and generated surface detail. The projected front material is explicitly emission-based, so its highlights and shadows remain image content rather than relightable PBR.

Coarse geometry was authored from source-image landmarks: a curved breastplate with real side/back depth, separate curved shoulder layers, coarse collar masses and, in the final trial, a hollow gorget and neutral arm roots. Front UVs use the declared orthographic transform `x=(pixel_x−473)/500`, `z=(650−pixel_y)/500`. Reference camera looks along +Y; three-quarter and side cameras expose the actual depth. Scale is approximate, not calibrated photogrammetry. Unseen faces use a neutral material instead of invented source detail.

Rivets, engraving, hair strands, stitching, plate wear and nearly all fine relief visible in projected views are **pixels, not sculpted geometry**. Every projected render is labeled baked-light/not-PBR. Clay and checker-coordinate diagnostics are separate and expose the actual coarse surfaces.

## Three actual candidates

1. **Attempt01:** source angle shows the concept's detail, but a missing clavicle region and shallow disconnected shoulder/collar shells fail multiview inspection. Side reveals a detached neutral rear support.
2. **Attempt02 / correction1:** filled clavicle region; shoulder/collar surfaces wrap through actual depth, and the detached sphere was removed. Side and three-quarter still reveal stretched image content, disconnected rear return and unsupported far shoulder. Better source-angle look study only; not accepted as a character asset.
3. **Attempt03 / correction2:** a hollow gorget and arm-root supports attempt to connect the volumes. The supports visibly occlude/intersect the projected shoulder layers, including at the reference angle. This is a regression and is rejected. The cap is reached; the failure is preserved rather than hidden by a fourth iteration.

All 18 renders, all three scenes, per-attempt sources, construction records and run logs remain available. `attempt-ledger.json` records the observed run outcomes. The final scene directory has a prominent rejected-study README so its last candidate cannot be mistaken for the working costume.

## Verification and limits

The read-only reload audit verifies source-image identity, packed-image bytes, finite geometry/UVs and per-piece depth bounds. It does not transform the failed artistic result into a pass. These are ordinary real mesh shells, not a single billboard; nevertheless the projection is strongly view-dependent and does not recover missing 3D form.

Physics was off by request. There was no simulation, collision certification, topology/production-UV claim, rigging, Unreal integration, gameplay test, AI work, new model download or material scan. The original game, V10 and source image were not modified. All Blender runs used the project-local foreground CPU launcher and unchanged storage guards.

## Files and reproduction

- Source: `unreal/art-studio/source/last_vigil_v11.py` (final rejected attempt03).
- Scenes: `unreal/art-studio/revision-v11-2026-11-07/v11-attempt-01.blend` through `v11-attempt-03.blend`.
- Evidence: `artifacts/art/last-vigil-v11/attempt-XX-{reference,three-quarter,side,clay-reference,clay-side,uv-reference}.png`.
- Manifest: `artifacts/art/last-vigil-v11/techart-delivery-audit.json`.
- Read-only audit: `./scripts/bosslab-art-v11 audit`.
- `./scripts/bosslab-art-v11 probe reference three-quarter side` rerenders the existing final rejected scene; it does not improve it. Do not start another draft within this capped study.

The concrete limitation is not missing texture detail: a single generated view supplies attractive pixels but leaves the side/back shape and layer attachment underconstrained. This implementation did not fit coherent supporting volumes within the bounded attempts. A successful continuation would require a separately authorized geometry/multiview authoring task; this study does not establish a usable asset or permission to expand the experiment.
