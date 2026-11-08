# ART-07/08 — focal surface and authored material study

Date: 2026-11-07. Animation-techart owns separate v3 source, guarded launcher, scene and evidence. V2 and the playable game remain unchanged. Approved concept is direction only; no reference-quality acceptance, rig, skinning, cloth simulation, gameplay integration or boss AI is claimed.

## Actual shape work

Replaced straight helmet cross-section interpolation with curved fields, retaining a median keel and plate boundaries. Raised the eye line 8 mm within similar overall bounds. Corrected longitudinal interpolation for unequal section heights after actual clay side views exposed stepped crown curvature. Fitted the visor edge into the side overlap after the first pass exposed a wavering sliver. Preserved the 5 mm nominal front opening before shell thickness, tapered at the temples.

Gloves retain connected closed leather geometry and unequal fingers. Reduced palm thickness, removed the broad transverse padded crease, authored a shallow central hollow and local thenar compression, and staggered/broadened root saddles. First narrow root depressions read as little notches in clay; their width was increased and depth reduced. Static anatomy remains simplified; these corrections are not human anatomy or deformation acceptance.

## Local material sample

Original 1024×1024 color, roughness and relief maps plus RGB placement masks are authored in source and packed into the scene. No downloaded texture or concept-image projection. Helmet uses a cylindrical plate field; glove uses mirrored local X/Z projection for a focal sample. The glove projection overlaps palm/back and compresses side edges; it is explicitly not a production unwrap or atlas.

Steel placement channels: red interrupted exposed-rim rub, green recess accumulation, blue selected directional scratches. Leather placement: red thumb/index/pad contact, green crease compression, blue side-seam stitch relief. The seam is represented by a height/color mask, not sewn geometry. The first cuff-seam placement was hidden under the metal cuff and scratches fell on rear-facing UV sectors; preserved rather than presented as successful visible wear. The first glove shader also required explicit authored-UV wiring instead of inherited render-active coordinates.

## Evidence and limits

First form probes and failed sample views/source/scenes are preserved under numbered iteration directories. Clay images are actual geometry with a neutral material override; generated concept remains separately labeled NOT BUILT. Current low-cost crops use fixed lights and cameras. Final audit will record map packing, UV coverage scope, topology, dimensions, hashes and process receipts.

Remaining quality gaps include helmet silhouette refinement, simplified palm/knuckle anatomy, broader costume/mantle/material work outside this focal scope, and production UV/retopology/rig/cloth/runtime gates. No gameplay tests or FPS claims follow from this DCC-only pass.

## Final verified delivery

Final scene: `unreal/art-studio/revision-v3-2026-11-07/last-vigil-v3.blend`. Source: `unreal/art-studio/source/last_vigil_v3.py`. Launch: `./scripts/bosslab-art-v3 draft`; diagnostics/reload: `./scripts/bosslab-art-v3 audit`. Both use the unchanged 10 GB Unreal ceiling, 24 GiB free reserve and 20-minute foreground guard. CPU default. No Blender process remains after handoff.

Final geometry has 445 renderable objects, 512,906 evaluated vertices and 958,672 evaluated triangles, finite positions. Each glove is one connected closed base of 20,854 vertices. There are ten packed images: two inherited original maps plus eight new 1024×1024 sample maps. A separate saved-scene reload confirms all eight new maps remain packed and the actual shader UVMap nodes name `Authored sample UV`.

The inherited `UVMap` was the cause of the first misleading glove diagnostic: implicit image coordinates and the first audit's active-layer selection used that old layer. Explicit shader UVMap nodes and named-layer audit corrected both. Actual mask-on-mesh diagnostics now show thumb/pad contact, short palm compression and the side stitch strip, plus front helmet scratches and exposed rim treatment. The original failed mapping evidence is preserved. A 2.53-second mask-probe failure exposed that unused packed diagnostic masks were purged on reload; fake-user retention corrected this, then the saved scene was successfully reloaded and audited.

UV coverage is a 256-grid raster union, not an overlap certificate. Glove sample coverage is about 50.99%; its planar projection has 997 left / 993 right degenerate UV triangles at compressed side surfaces and intentional front/back overlap. This is a limited focal material study, **not a production unwrap, atlas or bake-ready asset**. Actual UV wire sheets show the authored layer; the prior wrong-layer sheet is preserved.

Final evidence contains eleven 720×920 renders: `head`, `headside`, `palm`, `hand`, `hero`, `clay_head`, `clay_headside`, `clay_palm`, `clay_hand`, `mask_head`, `mask_palm`; plus two 512×512 UV wire sheets and eight texture maps. Emission-color mask diagnostics prove placement only, not finished shading. Final render completed in 100.46 seconds, exit 0; saved-scene reload audit completed in 12.38 seconds, exit 0. The guard reported 2,901,811,200 bytes under Unreal and 28,368,830,464 free bytes after reload. All prior failures/iterations remain dated evidence.

Static cape vertex-ray check remains separate: 25,822 hit samples, minimum 31.1518 mm clearance and zero negative samples. Excludes attachment region above 1.515 m, mantle/curves and arbitrary triangle intersections. No new motion or all-pose safety is inferred.

Independent art review finds smoother fields/fitted side overlap and readable localized steel, but overall realism remains **needs work**. The glove's distal palm ledge and padded anatomy remain, and the final leather improvement is too subtle for an artistic pass. Material diagnostics cannot close those geometry or quality gaps. Preserve these limits and obtain further art review before production UV/rig/deformation work or any AI milestone.
