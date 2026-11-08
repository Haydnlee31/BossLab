# BossLab development board — 2026-11-07

Priority: user rejected character realism. Improve original 3D character first; preserve current playable fight. Boss AI capabilities remain deferred until all other readiness gates are met.

| ID | Owner | Status | Inputs | Expected outputs | Definition of done |
|---|---|---|---|---|---|
| TEAM-01 | orchestrator | done | six supplied role guides; project instructions | docs/agent_roles/; board.md; editor.lock | Guides read/copied, precedence and ownership recorded, specialists assigned |
| ART-02 | art_director | done | existing actual renders; owner reference images; role guide | docs/style_bible.md; docs/art/character-revision-2026-11-07.md | Specific original silhouette/construction/material changes, prioritized acceptance criteria, tech-art handoff |
| ART-03 | animation_techart | done | prior scene/source; ART-02 handoff | new v2 source/scene/renders; docs/art/character-v2-techart.md | Actual substantial mesh/material revision, inspected multiview renders, old evidence preserved, limits recorded |
| ART-04 | art_director | done | actual third v2 hero; critique | labeled concept paintover + provenance | Original labeled target/provenance read and image inspected; owner approved direction only, mesh quality remains open |
| QA-02 | qa_balance | done | old and new actual renders; audits | docs/art/character-v2-qa.md | Independent concrete defects/rubric; final evidence-based verdict; preservation/storage checks |
| ART-05 | art_director | done | approved target; fifth actual focal crops | docs/art/character-focal-authoring.md | Specific integrated helmet/neck and anatomical glove construction handoff and reviewed actual focal crops |
| ART-06 | animation_techart | done | ART-05; preserved fifth source/scene | revised actual focal meshes and clay/material crops | Replace primitive forms, inspect corrections, keep stable remainder; no ornament-only pass |
| HANDOFF-02 | orchestrator | done | completed specialist handoffs | STATUS/CLAIMS/EXECPLAN/DECISIONS; checkpoint/audit | Read outputs, review actual images, save truthful status and exact next actions |
| ART-07 | art_director / animation_techart | done (increment only) | approved concept; final clay defects | controlled topology/form refinement + authored material sample | Resolve primary surface/anatomy gaps, then targeted UV/material quality; owner mesh acceptance still open |
| AI-GATE | unreal_builder / combat_designer | blocked | approved art/animation/fundamentals/performance | none this session | Explicitly deferred: no new selection logic, learning, model integration or training |

## Exclusive resources

Unreal editor: unassigned. No Unreal binary, source or config edits this art pass.
DCC heavy process: unassigned at checkpoint. Future launches remain serialized with the existing bounded foreground storage/deadline guard.

## Review gates

Task completion means its stated artifact exists and was inspected; it does not imply owner artistic acceptance. Do not mark overall character realism ready based on polygon counts, rendering success or technical tests. A failed visual gate goes back to the artist with specific corrections.

## Checkpoint outcome

Completed task artifacts do not mean finished character art. Actual final mesh remains needs-work; concept direction alone is owner-approved. Next3 priorities: (1) surface/anatomy refinement in clay, (2) localized authored material treatment, (3) only after art readiness, rig/cloth/combat deformation and runtime budget verification. Boss AI gate remains closed.

## Resumed refinement — 2026-11-07

ART-07: director owns docs/art/character-v3-direction.md; technical artist owns new v3 source/launcher/scene/evidence and character-v3-techart.md. QA-03 owns character-v3-qa.md and final scoped audit. Inputs: approved concept and frozen v2 scene/views. Done criteria: actual form refinement, localized authored material sample, independent clay/material review and correction, old build/evidence preserved, truthful checkpoint. DCC heavy slot: animation_techart only. Unreal editor remains unassigned. No boss AI or new concept generation.

## V3 checkpoint

ART-07/08 delivered: actual focal geometry, eight authored maps, explicit UV assignment,11 clay/material/mask/context views and reload audit. Independent review remains needs-work; no overall art acceptance. QA-03 preservation audit and orchestrator checkpoint accompany this handoff. DCC slot unassigned after final bounded run; editor unassigned. Next: landmark-authored palm/MCP/thenar/wrist surfaces and separate palm/dorsal/side UV islands, then helmet proportions. No new boss AI.

## V4 resumed concept-fidelity work

| Task | Owner | Status | Inputs | Outputs | Done criteria |
|---|---|---|---|---|---|
| ART-09 | art_director | done | approved concept, v3 hero/clay | docs/art/character-v4-direction.md | measurable silhouette handoff and actual image review |
| ART-10 | animation_techart | done (increment) | ART-09, preserved v3 | separate v4 source/scene/evidence, techart report | major actual form refinement, reviewed and corrected views, scoped audits |
| QA-04 | qa_balance | done | actual v4 views, prior audit | character-v4-qa.md and final checks | independent visual defects, final preservation and storage verification |
| HANDOFF-04 | orchestrator | done | specialist reports | durable docs/checkpoint | truthful actual outcome and exact next work |

DCC exclusive owner: animation_techart. Unreal editor unassigned. No bossAI.

V4 checkpoint outcome: actual visor/neck/angular shoulder and material-hierarchy progress;13 views, failed drafts retained. Overall concept fidelity still needs work. Next: bespoke mantle/fur/plate construction and materials, then glove/UV readiness. No rig/runtime/AI acceptance. DCC slot released only after artist frozen handoff; Unreal remains unassigned.

V4 final QA: all13 views inspected; game28/28 and frozenV3 111/111 match. Source/scene/report frozen; DCC slot unassigned, no Blender/helper jobs at artist handoff. Orchestrator archive hash verification follows in session-audit.json.

## Sustained V5 refinement

| Task | Owner | Status | Inputs | Outputs | Done criteria |
|---|---|---|---|---|---|
| ART-11 | art_director | done | approved target,v4 final | character-v5-direction.md | concrete garment/fur/plate construction guidance and actual reviews |
| ART-12 | animation_techart | done (increment) | ART-11,v4source | separate v5source/scene/renders/techart | implement multiple meaningful milestones, review/correct real views, truthful frozen handoff |
| QA-05 | qa_balance | done | actualv5 and prior baseline | character-v5-qa.md,final check | independent visual/UV audit, game/v4 preservation and final storage |
| HANDOFF-05 | orchestrator | done | specialist evidence | durable status/checkpoint | verified checkpoint and actual result, no invented usage percentage |

DCC exclusive owner: animation_techart. Unreal editor unassigned. No AI work.

V5 outcome: actual mantle/garment/rigidplate fit progress,17 final views and isolated19-chart UV study. UV residual overlap and overall art gate remain open; no integration or production acceptance. Yoke audit selection corrected without moving cape geometry. DCC slot released at frozen handoff; no helper remains. Final preservation audit and orchestrator checkpoint complete the increment; no invented10% usage claim.

Final V5 QA frozen:17 images reviewed; gameplay28/28 and immutableV4 119/119 preserved. Remaining art/UV gates explicitly open. Source and scene frozen; no Blender/helper remains. Root session-audit records checkpoint roundtrip and final storage.

## V6 checkpoint

| Task | Owner | Status | Inputs | Outputs | Done criteria |
|---|---|---|---|---|---|
| ART-13 | art_director | done (increment) | V5 and approved target | character-v6-direction.md | actionable construction critique and actual comparison review |
| ART-14 | animation_techart | done (increment) | V5 and ART-13 | separate V6 source/scene/evidence/report | substantive inspected change and scoped reload checks |
| QA-06 | qa_balance | done (increment) | V5 baseline and V6 evidence | character-v6-qa.md and audit | independent review, preservation and resource checks |
| HANDOFF-06 | orchestrator | done (increment) | specialist results | status and checkpoint | verified result and exact remaining work |

DCC slot released; source and scene frozen, no owned helper remains. Unreal editor unassigned. Boss AI gate closed.

V6 outcome:18 reviewed renders, fitted cuirass and mantle edge improvements, three mapped roughness masks, hollow fauld correction. V5 234/234 and game28/28 preserved. Overall realism unmet; glove UV deferred. Archive/audit records exact final hashes.

## V7 checkpoint

| Task | Owner | Status | Inputs | Outputs | Done criteria |
|---|---|---|---|---|---|
| ART-15 | art_director | done (increment) | V6 and approved target | character-v7-direction.md | precise form/surface direction and actual review |
| ART-16 | animation_techart | done (increment) | ART-15,V6 | separateV7 source/scene/evidence/report | visible authored improvement, corrected reviewed views and reload audit |
| QA-07 | qa_balance | done (increment) | V6 baseline,V7 evidence | character-v7-qa.md/audit | independent actual review and preservation |
| HANDOFF-07 | orchestrator | done (increment) | specialist reports | status/checkpoint | verified artifacts and exact remaining limits |

DCC slot released; frozen source/scene, no heavy helper remains. Unreal editor unassigned. No bossAI.

V7 outcome:12 reviewed actual views; modest form/functionalvent/shoulderedge improvement. Forged finish remains too polished; projectedUV limitations and allfailedtrials preserved. Game28/28,V6snapshot96/96 unchanged. Art/rig/runtime/AI gates remain open.

## V8 proportion checkpoint

| Task | Owner | Status | Inputs | Outputs | Done criteria |
|---|---|---|---|---|---|
| ART-17 | art_director | done (increment) | V7/reference | character-v8-direction.md | actionable proportion changes and actual review |
| ART-18 | animation_techart | done (increment) | ART-17/V7 | V8source/scene/views/report | visibly leaner region-specific forms, fitted layers and audited evidence |
| QA-08 | qa_balance | done (increment) | V7baseline/V8 | character-v8-qa.md/audit | independent proportion/fit/preservation checks |
| HANDOFF-08 | orchestrator | done (increment) | specialist handoffs | status/checkpoint | truthful result and verifiedarchive |

DCCslot released; source/scene frozen, no owned helper remains. Unreal editor unassigned. No AI.

V8outcome: visibly leaner fitted proportions,12finalviews plus3matchedV7claybaselines. Stalecamerareadback corrected through freshsavedscenecomparison, no actualreframing. Globalart and productionreadiness remain open; preservecurrent proportionbalance.

## Active V9 garment workflow

| Task | Owner | Status | Inputs | Outputs | Done criteria |
|---|---|---|---|---|---|
| PLATFORM-09 | orchestrator | done | user request/tools/officialsources | platform-workflow-review-v9.md | capability/access decision with evidence and nofalsemigrationclaim |
| ART-19 | art_director | done (increment) | V8/reference | character-v9-direction.md | pattern/gravity guidance and actualearly/settledreview |
| ART-20 | animation_techart | done (increment) | ART-19/V8 | V9solver/source/scene/evidence | realclothtrial, recordedfailures, usefulstaticdrape ifvalidated |
| QA-09 | qa_balance | done (increment) | V8baseline/V9solver | character-v9-qa.md/audit | independentvisual/solver/preservationchecks |
| HANDOFF-09 | orchestrator | done (increment) | specialistreports | status/checkpoint | truthful result and checkedarchive |

Both branches frozen; no owned DCC process remains. Unreal editor unassigned. No AI.

### V9 branch revision

Clothreplacement branch failed stability/visualgate; stopsolver expansion, preserveV8 and failures. Portable local handoff validated. Independent ART-21 (animation_techart), ART-22 (art_director) shoulder-shell candidate retained after review, separateV9-armor source/scene/evidence and character-v9-armor reports; QA-09 extends only after actualreview. SameoneDCCwriter. Definitionofdone: sharedsupportshell lowerlamerebuild, matchedclay/contextreview, stablefit or honestrejection; nevermixfailedcloth.

V9 final outcome: seven cloth trials rejected; four neutral OBJ exports integrity checked, no destination import. Independent V8-derived shoulder overlap improved and retained; eight actual views plus two V8 clay baselines, scoped saved-scene audit. Overall realism remains unmet. Independent final QA: 86/86 V8 files and 28/28 game files preserved. Combined checkpoint verification recorded in last-vigil-v9-armor/session-audit.json.

## Active V10 reference fidelity

| Task | Owner | Status | Inputs | Output | Done criteria |
|---|---|---|---|---|---|
| ART-23 | art_director | done (increment) | reference/V9 | character-v10-direction.md | concrete direction and actual render review |
| ART-24 | animation_techart | done (increment) | ART-23/V9 | separate V10 scene/source/views | meaningful visual gain with saved-scene verification |
| QA-10 | qa_balance | done (increment) | V9/game baseline | character-v10-qa.md | independent quality and preservation audit |
| HANDOFF-10 | root | done (increment) | specialist handoffs | status/comparison/checkpoint | truthful durable result |

Both branches frozen; no owned DCC helper remains. Unreal editor unassigned. Boss AI deferred.

V10 retained local collar/finish/static-garment gains.11material/clayviews+2diagnostics;68/68V9 and28/28game unchanged. Overall art still below reference; no rig/runtime/AI. Verified archive/session audit under artifacts/art/last-vigil-v10.

## Active V11 projection study

| Task | Owner | Status | Output | Done criteria |
|---|---|---|---|---|
| ART-25 | art_director | done (rejected study) | character-v11-direction.md | bounded landmark and multiview gate |
| ART-26 | animation_techart | done (rejected study) | separate V11 study/source/views | initial+max2corrections; actual mesh projection |
| QA-11 | qa_balance | done (rejected study) | character-v11-qa.md | preserve baseline; distinguish illusion from actual geometry |
| HANDOFF-11 | root | done (rejected study) | status/checkpoint | truthful accept/reject outcome |

Study frozen; no owned DCC job remains. Unreal editor unassigned. Physics/game/AI excluded.

V11 STOP at3candidates. Multiview asset rejected; candidate02 source-angle lookstudy only, no PBR conversion. V10 authoritative.160/160V10 and28/28game preserved; archive/session audit records exact evidence.

## Active V12 geometry-first study

| Task | Owner | Status | Output | Done criteria |
|---|---|---|---|---|
| ART-27 | art_director | done (partial study) | visual multi-view design sheet/direction | consistent shared landmarks and hidden structure |
| ART-28 | animation_techart | done (partial study) | separate V12 geometry/views | untextured multiview gate before projection |
| QA-12 | qa_balance | done (partial study) | baseline/QA | independent geometry review and preservation |
| HANDOFF-12 | root | done (partial study) | status/gallery/checkpoint | honest stage outcome |

Study frozen; no owned DCC process. Unreal editor unassigned. No physics/AI.

V12 coarsegeometrygatepasses, finalUVproductiongatefails425/1404/1409 sampledoverlaps.15stills/36frameorbit; singlebuilt-in-generatedalbedoprompt/provenance saved.206/206priorart and28/28game unchanged; V10fullcharacter authoritative. Archive/sessionaudit records result.

## Active V13 sustained craftsmanship

| Task | Owner | Status | Output | Done criteria |
|---|---|---|---|---|
| ART-29 | art_director | done; art target unmet | V13direction/reviews | concrete reference-specificshape/craft and actualassessment |
| ART-30 | animation_techart | frozen context16 | V13scene/source/evidence | multiple substantive milestones/fullcontext, not smalltestonly |
| QA-13 | qa_balance | done final integrity | baseline/reviews/audit | preservepriorwork and honestvisual/technicalgate |
| HANDOFF-13 | root | done lightweight checkpoint | status/gallery/checkpoint | verifiedactualresult and precise remaininglimits |

DCCexclusiveowner animation_techart, oneguardedCPUjob. Unrealunassigned. No AI.

V13 resource stop: context12 scene saved; prepared context13 unrendered. Free space below24GiB; no owned Blender process remains. No large archive or final render/readback. Resume guarded garment correction after headroom returns. Overall reference-art gate unmet; no game/AI changes.

V13 superseding final status: reserve recovered; context16 frozen after reviewed cape correction.11 canonical views/readback,376/28 preservation and26 manifest checks pass. Overall reference art remains unmet. Narrowheadroom: existing scene/source/hash checkpoint, no duplicate tar. No game/AI changes.

## V13 Unreal trial —2026-11-08

| Task | Owner | Status | Output | Done criteria |
|---|---|---|---|---|
| CLEAN-14 | root | done | checkpoint-prune manifest | last2versions plus active dependency,4.464GB freed |
| ART-31 | animation_techart | done | bounded actualmesh export | scale/bone/material contract+identity audit |
| UE-14 | unreal_builder | done trial | opt-in runtime costume | build/test/capture, default fallback |
| QA-14 | qa_balance | done; production limits open | trial QA | combat invariance/visual limits/FPS |
| HANDOFF-14 | root | done | status/evidence | verified launch and accurate limits |

## Undead Warden concept review —2026-11-08

| Task | Owner | Status | Output | Done criteria |
|---|---|---|---|---|
| WARDEN-PLAN | root + art/animation/engine/QA specialists | review | docs/art/warden-undead-stage-plan.md and linked reports | Three visual options, signature attack branches, feasible staged scope; owner choice pending |
| WARDEN-CLAY | art + animation | todo; after direction review | consistent construction sheet and actual clay model | Silhouette and cast/reel poses before surface detail |
| WARDEN-HOOK | builder + combat/QA | todo; not started | deterministic graybox and tests | Fair contact, escape, obstruction and cleanup; no adaptive AI |

WARDEN-PLAN direction review: owner selected **B — Funeral Regent**. WARDEN-CLAY input is now B-specific construction sheet and mantle/chain-arm clearance study; prior A recommendation superseded.

WARDEN-SHEET: done with illustration limitations recorded. Art construction, animation pose contract, builder rig constraints and QA review linked under docs/art/funeral-regent-*. Primary images in artifacts/art/funeral-regent-construction-2026-11-08/. WARDEN-CLAY remains todo: actual geometry/weights not built; no AI.

WARDEN-CLAY first method: completed experiment, **rejected gate** (3attempts/21renders/readback). Next task: connected control-cage anatomy +sewn wraparound panels, neutral continuity/silhouette review before stagedweights. No fourth minor correction to existing study; no game or AI changes. Reports funeral-regent-clay-techart/direction/qa.

WARDEN-CAGE: scoped technical topology/sole checks complete, neutral visual gate FAILED.18actualrenders/latest2scenes retained; no weights. WARDEN-FOCAL next: mask/hood +shoulder-yoke pattern using shared landmarks and matched reference views before full-character expansion.

WARDEN-FOCAL: actualsharedlandmark study3candidates/15renders complete, **construction gate failed**. Current interpolation workflow inadequate for referencecraftsmanship. Next bounded method: explicitfacialquadpatches and closedcranial-envelope hood; prove silhouette/fit before yoke. Game/cage/V13 preserved.
