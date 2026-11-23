# The Last Casting — Bellbreaker arena direction

2026-11-16. Authoritative art and combat-space brief for the new arena study, not approved gameplay dimensions or a runtime implementation. Existing game, Regent arena, combat definitions and AI remain unchanged. Root handles Hugging Face generation; technical art owns actual assembly and the heavy-job slot. This document creates no models or effects.

## Identity and reference

Primary reference inspected: `artifacts/art/boss-options-2026-11-16/bellbreaker-concept.png`. Its broad human laborer, quilted ochre cloth, riveted iron harness, aged bronze bell-maul and sparse oxblood remnants define the environment's material family. The concept is a visual target, not evidence of a built boss. Do not copy its illustrative floor rubble into the playable area.

**The Last Casting** is an abandoned cathedral bell foundry: a sacred industrial hall where the final great bell cracked before it could be raised. The Bellbreaker remains its exhausted custodian. Longitudinal structure, heavy lifting apparatus and cold furnace mouths express weight, leverage and committed momentum. This must differ immediately from the Regent's circular blue-lit necromantic court: pale overcast daylight, soot, bronze and masonry; no magical floor rings, skull chandeliers, active lava or repeated flame jets.

## Shared coordinate and scale contract

XY origin is fight-floor centre; +Y points toward the boss/rear bell, −Y toward the player entrance, Z is up. Units are metres in the design document. Record actual imported/model scale separately.

| Element | Proposal | Constraint |
|---|---|---|
| Fight boundary | Rounded rectangle28m wide(X) ×36m long(Y), corner radius4m | Flat continuous surface atZ0; limits approximatelyX±14,Y±18 |
| Camera/scenic reserve | 6 m outside the entire rounded boundary; bounding envelope 40 × 48 m | No scenic props inside reserve; proposed clearance, not validated camera travel |
| Outer hall | Approximately 46 m X × 58 m Y, with additional recesses as needed | Extra outer depth houses scenic machinery; no implied walkable extension |
| Roof ribs |14–18m above floor | Enclosed structural span with high side clerestories; avoid low hanging tackle over combat |
| Character proxies | Player1.8m, boss2.7m | Height references only; do not resize existing actors/capsules |
| Charge study |8–10m assumed travel | Design hypothesis only; no attack distance, timing or collision changes |

QA revision: the initial 3 m buffer / 38 × 48 m hall proposal is superseded and retained only as historical planning. The current reserve is 6 m, with a 40 × 48 m bounding envelope and approximately 46 × 58 m outer hall plus recesses. Do not shrink the 28 × 36 m floor to fit props.

Clearance follows the rounded boundary, not merely its four extreme coordinates. Maintain a proposed boss/weapon sweep allowance when reviewing edges; the maul dimensions and charge brake distance remain unapproved. Width28m allows lateral escape and length36m allows approach, charge and recovery studies without requiring narrow lanes. This is an intention to test, not a fairness claim.

```text
                           +Y / REAR
                  giant broken bell in cradle
                  dead lifting gantry overhead
        cold furnace                         cold furnace
        + mold bays     6 m empty reserve       + mold bays
                    ╭──────────────────╮
                    │                  │
                    │    BOSS 2.7m     │
                    │                  │
                    │  CLEAR FLAT      │
                    │   28m ×36m       │
                    │                  │
                    │   PLAYER 1.8m    │
                    ╰──────────────────╯
                     6 m empty reserve
                    sealed foundry doors
                           −Y / ENTRY
```

## Landmark placement and hierarchy

**Rear bell, first read:** a great cracked bronze bell approximately 5.6 m across (initial normalized bounding size about 5.6 m per axis; actual depth must be measured), standing upright in a stout oak timber cradle with iron bands around (0,+27,0). Its actual footprint must remain at Y ≥ +24 m, including cradle and lip. A 5.6 m deep object centred at +27 m has only 0.2 m nominal margin; measure the generated bounds rather than trusting its origin. If the asset is deeper than the rear allowance, recess the rear wall or reduce the prop; never squeeze the clear floor. Rotate the upright bell so its open fracture and dark interior face diagonally toward the entrance; do not tip the whole bell onto its side. One broad missing segment establishes damage; avoid a pile of sharp splinters. The cradle explains support and provides a dark/light contour behind the boss.

**High gantry, second read:** heavy paired hoist beams and one stopped lifting block above the rear bay, aroundZ10–13. Cables/chains terminate at visible anchors, not arbitrary ceiling points. No moving suspended mass or falling hazard in this design. Keep its silhouette separate from roof ribs and boss weapon wind-up.

**Cold side furnaces, third read:** two unequal furnace stations in outer side-wall recesses, centres approximately X±22.5 m, Y±10 m. Furnaces face inward through broad soot-dark arches, with closed hearths or cooled ash floors. Normalize each furnace to at most 5.5 m high, 5 m wide and 3 m deep, orient depth radially, and require all actual bounds and surrounds outside |X| = 20 m. Recess the wall for depth instead of consuming the reserve. No active orange fire sources competing with attack cues. One side may retain a cracked mold shell, the other an empty iron pouring cradle, giving asymmetry without random clutter.

**Architecture:** four main longitudinal bays with massive perimeter piers and high pointed/segmental masonry arches supporting iron roof ties. Column centre lines are X±22 m; complete bases, capitals and buttresses must stay outside the 6 m reserve. Buttresses belong in wall thickness. Clerestory windows form a repeated upper rhythm; lower walls have fewer, larger quiet fields. Rear bell bay is the largest opening. Entry doors are broad and visibly sealed after arrival, with a flush threshold. The roof is complete; missing glass is optional but never an excuse for a bright sky plane dominating the camera.

## Floor, boundaries and camera

Use worn pale-ash stone or cooled casting-yard slabs with flush dark joints. Former casting channels are filled level, readable as shallow color/material bands only. No open drains, pits, rails, trip-height trim, stairs, props, pillars or raised rubble inside the combat floor. A restrained continuous darker edge course makes the proposed boundary visible; do not invite players through a scenic furnace mouth that collision would silently block.

Primary hero view: from the outer entry near (0,−27,1.7), facing rear bell, moderate28–35mm equivalent lens. Foreground doorway frames the long space; clear floor is middle ground; boss proxy and bell/cradle form the rear focal pair; gantry and clerestories establish height. Keep enough floor visible to understand movement, without using an extreme wide lens that shrinks the boss.

Required actual views: entry hero, overhead labelled dimensions, lateral gameplay-height view, reverse entry view and one rear-bell/furnace detail. Include player/boss proxies in at least two views, and a neutral clay view proving real depth. A static view cannot prove camera collision; later testing must include wall-hugging, corner turns and both ends of an8–10m study charge with a representative third-person camera.

## Material and lighting targets

Colors are sRGB appearance references, not raw shader inputs:

| Family | Appearance | Placement/use |
|---|---|---|
| Ash limestone | `#77736A` / lighter worn `#AAA293` | Main floor and quiet lower wall fields; medium-value ground distinguishes dark boots |
| Sooted masonry | `#393735` | Furnace recesses, upper wall shadow and rear bell interior |
| Oxidised iron | `#484540` with sparse ochre `#795E3F` | Gantry, ties and working brackets; mostly matte |
| Aged bronze | `#8C7047`, recessed green-grey `#53605A` | Bell and limited foundry fittings; restrained highlights |
| Faded oxblood | `#4A2D2A` | One or two torn workshop standards outside action silhouettes |

The boss concept's brass shoulder and bell-maul should sit within this family but remain distinct through silhouette and local value. Broad cold overcast clerestory light gives directional form; a slightly warmer reflected floor contribution prevents grey mush. Rear bell catches one soft edge highlight. Furnace mouths stay dark but retain detail. No cyan ambience, active fire spam, thick fog hiding feet or bright streaks masquerading as telegraphs.

Surface craft follows use: soot rises above hearths, polish follows lifting contacts, oxidation collects inside casting cracks, and floor abrasion follows old transport paths. Keep most surfaces quiet. Avoid uniform cloud noise, indiscriminate scratches or gold trim on every architectural edge. Do not claim scanned/calibrated materials if generated imagery supplies only color.

## HF generation and assembly handoff

Generate or acquire bounded scenic objects separately: broken bell/cradle, cold furnace facade, hoist/gantry components and one architectural bay. Plain deterministic floor/boundary geometry supplies measured combat space; never rely on a generated whole-room mesh for collision or exact scale. Any generated prop may contain guessed rear surfaces, fused openings or baked lighting, so inspect front/side/back and underside before placement. Keep generated scenery outside the buffer and avoid duplicated baked shadows under new lighting.

A convincing draft must show the rear broken bell, clear rectangular charge field and high industrial-sacred structure immediately. Do not spend the first pass on rubble, small tools or decorative plaques. If these three large reads fail, change composition/scale before generating more objects. Root owns model/service calls and provenance; no paid escalation is implied.

## Acceptance and scope

Pass the environment design gate only when actual multiviews demonstrate a flat unobstructed rounded fight floor, a clear external buffer, coherent enclosure/support, distinctive Bellbreaker palette and readable2.7m boss/maul silhouettes. Record measured dimensions and all deviations from this proposal. Subsequent combat, camera, collision and performance gates require the actual engine, not Blender screenshots or triangle counts.

No existing game edits, boss AI, controller changes, attack implementation or runtime acceptance in this brief. Reserve/storage and one-heavy-job rules still apply. Preserve current assets and rejected trials; a new foundry study does not supersede the playable Regent encounter.


## Actual generated bell probe review — 2026-11-16

Inspected `inputs/bell-cradle.png` against the actual `bell-probe/prop-detail.png`, both under `artifacts/art/bellbreaker-arena-2026-11-16/`. The assembled mesh retains the useful large reads: upright bell crown with lifting openings, substantial missing wall segment, open dark interior and supported oak cradle with iron straps. This is a meaningful scenic asset rather than a placeholder. The actual upright timber construction supersedes the initial oblique masonry-cradle proposal.

Fine relief is substantially softer than the source image: the procession becomes rounded indistinct masses, architectural bands lose crisp profiles, bronze/patina separation is subdued and timber grain/joints simplify. Do not present this as source-image fidelity or finished close-up hero art. Its strongest role is a monumental middle-distance landmark; evaluate recognition from the real entrance/gameplay camera before requesting decorative refinements. A quiet dark rear niche and restrained edge lighting should separate the fracture and crown without disguising softness through overexposure.

The probe alone does not accept the assembled hall. Its rear wall still visibly abuts the bell, and the reported mesh maximum Y=29.707 m exceeds the original wall at29 m. The rear niche and its floor must enclose the entire measured bell/cradle bounds, keeping minimum Y≥24 m and the fight floor unchanged. Final views must show actual corrected support and clearance. Adjacent tiled floor/masonry currently reads busy and relatively bright beside the soft bell; reduce that visual competition through broader quiet floor fields, not additional small props. Await the coherent assembled view set for overall composition judgment.


### Corrected assembly review in progress

Inspected `final-v2/furnace-detail.png`: the cold hearth mouth, complete base and projecting casting spout now read clearly, and the darker desaturated floor competes less with the prop. The near pier partly hides the right furnace return; this is a contextual view, not a complete asset inspection. The visible arch support reads as an assembly, but broad smooth bases/springers/wall fields beside repeated rubble masonry and isolated horizontal stone strips still expose the draft construction method. No finished architectural-material or reference-realism pass. The complete room hierarchy remains pending the corrected entry/gameplay views. This delivery is arena planning and a first actual HF asset assembly, not engine integration, camera validation or gameplay acceptance.


Inspected corrected `final-v2/entry-hero.png`: the flat nave, generous roof span, two scale proxies and rear fractured-bell silhouette are readable. The palette separates this from the Regent encounter. However, the high blank rear wall, small distant bell, symmetric thin masonry strips and generic roof fields still read as a first studio assembly rather than a finished dramatic cathedral foundry. These are explicit art limits, not a reason to consume combat space with clutter. The actual arch tails terminate without supports at approximately X±6 m/Z8 m, outside the narrower inner frame: this is a construction defect, not intentional ruin. Parent authorized one narrow correction with proper bearing jambs/springers and removal of the competing inner frame. Final-v2 is therefore superseded for acceptance pending actual final-v3 views; no final room-quality claim yet.


## Completed first assembly — final-v3 review

Final-v3 supersedes final-v2. Independently inspected final entry hero, gameplay-height, true neutral-clay architecture and overhead plan. The rear pointed arch now terminates on full bearing piers/springers; the competing inner frame is removed. The formerly unsupported ends are visibly resolved. Clay shows a real enclosed hall, recessed foundry stations and supported rear landmark, rather than image-only architecture. The plan shows the rounded unobstructed central field and surrounding scenic reserve. These views support a **coherent first architectural draft for human review**, not finished environment art.

As-built scope reported by technical art/root: eight canonical views; saved Blender scene and GLB reloaded; bell approximately5.5m high, furnaces approximately3.03m high after radial-depth fitting (5.5m was a ceiling, not a promised furnace height). Main hall remains approximately46×58m; complete assembly including alcove floors spans approximately50×60.35m. The 28×36m/r4 fight-floor proposal remains intact. The top-plan hall label denotes the main hall, not the full asset extent. Root/QA report289 scoped static checks passing and49 source hashes matching; those checks are not an artistic judgment, full geometric collision proof or engine validation.

Confidence is good in the visible layout/landmark and repaired arch construction; low in untested gameplay camera behavior, runtime performance, collision/charge fairness and final art fidelity. The boss/player are scale proxies, not evidence of combat. Strong remaining visual limits: broad blank wall fields, repetitive masonry treatment, simple roof/hoist forms, modest distant bell emphasis, softened generated relief and limited material variety. The quieter floor improves combat readability but the room still lacks the deliberate architectural craftsmanship and atmospheric depth of a finished dark-fantasy level. Future art work should improve bay construction/material transitions and rear focal hierarchy while retaining the clear field, rather than fill the arena with clutter. No additional model call or fine-adjustment loop is requested for this planning/first-assembly milestone.

Reviewed final image SHA-256 records:

- `entry-hero.png`: `2f00b4a0725953280824a77c11664cdba30ba9ed6197ca2378fa43741ea6cc73`
- `gameplay-height.png`: `c739292fdf61a2c29264a5d0e2222a4d9931157c64b41138c21326fb76f2711e`
- `clay-architecture.png`: `2faa1055db22adeb8323a3a4380dee99cf163c66100c5cf842e4d45261dbecc3`
- `top-plan.png`: `a59f8d657482858a7f2f6e09b6df1fb7b93631e953146c8269a478d9b9fe4ab4`
