# Generated witness skull, 2026-11-11

- **Generation:** TRELLIS.2 on [skull-side-7.png](../hf-leftover-2026-11-10/inputs/skull-side-7.png), the 45° FLUX input, with seed 3 and resolution 1024. It took 72 s and used one free daily run. The owner's token was passed only as an environment variable.
- **Result:** a fully volumetric skull, with a cranium, sockets, nose, teeth and a separate jaw line. The thinnest dimension is 0.68 of the largest; the rejected overnight skull was a flat relief. It has 284k faces, so it must be decimated.
- **Evidence:** `skull-trellis2-views.png` shows eight orthographic views (front, sides, back, three-quarters, top and below), rendered as a quick face splat without Blender.
- **Local only:** `trellis2/model.glb` (10 MB) stays local, like the other generated assets.
- **Remaining quota:** spent on one censer input, [censer-5.png](../hf-leftover-2026-11-10/inputs/censer-5.png), for the next TRELLIS run.
- **Integration pending.** It was not started because free disk space was 21.2 GiB, below the 24 GiB reserve.
  1. Blender: `prep_skull_trellis.py <model.glb> <out_dir> [yaw]`, which decimates to about 9k triangles, sizes the skull to 22 cm and exports FBX.
  2. Unreal: `ue_import_regent_props.py` in editor mode.
