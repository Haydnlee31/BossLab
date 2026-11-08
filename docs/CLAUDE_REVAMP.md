# Claude revamp — 2026-11-09

Branch `Claude-revamp`. Owner direction (2026-11-09): reach the approved player and Funeral Regent concept targets; free models and free services are allowed, paid services are not.

## Why the method changes

V1–V13 and the Regent clay/cage/focal studies were built by Python scripts placing and smoothing primitives in Blender. That method plateaued well below the targets: the targets depend on sculpted forms, simulated cloth and painted textures, which script-placed geometry does not produce. Another scripted iteration is not planned.

New pipeline:

1. **Image-to-3D from the approved concepts.** Clean single-character inputs are in `artifacts/art/claude-revamp-2026-11-09/inputs/` (player from `last-vigil-concept-2026-11-07`, Regent front from `funeral-regent-construction-2026-11-08`; title text, the separate player sword and the floating skulls painted out). Generation uses free Hugging Face Spaces (`microsoft/TRELLIS.2` first, `tencent/Hunyuan3D-2.1` as alternative) through `unreal/art-studio/source/gen3d/trellis2_generate.py`.
2. **Review renders** of each result with `unreal/art-studio/source/gen3d/render_glb.py` (project-local Blender) against the concept.
3. **Cleanup in Blender:** separate sword/skulls/chain, decimate to a runtime budget, fix scale and pivot.
4. **Rig:** fit to the existing Epic mannequin skeleton so current animations and engine-owned combat timing are unchanged; mantle/cape get secondary bones or cloth.
5. **Unreal import** as another opt-in costume, like the V13 trial. Default costume and packaged app stay preserved.

Boss AI work can then resume in parallel on placeholder-or-better art rather than waiting for final art.

## Status

- Inputs prepared and inspected.
- All seven candidate Spaces run on shared ZeroGPU hardware. The first anonymous TRELLIS.2 run (1536 resolution) hit the ZeroGPU quota. With the owner's free Hugging Face token (passed only as `HF_TOKEN`, never stored), both 1024-resolution runs succeeded.
- **Player** (`player-trellis2/model.glb`, seed 0, 109 s): 296,405 triangles, one material, two 2048² textures. Silhouette, layered pauldrons, gothic breastplate panel, belt/pouch, tassets, fur mantle and tattered red cape all match the concept. Armor albedo reads darker and less worn/riveted than the concept; back fur is a coarse blob; separate sword not generated.
- **Funeral Regent** (`regent-trellis2/model.glb`, seed 0, 75 s): 286,829 triangles. Crown, ivory mask, ribbed cuirass, engraved left pauldron, embroidered stoles, chain-reel bracer with hook, held sword and tattered mantle all match the construction sheet. Sword is thin and fused to the hand; the three skulls were deliberately excluded and still need generating.
- Review sheet: `artifacts/art/claude-revamp-2026-11-09/both-sheet.png` (front, three-quarter, side, back, rendered by `review.sh`). Owner silhouette/material review comes before rigging.

## Next

1. Owner reviews the sheet. Optionally run more seeds or a 1536 pass for detail.
2. Generate the three skulls and a separate greatsword from the concept detail panels.
3. Cleanup: split weapon/chain, decimate to ~60–80k triangles with a normal bake from the 300k source, fix pivots.
4. Rig to the existing mannequin skeleton via a remeshed proxy and weight transfer; test the existing swing/roll animations.
5. Unreal opt-in import alongside the V13 trial.

## Limits

Generated meshes will be dense triangle soups with baked texture lighting and no rig; expect cleanup. Single-view generation guesses unseen sides (back of the player, back of the mantle). Do not describe generated output as hand-authored or production-final.
