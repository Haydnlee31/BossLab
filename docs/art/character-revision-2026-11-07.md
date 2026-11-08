# ART-02 — Last Vigil character revision handoff

Owner: art-director. Date: 2026-11-07, Asia/Singapore. Handoff recipient: animation-techart. Scope: original Blender studio revision, no Unreal integration or AI. Inputs read: current project instructions/status/claims, `docs/LAST_VIGIL_ART_STUDY.md`, actual `artifacts/art/last-vigil/{hero,front,back,armor,hilt}.png`, and construction source `unreal/art-studio/source/last_vigil.py`. Role guidance: owner-supplied `/Users/haydn/Downloads/art-director.md`.

## Diagnosis from the actual renders

The existing character has many objects but weak large-form design. The egg-shaped helmet sits on a visibly tall cylindrical gorget; both shoulder domes look like matching rounded caps. Hands end in four bead-like tips without an effective thumb/palm silhouette. Fur forms an evenly hanging brush around the collar. Rear cloth reads as a narrow rectangular curtain with similar vertical folds from top to bottom. Repeated metal scrolls and equally bright borders flatten the hierarchy, while cloudy color variation makes forged steel resemble patterned plastic. The hilt has an open gap where a convincing tang/ricasso connection should read; its angular guard and ring are schematic. These are visible construction/style problems, not insufficient polygon count or disk space.

The following are authored target choices, not measured historical requirements. Preserve the existing original lore and gameplay weapon reach. This session should visibly change the large forms before another detail pass.

## Five changes, in execution order

### 1. Seat and reshape the head/shoulder silhouette

Retain skull volume around a human head but shape cheek/jaw planes, a modestly projecting brow and a protective nape. Remove the bulbous egg impression and central gold wire ridge. Reduce exposed neck height by approximately 20–30 mm where clearance permits; overlap the lower helmet into a flared, shaped gorget rather than simply sinking meshes through each other. Exposed mail becomes a narrow dark transition, not a necklace stripe.

Replace hemisphere shoulder outlines with flattened crowns and swept rear wings, two or three tapered overlapping lames. The left outer/rear wing may be 8–12% broader; keep the right shoulder close for the two-handed sword. Keep a clear arm-to-torso gap. Retain steel edges but suppress circular rosette badges and gold joint rings. Shape elbow wings with directional taper; no ball joint silhouette.

Source attention: `Helm |`, `Visor`, `Gorget |`, `Visible coif rings`, `articulated pauldron`, associated trims and collision stand-ins. Existing surface ornaments must follow changed meshes or be hidden in the revision, not float above old coordinates.

Acceptance: at roughly 250 px character height, brow/jaw and sloping shoulders distinguish the new outline from the old; no long straight neck tube; no obvious head/collar penetration in front, side and three-quarter views. Detail changes alone do not pass this criterion.

### 2. Rebuild readable hand anatomy

Use a tapered palm, visible thenar/thumb base, knuckle arch and four fingers of different lengths. Each finger needs two or three connected segments, taper and a relaxed curl; fingertips should not be tiny independent spheres hanging beneath a cuff. Place a real opposing thumb. Flare the cuff to admit the wrist and layer a knuckle plate over the glove. Remove shiny beads/repeated three-band mitten treatment.

Source attention: glove/finger meshes and wrist cuffs; this is studio anatomy, not a new production hand rig. Keep hands in a relaxed neutral pose for this revision; do not claim grip/animation validation from a static render.

Acceptance: full-size crop clearly identifies thumb, palm and fingers; silhouette reads as a gloved human hand even with all materials replaced by grey. No disconnected fingertips, plate penetration or obvious wrist gap.

### 3. Make garments and mantle appear worn and sewn

Break the uniform fur ring into irregular overlapping clumps with darker roots and lighter tips, shorter near the front fastening and longer over the rear-left shoulder. Vary direction from skin/garment flow; no continuous straight fringe. Reduce fiber count if clumping improves the read.

Give cape attachment a visible folded collar/yoke or fastening seam. Use a small number of broad gravity folds emerging from attachment points, becoming less regular toward the lower half; overlay only a few smaller folds. Introduce modest asymmetric drape and hem wear, not serrated noise. Darken toward dried oxblood and keep the highlight broad/diffuse. The existing emblem can be dimmer, partly worn and interrupted by a restrained sewn repair; it must follow cloth UVs. The split front surcoat needs diagonal tension folds at belt/hip and less identical panel edges.

Source attention: mantle curves, cape rest surface/material, surcoat surface, cape texture. Changing cape vertices or attachments invalidates the old cloth cache: label the new scene static or rebake and re-audit. Never reuse the old clip as proof of new cloth motion.

Acceptance: rear quarter view shows attachment, broad fold hierarchy and edge thickness; silhouette no longer reads as a rigid rectangular curtain; fur has visible clump gaps and direction changes. Avoid concealing shoulder armor or future sword-path readability.

### 4. Replace all-over decoration/noise with a focused material hierarchy

Remove or hide most repeated limb scrolls and several chest curls in the revision. Keep one small oath seal and a few restrained etched/embossed bands. Thin bright trims and reduce electrum saturation. Replace high-contrast cloudy base-color noise with predominantly stable blackened steel, subtle directional roughness and targeted wear: overlap rub, a repaired shoulder plate, shallow rim scuffs, slight finger/grip polish. Keep fabric distinctly matte and leather compressed around fastening points. Small imperfections should differ across mirrored sides.

Source attention: `node_mat` drives common cloudy noise; narrow its color ramp and decouple medium-scale color from roughness. Use local masks/geometry fields if practical. Do not spend the pass merely adding scratch curves. Material work must be assessed under the same lighting, not a darker exposure.

Acceptance: a grey thumbnail has clear quiet torso/limb masses with limited focal details; at full-size, metal, leather and wool differ by reflection response. No uniform white outlining or identical mottling across all armor parts. Preserve sharp sword-edge readability.

### 5. Give Oathwake a credible structure and one strong history mark

Create a continuous tang/ricasso path seated through the guard into the grip. The incomplete halo is a smaller backed reliquary fitting attached to the guard, never the apparent structural bridge between blade and grip. Shape the guard as a forged, tapering curved span instead of a zigzag polyline; reduce round button-like quillon ends. The long grip should gently swell/taper around two hands, with leather seams of plausible width and a secure pommel.

Keep the original seven oaths and repaired fracture, but express them as shallow inlay/engraving and an irregular narrow brazed scar. Avoid raised gold line doodles. Maintain the blade's usable bevel, shoulder and point; no new emissive/magical effect. Studio geometry changes do not authorize gameplay reach, damage or timing changes.

Acceptance: complete hilt crop shows how blade, guard, grip and pommel connect; no floating gap; the broken reliquary and repaired seam remain identifiable without reading lore. The blade must still look wieldable in a two-handed grip.

## Delivery and review gate

Preserve November 6 evidence unchanged and use a new dated source/scene/evidence path. Deliver a hero, front, rear-quarter, head/shoulder, hand, and hilt detail at sufficient resolution, with matching-camera comparison where possible. Record which requested changes were actually implemented, and any retained defects. A static scene is a valid interim artifact but must not be called a rigged/game-ready character. Existing cloth metrics do not apply after geometry changes. No new gameplay or FPS claim.

Art-director and QA should inspect the actual new images before the orchestrator marks the implementation reviewed. The gate is a clearly improved human silhouette and material/construction read, not a triangle count. Reference-level quality and owner acceptance remain separate. If the image still looks like decorated primitives, route the specific failure back to modeling rather than adding more ornaments or changing lighting.

## Research basis

See `docs/style_bible.md` for palette, scope and primary sources. The [Denver Art Museum construction guide](https://www.denverartmuseum.org/en/age-armor-access-guide-reality) supports fitting/articulation/attachment principles; the [V&A armor discussion](https://www.vam.ac.uk/articles/fashion-and-armour) supports considering armor as shaped, mobile clothing. All dimensions, asymmetry and stylistic choices above are original project direction, not quoted museum specifications. No reference meshes, textures or images were downloaded for shipping.

## First v2 render review — ART-02 follow-through

Inspected `artifacts/art/last-vigil-v2/iteration-01/hero.png` after the first technical-art pass. This is a provisional render, not the final revision. Improvements: fingers now connect into a readable hand outline; rear cloth extends into a broader drape; sword hilt has a continuous structure; repeated decorative clutter is reduced.

Still **needs work**: crown is pinched/scalloped rather than intentionally forged; tassets have obvious broad triangle/facet shading and are disproportionately bright; the mantle is sparse strings over a blank dark collar; large metal fields read uniformly smooth/chrome; removing all chest identity produced an overly generic mechanical appearance. Directed tech art to correct crown continuity, curved dark tassets, opaque clustered mantle under-volume with fine strands, one restrained gate seal and localized roughness/contact scuffs. Do not interpret fewer ornaments as finished material authoring. Final images must be re-inspected; no reference-quality or owner acceptance claimed.

## Third v2 review and explicit concept target

Third actual hero (preserved as `artifacts/art/last-vigil-concept-2026-11-07/input-actual-v2-render.png`) fixes earlier crown/tasset artifacts and improves collar coverage. It still reads as a generic smooth armored mannequin: helmet crown remains round, fur clumps resemble leaf plates, steel fields are uniformly smooth, and the small chest wire does not establish identity. Technical repairs alone do not meet the requested visual target.

With orchestrator authorization, used the **imagegen** skill and built-in image-edit tool once on the actual third hero to create a clearly labeled [concept target — NOT BUILT](../../artifacts/art/last-vigil-concept-2026-11-07/concept-target-not-built.png). This is an AI-generated paintover, not a new Blender render or game evidence. [Exact prompt and provenance](../../artifacts/art/last-vigil-concept-2026-11-07/README.md); actual input render preserved alongside. No API/CLI fallback or character asset downloads.

Specific feasible translation priorities sent to technical art: sculpted peaked brow/cheek planes; tapered overlapping shoulder-lame edges and riveted construction; one inset gate plaque with seven studs rather than a wire logo; dark quilted mantle with irregular soft fur; localized wear/roughness and garment texture that differs materially from smooth metal. The target's detailed surface authoring is not yet built. Do not substitute the generated image for actual evidence, and do not assume all generated connections are structurally valid.

## Owner direction response

The owner replied **“This is the right direction”** to the explicitly labeled generated concept target. Record this as approval of that visual direction only. It does not approve the current Blender model, reference-level realism, rigging, cloth simulation, gameplay integration, or performance. Future modeling should translate the approved concept's actual construction and material hierarchy into geometry and authored surfaces while preserving honest implementation evidence.

## Final fifth-v2 art review — needs work

Inspected the actual fifth-revision `hero.png`, `hand.png`, `side.png`, `back.png`, `armor.png` and `hilt.png` under `artifacts/art/last-vigil-v2/`. These are Blender images, distinct from the approved generated concept. The current revision is worth preserving as a coherent construction increment; it does **not** meet the approved concept's realism or finish.

| Area | Visible improvement | Remaining art limitation |
|---|---|---|
| Crown / chest | Crown ridge is seated; gate plaque and seven fixings follow the chest more consistently | Helmet remains an egg-like shell with attached visor; side view reveals brow trim projecting as wire. Plaque is a surface addition, not yet convincing inset metalwork |
| Shoulders / torso | Swept lame edges and repaired left-shoulder detail create some hierarchy; repeated scroll clutter removed | Shoulder domes and limb cross-sections remain generic; breastplate/arm proportions read as assembled procedural surfaces |
| Hands | Thumb is closed/rounded, fingers taper and connect, fewer spherical knuckle caps | Palm is slab-like; thin similar finger segments lack convincing knuckle/thenar volume, garment wrinkles and fitted plate articulation |
| Cape / mantle | Visible upper-back armor/strap breakthroughs are absent in the inspected corrected back view; wider drape and broad folds | Static cape lacks convincing sewn shoulder fullness and layered folds; mantle clumps remain blade/leaf-like with straggling fibers, not soft matted fur |
| Sword | Guard flows continuously and blade-to-grip structure is now present | Rounded button tips, blocky blade shoulders and uniform grip/metal finish remain schematic; legendary craftsmanship is below concept target |
| Materials | Metal has more varied response and small local marks; material regions are separated | Mottled steel is still procedural and broad; fabric, leather and wear lack authored local history. Smooth specular gradients dominate close-ups |

The corrected back view supports “no previously observed breakthrough in this static view,” not “collision-free cape.” No pose, movement, simulation or game integration acceptance is inferred. Owner's positive response belongs to the generated concept only.

### Next focused production task

Stop ornament iteration. Rebuild one coherent **head/neck and hand construction study** against the approved concept: a fitted helmet shell with integrated brow/cheek/jaw transitions and real edge thickness, plus a continuous anatomical leather glove with palm arch, thenar volume, knuckle progression, finger pads and fitted overlapping dorsal plates. Evaluate three-quarter/side/grey-material crops before copying the solution across the outfit. This requires deliberate mesh/topology authoring rather than more attachments to the current primitives.

Then UV/paint a small representative material section (helmet or gauntlet): darkened steel field, exposed contact edge, recessed grime, fine tooling, leather compression and thread/lining. Preserve uniform lighting and compare the actual rendered section to the approved concept. Expand that proven construction/material treatment to shoulders, torso, sword and garments only after it works. Retopology, full rig/weights and fresh cape animation remain separate later steps; no AI work.
