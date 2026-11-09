# Court of the Last Witness — technical art draft

2026-11-09. Standalone original Blender architecture concept; not an Unreal level, collision import, performance result, or approved final environment. Current Revamp assets and gameplay were not edited.

## Delivered construction

A sunken circular judgment court, sixteen funerary arcade bays with modeled stone voussoirs, burial recesses, clustered perimeter supports, bronze vault ribs, sealed ivory oculus, and an elevated empty judge's apse. Three small passive blue reliquary chambers are architectural fixtures, not modeled skull characters or combat effects. The final boundary piers are planar memorial facings contained within the inherited pillar envelope. The throne is offset tangentially to Y+2.2m to reveal its seat beside the retained central pier; its backrest is still partly occluded from the unchanged entrance camera.

Coordinates are metres, entry −X and apse +X. Floor radius14m; tactical guide12m and proposed clear geometry radius12.8m are distinct. The source reproduces32 wall positions at radius13.6m, dimensions.55 radial×2.8 tangent×2.6m, and8 original pillar envelopes radius.55m/height5.4m. No collision was edited. Spawn markers retain(−4.5,0)/(3,0), separation7.5m. Rulers1.8m/2.43m are scale placeholders, not actual character bounds.

New support centres have radius17.0077m (local radial16.8/tangent±2.65); full plinth radius.62m yields inner bound16.3877m. The oculus is deliberately8.1m diameter at16.17m high, larger than the early3.5m direction sketch. Inlays are flat meshes1mm above the slab solely to avoid rendering interference, not raised gameplay geometry. Existing floor rings3.6/7.8/12.1m remain readable.

## Attempts and visual limits

Candidate01 was intentionally stopped after two complete frames: overlit hall and concealed throne. Candidate02 completed five frames, adding darker hierarchy, larger apse and actual stone arch sections, but the unchanged axial pillar hid the throne. Candidate03 is the final targeted correction: offset throne and contained memorial-pier cladding. Five final views are selected; twelve actual stills survive across all attempts. No fourth design iteration occurred.

Final images: `hero-entry`, `gameplay-height`, `side-architecture`, `near-boundary-inward` at1280×800; `annotated-plan` at1280×1280. All are CPU16-sample denoised renders. Gameplay-height uses horizontal75° FOV; other views are design cameras, not engine camera traces. The upward side view demonstrates the sealed vault, while the plan hides the roof and adds clearly labeled guides. Near-boundary views show the actual continuous barrier; they do not prove unobstructed camera boom travel.

The architecture is a coherent concept draft, with repetitive bays, simple burial relief and clean materials rather than final bespoke environment art. Throne occlusion remains partial, blue-fixture contrast is subdued, and ruler proxies cannot establish moving skull/attack readability. Fourteen offline lights, many separate objects and no LOD/instancing preparation mean no runtime-cost claim.

## Saved-scene checks

Final audit reloads the saved scene and evaluates133,314 visible triangles across771 total scene objects. Every visible nonfloor mesh/curve triangle is clipped toZ0–3m and tested for projected radial proximity; nearest is a memorial-pier base at13.0578459m, outside proposedR12.8m. Hidden annotations/rulers and floor/inlays are excluded. This is a static geometry test, not Unreal collision, camera or dynamic clearance certification.

Slab flatness is separately sampled by81 vertical rays over centre and five rings throughR12.8: Z0 to5.96e−8m. The inlay-only vertex range is.001m; slab perimeter vertices alone would not validate its interior, hence the separate rays. Detailed bounds and scope are in `candidate-03/saved-scene-audit.json`.

The source originally saves before assigning its render camera. The audit restores the opening hero camera and resaves; geometry digest before/after is identical (`0da32cfc2af911b8df8683bc613893304d32a42ec5fe883a6b181cc22db0665b`). The initial readback scene hash therefore differs from the final camera-restored scene; neither implies geometry changes.

Final source SHA256: `010e38ffbb3c061027d2af1f2dbc90d7f8ada7cf0d60ed5ec34c27204b56fc34`.
Final scene SHA256: `8aebd21390fd89399f0a86624f2dce7d663c2f3161fa85d1f3780e2d86b98b54`.

## Reproduce and retain

Run sequentially from the repository root:

```sh
python3 scripts/bosslab-arena-design-01 3
python3 scripts/bosslab-arena-design-01-audit audit
```

Both launchers enforce24GiB free/10GB under Unreal, CPU2threads and a20-minute deadline. Final render exited0 in291.92s; audit exited0 in2.55s. Audit finish free29,944,037,376bytes, Unreal3,738,787,840bytes. All owned processes finished. No downloaded assets, paid calls, AI, game changes or public deployment occurred.

Editable final scene: `unreal/art-studio/arena-design-01/court-last-witness-03.blend`; previous02 retained. Candidate01 scene was removed under latest-two retention with its exact hash recorded; its source snapshot, two images, logs and intentional-stop receipt remain. Gallery: `artifacts/art/arena-design-01/index.html`. Canonical files and hashes: `delivery-manifest.json` beside it. Parent owns publication/commit and independent QA owns preservation checks.
