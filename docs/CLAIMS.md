## Main publication and Windows audit — 2026-11-14

Owner requests main push. Publication selection includes the latest frontend/audio implementation, runtime UI art/font licence and InterfaceAudio assets, plus Windows setup guidance. Remote main matched the previous gameplay branch before this change; no history rewrite is needed. Current generated game content remains local-only under the documented publication boundary. A Windows clone is not immediately playable: no executable, Mac-specific launchers, omitted asset dependencies and no Windows build/test. See docs/WINDOWS_SETUP.md and refreshed HANDOFF/README. Existing Mac regression evidence41/41 is retained in docs/ui/VALIDATION.json; this publication adds no platform verification. Next: owner frontend/audio review, then Windows asset transfer/build if requested. Git history and remote receipt establish publication completion.

## Interface audio revision — 2026-11-14

Owner reports buzzing beneath menus. Found title/pause routing left boss drone, room tone and six fire loops playing. Now title screens use a separate original sparse32-second struck-string theme with short dry confirm/adjust cues; combat ambience/music and lingering spell voices stop behind menus, pause/results are quiet. Saved volume settings apply before sound setup; mute/music/effects work independently. Boss music gain restoration after resume is covered by a component-level regression. No combat/AI changes.

Final build succeeds; native **41/41**, zero warnings/failures/notRun. Actual recorded Home→boss selection→fight→death/restart→pause→resume→pause routes inspected; initial mix was too quiet and preserved. Final menu-only44.16s recording: peak-21.073dBFS, zero clipped samples, first30s RMS-35.855dBFS; melody-envelope correlation0.983 with generated source. Paused portions in the earlier recording reach digital silence after reverb decay. These are numerical/output checks, not a claim of listening or owner acceptance.

Launch `./scripts/bosslab-game`. Listening preview: `artifacts/audio-interface-2026-11-14/menu-preview.wav`; sources/importer under `unreal/art-studio/source/audio/`; reports, initial/final recordings in the same artifact directory. Local interface assets /Game/BossLab/InterfaceAudio; no model/server/token required. No package/FPS/publication claim. All owned jobs stopped. Exact next action: owner listen to menu and cues at normal speaker/headphone level and judge timbre/balance.

## Cinematic frontend revision — 2026-11-14

Owner rejected the prior dashboard-like UI. Rebuilt Home/roster/pause/settings/Creative/results as cinematic native game menus with Cinzel, gold text focus and two actual Hugging Face FLUX.1-schnell illustrations. Home and Regent selection now use full-bleed key art; no card dashboard. Challenge/Creative rules retained. Fixed R restarting from Settings and ineligible wins being mislabeled as death.

Build succeeded; native **40/40**, zero warnings/failures/notRun. Live Home, Regent selection, Settings, Creative, pause, Challenge start, actual defeat and returnHome inspected. Real defeat545ticks/100damage/6hits/0flasks. Success and Creative exclusion are fixture-tested, not a human victory. Synthetic mouse activation remains unreliable; physical mouse acceptance pending. Project-only focus styling uses custom gold indicators.

Launch: `./scripts/bosslab-game`. Evidence/provenance: `artifacts/ui/cinematic-2026-11-14/`; design: `docs/ui/CRUCIBLE_FRONTEND.md`. Images are illustrative UI art, not new 3D assets. Two HF requests succeeded; quota consumption not measured. Token not stored; no runtime model connection. No new AI, package, FPS or public-push claim. Original package unchanged. Next: owner review of the actual game frontend and physical mouse navigation; no bossAI work.

## Crucible UI — 2026-11-14

Branded local editor-game frontend implemented,40/40 native tests on two runs. Actual Home/roster/settings/Creative/Challenge launch and defeat summary inspected. Success eligibility/statistics tested through state fixtures, not a human victory. Synthetic mouse activation unreliable; physical review pending. Final text-layout-only build follows tests. No new FPS, package or AI claim.

## Regent combat proposal — 2026-11-09

Weapon, fireball, chain and dash design saved in docs/design/REGENT_WEAPON_AND_MOVESET.md. Proposed dimensions/timings are untested. No new gameplay implementation, renders, tests or performance results. Arena draft deferred, existing assets preserved.

## Arena design01 — studio evidence only

Actualeditablearena and5finalrenders exist. Scoped floor/clearance audit passes;43currentgame/config/Revampfiles unchanged. No new Unreal arena, playabletest/FPSresult, hook/skullability orAIintegration claimed. ExistingClaude-revamp improvements remain intact; older characterfailures below are historical.

## Publication handoff —2026-11-09

New browser24/24tests anddoctor pass; source-safe staging audit passes scoped checks. Cleanup1113files132,840,630bytes, original activegame retained. GitHub source handoff does not certify clean-clone Unreal build or accepted boss art. No new Unreal/AI results.

## Landmark focal study rejected —2026-11-09

Actual sharedlandmark source,2savedscenes and15renders exist. Real almond apertures/nose gain; face/hood/yoke construction still FAILED. Final source665maskvertices/974faces/0zeroarea controls and exit0readback are integrity only; visible cranialpenetration disproves fit. Root33protectedfiles unchanged. No rig/fullbodyintegration/game/AI/performance results.

## Connected-cage results —2026-11-09

Actual new body passes scoped closed-topology/zero-area/sole checks after saved readback, with18actualstills. Neutral B art gate FAILED; no rig or weights, no proven selfintersection or costume clearance. Technical cage retained; latest2scenes saved. Root31protectedfiles unchanged. No gameplay/AI/FPS claims.

## Actual Funeral Regent clay failure —2026-11-09

Saved Blender scenes/source,19bone study rig,7pose snapshots and21actual renders exist. This is a REJECTED study, not a usable boss: underbody19components, detached limbs, soles7.222mm high, poor mantle and mask. Final process/readback exit0 means execution integrity only. Root31protectedfiles andQA32baselinefiles unchanged. No gameplay tests, runtime integration, FPS or AI results for this asset.

## Funeral Regent construction sheets —2026-11-08

Generated construction and motion targets plus specialist reviews delivered. No boss mesh, cloth, rig or animation implemented. Corrected illustration still has two visible skulls in front/back, despite three-skull design requirement; action drawings do not prove clearance or distinct windup/recovery. Actual clay gate remains open. No new gameplay tests or performance measurements.

## Undead Warden planning only —2026-11-08

Owner confirmed the existing V13 launch works. New undead outfit/chain/skull concepts are generated illustrations and written proposals, not implemented assets or combat. Four specialist reviews completed. Owner selected B — Funeral Regent; this is concept approval only, not acceptance of a built boss.  No new tests, benchmarks or learning/model results; proposed timings and budgets remain unverified. Current trial results below apply only to the existing build.

# V13 actual Unreal editor-game test —2026-11-08

Actual V13 geometry runs in the existing animated player:18 rigid groups/103,356 rendered triangles after656 zero-area faces filtered. Corrected export SHA53d5415d57f2a69df25c03dbfa35df98ffea0a957bfc5273ee78d4269c7dd7fa. Eight palette materials omit Blender texture/shader fidelity; cape uses existing cosmetic motion, not cloth simulation. Frozen studio source/scene and original packaged executable unchanged.

Native21 baseline +1 valid transfer +1 missing fallback +1 malformed fallback passed. Two corrected actual engine clips encoded/decoded180 frames each; QA inspected9 outfit and13 motion keyframes. Fixed30Hz capture is not an FPS test or human-control acceptance. Actual separate720p benchmark:58.55FPS original /59.03 V13, p9517.04/16.81ms, one sequential shared-machine run each. No optimization or locked60 claim; rare stalls remain.

Visible cape/leg intersections and approximate glove grip remain despite scoped floor/death/engine-grip checks. No production rig/skinning, cookedtrial or complete collision certification. Decorative blade reaches148.115906cm, within documented2mm visual tolerance; engine reach/timing unchanged.24/27 preexisting Source/Config files unchanged; presentation/HUD/header updates and new loader/tests are the trial scope. No AI/models/training.

Owner-authorized cleanup removed1,933 oldcheckpoint/mediafiles4.464GB while preserving V13/V12 plus liveV10 dependency and canonical code/reports. Separate completed project compiler-cache cleanup reclaimed889MB with linked binaries unchanged. Initial permission/reserve/compile/test/material failures retained; current successful evidence is explicit. Single shader worker is launch-only and observed in logs. Old packaged binary hashverified unchanged; packageV13 rejected to avoid silently runningoldcostume. All owned jobs completed.

# V13 frozen context16 — actual gains, reference realism unmet

Actual static3D construction/material changes cover armor, collar, limbs/joints, cloth/cape, sword, gauntlets and crown. Sixteen full-character contexts include preserved failures; no new generated image or external asset. Packed V12 generated steel is reused with provenance. Object-space box mapping and inherited maps are preview methods, not a clean production UV or calibrated PBR delivery.

Eleven final720×920 views are from the same context16 scene. Final guarded batch and saved readback exit0. Finite control geometry:143 meshes,170,009 vertices,166,984 faces; not evaluated triangle counts or a runtime/rig/collision certificate. Independent QA:376/376 old art,28/28 game,26/26 manifest entries match; all11 images inspected. Launcher signal error mocks2/2 passed. No new combat/FPS/model/AI tests.

Reference-quality art remains unmet: cloth/fur, anatomy and bespoke surface finish are still simplified. Targeted cape attachment/edge defects were corrected after reopening an interim freeze; no intermediate image is presented as current evidence. No physics, rig, animation, runtime or boss AI integration.

The context12 reserve interruption/PermissionError is retained as failed wrapper evidence. After storage recovered, continuation passed unchanged guards. Disk headroom was about181MB at QA and recovered to about1.25GB at the root audit; exact measurement is in session-audit.json. Checkpoint is existing scene/source/evidence plus hashes, without another large duplicate archive. Process absence is reported by artist/completed foreground job receipts; QA's independent ps was unavailable. No universal or finished-art acceptance is claimed.

# V12 geometry-first study — partial method success

Actual shared-dimension SVG/JSON design, three geometry candidates and final untextured multiview/orbit review. Geometry03 passes narrow coarse static structural gate, not reference-quality artistic acceptance. Initial coplanar plates and subsequent hidden inter-lame overlap corrected within3candidatecap. Final parity sampling finds0 contained vertices for6overlappairs; minimum sampled arm gap2.944mm. No exhaustive triangle, articulation, rig or physics claim.

Separate derivedUV cleanup merges4near-vertex pairs at100nm tolerance; measuredmaximum displacement15.56nm, closedmanifold retained. Frozen03 preserved. Initial autoUV had8collapsedtriangles; cleanup removes them, but visiblefragmentedcharts fail visualcontinuity. OneUV-onlycorrection improves actual continuity while leaving425/1404/1409 sampled overlap pixels in torso/cups. Not a clean productionunwrap.

One original flatsteel image generated using built-inimagegen, copied into workspace with exactprompt/provenance. Albedo and artisticroughness estimate, not scanned/calibratedPBR. No image-derivednormal/displacement. Actual renderedmaterial responds to changed lighting and retains real side/back coverage; not V11sourceimage illusion. Genericforms and uniformfinish remain wellbelow reference.

SVG couldn't be raster-previewed: CUA browser/native host unavailable; qlmanage and sips rendering unavailable. Sharednumeric/source checks and actualBlenderclay/material evidence are distinct. No game, bossAI, runtime, productionrig or physicswork. V10fullcharacter and V11evidence preserved. Final sessionaudit/checkpoint under artifacts/art/last-vigil-v12.

# V11 projection outcome — rejected as usable 3D

Actual initial study plus two corrections completed,18renders/3saved scenes. Image projection transfers visible reference detail at its source angle; side/oblique and clay reveal unresolved geometry and stretching. Final candidate regresses with neutral supports visibly penetrating shoulder layers. Candidate02 retained only as source-angle look study. No multiview asset pass, PBR conversion, new finished character or V10 integration.

Image emission contains baked lighting and depicted details. Engraving/rivets/fur/scratches are not inferred sculpted detail. Physics off. Existing V10/game preserved; no AI work. Current implementation failed, not proof projection painting cannot work. Hard3candidate cap respected. Evidence: artifacts/art/last-vigil-v11/index.html and session-audit.json.

# V10 refinement claims — 2026-11-07

Retained local improvements: compact padded collar with fitted strap ends and short rim; selective darker mapped steel response; authored static split-surcoat folds and curved unequal hems. Actual model remains well below reference realism. Fur reads as fringe, metal masks show repeated bands/contours, and garment remains heavy/plain. These are studio authoring studies, not production hand-painted/scanned materials.

Final evidence:11 actual material/clay views (9 at720×920,2 at1400×1800) plus2 separately labelled placement diagnostics. Historical bare-collar and constant-oxide diagnostics are excluded. No generated concept used as built evidence.

Saved scene:339 renderable objects,430752 evaluated vertices,813036 triangles,37 packed images.327 retained visible geometry objects unchanged; protected camera/root/sword equal. Evaluated collar support-only width546.25→340.96mm excludes groom; four strap endpoint control samples1.5mm from collar. Scoped garment rays minimum3.877mm to body/mail and5.130mm behind tassets; zero below3mm. Not complete collision, contact, movement or physics proof.

New cylindrical sample UVs are finite but have740 degenerate triangle areas across caps; inherited visorUV limitations remain. Not a clean atlas/production unwrap. Saved maps are8-bit; banding is observed but its cause has not been isolated. No new gameplay/FPS, rig, runtime cloth, engine integration, AI or training evidence. Existing game is preserved.

Archive and preservation evidence: artifacts/art/last-vigil-v10/session-audit.json after final freeze.

# V9 refinement claims — 2026-11-07

- Retained: static shoulder overlap refinement from frozen V8. Original garment and lean proportions retained; no failed V9 cloth in this scene.
- Rejected: seven actual cloth trials. Stable diagnostic is not approved; failed numerical/visual gates remain recorded. No successful new garment or runtime cloth claim.
- Four neutral OBJ exports and 42 attachment indices checked for finite data, valid indices and hashes. No destination-DCC import/roundtrip or production-pattern claim.
- Other DCC access unavailable; owner confirms no licenses. No platform migration, paid call, download or external upload.
- Main asset remains below reference quality, unrigged and not integrated into Unreal. No new gameplay/FPS/AI/training evidence; historical results apply only to their old builds.
- Final evidence/hash checkpoint: `artifacts/art/last-vigil-v9-armor/session-audit.json` (written after final review).

# Claims ledger

## V8 owner proportion correction — 2026-11-07

Visibly leaner regional shoulder/chest/waist/arm/boot fit, dependent garmentbinding/hardware corrected. Actual namedregion reductions and scopes in regional-fit.json. Twelve final actual images plus3V7clay baselines; saved-scene camera/lens/root/sword comparison matches with6distinct views after stale-audit correction. No framing trick or global squeeze. Geometry finite354objects/1933572triangles;25packedimages. Scopedcape24144rays/min37.229mm/zero negative,6slotrays backing; not fullcollision/animation. Overall realism remains unmet, materials unchanged, priorUVlimits retained. No game/rig/AI claim.

## V7 partial helmet/shoulder construction — 2026-11-07

Actual crown/cheek reprofiling, folded brow, six cut visor openings and returned shoulder edges. Twelve original1024-square sample maps; loaded shader contrast verified but visible aged-forged finish remains insufficient. No reference-quality or production UV/rig/runtime/AI claim. New visor projection has33 degenerate triangles; glove UV study unintegrated. Rejected regular stamps/UV seam wear/duplicate trim, ray API exception and diagnostic-only map persistence defect preserved. Twelve coherent actual views reviewed; saved-scene audit finite354 objects/1,933,368 triangles/25packedimages, all12V7maps persisted. Six tested slot rays reach backing; static cape24,982body rays/min34.584mm/zero negative within declared exclusions. Game28/28 and V6snapshot96/96 preserved. See character-v7 technical/direction/QA reports.

## V6 static construction increment — 2026-11-07

Actual fitted breastplate center/side fields, seated arch/tabs, neck tether and rounded lower return, hollow upper fauld, local-surface groom attachment and unequal hanging locks. Three original512-square panel-space roughness masks explicitly mapped; material gain is modest.18 final actual renders independently reviewed; saved-scene audit finite344 objects/1,924,004 triangles,13 packed images. Scoped24,982 static body-ray samples/min34.584mm/zero negative; not full collision or motion proof. V5 snapshot234/234 and game28/28 preserved. Overall art remains below target; no rig/animation/runtime/game/FPS/AI claim. Glove UV study remains V5 isolated/unintegrated, with residual overlaps. Failed shoulder breakthrough, neckline/lower-edge drafts, material-scope mistake and NumPy/Vector source failure preserved. See character-v6 technical/direction/QA reports.

## V5 sustained static construction and UV study — 2026-11-07

Actual68-landmark mantle cage/folds, continuous22,800-strand groom, static sewn garment details/fine weave, dark neck seal and corrected rigidplate/hiddencloth fit.17 same-geometry final renders (15×720×920,2×1400×1800) inspected across root/director/QA; higher resolution confirms remaining craftsmanship gap. Main326 objects/858923 vertices/1523374 triangles, finite. Isolated glove study19 islands each,0degenerate,2R/1L sampled overlaps at1024; not integrated or repainted. Main UV projection unchanged. Artistically still below approved reference; no rig/motion/runtime/AI claim.

Cape audit1975 negatives were all incorrectly included mantle yoke. Correct exact semantic exclusion, unchanged geometry25236 samples/min23.486mm/zero negatives; no geometry penetration repair or global collision claim. Failed audit, failed UV attempts, conformed-plate regression, source exception and reserve incident retained. Only rebuildable local DDC reclaimed; user freed resources before resumed guarded work. No remaining-token percentage was available or fabricated. See docs/art/character-v5-techart.md, character-v5-direction.md, character-v5-qa.md and artifacts/art/last-vigil-v5/session-audit.json.

## V4 concept-fidelity increment — 2026-11-07

Actual central/cheek visor, three gorget lames, tapered waist and newly angular descending shoulder plates improve silhouette. Dense conformed fur replaces the prior brush ring; neutral steel and existing pointed-arch gate improve hierarchy.13 actual720×920 clay/material/mask/multiview images retained; separate editable scene.323objects/751071verts/1385762triangles,9360 offline strands. Counts validate no artistic success. Overall model remains below target: sheet-like plates, repeated clumps on exposed backing, smooth armor and simplified fabric/anatomy. No production UV/rig/groom/motion/game/FPS/AI claim; maps are retained localized samples and body materials procedural. Failed iterations and arch exception preserved. See docs/art/character-v4-techart.md, character-v4-direction.md, character-v4-qa.md and artifacts/art/last-vigil-v4/session-audit.json.

## V3 localized form/material increment — 2026-11-07

Eleven actual720×920 views and reload audit validate a separate editable v3 scene, smoother helmet transitions/fitted overlap, softened root notches and explicitly UV-placed steel/leather sample. Eight new1024 maps packed; geometry445 objects/512906 vertices/958672 triangles. Not an artistic pass: bowl helmet, padded palm ledge, uniform leather and procedural body/mantle persist. Glove UV overlaps and degenerate projected side triangles prevent production-atlas claims. Final small leather correction was too subtle to substantiate meaningful visual gain. Failed mapping/mask probes retained. See docs/art/character-v3-techart.md, character-v3-direction.md, character-v3-qa.md and artifacts/art/last-vigil-v3/session-audit.json. No new rig/cloth/runtime/gameplay/FPS/AI/training claim.

## Specialist character revision — 2026-11-07

Three specialist agents produced an actual separate Blender revision and independently reviewed neutral/material/clay views. Owner approved the generated concept direction only. Actual mesh remains **needs work**, below reference/approved-target realism. Integrated helmet and connected leather glove geometry are implemented; prior detached brow, wrapping slit, open finger ends and observed static cape breakthroughs were corrected in inspected views. Focal topology/static clearance evidence is narrowly scoped and does not prove anatomy, motion or runtime readiness.

No production rig/skinning/LODs, new cape simulation, Unreal integration, new gameplay tests/FPS, boss AI/adaptation/RL/model connection or training. The generated concept is visibly labeled NOT BUILT and is not used as implementation evidence or texture. All prior failed iterations and intentional render stop retained. See [technical handoff](art/character-v2-techart.md), [independent QA](art/character-v2-qa.md) and [session audit](../artifacts/art/last-vigil-v2/session-audit.json).


## Current Blender studio draft — 2026-11-06

Owner rejected the previous runtime costume. Original Keeper of the Last Vigil/Oathwake now exists as editable Blender geometry/materials with six inspected1400×1800 renders and a baked100-frame cape turn study. All100 unique720×900 motion frames encoded/independently decoded;25 chronological samples plus selected extremes visually inspected. Final static/master cosmetic revision closes shoulder caps and exposes blade marks/fracture; the motion clip precedes those minor corrections, with identical cape mesh/cache/solver.

Cloth3185 vertices: max edge stretch1.04549×, minimum floor clearance0.13052m, max vertex step0.03245m. Failed collision/stretch studies retained. Geometry audit795 objects/546458 vertices/985044 triangles, finite coordinates and2 packed original maps. Actual offline rendering and physical cloth, not a generated concept-image substitute; not walking/combat animation, runtime FPS or proof of zero clipping. Body has only a rigid root turn; no production skeleton/skin weights, runtime bakes or LODs.

**The requested reference-level realism is not achieved or approved.** Repeated forms/ornament, hands, collar, garment folds and procedural material wear need bespoke authoring. Existing game remains byte-identical across28 source/config/binary hashes; no fresh gameplay tests/performance claim. Tool provenance verified, no downloaded character assets, AI/model/training or deployment. Prior reserve/deadline stops retained; final six-view render succeeds under unchanged limits. [Review and limits](LAST_VIGIL_ART_STUDY.md).

## Current playable outfit — 2026-11-06

Original Ashbound armor and Oathwake are implemented in the local Development app: 26 parts / 15,448 triangles, five materials, rigid bone attachments, controlled cape sway/folding. The Epic mannequin remains the body/rig. This is a first stylized model pass, not final skinned clothing, fur or production textures. Static OBJ export is not an animated character.

Native **21/21** and graphical cooked **18/18** pass with zero test warnings/failures. Two final 180-frame outfit/motion clips independently encode/decode; actual views and 48 motion samples inspected. Fixed30Hz captures are not FPS evidence. Capture-only PSO override avoids initial blank frames; normal startup can still warm up. Prior failures retained. Last packaging command stopped at reserve; the matching staged app independently passed signature, cooked tests and runtime checks.

Final single-instance performance preset720p: **59.07FPS mean, p95 16.7936ms, 11/3233 frames >33.3ms**. Initial37.88FPS and profiled38.19FPS runs had another BossLab process running, discovered afterward; owner authorized closing it before the unchanged-build retest. All runs retained. Supports short-session review, not locked60 or causal costume-cost attribution. Combat rules and swing choreography preserved. No new human play/feel approval, AI/RL/model connection or training. [Full delivery and limits](PLAYER_OUTFIT_IMPLEMENTATION.md).

## Player outfit proposal — 2026-11-06

Six preserved reference frames visually re-inspected; original MP4 absent at prior path, so attempted native-resolution extraction yielded no new frames. PLAYER_OUTFIT_PLAN.md distinguishes observations, uncertainty and original design. Written 3D construction map, three-view specification, sword design and provisional production targets only: no 3D mesh, concept render, changed gameplay, new tests or FPS result. Owner accepts basic animation/controls for moving into outfit planning; detailed design and broader animation quality remain reviewable.

## Research and controls — 2026-11-06

Shift sprint (540 versus 360 cm/s, 12 stamina/s) and native Slate Esc/P menu with Resume/Quit and Q exit are implemented in the standalone build. Final native 20/20 and cooked 17/17 pass; tests cover actual sprint travel, normal cost/exhaustion, roll commitment, pause clock freeze and input clearing. First native 19/20 failure retained.

Actual desktop Esc pause/resume, LMB attack and Q menu exit succeeded. **Owner subsequently confirmed physical Resume, Shift sprint and Quit work.** Two requested click positions produced identical Slate coordinates (1004,520); automation Shift+W emitted no Shift key event. These input attempts are not passing checks. Native Slate replaced legacy HUD hitboxes, but no claim that the observed automation issue was a product bug or fixed by that replacement. This is owner-reported verification, separate from the failed automation attempts. Specific Resume click-through prevention was not separately confirmed.

Online research distinguishes mesh/skinning, FK/IK, authored body mechanics and runtime playback. Source diagnosis identifies weapon-first poses plus heuristic arm/body solving; boss swing source remains byte-identical to prior checkpoint. No Control Rig migration, imported animation, mastery or resolved artistic quality claim. [Research](ANIMATION_WORKFLOW_RESEARCH.md) and [control evidence](CONTROLS_2026-11-06.md). Fixed rehearsal remains active; no new adaptation, RL, model integration or training.

Final controls performance preset720p:59.78FPS mean,p95 16.7175ms,p99 17.5479ms,max26.6540ms,0/3272frames over33.3ms. Short shared-machine fixed-rehearsal run; no sprint/menu workload, long-session guarantee or causal speedup claim. Raw evidence retained.

## Previous fundamentals review candidate — 2026-11-06

Close pair framing, camera-only fighter collision exclusion and moving-entry support-foot anchors/reach correction are in the standalone package. Native18/18 and cooked15/15 pass with zero test warnings/failures. New checks measure four-entry support drift0.000cm and ankle landing error0.002cm; camera head/foot margins at80/170/300cm, wall retraction and unlocked restoration pass. Initial failures remain archived; these metrics do not establish natural motion or complete absence of overlap.

720 unique packaged engine frames encoded/decoded,96 samples inspected; actual manual start/move/lock/cut/roll/unlock/pause/quit verified. Clip is a disclosed test pilot at fixed30Hz without audio, not a human demonstration or FPS result. Same rules and pilot; no tuning of held-out evaluations.

Performance preset720p: unchanged baseline58.49FPS mean,p95 16.9203ms; final59.44FPS mean,p95 16.8215ms,p99 20.7646ms,max91.4088ms,6/3253 frames above33.3ms. Supports focused human review, not locked60FPS, long-session stability or a proven causal speedup. Previous shared-machine regressions preserved. **Owner feel/artistic acceptance remains pending**; procedural shoulders, cape/fingers, contact overlap and audio remain limited. [Evidence](REFINEMENTS_2026-11-06.md).

No AI/RL/model integration or training added. Active fight uses fixed rehearsal; historical browser statistics/PPO are separate and missing model adapters remain unavailable.

## Historical gameplay rework — 2026-11-04

The frozen blendspace was reproduced by a new real-stride test (0.052 cm excursion,15/16 fail report preserved), then fixed by advancing actual animation time. The same assertion now measures92.149 cm. Final source rebuilt and packaged: **native16/16, cooked13/13**, zero test warnings/failures. New12-tick queue, acceleration/braking, smoother same-distance roll, grounded tuck/unfold, player hurt/boss poise, recoil/death, close-camera adjustment and fixed rehearsal pacing are implemented. Approved sword timing and roll protection/costs remain. Tests validate mechanics, not artistic quality.

Final actual packaged clip:24 seconds,720 unique frames encoded and independently decoded;96 chronological samples inspected. Agent-operated editor and standalone controls checks include movement, target lock, attacks, roll, healing, death/reset and camera recovery. [Evidence, precise limits and failures](GAMEPLAY_REWORK.md). No human acceptance or final art claim. Contact-range silhouette overlap remains.

Performance is **not cleared**: balanced25.23 FPS mean (p95 110.481 ms); opt-in performance preset40.95 then26.53 FPS (p95 49.8608 then114.549 ms). Profiled run13.13 FPS and incomplete1200-frame CSV are retained. Shared-machine contention prevents isolated attribution. Minimal-render diagnostic31.61FPS mean,p95 92.1997ms also failed smooth-review readiness; no stable30/60 FPS or proven repeatable speedup. Offline package works without a model/key. Fixed rehearsal only; adaptive statistics,RL and LLM/Laya integration remain inactive. Browser PPO evidence is historical/headless-only.


## Historical gameplay diagnosis — 2026-11-04

Owner rejects current prototype quality; not ready for visual enhancements. Current source and existing version-labeled contact sheets reviewed. Isolated compilation of actual combat state with a copied queue branch reproduces expiry for a dodge requested at strike age 85 versus acceptance one tick later; this is not an Unreal runtime/input latency test. [Review](GAMEPLAY_REVIEW_2026-11-04.md) separates confirmed mechanics, sampled observations and inferred feel issues. No gameplay changes, new full suite, fresh gameplay run or FPS benchmark. Previous mechanics passes remain valid within their scope; no quality/feel acceptance claimed.

## Historical researched directional rolling — 2026-11-03

Native **13/13**, cooked **10/10** passed. Eight headings verified with lock on/off through 16 normal queued requests; 300 cm/28 stamina each. Real-contact age-boundary test proves damage rejection at 4 and 17, damage at 3 and 18. Protection remains 14 simulation ticks (~0.233 s); no source-game numerical equivalence claimed. Travel-facing tumble now replaces the barrel-like sideways presentation.

Two actual cardinal/diagonal clips cover eight normal rolls, with combat-state protection labels and CSV proof. Each 180 fresh unique encoded/decoded frames; 48 visual samples inspected. No new FPS benchmark; previous 53.9 FPS is historical. **Artistic quality remains unapproved**; landing/turn-back, weight transfer, locomotion and provisional art still need polish. [Research, citations, evidence and limitations](SOULS_COMBAT_RESEARCH.md).

## Historical stiffness correction (owner requested further polish) — 2026-11-03

Continuous active-cut arc, evaluated idle/locomotion base, base-pose blending, hip/chest overlap, head counterbalance and clavicle/elbow articulation are packaged. Native **11/11**, cooked **8/8** pass with unchanged acceptance thresholds and a new middle-of-cut movement assertion (minimum 20.037 cm/tick). Actual motion/combat clips each have 180 unique encoded/decoded frames and 48 visually inspected samples. **Owner artistic acceptance is pending; passing tests do not establish natural motion.**

Fresh balanced 720p: 53.9 FPS mean; 18.539 ms mean / 29.6155 ms p95 (2,957 frames). Shared-machine run; no causal speedup or sustained 60 FPS claim. Approved combat windows/costs unchanged, actual blade paths retested. Close-range overlap, rigid cape/fingers and broader locomotion polish remain. No AI/model/training added. [Evidence and limitations](ANIMATION_FLUIDITY.md).

## Historical first animation refinement (owner found it stiff) — 2026-11-03

| Capability | Actual evidence | Limits |
|---|---|---|
| Motion | Hip load/drive/settle, staggered recovery, carried sword follow-through, directional tuck/landing and corrected blade clearance | Original procedural poses; provisional art/fingers, close-camera overlap and locomotion transitions remain |
| Verification | Final native 11/11, cooked 8/8; zero test warnings/failures; stricter initial 10/11 failure retained | Sampled joints/blade, not all mesh vertices or human feel approval; flat-arena clearance correction |
| Measurements | Roll max joint step 31.008 cm; final jump 0.000 cm; head minimum 20.000 cm, blade 31.941 cm | Test conditions, not arbitrary terrain |
| Footage | Two actual packaged clips, 180 fresh unique frames each, independently decoded; 48 chronological visual samples each | Six seconds each, fixed 30 Hz, no audio; not FPS or full repertoire coverage |
| Rules | Approved 30/20/36 strike and 36-tick/300 cm roll unchanged; normal costs and action acceptance traced | Blade paths changed and were retested; no new balance approval |
| Performance | 59.7 FPS mean, 16.7482 ms mean frame interval, p95 17.5266 ms (3,269 samples) at balanced 720p | Shared-machine run, no causal speedup or stable 60 FPS claim |
| Availability | Offline packaged build updated; no new downloads/models/training/persistence | Fixed rehearsal only; statistical adaptation/RL/model integration inactive |

See [ANIMATION_REFINEMENT.md](ANIMATION_REFINEMENT.md) for final artifacts, failures and limitations. Storage stop resolved after owner freed space; reserve remains 24 GiB.

## Historical fundamentals baseline — 2026-11-03

| Capability | Actual evidence | Limits |
|---|---|---|
| Playable sword/roll arena | Tab lock, Space roll, two-handed cut with actual blade sweeps, fixed three-attack rehearsal/dummy, stamina/heal/death/reset | Temporary Epic rigs/geometric art; basic greatsword pace approved, broader animation review pending |
| Verification | Native 10/10; final cooked 7/7, zero test warnings/failures; real manual 32 damage and 300 cm roll | Native report predates metadata-only correction; final package tested afterward |
| Reference review | Full 7:46 local-video timeline sampled; both combat phases at 1-second intervals; selected motion at 8/20 samples per second; timestamped sheets inspected | Visual sampling, not every source frame or audio; no exact rule/input inference or verified BossLab animation matching |
| Poses | Shared reachable hilt IK, keyed body/footwork, 0.000 cm rounded max tested grip error, 57.518 cm/tick max blade travel | No motion capture or reference-video matching; finger polish/close silhouette issues remain |
| Performance | Balanced 1080p 42.4 FPS mean, p95 49.3637 ms; default 720p 39.7 FPS, p95 56.4095 ms; all slower runs retained | 60 FPS not established; shared-machine load and different workloads prevent causal speedup claims |
| Footage | Actual final packaged balanced clip, 180 unique frames encoded/decoded, 6 s at 720p | Fixed 30 Hz capture, not FPS evidence; no audio; not every attack family covered |
| Availability | Offline local package, no API/model/Aura dependency; fixed rehearsal explicitly labeled | No active statistics, adaptation, RL or model integration; historical browser PPO remains separate |
| Storage/persistence | 10 GB work ceiling and 24 GiB free guard; generated duplicate apps only reclaimed; no owned helpers left running | Installed engine separate; system free space fluctuates; no deployment/notarization |

See [FUNDAMENTALS.md](FUNDAMENTALS.md), [STATUS.md](STATUS.md) and [REFERENCE_VIDEO_REVIEW.md](REFERENCE_VIDEO_REVIEW.md). Previous results below are historical, not sword-version validation.

## Historical unarmed Unreal checkpoint — 2026-11-03

| Capability | Actual evidence | Limits |
|---|---|---|
| Complete native fight | Animated movement, committed strike/dodge/heal, 3 boss moves, actual limb sweeps, stamina/cooldowns, win/loss/reset; actual desktop win at tick 3,027 | Prototype gauntlet/kick repertoire; no gamepad or extensive human balance study |
| Native verification | 13 editor/native tests and 10 packaged combat/fairness tests passed, zero test warnings/failures | Last input-config fix is not yet recooked; packaged optional HTML template missing, JSON valid |
| Original presentation | Project-authored sanctuary geometry/materials and armor over Epic mannequin rigs; actual screenshots; owner approved camera and direction | Simple stylized prototype, not original skeleton/animations or AAA asset fidelity; auditory quality unassessed; packaged CoreAudio device/timeout warnings retained |
| Statistical adaptation | Actual recent/long counts and bounded utilities; u5-real-switch.json: .580243→.118542 early expectation | Statistical modeling + authored selection, not RL; family context only, no learned network |
| Fairness | 12-tick delayed value DTOs, hidden-input/resource invariance during actual attack selection, fixed rules, locked aim, rejection/censorship tests | Software architecture boundary, not an untrusted-code security sandbox |
| Inspector/demo/export | Actual graphical late phase, displayed reset count, event history and JSON/CSV; combat-20261103-091806-1469.png | Trace is not a validated exact replay; demo uses a labeled reactive script |
| Held-out comparison | 64 native encounters; static/adaptive boss wins 16/32 each, zero timeouts; complete JSON/CSV | No win-rate gain. All switching encounters ended before the switch; actual reversal evidence is development-only |
| Rendering performance | Actual 1920×1080 editor-game run: 2,278 samples, mean 23.467 ms, p95 52.1445 ms | 60 FPS target not met; shared Mac, not an isolated GPU test; package performance not inferred |
| Gameplay footage | 180 unique actual engine frames encoded and decoded, 6 s at 1280×720; MP4 and poster | Fixed 30 Hz capture, not real-time performance evidence; no audio track |
| Native MCP | 15-operation create/move/read/save/reload/remove proof using installed Epic tools | Editor tooling only; no Aura clone or runtime model connection |
| Local package | Built, independently launched, actual manual strike/heal and scripted victory verified; exports saved in app sandbox | U7 paused: inherited F1–F5/F9 debug bindings conflict. Source config fix saved but NOT packaged/verified. No packaged benchmark, notarization or public deployment |
| Storage | Launcher enforces 6 GiB under unreal/ and 24 GiB free reserve | System swap/tool diagnostics can change total free space; no personal-file deletion |
| Model availability | RL/Laya/LLM visibly unavailable in native inspector | No native training/inference; browser PPO remains separate and headless-only |
| Preservation | Build kit and browser implementation retained; browser 24-test suite passed in preflight | Browser evidence does not validate Unreal |

## Historical browser build — 2026-10-04

| Capability | Implemented and evidence | Limits |
|---|---|---|
| Playable duel | Human controls, three attacks, health/stamina, healing, death/victory, pause/restart; tests and Chrome use | Agent controls and scripted play, not extensive human usability testing |
| Original visuals | Procedural arena, armor/cloak, cues, trails/particles, menus; real 720p/1080p captures | Canvas fallback, silent, no video or FPS benchmark |
| Statistical adaptation | Decayed event counts, family backoff, utility contributions; real-simulation reversal test | Rule-based selection plus online statistics; not RL |
| Fairness | Immutable DTO, 12-tick delay, hidden-input invariance, fixed combat, locked aim, stale rejection tests | Software boundary, not a hostile-code security sandbox |
| Demonstration | Reactive script switches at 40 simulation seconds; deaths/resets disclosed and logged | Evidence retained across labeled demo rounds; human restarts clear it |
| Evaluation | 36 paired encounters; both bosses win 6/18 | Six seeds per scenario, no win-rate gain or human generalization |
| Inspector and events | Actual samples, probabilities, accepted actions, phases/timing, export/viewer | Action probability is not hit probability; no exact replay |
| PPO training | Actual 4,096-transition masked PPO; finite losses, actor L1 change 3.367934, checkpoint/reload | Headless-only; custom PyTorch, not SB3; no established improvement |
| PPO evaluation | Trained/untrained each win 2/9; static/adaptive each 3/9 separately | Different decision cadence noted in RL.md; tiny sample |
| Laya / Jev / CLM | **Not connected** | No supplied authorized checkpoint/runtime; no inference claimed |
| LLM strategist | **Disabled / not connected** | Only validated plan schema; no fabricated transcript |
| Optional bridge | Versioned single-in-flight request, deadline, stale/invalid rejection; test doubles | Generic contract, not verified upstream Laya compatibility |
| Network/persistence | Project files; loopback preview; default no network inference | No deployment, cron, relaunch loop, account or cloud service |

`pilot-evaluation.*` uses an earlier scripted-player configuration that died before switching; it is retained as a finding, not mixed into final results. PPO diagnostics are actual losses/returns, not a claimed converged learning curve. Checkpoint identity and configuration are in `artifacts/ppo-training.json`.
