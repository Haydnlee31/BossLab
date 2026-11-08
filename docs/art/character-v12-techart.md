# V12 — geometry-first upper-body study

The isolated chest–shoulder section now has genuine wraparound depth, a continuous rear, open arm sockets, hollow gorget and overlapping shoulder shells. Independent clay/orbit review accepted a **coarse static construction gate only**. It remains generic and below the approved character concept. This is not a new playable costume or reference-quality character.

The final mapped steel sample removes the earlier visible rectangular UV patchwork, but the final continuous UV layout still has sampled foldovers. **UV production acceptance remains failed.** No physics, rigging, game integration or adaptive boss work occurred. V10 remains the working full-character art checkpoint; V11's rejected projection scenes remain quarantined.

## Construction and correction budget

The source uses the director's original front/side/back/shared-ring sheet and JSON in `artifacts/art/last-vigil-v12/design/`. Dimensions are construction guides, not measured human anatomy. The hidden arm-root half-width was corrected from65mm to56mm before the initial build so the315mm shoulder half-span could accommodate clearance and sheet thickness.

The torso is built from connected cross-sections with real boolean arm sockets. A closed unioned torso/arm support sits inside it. The gorget and shoulder pieces have actual3mm hollow sheet thickness. Cups wrap anterior, lateral and posterior depth; the medial opening is articulation clearance. These are not traced flat cutouts or front-image billboards.

Exactly three geometry candidates were made:

1. `attempt-01`: coherent torso/back/neck, but visibly conflicting coplanar lames.
2. `attempt-02`: recessed upper tongues and a longer medial cup return removed the visible bands. A stronger ray-parity test nevertheless found63 lower-shell vertices inside the preceding shell in each of four pairs.
3. `attempt-03`: hidden tongues stay recessed through the full12mm overlap before rising to the exposed surface. All six sampled pairs then reported zero contained vertices. No fourth appearance candidate was made.

The original nearest-normal sign diagnostic is retained as `attempt-02-nearest-normal-audit-inconclusive.json`. Its negative signs beyond thin shell ends were not valid containment classifications. Final reports explicitly distinguish that legacy diagnostic from three-direction majority ray parity. Vertex sampling is not exhaustive triangle-intersection or motion validation.

## Actual geometry evidence

The final base has11 mesh objects,15,232 vertices,14,789 faces and30,436 triangles, plus a rear closure curve. Every mesh has zero boundary/nonmanifold edges in the saved-scene audit. The smallest sampled shoulder/lame-to-body clearance is2.944mm; this is narrower than the initial8mm exposed-field guide because hidden tongues approach the body. No negative body samples or ray-parity-contained overlap vertices were found in the declared sample scope.

Five900×900 clay stills show front, side, back, three-quarter and elevated neck opening. The actual camera orbit has36 unique480×480 frames, encoded and decoded as36 frames at12fps. The tech artist inspected six chronological frames; QA inspected12/36 and the director six, alongside the stills. This is a camera orbit around static geometry, not animation, cloth simulation or all-frame collision proof.

## UV preparation and preserved failures

The first automatic atlas rendered conspicuous rectangular/triangular finish discontinuities. Its mapping, material images and scenes are preserved under `automatic-uv-discontinuity/` and corresponding suffixed `.blend` files. The initial pre-cleanup mapping is separately preserved under `uv-initial-slivers/`.

Eight UV-degenerate triangles traced to four near-coincident Boolean vertex pairs. An authorized derivative-only cleanup merged those pairs at a100nm tolerance: cuirass vertices1503→1499, faces1231 unchanged, maximum original-point displacement15.56nm. No nonmanifold edges resulted. The frozen attempt03 scene was not changed. This necessary UV preparation changes topology, so the cleaned derivative is not described as geometry-identical to the base.

The cleaned mesh has15,228 vertices and30,428 triangles across the same11 mesh objects. Its sampled body/overlap results match the base. The material scene's geometry digest matches the cleaned UV scene exactly.

One bounded UV continuity correction replaced automatic planar fragmentation with angle-based surface charts, rear median seams on torso/gorget and sharp thickness-return seams. Cuirass charts decreased22→6; shoulder cups14→3 each. Actual checker and material views show a more continuous front/side/back surface.

However, the final1024px strict-interior raster finds425 overlap pixels on the cuirass and1404/1409 on the two cups. Other pieces report zero; all pieces have zero UV-degenerate triangles. These are finite-resolution samples, not an exact/subpixel certificate. Local checker distortion and density differences remain. The improved visible continuity does not constitute clean or production-ready UVs.

## Generated material sample

The art director generated one original1254×1254 flat aged-steel color image with the built-in image-generation tool. The prompt, original output provenance and SHA256 are in `texture-study/`; no reference concept image was projected onto this model. The packed asset hash is `3a7f67eb9b7e205ef8795bcbdcbeeb9e0e328d972d500070c9d64d2fe066f184`.

Real per-piece UVs feed the color image with a400mm mean tile scale. Roughness is an explicitly illustrative inverse-luminance estimate between0.68 and0.32. Metallic is1. There is no image-derived normal, displacement or bump, and no claim that the image is scanned/calibrated albedo or that painted scratches are modeled relief. Seamlessness and physical calibration are unverified.

Four900px material angles, a same-camera alternate-key-light image and one1400px detail show actual lighting response over the same geometry. Source mapping and light response are more credible than V11's projected visual illusion, but the result remains a broad generic armored form with uniform material application. It does not match the character reference's bespoke craft or outfit construction.

## Editable artifacts and commands

- Source: `unreal/art-studio/source/last_vigil_v12.py`
- Guarded launcher: `scripts/bosslab-art-v12`
- Frozen clay base: `unreal/art-studio/revision-v12-2026-11-07/v12-attempt-03.blend`
- Cleaned/checker derivative: `unreal/art-studio/revision-v12-2026-11-07/v12-uv-checker.blend`
- Packed material study: `unreal/art-studio/revision-v12-2026-11-07/v12-material-study.blend`
- Evidence/gallery: `artifacts/art/last-vigil-v12/index.html`
- Exact canonical paths/hashes: `artifacts/art/last-vigil-v12/techart-delivery-audit.json`

Reproduction commands, which overwrite their canonical study outputs and should therefore run only in a copied/new revision when preserving this delivery:

```sh
./scripts/bosslab-art-v12 draft
./scripts/bosslab-art-v12 audit
./scripts/bosslab-art-v12 turntable
./scripts/bosslab-art-v12 uv-continuity
./scripts/bosslab-art-v12 uv-audit
./scripts/bosslab-art-v12 sample artifacts/art/last-vigil-v12/texture-study/generated-aged-steel-albedo.png
./scripts/bosslab-art-v12 sample-audit
```

All final commands completed with exit0 behind the existing10GB Unreal/24GiB free-space guards. Exit status is process evidence, not artistic or UV acceptance. No persistent jobs remain. Final storage and individual process receipts are recorded in the delivery manifest.

## Next concrete action

Preserve this coarse base and failed UV criteria. Before any character integration, resolve the continuous-chart foldovers with deliberately placed thickness/pole seams and distortion checks, then author the concept-specific plate silhouette and actual construction details. Do not restart front-image projection, hide UV defects with noise, or treat this isolated material demonstration as a finished outfit.
