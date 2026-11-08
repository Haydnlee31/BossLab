# Player outfit proposal — The Ashbound Knight

Status: direction approved by the owner, 2026-11-06; first playable mesh implementation delivered; see [actual delivery and remaining targets](PLAYER_OUTFIT_IMPLEMENTATION.md). The design below preserves the original proposal and distinguishes targets from delivered assets.

Original planning snapshot: The owner considers basic animation/controls in place and now requests player-outfit planning from the supplied Godfrey video, with an original twist and a single legendary two-handed sword. This authorizes design planning; no character mesh, texture, rig, animation or game package has been changed. Boss motion refinements remain a separate backlog item. No AI/model work.

## Reference: what is visible

Re-inspected six preserved video frames: 0:00, 1:52, 2:32, 7:28, 7:32 and 7:44. The first is a close rear view; the late frames show the front. These are actual extracted reference images, not BossLab renders. The original MP4 is no longer present at its previously supplied Downloads path. Attempted native-resolution extraction therefore failed; this pass uses the preserved 960×540 images. Prior full-timeline sampled review remains in REFERENCE_VIDEO_REVIEW.md.

- Pale shaggy material surrounds the head/neck and broadens the upper silhouette. From these views, individual regions cannot reliably be separated into hair, fur, plume or helmet ornament.
- A patterned, weathered metal collar spans the upper back, with raised shoulder pieces. A faded rusty-red cloth panel drapes across the shoulders/back.
- Long, irregular pale/dark fur-like layers create a heavy trailing silhouette behind the torso and legs.
- Front views show layered metallic arm and leg protection, a darker torso with red cloth, waist layers and armored boots. Exact chest engraving, buckles and hidden attachment construction are unclear.
- The player carries separate curved blades, consistent with the owner's dual-katana description. The source hand/weapon stance will not be used as the grip design for our single greatsword.

Useful views: [rear close-up](../artifacts/reference/godfrey/overview/frame-00000.000.jpg), [rear silhouette](../artifacts/reference/godfrey/overview/frame-00112.000.jpg), [front](../artifacts/reference/godfrey/overview/frame-00448.000.jpg). Do not assign a named source-game armor set without separate verification. The concept below is an original reinterpretation, not a recovered 3D mesh or exact costume replica.

## Core design

**The Ashbound Knight** — a former sanctuary guardian who carries a sword entrusted to a broken order. The equipment should feel old, maintained and personally repaired. Human proportions, broad but mobile shoulders, a defined waist and visible knees/boots. The sword supplies the largest clean shape; the outfit supplies layered history.

Retain the reference's pale upper silhouette, weathered metal, red textile and traveled-in character. Concentrate the fur around the neck/upper back, shorten the cape and reduce protruding shoulder shapes to support our two-handed pose. Main original motif: a bronze circle with one deliberate missing segment, repeated sparingly on the chest clasp and sword guard. It connects the knight to the arena's circular bronze inlays without using source-game emblems.

## 3D construction map

All dimensions/proportions are initial art targets for a blockout on the current rig, not measurements recovered from the footage.

| Region / separate modeling part | Proposed volume and materials | Assembly and movement requirements |
|---|---|---|
| Underlayer | Charcoal quilted fitted jacket and trousers; small chainmail regions at armpits, elbows and hips | Soft skinned foundation. Keep joint folds readable; hide covered body surfaces only after fit is checked. |
| Head / helmet | Tapered enclosed steel helm; narrow horizontal eye opening, split brow ridge, restrained ivory crest at the nape | Helm follows the head as a rigid part. No long horns or projecting face spikes. Head remains distinct from collar in side view. Face customization is deferred. |
| Neck / mantle | Ash-ivory short fur collar, thickest at rear neck, thinning toward the chest | A few broad clumps establish volume; selected edge cards add softness if needed. Leave throat/arm-lift clearance. Avoid a full-length fur cape in the first version. |
| Chest / abdomen | Dented silver-steel breastplate with a shallow central ridge; overlapping abdominal plates; narrow oxblood cloth visible underneath | Separate rigid chest volume from flexible waist. Engraved detail follows big forms. A repaired bronze strip and broken-ring clasp are the signature accents. |
| Shoulders | Low overlapping steel pauldrons; left slightly more layered than right, both rounded and compact | Articulate away from chest/upper arm as the arms lift and cross. No fixed spheres/spikes that collide with neck or sword. Asymmetry stays modest. |
| Arms / hands | Fitted steel forearm guards, dark leather gloves and articulated knuckle plates | Both wrists must flex around one shared hilt. Open inner elbow/forearm clearance; hand silhouette must read at gameplay distance. Finger fit follows real grip, not a rigid mitten. |
| Waist / hips | Dark leather belt, short overlapping tassets and split cloth skirt; one compact flask pouch behind the left hip | Tassets overlap with leg movement. Keep crotch/hip flexion clear for deep roll tuck. Pouch stays close to body, away from hilt and thighs. |
| Legs / feet | Slender steel greaves, shaped knee plates, dark leather at rear joints; broad grounded armored boots | Preserve knee bending, ankle articulation and readable foot contact. No long spurs or toe spikes. |
| Back / cape | Faded oxblood wool cape, split vertically into two uneven tails, ending around mid-thigh; dark lining | Attach beneath mantle at two upper-back points. Preserve a central gap and knee visibility. Prefer a small bone-driven cloth setup first; assess physical cloth only after profiling. |

Layer order: body → quilted underlayer → exposed mail → main plate → mantle/cape → belt and small fittings. Main plate pieces remain rigid in appearance; flexible seams carry bending. Avoid welding shoulder/chest/upper arm into one deforming shell.

## Three-view specification

**Front:** readable helmet slit; ivory collar framing a dark neck opening; silver chest tapering into a narrow belt; small bronze broken ring above the sternum. Red shows as a narrow central textile panel and cape edges. Hands and shared hilt remain unobstructed. The two greaves are clearly separated.

**Side:** shallow chest/back depth with comfortable head clearance; compact overlapping shoulder caps; elbows clear of the torso during guard. Cape projects slightly from the upper back and falls toward mid-thigh, not to the ankles. No giant back-mounted scabbard in the initial design; sword is held in combat.

**Back (highest gameplay priority):** ivory collar forms an identifiable crescent above the red split cape. A short vertical bronze repair/clasp detail links the upper back to the chest motif. Two cloth tails reveal the waist turn and legs. The outline should read even when textures are reduced to flat colors.

Palette targets under neutral light: worn silver-steel #747A7D, charcoal #25292B, ash ivory #BEB7A4, faded oxblood #653D3A, aged bronze #88704B. These are design swatches, not calibrated PBR shader values. Metal and cloth need distinct roughness; distribute wear around edges, straps and contact areas instead of uniform noise. Keep bronze accents limited so they do not merge with the arena lighting. No constant full-body glow.

## Legendary two-handed sword — Oathwake (working name)

A long, straight, double-edged steel blade with a clear taper; a narrow inscribed central channel; a subdued bronze guard forming an incomplete ring; a long dark leather grip with room for both gauntlets and a counterweight pommel. One repeated repair/inlay detail connects sword and breastplate. The legendary quality comes from silhouette, craft and history. A restrained light treatment is an optional later presentation experiment, not a gameplay power or required emissive effect.

Build the decorative weapon around the current authoritative hilt, blade endpoints and hand separation. The prototype's shared hand targets are approximately17cm apart in local presentation space; verify actual gauntlet fit on the rig. Any proposed change to blade reach, thickness used for contact or grip locations must be explicitly separated from the cosmetic pass and retested. Do not enlarge the visual blade beyond the existing contact sweep merely to make it look legendary. Preserve the approved deliberate attack timing. No second blade, shield or combat-changing accessory is part of this proposal.

## Practical modeling and validation sequence

1. Produce consistent front/side/back concept views plus a rear gameplay silhouette, with the sword shown separately and in a two-handed guard. Owner reviews silhouette, fur/cape amount, helmet and palette before detailed modeling.
2. Block volumes around the existing rig: torso, helmet, shoulders, forearms, hips, legs, collar and cape. Test the actual guard, wind-up, contact, recovery, sprint and eight roll directions while surfaces are still simple.
3. Check overhead arm lift, crossed arms, both hand grips, shoulder/neck gaps, crouched hip clearance, knee bends and cape clearance at the back of the legs. Fix forms before engraving or textures. Use gameplay camera as well as turntable views.
4. Build mesh topology, skin flexible regions and attach/weight rigid plates deliberately; author UVs and bake surface detail. Avoid bending steel like rubber. Keep hero and boss silhouettes distinct.
5. Add controlled secondary motion and materials, then test silhouette and clipping at720p. Profile the actual engine build; retain current controls and sword/roll rules.

Provisional resource targets (to measure, not guarantees): outfit/body around30–40k visible triangles at the nearest LOD, sword3–5k; progressively simpler distant LODs; two shared2K texture sets for metal and textile/leather, plus a small fur atlas only if necessary. Start with a small material-slot count and no strand-hair simulation. Reuse the rig and hide unused covered surfaces. Keep additions within the existing10GB project ceiling and24GiB free-space reserve; do not download large asset packs. These targets can be reduced after profiling.

## Review gate and remaining choices

Recommended first direction: closed helm, short ivory mantle, mid-thigh split red cape, restrained asymmetry and the bronze broken-ring motif. The main review is whether this should feel like a lean wandering knight or a heavier ceremonial guardian; this proposal chooses the former while giving the greatsword the visual weight. Character face/body identity, final name, insignia details and any sword light effect remain provisional.

No production 3D model, concept render, texture or gameplay evidence was generated by this planning pass. The 3D map above is a proposed construction specification. Existing mechanics tests20/20 native and17/17 cooked remain historical results for the unchanged build; no new tests or performance gains are claimed. Owner acceptance of basic animation/controls authorizes this outfit-planning phase, not a claim that every boss animation issue is resolved.
