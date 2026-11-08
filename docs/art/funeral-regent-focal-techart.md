# Funeral Regent landmark focal study — rejected

2026-11-09. Three actual candidates, initial plus two targeted corrections. **Focal face/hood/yoke gate failed; no full-body assembly, weighting, materials or gameplay expansion.** Previous connected cage and playable assets were neither loaded nor edited.

## Actual method and artifacts

Source `unreal/art-studio/source/funeral_regent_focal.py`; shared art-director input `regent_focal_landmarks.json`. The11 authored curves, named features, rear hood profile and shoulder arcs are genuinely consumed. One transform converts normalized coordinates into metres: X=.075x, Y=-.065-.075y, Z=1.65+.075z. Reflection is baked in coordinates and normals recalculated; no negative object scale is used.

The mask is one constrained triangulated surface. Outer silhouette, mirrored almond eye loops, brows, lower orbits, nose-side paths, cheek/jaw paths, closed-mouth paths and midline are constraints, not separate face decals. Eye interiors are excluded through closed-polygon tests, not rectangular cell deletion. A2.5mm inward Solidify modifier provides real rims. The approach is not production quad retopology.

Initial interpolated path depth plus subdivision caused radial pinching. Correction1 introduced a cubic radial interpolation field and distributed interior samples to improve triangle aspect ratios; the extra samples add no random displacement. Correction2 fits the field to sparse original landmarks with regularization0.005, retaining the constrained path locations but **not exact depth interpolation at every landmark**. Curves are piecewise-linearly sampled; this does not implement the JSON's suggested shape-preserving cubic interpolation. These deviations matter: the final shape loses mouth/lip definition despite smoothness.

Hood opening uses the shared curve and curved rear depth profile. A separate closed cranial volume tests visible depth. An initial erroneous rear-depth clamp displaced the rim behind the mask; correction1 repaired it. Correction2 closes/curves the crown seam and adds a real nape-to-yoke bridge. However the resulting fit still allows skull breakthroughs, and the front/rear yoke remains stiff disconnected-looking cloth. The standalone skull is a focal fit reference, not the previously frozen body head or a validated full-body attachment.

Scenes `unreal/art-studio/regent-focal-2026-11-09/regent-focal-02.blend` and `regent-focal-03.blend` retain the latest two. Attempt01 scene pruned with hash receipt after final readback; all source snapshots, images/logs remain. Each candidate has five760×900 renders: head-front, head-side, head-threequarter, bust-front, bust-back.15 actual images total; no generated image is used as build evidence.

## Failures and retained gains

Actual almond apertures, visible nose side profile and joined facial feature surface improve on the previous blank grid mask. That local gain is not acceptance. Initial cheek/eye/chin pinching improves, but final lips/alar transitions are washed into a weak uneven field. The hood crown and nape reveal gray cranial penetrations in the final side view; overlapping yoke pieces still do not read as a seated sewn garment. No texture, extra ornament or broad body rebuild can be justified by this failed gate.

The initial tool execution failed before any render because a2D CDT vector sum used a3D zero vector. Its receipt/log/source were preserved. The corrected initial run and both visual corrections exit0. This scripting retry did not add a rendered design candidate.

Independent art-director review inspected final head front/side/three-quarter and bust back, and explicitly rejects the focal gate: lips lost, crown/nape breakthroughs and hovering yoke remain. No fourth correction or full-body/material/rig advancement is recommended. Shared landmarks remain design constraints, not accepted mesh evidence.

## Saved readback, boundaries and next action

Final run including five renders and reopening saved scene exited0 in37.96seconds. Readback records665 mask control vertices,974 faces,96 boundary edges before Solidify, zero control faces below1e-12m² and zero armatures. This is not a garment-contact, all-triangle intersection, skin-deformation, production topology or artistic quality pass. The visible skull penetrations explicitly invalidate a fitted-hood claim. Exact source/scene/input hashes are recorded in `artifacts/art/regent-focal-2026-11-09/attempt-03/readback.json` and the delivery manifest.

Commands `python3 scripts/bosslab-regent-focal 3` reproduce the rejected final study. CPU2threads, unchanged24GiB/10GB guards. Last receipt:26,648,326,144bytes free,2,743,902,208bytes under Unreal. All owned jobs exited. No downloads, physics, AI or game edits.

Next distinct method requires deliberate **patch-based quad topology around eyelids/nose/lips** instead of global depth interpolation, followed by an independently constructed closed hood control cage fitted to the actual cranial envelope before adding yoke. First prove one clean front/side facial patch and closed cranial shell, then assemble sewn support panels. Do not start a fourth minor correction of this three-candidate study or claim that landmark input alone solved character craftsmanship.
