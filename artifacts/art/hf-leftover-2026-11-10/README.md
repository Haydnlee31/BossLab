# Leftover ZeroGPU quota, 2026-11-10

The owner asked me to use the about 2.7 minutes of free ZeroGPU quota left after the overnight TRELLIS skull run. Their token was used only as a temporary environment variable and was never written to a file.

## What happened

- **FLUX.1-schnell inputs.** [flux_generate.py](../../../unreal/art-studio/source/gen3d/flux_generate.py) made three clean skull images in `inputs/`. Each one has a `.json` alongside it recording the prompt and seed.
  - **Quota cost:** each call reserved 90 s of quota, although generation took about 8 s. Three calls spent the remainder.
  - **Not made:** the fourth skull and both censer images were refused for quota.
- **Unauthenticated image-to-3D attempts on `skull-side-7.png`:** both failed with no result.
  - Stable Fast 3D: upstream error, no detail given.
  - TripoSG: `RuntimeError`.

## Inputs

| File | View | Notes |
|---|---|---|
| `skull-side-7.png` | 45° three-quarter | Cranium depth, cheekbone and jaw are visible. Slightly stylised anatomy. **Preferred image-to-3D input.** |
| `skull-11.png` | Near frontal | Clean, but likely to reconstruct flat. |
| `skull-23.png` | Frontal | Clean, but likely to reconstruct flat. |

## Lessons

- **Quota is charged by reservation.** A ZeroGPU Space is charged its requested duration up front, not the time it takes: FLUX reserved 90 s and TRELLIS.2 about 120 s at double cost. On a free account, the 5-minute daily quota buys about three image calls or one 3D run.
- **Use angled views.** Image-to-3D inputs should be single, large objects at three-quarter view on a plain background. A frontal view gives flat reliefs, as the overnight skull showed.

## Next

- **Skull model:** run `trellis2_generate.py` on `skull-side-7.png` when the quota resets, at about 02:49 +08 on 2026-11-11.
- **Censer:** generate an input image with the censer prompt below in a later session.

Censer prompt: "A single ornate gothic funeral censer lantern hanging from a short ring, blackened iron cage with pierced arched windows and a pointed spire cap, tarnished bronze bands and finials, glass panes, empty, isolated on a plain flat light grey background, centered, whole object in frame, three-quarter view, studio product photograph, soft even diffuse lighting, sharp detail, no chain, no text"
