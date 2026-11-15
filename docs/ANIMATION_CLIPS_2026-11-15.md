# HY-Motion refinement pass, 2026-11-15

A one-hour pass on the owner's HF Pro quota (about 6 minutes of wall time on the
HY-Motion 1.0 Space; token inline only, never stored). Ten prompts with two seeds each
gave 20 clips in `artifacts/art/hy-motion-2026-11-15` (local, Tencent Hunyuan licence; the
owner is outside the EU, UK and South Korea).

## Pipeline

- **Retarget:** `retarget_motion.py` writes the batch FBX `artifacts/art/hy-motion-2026-11-15/HY_Anims.fbx`.
- **Import:** `ue_import_hy.py` now imports every batch folder's `HY_Anims.fbx` into
  `/Game/BossLab/Anim/HY`, giving 38 clips.
- **Prompts:** the exact prompt and seeds for each clip are in `raw/<name>.json`.

## Wired clips

All of these are presentation only: rules, timing, hit boxes and iframes are unchanged.

| Moment | Clip | How |
|---|---|---|
| Death (player and boss) | `death_s0`: reels, drops to both knees, falls forward flat | Whole body. It runs on its own clock at 1.1× and eases in over 8 ticks (`DeathAge` still stops at 72). The blade stays in the right fist on one hand, and the floor solve grounds the body. `BOSSLAB_ANIM_DEATH=off` gives the keyed fall. |
| Backward roll | `back_roll_s1`: sits back, tumbles over the shoulders, comes up crouched | Its 0.1–1.0 s span is mapped onto 72% of the roll, like the forward roll. The mesh faces away from the travel. The blade is laid across the body: along the forearm, it swept about 80 cm through the floor overhead and made the floor solve jump the body by 84 cm. |
| Boss stance break | `stagger_s0`: drops to both knees, curled over, then rises | Whole body at 90% across the 84 hurt ticks; the keyed hip sink is skipped under it. |
| Drinking | `heal_s0` | Spine, neck and head at 60%, sampled on `OverlayBody` so the walk keeps its clock. |
| Landing a jump | `land_s0` (deep absorb) | Upper-body overlay, 0.17–0.95 s over 26 ticks at 70%. |
| Cut II | `cut_b2_s2` (high wind-up, full torso turn), replacing `cut_b_s1` | Peak 0.3 s (was 0.2 s, which left almost no wind-up). |

## Imported but not wired

- `stalk` (a regal walk for the Regent; it needs a clean loop span);
- `cast` (arms raised to summon; the Regent's arms are keyed with the censer chain);
- `backstep` (no backstep action yet);
- `strafe` (the lock-on strafe already uses the blendspace);
- the other seeds of each clip.

## Checks

- **Native suite:** 41/41. `DirectionalRollPoseContinuity` has a maximum step of 44.1 cm (the forward roll, unchanged; limit 45). The reactive bot beats the Regent 4 of 6 times, unchanged.
- **Fixed during the pass:** a null sampler instance crashed the input-buffer test before anything had played on `OverlayBody`.
- **Captures:** `rolls-cardinal` shows the backward roll with the blade across the body. `spectacle` (Regent, dungeon) shows the felled Regent dropping to his knees and folding over. The stance-break kneel is covered only by the native tests, not by a capture. Frames were deleted after inspection.
- **Not owner-tested.**
