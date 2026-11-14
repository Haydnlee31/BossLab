# Generated raised-dead skeleton, 2026-11-14

## Input

- **Image:** FLUX.1-schnell seed 3 (`inputs/skeleton-3.png`). It has an A-pose with the arms held clear of the ribs; the prompt is in its `.json`.
- **Model:** TRELLIS.2 at seed 3 and resolution 1536. The run took 40 s on the owner's HF Pro account. The token was passed inline only and not stored.
- **Result:** a real 3D ribcage, pelvis, spine and limbs, with open gaps between the limbs. See `skeleton-trellis2-views.png`.

## Rig

- **Fit:** `rig/skeleton-fit.json` with `rig_fit.py`. The only pose change raises both forearms 36°, because the generated forearms splay outward. Bone names, order and translations stay identical to `SKM_Manny_Simple`.
- **Mesh:** 40k triangles, with 0 unweighted vertices.
- **Checks:**
  - joint overlay (`rig/fit2-overlay.png`; `fit1` was the rejected try that raised the upper arms);
  - stride and raised-arm deformation (`skeleton-pose-test.png`).

## Unreal

- **Import:** `ue_import_dead_gen.py` (editor mode) creates `/Game/BossLab/Regent/Dead/SKM_RegentDeadGen` (local) on **SK_Mannequin**, so `MF_Unarmed_Walk_Fwd` and `MM_Attack_02` play on it unchanged.
- **Material:** `M_RegentDeadGen` is the albedo ×0.8, rough and non-metallic. Two emissive tries lit the dark shins solid blue (`skeleton-in-game-first-blue.png`), so the emissive was removed.

## Game

- **Mesh:** each dead slot prefers this mesh over the gaunt mannequin. It keeps its own material at uniform scale 1.
- **Head:** the separate generated skull is hidden. The soul-fire eyes sit in the sockets (head bone + 9 cm forward, 6 cm up, ±4 cm), and the crown flame sits 19 cm above the head bone.
- **Rules:** Raise the Dead rules are unchanged.

## Verification

- **Tests:** native suite 39/39.
- **Capture:** `capture regent-study` with `BOSSLAB_STUDY_FROM=16` had 0 material failures. `skeleton-in-game-closeups.png` shows a rise, walk and swing.
- **Not verified:** the owner has not tested it, and the eyes are small at the study distance.
