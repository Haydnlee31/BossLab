# V13 actual Unreal transfer test — 2026-11-08

Actual graphical transfer and performance comparison completed. Earlier blocked/failed attempts are retained below.

Owner explicitly authorized testing the Blender design in-game. This is an opt-in runtime attachment experiment; the original packaged game is preserved. No boss AI or combat definitions were changed.

## Actual transfer

Frozen V13 scene SHA256 `2457b527d43ceea7bf94f16d3fb15fcda230a302253956c36d9c2cbd4ed00839`; current corrected JSON SHA256 `53d5415d57f2a69df25c03dbfa35df98ffea0a957bfc5273ee78d4269c7dd7fa`. Initial palette-error JSON SHA256 `f7e7067e4c5e5ade6173dbbd2fe9d4d98fa5554bdf53e679d77196d33b2504de` retained. Export: `unreal/BossLabWarden/Content/BossLab/V13/v13-runtime.json`. Actual evaluated geometry, reduced fur/detail, 18 groups / 60,240 exported split vertices / 104,012 exported triangles. Unreal skips 656 zero-area faces, producing 103,356 rendered triangles in 48 sections.

`WardenV13.cpp` builds real static render meshes and attaches them to existing animated Epic bones. Limb axes are aligned to bone-to-child directions, length adjusted independently of cross-section. Hands/feet rotate without longitudinal scale. Sword geometry retains the existing hilt coordinate frame and approximately 148cm tip reach; decorative relief reaches 148.115906cm (1.159mm past the engine endpoint). Combat collision and timing remain engine-owned and unchanged.

Eight simple color/roughness/metallic materials approximate the studio palette. Blender textures and shader graphs are **not** transferred. Gloves, armor and cloth are rigid attachments, not production skinning. Cape uses the existing cosmetic sway/roll tuck, not cloth simulation. The hidden mannequin still supplies animation. Conservative attachment bounding boxes support the existing flat-floor presentation correction.

## Launch and fallback

Verified graphical trial route (same editor `-game` build used by successful captures): `BOSSLAB_OUTFIT=v13 BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play` (editor `-game`, local raw JSON dependency). Default `./scripts/bosslab-unreal play` retains original costume. The existing `package-play` app has not been replaced by this trial. Do not describe this as a portable cooked delivery.

`BOSSLAB_V13_DATA` optionally selects an alternate local export. Missing or invalid JSON/indices leaves the original costume usable. No collisions/nav geometry are added to the decorative meshes. Runtime mesh build is unconditional for the new loader, not hidden inside assertions; Shipping has not been validated.

## Test evidence so far

- Baseline native BossLab suite: 21/21 passed. Trial tests use a separate `V13Trial` namespace, outside the default BossLab filter.
- Dedicated actual transfer/motion: 1/1 passed, 18.68s. All imported vertices sampled at seven phases in each of eight roll directions; minimum world height 0.490cm. Sampled death pose minimum 1.367cm; finite coordinates. Reset did not duplicate parts, boss/player switching retained correct visibility. Underlying engine hand/hilt constraint error 0cm; this does **not** prove imported glove grip fit.
- Initial dedicated run failed a 0.2mm tip tolerance: source decorative relief extends 1.159mm. Retained failure; test now explicitly allows 2mm visual relief, with combat reach unchanged.
- Earlier build hit the storage reserve; after authorized cleanup, compiler errors were fixed and build passed. All failed receipts retained.

Evidence directory: `artifacts/unreal/v13-trial-2026-11-08/`. Export audit: `artifacts/art/v13-unreal-test-2026-11-08/export-audit.json`.

- Missing-file fallback: 1/1 passed, 12.39s. Malformed negative triangle index fallback: 1/1 passed, 12.48s. Both spawned the actual original Ashbound costume, checked visibility/triangle count and absence of partial trial components. Deliberate loader warnings were expected by those dedicated tests.
- **Earlier graphical attempt blocked (subsequently resolved below):** first editor `-game` capture stopped at the 24GiB reserve during shader initialization, before gameplay frames. Receipt records 25,289,994,240 bytes free at stop versus 25,769,803,776 reserve; exit -9 after bounded graceful termination timeout, 76.43s. The approximately 127MB increase under `unreal/` does not explain all free-space loss. At that point no actual screenshot, motion clip or V13 FPS result existed. Native geometry tests are not visual-quality evidence. Original packaged app was untouched.

## Lower-memory retry preparation

Installed engine source `Runtime/Engine/Private/ShaderCompiler/ShaderCompiler.cpp:1224` reads `DevOptions.Shaders` thread reservations before worker creation. This host has eight virtual cores; reserving seven yields one local worker. Launcher graphical editor modes now pass launch-only Engine INI overrides for normal/during-game reservations (7 each) and threshold999 to avoid the percentage branch. `BOSSLAB_SHADER_WORKERS=default` restores normal engine behavior. This is not a global configuration change. Actual retry log confirmed `Using 1 local workers for shader compilation`; process inspection also found exactly one shader worker.

Rebuildable completed editor compile file inventory: `rebuildable-editor-cache-candidates.json`, 20 `.gch`/`.o` files, 888,519,212 bytes. Inventory is not a deletion claim; root owns any cleanup. The linked editor module and old packaged game must remain intact. No heavy retry until the guard passes.

## Actual graphical transfer observed

After root reclaimed the completed editor intermediates and the launcher limited shader workers to one, the outfit capture completed (132.54s, exit0). All180 fixed30Hz frames were encoded and decoded successfully; nine selected PNGs plus the full frame/hash manifest were retained. `v13-outfit.mp4` is the **initial palette-error capture**, not final art. Viewed front/side/back frames show actual imported armor, body, gloves, sword and cape in the arena. Hands are approximately aligned around the hilt but rigid fingers and overlap remain visible; no production grip acceptance is implied.

Inspection caught a real export error: inherited cape fabric material name contained “gold,” and the palette classifier selected bronze before checking cape. The artist changed2370 cape triangle material indices to cloth; all3138 cape faces now use oxblood cloth. Geometry, normals, UVs and bindings are unchanged. Corrected JSON SHA256 `53d5415d57f2a69df25c03dbfa35df98ffea0a957bfc5273ee78d4269c7dd7fa`; original JSON and audit retained. This illustrates why native passing tests did not establish material correctness.

Encoder initially failed inside the sandbox (AVFoundation encoder unavailable), then the first escalated retry encountered the existing zero-byte failed output. That output was preserved separately; a fresh output encoded and decoded180/180 successfully. No failed encoder result is represented as a playable clip.

Corrected motion capture completed in25.09s, exit0; `v13-motion.mp4` encoded and decoded180/180 actual frames. Inspected ready, attack contact, roll protected/vulnerable and attack recovery frames. Cape is correctly oxblood cloth. Body/armor/sword follow the existing animation, but rigid cape/leg intersections and approximate open fingers remain. This is a functional transfer experiment, not production costume acceptance.

## Actual performance comparison

Both runs use the same compiled editor-game module, 1280×720 window, performance preset (75% internal screen percentage), fixed rehearsal and one game instance at a time. First180 active frames are excluded. These are real wall-clock runs, unlike fixed-step capture.

| Costume | Samples | Mean FPS | Mean ms | p95 ms | >33.3ms | >50ms | Maximum ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original Ashbound |3213|58.55|17.0784|17.0415|11|5|343.4862|
| V13 corrected palette |3244|59.03|16.9400|16.8072|7|7|263.3739|

Sequential short shared-machine runs show no obvious large V13 regression; they do not establish that the costume improves performance or that60FPS is locked. Both preserve substantial outlier stalls. These editor results are independent of historical packaged-game benchmarks. Reports, raw frame CSVs and logs are retained with `original-` and `v13-` prefixes.

## Final review delivery

- Primary actual outfit turntable: `artifacts/unreal/v13-trial-2026-11-08/v13-outfit-final.mp4` (corrected palette,180 encoded/decoded frames,24.46s guarded capture run).
- Actual attack/roll clip: `artifacts/unreal/v13-trial-2026-11-08/v13-motion.mp4` (180 encoded/decoded frames).
- Final front/back PNGs: `outfit-final-frames/frame-000020.png` and `frame-000110.png`; nine turntable keyframes retained. Motion has13 selected keyframes, including visible shin/cape intersection at110.
- Initial gold-cape clip remains failure evidence; it is not the primary review target. Full frame hash manifests and raw-cleanup receipts preserve what was generated and reclaimed after successful video decoding.
- `BOSSLAB_OUTFIT=v13` with any `package*` command now fails early with an explanatory message. Lightweight check returned expected exit1 and started no game. The unchanged staged binary cannot silently masquerade as the V13 trial.

Current controls remain WASD movement, mouse camera, Shift sprint, Tab target, Space roll, J/left-click greatsword, E heal, Esc/P menu; Q quits from the menu. No new control or combat authority was introduced.

This is ready for **opt-in technical/human inspection**, not artistic or production acceptance. No production skinning, cape simulation, texture bake, packaged integration, Shipping validation or model/AI capability was added. Next substantive work is proper hand posing/skinning, cloth deformation and local body collision, and actual material/texture transfer before replacing the default costume. Maintain the original fallback.

Final storage snapshot:26,374,811,648 bytes free (605,007,872 above24GiB reserve);2,735,607,808 allocated bytes under `unreal/`, below10GB. All owned capture/benchmark/encoder processes exited. No packaged executable was modified.
