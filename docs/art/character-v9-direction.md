# V9 — pattern and drape authoring pivot

Preserve the lean V8 proportions, armor, sword, materials and matched cameras. The owner asks for continued development and alternatives to an unproductive refinement loop. This increment changes the garment construction method: actual cloth patterns, constrained attachment and collision-driven settling in Blender, followed by inspection of the resulting geometry. No new platform installation, material pass, AI, rig or game integration is implied.

## Audit of the previous loop

Earlier revisions improved regional fit and several real construction defects, but the skirt repeatedly remained two thick, straight boards projecting ahead of the legs. Analytic control rows and added seam details did not solve the gravity/attachment relationship. More periodic folds, noise or stitches would repeat that failure. V8's leaner proportions are useful and must remain stable; V9 succeeds only if actual front and side silhouettes demonstrate a different, plausible hanging garment.

## Pattern and attachment target

Use two separate woven-cloth panels, with grain predominantly vertical. Their upper edges attach beneath the belt, not to the full thigh or all perimeter vertices. Introduce modest top-edge gathering ease (initial trial 5–8%) so support creates a few unequal folds. Keep an open center slit and subtly unequal lower hems, roughly 15–25 mm difference. Lower outer edges should converge slightly toward the knee instead of forming an outward rectangular apron. These values are reversible art trials, not measurements extracted from the concept.

Each panel should hang from the waist, touch the upper thigh where supported, and release into a loose lower span. In side view the hem must stop projecting forward as a rigid board. Avoid tight vacuum-fitting to the leg, deep paper accordion folds and rigidly mirrored waves. The hem may turn gently; thickness and binding follow the settled sheet rather than creating its shape.

Tassets are rigid separate plates. Keep their planes and mounting points intact. Cloth settles behind them with collision clearance; do not conform metal to fabric wrinkles. The first visual trial should show both the armor relationship and the cloth itself. Existing seams/binding must be rebuilt along the final evaluated sheet, not left at the old analytical outline.

## Cheap visual gate before detail work

Render matched low-cost clay front and side after a bounded settling trial, with armor visible. If hidden support or collision is ambiguous, add an isolated cloth-plus-body view. Review these actual images before thickness, seam details or higher-resolution beauty output.

Acceptance requires visibly reduced rigid forward projection, a readable belt-to-thigh load path, unequal broad folds, an open split and plausible hem clearance. Reject exposed intersections, cloth crossing tassets, upside-down/inverted sections, contact hovering and an unchanged board silhouette despite a technically completed simulation. Preserve the failed trial if any and record parameters/frame/sample evidence truthfully.

This is a static garment authoring experiment. A settled simulation does not establish a production cloth rig, deformation quality, animation stability, Unreal integration or runtime performance. Overall concept fidelity remains needs-work until actual evidence supports a narrower claim.

## First actual solve: rejected

Inspected frame-001 clay side, frame-100 clay front and side, and the garment material crop. The final cloth tangles across the front of rigid tassets and bunches into short flaps high on the thigh. It does not form the requested hanging panel. Solver completion is not a design pass, and this result is not yet a useful replacement for the prior board-like garment.

Directed a setup-first diagnostic: isolate a panel; establish that its initial sheet lies behind the tassets and outside the thigh collider, with collision offsets smaller than the actual available gap; verify normals and transforms. Establish a plain stable hang with zero gathering before restoring modest ease. Do not add seams or conceal the failed solve. The desired lower edge remains near the top of the knee, with a loose span below the rigid plates and no fabric crossing onto their visible faces.

## Second actual solve: stable but visually too flat

Inspected the updated frame-100 clay front/side and garment crop after removing tasset collision from the solve while keeping plates visible and rigid. The tangling is gone and forward projection is reduced. Panels remain nearly flat hanging ribbons. Artist reports stable strain and positive plate-back clearance, but a 41–44 mm gap to body proxies; those solver figures do not establish the intended supported garment.

Directed the measured belt-underpin trial inward toward the actual attachment surface, retaining verified plate clearance. Keep current length and unequal hems. Seek upper-thigh support followed by a free lower span before deciding whether additional top ease is needed. No seam/detail work yet. This is a real setup improvement, not an artistic acceptance.

## Third attachment trial: mail-layer defect exposed

Actual garment crop shows vertical strips of chain mail penetrating the newly seated panels. The original underlayer needs fitting to the thigh envelope; moving the cloth forward again would conceal the construction defect and undo the attachment improvement. Agreed an actual mail-layer correction plus coverage proxy before another solve. The plate faces remain rigid. Once layer fit is correct, trial total gathering ease around 12–15% with the same pin span and current hem length, seeking broad support-driven folds rather than accordion ruffles. Current panels remain too planar for an artistic pass.

## Fourth solve: layer fit improves, pattern still fails visually

Inspected actual garment and frame-100 clay front/side. Mail no longer crosses the panels, and shallow folds are visible. The near-parallel rectangular cut still dominates; physics alone cannot make a poorly tailored pattern attractive. Directed a substantive cut revision instead of further ease increments: lower width about25% narrower by bringing the outer edge inward below the plates, leaving the slit edge mostly vertical; outer lower corner about30–40mm higher with a curved/sloping hem; other panel approximately15–20mm shorter overall. Keep waist span and inner-edge length. This is a new physical cut to solve, not deformation noise or applied fold ornament.

Side view also reveals a sizable plate-back gap after the cloth moved inward. Rigid armor must retain a credible mounting relationship; flag unsupported plate spacing rather than bending the metal to fit wrinkles.

## Curved attachment trial rejected

The artist reports that the tailored cut combined with a25mm curved pin return became unstable (3.24× maximum strain,15mm step motion). This does not validate the pattern or invalidate cloth authoring in general: two variables changed. Directed restoring the measured stable straight attachment while retaining the new cut, with no further pin movement before contact-clearance checks. Preserve the failed trial. The belt-arc suggestion was conditional on fit and must not override measured collision constraints. The next review isolates whether the actual tailored cut improves silhouette under the proven attachment.

## Final independent verdict: replacement not accepted

The subsequent layered-collider and closed-proxy trials did not satisfy stability gates. Inspected the last root garment crop and frame-200 clay side: one panel curls upward into a pronounced horizontal bunch beneath the plate while the other hangs longer. This is visibly a failed result, not intentional asymmetry or attractive drape. Artist-reported final structural trial figures (1.7598 maximum strain,12.4mm step motion,61.9mm net drift) also reject a settled-cloth claim.

Iteration04 remains the best stable partial experiment: cleaner mail layering and broad shallow folds, but nearly rectangular ribbons and no accepted garment silhouette. Later tailored-cut trials must not be represented as a successful replacement. Preserve V8 as the working art checkpoint; V9 is an unsuccessful replacement experiment with reusable patterns, colliders, pin data and documented failures. No new seams, material polish or runtime integration should conceal this outcome.

The method pivot was real: physical cut patterns, measured layered contacts, simulated progression and isolated failed trials. The desired visual outcome was not achieved. Moving the neutral pattern/body data to another authoring environment may assist interactive fitting, but a different tool alone cannot prove garment construction quality; the same front/side visual and layer-clearance gates still apply.
