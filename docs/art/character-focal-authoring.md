# ART-05 — fitted helmet and coherent glove authoring

Date: 2026-11-07. Owner: art-director. Implementer: animation-techart. Inputs: approved generated concept at `artifacts/art/last-vigil-concept-2026-11-07/concept-target-not-built.png`; actual fifth-v2 scene/views and `unreal/art-studio/source/last_vigil_v2.py`; `docs/style_bible.md`. The concept is direction only. This task must produce actual editable geometry and actual focal renders. No more image generation, no boss AI, no game integration. Keep all other costume, weapon, camera and lighting work stable.

## Purpose and acceptance

Replace two remaining primitive assemblies with surfaces that describe construction around a human body. This is not another trim/rivet pass. A grey-material crop should read as a fitted forged helmet and a human leather glove before material detail. Preserve the old scene and fifth-v2 evidence, then save the focal revision separately or as a recorded new iteration.

All ratios and dimensions below are original art targets chosen for the existing approximately1.9m studio figure. They are not museum measurements or combat constraints. Adjust within a few millimeters to avoid collisions and preserve the current head/wrist placement; report material deviations.

## A — integrated helmet and neck

### Primary form

Target maximum temple width approximately210–220mm; top-to-chin approximately235–250mm. Keep cranial clearance, but remove the egg-shaped continuous round front. Make the upper shell a deliberately shaped volume with a center ridge, broad brow planes, narrower cheeks and protective nape. The ridge must be in the shell's vertices, not a separate strip or curve attached above a sphere.

Build horizontal sections from named contour landmarks rather than a circular/elliptic ring. A useful normalized section, viewed from above with front=-Y, has front median `(0,-1.00)`, paired cheek landmarks `(±0.65,-0.82)`, front temples `(±0.96,-0.30)`, side temples `(±1.00,0.10)`, occiput `(±0.75,0.75)` and rear median `(0,1.00)`. Interpolate each segment with enough vertices to avoid a decagon silhouette, but retain a controlled normal/curvature break at cheek and temple. No hard faceting across the entire skull.

Use these section proportions as the shape guide, relative to the temple section:

| Section | Half-width | Front depth | Rear depth | Shape purpose |
|---|---:|---:|---:|---|
| Chin / lowest visor | 0.68–0.72 | 0.76 | n/a | Narrow jaw, tucked into collar |
| Cheek / mouth | 0.88–0.92 | 1.00 | n/a | Two broad sloping cheek planes, slight central keel |
| Eye / temple | 1.00 | 0.93 | 1.00 | Widest face fit, defined temple pivot zone |
| Brow / low forehead | 0.95–0.98 | 0.98 | 0.96 | Brow grows from forehead, not a free rail |
| Upper forehead | 0.83–0.88 | 0.80 | 0.85 | Roof begins narrowing; no sudden spherical bulge |
| Crown shoulders | 0.48–0.58 | 0.50 | 0.57 | Flow into longitudinal ridge |
| Crown ridge | 0.08–0.15 | 0.25 | 0.32 | Narrow continuous rounded keel, not a pinched point |

Shape the top longitudinally: forehead slopes back into crown, crown flows into occiput. A close side silhouette should have a clear brow/forehead/nape relationship. Avoid adding a tall crest. Use short support loops around intentional edges, with subdivision or weighted normals only where continuity is intended.

### Eye opening and plate connection

Upper brow and lower visor are separate plate surfaces with a real4–5mm opening between them. It should be black because a dark backing is recessed at least5mm, not because a black tube is painted on the front. Opening tapers toward temples; do not extend it fully around the head. Keep the upper lip only8–12mm forward of the eye plane, seated in the shell. Remove the existing projected brow curve and all duplicate rail-like fittings.

Use approximately2–3mm plate thickness and a0.8–1.2mm edge radius. The lower visor should meet cheek-side hinges without penetrating the skull or creating an exposed gap. Vent holes may be represented as shallow recesses for this pass; do not introduce many new decorative pieces. If topology cannot support actual small vents cleanly within scope, omit them rather than add floating black strokes.

### Neck / gorget overlap

Shape a short, flared gorget around the neck base with a broad chestward skirt and a narrower neck opening. The visor chin seats approximately3–6mm behind the protective lip in the rest pose, with a visible dark separation. It must not look welded into the gorget or float on a tall bright neck tube. Keep side neck clearance approximately5–10mm and the nape protected without projecting a rectangular flap beside the head. No movement acceptance is claimed until pose testing; this is static fit.

### Head render checks

1. Same three-quarter armor crop as fifth-v2, plus a close side crop.
2. Eye slit is negative space; no detached brow rail or visible cap crossing the gap.
3. Brow/cheek shape is legible under a plain rough grey material; not a round egg with a bolt-on wedge.
4. Crown ridge grows from shell; no scalloped top, pinched point, duplicate strip or separated normals.
5. Chin/gorget layer order and side clearance are readable; no visible penetration.

## B — coherent glove / gauntlet

### Underlying volume

Keep current wrist attachment and hand orientation. Model a continuous leather glove volume: wrist narrows into a palm with an arched knuckle line, asymmetric thenar/thumb pad, flatter dorsal face and softly convex palm. The hand cannot be a sphere hidden behind a rectangular plate. Use approximately80–85mm maximum palm width,80–90mm wrist-to-knuckle length,25–30mm palm thickness and a narrower wrist. Interpret dimensions in the model's local hand axes, not blindly in world Z.

The thumb begins near the wrist-side third of the palm and broadens into a thenar web before narrowing; it should not attach as a pipe at the outer edge. Keep a visible curved web between thumb and index. Use one continuous palm/thumb/web mesh or a properly joined/remeshed and smoothed volume with controlled density; overlapping spheres are not the finished surface.

Finger roots should share the palm surface with shallow webs, not hang from its lower rectangular edge. Use lengths index:middle:ring:little =0.87:1.00:0.94:0.74; choose a middle finger length approximately75–80mm. Stagger root/knuckle positions on an arc, with little knuckle recessed about6–8mm and index about3–4mm relative to middle. Width varies: middle/index widest, little approximately75% of middle. Taper the finger width/thickness by roughly25% from first phalanx to tip. Add a small joint bulge rather than uniform cylinder radius. Tips are soft flattened pads integrated into the surface, not spheres or caps with visible seams.

Use gentle relaxed finger flexion toward the palm: approximately15–20° at MCP,20–30° at PIP and10–15° at DIP, with some finger-to-finger variation. This is a static relaxed pose, not grip validation. If current orientation makes these numbers ambiguous, preserve a clear natural arc and report the local axes. Avoid identical parallel finger positions. Thumb should oppose the palm with two visible segments and a softened rounded pad.

### Plate construction

The leather underglove must be visible around side edges, palm, webs and joint creases. Fit a curved dorsal metacarpal plate over the hand rather than a rectangular slab. Let its distal edge follow the knuckle arch. Plate edges do not enclose the entire finger: short dorsal plates cover roughly the upper half to two-thirds of each segment, leaving leather underneath. Overlap adjacent dorsal plates by1–2mm in the relaxed pose, with1–2mm dark crease separation where bending occurs. No spherical knuckle buttons; use shallow integral knuckle bulges or a shaped continuous knuckle lame.

Cuff should flare around the wrist with3–5mm visible fit clearance and overlap the forearm guard. Keep wrist/hand continuity: no floating dark band or isolated cuff. A few structural rivets are acceptable, but no new ornament is necessary.

### Hand render checks

1. Match fifth-v2 hand crop; add one palm/side angle that reveals thumb web and finger pads.
2. The silhouette reads as a human glove in rough grey before metal material; thumb, knuckles, webs and unequal finger lengths are visible.
3. No segmented pipes, spherical beads, disconnected tips or slab palm.
4. Dorsal steel wraps over a continuous underglove; leather appears at creases and sides.
5. No visible plate-to-finger penetration or open cut ends in the inspected angles. Static checks are not a full topology/animation certificate.

## Delivery boundaries

Produce actual focused crops early and send them to art-director/QA. Avoid expensive full8-view rendering until these two regions improve. The comparison must use unchanged lighting and framing where possible. Keep rest of costume, weapon, materials and art evidence intact; only local material assignments needed to explain new glove/helmet construction are permitted. Record actual mesh/vertex counts and static geometry checks; no game tests are implied by a DCC-only change. Any eventual deformation/rigging needs separate work and evidence.

## First focal probe review

Inspected actual head, headside, hand and palm crops. Useful change: the brow is no longer a detached wire rail and the glove has a connected underlayer. However, the eye slit wraps around the side/back, the two head halves remain rounded, crown bands are abrupt, the side camera is obstructed by the sword pommel, and the palm/thenar/thumb are excessively bulbous. This is not acceptance.

Sent concrete corrections: stop slit before the temples; narrow the lower jaw another approximately12–15% and flatten broad cheek planes instead of rounded side bulges; terminate crown ridge continuously. Reduce palm thickness approximately20% and thenar prominence approximately25%; retain a shallow thumb-web saddle and use a continuous tapered thumb path rather than pearl-like lobes. Move the side camera to an unobstructed angle. These are visual tuning directions to the implementer, not measurements of the current mesh or anatomy claims. Reinspect focused material/clay crops after correction.

## Corrected focal review — iteration7

Inspected actual `head.png`, `headside.png`, `hand.png`, `palm.png`, `clay_head.png` and `clay_palm.png` preserved under `artifacts/art/last-vigil-v2/iteration-07/`. This includes the opposite-side camera with the sword no longer blocking the head and the revised continuous thumb. These are implemented Blender geometry views, not the generated concept.

**Construction increment verified; overall art verdict remains needs work.** The brow rail is removed, the eye gap terminates near the temple, the cranial/cheek/nape assembly is more continuous, and the chin seats within the gorget outline. The glove has a coherent palm/thumb/web underlayer, unequal fingers and visible fitted dorsal plates. The latest thumb no longer consists of pearl-like separate lobes. These are real improvements over the fifth-v2 tube fingers and attached helmet trim.

The material-free crops also expose remaining weaknesses. Helmet crown and cheek transitions have broad facets and abrupt local shading patches; the lower face and neck remain slab-like rather than convincingly fitted forged plates. The palm is smoother and more connected but still padded/mitten-like, with simplified knuckle/root anatomy and limited crease/edge construction. Mantle blade-like clumps and broad costume material weaknesses remain unchanged outside this focal scope. This does not match the approved concept's natural form, craftsmanship or surface finish.

No additional ornamental pass is recommended to address these defects. A cheap local surface-normal continuity correction may reduce accidental square shading while retaining intended plane breaks; deeper improvement requires deliberate surface shaping and controlled topology around crown, cheek, thumb web and knuckle arc. After form holds in clay, author a localized material sample with stitching, leather compression, edge wear and recessed grime. Do not paint over inaccurate forms to imply completion.

Static crop inspection does not establish hand grip, joint articulation, collision-free head motion, rig/skinning readiness, game performance or owner acceptance. The owner approved the generated direction only. The scene remains a studio asset; boss AI remains deferred.

## Final perimeter-bevel correction review

Re-inspected current `head.png`, `headside.png` and `clay_head.png` after the local visor bevel was restricted to its actual perimeter. The broad square visor shading patches are visibly reduced, including in clay; the integrated shell/temple-ended slit remains intact. Crown/cheek planes remain broad and stylized, and overall reference-quality verdict is still **needs work**. This is a local shading/construction correction, not a new art-quality pass. The earlier iteration7 six-view hashes now point to their verified preserved `iteration-07/` paths; final three-view hashes are recorded separately in `character-focal-authoring-review-hashes.json`. No new scope, ornament, pose or gameplay changes are implied.
