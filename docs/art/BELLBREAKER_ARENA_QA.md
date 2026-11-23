# Bellbreaker arena — independent QA

2026-11-16. Final verdict: ready for human studio layout review only; not production/runtime acceptance. Scope: approved HF-assisted offline environment modelling only. No Bellbreaker implementation, combat/AI change, Unreal build, runtime fairness test or FPS measurement.

## Preservation

Independent baseline: `artifacts/art/bellbreaker-arena-2026-11-16/qa-preservation.json`,49 files covering current Unreal Source/Config/.uproject plus protected browser simulation. Hash again after artist freeze. This does not baseline all binary/generated assets. Parent coordinates other preservation and the sole heavy-job owner; QA launches no DCC process.

## Planned dimensions and player-relative review

Current revised contract:28×36m flat rounded-rectangle fight floor, corner radius4m;6m reserve gives40×48m outer envelope with radius10m corners; hall46×58m. This leaves nominal3m side/5m end margins beyond the reserve before construction. Wall thickness, buttresses and plinths consume those margins; centre coordinates alone are insufficient. Initial3m reserve/38×48m hall/r3 blockout is superseded.

Player1.8m/boss2.7m proxies give a1.5× height relationship. The floor spans approximately15.6×20 player heights. Hypothesized8–10m charges cover29–36% of the width and22–28% of the length: these are future design distances, not implemented reach. At current420cm/s run and630cm/s sprint, crossing28m takes roughly6.7s/4.4s without acceleration or interference; actual combat opportunities need closer spawn spacing. Recommend a provisional8–10m initial separation with equal lateral escape room, labelled proposal rather than a rule change.

Existing lock-on breaks above24m;36m axial separation exceeds it. Preserve this as an explicit future integration issue, not a reason to silently extend targeting. Current camera nominal boom is5m (5.6m for a towering foe) plus separation extension, and user distance scale can lengthen it.Even6m reserve cannot guarantee full boom clearance: the current towering-boss maximum nominal6.8m boom at1.5× user setting reaches10.2m before socket/target offsets. Roof height alone cannot certify visibility: test actual low-angle views with tall pillars, boss body and weapon occluding the camera.

## Actual-draft acceptance gates

- Dimensioned overhead footprint: consistent floor boundaries/corner radius, readable spawn axis and clear straight charge lanes. No interior steps, loose debris, rails, tombs, floor chains or raised trim in the clear region.
- Prop and support complete footprints outside that region; annotation/ruler exclusions declared. Rounded corners must offer lateral sidestep space rather than funnel a player into a wedge.
- Player-height and near-wall inward/tangential views with both scale proxies; separate architectural beauty camera from gameplay-like view. Use a quiet contrasting floor behind feet and boss wind-up silhouette.
- Charge destination/braking area stays readable. Do not promise wall-stagger functionality, destructible cover or damaging arena hazards through set dressing. A future wall impact must use engine-owned collision and preserve an escape route.
- Surface geometry supports a flat floor; intentional shallow inlays identified for material/noncolliding treatment. Studio mesh clearance is not a swept-capsule or wall-contact guarantee.
- Keep atmospheric effects below telegraph contrast. No bright floor marks resembling active attack warnings; no large opaque foreground decoration blocking side-step cues.

## Future validation boundary

8–10m charges need aim-lock, bounded tracking, wall-stop, recovery and greatsword punish tests once separately implemented. No adaptive attack selection now. If later authorized, adaptation may select among unchanged attacks using completed observable player actions only. Current static render, generated model provenance, source integrity and geometry counts do not establish fairness, collision quality, animation, runtime performance or artistic acceptance.

## Initial blockout and revised source review

Actually viewed the two initial blockout images (entry-hero/top-plan). Floor is clear and axial scale markers are readable, but white structural ribs, rectangular clerestories and simple box masses read as a warehouse. These are preserved initial views, not images of the revised hall or evidence of generated props. Rear bronze and flank iron boxes are reserved envelopes only. Actual final architecture/material/HF refinement is pending.

Reviewed assembly clearance calculation without executing Blender: for each evaluated object whose full AABB intersectsZ0..5m, max(loX−20,−20−hiX,loY−24,−24−hiY)>=−1e−5 means its AABB lies outside or touches the40×48m rectangle within tolerance. This is a conservative axis-separation test, not Euclidean closest distance. Using the complete rectangle is stricter than rounded-corner exclusion; full bounds rather than height-clipped bounds can conservatively fail objects whose overhang enters only above5m. Floor/inlays and explicitly labelled proxy/plan objects are excluded. Actual exported layout results must still be checked after generation.

Rounded r4 and r10 corner centres coincide: expansion increases each half-extent and radius by6m. Therefore the stated reserve is geometrically consistent as an outward offset. It is a design zone, not a demonstrated camera envelope. Prepared roof source spans12..17.4m rather than initial14–18m concept; final report must disclose actual geometry. High overhead shapes are outside the below5m audit, not universally certified clear.

## Explicit future integration boundary

The current game uses a radius14m circular floor and fixed circular boundary actors. This28×36m rounded-rectangle proposal is a different layout; it cannot be installed as presentation-only dressing under the existing Dungeon compatibility claim. Any later integration needs separate engine boundary, movement, charge/wall and camera tests. No engine change is made now.

The bronze clear-floor outline is a planning inlay, not an implemented movement limit. The6m empty reserve is measured studio space, not currently playable or camera-only territory. Before integration, decide the actual collider footprint and visible boundary together; an invisible wall at the inlay must not surprise players. Clearance of lower objects does not prove overhead visibility, occlusion freedom or runtime camera movement. Final delivery is a measured arena study, not combat-ready geometry.

## Final-v3 interim review (plan/readback refresh pending)

Seven actual final-v3 views independently inspected: entry hero, reverse, gameplay height, near boundary, neutral clay architecture, furnace detail and bell detail. Real imported bell opening/cradle and furnace volume remain evident in gray clay; these are meshes, not the generated input illustrations composited into a scene. The enlarged floor stays visibly unobstructed. Rear pointed arch now lands on full-height piers and springers. Generated surfaces still have soft/melted relief and simplified roughness; repeating wall textures and plain large upper fields remain art-study limits.

Independent recalculation agrees with all289 reported lower-object AABB margins; minimum0.292390823m beyond the40×48m rectangular reserve. This is a static separating-axis result, not clearance of an implemented player/camera/charge. Main floor and support patches have topZ0; rear patch spansY28.95..31.05 andX±5.25, furnace patches extendX±25/Y±13.25 around the specified pockets. Mainhall46×58 must not be described as total geometry extent. Rear bell atY27 has depth5.41352m, so the extended floor/recess covers its far extent; source arch piers occupyZ0..8m with seated springers.

Final manifest records314,467 evaluated triangles and actual prop fitting: bell119,777 imported→50,000 triangles, height5.5m; furnace114,767 imported→50,000 per instance, actual height3.03166m after depth-constrained fit. Raw furnace glTF has114,773 faces (six dropped on import), not an inconsistent claimed import result. Raw source audit reports23 exact-zero-area triangles total across the two source models; raw finite/index/UV checks do not certify manifold topology or production collision. The subsequently completed derived readback is reported in Final closeout below.

Actual ruler centres(-1,−5)/(1,5) give10.198m separation, not the requested9m approximation; notified parent. Their heights measure1.8m/2.7m. A camera with75° horizontal FOV is still a studio framing sample, not current game camera behavior. No implementation of a Bellbreaker attack, boundary, navigation, AI or physics exists in this delivery.

Current independent preservation check:49/49 source/config/project/browser files unchanged. Final image/scene delivery hash checks are recorded in Final closeout below.


## Final closeout

All eight canonical final-v3 views now independently inspected, including refreshed top plan. Roof/hoist hidden for that diagnostic view and emissive labels make the fight outline, reserve and axes readable. The recapture records no saved-scene or geometry change; it is not a different arena. Layout measurements and actual visible open floor support review of the proposed arena, not an implemented movement boundary.

Saved-scene readback reports finite positions/UV values and14 packed images. It retains24 triangles at or below1e−12m² (six per furnace instance): cleanup remains necessary before runtime asset acceptance. This is not a watertight/manifold, collision or clean-UV certificate. Scene mesh/curve count308,384 excludes text relative to the broader314,467 studio count. Portable GLB is30,882,944 bytes with787 meshes/308,132 reloaded triangles and8 embedded images, no external buffers; procedural Blender bump is not baked/transferred. Its actual boundsX±25/Y−29.3..31.05/Z−.4..17.4 confirm recess/support extensions beyond the nominal main hall.

Final independent49/49 protected files unchanged; source, saved scene, GLB and both actual generated input meshes match declared hashes. Eight PNGs hashed/dimensions recorded in `artifacts/art/bellbreaker-arena-2026-11-16/qa-final-check.json`. Final scene b124ceedcf62ef9031ef1a78df0e117e5920179bf472752a0bd0d80a00bc450e; assembly source f68510a106fd49f1c3aed2c7d1494a13a025ab38aa02efbd25fb8a11f6810713. No Unreal builds/tests, FPS measurement, boss implementation or AI work by QA. Artist's authorized intermediate-scene prune retains blockout/final-v3 and receipts; it does not alter this game-preservation baseline.

Accept as a measured studio draft for owner review. Before engine integration: resolve physical/visible boundary and camera behavior, remove degenerate prop faces and establish collision/LOD/material budgets, then test actual player/Bellbreaker silhouettes and hypothetical charge/escape/punish distances. Artist/engine numeric integrity is evidence of what exists, not proof of finished art or fair combat.

Final frozen delivery-manifest verification: 29/29 files match their SHA-256 values. The eight canonical PNGs are separated from the retained dark-plan diagnostic in the QA JSON.
