# V8 regional lean silhouette study

Status: final static regional proportion increment frozen; overall reference realism remains unmet. This separate static Blender scene addresses the owner's bulk criticism; it does not establish reference realism, anatomical rigging, deformation, cloth simulation or game readiness. Materials, lights, camera framing, figure height and sword are preserved from frozen V7. No AI/game/runtime work.

## Method and visible changes

The source loads the frozen V7 scene, then fits each visible character-owned mesh and curve control point in world coordinates. It transforms points back into each object's local space, without scaling the character parent or changing joint-center spacing. The coordinate field treats helmet, torso, waist, arms, shoulder flare, cape attachment and hanging garment separately. Dependent seams, hardware, linings and garment edges share the same field. This is a reversible proportion study, not bespoke anatomical sculpting or a production deformation cage.

Chest narrows and loses excess depth while retaining its central keel. Fauld/belt flare narrows without a second waist squeeze after review. Shoulder lames and returned sheet edges move inward together; lower lames sit slightly closer together. Upper-arm tubes and cuff hardware gain a more coherent taper, with elbow cap and hand dimensions retained. Skirt panels shorten approximately30mm and taper at their lower edges. Helmet width reduces modestly, with height unchanged. A final boot correction narrows boot/sabaton/sole/edge width9% about original foot centers and reduces upper instep7% with a blend to zero at sole contact and ankle attachment. Foot length, ground contact, leg height and remaining lower-body art are unchanged.

`regional-fit.json` records each changed object, maximum control-point displacement, evaluated named armor-region dimensions, and before/after camera matrices/lenses, root scale and sword geometry/transform digest. Region measurements use the same named object sets and height bands, not apparent pixel size. Bilateral arm span is not a limb diameter; sample counts can vary where an adjusted shoulder edge crosses a band boundary.

## Preserved failures and review limits

First pass transformed surcoat panels but missed two legacy curve names for their binding and hem. Actual renders showed floating old outlines. The failed images/source/receipts are preserved under `iteration-01-garment-binding-mismatch`; the corrected semantic garment group includes those curves. An initial x-window measurement admitted different arm vertices after narrowing; it was replaced with stable named armor groups before reporting torso reductions. The second coherent pass remains under `iteration-02-first-coherent-fit`. QA also caught stale camera matrices in the initial protected-state readback (all views repeated one matrix because the dependency graph had not been updated). That report is preserved as `regional-fit-initial-camera-audit.json`; final audit explicitly updates the view layer after each camera change and compares fresh saved V7/V8 scenes. Actual renders were already correctly updated by Blender rendering. This fixes audit evidence, not camera framing.

The thinner figure still has stylized stepped shoulder edges, simple helmet geometry, smooth steel, broad carpet-like mantle backing, rigid skirt panels and simplified gloves. This pass changes proportions; it does not claim those craftsmanship problems are solved. V7 projected visor UV degeneracy and unintegrated V5 glove UV study remain unchanged.

Scoped reload checks include finite geometry, six transformed slot-center rays reaching recessed backing, and sampled cape/body back-envelope clearance. These exclude outer mantle/yoke, top cape attachment and curves and do not test arbitrary triangle intersections, animation or all clothing clearance. The historical motion cache does not validate this modified shape.

Final exact source/scene hashes, image list, resource receipts and scoped results are in `artifacts/art/last-vigil-v8/techart-delivery-audit.json`. Guarded CPU jobs retain the10GB Unreal budget,24GiB free reserve and20-minute deadline. No persistent process or external asset download.

## Final evidence

Ten main actual views plus two supplementary head views; eleven720×920/16-sample and one1400×1800/48-sample hero. Three actual V7 clay baselines were rendered into the V8 folder without modifying V7. Camera/lens/root-scale/sword signatures compare equal before and after the regional fit. Reloaded geometry: 354 renderable objects, 1064128 vertices, 1933572 triangles; finite. Six slot-center rays reach backing. Scoped cape sample 24144 hits, minimum 37.229mm, zero negatives. No full collision/motion claim.

Reproduction requires frozen V7 source/scene and original `last_vigil.py` utility source as declared in the V8 source; saved V8 scene is independently editable with inherited packed maps. CPU commands: `./scripts/bosslab-art-v8 draft hero front side back clay_hero clay_front clay_side torso shoulder head headside`, `./scripts/bosslab-art-v8 render hero-detail`, `./scripts/bosslab-art-v8 audit`.

Measured armor regions (before → after): chest width441.96→408.94mm/depth338.70→298.23mm; fauld width367.45→328.99mm/depth260.00→224.92mm; shoulder span739.47→628.48mm; upper-arm depth162.00→126.36mm. These are specific sampled armor bands, not whole-body anatomical measurements. Final camera reload contains six distinct per-view matrices with exact V7/V8 matching; initial stale readback preserved.
