# Character V10 independent QA

**Overall reference likeness remains needs work.** Separate V10 branch must preserve accepted local proportion/shoulder gains and leave rejected V9 cloth quarantined. Judge actual matched clay/material renders, not geometry counts, simulation execution or similarity-score proxies.

Baseline: 68 immutable V9-armor files snapshotted, game 28/28 unchanged. [Baseline JSON](character-v10-qa-baseline.json). No heavy jobs from QA.

Review priorities: major silhouette and layering against owner references; convincing garment support, hem weight and varied folds; readable material hierarchy and wear at plausible locations; no new plate/cloth attachment regressions. Keep original design identity without claiming reference-level results. Final source/evidence preservation and resource audit only at freeze. No new AI, gameplay, rig, runtime cloth or FPS evidence.

## First bare collar probe: needs correction

Actual clay_shoulder and clay_headside inspected. Three smooth concentric shelves read as a stepped solid ring, not padded sewn cloth. The lower rim bridges above the shoulder with a broad dark gap; the front end looks like a flat cut slab. Require seated underside/contact landmarks plus unequal channel compression and sag before groom/material can obscure the construction. No new armor break apparent in these views. The reported .461m new control span versus .625m removed-geometry span compares different geometry scopes; it is not proof of identical evaluated shoulder envelope.

## Third bare collar review

Current clay_shoulder, clay_headside and hero show the stepped shelves removed and the lower edge seated more closely around the shoulder cap. The compact continuous pad is a useful local improvement and preserves the lean figure/overlapping armor. It can proceed to sparse rim/clasp and same-light material trials. Front ends remain simple broad pads, with a sharp side-front crease; a dense fur carpet must not hide those limits. This is not whole-character realism acceptance.

## Collar trim and selective finish sample

Actual current hero/head/shoulder reviewed. Compact asymmetric collar and single clasp improve neck layering; darker crown/fauld/forearm establish clearer value hierarchy. Still smooth molded surfaces, broad blobby shoulder highlights and parallel fringe/loop strands rather than convincing irregular fur. No gross new sampled attachment regression. Hero now appears to contain narrower/tapered hanging panels; final coherent views/source must identify the final skirt version. Static authored skirt should be evaluated for support, hem weight and folds, not credited as cloth simulation or accepted merely because narrower.

## Final candidate review and scope

Current coherent low-resolution set shows broad unequal static skirt folds and reduced forward projection. Corrected belt support is tucked behind the belt; no gross new plate breakthrough appears in garment/side/back views. The skirt still reads as stiff leather-like panels, not convincing textile drape. It is authored static geometry, not a successful replacement cloth solve. Failed V9 solver candidates remain excluded.

Final shoulder-detail reveals real localized mapped finish and weave at high resolution, but broad processed-looking patches, smooth simplified forms and repeating bent fringe fibers remain. The compact collar and darker selective armor improve layering/value hierarchy without establishing reference-level likeness. The mask_head/mask_shoulder renders show actual placement. Source explicitly wires V7 forged UV or V10 cylindrical plate UV into color/property/mask textures; packed property red/green channels feed roughness/metallic, and mask-modulated grain feeds bump. Map presence and wiring are technical evidence, not production UV or finish-quality certification.

Final view accounting excludes earlier bare clay_headside: it belongs to the earlier collar iteration, not the coherent delivery set. Geometry preservation hashes intentionally omit materials/UV to permit declared finish changes. Garment y-ray envelopes are sampled static body-front/tasset-back checks; they do not test all triangle intersections, cloth dynamics or a body rig. The initial six tasset samples per side at approximately1.6mm were preserved and corrected by moving hidden cloth back3mm, rather than weakening the3mm gate. Initial strap endpoint gap caveat is superseded by the corrected four endpoint samples near1.5mm, still not full strap-contact proof.


Final 1400×1800 shoulder-detail and garment-detail reinspected after the final render completed. Garment folds are broader and less projected, but panels remain thick/plain. An irregular dark patch and exposed layer edges remain on the viewer-right belt near the pouch rod. Hash-identical belt geometry alone cannot diagnose its shading/contact cause; retain as an unresolved visual limitation, not a clean global fit claim. Shoulder fringe still repeats bent fibers, and the metal pattern remains processed-looking. Overall verdict remains **needs work**, with local collar/finish/static-garment progress. Final delivery contains 11 material/clay views plus two mask diagnostics, not 13 beauty views.


## Frozen independent integrity check

68/68 immutable V9-armor files and28/28 game files remain unchanged. All manifest source/script/scene/report/index files,13 final views and12 texture files match hashes. [Final check](character-v10-qa-final-check.json). Source `f49bfcc8136e9f4fb85c5bda86e864f6069b616d006c855df9acba32af0c71ec`; scene `c91477d262097a45fc5198c3bc0a808783594505f89f8fd6e5a3027454c9cf66`. Allocated unreal storage 4128923648 bytes; free 27232702464 bytes, within10GB/24GiB limits at check time.

Producer saved-scene evidence:327 retained visible geometry objects unchanged, protected camera/root/sword signatures equal. Collar evaluated support-only width .54625→.34096m, excluding groom; strap four endpoint nearest distances1.500mm. Body/mail minimum3.877mm, tasset minimum5.130mm with zero sampled distances below3mm. These are scoped static checks, not complete contact certification. Final339renderableobjects/430,752vertices/813,036triangles/37packedimages describe offline geometry, not runtime performance.

New cylindrical projection audit discloses740/3044 degenerate cap triangles; prior visor/glove limitations remain. No clean unwrap, rig, simulation, game integration or artistic acceptance claim. **Boss AI gate remains closed.**
