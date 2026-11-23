# Bellbreaker smeltery walkthrough — independent QA

2026-11-16. **In progress; no actual Unreal acceptance yet.** This new medieval smeltery supersedes the rejected cathedral-foundry study. Its old Blender renders are not evidence of the new Unreal walkthrough. Boss implementation, combat tuning and AI remain outside scope.

## Preservation and isolation

`artifacts/art/bellbreaker-smeltery-2026-11-16/qa-preservation.json` captures 53 current files including two available package PAKs and the browser reference. Capture followed initial opt-in implementation edits; the earlier 49-file `bellbreaker-arena-2026-11-16/qa-preservation.json` remains the actual preimplementation source baseline. At capture four old files differed: WardenEncounter.cpp, WardenMenu.cpp, WardenPrototype.cpp and WardenPrototype.h. These require scoped diff review, not a blanket unchanged claim. No final hash comparison has run yet.

First source review: opt-in BeginPlay/Tick branches bypass ordinary encounter setup/stepping; no Warden spawned, no adaptive/rehearsal controller; player retains movement/jump/roll. Pause offers Resume, Settings and Quit, not encounter restart. Launcher rejects package selection and missing imported layout/assets. Current movement still uses swept capsule steps; numerical actor counts alone do not establish working collision. All art is NoCollision, so dedicated visible boundary alignment matters.

## Early issue routed to builder

Initial hidden walls end at X±14m/Y±18m while the previous art contract reserved six further metres, preventing close approaches to distant props. Builder reports root deliberately accepts a rectangular 28×36m walkthrough (not rounded r4 combat layout), with new prop bounds at least 0.5m outside and visible coping aligned to the boundary. This resolves the intended contract only; actual imported geometry/visual alignment and viewing distances still require verification. Do not present this as the former six-metre camera reserve or a tested combat boundary.

## Required evidence gates

- Native default suite passes without altered combat definitions; dedicated isolation fixture verifies no boss/controllers/combat-stat progression and targetless locomotion.
- Actual swept travel at four edges and corners, roll/jump impacts, no floor escape; native tests must initialize world collision. Four boundary actors and BlockAll response alone are insufficient.
- Graphical player walkthrough from entry toward forge, both work bays, channel edge and reverse view. Confirm recognizable human scale, continuous level floor, visible stopping boundary, no scenery penetrations, no boss or giant scenic bell. Record actual imported asset availability rather than silently accepting blank fallback.
- Mouse camera near walls/corners at minimum/default/maximum distance; visible coping does not itself ensure camera correctness. Inspect roof and furnace during yaw/pitch, not only fixed hero views.
- Physical/graphical Esc/P pause, Settings, sensitivity/camera-distance changes, Back, Resume, cursor release and Quit; no movement while paused and no accidental encounter launch via R/Enter/debug keys. Distinguish automated fixture checks from human interaction.
- Original browser/package and combat definition hashes preserved; permitted shared wiring changes independently reviewed. No FPS claim until an actual measured engine run, no collision/fairness claim from Blender AABBs.

QA has launched no heavy processes or engine tests. Initial free space was 39,542,358,016 bytes; this is a timestamped measurement, not a reservation for later work. Builder owns coordinated native/graphical verification; final results remain pending.

## Native/code review update — before graphical import

Independently read actual `artifacts/unreal/smeltery-native-full-2026-11-16.json`: 43 succeeded, zero warnings/failures/notRun. After the F9 no-boss guard, `smeltery-native-final-focused-2026-11-16.json` records one successful dedicated test with zero warnings/failures. This is not a second full-suite run. Dedicated fixture now exercises eight-direction pawn sweeps at floor/jump height, committed rolls against boundaries, pending jump/roll through walkthrough Tick, Y15m without old circular clamp, pause→Settings→Resume and frozen combat ticks. It is not physical mouse/keyboard acceptance or rendered camera coverage.

Reviewed shared source diff: BeginPlay and Tick early opt-in branches; walkthrough action restriction, pause presentation and R behavior; F9 report guard against absent actors; declarations only otherwise. No combat timing/definitions changed in this diff. Launcher validates imported layout paths/assets and rejects packaged mode. Final preservation will compare hashes after source freeze.

Actual `final-preview.png` is a Blender render, inspected separately: continuous masonry vault/arches and recessed furnace now read as medieval construction, clear central floor and coping. Remaining broad repetitive stone fields, bright clean floor and subdued workstation detail are visible art limits; engine lighting/texture transfer remains unverified. No giant scenic bell appears in this view.

Current cleaned DCC readback reports zero triangles at area≤1e−12 for all11 modules after removing112 masonry triangles; 342,386 unique triangles and17 instances in export audit. These derived results must not overwrite raw generated-mesh failure/degenerate evidence or imply manifold/production rig/collision quality. Full generated-prop AABBs have positive axis separation from the rectangular walkthrough; furnace nearest face is3.995m beyond the rear boundary, anvil1.562m beyond sides. Near-prop inspection therefore means viewing from within the bordered central floor, not freely walking around each workstation.

Builder informed: scripted study does not exercise Shift sprint or minimum/maximum camera settings; manual review must cover these. Requested imported local bounds/orientation checks against DCC pieces to catch FBX scale/axis errors. Graphical evidence and final integrity remain pending.

## First Unreal study — orientation failure, preserved

Root's actual first graphical review found misplaced opposite-wall ember beds. Signed bounds then identified a systematic Y reflection: floor source Y−2850..3550cm became imported−3550..2850cm; all11 module bounds matched that reflected transform within0.0006cm. Matching dimensions alone had not validated orientation. This is a real failed integration, not merely a camera/art preference. Techart is correcting export basis and triangle winding; importer now requires signed-bounds assertions. Final corrected import and rendered placement remain pending.

The first scripted study's reported56.96 FPS includes15 screenshot captures and visually incorrect geometry. Preserve it as that instrumented failed study, not accepted runtime performance or an isolated comparison. Builder also corrected a directional-light priority warning and reduced overbright lights; those fixes still require actual corrected graphical review. Root manual camera/pause/settings/quit review has not yet run.

## Corrected import, manual controls and preservation

Actual corrected `import-report.json` contains11 modules with signed bounds checked against source; independently recomputed maximum reported error0.00048828125cm. `export-axis-correction.json` declares disposable-copy Y compensation and reversed winding with positive transforms; original studio scene unchanged. This resolves the measured reflection evidence; complete visual verification uses the forthcoming final localized-light study. Geometry counts are342,386 unique triangles versus562,381 placed triangles across17 instances, not interchangeable totals.

Root's actual CUA record `manual-cua.json` reports player/no boss, Esc pause→Settings→Back→Resume, W movement, Esc/Q quit; builder confirms normal exit0. This is native application interaction, not owner physical acceptance. Synthetic Shift+W, mouse orbit and changing camera distance were inconclusive; camera stayed100%. Do not claim minimum/maximum camera clearance or verified physical sprint from this session. The native sprint fixture and scripted movement are separate evidence.

Importer encountered an ICU shutdown exit1 after assets were saved. Preserve that failed process status despite later successful clean graphical runs; successful import assertions do not make the importer process exit0.

Independent preservation at16:47+08 checks all49 prior files:44 unchanged, five reviewed shared wiring changes (Encounter, Inspector, Menu, Prototype.cpp/.h). Browser reference, both available package PAKs, WardenCombat.h and WardenRegent.h hashes unchanged. This is package-PAK preservation, not a fresh exhaustive package binary audit. `qa-final-check.json` records exact scope and free36,724,404,224 bytes. Final runtime visual/timing review pending; no additional build or heavy job by QA.

## Final delivery verdict — actual Unreal walkthrough

**Ready for owner walkthrough review, with visual and physical-control limits below.** Final evidence is `artifacts/unreal/smeltery-walkthrough-2026-11-16/final-molten/`, not the earlier Blender preview, reflected first study, or superseded side-light study. Independently inspected actual final frames0360,1680,1800: human character approaches the large furnace behind visible coping; ember beds sit within its mouths; a narrow bright channel is visible along the side masonry; the toolbench and tools are legible from the traversable floor. No boss is visible. No new critical placement regression identified in these samples. Furnace relief remains soft/faceted, broad masonry repeats, hot foreground coping is bright and the floor remains comparatively clean; this is not finished-art acceptance.

The final localized change raised24 channel/basin vertices by0.2825m to a top surface0.32m, leaving384 ember vertices and other module digests unchanged according to the saved audit. Side coping remains0.18m above the liquid. Latest actual molten import signed-bounds maximum error0.0003824234cm; the other corrected module checks remain applicable. This is scenic molten metal, no hazard simulation/damage or fluid dynamics. The edited source scene has a new recorded hash; do not claim it unchanged from the pre-height scene.

Final native-cadence scripted study:1,654 samples,57.0128 FPS mean,17.5399ms mean,16.6707ms p95,23.8630ms p99,138.7783ms maximum;16 frames above33.3ms and all16 above50ms. Screenshots every2s add GPU readback/PNG overhead. These numbers characterize this31s scripted capture, not clean performance, locked60 or an optimization comparison. Report records no boss and zero combat ticks. Builder reports normal study exit0; importer ICU shutdown exit1 remains separately preserved and must not be relabelled clean.

Final independent18/18 study-manifest hashes match (15 PNGs plus route/report/timing). Rechecked browser and both package PAK hashes unchanged, and the same five permitted shared source files differ from the prior49-file baseline. No new combat-rule edits. Free space36,659,998,720 bytes at QA closeout. Exact checks are in `qa-final-check.json`.

Remaining owner review: mouse orbit, physical Shift sprint and minimum/maximum camera-distance behavior were not established by CUA; settings stayed100%. Root did observe pause/settings/back/resume/W movement/quit with clean game exit. This is an editor-game human-character environment inspection, not a combat-ready Bellbreaker arena, new boss, adaptive controller or production quality certification. Launch `./scripts/bosslab-smeltery`; existing fight and packaged game remain separate.
