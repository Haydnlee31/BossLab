# Bellbreaker's Bellfounder remodel

The owner requested a complete remodel with finer surface detail and better shoulder, elbow and hand behaviour. The new character follows the original bellfounder turnaround: asymmetric iron shoulder, aubergine quilted sleeve, short bracers, smoke goggles and a split oxblood apron. Its shape master is the earlier 885,818-triangle Hugging Face Hunyuan four-view sculpt. All generative work is offline asset authoring.

## Source resolution

Four individual portrait views were newly authored and registered to the established four-camera UV layout. The old projection atlas was 1088 × 1088 with 481–484 pixels of character height in each view. The new source figures occupy 1419–1511 vertical pixels before atlas assembly. Base colour, shallow surface normal and packed material masks each use 4096 × 4096 texels. The 4K figure applies to each atlas; all four directions share it.

The paired texture comparison in `artifacts/art/bellfounder-hires-20261120/registered-detail-comparison.jpg` uses the same UV rectangles at the same scale. The face, shoulder, harness and elbow can be compared independently. These crops are texture samples. For the capture of the character in motion, see the Unreal verification below.

The new materials preserve some lighting from their painted references. The normal map represents shallow estimated relief. Roughness and metal regions are authored approximations. The higher-resolution sources cannot by themselves correct a joint whose orientation changes too abruptly.

## The fitted character

The shipped Bellfounder mesh has 180,000 triangles, up from 92,450 in ForgeShoulder. The editable Blender scene and portable GLB share the fitted rig and maps. The GLB has 88 deform joints. Unreal's reference skeleton has 89 entries including its root. A fresh GLB readback verified all three embedded maps and normalized weights across both material sections. The rigid armour section uses one influence per exported vertex and the flexible body section uses up to four.

A first hand-weight pass incorrectly left some old digit weights beneath a full-strength palm weight. It was rejected after the overhead pose produced long spikes. The corrected model retains the remodeled hands and independently weighted fingers. Another early export split almost every triangle corner, producing 539,996 Unreal render vertices. Smoothing the curved surfaces while retaining 687 deliberate sharp edges brought that to 108,021 vertices at the same triangle count. The final cheek and upper-arm colours reconcile the four cameras in areas where an oblique view exposed a hard seam.

The old model's Unreal source colour and material atlases were 2048-square. A texture's resident streaming mip in a headless process can be much smaller. The comparison here uses source dimensions. Both remodel materials were independently reopened in Unreal to verify the shared 4K textures, channel assignments and use of the existing encounter skeleton.

## Unreal verification

The final four-move study decoded 600 frames. The mesh audit covered 662 poses including its lead-in and recovery. Both hands touched the haft on 662/662, while measured active bell-to-damage offset was 0.0 cm at logging precision. The shaft touched the forearm in 23 poses, down from 119 on the previous playable revision. Upper-arm contact occurred in 11 poses. Head, torso and legs had zero sampled crossings. The lower sole ranged from −1.63 to +0.60 cm. The guide wrist's largest eligible adjacent-sample rotation was 22.78° on the new mesh. These are fixed-rehearsal results.

The actual Quake pose was reconstructed from the 89 captured Unreal transforms. Its surface matched the 108,021 rendered vertex positions to within 0.000034 cm. That verifies the correspondence between the pose data and the mesh. Across different costumes, the fraction of measured forearm surface compressed below half its rest area fell from 3.83% to 0.78%, while the fraction stretched above twice its rest area rose from 2.17% to 6.18%. The two costumes have different geometry and reference areas. A localized point remains at the outer shoulder, with folding at the bracer edge. Further work should target these boundaries with the same poses.

Launch `./scripts/bosslab-game` and select **Challenge → The Bellbreaker**. `BOSSLAB_BB_SKIN=forge ./scripts/bosslab-game` selects the previous ForgeShoulder for comparison, and the earlier weathered variant remains available. An explicit `./scripts/bosslab-game 1080p` launches a 1920 × 1080 viewport at 100% requested screen percentage. The usual performance preset otherwise uses 75%.

The local Mac editor-game passed 54/54 native tests (one engine HTTP connectivity warning) and 2/2 dedicated forge tests. A real 1920 × 1080 encounter-selection capture confirms the matching painted poster and launch resolution. The actual fight movie is separate and silent. Visual evidence is under `artifacts/art/bellbreaker-remodel-20261120/runtime`; the packed editable and portable models are under its sibling `playable` folder. The 1500-pixel mesh close-up and 72-view orbit under `artifacts/art/bellfounder-hires-20261120` use the completed GLB's actual surface and colour map. They are independent of Unreal lighting.

On this Mac the performance preset at its usual 1280 × 720 viewport and 75% screen percentage averaged 59.65 FPS across 3,436 active frames, with 16.76 ms p95. At a native 1920 × 1080 and 100% screen percentage it averaged 45.32 FPS across 2,574 frames, with 22.95 ms p95. Each test excludes 180 warmup frames. Both runs identified the remodeled default in their logs. No locked frame-rate claim.
