# Hearth A playable walkthrough

Hearth A is a separate, environment-only Unreal editor-game scene. It uses the existing player and controls, without spawning a boss, running combat encounter ticks, showing combat HUD, or starting encounter ambience/music. No AI, learning, combat rules, or packaged application changed.

## Launch

From the project root:

```
./scripts/bosslab-smeltery
BOSSLAB_SMELTERY_VARIANT=original ./scripts/bosslab-smeltery
./scripts/bosslab-smeltery study
./scripts/bosslab-smeltery timing
```

The wrapper selects Hearth A; `original` preserves the previous smeltery. Missing meshes/layout, invalid variant names, and packaged-mode use are rejected before launch. WASD moves, mouse looks, Shift sprints, Space rolls, F jumps; Esc/P pauses and Q quits while paused. Default/Regent game launchers remain separate.

## Implemented scene and coordinate contract

The clear level floor is 20 × 24 m, X ±1000 / Y ±1200 cm. Four full-height invisible boundary boxes block pawn and camera. No rectangular perimeter fence is rendered. Decorative meshes are NoCollision; three additional hidden camera-only boxes use manifest half-extents. Native tests sweep the actual pawn against cardinal edges and corners, including jump height and committed rolls, and check pause/settings/resume isolation.

`Content/BossLab/HearthA/layout.json` references only `/Game/BossLab/HearthA/`. There are 21 unique imported meshes, 27 placements, **417,363 unique / 627,363 placed environment triangles**, before the player. Generated-prop transformed AABBs stay at least **50.707 cm** outside the walk field; this is a conservative bounds check, not a production collision guarantee.

The canonical Blender scene is preserved. Its coordinates are right-handed; to match the approved camera composition in Unreal, the derived export maps author `(x,y,z)` to runtime `(-x,y,z)`, with corresponding reflected placements, light targets and camera boxes, negated placement yaw, and positive actor scales. The FBX Y conversion is separately compensated. `pieces.json` retains original author bounds and explicit expected runtime bounds. Author entry (−600,−800,95) becomes runtime (+600,−800,95), facing toward (0,800), yaw110.55605°. Initial camera rotation is applied after possession.

Two generated meshes have measurable transfer differences: cistern maximum-height difference0.962253 cm and ore rack maximum-X difference1.714846 cm. Both pass the existing2 cm import tolerance; neither is described as submillimetre. The source has417,593 triangles; Unreal retains417,363. Actual cistern/ore AABBs remain102.49/90.62 cm outside the field. Water top is88 cm; imported cistern maximum is115.35 cm, with the surface inset in XY. Visual rim fit is inspected separately from that bounding-box comparison.

## Lighting and materials

One cool shadowed window spotlight and four warm shadowless points illuminate the scene. Three warm points coincide with visible lantern emitters; the furnace point is outside its mouth,1600 lumens with1500 cm attenuation radius. The window spotlight is16000 lumens,16°/27° cone,4000 cm radius; its local volumetric scattering is4. Broad directional fill is deliberately low: .22 neutral-warm shadowless bounce and .35 cool shadowless fill. The window is the only shadowed light. No global lighting preset changed.

Quench water has an animated tangent-normal ripple. Two soft translucent, unlit depth-faded vapor cards provide approximate steam; this is presentation, not fluid simulation. The window is unlit/emissive. The floor wetness mask follows the reflected quench location. There is no claim that generated color/roughness maps are calibrated PBR. Window illumination is visible, but the volumetric shaft remains subtle rather than matching the concept's strong painted beam.

## Actual verification

- Initial full native suite: **44/44**, zero warnings/failures, exit0, before final entry and art fixes.
- Final focused arena suite: **3/3**, zero warnings/failures, exit0. Includes the added regression that300 warmup ticks leave the actual pawn stationary and never roll/jump.
- Final full720p actual-player study: **14 engine PNG frames**,31 simulation seconds, exit0. Standing entry and walking work-bay views inspected. `bounce100/frame-0300.png` shows the actual stationary player after warmup. Frame0480 retains a transient `Preparing SoundWaves(4)` engine overlay; this is not hidden or described as a clean first startup.
- Screenshot-free comparison before final bounce:75% averaged56.49FPS (3435frames,p95 18.955ms,p99 34.583ms,37frames>33.3ms,16>50ms,max400ms).100% averaged59.55FPS (3572frames,p95 16.733ms,p99 18.562ms,6frames>33.3ms,4>50ms,max62.447ms). The higher-resolution run happened to run faster; this is shared-machine/cache variability, not evidence that higher resolution optimizes performance. Both retained zero PNGs.
- **Final full 720p bounce build:** 59.647 FPS mean, 16.7653 ms mean, 16.6745 ms p95, 18.7435 ms p99, 3,578 measured frames; 3 frames >33.3 ms, 2 >50 ms, max63.932 ms. Zero screenshots; process exit0. Native frame deltas are measured after300 simulation warmup ticks, not an external GPU profiler or locked60 guarantee. Normal desktop check completed: the human character was visible, W changed position, and pause → Settings → back/resume worked. Selecting Quit Game with the arrow key/Return closed the normal instance (exit0,114.49s). Short synthetic key presses were unreliable; Q did not conclusively quit in this check. The first normal observation was near top-down despite no explicit mouse tool action, so normal entry composition and physical mouse/Shift comfort remain unverified. Source initializes pitch−12° and only clamps unlocked pitch to−55..25°; focus/mouse warp is a possibility, not a proven cause. No speculative camera change was made.

The timing mode runs3900 simulation ticks, excludes the first300 stationary warmup ticks, and requests **zero screenshots**. Native rendered-frame deltas, path and process logs are retained. Screenshot studies include readback/PNG overhead and cannot establish clean performance. The wrapper now defaults to full720p with low shadows, AO disabled and a60FPS cap. `BOSSLAB_HEARTH_SCREEN_PERCENTAGE=75` restores the earlier960×540 internal render at1280×720 output, scoped to Hearth A. The original smeltery/default presets are unchanged. No locked60 or isolated optimization claim is made.

## Retained failures and remaining limits

Initial studio previews were rejected; initial game evidence was also rejected for darkness, mirrored composition and incorrect entry view. A subsequent study exposed an automation bug: a roll scheduled inside stationary warmup moved the pawn320 cm backward, compressed the camera and hid the body. The study action clock now starts after warmup; human gameplay was not changed to conceal this issue.

Both Hearth A imports saved all assets and wrote signed-bound reports, then exited1 with the previously observed ICU `ubidi_close` / Slate text-layout invalid-free shutdown crash. Exact logs and crash stacks are retained. Subsequent independent native tests and actual game launches exited0. No engine/global patch or suppression was applied.

The room remains below the approved concept's density and finish: masonry repetition, coarse generated furnace surfaces, soft small props, dark remote bays and subtle steam/shaft remain visible limitations. Actual mouse comfort, physical Shift and owner artistic acceptance are not inferred from automated movement. The default packaged build and old smeltery remain preserved.

The first compile used the artist's explicitly released heavy slot but omitted updating `editor.lock`; root caught it. No overlapping heavy job or asset write occurred. Later builds/imports recorded ownership before starting. After the normal game quit, a desktop observation relaunched a bare Unreal Editor (PID51001). Root explicitly authorized its shutdown; the builder verified its exact executable, sent SIGTERM only to that instance, and confirmed no UnrealEditor processes remained. `editor.lock` is released. Cleanup and process-audit receipts are retained.

## Evidence

- Runtime logs, native reports, failures, screenshots and timing: `artifacts/unreal/hearth-a-walkthrough-2026-11-16/`.
- Frozen full720p visual study: `bounce100/`; earlier75% visual study: `final75/`; failed initial and intermediate studies: `initial/`, `corrected/`.
- DCC exports/import reports/provenance: `artifacts/art/hearth-a-2026-11-16/`.
- Canonical source and derived export/import scripts: `unreal/art-studio/source/hearth_a/`.
- Engine logic/tests: `WardenSmeltery.cpp`, `SmelteryTests.cpp`, with launcher wiring in `scripts/bosslab-smeltery` and `scripts/bosslab-unreal`.

Exact next action: owner launches the frozen review build and judges the room, physical mouse/Shift controls and initial camera framing. Rear/side bays remain dim and the art is not reference-fidelity accepted. Preserve the old smeltery, failed evidence and runtime measurements; no boss or AI work is implied.
