# V6: fitted cuirass and surface-attached mantle

Status: final static evidence frozen; overall artistic reference target remains unmet. Separate editable static studio revision; V5 and the playable game are preserved. No rigging, cloth simulation, runtime integration, gameplay changes or boss AI. Artistic reference target remains unmet.

## Implemented construction

The mantle backing is tucked inside its intended pelt edge. Fiber roots and guide paths now use the actual surface tangent/across/normal frame, replacing world-Z offsets and planar extrapolation. Unequal front/outer/rear guides curve beyond the hem and drop under gravity as authored static curves. Existing 18,000 short and 4,800 long strands are redistributed, not increased. Shortening the backing exposed a shoulder-cap oval in the first draft; the fitted surface now uses the actual evaluated upper shoulder plate to maintain padded clearance. Both backing and groom share that fitted surface. Longer grouped locks visibly change the edge, but the mass still reads broad and combed, not convincing reference fur.

The old rounded cone is replaced by a fitted central breastplate and two separately returned flank fields. Broad fields meet a shallow central keel, with a concave upper opening and rounded lower return. The existing seven-stud arch follows the new front surface. Side retention tabs wrap toward the returned fields. The old mantle tether is separated from the neck border, fixing the initial crossed-line artifact. This is a visible construction change, not merely ornament.

Camera-ray diagnosis located a remaining pale waist crescent on the original upper fauld's solid horizontal cap. That loft is converted to a thin hollow plate by removing the broad end-cap polygons and adding 2 mm thickness; outer shape is retained. The diagnostic before-image/report remains archived.

## Scoped material sample

A helper initially inherited the base script's global steel instead of the revised local material. Explicit material arguments correct that scope error. Three original 512×512 panel-space construction masks are packed and explicitly bound to `V6 panel UV`: red interrupted rim handling, green narrow recess roughness, blue side-fastener contact. Stable base color and restrained fine forging normal preserve broad plate fields. Actual mask-on-mesh views and read-back UV/material audit accompany the material render. Visual effect is subtle; no production-painted-atlas or reference-realism claim.

## Deferred work

No glove UV work was executed in V6. The V5 isolated 19-island study still has 2/1 sampled overlap pixels and remains unintegrated. The main glove retains the disclosed projected sample UV with dorsal overlap and side compression. Finishing a useful unwrap/repaint remains open; it was explicitly deferred to prioritize whole-figure construction.

Helmet, padded glove anatomy, pale/simple shoulder plates, broad smooth steel and printed-looking cape decoration remain below target. High-resolution head inspection also exposes repeated arcing fine fibers and broad visible backing between long locks; these remain grooming-quality defects, not a realistic-fur pass. Mantle/cloth modifications are static and invalidate earlier motion-cache applicability. Source geometry and sampled body-envelope clearance do not validate animation or all garment intersections.

## Failures and preservation

Milestones retain first normal-frame groom, initial cuirass, corrected pre-material form and material trial. A NumPy/Vector mismatch stopped one draft before save; its source/log/receipt are retained. No thresholds were lowered, no assets downloaded, no global files altered, and no persistent jobs added. CPU foreground jobs enforce 10 GB unreal storage, 24 GiB free reserve and 20-minute deadline.

Final dimensions, hashes, geometry, map wiring, process exits and storage are recorded in `artifacts/art/last-vigil-v6/techart-delivery-audit.json`. The final gallery links the parent-owned matched V5/V6 comparison; the approved concept is separately labeled NOT BUILT.

Final geometry: 344 renderable objects, 1059336 evaluated vertices, 1924004 triangles. Eighteen actual views: sixteen 720×920/16-sample and two distinct 1400×1800/48-sample details, all from the saved final geometry. Exact image/source/scene hashes are in the delivery audit.

Final saved-scene body-envelope readback: 24,982 ray-hit samples, minimum 34.584 mm, zero negative samples. Earlier pre-final audit had 24,976; the final report uses the actual reloaded final scene result, not that stale count. The scope excludes mantle/yoke, top attachment zone, curves and arbitrary triangle intersections; it is neither animation nor complete collision validation.
