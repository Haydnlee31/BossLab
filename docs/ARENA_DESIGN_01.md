# Arena design01 — Court of the Last Witness

Branch `arena-design-01` starts from the existing `Claude-revamp` commit9e7c75b, preserving the newer playable characters. This is an original editable Blender environment draft for the Funeral Regent, not a new Unreal level or tested fight. Current game source, collision and local Revamp assets remain unchanged.

## Design

An enclosed, sunken funerary tribunal. The player enters from the petitioner's side; the Regent stands before an empty court. Sixteen pointed burial arcades and an ivory sealed oculus surround a quiet duel floor. Three blue witness lights sit in the far apse. The empty throne is offset within that apse so an existing boundary pillar does not completely hide it.

Architecture serves the boss's fight: the open central floor supports committed sword attacks, a readable straight chain throw and lateral dodges. Graves, columns, steps and throne dressing stay outside the fight disk. The warm neutral floor contrasts with dark robes and proposed blue attacks. Decorative witness lights are small, static design cues; they are not damaging skull attacks or independent AI.

The court wall is intentionally part of the composition, not an invisible barrier hidden by an outer scenic shell. Existing pillars become memorial piers within their original envelope. The chamber reads as a judgment pit overlooked by an unreachable ceremonial seat; the pit floor itself is flat. All ramps/steps in the apse are scenic, beyond the current boundary.

## Dimensions and constraints

| Element | Draft contract |
|---|---|
| Nominal existing floor |14m radius |
| Primary tactical disk |12m radius; visual planning guide |
| Proposed obstacle-free floor extent |12.8m radius, subject to geometry audit; not a new engine boundary |
| Existing wall inner face |13.325m nominal;32segments,2.6m high |
| Existing8pillars |Centres13.6m;0.55m radius;5.4m high; nearest extent13.05m |
| New scenic structural piers |Around16.8m, outside current collision; full plinth envelope in layout JSON |
| Spawns |Player(-4.5,0),boss(3,0),7.5m apart; scale references only |
| Orientation |Entry−X, apse+X |
| Vault/oculus |Around16m high; sealed8.1m-diameter ivory disk in current draft |
| Camera |Gameplay study uses75° horizontal FOV; no Unreal camera/probe acceptance implied |

The inner band cannot accommodate an uninterrupted5–6.2m camera boom. Current engine collision retracts the camera, and opposite-edge lock-on can break at24m. Those constraints remain; a roomy concept image cannot prove camera behavior. Dark walls and quiet materials must be checked with actual characters/effects later.

## Deliverables and review

- Editable scene and layout/source under `unreal/art-studio/arena-design-01/` and `unreal/art-studio/source/arena_design_01.py`.
- Actual studio renders and evidence gallery: `artifacts/art/arena-design-01/index.html`.
- [Art direction](art/arena-design-01-direction.md), [engine feasibility](art/arena-design-01-engine.md), [QA](art/arena-design-01-qa.md).

Actual source-matched dimension checks, rendered sightline review and saved-scene readback are studio evidence only. No new Unreal collision, lock-on, chain ability, character contrast, FPS or combat validation has been performed. Height rulers are scale proxies, not imported characters. Studio lighting is not a proposed runtime light budget.

## Actual draft verification

Five final views were rendered and inspected, with12actual images retained across the initial study and two corrections. The saved scene contains133,314 visible evaluated triangles and771 total objects. A scoped Z0–3m projected-triangle check found the closest nonfloor geometry at13.0578459m, outside R12.8. Eighty-one slab ray samples were atZ0 within5.96e−8m numerical tolerance; inlays use a1mm visual offset. These checks do not certify Unreal collision/camera/performance. All43 current gameplay/config/Revamp preservation hashes match the pre-task baseline.

The throne is more visible after its tangential offset, but remains partly obscured by the retained pillar. Material detail and light budgets remain draft-level. Art review accepts this for human architectural review, not final art approval.

## Next stage

Review the final arena views first. If carrying the draft into Unreal, build an opt-in graybox with the existing characters and compare original versus new arena at the same camera/performance preset. Test boundary camera retraction, target loss, all-direction rolls, wall adjacency, and proposed hook paths without changing player rules. Then refine reusable architecture modules, materials, light counts and collision only from observed results. No boss AI work is part of this arena branch task.
