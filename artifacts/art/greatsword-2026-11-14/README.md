# Generated player greatsword, 2026-11-14

## Input

- **Images:** four FLUX.1-schnell inputs (seeds 3, 7, 11 and 19). See `greatsword-input-candidates.png`; the prompt is in each `.json`.
- **Model:** TRELLIS.2 at seed 3 and resolution 1024 on seed 7 (chosen for its broad blade and down-turned guard) and on seed 3 (the alternate, kept in `prep-3`).

## Blender prep

- **Script:** `prep_estoc_trellis.py`, now generic: it takes a name plus `guard_z` and `tip_z`. It runs with `1.78 X SM_GreatswordGen 0.08 1.48`.
- **Placement:** seated in the sword-root frame with the grip at the origin, the guard at 8 cm and the point at 148 cm (the engine's reach). The pommel lands at −45 cm.
- **Mesh:** 16k triangles. See `greatsword-prepared-previews.png`.

## Unreal

- **Import:** `ue_import_greatsword_gen.py` (editor mode) creates `/Game/BossLab/SwordGen/SM_GreatswordGen` (local), 42.5 × 7.3 × 193 cm.
- **Material:** `M_GreatswordGen` uses the albedo, roughness from G (at least 0.28) and metallic from B.
- **Runes:** a scalar `Glow` lights six blue glyph segments down the fuller (local |x| < 0.9 cm, 22–118 cm). A first compile failed because `line` is an HLSL keyword; it was renamed.

## Game

- `DressGreatsword()` prefers this mesh over the Blender `SM_Greatsword` and drives `Glow` through the existing rune code (slot 0).
- Reach and contact sweeps are unchanged.

## Verification

- **Tests:** native suite 39/39.
- **Capture:** `capture feel` had 0 material failures. `greatsword-in-game.png` shows the guard, a roll, the cut chain and the runes.
- **Not verified:** the owner has not tested it.
