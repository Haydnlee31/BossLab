# Arena design01 — engine and scale contract

2026-11-09, `arena-design-01` branch, derived from the current Claude-revamp build. Read-only source assessment and drafting instructions only: no Unreal gameplay/map/source changes, build, render or benchmark was performed. Current player/Regent skeletal costumes and presentation-only cloth chains are preserved; this document does not validate them against a new arena.

## Existing geometry and gameplay coordinates

Unreal units are centimetres; Z is up. Dimensions below are source-derived nominal dimensions using the standard100cm Unreal BasicShapes cube/cylinder. Runtime primitive bounds/collision were not queried in this planning pass. Preserve the actual existing actors/transforms when integrating; do not reconstruct a purported equivalent collider from rounded dimensions.

| Element | Existing definition / nominal dimensions |
|---|---|
| Floor | Engine cylinder at(0,0,−50), scale(28,28,1): radius1400cm,100cm thick, topZ0 |
| Boundary walls |32 BlockAll cube actors, angle θ=i×11.25°, centre(1360cosθ,1360sinθ,130), yawθ, scale(.55,2.8,2.6):55cm radial×280cm tangent×260cm high |
| Wall inner face | Radius1332.5cm at each wall centre; polygon corners/overlap differ from a perfect circle |
| Existing collision pillars | Every fourth wall location:8 cylinders atR1360, centreZ270, scale(1.1,1.1,5.4): radius55cm,height540cm,inner extremeR1305cm |
| Player reset | Root(−450,0,95), yaw0°; base capsule radius34cm/half-height90cm |
| Boss reset | Root(300,0,128), yaw180°, actor scale1.35; nominal scaled capsule radius45.9cm/half-height121.5cm |
| Initial separation |750cm /7.5m, along the X axis |
| Interior obstacles | None: no colliding altar, stairs, debris, graves or central pillars |

Floor, boundary boxes and eight cylinders use BlockAll. Fighter body/costume decorative meshes are noncolliding; capsules and engine weapon queries retain combat authority. Arena walls block the camera; fighter capsules explicitly ignore the camera channel. No new walkable area or combat boundary is authorized by the design sheet.

Existing noncolliding dressing (`DressArena`): three96-segment bronze floor rings atR360/780/1210cm;16 radial420cm inlays centredR995;16 outer dark-stone blocks centredR1420,Z350,size160radial×135tangent×700high;16 iron ribs atR1330,Z330,size10×145×600;16 bronze accents;8 emissive spheres atR1290,Z295. Floor inlays sit approximately0.4–0.5cm aboveZ0 and must not become physical trip edges.

## Camera constraints

Gameplay FOV75°. Default spring arm500cm, socket offset(0,45,100); at close lock-on separation it interpolates toward620cm and a pair midpoint target, socket offset reducing towardzero. Collision probing is enabled, radius16cm. Free-view pitch is clamped−55° to25°; locked desired pitch−35° to15°, with manual locked offsets yaw±25°/pitch±12°. Lock breaks beyond2400cm separation. Outfit inspection cameras are different and must not validate gameplay framing.

Because the arena diameter exceeds the24m lock-break distance, opposite-edge fighters can already lose lock. Do not enlarge the arena and assume targeting still works. Existing walls already retract the camera near the perimeter; retaining them preserves that limitation rather than certifying ideal framing. Test both tangential movement beside a wall and looking toward/away from the centre before accepting replacement wall art. New tall opaque foreground slabs can obscure the camera even without collision.

For the DCC overview, show a dashed camera envelope up to620cm behind a representative player, plus the collision wall. It is a review overlay, not a demand to widen the playable floor. Keep proposed overhead elements aboveZ800cm over the central disk until real worst-pitch camera tests establish clearance. This height is a proposed art constraint, not a current ceiling: the existing arena has no roof collider.

## Proposed original court — unchanged collision footprint

A circular funerary court for the Funeral Regent: pale ash-limestone fighting floor, worn radial burial inscriptions, dark ribbed perimeter, sealed witness niches and a recessed royal judgment apse. The Regent's blue skull flames remain the brightest saturated blue elements; peripheral lamps stay warm, low and restrained. The court must frame the characters rather than compete with the hook tell.

Exact drafting layout:

- Centre(0,0,0). Draw the physical floorR1400 and all existing32 wall/eight pillar collider outlines as a separate labelled overlay.
- Mark **R1200cm as an unobstructed art zone**: continuous flat floor, no raised altar, loose rubble, tomb lid, chains across the ground, interior columns, railings or stairs. This is a conservative design guide, not a new smaller combat boundary. Preserve the full current playable extent outside it.
- Entry motif on−X axis; judgment apse on+X. These are visual orientation cues beyond the existing boundary, not functional doorways or player-accessible rooms. Existing wall collision remains continuous; a real entrance/door would be a separate approved gameplay change.
- Put16 repeating funerary bays on22.5° increments, aligned with current dressing. Existing eight collider pillars remain on45° increments. Shape new buttress art around/behind their silhouettes so the actual collision is visually legible.
- Place niche interiors, sarcophagi, seals and the apse outside the current wall, preferablyR1450cm and beyond. Any art protruding inward must be checked against the exact collider and camera, not merely the safe-disk guide. Do not place apparently reachable loot or doorways behind an invisible barrier.
- Use three worn floor bands at the existingR360/780/1210cm locations for construction continuity. They are flush material/inlay treatment, not arena hazards or promised indicators of attack range.
- Optional broken upper arcade/crown silhouette atZ800–1000cm; no hanging chain or banner across the overhead view of the fighters. No enclosed ceiling, new collision or fog volume is required for the first draft.

Recommended four review views: orthographic floorplan with collision overlay; player spawn camera toward+X; close-range side-on locked framing; player near outer wall looking inward. A beauty render without those views is insufficient to approve arena integration.

## Chain, sword and skull lanes

Keep the full interior free so a committed hook can travel straight, miss visibly and pull only along a clear swept route. Do not add central cover solely for visual variety: it changes the already-planned hook obstruction/cancellation problem and sword spacing. Decorative chain links, skull flames and floor script must not acquire hidden collision.

The previous hook proposal is still not implemented: zero damage on catch, bounded reel to a safe standoff, release before a separately avoidable stab, cancellation on wall/interruption/death/reset. Arena drafting should preserve space for both lateral walking escape and a300cm roll; these do not imply a fixed approved hook reach. Hook maximum range remains a combat-design variable, not something the floorplan invents. The three skulls stay behind the boss silhouette during chain actions; no new skull AI or arena hazards.

The current weapon path spans14–148cm in its local sword frame and the boss actor scales that presentation; the actual query radius/pose remains engine-owned. Floor decoration must not be presented as an exact sword-hit boundary. Validate blade-wall occlusion and near-wall pull/stab before integrating any replacement perimeter art.

## Rendering and storage approach

Current arena lighting already includes a shadowed movable key directional light (intensity3), a nonshadowed fill directional(intensity2), a skylight(.65),8 nonshadowed point lights(intensity1800,attenuation600cm) and nonvolumetric height fog(density.012,start distance700cm). Do not layer a new lighting rig over it by default. First draft should propose replacement visuals within those light counts, not add shadowed lights to every niche.

Use shared modular meshes and instancing for repeated bays/inlays. Opaque stone/metal first; limit masked banners and avoid broad transparent fog/flame sheets at gameplay-camera height. Budget proposal: a small repeating bay set and one hero apse, shared materials/trim textures, no scan pack or large environment download. Any numerical triangle/texture budget is provisional until the DCC draft and actual viewport costs are measured.

Latest Claude-revamp performance evidence is shared-machine and already has variable p95; old V13 numbers do not certify additional arena headroom. Later integration requires same-build baseline/candidate720p performance runs, camera/roll/collision checks and actual clips. Respect10GB total under `unreal/`,24GiB free reserve, one heavy job at a time and practical cache-regeneration headroom. Drafting this document did not reclaim files, run tests or change the playable build.

## Explicit alternatives outside this first draft

An elongated nave, raised dais, central grave cluster, destructible pillars, chain-catching statues, projectile-cover niches, functioning doorway or expanded radius all change gameplay/camera/collision assumptions. They may be illustrated as separately labelled future alternatives only. The primary design01 sheet uses the current circular collision footprint unchanged.
