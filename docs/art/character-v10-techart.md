# Last Vigil V10 — static construction and finish study

V10 is a separate Blender authoring increment from the frozen V9-armor scene. It retains the lean body and overlapping rigid shoulders, replaces the mantle support and front garment, and changes selected metal materials. It is **not reference-quality finished art**, a rig, an animation, a runtime asset, or an AI feature. The rejected V9 simulated-cloth branch was not loaded.

Review actual images in [the local gallery](../../artifacts/art/last-vigil-v10/index.html) and the parent-owned [matched comparison](../../artifacts/art/last-vigil-v10/comparison.html). The approved generated concept remains a design target, not built evidence.

## What is actually built

- An inward, closed padded collar replaces the broad thin yoke and all-over carpet groom. The first two stepped-channel attempts were rejected. The retained support is one convex stuffed volume with shallow compressed seams and asymmetric front ends. Short rim curves replace the old 22,800-strand full-surface groom. A curved leather retention strap has its short end sections fitted to the evaluated collar. The fringe still lacks natural fur clump mass.
- Selected shoulders, visor, crown, forearms, gauntlet cuffs and fauld use explicit construction-region masks. Dark protected/oxide regions affect color, roughness **and metallic response**; worked metal and handled areas retain subdued reflections. Masked intermediate-scale relief was reduced and elongated after the first visible version read as orange peel. The existing torso/limbs outside this scope remain unchanged. This is authored/procedural surface sampling, not scanned PBR, hand-painted production texturing or a clean final atlas.
- Two new static split-surcoat meshes use support landmarks at belt tuck, plate bottom, thigh, release and unequal curved hems. Additional close rows tuck the cloth behind the belt. Broad unequal diagonal control paths replace the forward-projecting boards; binding curves follow the new sheet. This is **explicitly authored static drape**, not physics. Rigid tassets and mail geometry remain unchanged.

## What failed, and what was corrected

All run source snapshots/logs remain in `artifacts/art/last-vigil-v10`; numbered iteration folders retain superseded images and relevant audits. Stepped collar shelves, exposed collar/cap overlap, rigid floating retention strap, sparse straight fringe, weak material contrast, coarse orange-peel relief, weak front folds and cloth-over-belt overlap were observed rather than accepted silently.

A mask diagnostic initially failed to reload because unused packed images lacked fake-user retention. The final source retains them, and final saved-scene audits inspect packed data. The linked color/property maps had persisted: the earlier chrome-like appearance was not caused by missing shader links. A separately labeled constant-oxide render and pixel/link readback established the fixed-light material response. Those diagnostics are not final beauty views.

The first scoped garment audit found six samples per side below the unchanged 3 mm target (minimum about 1.6 mm). Moving only the hidden upper cloth back 3 mm corrected that result. A later audit found one strap end 22–26 mm from the collar; only the short attachment sections were fitted to the actual evaluated collar, with a smooth transition. Both pre-correction audits are retained.

## Verification scope

`v10-reload-audit.json` compares retained visible mesh/curve geometry and transforms against the frozen V9-armor input, records exact camera/root/sword equality, and reads the final packed maps and BSDF links. Geometry hashes deliberately omit materials/UV because those are explicitly changed. Newly mapped fauld/forearm/cuff regions use cylindrical sample coordinates; crown/visor/shoulders retain inherited sample UVs and their prior limitations. No production unwrap claim follows.

Cloth tests are sampled vertex rays against body/mail front envelopes and rigid-tasset back envelopes. They include evaluated cloth thickness, but are not exhaustive triangle intersection, seam, motion, cloth-simulation or deformation certificates. Collar measurements compare evaluated support-only bounds, excluding groom. Retention checks cover four endpoint control vertices only. Cape audit retains its earlier explicit outer-mantle/top-attachment exclusions; the cape itself is unchanged.

## Reproduce and inspect

From the project root:

```sh
./scripts/bosslab-art-v10 draft hero front side back head shoulder garment clay_shoulder clay_side mask_head mask_shoulder
./scripts/bosslab-art-v10 render shoulder-detail garment-detail
./scripts/bosslab-art-v10 audit
```

The launcher runs foreground CPU Blender with the unchanged 10 GB Unreal-tree / 24 GiB free-space / 20-minute guards. No additional download, paid call or persistent helper was added. The saved scene is `unreal/art-studio/revision-v10-2026-11-07/last-vigil-v10.blend`; source is `unreal/art-studio/source/last_vigil_v10.py`. Source utilities inherit the frozen V9-armor→V8→V7→original studio Python definitions; actual starting geometry is the frozen V9-armor scene. New PNG maps are in the V10 scene's `textures/` directory and packed into the scene.

## Remaining limits

The collar is a simple padded wrap with fringe, not the reference's rich fur mantle. Garment folds are a useful static shape change but still read heavy/smooth. The metal hierarchy is more visible yet remains simplified; oxide boundaries and repetitive construction-region placement require artist-level refinement. Cape, anatomy and much of the costume remain below reference. No combat motion, runtime FPS, rigging, cloth dynamics, game integration or boss AI was implemented or validated by these renders. The existing game remains a separate preserved checkpoint.

Final values and hashes are recorded in the machine-readable delivery audit, rather than inferred from a passing render process.

## Final inspected measurements

The saved-scene audit records 327 retained visible geometry objects unchanged, no unexpected missing objects, and equality of the six protected camera views, root scale and sword geometry digest. It records 339 renderable objects, 430,752 evaluated vertices and 813,036 triangles with finite coordinates. These are offline studio counts, not a runtime budget/performance result.

The evaluated support-only collar width changes from 0.546249 m to 0.340955 m; the existing shoulder plates are unchanged. Four sampled retention endpoint vertices are approximately 1.500 mm from the actual collar surface after fitting. This does not validate all strap contact or animated attachment.

Static garment body/mail front-envelope samples total 15,829 with a minimum clearance of 3.877 mm. Tasset back-envelope samples total 3,294 with a minimum of 5.130 mm. Neither set has a sample below the declared 3 mm threshold. Initial failed near-clearance and detached strap metrics are preserved in iteration folders. The unchanged cape has its own scoped audit; this is not a new cape simulation.

Twelve new 1,024×1,024 PNG maps are packed alongside inherited maps (37 packed authored images total). The new PNGs are 8-bit samples, verified from their headers. Visible bands/region boundaries remain a separate quality defect; this pass did not isolate whether their cause is quantization, mask construction, or both. The final saved-scene audit records actual image-channel ranges and shader connections. No smooth-gradient or production-precision claim is made.

The delivery set is **nine 720×920 material/clay views**, **two 1,400×1,800 detail views**, and **two 720×920 placement-mask diagnostics**. The masks are not beauty renders. Earlier bare collar and constant-oxide diagnostic images are explicitly excluded from this final set. Exact hashes, final run receipts and storage are in `artifacts/art/last-vigil-v10/techart-delivery-audit.json`.

The new cylindrical sample coordinates are finite but **not a clean unwrap**: 740 of 3,044 raw triangles have UV area below 1e-12, concentrated on the loft caps of fauld/forearm/cuff meshes. This sample intentionally does not establish island packing, overlap freedom or production UV readiness. The saved audit lists counts per object; inherited helmet/shoulder UV limitations also remain.
