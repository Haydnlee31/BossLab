# Authored animation clips, 2026-11-14

The owner asked for real animation clips (item 1) and whether a Hugging Face model could generate animation.

## Source checked and rejected

The free MoCap Online "T.C. Sword" pack licence prohibits "AI usage", including AI retargeting, without a separate permit. It also forbids redistributing the raw files and needs a store checkout, so it was not used.

## Quaternius Universal Animation Library 1 + 2 (CC0, owner-downloaded)

The owner downloaded the free Standard zips to `artifacts/anim-sources/`. They are extracted to `artifacts/anim-sources/quaternius/` and kept local.

- **Rig:** 65 bones with UE4-mannequin-style names, at 24 fps. The clips used are the in-place versions.
- **Retarget:** `unreal/art-studio/source/anim/retarget_ual.py` (Blender).
  - Each mapped bone takes the source bone's world-space rotation change from its rest pose: `R_t = R_s · inv(R_s_rest) · R_t_rest`.
  - The spine maps 01/02/03 to Manny's 01/03/05, and Head maps to head.
  - The pelvis offset is scaled by 1.046 (the ratio of the two pelvis heights).
  - It exports `UAL_Anims.fbx` with 22 takes:
    - locomotion: Idle, Walk, Jog, Sprint, Roll;
    - one-handed sword (UAL2): Sword_Idle, Sword_Attack, Regular A/B/C with recoveries, Heavy_Combo, Dash, Block;
    - hits and death: Hit_Chest, Hit_Head, Hit_Knockback, Death01;
    - Jump start, loop and land.
  - **Root track:** the armature object must be named `root` and keyed in every take. Blender turns the mannequin FBX's `root` bone into the object, and Unreal then reports "animation doesn't contain the root track".
- **Import:** `ue_import_ual.py` (editor mode) puts the clips in `/Game/BossLab/Anim/UAL/UAL_Anims_root_UAL_<Clip>` on `SK_Mannequin` (local).
- **Evidence:** `artifacts/art/anim-ual-2026-11-14/evidence/retarget-poses.png`.

## In the game

- **Sprint (on by default):** the player plays the authored sprint loop when sprinting, unlocked and above 480 cm/s.
  - The clip's clock follows ground speed (0.7–1.3×).
  - The gait switch settles over 8–10 ticks.
  - The existing carry, lean and free-arm layers stay on top.
- **Roll clip (opt-in, `BOSSLAB_ANIM_ROLL=clip`):** forward and side rolls play the authored roll.
  - **Timing:** the tumble (clip 0.1–1.0 s) fills 72% of the roll and the stand-up the rest.
  - **Facing:** the mesh turns to face the roll's travel and returns by tick 38.
  - **Sword:** tucked along the right forearm. The blade on the knuckle line stabbed the floor while inverted, and the floor lift then jolted the whole body.
  - **Legs:** the tuck IK is skipped, because its fixed knee hint flipped the knees upside down.
  - **Floor:** the floor solve only lifts the body out of the floor.
  - **Tests:** with the opt-in, `DirectionalRollPoseContinuity` passes (maximum joint step 43.5 cm, under the 45 cm limit).
  - **Why opt-in:** the clip is a straight-legged dive roll, which reads as parkour rather than a tucked souls roll. The procedural shoulder roll stays the default.
- **Test change:** the roll continuity test now reports which bone and tick produce the maximum step.

## HY-Motion 1.0 (Tencent, text-to-motion)

- **Access:** the official Hugging Face Space `tencent/HY-Motion-1.0` runs on ZeroGPU. It is called through `/generate_motion_func` with text, seeds, duration and cfg, and returns FBX.
- **Test run (15 s on HF Pro):** the prompt was "A person holds a heavy two-handed greatsword, raises it over the right shoulder, then swings it diagonally down while stepping forward." The result is 2.5 s at 30 fps: a believable two-handed overhead chop. See `artifacts/art/hy-motion-2026-11-14/greatsword-chop-test.png`.
- **Rig:** an SMPL-style 52-bone skeleton (Pelvis, L_Hip, Spine1–3, L_Wrist and so on), so it needs its own bone map for the same retarget.
- **Licence (Tencent Hunyuan community licence):**
  - it does not apply in the EU, UK or South Korea;
  - products above 1M monthly active users need a separate licence;
  - outputs may not be used to improve other AI models.
- **Storage:** outputs stay local and are not committed.

## Next

- Map the HY-Motion skeleton onto Manny.
- Generate the moves we have no clip for: greatsword cuts, a low souls roll, run start and stop, pivots, hit reactions.
- Rebuild the player's swings on authored clips while keeping the engine-owned timing windows.

## HY-Motion in the game (same day, owner said go)

- **Generated:** 9 prompts with 2 seeds each, through `unreal/art-studio/source/anim/hy_motion_generate.py`. Each call took 18–40 s on HF Pro. The prompts are recorded in `artifacts/art/hy-motion-2026-11-14/raw/*.json` (local).
  - roll, cut A (horizontal), cut B (diagonal), heavy cut;
  - jump attack, run start, run stop, 180° pivot, heavy hit.
- **Retarget:** `retarget_motion.py` maps the SMPL-style rig (Pelvis, L_Hip, Spine1-3 and so on) to Manny.
  - **Rest alignment:** HY rests in a T-pose and Manny in an A-pose. Each Manny bone's rest is turned onto the source bone's direction (taken from child joints) before copying rotation changes.
  - **Facing:** each clip is turned to start facing forward, using its first-frame hip line. Yaws were fixed by up to 26°.
  - **Standing height:** the rest leg length plus the planted toe-joint height.
  - **In place:** the smoothed (±7 frame) hip path is removed. A straight-line removal left curved travel, such as pivots and jumps, out of frame.
  - **Contact point:** the frame of peak hand speed is recorded for timing.
- **Import:** `ue_import_hy.py` puts the clips in `/Game/BossLab/Anim/HY/HY_Anims_root_HY_<name>` (local; outputs are never committed).
- **Evidence:** `artifacts/art/hy-motion-2026-11-14/evidence/`.
- **Roll (default now):**
  - **Clip:** `roll_s0`, a crouch, a low dive, a ground tumble, then up.
  - **Timing:** its tumble span (0.15–0.75 s) is mapped onto 72% of the 40-tick roll.
  - **Blending:** it eases in over 10 ticks and back to the guard stance over the last 20%. The mesh turns toward the roll's travel over 10 ticks and returns by tick 38.
  - **Switch:** `BOSSLAB_ANIM_ROLL=ual` gives the UAL dive roll, and `=procedural` the keyed shoulder roll.
  - **Tests:** `DirectionalRollPoseContinuity` gives a maximum joint step of 44.1 cm (the limit is 45) and an exit of 0.9 cm. Using the whole clip moved joints about 50–70 cm a tick.
- **Cuts I–III (default now, `BOSSLAB_ANIM_CUTS=off` to disable):**
  - **Clips:** `cut_a_s0`, `cut_b_s1` and `cut_heavy_s1` drive the spine, neck and head.
  - **Timing:** each is time-warped so its peak hand speed falls mid-contact. Wind-up maps to the clip start up to peak − 0.12 s, contact to ±0.12 s, and recovery to the rest of the clip.
  - **Unchanged:** the arms stay on the procedural sword path, so the blade sweep, hit timing and reach are the same. The hips and legs stay keyed, because the clip's hips slid the support foot by about 10 cm.
  - **Layering:** the keyed hip and spine layer drops to 40% under a clip.
  - **Tests:** `MovingStrikeSupportFoot` gives a drift of 1.28 cm (the limit is 3) and a height error of 1.02 cm (the limit is 1.5).
- **Native suite:** 39/39. Captures: `in-game-roll.png`, `in-game-cuts.png`.
- **Not wired yet:** jump attack, run start and stop, pivot and heavy hit are imported but unused. Their entry points, such as stop and pivot detection, need care. The feel is not owner-tested.

