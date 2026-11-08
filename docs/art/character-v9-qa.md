# Character V9 independent QA

**Pending actual drape review; overall art gate remains needs work.** Scope: bounded offline cloth-solver study replacing rigid front garment panels, preserving V8 proportions. Simulation execution alone does not establish good cloth, stability, collision coverage or production readiness.

Baseline snapshot: 86 immutable V8 files; 28/28 game files match. See [baseline](character-v9-qa-baseline.json).

Acceptance: compare early and settled actual clay/material views with unchanged framing; require visible gravity-dependent folds, supported waistband, plausible hem and no new plate/leg/boot penetration in sampled views. Inspect source frame range, pinning, collider scope and actual solver outputs. Distinguish static drape from animated combat cloth, and shape quality from numeric stability. Preserve failures. Final audit only after artist freeze; no gameplay tests, AI, rig or runtime claims.

## First solver trial: failed

Independently inspected preserved iteration-01 frame 1/25/100 front clay and frame 100 side. The hem rises and twists by frame 25; frame 100 is crushed/bunched against the tasset stack rather than hanging. Audit reports maximum edge ratio 7.03323 and maximum last-ten-frame per-step movement 25.987 mm despite finite vertices. Neither solver completion nor finite geometry implies stability.

Proposed fixed diagnostic thresholds before subsequent review: finite every sampled frame; maximum structural edge stretch at most 1.10 through the run; last-ten-frame maximum per-frame vertex movement at most 1 mm before calling it settled, with endpoint drift and pinned-row error reported. These are study heuristics, not calibrated textile properties. Successful body-only proxy isolation would diagnose solver contact behavior; it would not certify cloth against final rigid tassets/leg geometry. Final visible fit/contact scope must remain explicit.

## Body-proxy isolation

Second actual frame100 front/side is stable-looking but remains flat hanging ribbons; no visual drape-quality pass. Reported stretch1.01322 and last-ten maximum step0.719mm meet fixed study gates. Tasset collision is disabled in solver; actual plates remain visible. Clearance code independently read: closed ellipsoid body proxies use nearest-surface normal signed distance; cloth mid-surface vertices cast y-axis rays against actual tasset backs. Ray-hit gaps do not cover missed silhouettes, arbitrary edge/triangle intersections, final subdivision/solidify shell or motion. This is deliberately scoped contact evidence, not a global certificate.

Flagged endpoint displacement as frame1→100 total deformation rather than settling drift. Pin error compares world candidate positions against local solver targets; must assert identity or transform targets for reliable general measurement. Next trial should preserve thresholds and demonstrate actual body-contact shaping, without adding fake procedural wrinkles to claim solver benefit.

## Cloth branch closed as rejected study; neutral handoff

Later tailored contact trials failed stability, including the final closed-tasset-proxy run reported at 1.7598 maximum stretch and 12.4 mm final per-frame motion. Earlier stable partial remains explicitly unapproved and ribbon-like; it is not evidence that the tailored variant works. Mail fitting and proxy changes were real study changes, not a claim that all armor layers remained untouched. Failed cloth is not selected as the working outfit.

Independently parsed all four neutral OBJ files: finite coordinates and valid vertex indices, hashes matching producer; 42 attachment indices/rest coordinates match the rest-panel OBJ within 4.34e-10 m and targets are finite. [Independent handoff check](character-v9-qa-handoff-check.json). Files supply local portable geometry and virtual supports, not imported application constraints, physical textile calibration, finished flat cutting patterns, UV guarantees or a successful platform migration. No destination DCC import was performed. Separate V9 armor candidate derives from preserved V8 and will be reviewed independently; it must not inherit failed cloth claims.
