# Last Vigil v5: static garment construction study

Status: final static review evidence frozen; overall artistic target remains unmet. Original studio asset only; no Unreal integration, production rig, motion validation, runtime optimization or artistic acceptance. The approved generated concept remains a direction reference, not a built asset.

## Actual changes

- Replaced the v4 separate mantle backing with an authored open horseshoe cage: 17 deliberately spaced sections and four load bands, 68 landmarks. A local paired-section fold, shoulder support band and downward hem replace the earlier radial cone. The control cage is retained in the scene and exported as JSON.
- Continuous surface-following undercoat and longer guided fibers replace repeated tiles: 18,000 short strands and 4,800 longer strands. This is offline studio cost. The groom still reads combed and its backing remains too broad for the reference target.
- Shoulder fields retain angular descending silhouette with shallow curvature. Neck side rays identified the exposed padded seal; this specific liner was fitted inward/down and made dark, rather than recoloring steel globally.
- Surcoat and cape use authored unequal broad fold controls, fitted bindings, actual small stitch curves, panel seams and hem thickness. New physically scaled original wool shader uses 0.8/1.1 mm yarn directions and restrained relief, high roughness and low sheen. Existing gold cape graphic is retained and still reads printed rather than convincing embroidery.
- Rigid tassets retain broad gently curved plate fields. Hidden cloth is compressed behind the plates; the rejected attempt to conform metal to cloth folds is preserved separately.

## Isolated glove UV milestone

`v5_glove_uv_study.py` loads only two static glove meshes. It marks actual seam edges, unwraps, averages island scale, packs, renders checkers and measures strict-interior raster overlap at 1024. Final MINIMUM_STRETCH trial has 19 islands per hand, no one-face debris (smallest 281 faces), zero degenerate UV triangles and finite coordinates. It still has 2 right / 1 left overlapping raster samples. This is a substantial improvement over the old collapsed projection, not a perfect or production unwrap. Finite raster sampling cannot certify absence of subpixel overlap.

The isolated study is **not integrated** into the full character. The main scene retains the explicitly named projected leather sample UV with dorsal overlap and side compression; original masks were not falsely claimed to transfer to new islands. Earlier normal-fragmented, face-isolation, two-half and digit-cut failures are preserved under `glove-uv/iteration-*`. Numerical zero overlap from hundreds of tiny face charts was rejected as unusable.

## Preserved failures and resource limits

Analytic mantle, initial cage, support-02 and support-03 evidence are retained. The support-03 fold was subsequently softened and groomed. The conformed-metal regression is retained under `milestone-02-conformed-plate-failure`. A NumPy vector attribute error in the cloth-fit patch caused a 4.18 second failed build; its log, source and receipt remain. Corrected build exited 0.

An early backing run crossed the 24 GiB reserve between the last periodic poll and child exit. Work stopped; the launcher now also checks after exit. Parent reclaimed only documented project-local rebuildable DDC, and free space recovered before continuation. Guards remain 10 GB under unreal/, 24 GiB free and 20 minutes per foreground job. No GPU, downloaded assets, global cache changes or persistent jobs were used.

## Remaining quality limits

The hero remains below the approved reference: mantle resembles a combed pelt, armor and skull have simplified authored fields, glove anatomy remains padded, material craftsmanship is not reference-level, cape decoration is largely flat. All cloth/cape changes are static: old physics cache is invalid and no animation evidence is claimed. Static surface clearance checks do not validate motion or all garment intersections.

Final exact hashes, geometry metrics, dimensions, process receipts and image list are recorded in the adjacent `techart-delivery-audit.json` after the final renders. Review links are in `artifacts/art/last-vigil-v5/index.html`; parent owns the matched v4/v5 comparison board.

## Final collider audit correction

The first final audit reported 1,975 negative samples (minimum -67.99 mm). Object-tagged rerun proved **all 1,975 hit the new sewn horseshoe yoke**, which is the mantle backing but lacked the old name substring `mantle`. This incorrectly entered the body collider set. The exact yoke is now explicitly excluded, matching the original stated mantle exclusion. No cape geometry was moved. Corrected body-envelope audit: 25,236 samples, zero negative, minimum 23.486 mm. The diagnostic-inclusive-yoke report and receipt remain under `milestone-02-clearance-failure`. This does not validate cape/yoke intersection or animation.

Final evidence: 15 coherent 720×920/16-sample views plus two distinct 1400×1800/48-sample details, all from the same saved geometry. High-resolution inspection resolves subtle cloth weave but confirms the remaining broad smooth surfaces, sparse-looking overcoat fiber traces and simplified construction. Reloaded geometry: 326 renderable objects, 858,923 evaluated vertices, 1,523,374 triangles, all finite; ten packed images.
