# V12 — matching-view geometry-first upper-body study

New owner-approved workflow, not a fourth V11 correction. Preserve V10 and all V11 failures. One chest–shoulder section: build coherent untextured geometry from shared front/side/back design, then inspect a three-quarter view and actual clay turntable before any projection. Initial build plus at most two geometry corrections. No physics, material polish, whole-character work or AI.

## Actual design artifacts

- `artifacts/art/last-vigil-v12/design/upper-body-design.svg`: authored visual front/side/back schematic and three-quarter ring construction, with dimensional annotations.
- `artifacts/art/last-vigil-v12/design/shared-landmarks.json`: common millimetre landmarks used by every view.

This is an original geometric design guide, not source-image tracing, an existing model or measured anatomy. Coordinates: X left/right, Y anterior negative, Z upward from waist. Widths/depths are outer design envelopes, not rigid instructions to intersect parts.

## Shared construction

Chest440mm wide ×260mm deep atZ240; waist330×210 atZ0. Upper bridge narrows toward neck atZ390. Cuirass front has a sternum keel and side returns; rear is a continuous convex shell with centre closure, not a disconnected slab. Remove/open arm sockets aboveZ240 and connect bridge/back around them. Do not retain a full ellipse through arm volumes merely because the section table lists an ellipse envelope.

Arm centres X±245,Y0,Z310; hidden root half-width56 and half-depth75. The initial sheet draft used65mm half-width; the artist caught that this plus8mm clearance and3mm sheet exceeded the315mm shoulder half-span. Corrected to56mm before the first build, retaining the lean630mm total silhouette. Sheet/JSON now agree on these values. These dimensions define a hidden support envelope, not a separate visible sphere.

Gorget is a hollow oval with140×150mm opening, base flange210×210, baseZ375 and rimZ455. Seat it on the neckline bridge; preserve a real opening and coherent rear return. No capped cylinder or floating ring.

Each shoulder cup wraps around the arm root from anterior to lateral to posterior. Three lower lames end atZ270/240/210 with approximately12mm hidden overlap,3mm shell thickness and initial8mm body clearance. Actual fit wins over nominal dimensions. Keep medial armpit clearance and the continuous lean outer arc; do not create free-floating cutout plates or disconnected back supports.

## Visual gate and correction budget

Render actual clay front, side, back and three-quarter plus an untextured turntable exposing all sides. Diagnostic geometry must show neck opening, arm roots, rear closure and overlapping plates. Reject support penetration, disconnected rear pieces, hovering collar, shallow extruded cutouts, bulky shoulder growth and front-only silhouette success. Numeric clearance/topology checks support this review but cannot replace it.

Review initial actual geometry and allow at most two concrete corrections targeting the largest visible construction failure. Stop at that cap if the base remains incoherent. No projection until the actual multiangle clay result succeeds; no implied production rig or runtime readiness even if this local base passes.

## Initial actual geometry review

Independently inspected all five clay views: front, side, back, three-quarter and neck. Torso/back/arm volume and hollow neck are now coherent real depth, a meaningful construction change from V11's projected cards. Lower lame overlap regions show obvious noisy coplanar-surface conflict. Approved correction1: recessed hidden upper overlap tongues, maintaining exposed radii and checking actual shell/body clearance; adjust cap seating within the lean envelope.

A further visible issue is the cap's open upper/medial edge reading as a detached upright shield. A short upper return toward the shoulder root can improve seating while retaining the open arm socket; do not cap the armhole or create another intersecting backing. Generic chest and gorget shapes remain below reference quality. No projection is approved by this initial review; corrected clay and turntable must be evaluated first.

The SVG is authored and structurally checked but was not raster-previewed: local thumbnail generation failed and browser/native rendering was unavailable. Actual Blender clay views, not an unverified SVG preview, are the visual evidence for the geometry decisions above.

## Final construction correction and sampled turntable gate

Attempt02 removed visible coplanar noise, but the artist's stronger parity audit detected lower-lame overlap containment. The final permitted correction recessed each hidden tongue across the full overlap before its transition below the preceding hem. Independently inspected all five attempt03 stills, then six actual orbit samples003/009/015/021/027/033 spanning front, both sides and rear.

**Narrow structural gate: sufficient for a bounded UV/material study.** Continuous cuirass/rear volume, seated hollow gorget, arm clearance and layered shoulder shells remain coherent through these sampled angles; no conspicuous new break appears. This is a coarse construction base, not reference-quality sculpting, full animation clearance or owner artistic approval. Six samples are not an all-frame playback claim. No fourth geometry candidate is allowed.

Any next surface test must preserve this geometry and use clean UVs with a checker diagnostic. A flat original generated metal image, if used, must be labeled generated albedo with derived roughness, not a measured PBR scan or projection of the lit concept. Inspect front/side/back under multiple lights before expansion. No source-image rivets/fur/shadows may be presented as modeled detail.

## Generated texture sample and first mapping review

After the structural gate, one original built-in image generation produced a flat aged-steel color texture. Exact prompt, source provenance, hash and limitations are stored in `artifacts/art/last-vigil-v12/texture-study/`. Source image inspection found no conspicuous directional highlight or cast shadow. It is generated albedo; luminance-derived roughness is an artistic estimate, not measured PBR. No normal or displacement was inferred.

Inspected actual material three-quarter, side, back, alternate-light three-quarter and1400px detail. Fine directional variation is visible across real volume and changes light response under the second illumination. However, obvious rectangular/triangular chart discontinuities create patchwork on chest and cups. A zero-overlap audit is not clean visual mapping. Agreed ONE bounded UV-only correction: coherent visible panel/cup islands, seams at real rear/underarm/plate boundaries, separate hidden rim charts. Preserve geometry and generated source; no regeneration or bump to hide the defect.

## Final UV-corrected material review

Inspected final three-quarter, alternate-light three-quarter, back and1400px detail after the single UV continuity correction. Prominent rectangular/triangular patchwork discontinuities are gone in these views. Texture flow now follows coherent real surfaces and the alternate illumination changes the shading rather than revealing a front-image illusion. This is a useful foundation/method gain over V11 and the first automatic mapping test.

The artistic target remains unmet: the base is generic smooth armor with uniform aged finish, not the reference's designed construction, layered textile silhouette or craftsmanship. The artist reports residual overlap pixels despite fewer coherent charts; therefore no clean production-UV or baking-readiness pass. Generated albedo and illustrative derived roughness remain explicitly distinct from measured PBR. No further correction is requested within this bounded increment.

Final scope: three geometry attempts total, one original image generation, one UV continuity correction, no physics, no concept projection, no whole-character replacement and no game/AI integration. Preserve the clay base and all rejected mapping/geometry evidence.
