# Funeral Regent explicit cage study — technical gain, visual gate failed

2026-11-09. New method, separate from the rejected primitive/voxel study. Initial candidate plus two targeted corrections completed. **Neutral Funeral Regent identity/construction gate remains rejected. No rig, weight test, materials or game integration followed.** Retain the continuous body as an unaccepted technical resource only.

## Actual construction

`unreal/art-studio/source/funeral_regent_cage.py` constructs shared torso cross-section rings, omits explicit shoulder patches and bridges their boundary vertices into upper-arm/elbow/forearm/wrist/palm loops. A shared crotch partition bridges into two leg/ankle/sole outlines. Final thumb branches extrude actual palm faces with connected boundaries. No voxel, overlapping-shell join, remesh or imported character was used. Anatomical left is +X, with reel on viewer-right in front; sword is anatomical right.

Hood, planar mask with actual eye apertures, rib wraps and two curved mantle halves are separate shell meshes. The body alone is the watertight surface. The source comment calling the mask closed is imprecise: it has deliberate eye apertures and an outer perimeter with a Solidify modifier. Mantle halves cover back/flanks and open at front; no cloth simulation or weight deformation. Three separate skull cores are proxies, not completed skull anatomy. No generated textures or new concept imagery.

Attempt01 passed closed-body counts but arms were blade-thin because section offsets occupied Y/Z instead of a frame perpendicular to the descending limb. Attempt02 corrected the frames, added eye apertures and sole support loops; body-only views exposed crude head/hand and garment forms. Attempt03 added connected thumb branches, separated neck/head profiles, corrected leg-loop correspondence, reshaped hood/mask and introduced asymmetric mantle fold paths. All actual outputs and source snapshots are retained; no fourth design correction.

## Evidence and saved verification

Final scene: `unreal/art-studio/regent-cage-2026-11-09/regent-cage-03.blend`. Latest two scenes02/03 retained; scene01 pruned with a hash receipt under the declared last-two policy, preserving its actual images/source/logs.

Evidence: `artifacts/art/regent-cage-2026-11-09/attempt-03/`: front, side, back, threequarter, body-front, body-side and head PNGs,640×800. Four initial plus seven second plus seven final renders =18 actual stills. Neutral/body diagnostic cameras are explicit; body-only views hide costume, not proof the costume is clear of the body.

Final build/render37.86s exit0. Separate saved-scene audit2.39s exit0, recomputed after reopening the frozen blend:

- Body429 control vertices/417 faces, one component, zero boundary/nonmanifold edges, zero control faces below1e-12m².
- Positive signed volume0.0574435m³;3376 evaluated triangles, none below1e-12m², minimum4.19e-6m².
- Evaluated minimum soleZ exactly0 on both sides.
- Twelve evaluated vertices in each local arm sample slab. Elbow cross-axis/Y extents98.06/65.34mm, wrist63.79/43.37mm. These are finite slab bounds, not exact cross-section intersections.
- Zero armatures in saved scene. No clean self-intersection, all-costume clearance, anatomy, production topology or deformation certificate follows from these tests.

Audit source `funeral_regent_cage_audit.py`; commands `python3 scripts/bosslab-regent-cage 3` and `python3 scripts/bosslab-regent-cage-audit audit`. They reproduce a **rejected study**, not approved production art. All jobs completed behind unchanged10GB/24GiB guards. Last receipt free26,690,297,856bytes; Unreal2,742,722,560bytes.

## Independent visual outcome and next method

Art direction retains the connected limbs/thumbs and grounded soles as genuine local progress, but rejects B's neutral shape: simple mask slab, long hood tube, ladder ribs, smooth coat-like mantle and pale shoulder-boundary intrusions. Body anatomy is still a coarse mannequin, with unsolved shoulder/crotch craftsmanship and basic hands. Do not hide these with weights or surface detail. A functioning projected silhouette or numeric integrity count cannot substitute for the selected design.

Next work should author the **head/hood and shoulder-yoke pattern as controlled focal meshes with shared section landmarks and actual attachment fit**, evaluating against the chosen B sheet at matching front/side angles before any full-character expansion. Preserve this closed-body resource, but do not describe it as an accepted visual foundation. Rigging remains blocked by the neutral art gate; no arm/panel weight test was started.
