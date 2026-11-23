# Hearth A2 integration contract — read-only assessment

2026-11-16. The owner rejected A's shape and prop fidelity. A2 is a separate substantive DCC rebuild, not a further lighting/material adjustment to the accepted-for-review technical build. This document proposes integration requirements only. No C++, assets, launcher, settings, build or runtime process was changed for this assessment. Integration begins only after root accepts the actual DCC composition.

## Preserve the playable fallbacks

Keep `/Game/BossLab/HearthA`, its layout, canonical Blender scene, failed evidence and current compiled game intact. Keep `/Game/BossLab/Smeltery` as the older fallback. Use a new `/Game/BossLab/HearthA2/` destination and separate DCC/export/evidence directories. Proposed future selector: `BOSSLAB_SMELTERY_VARIANT=hearth-a2`; it is **not currently implemented**. Existing `hearth-a` and `original` selections must remain explicit and functional. Do not make A2 the wrapper default until imported gameplay views and normal controls pass review.

Current runtime hardcodes A's 20 × 24 m floor, spawn and study route; its loader does not consume `walkable_cm`. The artist's proposed A2 16 × 18 m court is provisional. The final approved dimensions must drive the collider, camera envelope, scripted route and native fixture together. It is unsafe to supply a smaller visual layout and assume the old collider will adapt.

## Diagnoses from the current source

**Primary forms.** The previous furnace's coarse silhouette and layered/faceted surfaces are asset geometry problems. Recomputing vertex normals or increasing lights cannot turn those shapes into the concept's stepped forge. Require matched clay views of the new hero forms before their texture treatment is accepted.

**Flat floor.** A's exported `M_SmeltFloor` supplies generated base color, constant roughness0.8 and a local procedural wet roughness mask. It supplies **no normal map, height map or displacement**. The collision/render floor is predominantly planar. The importer supports `normal_gl`/`normal_dx`, but absent maps cannot be created by that support. The generated furnace material likewise has diffuse and ARM maps, not a normal map. Vertex normals and tangent-space normal textures are different data.

The runtime also disables dynamic GI, reflection methods, mesh distance fields, Nanite and auto exposure. The performance preset disables screen-space AO. Shadowless points and directional bounce therefore provide little contact or indirect structure; emissive objects do not automatically light their surroundings. These are contributing constraints, not a reason to switch on every expensive renderer feature.

**Camera.** `AWardenChallenger::BeginPlay` and `PossessedBy` set control rotation to pitch−12/yaw0. The walkthrough sets its entry rotation in BeginPlay and once on its first tick. Normal `Look()` forwards mouse-axis input into controller pitch. Unlocked tick clamps pitch to−55..25 degrees, and recenters **yaw only**. Saved settings do not store camera pitch. There is no identified code path that deliberately initializes a top-down normal view. The CUA observation of steep pitch remains unexplained; a focus/cursor delta is plausible, not established.

The scripted study repeatedly forces camera rotation, so its correct entry image does not validate normal mouse/focus initialization. The earlier disappearing study player had a separate, proven cause: a roll inside warmup moved the pawn backward into camera compression; that clock bug has already been fixed and tested.

## Coordinates, normals and export requirements

Use one explicit authoring-to-runtime convention throughout A2:

- Authoring coordinates are metres, +X across the room and +Y toward the rear.
- Runtime positions are centimetres: `UE = (-100 * author.X, 100 * author.Y, 100 * author.Z)`. This makes the author's left forge appear on the left of the Unreal entry view.
- Under the verified FBX route, export-copy vertices use `(-x,-y,z)` because the importer separately flips Y. That copy transform has positive determinant, so do not add an extra winding reversal. This is specific to the tested FBX route, not a universal glTF rule.
- Reflect placement X and yaw, light positions/targets, camera boxes, spawn/look target, decals and world-space material masks exactly once. Existing placements have zero pitch/roll; nonzero rotations require a full basis-conjugated matrix, not guessing additional Euler signs.
- Keep actor scales positive. Preserve canonical author geometry and UVs; record derived-copy hashes. Recompute or correctly transform normals with the inverse transpose after geometry edits, preserving deliberate hard edges. Validate tangents against UV orientation when a normal map is present.
- Retain both `author_bounds_m` and `ue_expected_bounds_m`. Validate signed minima/maxima, used triangle counts, finite vertices, UV layers/material slots, front/back visibility and rendered orientation. Size-only validation previously missed reflection.

A's imported generated outliers differed by up to1.715 cm because extremal faces/vertices were not retained. That was explicitly recorded, not hidden under a submillimetre claim. A2 must record its own discrepancies and compare them with clearance. Reject substantial silhouette loss or boundary intrusion even if an overall two-centimetre tolerance passes.

## Proposed handoff manifest

Existing supported fields are `instances`, `lights`, and `camera_collision`. The following extended fields are a **proposal requiring future runtime/launcher changes**, not currently supported behavior:

```json
{
  "schema": 2,
  "scene_id": "hearth-a2",
  "coordinate_space": "unreal_cm",
  "author_to_runtime": "(-100*x,100*y,100*z)",
  "walkable_cm": [1600, 1800],
  "spawn_cm": [400, -400, 95],
  "entry_target_cm": [0, 500, 95],
  "entry_pitch_deg": -12,
  "instances": [
    {"asset": "/Game/BossLab/HearthA2/SM_Example", "location_cm": [0,0,0], "rotation_deg": [0,0,0], "scale": [1,1,1]}
  ],
  "lights": [],
  "camera_collision": []
}
```

The numeric field/spawn above illustrates the proposed compact layout, not final approval. Require finite values, a supported schema, the exact A2 asset prefix, positive scales and a declared light budget. Reject excess or malformed lights instead of silently truncating the current maximum-six loop. Required assets must exist before launch; no silent substitution with the old room.

## Camera and collision envelope

Current camera: 500 cm arm, socket offset(0,45,100), pitch−12, probe radius16 cm, horizontal FOV75°. Saved distance range is0.7–1.5×. The pawn capsule leaves 34 cm from the field wall. Current field walls block both pawn and camera; art meshes are NoCollision and separate camera boxes exist outside the field.

For a 16 × 18 m field, reusing author spawn(−6,−8)m leaves only1 m to the rear boundary and will compress the camera. Candidate author spawn around(−4,−4)m facing(0,+5)m puts the default eye analytically near(−5.5,−8.5,3.0)m, before collision and dynamic offsets. It is materially safer, but the exact camera transform, lateral socket and probe must be checked against the new architecture. Show both pawn and eye landmarks in DCC. Maximum-distance camera shortening near edges is expected; an invisible or heavily cropped player at the default entry is not.

If the compact field needs camera space in the decorative apron, an A2-only option is pawn boundaries that ignore camera plus explicit camera-only proxies for actual enclosing walls, roof and nearby props. Retain camera collision on the floor. This requires deliberate proxy coverage and native/game tests; do not simply disable spring-arm collision or remove boundary protection. The old A contract remains unchanged.

For the normal steep-pitch issue, the next approved engine pass should use a bounded, opt-in startup diagnostic: log possession/first-tick rotation, focus transitions, look-axis deltas, actual camera transform, arm compression/hit actor and owner visibility for a few seconds. Keep it local, separate from any controller/policy data, and stop automatically. Compare a normal physical launch with desktop automation. Do not force pitch every frame or discard arbitrary user input as a speculative fix. Avoid querying an app binding after Quit, which previously relaunched a bare editor.

## Required materials and visible relief

Deliver separate material records for base color, roughness/metallic/AO packing, normal convention and provenance. Base color is sRGB; normal and packed scalar maps are linear. The current importer flips the green channel for OpenGL normals and leaves DirectX normals unchanged. Verify with an asymmetric raised/recessed test under grazing light; a label alone is insufficient.

For floor relief, prefer actual shallow bevel/groove geometry with stone tops on the level walking plane, or normals baked from an authored height/geometry source. Sink mortar and joints below that plane rather than introducing untested stepped locomotion. Give major broken edges actual silhouette geometry. Do not call a luminance-derived/generated map measured displacement or calibrated PBR. A base-color photograph containing shadows remains color, not geometric relief.

Use repeatable texel density, nondegenerate UVs and stable tangent space. Actual PNG files must have PNG signatures; previous exports had WebP bytes under PNG names. Validate missing files, channels, dimensions and material-slot assignments before opening Unreal. Water must be fitted below the actual imported rim, with mapped world-space wetness and restrained translucent vapor; no fluid-physics claim.

## Lighting contract and current source inventory

Current A runtime sources, provided as diagnosis rather than A2 defaults:

| Source | Runtime location cm | Lumens | Radius cm |
|---|---|---:|---:|
| Furnace | (450,1150,230) | 1600 | 1500 |
| Window spot | (−750,1605,640), aims at(100,0,0) | 16000 | 4000 |
| Entry lantern | (920,−550,352.5) | 500 | 1000 |
| Rear lantern | (−480,1360,297.5) | 550 | 1000 |
| Rear-side lantern | (−1120,1380,317.5) | 400 | 850 |

Window cones are16°/27°, shadowed. Other local lights are shadowless; directional bounce is .22 neutral-warm/.35 cool, both shadowless. Several older visible lanterns have no corresponding dedicated point, and remote bays remained dim. This mismatch must not be repeated as an implicit promise that emissive materials supply GI.

A2 should pair each important fixture with a named lighting role and a coverage region. A point may represent a nearby fixture group, but the mapping must be explicit. Provide `fixture_id`, location, color, lumens/radius and shadow intent; spot records also need target/cones. Start within six local lights and one primary shadowed window source. Put lights outside solid furnace/glass surfaces, prove the window ray clears its opening, and keep enough camera-space illumination to read the player and tools in every bay. Additional shadow/contact costs require a measured A2-only decision, not a global preset change.

The studio preview must include the same limited source positions and a neutral exposure comparison. A giant studio area light can conceal a dark or flat runtime layout. Inspect hero, quench, left/right rear bays and floor grazing views; do not pass the room on the hero angle alone. Stronger fill is not a remedy for wrong shapes, missing relief or every unlit fixture.

## Integration gates after DCC approval

1. Substantive clay/material views match the intended forge silhouette, roof/loft proportions, workshop grouping and actual entry-camera envelope. Root accepts these actual views, not only a generated board.
2. Export audit passes the stated coordinate/normal/material contract, with measured prop clearance and source hashes. Preserve A and its importer evidence.
3. Claim the engine lock and sole heavy slot; import only A2. Validate saved assets and independent reload. Prior imports saved successfully but crashed on ICU/Slate teardown; record exit codes honestly and do not treat an import report alone as a successful process.
4. Add the A2 variant only then. Test actual pawn edge/corner/jump/roll behavior, camera proxies, stationary warmup, no-boss isolation, pause and Quit. Old variants remain accessible.
5. Inspect normal and scripted player views. Do not let scripted camera control stand in for normal focus/input testing. Capture actual water/steam and grazing floor detail.
6. Run screenshot-free timing at full720p and keep all regressions. A's59.65FPS result does not validate A2. Start with an environment budget around the previous627k placed triangles, then adjust only from actual geometry/draw/material and frame-cost evidence. No rendering, build or test was run for this read-only report.

No boss, AI, RL, runtime model adapter, gameplay timing or public deployment work is included.


## Source-only continuation (2026-11-16)

Root authorized reversible source implementation while DCC proceeds. This supersedes the opening paragraph only for the following source changes; the compiled build and current runtime assets remain untouched.

- `WardenSmelteryLayout.h` validates schema version 2, scene `hearth-a2`, explicit Unreal centimetres, approved 1600×1800 cm floor, finite spawn/target/pitch and default 500 cm camera/probe clearance. The source uses supplied approved dimensions rather than silently retaining the old collider. Instance transforms must be finite with positive scales and the exact A2 asset prefix. At most six explicit lights, each with fixture ID and valid photometric/cone values, and one shadowed spot are allowed. Camera proxies are validated too.
- `WardenSmeltery.cpp` resolves the complete A2 manifest and required meshes before spawning the room, uses its spawn/entry/floor dimensions, scales the existing position-driven route and writes separate `HearthA2Study` / `HearthA2Timing` evidence. Invalid or incomplete A2 startup logs an error and exits rather than substituting another room. Existing A and original defaults retain their values.
- `scripts/bosslab-unreal` accepts explicit `BOSSLAB_SMELTERY_VARIANT=hearth-a2` and passes `-BossLabHearthA2`. `scripts/bosslab-smeltery` itself is unchanged and still defaults to A. Missing imported A2 data rejects before launching the editor.
- Added `BossLab.Arena.HearthA2ManifestValidation` tests for the parser, coordinate/spawn semantics, wrong dimensions/prefix/space, negative scale, unsafe spawn, invalid light data and excessive light budget. These are asset-independent contract tests, not actual imported-room validation.

Only launcher Python syntax was checked successfully. **C++ has not been compiled; no native tests, import, runtime views or timing have run for A2.** No global configuration, lighting tuning, controls change, camera workaround, boss or AI change was made. Next: root approves the combined actual DCC scene, artist releases the heavy slot, then guarded compile and scoped import followed by actual-room boundary/camera tests and visual review. Future explicit source launch (not yet runnable): `BOSSLAB_SMELTERY_VARIANT=hearth-a2 ./scripts/bosslab-smeltery`.

### Foreground work-island revision (source only)

Root and artist subsequently approved side-corner work islands inside the 16×18 m outer pawn boundary. This **supersedes the completely clear rectangular field assumption**: the central route must remain navigable, but A2 is not a boss-fairness test. Add mandatory `prop_collision: []` to the A2 manifest; each nonempty record has `cluster_id`, `location_cm`, `extent_cm` (positive half-extents), and `yaw_deg`. These hidden rotated boxes block Pawn and Camera only; visual meshes remain NoCollision. Validation rejects nonfinite/invalid data and initial capsule-envelope overlap. Native parser tests now cover negative extents and a cluster covering spawn.

Optional `camera_boundary_mode: "outer_proxies"` makes only A2's invisible pawn perimeter ignore Camera, while the floor and prop islands continue blocking it. This mode requires at least four explicit `camera_collision` records for the real outer enclosure; their count does **not** prove enclosing coverage. The artist must supply continuous wall/roof coverage and actual camera tests must verify it. Default `"field"` retains the old behavior. Neither mode changes old A/original scenes.

The analytic default-camera check does not certify saved 1.5× camera distance or dynamic spring-arm behavior. The proposed rear camera apron reaches author Y−12 m with sides X±11 m. Final geometry, enclosure, entry sweep and physical camera extremes remain pending review. The scaled old study loop may intersect new foreground clusters: obtain a clear authored loop and validate/test it against the final colliders before claiming a successful walkthrough. No compile, native execution or heavy job has occurred for these source additions.

### Bounded normal-entry diagnostic (source only)

Root requested an opt-in camera investigation without a speculative controls fix. `BOSSLAB_CAMERA_DIAGNOSTIC=1` enables a maximum ten-second, eighty-record startup log (at most 48 nonzero raw mouse-axis records, leaving room for half-second state samples). Records include controller rotation, pawn position, camera position/rotation, arm length, offsets, actual camera distance and viewport focus (`-1` if unavailable). Raw Look/Turn values are recorded before the existing input processing; input, sensitivity, focus and rotations are not overridden by the diagnostic. Existing entry initialization remains unchanged and is separately marked in the log.

`BOSSLAB_ENTRY_CAPTURE=1` requests one timestamped screenshot under `Saved/NormalEntryDiagnostic` after eight wall-clock seconds of normal play. It introduces no scripted motion or camera updates and does not quit the app. The launcher rejects combining this capture with study/timing. It can be used independently of logging; launching/focusing the application can still generate real OS mouse events, which this mechanism does not suppress. Eight seconds is not proof shaders/audio preparation have finished: inspect the actual image and logs. Example after an approved build/import: `BOSSLAB_SMELTERY_VARIANT=hearth-a2 BOSSLAB_CAMERA_DIAGNOSTIC=1 BOSSLAB_ENTRY_CAPTURE=1 ./scripts/bosslab-smeltery`.

Launcher syntax passed; C++ remains uncompiled and no normal-entry image has been captured by this new code. This is instrumentation, not evidence that the earlier steep-camera cause is resolved.

A2-only AO cost/appearance trial is prepared behind explicit `BOSSLAB_HEARTH_AO=0|1` for non-original quality presets. It overrides `r.AmbientOcclusionLevels` and caps `r.AmbientOcclusionMaxQuality=50` in that launched process only; installed engine renderer source confirms these variables. It is not enabled by default yet. Inspect normal maps, grazing stone joints and prop contact in actual runtime, then compare otherwise-identical screenshot-free runs before choosing the final A2 setting. SSAO cannot supply missing silhouette/geometry or substitute for motivated lighting. No global config or old A quality was changed.

A2 now also requires `study_waypoints_cm` (2–32 distinct, separated world-space points at Z95 inside the pawn envelope). The validator checks spawn→first, every route segment and last→first against rotated prop boxes expanded by 50 cm horizontally/90 cm vertically. It checks the initial camera sweep against those proxies expanded by the 16 cm probe. These are conservative analytic checks; actual pawn/jump/roll/camera sweeps remain required after compilation. A2 study source follows these authored points and reports actual travelled centimetres, waypoint arrivals/count, coverage completion and ticks since last measured motion. A timer finishing is explicitly insufficient to claim room traversal. Added parser/rotated-proxy tests remain unexecuted until the approved build.
