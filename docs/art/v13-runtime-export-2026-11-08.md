# V13 actual-mesh runtime test export

Owner explicitly authorized trying the current Blender character in the game despite its open art/production gates. This is a reversible cosmetic test, not production rigging or art acceptance. The frozen context16 scene remains unchanged (`2457b527d43ceea7bf94f16d3fb15fcda230a302253956c36d9c2cbd4ed00839`). No V9 failed cloth solve or V11 projection is used.

## Actual export

- Exporter: `unreal/art-studio/integration-test-2026-11-08/export_runtime.py`.
- Guarded command: `./scripts/bosslab-v13-export`.
- Runtime file: `unreal/BossLabWarden/Content/BossLab/V13/v13-runtime.json`.
- Audit/contract checks: `artifacts/art/v13-unreal-test-2026-11-08/export-audit.json` and `export-contract-check.json`.
-18 rigid groups (17 bone targets; cape separate from chest),104,012 derived triangles,60,240 split vertices,~6.7MB JSON.439 actual scene meshes/curves contribute.592,008 evaluated triangles before decimation **after** fur sampling; not the full studio triangle count.
- Each original fur curve keeps every18th guide:5,400→300 original strands before curve conversion/decimation. No replacement fur card or pretend runtime groom. Small details and dense mail/gloves are decimated; per-object actual counts are in the audit.
- First148,487-triangle export failed the120k limit and wrote no runtime file; failed log/receipt retained. Lower derived targets produced104,012 triangles. Final guarded export exit0 in16.50s; afterfree27,262,300,160bytes, Unreal2,671,321,088bytes after parent’s separately authorized archive cleanup.

## Binding contract

Canonical authored game centimeters are `(-100*BlenderY,100*BlenderX,100*BlenderZ)`. Group vertices retain their actual derived geometry. `source_origin` is the declared authored anatomical joint; `source_axis` is actual joint→child displacement in cm when `target_child` exists. Upper/lower arms and thighs/calves permit longitudinal length fit; hands orient toward middle_01, feet toward ball, with `scale_length:false`. Head/torso/pelvis use translation-only origins. This is approximate rigid attachment, not weighted skinning or validated joint clearance. Cape is a separate `V13_cape` group attached to spine_05, allowing existing cosmetic tuck/sway without folding the chest; skirt panels with respective thighs; neither is simulated.

The Oathwake studio blade baseZ1.37m/tipZ0.10m maps to engine cosmetic bladeZ14/148cm with uniform scale1.0551181102. Z reflection reverses export winding to keep outward normals. Grip origin is implied by that mapping; the existing engine owns collision/timing. The exporter does not change gameplay blade definitions.

## Material and quality limits

Eight simplified materials: steel, aged bronze, oxblood cloth, oiled leather, charcoal wool, fur, mail and polished edge. Existing UVs travel with geometry but are not repaired. Blender node graphs, generated steel texture, gold cape graphic, local masks and calibrated PBR are **not** transferred by this initial palette. This loss must be visible in runtime reporting; it is not an equal-fidelity material import. Vertex normals are smooth per-vertex normals from evaluated geometry, not a production tangent bake.

JSON checks passed finite values, array sizes, valid triangle/material indices, source-axis contract and104,012-triangle cap. These are file integrity results only. Actual Unreal loader, rest/attack/roll pose, clipping and FPS tests belong to the builder/QA handoff and are not claimed here.

Final runtime JSON SHA-256: `f7e7067e4c5e5ade6173dbbd2fe9d4d98fa5554bdf53e679d77196d33b2504de`. Re-run the lightweight contract test with `python3 unreal/art-studio/integration-test-2026-11-08/check_export.py`. Heavy DCC slot released to Unreal builder after export; do not run exporter concurrently with a build/game test.

## Actual runtime palette correction

The first actual game capture exposed a metallic-gold cape. This was an exporter classification defect: the main wool shader name mentions its gold graphic, and the generic gold-name rule ran before the fabric rule. Main cape2,274 triangles + doubled hem96 triangles were wrongly bronze. The derived JSON alone was corrected:2,370 material slots changed; all3,138 cape triangles now use oxblood cloth. No geometry, UV, normals, attachment, Blender scene or C++ change was needed. Exporter priority is corrected for repeatability. Original6.7MB JSON and audit remain as failed evidence; exact correction is in `cape-palette-fix.json`.

Current runtime JSON SHA-256 supersedes the earlier handoff: `53d5415d57f2a69df25c03dbfa35df98ffea0a957bfc5273ee78d4269c7dd7fa`. Contract checks pass again; corrected actual runtime capture remains builder's verification responsibility.

Sword endpoint qualification:14→148cm is the nominal control-blade mapping. Evaluated forged blade reaches148.059906cm, and actual cutting-bevel modifier geometry reaches148.115906cm. The builder was advised to test actual exported/rendered bounds with a disclosed0.2cm cosmetic tolerance while preserving engine combat reach148cm. No collision/timing change is authorized or implied by this evaluated surface overshoot.
