# V7 helmet and shoulder construction/finish sample

Status: final static partial increment frozen; forged-surface and overall artistic quality remain unaccepted. Separate original static Blender revision; V6 and gameplay remain preserved. No rig, cloth simulation, runtime integration, gameplay/FPS test, AI or model work.

## Actual construction

Upper-front crown is set back, slightly narrowed and shortened; lower cheek/jaw narrows through a shared shell deformation. A small folded brow plate follows the existing skull rim. Six rounded rectangular cutters produce actual visor breathing openings with a separate recessed dark backing. A center-ray test checks whether each opening reaches that backing; its result is recorded rather than inferred from a dark mark. The broad cheek transition has an explicit normal break.

Shoulder fields retain angular silhouette and gain shallow asymmetric curvature and a turned lower sheet return. The initial separate rounded rail produced a doubled bright stripe; it was removed in favor of the returned sheet's own edge. Materials now explicitly address the new helmet/shoulder/neck objects rather than accidentally inheriting imported global steel.

## Scoped authored material sample

Separate crown, visor and shoulder maps place interrupted physical-rim handling, overlap/recess/hinge oxide, lower-cheek worked zones and sparse directional finishing. Stable neutral steel is modified only in those zones, with corresponding roughness and shallow normal-height relief. Three families each have original1024-square color, roughness, height and diagnostic placement maps. Small edge/gorget pieces use a quiet unpatterned steel response. These are programmatically authored local samples, not a production baked/hand-painted atlas or evidence of reference-level craftsmanship.

First sample's equal oval dents and central polished stripe were rejected after actual720 and1400 inspection. The cylindrical UV seam had incorrectly been treated as a physical rim. The corrected sample removes that seam wear, separates crown/visor patterns, places a few unequal overlapping elongated patches near real perimeter areas, and leaves the median/gorget quiet. Rejected first scene, source and images are preserved under `iteration-01-rejected-stamps`; quieter intermediate views remain under `iteration-02-quiet-worked-zones`.

One render completed its images/save but failed the new audit due to a positional `distance` argument to Blender's ray API. The failure receipt and log are preserved; the keyword argument was corrected before the next audit. No failed command is labeled a passing run.

## Limits

Reference realism remains unmet: overall helmet/side shell is still simplified, shoulder fields are pale and smooth under current lights, fine finish is restrained, mantle has broad backing and repeated arcing fibers, hands/cloth/sword remain below the intended detail. Glove UV work remains the prior isolated incomplete/unintegrated study. No changed static cloth is validated by old motion caches. Cylindrical/planar sample UVs are not production topology/UV certification; cut-edge and closure projection degeneracy must be reported in the reload audit.

Final evidence count, source/scene identities, sampled clearance and image hashes are recorded in `artifacts/art/last-vigil-v7/techart-delivery-audit.json`. Existing10GB unreal/24GiB free/20-minute foreground guard remains unchanged, CPU only, no downloads or persistent jobs.

## Bounded stronger finish trial

The initial localized patina was still too subtle in matched1400 renders. A further bounded trial widens connected brow/hinge/returned-recess zones and the lower-cheek working region, with coordinated stronger color darkening and roughness contrast while leaving most fields quiet. Actual saved-scene shader readback confirms intended color/roughness image links and explicit UV names; map presence alone is not visual acceptance. Six out of six visor-center rays reach the recessed backing, establishing actual openings at those tested points. High-resolution trial review remains the authority on finish quality.

Saved-scene audit also found that the three diagnostic-only placement images lacked persistent users and were omitted on reload, although all nine actual shader maps survived and were correctly linked. Their retention was corrected before the final build; the prior nine-image readback is preserved as `diagnostic-maps-not-retained-before-fix.json`. This was a diagnostic-persistence defect, not the cause of the visually weak finish. The final reload retained all twelve V7 maps and reproduced both mask views (probe exit 0, 24.88 seconds; final audit exit 0, 8.28 seconds). The visor parameterization contains33 zero-area projected triangles around cut/closure geometry; no clean production unwrap is claimed.

Loaded-image sample evidence (not rendered-pixel or artistic-quality proof): visor working-zone UV(0.085,0.22) has linear RGB(0.05098,0.04706,0.04706), roughness0.59608; quiet UV(0.04,0.55) has RGB(0.07059,0.07451,0.07843), roughness0.43137. This confirms the mapped contrast exists. Independent review still finds the overall response too uniformly polished. The increment is retained for useful form/construction progress; it does not close the requested forged-craftsmanship gate.

Final delivery:12 actual views (ten720×920/16-sample and two1400×1800/48-sample), all from final saved geometry. Reload: 354 renderable objects, 1064026 evaluated vertices, 1933368 triangles; finite. Exact hashes and resource results are in the delivery audit.
