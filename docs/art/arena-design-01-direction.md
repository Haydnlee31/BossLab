# Arena design01 — Court of the Last Witness

2026-11-09. Separate environment design/studio draft on `arena-design-01`, starting from the playable Claude revamp. This document does not authorize game geometry, combat, AI or character changes. The current generated Funeral Regent and moving mantle are the scale/readability reference; old rejected procedural character studies are not the asset baseline.

## Recommendation and story

Build an enclosed funerary tribunal whose court has outlived its judges. The Regent stands before an empty throne; three cold witness flames remain in the upper apse. The player enters on the former petitioner's axis. Burial recesses around the walls reveal who supplied the court's authority. No literal courthouse desks or cluttered cemetery gravestones: a solemn chamber built for public judgment, now used for a duel.

This connects the Regent's crown, mask, mourning robes and three skulls more strongly than a generic cathedral or ruined castle courtyard. Use a recognisable silhouette: tall pointed arcade below a compressed faceted dome, with one sealed ivory oculus and a deep throne recess. A complete enclosing structure is essential; the oculus is an opaque/translucent sealed stone or glass disk, not an opening to a skybox.

## Floorplan and scale proposal

Studio design dimensions are proposals, not changes to engine collision or reach. Centre is(0,0). The actual draft uses entrance−X and throne/apse+X; “south/north” below denote those conceptual entry/throne directions, not a conflicting world-axis mapping. The technical artist should record any difference from the existing playable arena before a future integration decision.

| Region | Proposed footprint / placement | Purpose |
|---|---|---|
| Primary tactical disk | Radius12m, flatZ0 | Main duel region free of columns, steps, loose props and raised trim |
| Clear floor envelope | Radius12.8m, flatZ0 | Additional clear floor up to the existing boundary band; no new scenic obstructions |
| Existing inner camera band | Radius12.8–13.325m | Retain current wall clearance; this is not room for a full6m camera boom |
| New scenic wall/arcade line | Radius16–18m; new columns at radius16.8m (minimum16.5m per source contract) | Architecture outside existing combat collision; actual runtime visibility/camera behavior unverified |
| Entrance | South wall,4m wide,6m tall | Recessed sealed bronze doors and player approach axis; threshold flush at floor |
| Throne apse | North wall recess,6m wide/3m deep | Empty throne on a perimeter-only dais; outside clear duel floor |
| Dais | Two broad shallow steps, total rise0.6m | Visual hierarchy only; if integrated later, outside reachable fight boundary |
| Arcade spring / apex | Approximately5m /8m | Monumental vertical rhythm visible from combat camera |
| Dome / sealed oculus | Vault peak16m, central disk3.5m diameter | Overhead mass/light focus without exposed sky |

```text
                         NORTH
                  [ empty throne ]
                 [ 3 witness fires ]
             / burial bays + deep apse \
           / perimeter columns / arches \
          |                               |
          |      CLEAR FLAT DUEL DISK     |
          |          diameter24m          |
          |                               |
           \ burial bays / camera buffer /
             \    sealed entry gate   /
                         SOUTH
```

Engine handoff supplied by the technical artist: existing floor radius14m,32 wall centres at radius13.6m with radial thickness0.55m and height2.6m, plus8 pillar centres at radius13.6m/radius0.55m. Preserve those as a separate collision reference, not a claim that the new scenic architecture is already integrated. The existing continuous2.6m wall must remain a visible boundary in the draft; the radius16–18m arcade is scenic space beyond that wall, not a walkable extension. The radius12m tactical disk and radius12.8m clear floor are distinct requirements.

The sketch is schematic; the actual overhead render must show the same dimensions and unobstructed region. Keep every new scenic column and plinth beyond the existing wall, within the scenic architecture band. Do not solve grandeur by filling the fight floor with tombs. If current combat boundaries are smaller, scale the proposal or keep architecture beyond them; never silently enlarge the engine-owned arena.

## Architecture: three scales, one coherent construction

**Primary mass:** octagonal chamber, deep north apse, strong entry portal and faceted vaulted roof. Four major buttress/piers frame the principal axes; intervening bays use slimmer paired supports. Rib geometry visibly meets capitals and crown ring, rather than ending in mid-air. The apse arch should be taller and wider than ordinary wall bays, establishing an unmistakable focal hierarchy.

**Secondary rhythm:** one pointed arch per perimeter bay, backed by shallow burial galleries. Each gallery contains two or three horizontal sealed recesses with plain fitted slabs and a few bronze name strips. Keep lower walls quieter so silhouettes remain readable. Upper recesses can be darker and more numerous, providing density without many freestanding objects. The throne is a narrow high-backed stone seat with an empty ivory mask-shaped relief above it, not another character statue.

**Tertiary craft:** bronze collar bands at structural junctions, restrained funerary arch relief, a few repaired stone seams and chisel wear at thresholds. Limit unique ornament to entrance, throne and three witness mounts. Repeated modules are appropriate for architecture, but vary recess depth and stone tone by bay rather than distributing random debris. Avoid an identical gold outline around every edge.

## Materials and light hierarchy

Dominant stone is charcoal-grey with warm ivory structural edges; aged bronze is a narrow structural accent; deep indigo textile belongs in recessed upper bays. The Regent's blue flame remains the strongest saturated accent. No bright cyan floor maze or wall of emissive skulls competing with the boss.

The floor uses large dark-grey fitted slabs and a restrained bronze tribunal circle, entirely flush. A slightly lighter central stone field gives dark boots/robe hems contrast. Keep value variation broad and low-frequency, with no bright cracks resembling attack warnings. Floor roughness should avoid a mirror that doubles effects and obscures foot contact.

For the studio hero shot, a soft cool overhead pool from the sealed oculus shapes the floor and mask; muted warm entrance light separates the player's silhouette; three bounded blue accents mark the distant throne. Shadows define arch depth, not crush all walls to black. For an eventual runtime implementation prefer few shared lights, opaque/masked fixtures and baked or inexpensive ambient treatment where supported. Do not assume Lumen, volumetric fog, shadowed lights per niche or dozens of translucent flames are free. These are visual intentions to benchmark later, not an FPS guarantee.

## Hero view and camera acceptance

Primary camera: entrance threshold, eye height approximately1.7m, modest wide lens(about28–35mm equivalent), looking slightly upward along the central axis. Foreground bronze doorway edges frame the arena; middle ground remains open; Regent stands short of the distant empty throne; oculus and highest arch complete the upper silhouette. Avoid an ultra-wide overhead angle that makes empty floor dominate and hides the tribunal.

Required actual draft views: entrance hero, gameplay-height view with player/Regent scale proxies, overhead floorplan, reverse view toward entry and a side bay detail. One clay/unlit view should expose real arch/vault construction. Generated reference images, if root supplies them, are targets only. Do not composite a detailed concept into an empty model render.

Acceptance: enclosure visible; throne axis unmistakable; playable floor uninterrupted; at least three distinct depth layers; boss and chain hand readable against the architecture; no camera-height columns obscuring combat inside the clear disk. Review blue effects disabled as well as enabled. Architecture must still look designed without bloom/fog.

## Lightweight implementation handoff and scope

Use modular pointed arch voussoirs, one pilaster/capital set, one burial recess, one radial wall bay and a small number of vault segments. Instance repeated pieces; reserve unique geometry for gate, throne and oculus ring. Opaque architectural silhouettes should carry most detail; avoid alpha-heavy banners/fog or thousands of individual loose stones. A compact shared material set and modest texture atlas can follow a successful blockout, not precede it.

The animation/technical-art agent owns the actual Blender environment draft and the sole heavy-job slot. Preserve character meshes, playable game, current cameras/code and the10GB/24GiB guards. No character rework, runtime collision/light changes, public deployment or AI work in this stage. Assess the actual draft before choosing runtime assets, collision, LODs or performance budgets. The environment may be visually rich without pretending that a studio render proves playable frame rate or fairness.

## Actual candidate01 hero review

Directly inspected `artifacts/art/arena-design-01/candidate-01/hero-entry.png`. The enclosure and clear flat floor are coherent, but the first view reads as an overlit generic grey hall. Equal bay rhythm and round pipe-like ribs weaken architectural hierarchy. The faithful2.6m boundary hides most of the throne and two lower witness mounts; the remaining central beige rectangle does not communicate a funerary tribunal.

Requested one focused correction: enlarge/tall-en the apse arch relative to ordinary bays; raise the outside-boundary scenic throne and three witness mounts until readable from the unchanged entrance/gameplay camera; use a dark indigo recess to isolate them. Retain the real boundary rather than lowering it for the shot. Change ribs to chamfered stone sections with visible spring blocks. Reduce broad floodlight and establish charcoal wall fields, ivory structural accents, restrained bronze and one soft overhead floor pool. Preserve readable medium-value ground and the entire clear floor. No fog, clutter or collision changes should conceal shortcomings.

Candidate01 establishes a spatial blockout only, not the intended dramatic environment, runtime camera validation or performance readiness. Corrected actual views remain pending.

## Resolved draft interpretation

The corrected architectural reading is a **sunken judgment court**: retain the existing2.6m combat boundary and place the ceremonial throne visibly elevated behind it. This is a deliberate scenic hierarchy, not lowered collision or a claim that the upper gallery is walkable. The actual draft's sealed oculus is8.1m in diameter at16.17m height, deliberately broader than the initial3.5m proposal above; those proposal dimensions are not an as-built assertion. Judge the resulting focal light and roof scale in actual corrected views.

## Actual candidate02 hero review

Directly inspected `candidate-02/hero-entry.png`. The enlarged apse, segmented stone arches and quieter lighting materially improve hierarchy. However, the newly visible faithful existing pillar blocks the empty throne on the centre axis, and unarticulated dark cylinders read as raw blockout obstacles. The throne is not accepted as readable merely because its geometry exists.

Recommended final targeted presentation correction: shift the scenic seat tangentially about2.2m within the broad apse, composing the three witness mounts around the visible seat while retaining the central institutional arch. Keep all existing collision fixed. Give existing piers restrained planar/octagonal memorial cladding, cap/base and a narrow bronze inset, without extending into the clear floor. Do not raise the throne implausibly into the roof or hide/remove the obstructing pillar. The unchanged-camera hero must reveal the actual seat/backrest and all three witness fixtures. This is an intentional asymmetric ceremonial composition, not a gameplay-boundary change.

## Actual candidate03 — architectural draft acceptance only

Inspected final `candidate-03/hero-entry.png` and `gameplay-height.png`. The enclosed sunken court, uninterrupted floor, larger apse and clad memorial piers form a coherent original architectural draft suitable for human review. The offset seat is now visible left of the central existing pier and all three witness fixtures are legible. Retain this layout rather than continue a geometry loop.

This is not finished environment art: the throne backrest remains subtle/partly occluded, wall burial slabs and indigo panels are schematic, stone fields are mostly uniform, and roof ribs remain repetitive. The view's value hierarchy improves on candidate01 but has not achieved the proposed richness or full funerary atmosphere. The gameplay-height image uses cross-shaped scale proxies, not actual characters; it cannot validate the Regent's dark robe/blue flames, real chain readability or runtime camera behavior. No runtime integration, collision test, performance result or human acceptance is inferred from these studio renders. Overhead/reverse review will be recorded separately when available.
