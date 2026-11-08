# Ashbound Knight — first playable outfit pass

Owner-approved creative direction, implemented 2026-11-06. First playable outfit pass delivered for silhouette/material review. Technical outfit checks pass; the final single-instance benchmark supports review. Artistic acceptance and sustained performance remain open.

## What is authored

WardenOutfit.cpp constructs26 original polygon parts totaling15,448 rendered triangles and39 material sections. These counts exclude the underlying Epic mannequin body. Parts include the enclosed slit helm/crest, chest and abdominal plates, shoulder/forearm/hand/leg armor, boots, ivory mantle, oxblood tassets and two split cape panels, plus Oathwake's tapered blade and broken-ring hilt. Five shared dynamic materials distinguish steel, bronze, red cloth, ivory and charcoal underlayer.

This is a lightweight stylized first model pass. The underlayer remains the recolored Epic mannequin, rigid armor follows its existing bones, and the two cape panels use controlled sway/folding. There is no new skinned character mesh, physical cloth, strand fur, baked wear/normal maps, production UV unwrap or distant LOD chain. Quilting, mail, pouch, detailed finger armor and surface weathering from the proposal remain targets. The retained OBJ/MTL is a static reference-pose armor/sword assembly, not an animated character export.

Oathwake uses the existing shared hilt and14–148cm blade endpoints. Authoritative combat definitions, movement/contact code, scripted rehearsal and all existing fundamentals assertions remain unchanged from the controls checkpoint. During roll/death only, presentation support now includes actual armor vertices to keep the new geometry above the flat arena floor. The capsule, roll travel/cost/protection and active swing paths are unchanged. No adaptation, RL, training or model adapter is active.

A project-authored16×16×6 ambient cubemap supplies broad reflections/fill for steel, with no downloaded environment map, real-time GI or reflection tracing. The normal arena also uses this lighting; it is not a capture-only beautification.

## Failures preserved and fixed

- Initial compile variable-shadow failure; later test pointer-type compile failure.
- Decorative mesh physics-cooking warnings: disabled unnecessary cooked collision data; parts remain non-colliding.
- Actual editor views exposed reversed front faces, low mantle attachment and insufficient ambient fill.
- Native outfit test caught cloth assigned to steel by editor fast-build section mapping and armor/cape penetrating the floor during rolls. Corrected section map, cape axes and outfit support; minimum tested vertex height now approximately0cm through eight headings.
- Startup order could create the obsolete sword after outfit dressing. Its initial visibility now respects fighter role; regression covers Reset before BeginPlay.
- Headless cooked launch asserted because runtime mesh rendering resources require a renderer. Package tests now run graphically; native tests remain headless.
- First rendered cooked run caught uninitialized UV streaming metadata. Explicit per-material metadata added; no assertion suppressed.
- One native run was interrupted after a physics-teardown stall. A clean unchanged rerun also paused in a physics transform operation, then completed21/21 in126.34s. Samples/logs retained; no claim that this engine timing issue is fixed. A briefly overlapping package command was stopped and restarted only after the native run ended.
- Sandboxed video encoding could not access the macOS encoder; reviewed execution encoded/decoded intermediate evidence successfully.

## Evidence and reproducibility

Evidence directory: `artifacts/unreal/ashbound-2026-11-06/`. It includes dated intermediate captures, manifests, failed reports/logs and native diagnostics. Videos are actual fixed30Hz engine frames, not live FPS measurements or generated concept art. Intermediate raw sequences were reduced only after successful encoding and independent full-frame decoding; hashes and selected raw frames remain.

Commands: `./scripts/bosslab-unreal build`, `test`, `package`, `package-test`, `package-capture outfit`, `package-capture motion`, and `BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-benchmark 720p`. Preserve reusable capture directories before another run. The package test intentionally enables rendering. Storage guards remain10GB under unreal/ and24GiB free.

No public deployment, model/asset downloads, paid services or persistent jobs were added. Existing reference video assets are review-only and not shipped.

## Final verified results

- Native **21/21**, standalone graphical cooked **18/18**, both with zero test warnings/failures. Reports: `native-final.json` and `cooked-final.json`. This includes unchanged combat/control checks plus outfit assembly, material slots, streaming metadata, startup/reset visibility, blade endpoints and floor clearance through eight roll headings.
- [Four-angle outfit study](../artifacts/unreal/ashbound-2026-11-06/outfit.mp4) and [normal-action swing/roll study](../artifacts/unreal/ashbound-2026-11-06/motion.mp4): each 180 actual frames, encoded and independently decoded. Four stable outfit views and all 48 sampled motion frames inspected. These are fixed 30 Hz captures without audio, not human play or real-time performance evidence.
- Final captures use a capture-only PSO proxy-creation override to avoid initial blank world frames; normal gameplay/benchmark retains the default. Earlier startup failures remain in `startup-*` evidence. Normal startup can still show brief shader/proxy warmup.
- [Static OBJ assembly](../artifacts/unreal/ashbound-2026-11-06/model/ashbound.obj): 26 objects, 8,668 vertices, 15,448 triangles, five materials. Cooked and editor exports match. This is not a rigged character export.
- Initial performance preset, 1280×720 output / 75% internal scale: **37.88 FPS mean**, p95 **50.04 ms**, p99 **87.85 ms**, 231/2,027 frames over 33.3 ms. A separate profiled run was approximately **38.19 FPS**. A second BossLab process was subsequently found running since 16:17, before both these measurements. These runs are confounded and cannot establish outfit-induced regression.
- The 1,200-frame CSV profile (180 startup samples excluded) reports mean game-thread 2.64 ms, GPU 9.85 ms and render-thread 15.39 ms, with substantial waiting. These overlapping timings are not additive and do not isolate the cause. Shared-machine conditions and profiler overhead prevent attributing the regression solely to the costume or to host contention. All bad results remain preserved.

**Final single-instance retest:** the owner authorized closing the second game; it exited after SIGTERM. The unchanged build/preset then measured **59.07 FPS mean**, **16.7936 ms p95**, **20.4880 ms p99**, maximum136.5382 ms, **11/3,233 frames over33.3 ms**. Source: `single-instance-summary.json` and raw CSV. Supports short-session review, not locked60, long-session stability or isolated proof of costume cost. No game/engine helper remained after the test. The two earlier poor runs and closure receipt are retained.

Final packaging hit the 24 GiB reserve during duplicate-app signing. All 25 duplicate app files matched the staged app before the duplicate was removed; the staged app then passed strict signature validation, all 18 cooked checks, captures and benchmarks. The package command itself did **not** finish successfully. Rebuildable compiler/cook/shader caches were reclaimed without changing the guards. Future rebuilds regenerate caches and need additional headroom. Current staged build is local Development only; Shipping is unvalidated (runtime mesh construction currently uses a `check` expression with a side effect that must be moved to unconditional execution before Shipping support).

## Launch and next action

```sh
cd /Users/haydn/Documents/BossLab
BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-play
```

Enter starts; WASD/mouse move/orbit; Tab targets; LMB/J cuts; Space rolls; Shift sprints; E heals; Esc/P opens the cursor-enabled Resume/Quit menu; Q quits while paused. The owner's earlier physical control verification remains valid evidence from that revision; this outfit pass adds automated tests/captures, not a new human play session.

Next: review the silhouette/materials in the final clips, then refine clothing shape/deformation and surface detail within the current budget; preserve the single-instance benchmark baseline. Improve the rigid mantle/cape, finger fit, UVs/weathering and garment skinning after that review. The boss remains the existing placeholder. Combat is still a fixed rehearsal; no AI/RL/models or training were added.

Checkpoint: `artifacts/unreal/checkpoint-2026-11-06-ashbound.tar.gz` (source/config/scripts/docs/model only; no engine or cooked assets). Final hashes, test counts, storage and evidence paths: `artifacts/unreal/ashbound-2026-11-06/final-audit.json`. The 10 GB project allowance and 24 GiB free-space guard are unchanged.
