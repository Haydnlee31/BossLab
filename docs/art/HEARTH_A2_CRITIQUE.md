# Hearth A2 — independent visual rejection and rebuild gate

2026-11-16. Owner rejects actual A. This is a new shape/composition rebuild, not another lighting/detail certificate. Reviewed approved `a-master-smiths-hearth.png` against actual `bounce100/frame-0300.png`. No engine/DCC jobs or implementation edits by QA. New62-file source/launcher/browser/package/project-dylib baseline: `artifacts/art/hearth-a2-2026-11-16/qa-baseline.json`.

## What failed visibly

- **Furnace identity:** reference is a heavy stepped masonry hood with distinct corner blocks, iron courses, projecting hearth and deep individual mouths. Actual is a smooth tapering bottle/cone with two rounded sockets. Surface noise and orange light cannot repair this silhouette. Replace the underlying mass and construction.
- **Working groups:** reference's bellows is a broad layered leather wedge with oak frame; actual reads as a low thin bench. Reference anvil has a crisp horn/heel on a substantial block and nearby reachable tools; actual side stations are tiny dark lumps. Require these shapes at gameplay distance before more accessories.
- **Depth/composition:** reference has near anvils/posts, overlapping midground stations and recessed rear hearth. Actual puts nearly everything on one distant wall behind a broad empty foreground. Work groups must create distinct near/middle/far layers without obstructing the agreed clear field; camera zoom alone is insufficient.
- **Architecture:** reference heavy piers, unequal portals, timber lofts and stored material break the enclosure. Actual repeats flat masonry bands and smooth ribs around a long wall. Large forms need different depth, span and load-bearing transitions. A stamped stone texture is not authored masonry construction.
- **Quench/window:** reference has a substantial basin under a damaged high opening with cool shafts, steam and localized wetness. Actual is a dark rectangular trough under a bright flat white rectangle, with a harsh lit wall patch. Match basin rim/interior, opening depth and light direction before effects.
- **Values/materials:** reference retains readable dark iron, leather folds and wood while fire is localized. Actual combines near-black side props with bright orange front wall and uniform floor. Fine shape disappears where most inventory sits. Counts do not establish readability.

## Matching camera before judging ratios

Use only the board's large hero image, approximately y55–685 of the1536×1024 board; exclude header/insets/footer. Compare to an actual render of the same aspect ratio, retaining full image without stretch. First fit camera height, yaw, pitch and FOV using floor vanishing lines, hearth arch and window corners. The generated concept has imperfect perspective; document residual mismatch rather than distort architecture to force every pixel. Freeze this review camera once approved and record its transform/FOV/actor transforms each candidate.

Maintain a **second actual gameplay camera** with normal player scale and controls. The board's tiny scale figure is not a mandate to shrink the playable knight. Do not pass art using a telephoto shot, hidden player, cropped defects or altered exposure unavailable during play. Show matched review view plus gameplay entry, both side workstations and reverse view; clay/neutral-light crops expose form independently of generated texture/baked lighting.

## Proposed screen-space targets (visual estimates, not measured test results)

These hand-estimated ranges are starting composition targets for the matched hero crop, not an automated quality score. Let W/H denote that hero viewport. Lock camera first; revise ranges openly if perspective cannot reconcile.

| Landmark/read | Reference estimate / target | Current visible failure / acceptance |
|---|---|---|
| Furnace body excluding enclosing arch | width~17–21%W; height~45–52%H | Actual~13–15%W/~30–33%H; demand broad stepped shoulders and a legible hearth base, not a taller stretched cone |
| Furnace+main enclosing arch group | ~34–38%W | Must read as one thick supported assembly with deep returns, not outline trim on a flat wall |
| Bellows broad leather/frame silhouette | ~11–15%W, beside furnace at waist-height relative to workstations | Actual almost a line; distinct folded leather thickness and tapered nozzle required |
| Right quench basin group | ~13–18%W, including thick rim/near supports | Must read as hollow heavy vessel with water inside, not black rectangle or emissive slab |
| Foreground workshop framing | substantial objects enter both lower side corners, roughly outer10–20%W each; centre remains clear | Actual essentially no near workbench/anvil layer; add real spatial groups, not billboard borders |
| Floor/rear-workplane junction | around55–62%H from top in matched hero crop | Actual~38–42%H, yielding too much uninterrupted floor; correct geometry depth/camera together |

## Reject/accept sequence

1. **Major shape gate:** actual neutral/clay furnace, bellows, anvil and quench front/side/three-quarter. Reject cone furnace, melted anvil horn, wafer bellows, sealed/fake basin, unsupported architecture. A source illustration or successful HF request is not a mesh pass.
2. **Composition gate:** actual matched-camera scene plus normal gameplay views. Hearth, bellows and quench independently recognizable at reduced thumbnail size; near/mid/far grouping visible; no giant empty wall/floor dominating by accident. Object families present but invisible count as unresolved.
3. **Material/light gate:** same views with no hidden geometry changes. Read iron/wood/leather/stone by shape and response, no baked shadow mistaken for depth, no white window rectangle replacing opening construction. Rear stations must remain readable; retain dark mood without blacking out form.
4. **Runtime gate:** actual imported signed bounds/orientation, invisible boundaries with no rectangular fence, no player/prop penetrations, sensible camera collision and no boss/AI. Existing tests preserve rules; they do not certify A likeness. Timing and human control evidence remain separate from art judgement.

No exact incidental board object is mandatory simply because a generative model drew it. Major forms and spatial hierarchy are mandatory. The bell inset stays excluded from arena furnishing. Explicitly disclose remaining rope/vegetation/fine-clutter omissions rather than replace them with generic shapes and claim reference fidelity. Accept each major group on observed shape; never substitute triangle counts, asset count, finite coordinates or passing collision tests for visual approval.

## New image-generation references and composition proposal

Independently inspected all four actual new input PNGs: stepped-furnace, oak-bellows, anvil-workstation and stock-workbay. These are imagegen references derived from the approved board, **not3D evidence**. No major illustration-level blocker to a bounded HF attempt: furnace now shows projecting pier/cap courses and supported mouths; bellows has real visual thickness/fold hierarchy and an oak frame; anvil has a horn/waist/heel on a substantial stump; stock bay groups tools, storage, rope and blades in a deep frame. They address the previous shape failures in the drawings only.

Actual output checks before acceptance:

- Furnace: mouth openings must remain hollow from oblique/side views; caps and stepped shoulders must change the silhouette. Painted mortar and baked orange embers do not prove individual stone depth or live fire. Inspect rear mass and ground contact.
- Bellows: folded edge depth, open nozzle and negative spaces beneath the lever/frame must survive. Reject a sealed cushion/flat bench with folds painted on. Static output is not working bellows mechanics.
- Anvil: retain distinct horn, narrow waist, squared heel and hardy opening; secure footing and reachable table. The pictured stump is very substantial—fit overall top to plausible waist height rather than enlarge everything to occupy the frame. Check that hammers/tongs do not become fused shelf relief.
- Stock workbay: highest reconstruction risk because thin hanging tools, rope, swords and small containers overlap densely. Require actual side depth/supports and recognizable major silhouettes; reject a textured billboard or one melted wall. Do not claim every fine illustrated implement reconstructed.

Read `COMPOSITION.md`: proposed16×18m court, deep offset giant hood, lower unequal bellows portal, angled high-window wall, closer galleries and near anvils address actual spatial shortcomings. This is a new proposal, not current engine movement/camera evidence. Architecture02 remains an unaccepted construction proof; later unrendered floor/sill edits are not visible results. Fixed entry and companion gameplay cameras are appropriate for repeat comparisons. Do not score pixel ratios across differing camera setups; use the earlier ranges only as rough composition guidance after matching framing, and prioritize actual supported forms/readability.

## Actual assembly01 / first new mesh review

Inspected actual assembly01-entry and oblique furnace/bellows mesh probes. New furnace has real stepped shoulder/piers, projecting cap courses and hollow top; bellows has actual folded-edge thickness, nozzle and frame gaps. This is substantive geometry progress over prior A. Furnace repeats mouths around its circumference and retains soft/generated hearth detail; retain that limitation rather than imply exact reference reconstruction.

Assembly01 is incomplete and unaccepted. Huge enclosing arch/close upward framing dominate; missing hood closure exposes grey background above the furnace. Bellows becomes near-black, cistern a dark bar, while frontal light washes furnace masonry. Window joins show thin bright cracks and coarse broken wedge blocks rather than a coherent deep opening. Essential corrections routed: close hood, make window returns continuous, correct camera/depth grouping, preserve material values with localized readable light and add meaningful foreground groups. Ratios cannot establish a pass while camera differs; use supported silhouettes and normal gameplay framing first.

Read-only A2 validator review: separate schema/namespace, finite vectors, positive scales and explicit floor/spawn/light/camera-proxy contract are appropriate.500cm entry camera check is a default-envelope approximation, not a guarantee for saved camera-distance settings up to1.5x or all spring-arm offsets. Actual runtime imported sweep/camera tests remain pending; source draft is not passing-test evidence. No implementation edits or heavy jobs by QA.

## Assembly02 entry / stock mesh interim

Actual stock oblique and back probes confirm a volumetric frame, shelves/logs, sword rack and rear panels rather than a flat billboard. Fine tools and edges remain softened; this is sufficient for contextual DCC inspection, not an exact recreation of every illustrated implement.

Assembly02-entry shows meaningful gains: hood background is closed, bellows folds/frame read in local light, furnace is less washed out and unequal portals create hierarchy. However the entry still shows no substantial foreground anvils/workstations despite asset availability. Requested companion gameplay/context view before accepting spatial grouping. Thin bright left-window-jamb seam and upper-right masonry split still read as construction gaps; artist notified. Large rectangular slab grids and simple cloth remain quality limits. Full assembly gate pending actual companion image; no runtime or owner acceptance.

## Pre-build collision contract review

New A2 source declares prop collision islands and separate outer camera proxies. Read-only validator checks finite positive box extents, cluster IDs and spawn-capsule separation; field boundary can ignore camera while proxy boxes block it. These are useful declarations, not proof that four or more proxies enclose the actual roof/walls or that initial camera sweep clears a prop.

Routed a substantive study risk to builder: the inherited six straight waypoint segments can now intersect new prop islands. A timer-completed capture could show a pawn stuck against one station rather than traversing the room. Once final layout exists, check segment/capsule clearance or actual waypoint progress and use a necessary detour. Verify low prop interaction during jump/roll with the existing manually controlled vertical lift; do not infer collision success from unobstructed floor tests. No build/test/clearance pass is claimed from this source review.

## Assembly06 three-view review

Independently inspected actual entry, gameplay approximation and reverse. Meaningful shape/composition gain over rejected A: projecting furnace courses, thick readable bellows, substantial foreground anvil/workbench, deep stock bay and window, irregular physical flagstone boundaries and unequal portals. The former asset-count problem is partly resolved because major tools now occupy readable foreground/midground positions. This is actual DCC evidence, not Unreal or owner acceptance.

Critical construction failures remaining in06 are the already identified wide background opening above the entry wall in reverse and the bright stair-step seam/grey upper corner right of the window in gameplay view. Artist is closing these and rerendering; no additional separate critical issue identified. After actual closure verification, proceeding to runtime integration is reasonable without claiming concept fidelity. Regular blank rear masonry, soft generated detail/wood, simple cloth and relatively flat clean surfaces remain honest quality limits; no new cosmetic loop requested.1.8m ruler is a scale aid, not a rigged player.

Builder reports source now requires explicit study waypoints and checks rotated prop boxes against segments including spawn/loop with expanded capsule envelopes; initial camera sweep is also checked. Study will record actual arrivals/distance/stall ticks. These address the earlier tour-stall risk as source design only; compiled and imported-room validation remains pending. Final baseline audit must follow build/source freeze, not this pre-build DCC review.

## Final DCC closure gate

Independently inspected `final-reverse.png`: the previously exposed grey background above/along entry returns is now backed by dark geometry. Read `final-return-readback.json`: three formerly missed reverse-view rays now hit the added raised-vault closure; the fourth already hit the framing post. This is four pixel rays and one corrected-area render, not a global watertight/collision certificate. Assembly08 entry/gameplay/reverse precede these localized entry-side closures; final-reverse documents the newer area.

Final scene hash reported32b788d212e7fc24e364273b6b4ff5e8351e57da2990fe0fa2afcf86d856d624. Major forms/composition are now sufficiently improved and the identified reverse-view construction gap sufficiently resolved to proceed to independent runtime integration checks. This is not overall reference-art or owner acceptance. Regular masonry, soft generated detail and simple surface/cloth treatment remain limitations; no additional cosmetic loop requested. Actual imported asset orientation, prop-island sweeps, camera/route coverage and preserved source/build audit remain pending.

## First actual A2 runtime — failed shading/readability review

Independently viewed cold-study0300/0600. Actual foreground anvil, thick bellows and stock bay establish meaningful runtime form gains, but furnace/anvil have harsh black facets inconsistent with the DCC views; authored small-arch front faces also form a nearly black band against bright soffits. Root/artist are diagnosing normals rather than treating this as finished material. Window clips to white and hides tracery; reverse door/wall are almost unreadable. No new separate critical construction failure identified in these two samples, but this visual gate is not passed.

0300 contains Preparing Mesh Cards(8), so retain it as cold-state evidence. Actual entry clips the furnace at left/top compared with DCC framing; do not call it a matched-camera comparison. Source correction and localized lighting remain in progress. Root reports full45/45 and actual asset trial1/1, plus movement11043.5cm/21 arrivals/six points/no boss or combat; these remain runtime-rule/route evidence and do not override shading rejection. Independent final report parsing and preservation await freeze.

## Final visual candidate — actual Unreal front/rear views

Independently inspected final-study0300/0600/1200. Small-arch front faces and reverse door/arch are now readable rather than black; distinct window openings are visible although the sill/window-side light remains strong. Foreground anvil, broad stepped furnace, folded bellows and deep stock group establish a meaningful visible shape upgrade over rejected A. No new critical construction hole or fence regression identified in these samples. This frozen candidate is suitable for owner walkthrough review once final runtime/preservation closes.

Do not claim the generated shading issue vanished completely: furnace shoulder/pier transitions and anvil/stump still show uneven facets/soft construction, stock tools/wood remain simplified, and the rear wall is regular and sparse. Window wash, overall clean floor and differing camera still prevent an exact A-board fidelity claim. Normal/material diagnosis and light fixes are distinct from new geometry or artist-quality acceptance. Final timing AO comparisons, normal human controls and hash/credential checks await completed processes; QA does not add I/O during timed runs.

## Final independent audit and performance limitation

Actual native reports independently parsed: full45/45, final arena4/4 and final imported-asset trial1/1; each zero warnings/failures/notRun. Preserve initial fixture crash and importer shutdown failures separately. Tests support scoped movement/collision/route correctness, not artistic acceptance. No jump intrusion was reproduced, so no tall pawn-only collision workaround is claimed.

Screenshot-free100% internal1280×720 timing results remain a material delivery limitation:

| Run | MeanFPS | p95ms | Frames>33.3ms |
|---|---:|---:|---:|
| A2 AO0 |28.54|77.71|580/1808|
| A2 AO1 |32.35|61.49|487/1997|
| A2 visibility0 trial, not retained default |33.09|63.69|449/2035|
| Current old-A comparison |45.34|36.37|160/2761|

These are shared-system runs with memory pressure, and added A2 scene cost also remains unresolved. AO1's faster measured run does not establish AO as an optimization. Old A was also slower than its historical59.65FPS, so neither machine contention alone nor scene cost alone is proven as the complete explanation. Do not reuse old-A historical performance for A2 or claim sustained30/60. All A2 timing reports record complete waypoint coverage; each timed route travelled25403.7cm with51arrivals. Screenshot study travelled11043.5cm with21arrivals/six waypoints. Timings contain no screenshot requests.

Final audit `artifacts/art/hearth-a2-2026-11-16/qa-final-check.json`:105/105 DCCmanifest hashes match.62 starting files checked;55 unchanged, seven expected source/launcher/build changes. Browser reference, both package PAKs and combat definitions unchanged. Three tracked Build Kit files match GitHEAD; this does not invent a pretask hash baseline for untracked files. Scoped recognizable credential/private-key pattern scan covered239 newA2 text/script/doc/runtime files with zero matches; this is not a universal secret detector and no secret values were printed.

Final process receipt independently read: normal game exit0 after231.33s, no remaining Unreal process, editor lock unassigned. Recorded31.42GBfree/6.051GB allocated under unreal at process closeout. No heavy work by QA. Final verdict is an improved, playable owner-review candidate with **significant performance and remaining visual-quality limitations**, not a completed reference-quality arena or boss-ready release. Exact manual-control observations will be recorded when supplied; do not infer them from clean exit.

## Final normal-control observation

Read exact native-CUA `normal-entry/manual-review.json`: normal pre-CUA screenshot contains full human; W movement after focus, Esc pause, keyboard Settings, Esc back, Return resume and subsequent W movement observed. Down twice selected Quit Game and Return exited; global inventory confirmed editor not running without reopening it. Initial short synthetic Esc/P did not register and a mouse Settings click did not activate; keyboard navigation did. CUA changed camera angle markedly. Physical mouse/Shift feel, settings adjustment and exhaustive camera extremes remain unverified; no settings values changed. This is actual tool-mediated UI observation, not owner physical acceptance. Final newly completed documentation received a supplemental scoped credential-pattern scan with zero matches. QA closed with the visual/performance limitations above.
