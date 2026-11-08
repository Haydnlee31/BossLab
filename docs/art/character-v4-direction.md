# V4 — recover the approved silhouette

Date: 2026-11-07. Art-director brief. Re-read current status/role guidance and compared approved concept directly with v3 hero. This is a separate studio revision; preserve previous versions and game. No new concept generation, downloads, runtime integration or boss AI.

## Diagnosis

The visible gap is primarily authored design, shape and material construction, not a physics restriction. The approved image suggests fitted angular armor, articulated thin plates, soft irregular textile and a believable anatomical body beneath. V3 substitutes rounded caps, smoothly tapered tubes, a brush ring and uniform surfaces. Smoothing those primitives improves defects without recovering the intended design. Cloth physics will eventually matter for motion and collision, but it cannot turn an incorrectly shaped static mantle into the approved garment.

A concept raster gives one lit projection, not hidden surfaces, fitted plate volumes, topology, UVs or deformation. Those must be designed. Our earlier procedural construction made those decisions too mechanically. Its numerical mesh integrity is separate from the artistic result. The correction is a deliberate large-form pass before more ornament or material amplification.

Official workflow context: Blender Studio's public indexed [Design Sculpting description](https://studio.blender.org/training/realistic-human-research/design-sculpting/) separates design-sculpt approval from retopology; its [modeling guide description](https://studio.blender.org/tools/artist-guide/asset-creation/modeling) describes production modeling after approved design, generally retopologizing shapes developed through sculpting/loose modeling. Full page fetches returned402, so this research uses only their public indexed descriptions, not unseen paid course content. Applying that distinction here is our workflow inference, not a claim that a particular tool guarantees quality.

## Priority 1 — helmet, neck and shoulder silhouette

The following ratios are reversible design targets relative to v3, not measurements recovered from a perspective concept image.

- Narrow maximum crown width approximately10%, and lower visor width12–15%. Chin width should be approximately80% of eye-line width. Preserve plausible skull clearance by editing profile, not simply crushing the whole head.
- Replace rounded bowl front with a shallow central ridge and two swept cheek fields, transitioning into a narrower jaw. Deliberate broad fields remain smoothly forged; do not replace a bowl with many arbitrary facets.
- Brow/eye edge should make a shallow central downward V, approximately6–10mm depth at this scale. Preserve a real narrow slit that closes toward temples. No detached rail, triangular spike or painted black line.
- Seat skull10–15mm lower if clearance permits. Replace bright tall cylindrical neck with2–3 fitted overlapping gorget lames, narrow beneath jaw and widening into sternum/shoulder. Keep visible rotation clearance; avoid burying the whole chin.
- Flatten inflated shoulder caps and replace repeated rounded lower bands with thin descending lames whose outer lower corners sweep down/back. A slightly asymmetric left/right silhouette is preferable to identical stacks. Keep actual plate thickness/rolled edge and plausible overlap, not razor-thin paper.

## Priority 2 — remove the brush-ring mantle

Suppress the uniform radial front leaf/fiber ring. Build two asymmetric dark cloth pads lying over trapezius/shoulders: inner edges rise behind the neck, outer edges descend toward acromion. Author3–4 broad quilted folds per side, with different size and spacing, not radial corrugations.

Leave front center open enough to expose roughly60% of gorget/upper-chest width. One flap extends approximately30mm farther forward. Halve current front silhouette thickness. Keep the attachment strap readable across exposed chest. Fur belongs mainly on outer/rear edges:5–8 overlapping unequal tapered clumps each side,15–40mm long, swept outward/back with limited downward tufts. These numbers set a coarse clump hierarchy; they are not instructions to make visible flat leaves or identical triangular teeth. Fine strands are subordinate and must not recreate the brush ring.

## Priority 3 — fitted breastplate and waist

Maintain broad upper chest and plausible front-to-back depth, flowing into a waist approximately8% narrower than v3. Use separate side-panel curvature and restrained median/chest breaks to describe fitted construction. Move dependent straps/plates with the change. Do not shrink a torso underneath unchanged attachments or leave cloth penetrating metal. Existing focal gate motif stays; no more decorations this pass.

## Secondary — hand slab and UV construction

Replace the lower-palm straight ledge with a staggered MCP/root arc, shallow palm hollow and broad thenar saddle. Keep fingers tapered with unequal lengths and a credible thumb opposition. Fit dorsal shells after the base shape. This must improve in clay, not only through darker crease paint. Use separate seam-based palm/dorsal/side UV islands rather than projected front/back overlap. Avoid letting a glove-only loop consume the whole-figure pass.

## Evidence and acceptance

Keep neutral lights, comparable camera and framing. First actual outputs: hero/front three-quarter and head-side in clay/material, plus palm clay if revised. At thumbnail scale the mantle must no longer form a rigid ring, shoulders must cease reading as cushions, and head must read as a shaped brow/cheek construction. At crop scale inspect overlap, actual slit, collar clearance and textile layering. Material changes must support those shapes, not hide them under dark light or cloud texture.

This pass aims for a visible major advance toward the approved design; no promise of reference-quality completion. Full garment sculpting, material painting, production topology, rigging/cloth and runtime evaluation remain separate gates. Owner approval of the concept is not approval of the model.

## First actual V4 review — rejected mantle construction

Actual hero/head and clay hero/head inspected. Narrowing is modestly visible, but the new mantle is a regression: two shiny tan rigid sheets and an exposed repeated row of claw-like tufts. They do not read as quilted wool and fur. The dark neck apron has bright central trapezoid breakthroughs, and thin bright cord-end rods protrude at the shoulders. These are defects, not intended wear.

Immediate correction sent: dark matte wool response, three broad shallow draped folds from neck attachment toward shoulder, outer edges following the shoulder rather than turning into rigid wings. Remove thick isolated claw shapes; introduce several staggered roots of softer overlapping wisps at outer/rear edges, never a comb. Expose correctly fitted actual gorget lames rather than a black annulus masking them; resolve penetrations/cord ends. Helmet needs a broad near-planar central face with angled cheek returns, not merely a scaled bowl. No art pass; the whole-figure target remains unmet.

## Second actual V4 review

Actual hero/head inspected again. The central visor now has deliberate planar fields, and the conspicuous gorget breakthroughs are resolved; those are worthwhile form/construction changes. The mantle remains two rigid floating boards with straw-like surface flecks. Corrective direction: seat outer pad tips over shoulder caps, curve the front edge downward approximately15–25mm to follow plate, keep inner/back attachment higher, and author two broad soft fold valleys. Conform fibers above the cloth, but do not confuse a fiber visibility fix with cloth drape. A continuous undercoat mass and irregular overlapping edge tips should replace exposed board surfaces. A modest studio geometry increase is acceptable under actual resource guards; the old mesh count is not an artistic ceiling or runtime certificate.

## Third actual V4 review and bounded hierarchy correction

Dense continuous fibers now cover the mantle, eliminating bare board/straw patches and isolated claws. The edge still resembles short carpet with rigid backing; it is not yet the concept's soft irregular garment. Helmet face planes remain a visible improvement. Overall steel is still uniformly blue-silver with bright piping and broad cloud contrast, unlike the target's quiet forged charcoal fields.

Directed a bounded material hierarchy trial under unchanged light: reduce blue saturation approximately half and broad cloud color contrast70–80%; main plate roughness about0.42–0.52 and localized polish0.28–0.34, preserving readable reflections. These are starting shader choices, not measured physical properties. Avoid a uniformly dark/flat result. Reduce all-edge bright piping. Reauthor the existing gate plaque as one fitted pointed arch with continuous curved shoulders, approximately45–55mm wide and190–220mm tall, shallow aged-bronze border and existing seven studs. It should be the small warm focal accent, not a new collection of decorative objects. The present diamond tip and narrow sliver do not express that motif clearly.

## Final direction assessment

Latest material hero/head, clay hero and palm inspected. Neutral darker metal reduces the blue/clouded toy sheen; the curved arch motif reads more clearly. Narrower planar visor fields and separated fitted gorget lames are substantive visible changes. These constitute progress over v3, but do not meet the approved concept's realism.

The remaining failure is not insufficient ornament or physics: shoulder plates still inflate into rounded cushions; mantle clumps repeat like coarse carpet tiles on a hard backing; breastplate remains a broad smooth field with limited fitted construction; glove is still padded. The procedural parameter approach has repeatedly regularized forms that require deliberate local decisions. Another density/noise/roughness adjustment would not resolve this construction problem. The art director recommends freezing this coherent increment with the design gate unmet, rather than describing another superficial adjustment as a solution.

**Next meaningful authoring step:** a coupled shoulder-and-mantle form study. Replace cushion caps with thin shaped shoulder shells and angular descending lames, then author cloth attachment, gravity folds and soft overlapping fur masses around that actual support. Establish irregular clump root distribution as part of the garment silhouette, not a repeated grid on a slab. Evaluate front/side/three-quarter clay without fibers first; only then add groom detail. This is bespoke surface/silhouette work, not a physics requirement. New rig/cloth simulation and runtime tests still follow art readiness; no claim of integration or owner acceptance.

## Final shoulder replacement review

After the assessment above, the technical artist performed one bounded actual cap/lame surface replacement. Final hero, head, head-side, clay head-side and clay hero were inspected. The shoulder silhouette now descends in angular thin plates instead of inflated cushion bands; this is a substantial visible form advance and supersedes the earlier cushion diagnosis for the final revision. No new conspicuous shoulder penetration was observed in these limited views; this is not a full intersection or motion certificate.

The side view exposes the remaining gap clearly: separated repeated fur rows over flat backing, broad smooth skull, a visible pale curved neck/collar insert and simple flat plate fields. The whole figure is closer in silhouette but still markedly less natural, detailed and constructed than the approved concept. No reference-quality acceptance is granted. Next bespoke shoulder/mantle work should retain the new descending plates, shape their fit/edge construction and replace the rigid carpet backing with genuinely draped garment volumes. Do not undo the actual silhouette advance by returning to domes.

Final inspected-view hashes: `docs/art/character-v4-direction-review-hashes.json`. These identify the views actually examined by art direction, not an assertion that every generated view or every hidden surface passed visual review.
