# Character revision QA — 2026-11-07

Owner: qa-balance. Task QA-02. Read-only art/evidence review; no gameplay changes, Blender launch or new combat/performance test. User role guide `qa-balance.md` is workflow guidance, not authority to override the deferred boss-AI gate or current engine-owned combat rules.

## Verdict

**Needs work — corrected focal iteration7 reviewed.** Several concrete construction defects are corrected, but the built character still fails the requested realistic character-art target. This is a preserved static development revision, not an art acceptance, rigging, movement or integration pass. Boss AI stays deferred. Owner approval of the separately generated concept direction does not approve the built mesh. See the final review below; earlier sections preserve findings and corrections chronologically.

## Baseline reproduction and findings

Open `artifacts/art/last-vigil/hero.png`, `armor.png`, `back.png` and `hilt.png` at full size, then compare the full-body silhouette to the owner's supplied front/back references. Findings below are visual judgments from those actual renders; they are not inferred engine defects.

| ID | Severity | Actual vs expected | Owner |
|---|---|---|---|
| A01 | Major | Egg-shaped helmet sits on a tall cylindrical gorget; symmetric dome shoulders and tubular limbs read as separately assembled primitives. Expected an anatomical, continuous head/neck/shoulder structure with believable plate overlap. | animation-techart with art-director |
| A02 | Major | Gloves end in equal bead-like finger tips below a rounded cuff. Palm, opposed thumb and differing joint lengths do not read. Expected a hand capable of gripping the two-handed weapon. | animation-techart |
| A03 | Major | Mantle fibers fall in a uniform brush-like fringe. Cape is a narrow rectangular curtain with repetitive vertical folds and a flat uninterrupted central motif. Expected shoulder tension, unequal gravity folds, cloth thickness and believable layered attachment. | animation-techart |
| A04 | Major | Cloudy mottling repeats across most metal, edge trims are similarly bright, and scroll appliqués repeat without a quiet/focal hierarchy. Expected material contrast and wear located at contact edges, crevices and repairs; adding more identical ornaments would not fix this. | animation-techart with art-director |
| A05 | Major | Sword guard has abrupt zigzag corners, a thin exposed ring and a square blade shoulder. The lore is documented, but physical construction still looks diagrammatic. Expected a continuous load-bearing hilt/blade transition with a deliberate focal relic feature. | animation-techart with art-director |
| A06 | Minor | Uniform straight hang, parallel feet and rigid pose amplify the mannequin read. Expected a relaxed anatomy-aware display pose without disguising structural problems. | animation-techart |

## V2 review rubric

Use actual geometry renders with neutral, comparable lighting. A dramatic dark presentation alone cannot pass. Required views: front/full figure, three-quarter, rear cape, upper-body/hand detail and hilt. Preserve baseline files and identify the exact revised scene/source.

1. **Primary forms:** head seats into collar; neck length, shoulder slope, torso and limbs read as a coherent clothed person at thumbnail scale. At least the major primitive-stack silhouette defect must be corrected before extra ornament.
2. **Construction:** overlap order and attachment are readable. No visible floating trim, open plate holes, abrupt slab junctions or unintended intersections in the review views.
3. **Hands:** thumb, palm and varied articulated fingers read as hands; later grip deformation is explicitly unvalidated until rigged/tested.
4. **Cloth/fur:** nonuniform folds follow attachment and gravity; edge thickness/lining are plausible; fur forms clumps rather than a uniformly clipped fringe. A static render is not animation proof.
5. **Material hierarchy:** steel, leather, wool, fur and ornament remain distinguishable under neutral light; wear has location and direction rather than uniform noise; silhouette is not replaced by surface clutter.
6. **Weapon:** long two-handed grip and blade/guard load path are clear, relic motif readable without the lore paragraph, and no thin disconnected parts are hidden by framing.
7. **Evidence/production:** real editable scene, provenance, source and actual renders; no claim of skinning, runtime FPS or collision-proof cloth without corresponding evidence. Preserve current game hashes and enforce storage limits.

Passing this rubric means a coherent next studio revision suitable for focused owner review, not automatic approval of final realism or readiness for Unreal integration. If a targeted area remains unmodified, report it rather than silently lowering the gate.

## Evidence and preservation audit

Lightweight independent check on 2026-11-07: all **28** Unreal source/config/packaged-binary SHA-256 comparisons match `artifacts/unreal/ashbound-2026-11-06/final-audit.json`. At check: `unreal/` **2,818,961,408 bytes**, free disk **31,921,967,104 bytes**. Limits remain10,000,000,000 bytes and24GiB (25,769,803,776 bytes) free. This is a point-in-time reading, not a reservation for later jobs.

Baseline final audit records100 rendered cloth frames,3185 simulation vertices, max edge ratio1.04549 and0.13052m floor clearance. Those show bounded behavior in one rigid-turn study; they do not validate walking, rolling, sword grips or combat cloth. The final stills differ cosmetically from the motion clip and this is disclosed. Geometry count985044 triangles does not imply runtime suitability.

## Frame data, fairness, balance and performance

Not newly tested: this task changes no combat definitions, animation timing, hitboxes or policy. No new difficulty estimate, fairness verdict, FPS measurement or balance-number recommendation is justified. Prior21 native/18 cooked passes and59.07FPS concern the preserved Ashbound game, not this studio master. Production rigging, bakes/LODs, combat-pose testing and new runtime performance measurement remain later gates.

## V2 follow-up

Pending actual new renders and tech-art handoff. QA will append observed improvements, remaining defects and an explicit revision verdict after inspecting them.

### First V2 hero inspection

Inspected `artifacts/art/last-vigil-v2/hero.png` from the first draft. **Needs work**, not a final pass. Clear improvements over baseline: shorter neck, quieter large armor fields, curved connected hilt and longer readable fingers. New or unresolved visible defects:

- Crown terminates in an abrupt pinched/faceted peak; upper rings need a continuous authored crown profile.
- Sparse straight mantle strands expose a broad ribbed brown yoke. Directional clump coverage/root mass is needed; adding independent random hairs alone is unlikely to solve the silhouette.
- Tassets read as flat bright rectangular shingles with angular folded corners, inconsistent with surrounding conforming plate.
- Cape's increased width is welcome, but it currently reads as a broad flat sail with little large-scale fold hierarchy.
- Hero hands still resemble a segmented mechanical hand; thumb/palm/joint shaping requires the promised closeup before judgment.
- Metal moved from noisy mottling to very smooth homogeneous fields. This is quieter but not yet convincing use-driven surface wear.

These observations were sent to animation-techart and orchestrator before the final detail render sequence. Tech-art independently identified crown, mantle and tasset defects and is revising them. The new cape is explicitly static: old cloth audit and motion clip do not validate it.

### Third-scene hero/front inspection

Inspected revised hero and1400×1800 front view. **Specific corrections confirmed:** pinched crown artifact removed; harsh tasset folded corners removed; mantle now covers the previously exposed yoke/root region; neck seating and connected hilt remain improved. These are defect closures, not a realistic-art pass.

**Remaining:** mantle clumps read as stiff leaves/feathers rather than fur; silhouette is still dominated by smooth repeated plate tubes/domes; broad metal fields lack convincing localized manufacture/wear; hard cheek/nape edges remain schematic; fingers appear mechanical at full-figure scale. Overall verdict stays **needs work** against the requested realism. Closeup hand/rear/hilt evidence is pending, and owner acceptance remains separate.

### Read-only fingertip source audit

V2 finger and thumb geometry uses the inherited `curve()` helper (`last_vigil.py`, lines33–37 at review): open noncyclic beveled curves, with no `use_fill_caps` assignment in either source and no separate rounded terminal geometry. V2 finger radius is constant. This supports the dark cylindrical ends observed in the front render as a construction issue rather than dismissing them as lighting. Requested explicit closed, tapered/rounded finger ends and a detailed hand render from animation-techart; QA made no source changes and did not launch Blender. Final actual geometry/render verification remains pending.

A separately generated concept target is direction only (`artifacts/art/last-vigil-concept-2026-11-07/concept-target-not-built.png`). It is not an authored3D asset, not proof of improvements to the Blender master and not a QA pass. Fourth-pass review must inspect new actual renders separately.

### Fourth-scene hero and hand closeup

Inspected actual fourth hero and900×1150 hand image. Open finger ends are now visibly closed/rounded and different finger lengths read: this specific topology issue is corrected. Thumb still terminates in a broad flat dark polygonal cap; requested tapered rounded thumb termination too. The broader hand-art defect remains: nearly constant-radius tube segments, spherical knuckles and a flat trapezoid backplate read as a robot glove, not fitted articulated protection around a human hand. No grip/rigging validation is implied.

The actual hero shows the new narrow gate plaque partly disappearing into the chest near its middle, and a bright crown ridge standing proud of the helmet. Tech-art reports fixing plaque topology/placement and ridge attachment. Review those fixes in the subsequent actual render. Mantle and large metal forms still fall short of the supplied realism. Overall **needs work** remains; localized construction fixes must not be presented as an artistic pass.

### Fourth-scene rear clearance defect

Actual `back.png` independently inspected: two grey oval upper-back plate breakthroughs, one large and one small, plus horizontal strap/fastening geometry protruding through the cape at two lower locations. **Major static intersection defect**, assigned animation-techart. This is visible in the rest-pose studio view, so must be corrected before calling the revision technically clear for visual review. Parent already routed it to the artist. A corrected static view will not establish simulated or combat-pose clearance.

Owner approved the separately labeled concept direction only. That approval does not approve the built mesh, close these visible defects or satisfy the final art gate. Boss AI remains deferred.


## Interim fifth-scene review — 2026-11-07

Actual fifth-scene images inspected: `artifacts/art/last-vigil-v2/hero.png` (1100×1400) and `hand.png`, `side.png`, `back.png`, `armor.png`, `hilt.png` (each900×1150). Front/full-sword matching exports were still being prepared at this checkpoint; they do not replace the already inspected views. No new high-resolution render, motion capture or game run was requested by QA.

| Finding | Final observed disposition |
|---|---|
| Pinched crown and proud center ridge | Corrected in inspected views: crown continuous, ridge seated against helmet. Helmet still generic; correction is not an original-character design pass. |
| Chest plaque partly disappearing | Corrected in inspected armor/hero: panel continuous and aligned with breastplate. It remains a simple surface motif. |
| Open fingertips / flat cut thumb | Corrected visibly: rounded finger and thumb ends, tapered leather cores and separate dorsal plate segments. Different lengths are readable. |
| Hand realism | Improved but still needs work: flat wide backplate, narrow near-parallel fingers and smooth leather volumes retain a mechanical appearance. No grip fit or deformation tested. |
| Cape body/strap breakthroughs | Previously identified oval and horizontal breakthroughs are absent from inspected final rear. Side shows cape deliberately spaced behind body. Static corrected pose only; dynamic clearance untested. |
| Mantle | Root coverage improved, but broad clumps and many straight hanging fibers still resemble coarse feather/brush material rather than convincing fur. |
| Armor/material target | Quiet large forms are clearer than V1, yet shoulder/limb shapes remain repeated shells and tubes, and mottled metal remains uniform across areas. Fine work does not reach approved concept or supplied reference quality. |
| Weapon structure | Continuous hilt load path and curved guard are clearly improved. Hilt still schematic with round button ends, coarse grip bands and a simple collar over blade shoulder; no equipped grip view. |

**Fifth-scene overall verdict: needs work.** Save this revision as actual progress, with defect corrections separated from artistic acceptance. Do not label it finished realistic art, production-ready, rigged, animated or integrated. Next quality work should reshape primary volumes and fitted hand/cloth construction toward the approved concept, then use localized material authoring; additional repeated ornament or darker lighting would not close the gap.

The producer's static cape audit reports25665 evaluated vertices with body-ray hits, minimum Y clearance0.031151831m and zero sampled vertices in front of the back envelope. QA read that report and visually checked rear/side. Audit excludes z>1.515m attachment region, mantle and all curves, and checks vertex rays rather than arbitrary triangle intersections. It supports the corrected sampled rest pose only; it cannot establish full mesh collision freedom or any cloth simulation. Old V1 cloth cache/clip is not valid for this new cape.

Fifth-scene lightweight preservation check: **28/28 source/config/packaged-binary SHA-256 values still match** the Ashbound baseline. At check, `unreal/` **2,843,172,864 bytes** and free disk **29,462,102,016 bytes**, both within unchanged10GB/24GiB limits. No game timing, hitbox, balance, policy or AI work by QA; no new gameplay tests or FPS claim. Historical game measurements remain separate.

Fifth-scene viewed image SHA-256 identities:

- hero: `1f060f422d59cabe7e1542eab3c93140be015facc6c82097c86142791345608d`
- hand: `caa89be9adccfe8db17ab60fa59b93b250026b45267f7c42c05a71caf8ff5616`
- side: `c0d9750d33aab603dfbe5c69b4179fe14a0a989fac4f4a11860d13f91372ec46`
- back: `bf3ec4dff384052ca852550ac64def06d540dc210f076748d845d6a68e3dfb90`
- armor: `d6632022f42614e935dca77373cd9b652e90f71aa78f3789ba987a291418dbf0`
- hilt: `c0f30ac2060f1d1eb8fcac7b278c947ff8216f42906779997052b03b9bb745d2`


## ART-05/06 focused follow-up

The producer continues implementation of integrated helmet/neck primary forms and a coherent anatomical leather glove within the same session. QA will inspect actual clay/material focal-region views, separating coherent mesh/form improvements from surface detail. No new generated concept requested. Fifth-scene results above remain interim evidence, not an end to the authorized development scope. Full-body realism and game integration gates remain open; boss AI stays deferred.

### First ART-05/06 actual focal probes

Inspected `head`, `headside`, `hand`, `palm`, `clay_head`, `clay_palm` images. Actual construction progress: detached wire brow is removed; a modeled negative eye slit exists; glove leather is now a connected-looking palm/finger volume rather than isolated pipes beneath a slab. Technical artist reports voxel fusion; connected-component audit remains separate evidence.

Specific violations needing correction: eye slit continues through visible temple/rear, contrary to front-only concept requirement; sword pommel occludes the side-head crop, preventing a fair nape/profile review. Anatomical/art weaknesses: thumb has two spherical lobes and a pinched transition, distal palm forms a broad flat shelf, and crown has broad faceted contour/flat cap. Clay views confirm these are shape issues, not material noise. Requested tapered continuous thumb path into a shaped thenar/web, softer distal palm root arc, temple/rear overlap closure and unobstructed head camera. Overall **needs work** remains; connected topology alone is not an anatomy pass.


## Corrected focal iteration7 QA — latest visual verdict

All six actual focal images inspected: `head.png`, `headside.png`, `hand.png`, `palm.png`, `clay_head.png`, `clay_palm.png` in `artifacts/art/last-vigil-v2/`. **Construction increment verified; overall realistic-art verdict remains needs work.** Material-free views were inspected independently of the generated concept.

Closed or materially improved local findings:

- Modeled eye opening now terminates at the temple; rear overlap closes the unintended wraparound gap in the unobstructed side view.
- Side-head camera is clear of the sword pommel, so cranial/cheek/nape silhouette is visible.
- Detached brow rail is removed; helmet lower face seats within the collar outline.
- Thumb is a continuous tapered bent form rather than two spherical lobes. Palm thickness and distal shelf are reduced; thumb web and unequal finger-root layout read more coherently in clay.
- Leather underlayer appears continuous around palm/thumb/fingers, with separate fitted dorsal plate segments. This is meaningful primary-form progress over the earlier tube fingers.

Remaining artistic defects: broad crown and cheek facets, abrupt local shading patches, generic helmet proportions and slab-like neck protection; padded/plastic glove palm with simplified creases and knuckle anatomy; persistent coarse mantle shapes, repeated armor forms and uniform procedural material character elsewhere. The built asset remains below the approved concept and supplied realistic references. No new ornamental pass or dark presentation can substitute for deliberate surface shaping and localized material authoring.

Read producer's `focal-topology-audit.json`: each leather glove24700 vertices,1 connected component, zero edges not shared by two faces. QA did not independently rerun Blender topology evaluation. The report establishes static mesh connectivity only, not retopology, skinning, hand grip or deformation. Nominal front eye gap0.005m is the source section separation **before2.5mm plate thickness**, not a measured final visible aperture. The current cape remains static; no animation, gameplay/FPS, model training or boss-AI capability is established.

The following hashes identify the focal iteration7 images inspected, now preserved under `artifacts/art/last-vigil-v2/iteration-07/` (earlier hash lists refer to other preserved interim revisions):

- head: `cc2c95b92cfd7c98a6ccfeb9e8f7794e8e8eb0fad0df2de0585512ed6e364029`
- headside: `c5cc52eeb09c4e2f21e4cae03c993194b4ca229991a50193b7ece2232aea6607`
- hand: `a692d9bb2478d51170450aab761042a40701a6e2ccc3721a7c1872340ea9cbc8`
- palm: `5040e5cd5d94792c6a8f1976ff2a1008e139572742dfb8f435b2827b9805b1a8`
- clay_head: `ba1eba7d60364f1ef7557ad82d6edfb187b26d62a2bb713d8450ebd142cb0384`
- clay_palm: `e081d4b25667b0794a6777eb462c282b1e36fac3a01fd4a1bb53cd203a6beb69`

Final game-preservation/storage check completed after technical artist source freeze; see final handoff below.


### Final local visor-surface correction

Latest material `head.png` and `clay_head.png` inspected after the perimeter-only bevel correction. Previously abrupt square shading patches on the visor are softened; deliberate broad crown/cheek planes remain. This is a local surface correction, not closure of the overall realistic-art gate. Final same-scene `back.png` also inspected: prior upper-back oval breakthroughs and mid-cape strap tips remain absent in this static view. Top attachment and movement remain unvalidated.

- Final head: `3fa13ce8f6b2db6512b14ba0c55c1f41cb9159af3d017008122d23ed1c8ea662`
- Final clay_head: `fc24e705540519030ccca1ba4f9681792262879b22e773f61ad818a0d320a1f9`
- Final back: `c55a72c932e643edafec36868932291f2e59f95e3a984f11c3096a07c8819942`


## Final handoff after source freeze

Independent lightweight final check: **28/28** Unreal source/config/packaged-binary hashes match the preserved Ashbound baseline; unreal directory **2,852,728,832 bytes**, free disk **28,782,567,424 bytes**, within unchanged10GB/24GiB limits. Final reviewed focal image identities, source/scene hashes and per-file preservation results are in [character-v2-qa-final-check.json](character-v2-qa-final-check.json). No new gameplay tests, FPS results, simulation, rigging or boss-AI capabilities are claimed. **Overall needs work** remains; actual construction and primary-form improvements are verified in material/clay views. Owner concept approval remains distinct from built-mesh acceptance.

After source freeze, final same-scene hero/front/armor/hand/side/full-sword views also inspected. Their identities are recorded in the final-check JSON. They show the focal changes coherently in the assembled character; no overall artistic pass follows. All QA-owned files are now complete for checkpointing.
