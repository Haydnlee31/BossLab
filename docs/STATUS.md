## Jump attack feel and flask heal (2026-11-10, branch regent-moveset-01)

- **Jump attack:** a snappier, higher jump. The attack hangs briefly with the blade raised, then plunges with momentum to land at contact, with a dust burst and camera kick.
- **Camera:** it follows only 40% of the jump's height.
- **Heal:** a flask-drinking animation (sword one-handed, flask to the mouth, head tips back) with crimson motes and a red flash when the heal lands. Timing and amount are unchanged.
- **Tests:** native suite 31/31. Front-view heal and jump-attack captures inspected.
- **Not done:** no owner feel test.

See [SOULS_CONTROLS.md](SOULS_CONTROLS.md).

## Souls-style controls (2026-11-10, branch regent-moveset-01)

The owner asked for Elden Ring-style controls and said the boss was unbeatable, there was no jump attack, and the roll and swing felt off.

- **Research:** community frame data gives Elden Ring's roll about 0.43–0.47 s of invincibility for 12 stamina, with roughly 45 stamina/s regeneration.
- **Roll:** 26 protected ticks (0.43 s), 320 cm, 14 stamina.
- **Stamina:** regenerates at 45/s after 0.5 s.
- **Movement:** run 420 cm/s, sprint 630 cm/s.
- **Attacks:**
  - a three-cut chain with buffered inputs;
  - roll-cancel out of late recovery;
  - F to jump, plus a jump attack, a rolling thrust and a running cut.
- **Impact:** hit-stop and camera shake on landed blows.
- **Stance:** heavy hits remove 2 stance points.
- **Regent:** now 600 hp and 6 stance, because a test bot beat the 240 hp version in 26 s.
- **Tests:** native suite 31/31. A frame-perfect bot beats the Warden in 18 s and the Regent in about 80 s using 2–3 heals.
- **Not done:** no owner feel test.

Read [SOULS_CONTROLS.md](SOULS_CONTROLS.md).

## Animation refinement round 2 (2026-11-09, branch regent-moveset-01)

- **Foot locking while walking:** plant is detected by the clip foot's speed, the foot is pinned with leg IK, and released with a 6-tick ease. Planted-foot slip is now 0–4% for both characters in every direction except the boss's sideways shuffle (13%). No pops: peak foot speed is 2.8–3.2× travel, with no forced releases.
- **Review capture:** new `capture gait`, a side-on tracking review of walking, backpedalling, circling, strafing and turning.
- **Regent:** the phase-change flames are now a low ring.
- **Tests:** 29/29.
- **Not done:** no owner feel test; generated skull still waits for the GPU quota and token.

See [ANIMATION_FEEL.md](ANIMATION_FEEL.md).

## Animation feel pass (2026-11-09, branch regent-moveset-01)

The owner said the boss and player movement felt weird. Measured first, then fixed how motion feeds the clips; combat rules unchanged.

- **Planted-foot slip:** cut from 65–70% of travel speed to 7% (player) and 10–20% (boss). Fixes: speed warping, scale-corrected blendspace speed, play rate 1.1 chosen by sweep, pose smoothing only around action changes.
- **Facing:** bosses face the player while backpedalling and strafing.
- **Turning:** turning on the spot steps the feet.
- **Judder:** render interpolation between the 60 Hz steps makes drawn motion even at any frame rate (variation 0.354 → 0.000 at 45 fps). The exact step state is restored before every step.
- **Tests:** native suite 29/29, with 3 new animation tests.
- **Not done:** no owner feel test.

Read [ANIMATION_FEEL.md](ANIMATION_FEEL.md).

## Funeral Regent refinement pass (2026-11-09, branch regent-moveset-01)

Owner: "rectify all the problems, gradually refine the moves". 
- **Props:**
  - the CC0 Poly Haven brass lantern as the censer;
  - a modelled chain link (up to 72 follow the chain);
  - an interim Blender skull with glowing eyes.
- **Sound:** 8 original procedural cues (bell, whoosh, thrust, skull wail, eruption, blink, pyre, wakes), played spatialised.
- **Readability:** a glint on the estoc point before each thrust, a censer flare in wind-ups, camera-facing flames, pools that smoulder before igniting.
- **Pacing:** new Held Thrust (delayed release), per-move pauses with punish windows, Drift Step flowing into the Dash.
- **Review tool:** new `capture regent-study`, a side-on review of every move.
- **Fixes from that review:**
  - lunges tipped backwards because the planted feet stretched the robe; the Regent now glides on long lunges, and a new pose test checks it;
  - the lantern core bloomed, and the flames read as white candles.
- **Tests:** native suite 26/26.
- **Performance:** in back-to-back benchmarks on a heavily loaded machine, the Regent was within noise of the Warden. No 60 FPS claim.
- **Remaining:** no owner feel test, sounds not listened to, interim skull, procedural poses. See [REGENT_MOVESET.md](REGENT_MOVESET.md).

## Funeral Regent moveset greybox — playable opt-in (2026-11-09, branch regent-moveset-01)

The owner chose weapon A: an estoc, plus a soul-fire censer on a left-arm chain. The owner also asked for diversified magic and a second phase. Launch: `BOSSLAB_BOSS=regent` (editor game only), with `BOSSLAB_REGENT_PHASE=2` to start at the threshold.

- **Moves:** 11 engine-owned Regent moves, boss indices 3–13: thrust, triple rite, censer arc, grave bell plus fire pool, witness-skull volley, drift step, procession dash, ashen furrow. Phase two adds: transition (hall fire turns blue), ash-step blink and funeral pyre ring.
- **Controller:** fixed, labelled rehearsal sequence; no AI.
- **Visuals:** greybox primitives, the estoc prop, and blue flame/rune materials (local `/Game/BossLab/Regent`).
- **Tests:** native suite 25/25, the default 22 plus 3 Regent tests. Each damaging move hurts a player who stands still and does 0 damage after one timed roll. Both phases use all 11 moves. Skull and pool budgets hold. Results are identical at 60 and 30 fps.
- **Captures:** two 24 s captures inspected. They led to two visual fixes: the transition burst and the pyre circle.
- **Not done:** no owner feel test, no performance measurement, no authored animation or final art.

Read [REGENT_MOVESET.md](REGENT_MOVESET.md). Next action: owner playtest, then timing tuning.

## Dungeon arena — props and souls-style pass (2026-11-09, branch arena-design-01)

Owner asked for more props and a more souls-like feel. Added CC0 Poly Haven props, converted in project-local Blender because the project has no glTF importer, and imported to `/Game/BossLab/Dungeon/Props` (local): guardian statues on plinths, a sealed great door, an entry door with a translucent fog wall, iron-gated cells, rubble, dropped arms, and candle shrines on the parapet. Also added procedural tattered banners, a cool moonlight shaft through an oculus with dust, and a muted grade. Default suite 22/22 (dungeon test: 1,030 instances, 17 lights, 0 colliding, nothing raised inside the wall line), RevampTrial 1/1. Inspected tour and exchange captures (new `capture tour`). Quieter-machine 720p run: dungeon 18.17 ms vs original 16.70 ms; shared machine, no locked-60 claim. See [ARENA_DUNGEON.md](ARENA_DUNGEON.md).

## Dungeon arena — playable opt-in (2026-11-09, branch arena-design-01)

Owner asked for "a dark dungeon with flames". Built in Unreal as `BOSSLAB_ARENA=dungeon` (editor-game only) around the unchanged floor/parapet/pillar collision, which only changes material; all added scenery is NoCollision. Fire-lit masonry hall: CC0 Poly Haven stone (world-projected), 16 piers, arches, barred cells, coal trench with flames over the parapet, pillar braziers, torches, chandelier key light, embers, fog. Default suite 22/22 (new `BossLab.Arena.DungeonIsPresentationOnly`: 921 instances, 17 lights, 0 colliding, nothing raised inside the wall line), RevampTrial 1/1 in the dungeon. Inspected 24 s exchange captures. Shared-machine 720p performance (load 40–110): dungeon 26.40 ms mean vs original 18.35 ms; the extra cost is the dynamic lights. Not isolated; no 60 FPS claim. Read [ARENA_DUNGEON.md](ARENA_DUNGEON.md). Textures and `/Game/BossLab/Dungeon` assets are local and not committed (rebuild steps in the doc). Next: decide the light-cost trade-off (fewer lights or baked wall light), then modelled props.

## Arena design01 — editable architectural draft (2026-11-09)

Created `arena-design-01` from latest `Claude-revamp`9e7c75b, preserving newer playable characters and local Revamp assets. Original Blender **Court of the Last Witness**: enclosed sunken tribunal,16burial arcades, raised/offset emptythrone,3passive witnessfixtures andsealedoculus. [Design brief](ARENA_DESIGN_01.md); actualgallery `artifacts/art/arena-design-01/index.html`; editablelatestscene `unreal/art-studio/arena-design-01/court-last-witness-03.blend` (02also retained).

Five finalactualviews/12total renders; savedsceneaudit133314visibletriangles/771objects, closestnonfloor13.05785m beyondR12.8,81slabraysZ≈0. Root43game/config/Revamphashes unchanged. Scoped studio geometry proof only: no UEimport/collision/camera/FPS test, no bossmechanic/AI changes. Gameplayheight uses75°horizontalFOV andheightmarkers, notactualcharacters. Thronepartlyoccluded andmaterials/simpleburialdetail remain; acceptablefirstarchitecturaldraftforhumanreview, notfinishedgameart. Two latestsceneskept; allownedjobsfinished.

Exactnextaction: reviewhero/gameplay/floorplan; then opt-in Unrealgraybox using existingRevampcharacters with measurednearwallcamera/lock-on/dodge/attackcontrast andsamepresetperformancecomparison before replacing livearena. Currentplayablegameunchanged.

## Claude revamp — cape/robe swing chains and opaque/cutout split (2026-11-09, branch Claude-revamp)

Owner asked to proceed with the GPU-cost research recommendations and to test the animation. Both costumes now carry `cape_*` swing-chain bones appended after the mannequin's (knight 4 back chains; Regent 4 back + 2 front), weighted onto the outermost back/front cloth layer and driven in game by a presentation-only Verlet solver on the fixed 60 Hz step (rigid-follow pull, exact bone length, body spheres, floor). Each costume has its own skeleton; the shared SK_Mannequin asset is untouched. Armour renders with an opaque material; only faces using base-colour alpha (knight 35%, Regent 5 faces) keep the masked one. Default 21/21 and RevampTrial 1/1 (now also chains present, max chain stretch 0.0000, cloth minZ 2 cm). Actual motion and 24 s exchange captures inspected: cape trails and settles, Regent robes swing; mid-roll the knight's leg-skinned coat skirt still stands up with the legs for ~5 frames. Shared-machine 720p back-to-back runs: original 16.85 ms mean/16.84 p95, revamp 17.42/22.36 (load rose 10→17 during the revamp run); not isolated, no locked-60 claim. Details: [CLAUDE_REVAMP.md](CLAUDE_REVAMP.md).

## Claude revamp — generated characters playable (2026-11-09, branch Claude-revamp)

Owner allowed free models/services and said to proceed through rigging and integration. Player knight and Funeral Regent were generated from the approved concepts with the free TRELLIS.2 Space, fitted and skinned to the mannequin skeleton in Blender (rotation-only re-rest, distance weights), imported as skeletal meshes and swapped in with `BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play`. Default 21/21 and RevampTrial 1/1 pass; actual in-game turntable/motion captures inspected; one 720p performance run 59.0 FPS mean / 17.31 ms p95 (single run, not locked 60). No cloth sim; engine sword placeholder remains; swords/skulls blocked on the free daily GPU quota. Default costume, V13 trial and packaged app unchanged. Details and next steps: [CLAUDE_REVAMP.md](CLAUDE_REVAMP.md).

## GitHub handoff —2026-11-09

Owner requested cleanup and push to public Haydnlee31/BossLab. Start at `HANDOFF.md` for portable launch, current art failure, AI boundaries and exact next task. Source-safe publication excludes Epic mannequin files, installed tools, binaries/packages/cache and referencevideo media. `docs/UNREAL_RESTORE.md` supplies local Epic restore instructions; fresh-clone Unreal build is not verified. Current playable local V13 build remains preserved.

Cleanup removed1113obsolete scene/cache files132,840,630bytes; exact deletion hashes in `artifacts/maintenance/handoff-prune-2026-11-09/manifest.json`. Latest current scene pairs and documented V10/V12/player dependencies remain. Older scene-preservation assertions below are historical. Newly checked browser tests24/24/doctor exit0; no new Unreal benchmark/build. Curated asset list in `docs/PUBLICATION_FILES.json`, bounded staging scan in `docs/PUBLICATION_AUDIT.json`. No license or deployment configured.

Initial source handoff commit `dff9e01cffbcfc1dc82f6daf08241894fe5edb9f` pushed to GitHub main and verified by matching remote hash. A clean export of that committed browser source passed24/24tests anddoctor; receipt in `artifacts/maintenance/handoff-prune-2026-11-09/clean-source-check.json`. This follow-up records verification; no new Unreal build. Underlying focal art verdict and next modeling task follow below.

## Funeral Regent focal landmarks — local gains, construction failed (2026-11-09)

Completed actual shared-landmark focal authoring:3candidates/15actualrenders, mask eye loops/nose/mouth constraints, hood and yoke surfaces; saved readback verified. Eyes/nose improve on blank cage mask, but regularized surface interpolation washes out lips, cranial surface penetrates hood crown/nape, and yoke remains unsupported-looking shelves. This is not accepted B art, fitted cloth or a production asset. Current procedural authoring workflow has not demonstrated reference-level craftsmanship; another generic repeat is not an adequate next step.

Retained latest2scenes `unreal/art-studio/regent-focal-2026-11-09/regent-focal-02.blend` and `regent-focal-03.blend`; source `unreal/art-studio/source/funeral_regent_focal.py` plus shared `regent_focal_landmarks.json`. Evidence `artifacts/art/regent-focal-2026-11-09/`; [technical report](art/funeral-regent-focal-techart.md). Root33protectedfiles unchanged including previous cage; no rig, full-body assembly, game/AI or gameplay tests. All owned jobs exited. Root resource snapshot26.642GBfree/2.743GBUnreal, guards preserved.

**Exact next action if continuing:** isolate a deliberate quad patch around eyelids/nose/lips (no global depth-field smoothing) and construct a closed hood cage from the actual cranial envelope with explicit clearance. Prove front/side facial shape and no crown/nape penetration before yoke assembly. Retain body and landmarks; do not rebuild whole character or apply a fourth minor correction to this failed field-fitting study. Visual comparison and observed fit remain necessary; topology/exit0 alone cannot certify success.

## Funeral Regent connected cage — technical gain, visual gate failed (2026-11-09)

New explicit shared-loop construction replaces the rejected primitive/voxel method. Three candidates,18 actual renders and saved-scene audit completed. Final body:1connectedcomponent,0boundary/nonmanifoldedges,0degeneratecontrol/evaluatedfaces; soles exactlyZ0. Connected thumbs/limbvolume and correct handedness are real improvements. These do NOT establish self-intersection freedom, costume clearance, accepted anatomy or reference-quality shape. No rig or weights were added.

Art/root/QA still reject selected B neutral appearance: crude projecting mask/hood, smooth coat-like mantle, shoulder boundary intrusions and simplified anatomy. Latest2editable scenes: `unreal/art-studio/regent-cage-2026-11-09/regent-cage-02.blend` and `regent-cage-03.blend`. Source `unreal/art-studio/source/funeral_regent_cage.py`; evidence `artifacts/art/regent-cage-2026-11-09/`; [technical report](art/funeral-regent-cage-techart.md). Root31protectedsource/config/V13 hashes unchanged. All owned jobs completed; root snapshot26.698GB free,2.742GB Unreal. Working game remains intact; no boss AI or gameplay tests this stage.

**Exact next action:** retain the connected body; isolate and author the mask/hood and shoulder-yoke garment pattern as focal meshes. Use shared facial/garment section landmarks and matching front/side reference comparison, then fit actual attachments onto the cage. Resolve nose/brow/cheek/jaw depth, hood opening, yoke load folds and mantle side gores before another whole-character rebuild. No fourth minor correction to this gate, no material noise or weighting to hide form failures. Rig only after neutral appearance and fit pass.

## Funeral Regent actual clay study — rejected, 2026-11-09

Three actual Blender candidates,21 rendered views and saved-scene readback completed. Initial plus two corrections failed the construction/pose gate: detached/missing forearms,19 disconnected underbody components, floating soles7.222mm above floor, mask intrusions and board-like mantle. Weighted-object counts and normalized weights do not constitute artistic/rig success. No final costume, game integration or AI work.

Latest two editable scenes retained: `unreal/art-studio/funeral-regent-clay-2026-11-09/regent-attempt-02.blend` and `regent-attempt-03.blend`. Source: `unreal/art-studio/source/funeral_regent_clay.py`. Evidence: `artifacts/art/funeral-regent-clay-2026-11-09/`; root audit verifies31protected source/config/V13 files unchanged. IndependentQA verifies its32-file baseline. See [technical report](art/funeral-regent-clay-techart.md), [art review](art/funeral-regent-clay-direction-2026-11-09.md) and [QA](art/funeral-regent-clay-qa-2026-11-09.md). All owned jobs exited. Current root snapshot26.743GB free,2.740GB allocated under Unreal; guards preserved.

**Exact next action:** start a new connected control-cage body and face, with deliberate shoulder/elbow loops and sole planes; author curved wraparound garment panels with side gores and a real shoulder yoke. Validate neutral front/side/back continuity and B silhouette BEFORE weights. Then weight one arm and one mantle panel and test cast/reel, expanding only after those pass. Do not apply a fourth cosmetic correction to the primitive/voxel study. No further concept-image generation needed; selected B remains the target. Existing playable V13 build remains unchanged.

## Funeral Regent construction handoff —2026-11-08

Selected B now has generated front/side/back construction and six motion studies, with separate art, pose, engine and independent QA notes. Primary images: `artifacts/art/funeral-regent-construction-2026-11-08/construction-corrected.png` and `motion-concept.png`. These are 2D design targets, not built boss assets. Long mantle preserved; split panels, wrist guide and front stride clarified. Initial image retained as superseded. Corrected front/back show only two visible skulls; written contract still requires exactly three. Wind-up/miss silhouettes, separate release beat and actual cloth clearance remain clay gates.

Next action: construct one consistent weighted clay Funeral Regent using `docs/art/funeral-regent-construction.md`, `funeral-regent-pose-contract.md` and `funeral-regent-engine-handoff.md`; review all angles plus cast/reel/release/thrust/miss before materials. No game changes, tests or benchmarks this stage. Boss AI remains deferred; preserve existing playable build and storage guards.

## Next stage: undead Warden concepts —2026-11-08

Owner confirms V13 launches. New request is planning only: undead boss outfit, three blue-flame skulls and chain pull/stab. Four specialists contributed; consolidated proposal: [Warden next-stage plan](art/warden-undead-stage-plan.md). Three generated outfit alternatives and attack storyboard are concepts, not models/gameplay. Owner selected B, Funeral Regent, superseding the A recommendation; chain releases before an avoidable stab. No gameplay edits or new tests/performance claims. Next action: B-specific front/side/back construction sheet and mantle/chain-arm pose plan, then clay pose review; AI remains deferred. Existing playable trial and limits below remain current.

# V13 in-game trial ready for technical review —2026-11-08

Actual current Blender geometry now runs as an opt-in player costume in Unreal Editor game mode. Default costume and original packaged app remain preserved. No boss AI, combat timing, collision authority or controller changes. This is a test integration, not production character/art acceptance.

[Actual in-game clips and launch guide](../artifacts/unreal/v13-trial-2026-11-08/index.html) · [implementation report](art/v13-unreal-test-2026-11-08.md) · [independent QA](art/character-v13-unreal-qa.md) · [final audit](../artifacts/unreal/v13-trial-2026-11-08/final-audit.json).

```sh
BOSSLAB_OUTFIT=v13 BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

Run from project root. Enter starts; WASD/mouse move/look; Tab targets; Space rolls; LMB attacks; Shift sprints; Esc opens pause/quit menu. Omit BOSSLAB_OUTFIT for original costume. V13 with package modes is explicitly rejected: the existing packaged executable is unchanged, independently hash-verified.

## Actual results and limitations

Export18groups/104,012 triangles, renderer103,356 after filtering656 degenerate faces.21 baseline native checks,1 V13 transfer/motion check and missing/malformed fallback checks1 each pass. Two corrected graphical clips each encoded/decoded180 frames; root/QA inspect actual selected attack/roll/outfit views. Same-build720p performance runs: original58.55FPS/p9517.04ms; V1359.03FPS/p9516.81ms. One sequential shared-machine run each, not isolated optimization proof or locked60; original/V13 max stalls343.49/263.37ms remain.

Rigid cloth intersects legs in some poses, glove grip is approximate, and eight palette materials omit Blender textures/shader graphs/cape embroidery. No weighted production rig or cloth simulation. Native floor samples and engine grip constraints do not certify imported visual fit. Initial gold-cape mapping error was corrected in the export only; its failed capture is retained and is not the primary review clip. Decorative blade tip extends1.159mm beyond the148cm engine endpoint; documented2mm cosmetic tolerance does not change combat reach.

## Cleanup, resources and next action

Owner-authorized pruning removed1,933 older checkpoint/archive/scene/media files totaling4,463,523,249bytes. V13/V12 checkpoint versions, approved concept, canonical sources/reports and activeV10 packed rebuild dependency remain. Paths/hashes and dependency checks: artifacts/maintenance/checkpoint-prune-2026-11-08/. Historical retired-media links/counts below are not present-day existence assertions. Completed editor compiler intermediates were separately reclaimed:20 files/888,519,212bytes; linked module verified unchanged.

The build and initial graphical startup hit the reserve; failures preserved. Scoped normal UBT trace-log access was approved, without globalsettings changes. A verified launch-only single shader worker allowed actual capture. Existing24GiB/10GB guards remain; all owned jobs exited and editor lock released. New raw capture frames were reclaimed only after video decode verification, retaining meaningful keyframes/manifests. No new large checkpoint archive.

Exact next action: human review with the opt-in command, particularly weapon-hand fit and cape/leg intersections during movement. Keep original costume for normal play if these defects interfere. Before further edits/rebuilds, check disk headroom because compiler intermediates must regenerate. Future improvement should address actual skinning/cloth fit and material transfer; do not call this final art or begin boss AI yet.

# V13 checkpoint — substantial static refinement, reference target unmet

Saved context16 is the current separate Blender study. Work continued through four initial clay construction iterations and sixteen full-character contexts, retaining failed trials. New construction includes a tapered hollow cuirass, seated pointed chest frame/seven studs, swept shoulder layers, layered gorget, rebuilt collar, coherent steel preview, shaped/hollow forearms, shield-like joint cops, fitted skirt/mail, ankle-length cape with curved supported attachment, layered gauntlets, crown shaping and a wrapped leather sword grip/continuous guard. Existing game and prior studies are preserved.

[Current actual renders](../artifacts/art/last-vigil-v13/index.html) · [editable scene](../unreal/art-studio/revision-v13-2026-11-07/last-vigil-v13-context.blend) · [technical report](art/character-v13-techart.md) · [independent QA](art/character-v13-qa.md) · [checkpoint audit](../artifacts/art/last-vigil-v13/session-audit.json).

## Verified outcome

All11 canonical720×920 views come from context16, including front/side/back, changed-region details and two clay views. Final guarded render exit0; saved readback exit0. All143 visible control meshes/170,009 vertices/166,984 faces are finite; these are not evaluated triangle counts or runtime performance evidence. Root, director and QA inspected actual images. Independent QA verifies376/376 prior-art files,28/28 gameplay files and26/26 delivery-manifest entries unchanged/matching. Launcher signal-denial/already-exited error mocks2/2 pass. No gameplay tests rerun because no gameplay changed.

The cape's exposed rectangular upper edge, pale cuirass breakthrough and sharp pouch-side bend were corrected after the first final review. The current model still falls well short of the reference's realism: heavy smooth cloth/hem puckers, sparse cape folds/graphic embroidery, fringe-like fur, simplified hands/anatomy and broad generalized finish. This is meaningful actual3D progress, not artistic acceptance, production UV/PBR, rigging, physics, animation or runtime integration. Boss AI remains deferred.

## Resource history and exact next action

A real reserve crossing interrupted context12. Its child saved images and exited, but wrapper termination raised PermissionError; this failed run remains documented. Space subsequently recovered and all context13–16 continuation ran behind the unchanged24GiB guard. Historical receipts and interim images are retained; the former unrendered13 status is superseded.

Final Unreal allocation is about4.228GB of10GB. Free space fluctuated: QA measured about181MB above24GiB; the later root audit measured about1.25GB above reserve. Consult session-audit.json for the latest exact measurement. Preserve the current source/scene/evidence and lightweight hash checkpoint; no duplicate tar archive is made. All owned guarded DCC jobs completed; artist reports no process remains. QA could not independently inventory processes because ps was denied; completed child receipts are recorded.

Next substantial work requires practical disk headroom first (about2GB additional is advisable), then a different character-art authoring pass: tailored/sculpted cloth and natural fur mass, proper UVs and deliberately painted material wear. Keep current lean proportions and useful armor/sword construction. Do not resume tiny procedural noise/ornament changes and call them reference fidelity. Do not integrate this model or begin boss AI before the art/fundamentals gates are actually ready.

# V12 geometry-first study — coherent base, unfinished UV/art

Shared front/side/back SVG design and JSON dimensions now drive a separate true3D chest–shoulder base. Final03 actual fiveclayviews and36-frame orbit pass a narrow structural gate: wrappedtorso/back, hollowgorget, armopenings and overlapping plates hold through observed angles. Threegeometrycandidates completed; no fourth. This is a coarse base, not the detailedreferencecharacter. V10 remains authoritative fullcostume.

[Study gallery and orbit](../artifacts/art/last-vigil-v12/index.html) · [design sheet](../artifacts/art/last-vigil-v12/design/upper-body-design.svg) · [technical report](art/character-v12-techart.md) · [QA](art/character-v12-qa.md).

DerivedUV cleanup removed microscopicBoolean slivers without visiblegeometrychange (4pairs, max15.56nm displacement; frozen03unchanged). AutomaticUVcharts passed numericcoverage but producedpatchwork; onecontinuous-outerUV correction improves actualmaterialcontinuity. Residualsampledoverlaps425 torso/1404 and1409 cups remain,0degenerateUVtriangles. No productionunwrap or globalcollision claim. Staticbodygapmin2.944mm,0parity-containedsamples across6lamepairs; notmotionproof.

Single originalflatsteel texture generated with built-inimagegen, savedprompt/provenance under texture-study/. It supplies color and an artisticroughness estimate, no calibratedPBR or inferrednormal/displacement. Actualfront/side/back andsamecameratwolight renders show realgeometry and relighting. Stillgenericforms/uniformfinish, no detailedcraft/referencequality. SourceSVG was not visuallyraster-previewed because browser/nativehost unavailable; actualBlenderimages were inspected.

Exact next actions: repair residualUVfoldovers beforeproductionpainting, refine structuralshape/detail againstreference usingconsistentviews, then develop deliberateornament/cloth/fur onthevalidatedbase. Do notpromote currentstudy into game or claim finishedcharacter. Frozen canonical15stills plus36-frame orbit. IndependentQA preserved206/206 V10/V11 files and28/28 gamefiles; all76manifest entries match. No owned DCCjob remains. Checkpoint artifacts/art/checkpoint-character-v12-geometry-study-2026-11-07.tar.gz; archive/hash/storage evidence in artifacts/art/last-vigil-v12/session-audit.json. No physics/rig/runtime/game/bossAI changes; existingstorageguards retained.

# V11 projection test — stopped and rejected as usable 3D

Executed the authorized method reset on one chest–shoulder–collar region: one initial attempt and two corrections, then stopped. Actual image-projected front views transfer the concept detail much more directly. Rotated/clay views expose unresolved coarse construction, stretching and missing sides. Candidate03 adds neutral arm-root supports that penetrate/occlude projected shoulder layers, including front. Candidate02 is only the better source-angle look study. None passes the multiview usable-asset gate; no PBR conversion, whole-body expansion or promotion into V10.

[All three attempts, with side and clay evidence](../artifacts/art/last-vigil-v11/index.html) · [art review](art/character-v11-direction.md) · [QA](art/character-v11-qa.md).18actual960px images:9 projected views,6clay and3UVdiagnostics. Allthree editable scenes and attempt sources preserved. Projected rivets/engraving/fur/light remain image detail, not sculpted geometry or inferred PBR. Physics disabled throughout.

V10 remains the authoritative static character fallback; existing game is untouched. This test demonstrates failure of the current coarse-geometry/projection implementation and the limits of the single source view, not a universal failure of projection painting. Do not resume a fourth correction or return to endless small shader changes.

Exact next action: retain this evidence; resolve connected sculpted chest/shoulder/collar geometry and unseen surface design before further image-assisted painting. A usable3D base and cleanUV/material authoring are unmet prerequisites. The current automated workflow has not demonstrated reference-level character quality. No paid tool, download or AI/game change. Independent QA:160/160 V10 and28/28 game files unchanged; all33 delivery file hashes match. Both source and scenes frozen, no owned jobs remain. Checkpoint: artifacts/art/checkpoint-character-v11-projection-study-2026-11-07.tar.gz; archive roundtrip/hash/storage verification in artifacts/art/last-vigil-v11/session-audit.json.

# Current refinement — V10 static collar, finish and garment

Separate V10 from frozen V9 armor has a compact padded collar with fitted retention strap, selective darker worked-steel material sampling, and authored static split-surcoat folds with curved unequal hems. Lean proportions and improved overlapping shoulders remain. Actual independent review finds useful local gains, **not reference-level realism**: mantle still resembles fringe, metal masks repeat and show bands, garment is heavy/plain, and broader anatomy/cape/construction remain simplified.

[Matched V9/V10 comparison](../artifacts/art/last-vigil-v10/comparison.html) · [gallery](../artifacts/art/last-vigil-v10/index.html) · [editable scene](../unreal/art-studio/revision-v10-2026-11-07/last-vigil-v10.blend) · [technical report](art/character-v10-techart.md) · [QA](art/character-v10-qa.md).

Eleven final material/clay views (nine720×920 and two1400×1800) plus two separately labelled mask diagnostics. Historical bare-collar/constant-oxide images excluded. Shader image persistence, mask placement and actual links verified; texture values alone were not called a quality pass.37 packed images;339 objects/430752 evaluated vertices/813036 triangles, finite.327 retained visible geometry objects unchanged; protected cameras/root/sword match. New cylindrical sample UVs have740 degenerate cap triangle areas; inherited UV limits also remain, no production unwrap.

Scoped garment vertex rays: minimum3.877mm body/mail front clearance,5.130mm tasset back clearance; none below3mm. Four strap endpoint control samples1.5mm from evaluated collar. Support-only width546.25→340.96mm excludes groom. These checks do not establish full contact, arbitrary triangle intersection, motion or physics. Static folds are authored, not simulated. Failed shelves/coarse finish/belt-overlap/clearance/strap trials preserved. No game/FPS, rig, runtime or boss AI changes.

Both source and scene frozen; no owned DCC helpers remain. Independent QA verified68/68 V9-armor baseline files and28/28 game files unchanged, and all13 final output hashes match the delivery manifest. Archive roundtrip verification is recorded in the session audit. Checkpoint target: artifacts/art/checkpoint-character-v10-2026-11-07.tar.gz; exact hashes/storage in artifacts/art/last-vigil-v10/session-audit.json.

Exact next actions: (1) replace sample projections with usable production UVs and deliberately painted metal regions; (2) author natural fur clump mass and textile edge/fold detail, replacing fringe; (3) refine belt/pouch/mail/anatomical construction before rigging. Do not repeat small procedural mask tuning as a claim of reference fidelity. Owner art acceptance remains open and boss AI stays deferred.

# Current refinement — V9 shoulder construction, cloth experiment rejected

Retained a local shoulder improvement in the separate V8-derived V9-armor scene: three lower lames per side now follow a shared tapered support surface with coherent overlap. The lean V8 proportions and original garment remain. This is a static construction improvement, not reference-quality acceptance. Eight final actual views (seven 720×920 and one 1400×1800) and two matched V8 clay baselines are frozen. Final saved scene has 348 renderable objects, 1,068,040 evaluated vertices, 1,941,420 triangles and 25 packed images.

[Matched V8/V9 comparison](../artifacts/art/last-vigil-v9-armor/comparison.html) · [editable scene](../unreal/art-studio/revision-v9-armor-2026-11-07/last-vigil-v9-armor.blend) · [platform assessment](art/platform-workflow-review-v9.md).

Seven actual Blender cloth trials did not produce an accepted replacement. The stable partial remained visually stiff; tailored variants failed strain/settling gates. All are preserved and rejected from the working armor scene. A local neutral OBJ/attachment handoff is ready under `unreal/art-studio/revision-v9-2026-11-07/neutral-handoff/`; integrity checked, external-application import untested. Owner confirms no other DCC access. No new platform, purchase, download or upload occurred.

Saved-scene audit: 311 retained original objects unchanged by geometry/material-name/transform hashes; only 12 declared old lower-lame/return objects removed. Protected camera/root/sword signatures match. New-lame nearest-arm vertex sampling: 13,572 samples, minimum 4.809 mm, no samples below −1 mm; this is not complete triangle or motion collision proof. Main scene remains an unrigged studio asset, with existing UV/material/garment limitations. No new gameplay, FPS, training or boss AI work.

Checkpoint target: `artifacts/art/checkpoint-character-v9-2026-11-07.tar.gz`; final archive/hash/storage verification is recorded in `artifacts/art/last-vigil-v9-armor/session-audit.json`. Independent QA preserved 86/86 V8 files and 28/28 game files; all final delivery hashes match. Both branches frozen, no owned DCC process remains.

Exact next action: preserve this shoulder and proportion balance; author a small front-garment study with explicit attachment, hem weight and folds, judged against matched clay views before replacing the existing garment. Do not repeat the failed solver parameter loop. Reference realism, production UV/topology, rigging/deformation and runtime integration remain open.

# Current checkpoint — V8 leaner proportion study

Owner said the character looked bulky compared with reference. SeparateV8 fits shoulder/torso/waist/arm/boot regions and their attached layers, rather than globally scaling the figure. Actual shape is visibly leaner in material and clay. Chest sampled armor width441.96→408.94mm/depth338.70→298.23mm; fauld width367.45→328.99mm/depth260→224.92mm; shoulder span739.47→628.48mm; upper-arm depth162→126.36mm. These are named sampled armor bands, not whole-body anatomical measurements. Bootwidth−9%, upperinstep−7% source construction preserves footlength/contact. Helmet width modestly fitted, height retained. Materials unchanged.

[Matched V7/V8 comparison including clay](../artifacts/art/last-vigil-v8/comparison.html) · [full-resolution figure](../artifacts/art/last-vigil-v8/hero-detail.png) · [gallery](../artifacts/art/last-vigil-v8/index.html) · [editable scene](../unreal/art-studio/revision-v8-2026-11-07/last-vigil-v8.blend).

Twelve final actual views (eleven720×920 plus one1400×1800 hero), including two supplementary head views; three V7clay baseline renders stored locally without V7writes. Fresh saved-scene verification establishes six distinct matching camera matrices/lenses, identical root scale and sword geometry/transform digest. Original stale-camera report was corrected after QA; no reframing change. Floating skirtbindings corrected; failedfit/render/audit evidence preserved.

Reload:354 renderableobjects/1,064,128vertices/1,933,572triangles/25packedimages, finite. Six slot-center rays reach backing. Scoped cape/body24144rayhits/min37.229mm/zero negatives; excludes upperattachment, outermantle/yoke, curves and arbitrary triangle intersections. No completecollision/motion/rig guarantee. V7visor projectedUV degenerates and isolated gloveUV limitations remain. No new gameplay/FPS tests, runtime integration or boss AI.

Source/scene frozen; no owned heavy helper remains. FinalCPUdraft86.56s,1400hero84.91s,audit4.18s exited0. Checkpoint artifacts/art/checkpoint-character-v8-2026-11-07.tar.gz; archive/hash/resource verification in artifacts/art/last-vigil-v8/session-audit.json. Independent QA final preservation accompanies the checkpoint.

Exact next action: preserve the improved proportion balance; replace rigid front-garment panels with believable attached weight/folds and refine shoulder overlap before more surface painting. Reference-quality art still unmet. Production topology/UV/rig/deformation/runtime work and boss AI stay deferred until readiness.

# Current checkpoint — V7 partial helmet and shoulder refinement

Separate static Blender revision now has a set-back crown, narrower cheek/jaw, folded brow edge, six actual visor breathing cuts with recessed backing and turned shoulder sheet edges. Twelve original1024-square maps place crown/visor/shoulder color, roughness, relief and diagnostic masks. Stronger localized oxide/repolish exists in loaded shader values, but actual rendered finish remains too smooth: **partial construction progress, not a realism breakthrough**.

Twelve coherent views independently reviewed: ten720×920 plus head/shoulder1400×1800 details. Reload verifies25 packed images including all12V7 maps;354 renderable objects/1,064,026 vertices/1,933,368 triangles finite. Scoped cape/body ray check24,982 hits/min34.584mm/zero negative; excludes top attachment, outer mantle/yoke, curves and arbitrary triangle intersections. Game28/28 and V6 snapshot96/96 unchanged. No gameplay tests/FPS, rig/cloth animation, integration or AI work. Prior glove UV remains isolated and unintegrated. New projected visor UV has33 degenerate triangles and is not production ready.

[Matched V6/V7 comparison](../artifacts/art/last-vigil-v7/comparison.html) · [actual gallery](../artifacts/art/last-vigil-v7/index.html) · [editable scene](../unreal/art-studio/revision-v7-2026-11-07/last-vigil-v7.blend).

Preserved failures: stamped dent rows, UV seam treated as physical wear, doubled shoulder rail, ray-API argument exception, and three diagnostic-only maps missing on reload. The nine shading maps survived; diagnostic loss did not explain weak material appearance. Actual slot-center rays6/6 reach backing; this does not prove manifold edges or animation.

Source and scene frozen; no heavy helper remains. Guarded final build124.69s, details240.30s, reload-mask probe24.88s and final audit8.28s exited0. Checkpoint: artifacts/art/checkpoint-character-v7-2026-11-07.tar.gz; exact archive/hash/storage in artifacts/art/last-vigil-v7/session-audit.json.

Exact next action: replace the current small-parameter surface loop with a focused sculpt/paint workflow on usable helmet UVs. Require a clearly improved neutral close-up before spreading treatment; mantle soft mass and glove anatomy/UV remain open. Reference-quality gate stays unmet; boss AI deferred.

# Current checkpoint — V6 construction refinement, 2026-11-07

Implemented separate static Blender refinement: shaped center breastplate and returned side fields, fitted arch and retention tabs, rounded lower return, corrected neck tether, hollow 2 mm upper fauld; surface-frame mantle fibers and unequal hanging locks. Three original 512-square panel masks drive localized roughness through explicit UV coordinates. Material effect remains subtle; armor remains too smooth and mantle too uniform for approved realism.

18 actual final views captured and reviewed (16 at720×920, two at1400×1800). Saved scene reload:344 renderable objects,1,059,336 vertices,1,924,004 triangles, finite;13 packed images. Scoped static cape/body check:24,982 ray-hit samples,34.584mm minimum,zero negatives; excludes outer mantle/yoke, attachment zone, curves and arbitrary triangle intersections. Not animation or complete collision proof. V5 snapshot234/234 and playable game28/28 preserved; no new gameplay tests/FPS, rig, cloth simulation, runtime integration or boss AI. Glove UV study explicitly deferred and unintegrated.

[Matched V5/V6 comparison](../artifacts/art/last-vigil-v6/comparison.html) · [actual gallery](../artifacts/art/last-vigil-v6/index.html) · [editable scene](../unreal/art-studio/revision-v6-2026-11-07/last-vigil-v6.blend).

Source/scene frozen. Final18-image gallery and matched V5/V6 comparison saved; comparison JavaScript syntax/paths checked, no browser-interaction claim. Guarded CPU main render156.96s, detail render239.31s and reload8.25s completed successfully. Failed drafts retained. Checkpoint: artifacts/art/checkpoint-character-v6-2026-11-07.tar.gz; archive integrity and exact storage in artifacts/art/last-vigil-v6/session-audit.json. No heavy helper remains.

Exact next action: author a localized helmet/shoulder material and form sample with visibly convincing forged surfaces under neutral lighting; correct mantle soft mass/looped fibers; finish glove anatomy and isolated UV/repaint before transfer. Preserve V6. Reference-quality gate stays open, then rig/deformation/cloth/runtime tests; boss AI remains deferred.

# Current checkpoint — V5 sustained character refinement, 2026-11-07

Owner requested continued refinement until remaining usage fell below10%. No account/context percentage was exposed: get_goal returned null remainingTokens/budget. No numeric stopping threshold is claimed. Completed a sustained multi-milestone art/diagnostic pass and saved a verified checkpoint; overall reference-quality art remains **needs work**.

Actual main asset: authored68-landmark mantle cage with shoulder support, local folds and turned hem; connected horseshoe backing;18,000 undercoat and4,800 guided longer strands; fitted dark neck seal; authored static cape/surcoat folds, panel seams, stitch curves, hems and original fine woven roughness/bump. Rigid thigh plates retain broad shapes with hidden cloth fitted behind them. Rejected carpet/poncho, crumpled-metal and script-error iterations remain preserved.17 final same-geometry images:15 at720×920 plus2 at1400×1800. High-resolution views show actual fine weave but also remaining smooth metal, combed fur/stiff backing, simplified hands and printed-looking cape decoration. No artistic acceptance.

[Matched V4/V5 comparison](../artifacts/art/last-vigil-v5/comparison.html) · [full actual gallery](../artifacts/art/last-vigil-v5/index.html) · [editable main scene](../unreal/art-studio/revision-v5-2026-11-07/last-vigil-v5.blend) · [technical report](art/character-v5-techart.md) · [independent art review](art/character-v5-direction.md) · [QA](art/character-v5-qa.md).

Isolated glove UV study: real seam-cut minimum-stretch unwrap,19 coherent islands per hand, smallest281 faces, zero degenerate triangles;2 right/1 left strict-interior overlap samples at1024 remain. Severe checker pinching improved, but residual distortion/seams remain. **Not integrated or repainted**: main model retains old projected sample UVs. Zero-overlap experiments with hundreds of tiny charts were rejected and preserved. Study scene/source/checkers accompany delivery.

Reloaded main geometry:326 renderable objects,858923 evaluated vertices,1523374 triangles, finite;10 packed images (2 original+8 retained focal samples). Static cape test initially failed1975 samples/min−67.99mm because renamed mantle yoke entered the body collider set. Object-tagged diagnosis proved all1975 hits were that backing; exact semantic exclusion restores the original declared mantle exclusion. Unchanged geometry now25236 body-ray hits/min23.486mm/zero negative. This is an audit-selection correction, not cape penetration repair. It excludes mantle/yoke, top attachment above1.515m, curves and arbitrary triangle intersections; no motion or full collision claim.

Resource incident: early completed backing run crossed24GiB between poll and exit; all heavy work stopped. Reclaimed only rebuildable local DDC Content/Buckets (338728757 logical bytes, manifest retained); owner freed/closed apps, headroom recovered and CPU work resumed. Launcher now checks reserve after child exit too. No prior evidence/personal/global files deleted. Final source/scene frozen; no heavy helper remains.10GB unreal and24GiB free guards unchanged. Optional CC0 texture research did not yield any downloaded/integrated asset.

Existing game unchanged; no new gameplay tests/FPS, rigging, cape animation, runtime integration, bossAI/adaptation/RL/model training or connection. Old motion cache does not validate revised cloth. Checkpoint: artifacts/art/checkpoint-character-v5-2026-11-07.tar.gz; exact hashes/storage in artifacts/art/last-vigil-v5/session-audit.json.

Exact next action: improve whole-figure mantle mass/edge/clump silhouettes, sewn seam compression and armor construction against the approved target. In the isolated glove study, resolve remaining overlap samples/seam distortion, verify at higher raster resolution and repaint masks before any main-scene transfer. Keep reference-quality gate open. Rig/deformation/cloth/runtime tests follow art readiness; bossAI remains deferred.

# Current checkpoint — V4 concept-fidelity refinement, 2026-11-07

Owner asks why design-to-model transfer is difficult and requests research/refinements. Diagnosis: our procedural form/material authoring is the current bottleneck, not physics or storage. A concept does not contain hidden surfaces/topology/UVs; those need deliberate authoring. [Workflow research](art/character-v4-workflow-research.md) distinguishes static mesh construction from later skeleton/cloth/collision work. No claim that research alone solves artistic skill.

Actual separate v4 narrows/reprofiles visor into central/cheek fields, builds three fitted gorget lames, tapers waist, replaces rounded shoulder caps with sloping thin descending plates, reshapes the existing pointed-arch gate, improves neutral steel hierarchy and replaces brush-ring mantle with asymmetric covered shoulder drapes.13 actual720×920 views include clay/material/detail, front/back/side and diagnostic masks. First mantle/claw, gorget-underlayer breakthrough, buried fibers and arch-script failure are preserved. Final views show real silhouette progress but **reference-quality design gate remains unmet**: flat plates, repeated fur clumps/exposed backing, broad smooth armor, pale neck insert, simple cloth and padded hands remain.

[Actual review board](../artifacts/art/last-vigil-v4/index.html) · [editable scene](../unreal/art-studio/revision-v4-2026-11-07/last-vigil-v4.blend) · [technical handoff](art/character-v4-techart.md) · [art review](art/character-v4-direction.md) · [QA](art/character-v4-qa.md).

Geometry323 renderable objects/751071 evaluated vertices/1385762 triangles, finite.9360 offline fur strands; no runtime groom/LOD claim. Retained eight1024 sample maps plus two original maps, explicit UV wiring; glove front/back projection still overlaps and934/932 projected triangles are degenerate. Whole-body steel is procedural object-coordinate material, not new painted atlas. Static cape ray check25547 hits/min31.76mm/zero negative samples excludes top attachment, mantle, curves and arbitrary triangle intersections. No rig, motion, new cloth simulation, Unreal integration, gameplay tests/FPS or bossAI/training. Existing game and prior v3 preserved.

Checkpoint: artifacts/art/checkpoint-character-v4-2026-11-07.tar.gz; final audit: artifacts/art/last-vigil-v4/session-audit.json. Actual10GB unreal/24GiB free guards retained; earlier~1m studio triangle heuristic lifted for offline fur only. Exact next action: bespoke mantle backing/fold silhouette and coherent irregular fur roots against front/side clay, fitted shoulder plate curvature/thickness, then armor/material craftsmanship and glove anatomy/production UVs. Stop relying on generic template parameter tweaks as evidence of target fidelity. Rig/runtime work and bossAI remain gated by readiness.

# Current checkpoint — V3 focal art refinement, 2026-11-07

Actual separate Blender v3 improves helmet curvature/fitted visor overlap and softens glove-root notches. Eight original1024×1024 steel/leather color, roughness, relief and placement maps are explicitly wired to authored UV coordinates. Eleven actual720×920 material/clay/mask/context views and saved-scene reload audit were completed. **Overall reference-quality art gate remains needs-work:** helmet is bowl-like, palm retains a straight padded ledge, leather is too uniform, mantle/body remain procedural. Owner approved concept direction only.

Review: [actual v3 board](../artifacts/art/last-vigil-v3/index.html), [editable scene](../unreal/art-studio/revision-v3-2026-11-07/last-vigil-v3.blend), [technical handoff](art/character-v3-techart.md), [independent art review](art/character-v3-direction.md), [QA](art/character-v3-qa.md). Glove planar UVs overlap front/back and compress side edges;997/993 projected degenerate triangles remain, so this is a localized sample, not a production atlas. Shader and diagnostic selection bugs were corrected and failed evidence retained.

Geometry:445 renderable objects,512906 evaluated vertices,958672 triangles; finite. Each glove has20854 base vertices, one closed connected component. Static cape ray sample has25822 hits,31.15mm minimum clearance, zero negative samples; attachment/mantle/curves and arbitrary triangle intersections excluded. No new cloth/rig/deformation validation. No game integration, gameplay changes/tests/FPS, boss AI/adaptation/RL/model integration or training. Earlier game evidence applies only to unchanged game.

Checkpoint: artifacts/art/checkpoint-character-v3-2026-11-07.tar.gz; final session audit: artifacts/art/last-vigil-v3/session-audit.json.10GB unreal and24GiB free guards retained. Exact next action: author palm/MCP/thenar/wrist landmarks and fitted dorsal shells in front/palm/side clay, removing straight palm ledge; then separate palm/dorsal/side UV islands. Narrower helmet brow/cheek proportions follow. Production rig/cloth/runtime work remains after art readiness; boss AI after all other gates.

# Current checkpoint — delegated character revision, 2026-11-07

Owner requested specialist-agent development and approved the separately labeled generated concept as the right visual direction. **Actual model quality remains below that target; approval was not a mesh, rig or gameplay acceptance.** Art director, technical artist and independent QA worked through preserved failed drafts and a focused helmet/glove authoring pass. Role guides, ownership, handoffs and gates are durable in board.md and docs/agent_roles/.

Actual delivered studio geometry replaces head/neck/shoulder assemblies, hands, cape/surcoat folds and sword socket; adds a restrained gate inset/repair and revises materials. The focused follow-up builds integrated helmet shells with a front eye opening and connected leather palm/thumb/web/fingers beneath dorsal plates. Actual neutral and clay views expose remaining broad planes/facets, simplified anatomy, stylized mantle and procedural materials. No finished-realism claim.

Review: [actual model board](../artifacts/art/last-vigil-v2/index.html), [approved concept — NOT BUILT](../artifacts/art/last-vigil-concept-2026-11-07/concept-target-not-built.png), [editable scene](../unreal/art-studio/revision-2026-11-07/last-vigil-v2.blend), [independent QA](art/character-v2-qa.md), [focal review](art/character-focal-authoring.md).

Final geometry audit: 445 renderable objects, 523820 evaluated vertices, 980484 evaluated triangles; finite positions and two packed original maps. Each leather glove is one connected closed base in the authored topology audit. Static cape ray check: 25827 hit samples, minimum 31.15mm back-envelope clearance, zero sampled negative clearances; excludes top attachment/mantle/curves and arbitrary triangle intersections. This is not a rig/deformation or motion certificate. New cape is static; v1 cloth clip/metrics do not validate it.

Existing playable Unreal build/source/config preserved. No new gameplay tests or FPS claim because gameplay is unchanged; old21/18 tests and59.07FPS apply only to the prior build. No boss AI/adaptation/RL/model integration or training. One labeled imagegen concept assists art direction only. No downloaded character assets, paid API/CLI calls, public deployment, global changes or persistence.10GB unreal ceiling and24GiB free reserve retained. Completed/incomplete render receipts and failed iterations preserved; no high-resolution pass used to conceal unmet art quality.

Checkpoint: artifacts/art/checkpoint-character-v2-2026-11-07.tar.gz. Session audit: artifacts/art/last-vigil-v2/session-audit.json. Exact next action: refine helmet cheek/crown and glove knuckle/web surfaces in clay against approved concept, then author one localized steel/leather/wool material sample with proper UV masks/stitching/contact wear and extend only once its quality holds. Rigging, new cape simulation and real combat deformation/performance gates come after art readiness. Boss AI remains blocked until all other readiness gates are met.

# Current — Last Vigil 3D studio draft, 2026-11-06

Owner rejected the first runtime costume for insufficient realism. A separate original Blender draft now exists: **Keeper of the Last Vigil**, with modeled armor layers/relief/mail, leather retention and repairs, a fiber collar, embroidered cape, and the legendary sword **Oathwake**. This is actual editable geometry and rendered material work. It is not yet at the supplied reference's realism: silhouette, fingers, repeated ornament and procedural wear remain too regular; bespoke sculpting/texture painting and garment construction need further work.

Review: [local visual board](../artifacts/art/last-vigil/index.html), [hero](../artifacts/art/last-vigil/hero.png), [cape study](../artifacts/art/last-vigil/cape-motion.mp4), [editable scene](../unreal/art-studio/last-vigil-motion.blend), [design/lore and evidence](LAST_VIGIL_ART_STUDY.md).

Six 1400×1800 stills inspected. All100 unique 720×900 cloth frames encoded and independently decoded;25 chronological samples plus probe/extreme frames visually inspected. Cape3185 vertices: maximum edge stretch1.04549×, minimum floor clearance0.13052m. Final geometry audit:795 renderable objects,546458 evaluated vertices,985044 triangles, finite positions,2 packed authored images. These validate artifact integrity, not artistic acceptance, gameplay movement or runtime FPS. The body turns as a rigid stand-in; no production body rig, skinning, game-ready bakes or LODs. Clip predates final shoulder caps/exposed sword marks; final scenes/stills include these cosmetic corrections. Cape/cache unchanged.

Existing Unreal source/config/binary match28 prior hashes. No combat changes or new gameplay tests; previous21 native/18 cooked and59.07FPS are historical, not validation of this draft. No AI/RL/model adapters or training. Official Blender4.5.15 is project-local with verified provenance; no external character assets, global installation, paid calls or deployment. Unreal directory approximately2.82GB including tools, within10GB; unchanged24GiB free reserve. Storage stops, two rendering deadlines and failed cloth probes preserved. Final corrected six-view render succeeded in116.74seconds with28.37GB free afterward.

Checkpoint: `artifacts/art/checkpoint-last-vigil-2026-11-06.tar.gz`. Audit: `artifacts/art/last-vigil/final-audit.json`. Exact next action: review the real front/back/detail images against the supplied references, then refine the generic helmet/shoulder silhouette, fingers, collar clumping, garment folds and localized wear in the editable studio master. Production retopology/UV baking/skinning and combat cloth checks must precede Unreal integration. Preserve the existing playable build and storage guards. Full reference-quality art acceptance remains open.

---

# Current checkpoint — Ashbound Knight, 2026-11-06

First playable original outfit delivered: 26 polygon parts / 15,448 triangles, silver plate, ivory mantle, split oxblood cape and Oathwake. Existing Epic rig/underlayer retained. Native **21/21** and graphical cooked **18/18** pass with zero test warnings/failures; final outfit/motion clips each contain 180 verified real engine frames. [Delivery, evidence and limitations](PLAYER_OUTFIT_IMPLEMENTATION.md).

**Final single-instance performance:** **59.07 FPS mean /16.7936 ms p95**, 11/3,233 frames over33.3 ms at720p performance preset. Initial37.88FPS and profiled38.19FPS runs were confounded by a second BossLab instance discovered at handoff; owner authorized closing it before this unchanged-build retest. All results retained. Supports short-session review, not locked60. First model pass remains visibly stylized: rigid clothing, no final fur/skin/texture wear or finger polish. Suitable for silhouette/material review, not final character-quality acceptance.

Packaging stopped at the unchanged reserve during duplicate-app signing. The identical staged app was subsequently signature-verified and passed the full cooked suite, captures and benchmark. Generated duplicate/cache cleanup preserved the working build; all failures retained. No claim that the last package command succeeded. Launch: `BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-play`. No AI, training, downloads, paid calls or deployment.

Checkpoint: `artifacts/unreal/checkpoint-2026-11-06-ashbound.tar.gz`; final audit: `artifacts/unreal/ashbound-2026-11-06/final-audit.json`. **Exact next action:** review final outfit/motion clips, then refine clothing shape/deformation and detail while preserving the single-instance FPS baseline. Check free reserve before rebuilding: reclaimed compiler caches will regenerate. Shipping remains unvalidated; remove runtime-mesh construction side effects from `check` before attempting Shipping. No heavy process remains running at handoff.

# Current direction — player outfit planning, 2026-11-06

Owner considers basic animation and controls in place and requests an original player outfit based on the supplied video, using one legendary two-handed sword. First proposal: [The Ashbound Knight](PLAYER_OUTFIT_PLAN.md). Re-inspected six preserved reference frames; original MP4 absent at prior path. No new model/render or game changes. Exact next action: owner review of the proposed silhouette and garment construction, then consistent concept views and a rig-compatible volume blockout. Boss animation refinement remains a separate backlog item; AI remains deferred. This planning request supersedes the previous instruction to do boss-sweep refinement next.

# Status — 2026-11-06, research and controls checkpoint

Implemented and packaged Shift sprint and Esc/P pause menu with native Resume/Quit buttons; Q quits only while paused. Research completed before further boss swing changes. Boss sword poses remain unchanged; animation quality is still open. [Research](ANIMATION_WORKFLOW_RESEARCH.md) · [Control evidence and limits](CONTROLS_2026-11-06.md).

```sh
cd /Users/haydn/Documents/BossLab
BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-play
```

Enter starts; WASD moves; hold Shift to sprint; mouse orbits; Tab targets; Space rolls in the movement direction (backwards without movement); LMB/J cuts; E heals. Esc/P opens/resumes the pause menu and releases the cursor. Click Quit or press Q while paused. [Full controls](UNREAL_RUN.md).

Final build/package succeeded. Native20/20 and cooked17/17 pass with zero test warnings/failures. Sprint simulation reaches540cm/s versus360 normal, costs12stamina/s and preserves action commitments; exhaustion requires release/repress. Pause freezes simulation and clears queued/held input. Initial19/20 controller-lookup failure remains archived.

Actual desktop Esc pause/resume, title/practice controls, LMB strike and Q exit verified. **Owner now confirms physical Resume, Shift sprint and Quit work.** Resume click-through prevention was not separately reported. Automation clicks at different requested coordinates arrived at the same stale Slate coordinate, and Shift+W emitted no Shift event. Logs are preserved as failed automation attempts; the separate owner report closes the basic physical-input verification gap.

Final performance preset720p:59.78FPS mean,16.7175ms p95,17.5479ms p99,max26.6540ms,zero of3272frames above33.3ms. Short disclosed rehearsal run, not a guarantee of locked60 or longer-session stability; pilot does not test sprint/menu.

**Exact next action:** isolate one boss broad sweep and author feet/hips/chest/shoulders/weapon together using the research workflow; compare multiple views before smoothing or applying it to other attacks. No art/AI expansion yet.

Fixed rehearsal only; statistical adaptation, RL and Laya/LLM are inactive in this fight. Historical browser PPO is headless-only; missing models remain unavailable. No training/downloads this pass.

Evidence: `artifacts/unreal/controls-2026-11-06/`. Checkpoint: `artifacts/unreal/checkpoint-2026-11-06-sprint-menu.tar.gz`. Audit: `artifacts/unreal/controls-2026-11-06/final-audit.json`. Unreal4.58GB of10GB; free27.51GB at check,24GiB reserve retained. Owned launches ended normally; no persistent jobs added. Existing build kit, browser and earlier evidence preserved.

---

# Previous checkpoint — 2026-11-06, fundamentals review candidate

The owner closed most unused apps and authorized continued refinement. Camera and moving-strike footing refinements are built, packaged, tested, visually sampled and checked through actual desktop input. **Ready for a focused human fundamentals review; overall animation/artistic acceptance remains open.** No visual-art expansion or AI milestone was started. Current evidence: [REFINEMENTS_2026-11-06.md](REFINEMENTS_2026-11-06.md).

## Verified launch and controls

```sh
cd /Users/haydn/Documents/BossLab
BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-play
```

Enter starts; WASD moves; mouse orbits; **Tab locks/unlocks, Space rolls in the movement direction, LMB/J swings the two-handed greatsword**. No-direction Space rolls backward. E heals; P/Escape pauses; R restarts (confirmation during a live fight). F5 twice switches/reset to practice dummy; F9 exports; F10 pauses/captures. [Full guide](UNREAL_RUN.md).

## Delivered and verified

- Close lock camera eases toward the pair midpoint with wider arm/oblique orbit; restores the approved distant/unlocked framing. Fighters ignore only camera queries; arena walls still retract the camera.
- Moving strike entry anchors actual foot positions; wide stances lower the pelvis as needed to keep the support foot grounded, and recovery lifts/repositions feet.
- Existing locomotion playback, acceleration/braking, late-input buffer, directional roll, hit/death response and fixed three-move rehearsal retained.
- Sword30/20/36 ticks,32damage,22stamina; roll36ticks/300cm/28stamina and protected ages4–17 inclusive unchanged. Combat rules remain engine-owned.
- **Native18/18 and cooked15/15 pass**, zero test warnings/failures. Actual contact/grips, costs/commitments, eight directions, iframe boundaries, locomotion, hurt/poise, camera walls/framing and moving entry covered. Initial16/18 and17/18 failed runs retained and explained.
- [Actual packaged24-second exchange](../artifacts/unreal/warden-refined-fundamentals.mp4):720 unique engine frames encoded and independently decoded;96 chronological samples inspected. Fixed30Hz/no audio; not FPS evidence. Same disclosed development pilot and normal rules; no human victory claim.
- Actual desktop controls verified in standalone: start, practice switch, movement, lock/unlock, strike240→208 bossHP /100→78stamina, roll recovery, pause/resume and clean quit. Evidence under `artifacts/unreal/refinements-2026-11-06/manual/`.
- Performance preset1280×720: unchanged baseline58.49FPS mean /16.9203ms p95; final59.44FPS mean /16.8215ms p95,3253 samples. Finalp99 20.7646ms,max91.4088ms,6frames over33.3ms. Useful near60FPS runs, not locked60 or isolated optimization proof. All November4 poor runs remain historical.

## Exact next action / limits

Owner play review using the launch command: judge lock-camera comfort, attack weight/recovery and directional rolling before further art or AI. If feedback identifies a defect, reproduce the specific exchange and keep original timing unless explicitly revisited. Passing tests and agent-operated input do not establish human feel acceptance. Procedural shoulder/guard motion, rigid cape/fingers, crowded-contact overlap and audio assessment remain. Performance needs longer human-session observation.

Fixed rehearsal only: no active opponent modeling, statistical adaptation, RL or Laya/LLM connection in this fight. Browser adaptation/PPO results are historical and separate; PPO is headless-only, missing model adapters unavailable. No training or downloads this pass.

Unreal directory4.52GB of10GB budget at package completion;24GiB free-space guard retained. Temporary duplicate raw frames were removed only after video/decode/hash/sample verification. No personal files, unrelated apps or machine settings changed. No public deployment, paid calls or persistent jobs. Owned game processes are stopped.

Checkpoint: `artifacts/unreal/checkpoint-2026-11-06-refined-fundamentals.tar.gz`. Audit: `artifacts/unreal/refinements-2026-11-06/final-audit.json`. Previous gameplay checkpoint and [November4 evidence](GAMEPLAY_REWORK.md) preserved.
