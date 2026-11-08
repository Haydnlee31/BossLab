# ART-07 / ART-08 — v3 focal surface and material direction

Date: 2026-11-07. Art-director handoff to animation-techart. Owner requests continued development. The approved concept establishes direction only; the actual v2 model remains below that quality. No new image generation, asset downloads, code edits by art-director, gameplay changes or boss AI.

Inputs re-read: project status/execution/decisions/claims; role guidance; `docs/style_bible.md`; `docs/art/character-focal-authoring.md`. Images re-inspected: approved labeled concept and final v2 head, clay_head, palm, clay_palm and hero. Preserve v2 scene and evidence; save v3 separately.

## Observed gap

The corrected v2 helmet has a real eye opening and continuous construction, but its crown silhouette and shading still expose broad polygon strips. The lower face is a bowl-like slab, not a deliberately forged cheek/jaw transition. The eye opening sits beneath a visually over-tall crown. The glove is connected but the palm remains a padded mitten with a broad transverse roll; finger roots lack a convincing knuckle/web progression. Broad metal mottling and flat brown leather do not explain how these objects were made or worn.

The next improvement comes from authored curvature/anatomy and material placement, not more decorative parts. Keep the torso, shoulders, mantle, cape and weapon stable this pass. Their remaining weaknesses stay documented, not disguised with dramatic lighting.

## 1 — smoothly forged helmet fields

Use the prior contour landmarks as shape guides, not hard planar facets. Smoothly interpolate **between** the median keel, cheek break, temple and occiput so the silhouette itself is curved. Merely adding smooth normals to a polygonal outline does not meet the requirement. Preserve distinct construction edges at the brow/eye opening, visor perimeter and hinge; preserve a gentle median keel. Remove hard normal breaks along ordinary interpolated meridians and height bands.

Round the crown's longitudinal termination into a small continuous crest/keel: no broad flat cap, scalloped top or pinched point. Let the forehead slope back, then let the occiput curve down into the nape. Keep overall head bounds and collar placement near v2. A small approximately8mm upward eye-line adjustment is permitted if it visibly reduces the over-tall crown while preserving cranial clearance and chin fit; it is a design adjustment, not mandatory anatomy data.

Lower visor should blend a subtly convex central face into sloped cheek fields and narrower chin. Avoid both extremes: perfectly spherical lower bowl and flat polygon mask. Do not reintroduce a separate raised brow rail. The slit remains a narrow real gap tapering to the temples with dark backing, not a black surface line or gap around the back. Keep thickness readable at perimeter edges without bright trim everywhere.

**Clay acceptance:** same head/headside cameras; continuous reflection/value gradient across ordinary crown and cheek fields, clean curved silhouette, no square bevel patches or hard strip bands. Eye/hinge/visor borders remain crisp enough to explain separate plates. A silhouette comparison should show an authored helmet profile rather than an egg or two bowls. Do not spend a full-body high-resolution render before these crops improve.

## 2 — glove knuckle, web and pad form

Preserve the continuous closed leather base and unequal finger lengths from v2. Remove the single transverse padded roll that crosses the whole palm. Shape a broad shallow central palm hollow, approximately1.5–2mm relative to surrounding pads at current scale; this is local surface relief, not a carved trench. Thenar and hypothenar pads should rise as broad gentle ramps into thumb and little-finger bases, with no spherical lobes. The thumb web is a shallow saddle connecting the palm and index, not a triangular hole or narrow pipe junction.

Stagger MCP/finger roots along an arc. Middle root highest, index slightly lower, ring lower again, little visibly lower; adjust from current source proportions rather than adding four identical cylinders. Web valleys must fall between finger roots and differ subtly in depth; they should not form a straight bar across the palm. Maintain subtle knuckle bulges and tapered finger pads; keep fingertips closed and rounded without bead seams. A restrained relaxed flexion and small finger spread are enough to separate forms. Avoid global smoothing that erases the knuckle/web anatomy into a mitten.

Dorsal plates continue to follow glove forms and overlap at bending joints. Leather must remain visible on palm, webbing, sides and crease gaps. Keep cuff-to-wrist connection plausible; any reshaping must move associated plates as needed rather than leaving penetration or float. Do not infer grip, skinning or motion readiness from this static pose.

**Clay acceptance:** palm and dorsal/side views identify palm hollow, thumb web, staggered knuckles and finger pads without textures. No transverse sausage roll, thumb pearl lobes, disconnected fingertips, flat slab or four equal pipes. Compared with v2, the anatomy should be visibly less padded and more fitted, without becoming emaciated or skeletal.

## 3 — localized authored steel/leather sample

Apply material refinement only to the focal helmet and glove, after improved clay crops. Author UVs and packed, inspectable masks tied to their physical construction. No imported texture library or concept-image projection. Two modest texture sets up to2K each are ample for this sample; use lower sizes if detail holds. Record map dimensions, UV purpose, channel meaning and intended wear causes. Procedural fine grain may support the maps, but cannot be the entire material story.

### Helmet steel

Most base metal should remain stable blue-black/neutral steel. Remove broad high-contrast cloud color variation. Use an authored2–4mm broken rub zone near selected real exposed edges, with interruptions so it is not a uniform white outline. Place darker accumulation in actual visor/hinge recesses and beneath overlaps. A small number of fine scratches may follow a plausible brushing/contact direction; no identical scratch pattern tiled over every surface.

Separate base-color, roughness and height logic. A rubbed region may be slightly brighter and smoother; a recess may be darker and rougher. Do not turn every dark patch into a pit or every scratch into a thick groove. Micro hammering should remain below silhouette scale and be almost absent at thumbnail size. Keep reflective behavior metallic without making a uniformly polished chrome toy.

### Glove leather

Place an actual stitched cuff or side seam following the garment construction, with a narrow folded/seam margin. Stitch scale should be physically plausible: roughly3–5mm spacing and submillimeter thread thickness, varied just enough to avoid a perfect wire fence. Seam geometry or height masks are acceptable; document which. Do not run stitching through plate or finger joints where it would be decorative rather than structural.

Use a restrained polished-contact zone on the thumb/index and finger pads, compression darkening in crease valleys, and small lighter wear on selected seam edges. Do not paint a uniform tan border around every finger. Grain is low contrast and fine; it must not read as stone, scales or cracked desert. Leather remains visibly distinct from metal by diffuse response and roughness. Retain meaningful color/roughness variation even when lighting is held fixed.

**Material acceptance:** show the same focal camera in clay and material, plus a UV/mask view or sheet identifying placement. At medium crop size, material differences read as steel/leather; at full crop, wear has an identifiable contact/seam cause. At thumbnail size, the broad forms remain quiet. No repeated cloud mottling, white outline halo, huge pits or texture used to conceal bad form. Material-off comparison must still retain the corrected anatomy.

## Evidence and handoff

Send a small first set: head/headside and palm/hand in clay. Art-director and QA inspect actual outputs and route specific defects. Then provide matching material crops, mask evidence and one hero/context view only once coherent. Preserve failed probes with revision labels. Record what changed, what was measured, and what remains below target. No expensive full-view polish or garment scope expansion is needed to establish this focal increment.

The acceptance levels remain separate: technical integrity of geometry/maps; visible improvement over v2; reference-quality art approval; rig/deformation/runtime readiness. Passing one does not grant the others. Boss AI remains deferred until all other readiness gates are met.

## First v3 focal review

Inspected actual first v3 head/palm material and clay crops, then clay head-side and dorsal-hand crops. Crown gradients are smoother than v2 and the palm's transverse roll is reduced. Remaining concrete defects: small steps in the upper-crown silhouette, an uneven dark visor-side join rather than a fitted narrow overlap, and repeated notch-like root depressions in the palm clay. Technical artist identified unequal-Z profile interpolation as a curvature problem; requested correction with fitted side overlap. Directed the three root depressions to blend into a broad knuckle arc, not a row of separate notches.

These bounded corrections should precede the localized authored material sample; no broad full-body render or endless smoothing loop is needed. The head still tends toward a rounded bowl and the hand remains simplified. Proceeding to a material sample is not an anatomy/art-quality pass, and the retained clay views must remain visible so textures do not conceal the remaining form gap.

## Second v3 focal review

Inspected actual updated head, headside, clay_headside, palm and clay_palm crops. The crown outline is smoother and the visor-side overlap is visibly narrower and fitted; the prior ragged side sliver is no longer apparent in these views. Root notch transitions are substantially softened. The helmet remains broad and bowl-like, and the palm remains simplified and padded, so neither region receives an anatomy or overall art pass.

Proceed with the bounded UV material sample. Current material crops are too quiet: helmet steel is nearly uniformly dark and polished, and glove leather lacks readable seam/contact structure. The artist identified scratches placed on a rear UV sector and stitches hidden by the cuff. Moving these onto visible, physically plausible regions is necessary; map existence alone is not material acceptance. Keep lighting fixed and retain readable steel reflections/midtones. Use sparse directional scratches, interrupted selected-edge rub, and recess accumulation without a white outline or further global darkening. Show the side glove seam without floating thread or armor penetration. Request actual UV/mask sheet plus matching material crop.

## Placement-corrected material sample review

Inspected actual latest head and palm crops, UV visor/glove layout PNGs, and the steel/leather placement-mask PNGs under `unreal/art-studio/revision-v3-2026-11-07/textures`. Steel midtones and sparse frontal scratches are now visible. Palm stitching appears as a small dotted construction line. This is demonstrable UV-placed material work, not only a map-generation claim. The disclosed cylindrical steel UVs and overlapping projected dorsal glove UVs are sample layouts, not a production atlas.

The masks remain simple: interrupted lower rim rub/recess strip and a few directional steel scratches; a broad leather contact region, curved compression line and side stitch line. Visible material quality remains limited. The palm still shows a broad straight dark band rather than convincingly localized compression, and stitches lack a clearly resolved seam margin. Requested one bounded correction to soften/break that band into shorter articulated creases and seat the stitch line in a subtle seam margin. Do not amplify global mottling, darken the whole material again, or add ornament. Overall art acceptance remains pending.

## Final v3 independent review

Reviewed the final eleven-view set across material, clay, diagnostic masks and hero context. The final diagnostic head explicitly shows rim/recess and scratch placement on the actual mesh; the palm diagnostic shows contact, short compression and stitch placement. These prove localized material assignment. They do not prove convincing leather or production-ready UVs. The final small leather correction is too subtle in the material crop to claim a meaningful visual quality gain; the lower-palm horizontal ledge remains visible in clay and material.

**Delivered visual improvements:** smoother crown fields and outline, cleaner fitted visor-side overlap, softened palm-root notches, readable steel midtones, sparse placed scratches, visible small stitch line and inspectable wear masks.

**Still below target:** helmet retains rounded cap/bowl proportions and broad simplified face fields; palm/thumb and knuckles lack fitted anatomical definition, with a straight lower-palm ledge. Leather is too uniformly smooth. At hero scale the costume remains a clean procedural mannequin, with generic repeated plate forms, sparse brush-like mantle and limited material storytelling. This is an improved studio iteration, not reference-quality acceptance, rig/deformation validation or runtime integration. The owner's earlier approval remains approval of concept direction only.

**Next highest-impact focused task:** replace the glove's broad palm slab with a landmark-authored palm-to-MCP surface: a curved staggered knuckle root arc, shallow central hollow, broad thenar saddle and taper into wrist; fit dorsal shells to that surface. Require front/palm/side clay at identical framing before further texture work. Preserve actual seam locations, then build separate nonoverlapping palm/dorsal/side UV islands and paint short compression/contact regions against those landmarks. This targets the visible ledge and padded anatomy instead of hiding them with noise. Helmet redesign toward a narrower authored brow/cheek profile remains an explicit subsequent form task. No further ornament or material amplification is warranted on the current slab-like forms.

Review hashes are recorded in `docs/art/character-v3-direction-review-hashes.json`. No new gameplay tests, cloth motion, grip tests, runtime integration or AI work were performed by this art review.
