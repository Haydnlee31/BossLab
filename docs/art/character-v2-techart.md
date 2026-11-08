# ART-03 — Last Vigil construction revision

Date: 2026-11-07, Asia/Singapore. Owner: animation-techart. Scope: original static Blender master revision; no Unreal asset/code edits or AI. Inputs: user animation-techart guide, project instructions/status/claims, art-director handoff `character-revision-2026-11-07.md`, style bible, v1 source/master and actual v1 render review. Independent art/QA feedback produced seven reviewed modeled iterations plus a local visor bevel correction. The owner approved the generated concept direction, not the current mesh or final artistic quality.

## Implemented

- Replaced the egg-like helmet and tall gorget with a seated sallet/bevor, defined cheek/jaw visor planes, narrow eye recess and protective swept nape. A second pass rebuilt crown rings to remove the first revision's pinched top.
- Rebuilt shoulder shells as lower swept overlapping lames, with 12% broader left protection. Removed repeated shoulder rosettes and most decorative limb/chest scrolls. Rebuilt the cuirass's major chest/belly sections and fitted padded underlayers inside the replacement steel after an actual render exposed penetration.
- Replaced equal bead fingers with connected tapered curved finger/glove segments of different lengths, palm/backplate, knuckle arch and opposing thumb. Static pose only: no new rig, grip solving or articulation proof.
- Reauthored split surcoat with asymmetric fold/tension geometry and tassets with convex quad surfaces; replaced the cape with broad unequal sewn folds and a bound edge. The v1 cloth cache is deliberately not reused or represented as new motion.
- Replaced the straight brush fringe with tapered clump masses and directionally varied fibers. Reduced redundant strands after the second draft exceeded the existing studio geometry budget. Mantle remains stylized and requires independent review.
- Replaced cloudy all-over metal color with stable blackened steel and subtle directional roughness/bump; restrained actual edge trims and selected local scuffs. Retained one small gate seal and the original garment embroidery; no generated images or downloaded materials.
- Added a continuous sword tang/ricasso socket through the guard, a smaller backed incomplete reliquary and a smoothly swept guard. Kept original blade endpoints and lore. No gameplay timing, reach, damage or combat authority changed.

## Actual iterations and verification

`artifacts/art/last-vigil-v2/iteration-01/` retains the first actual render/source/audit: sparse mantle, pinched crown and faceted bright tassets. Art director and QA independently reported these issues.

`iteration-02/` retains the next render/source/audit: crown/tasset corrections and opaque mantle clumps, but new chest and sleeves visibly intersected old padded underlayers. It also exceeded the approximately985k-triangle studio ceiling at1,266,062 evaluated triangles. Corrected underlayer fit and reduced redundant mantle fibers; neither issue is described as a pass.

Third actual draft:424 renderable objects,454,197 evaluated vertices,843,062 evaluated triangles. Preserved fifth draft:479 renderable objects,474,001 evaluated vertices,880,386 evaluated triangles, finite vertex positions,2 packed authored images. This is a studio integrity check, not a runtime optimization or artistic acceptance result. Same studio lights, cameras and exposure as the previous version. The third-draft CPU high-resolution pass was intentionally stopped after front/back at the orchestrator's request; receipt exit−15 is a superseded run, not a completion. Preserved fifth hero is1100×1400 and diagnostic views900×1150; no final-quality8-view render pass is claimed. Process receipts contain actual durations/device/storage.

## Files and commands

- `unreal/art-studio/source/last_vigil_v2.py`: reproducible transformation using original v1 utilities and saved static master.
- `unreal/art-studio/revision-2026-11-07/last-vigil-v2.blend`: new static master, v1 remains unchanged.
- `scripts/bosslab-art-v2`: bounded foreground launcher,24GiB free reserve/10GB unreal ceiling/20-minute deadline. Explicit Metal additionally requires3.5GB reserve headroom; CPU default.
- `artifacts/art/last-vigil-v2/index.html`: local review board with before/current views and evidence links.

```sh
./scripts/bosslab-art-v2 draft
./scripts/bosslab-art-v2 probe front back armor hand hilt sword side head headside palm clay_head clay_palm
```

Preserve existing v2 render files before regenerating; these commands intentionally replace v2 outputs only. The first commands used explicit Metal with sufficient headroom; the high-resolution sequence uses CPU because extra Metal headroom was unavailable. No storage guard was weakened.

## Limits and handoff status

No body rig/skin weights, production retopology/atlases/LODs, combat pose test, gameplay integration or FPS measurement. The newly authored static cape invalidates prior cloth motion evidence for this version. No montage/notifies were authored; all previous combat frame data remains untouched. The result must be judged from actual images; a geometry check does not establish reference-level realism or owner acceptance. Independent reviewers found real improvements but retain **needs work** for the artistic target. Current actual output does not match the approved generated concept's realism. The concept is not used as shipped texture or gameplay evidence.

## Preserved fourth/fifth correction evidence

The fourth actual pass added a pointed sanctuary chest panel with seven fixings, a left-shoulder repair, tapered shoulder edges, padded yoke, restrained surface grain and a forged crown ridge. Low-cost neutral views exposed the panel partially buried due to nonplanar ngon triangulation, the ridge floating above the shell, cut thumb end and armor/straps breaking through the static cape. These views/source are preserved in `iteration-04/`; no artistic pass was declared.

The fifth correction rebuilt the panel as conforming quads using the actual cuirass sections, seated the ridge against the skull, shifted the cape rest surface outside the back envelope, and replaced constant metal finger tubes with tapered leather cores and separate dorsal plate shells. Thumb/fingertip ends are rounded; finger lengths follow index/middle/ring/little ordering. Knuckles are flattened and palm plate curved. These are static modeling changes, not anatomy or rig acceptance.

`static-cape-clearance.json` measures25,665 evaluated cape vertices whose−Y ray hits evaluated body meshes. Minimum back-envelope clearance31.1518mm; zero sampled negative clearances. Excludes attachment zone above1.515m, mantle and all curves, and checks vertex rays rather than arbitrary triangle intersections. It does **not** establish arbitrary-pose clearance or simulated cloth behavior. Actual corrected back/side views visually remove the prior exposed armor/strap defects.

A2.54-second probe attempt failed with a source-insertion syntax error while adding this audit. The scene was unchanged; `probe-syntax-stop.json` and its log are retained. Insertion corrected and Python syntax checked before rerunning. No failure was relabeled as a pass.

Techart inspected current hero, hand, side, rear, armor and hilt views before handing them to independent reviewers. Fifth-version remaining weaknesses: helmet still based on a rounded shell with applied brow/ridge, sparse/feather-like mantle styling, simplified palm/thenar and articulated glove, procedural surface repetition, cape tailoring/lining and retained floating/poorly fitted accessory details. They require coherent mesh/material authoring against the approved concept, not more ornamental curves or brighter lighting. Retopology/UV bakes, rigging/skin weights, true cape simulation and combat-range performance remain future gates.

## ART-05/06 — final focal replacement

After the fifth checkpoint, the orchestrator authorized two substantive focal replacements against the approved concept. Earlier complete fifth source/scene/evidence/audit remain in `iteration-05`; first focal shell/glove images are in `iteration-06`, and reviewed seventh-state source/scene/images are in `iteration-07`.

The final head replaces the elliptical shell, attached ridge and old brow rail with authored median/cheek/temple/occiput contour sections, a continuous crown, front visor planes, overlapping side/nape coverage and a short flared gorget. The nominal front eye gap is5mm before2.5mm shell thickness; it ends at the temples. The first focal attempt incorrectly continued the gap around the side and its diagnostic camera was obscured by the sword. Both failures were corrected and preserved. A final local correction limits the visor edge bevel to the physical plate perimeter; actual neutral clay inspection shows the broad square visor patches reduced. Crown faceting remains; this does not certify perfect normals or production topology.

Both leather gloves now have one connected palm/thenar/web/finger volume, with a continuous bent tapered thumb. Finger lengths follow index:middle:ring:little ratios .87:1:.94:.74, staggered roots and taper. Separate fitted dorsal plates leave the palm and finger creases exposed. The first focal thumb had pearl-like lobes and the palm was too thick; the next revision reduced palm thickness and thenar mass, rebuilt the thumb as a continuous sweep and softened the distal shelf. These are actual mesh changes, not generated-image substitutions.

Final geometry:445 renderable objects,523,820 evaluated vertices,980,484 evaluated triangles; finite positions and2 packed authored images. Each leather glove has24,700 base vertices, one connected component, and zero edges lacking exactly two adjacent faces. This validates closed connected base topology only; it does not validate anatomical fidelity, rigging, skinning or deformation. Static cape clearance remains scoped exactly as above.

Final evidence is one1100×1400 hero plus twelve900×1150 diagnostic images: front, back, armor, hand, hilt, sword, side, head, headside, palm, clay_head and clay_palm. Clay images use a neutral material override on the real geometry. Same scene and source generate all final views. CPU is default; a focal Metal prelaunch was stopped by the additional headroom gate, preserved as `focal7-metal-prelaunch-stop.json`, then completed using CPU without weakening the reserve. Final bounded CPU draft completed in35.42 seconds; actual probe receipt records its own duration.

Independent review confirms the repaired front-only eye opening, unobstructed side camera, continuous thumb/web and static rear clearance. **Overall art target remains needs work**, despite meaningful construction improvements. Head faceting/local shading, padded simplified glove anatomy, mantle's feather-like clumps, procedural material finish and tailoring remain below the approved concept and supplied references. No rig, cloth simulation, production retopology, runtime integration, fresh gameplay test/FPS claim, AI or model connection was added. Next useful work is bespoke fitted-shell and anatomy/material authoring followed by review; rigging and integration remain gated.
