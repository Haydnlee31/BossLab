# Character V5 independent QA — 2026-11-07

## Scope and verdict

**Needs work; final V5 independently reviewed. Actual local progress, overall reference realism unmet.** Continue approved concept fidelity through meaningful visible authoring milestones. V4 remains preserved evidence; generated concept remains direction, not built geometry. QA owns this report and optional final audit only. No source edits, heavy jobs, runtime work or AI.

## Milestone review gates

1. **Mantle and plate fit:** inspect actual front/side/back and clay. Remove exposed rectangular backing and repeated comb-tuft reading; judge coherent mass, irregular clump direction/scale and shoulder attachment. Thin angular armor must feel fitted/constructed rather than floating flat sheets. Do not accept more strands as sufficient.
2. **Garment and armor craft:** inspect actual full figure plus chosen detail. Cloth needs meaningful thickness/folds/seams and material separation; armor needs intentional formed planes, edges and retention rather than blanket noise or ornament. Judge visible concept progress separately from numerical integrity.
3. **Hands/UV if implemented:** inspect palm/dorsal/side clay and material. Verify separate usable islands, projection collapse/overlap and actual named UV shader assignment. Diagnostic mask placement must correspond to physical regions. A texture file, packed map, UV coverage figure or closed mesh does not establish anatomy or production UV quality.

## Final evidence requirements

Review actual views at each milestone and route specific defects to technical artist/director. Preserve failures. Only after artist source freeze: hash unchanged gameplay baseline and selected immutable V4 evidence, record current storage, final reviewed image/source/scene identities. No repeated gameplay tests for unchanged gameplay. No cloth-motion, production rig, runtime performance or boss-learning claim. AI gate remains closed.

## Milestone1 first actual draft

Inspected hero/head. Continuous short undercoat removes much of V4's tuft-grid/exposed-backing patchwork. Remaining major mismatch: two broad thin carpet-like flaps, straight front boundaries, shallow shoulder crown and black opening near neck attachment. Routed deliberate backing form/cage correction before further fiber expansion: rounded attachment, visible thickness, asymmetric taper and shoulder mass. This is an observed coverage improvement, not a mantle realism pass. Await backing-only side/back/clay evidence.

## Reserve-constrained support02 review

Inspected actual `support-02/bare_headside.png` and `bare_back.png`, explicitly groom-omitted backing-only evidence. Continuous neck/rear attachment and absence of an obvious long rear tab are visible improvements. Backing still reads as a smooth broad conical poncho with near-even hem and abrupt side flare above the shoulder plate, rather than compact neck roll/shoulder saddle/irregular drape. Routed to technical artist. These views do not validate final groom, material or whole-mantle appearance.

Root reported reserve stop and recovery of rebuildable project-local DDC only; no heavy QA jobs requested or launched. Later source edits without render evidence must remain labeled unverified visually. No quality gate relaxation follows from storage limits.

## Milestone1 postfold groom/context review

After reported headroom recovery, inspected actual current hero/head. Continuous groom, absence of old tuft tiles and asymmetric front fold are real local gains. Mantle remains thin and slick/carpet-like; viewer-right fur sheet appears to disappear beneath the bright top shoulder plate. This may be deliberate layer order, but attachment/edge readability remains weak and does not establish clipping-free fit. Routed to artist while garment construction advances. No global artistic pass; final preservation audit remains deferred.

## Isolated glove seam unwrap — first failed sample

Read `unreal/art-studio/source/v5_glove_uv_study.py` and `glove-uv/seam-unwrap-audit.json`; inspected actual palm/dorsal/side checker renders and left island sheet. The study genuinely creates `V5 seam islands`, cuts real edge seams, unwraps/packs, and explicitly wires that UV layer into checker input. It is separate from the main character, which still uses prior projected sample UVs until verified integration.

First audit: right32/left30 seam-connected charts, many one-face scraps; right479/left708 strict-interior overlap raster samples at1024. This fails intended nonoverlap. Source uses barycentric pixel-center samples excluding shared triangle boundaries; it cannot prove absence of subpixel overlap or distortion. Nondegenerate triangle count is zero under its determinant threshold, but key labels area<1e-12 while implementation tests double-area<1e-12 (area<5e-13); clarification routed. Broad palm/dorsal checker coverage is real, while side/web regions have pronounced scale jumps, jagged seam boundaries and remaining stretch. Glove anatomy remains blocky. Failure preserved and correction requested before integration; no production-unwrap claim.

## Isolated UV face-cut repair — rejected

Inspected revised side checker/island sheet and source repair loop. The loop seams every edge of each offending face, producing233+ charts with many one-face scraps and a visible stack of microscopic islands. Zero sampled overlap is a narrow numerical improvement purchased through destructive fragmentation; it is **not a usable unwrap or production milestone**, and side/web checker distortion remains. Do not integrate this result.

Routed alternative criteria: connected anatomical seam regions, coherent palm/dorsal charts, opened finger-side/thumb/tip strips and wrist closure; merge tiny orientation fragments before unwrap rather than cutting individual failing faces. Require meaningful chart topology, usable padding/texel scale, no sampled overlap/degeneration and readable checker across webs/sides. Preserve both first overlapping study and fragmented repair as failures. Main character UV status remains unchanged.

## Stage2 garment and coherent UV retry

Inspected actual garment/cape detail and new palm/side checker/island sheet. Garment has a conspicuous pale triangular strip beside viewer-right tasset (already routed for correction); long skirt panels still read as smooth rubber sheets and cape ornament remains thin printed-looking linework. Construction/material realism remains unpassed.

Read revised unwrap source: per-face overlap surgery removed; adjacency-smoothed major halves and deliberate wrist/fingertip caps genuinely reduce charts to9 per glove. Determinant threshold labeling corrected. However actual audit now reports1697/1813 overlap pixels; checker shows a dense compressed/spiraling patch on middle finger and side-scale jumps. This is a coherent-chart improvement but still a failed unwrap. Routed chart/region-localized continuous finger/web cuts, not another individual-face split. Preserve9-chart failed evidence and keep main-character integration blocked pending better mapping and actual checker.

## Final bounded isolated UV trial and garment correction

Read current MINIMUM_STRETCH/coherent-region source and audit; inspected palm/dorsal/side checkers. Both gloves now19 meaningful charts, smallest281faces, no single-face debris, zero triangles below declared double-area threshold. Severe middle-finger compression visibly improves. Remaining right2/left1 strict-interior overlap samples at1024 and visible seam/scale discontinuities mean **not a clean unwrap or production pass**. This is a useful isolated study; no integration or texture repaint is claimed. Numerical overlap sampling remains approximate and does not establish exact no-overlap even if a later sampled count reaches zero.

Current corrected garment crop no longer shows the pale triangular tasset strip; rigid plate boundaries read more coherently. Plain smooth fabric/material and simplified construction remain below target. Await final coherent main scene views and definitive source freeze for preservation audit; no extra tests requested.

## New cape back-envelope failure — unresolved pending diagnosis

Actual producer audit reports1975/25236 samples forward of body back envelope, minimum−67.99mm: failed. A clear-looking rear image does not close this finding. Independent read-only source review confirms visible MESH children of character root are colliders, excluding cape/mantle-named objects and all curves. Cape seams/hem/stitches already satisfy exclusions; do not broaden exclusions merely to obtain a pass. New worst-sample owner tagging is appropriate for locating offending body geometry.

This ray-envelope check is not exact triangle intersection: remote same-x/z body geometry can affect envelope. Any such explanation requires actual offending points/object evidence and local view/source examination. Preserve failure and verify corrected cage under unchanged scope. The pass threshold is3mm; negative count alone also omits near-positive failures. No source freeze or final preservation audit yet.

## Cape failure diagnosis and audit-mask correction

Independently verified source: `refine_v5_mantle()` creates a hidden68-landmark mantle cage; the interpolated `yoke()` surface becomes `V5 | sewn horseshoe wool yoke`, and groom fibers use that same surface. The renamed backing is therefore the actual mantle support, not body armor. Original substring-based mantle exclusion missed its new name. Exact semantic exclusion restores the declared body-only scope; no actual armor exclusion or geometry correction is claimed.

Preserved diagnosis/failure lives in `milestone-02-clearance-failure/`. Corrected producer audit:25236 body-ray hits, minimum23.486mm, zero negative samples, passing unchanged3mm threshold. This supports sampled cape-vs-body envelope only. Mantle/cape relationship, top attachments, curves, arbitrary triangle intersections and motion remain excluded; this is **an audit-mask naming fix, not a cloth/collision geometry fix**.


## Final frozen review and preservation

Inspected all17 final actual images enumerated in `artifacts/art/last-vigil-v5/techart-delivery-audit.json`:15 at720×920 plus1400×1800 head-detail and garment-detail. Full figure/front/back/side, head/side, palm, clay, garment/cape, mask diagnostics and sword reviewed. Source and scene match producer freeze. Final image hashes are recorded in [QA final check](character-v5-qa-final-check.json).

**Actual gains:** continuous mantle undercoat and authored asymmetric folds replace the prior tuft tiles; garment bindings/panel construction and rigid tasset plates read more coherently; previously observed pale triangular tasset breakthrough absent. **Remaining major quality limits:** mantle still resembles thin carpet/slick fibers over a broad backing rather than irregular plush mass; silhouette/armor remain schematic and smooth; skirt drape is stiff, cape embroidery reads as printed linework; hand anatomy blocky. Close-up also exposes small bright gorget-edge tips and pouch straps extending upward without convincing attachment. Sword remains a simple clean studio prop; this pass does not establish legendary reference-level craft. More pixels reveal defects, not acceptance.

The isolated19-chart UV study meaningfully reduces fragmentation/stretch but still has2R/1L sampled overlaps. It is retained separately and **not integrated/repainted** into the main character, which keeps prior projected glove sample UVs. No clean atlas, final anatomy, production rig or runtime readiness claim.

Static cape negative report was preserved and diagnosed: all1975 negative hits were the named mantle yoke omitted from the old name-based exclusion. Exact semantic mask correction yields25236hits/min23.486mm/zero negative at unchanged3mm threshold. This is an audit correction, not a geometry or simulation fix; all stated scope exclusions remain.

Independent final preservation: **28/28 gameplay source/config/binary hashes unchanged**, **119/119 selected immutable V4 source/scene/evidence hashes unchanged**. Shared evolving docs/status excluded. All17 image hashes and listed source/scene/script hashes match delivery. Storage: **2,692,726,784 allocated bytes under unreal**, **29,303,713,792 bytes free**;10GB ceiling and24GiB reserve respected. No new gameplay tests or FPS evidence; no heavy QA launch.

Frozen source SHA256 `d604904951bb29f5bdbe410c05efabd4431c4ad36afbc8779edc99b30522c3bc`; scene `8f187e663f03ce4e8e07c100265665c22df940651d2800ace27e385fc01ff866`. Main scene: `unreal/art-studio/revision-v5-2026-11-07/last-vigil-v5.blend`; isolated study adjacent as `v5-glove-seam-study.blend`. Actual art evidence: `artifacts/art/last-vigil-v5/`.

Overall **needs-work**. Next art step should address material/garment construction and mantle mass at whole-figure scale, then resolve/repaint the isolated UV study only after remaining overlaps and quality checks. No production cloth motion, rig/deformation, Unreal integration, statistical adaptation, RL or model capabilities added. AI gate remains closed. Final QA report and JSON frozen for checkpoint.
