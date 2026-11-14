# BossLab UI emblem — 2026-11-14

Project asset: `unreal/BossLabWarden/Content/UI/BossLabLogo.png`, 1254×1254, 8-bit RGBA PNG. Original generated broken antique-gold circular seal surrounding an ivory/silver downward greatsword with one cyan guard jewel. No raster wordmark; UI should render B O S S L A B as live text.

Generated with the built-in imagegen tool using `/Users/haydn/.codex/skills/.system/imagegen/SKILL.md`; no API CLI, HF token, import or build. Source: `/Users/haydn/.codex/generated_images/01a1b1a0-77d3-7b81-af3a-e40b742bb743/exec-c10ce1a6-345e-437a-ad65-10eb58781003.png`. Copied unchanged into the project and visually inspected.

Alpha verification: PNG reports RGBA; direct lossless scan found 1,134,784 fully transparent pixels. The viewer displays red/yellow fringe harshly, but all detected saturated-red fringe pixels have alpha1–3/255, almost transparent. A targeted cleanup generation was rejected because it filled the emblem's interior with a pale field; the original remains the selected asset. Faint low-alpha fringe remains a limitation, not a claim of perfectly sanitized alpha. Inspect in the actual Slate dark background before final UI acceptance.

Suggested use:160–220px home-screen emblem with a separate restrained ivory serif wordmark; smaller displays lose fine engraving. Palette: near-black indigo background, antique gold selection accent, ivory primary text, muted cyan reserved for special status. Avoid tiling the emblem as decoration or using it behind body text. This is a generated branding asset, not a registered mark or trademark-clearance claim.

## Exact initial prompt

Use case: logo-brand. Create one original premium dark fantasy video game emblem for BossLab, emblem only with NO WORDS, NO LETTERS. Transparent background, square canvas. A broken circular ceremonial seal surrounding one perfectly vertical downward-pointing greatsword. Restrained elegant heraldic geometry with a few intentional gaps in the ring, antique muted gold ring, ivory silver sword, a single tiny cold cyan jewel at the guard. Strong distinctive silhouette, balanced negative space, refined sharp edges, lightly engraved craftsmanship but large quiet shapes; legible at 64 pixels, beautiful at 256 pixels. Flat front elevation, subtle restrained metallic tonal shading, no perspective. Centered compact composition occupying 78 percent of canvas with safe transparent padding. This is a professional game home screen logo, not a scene, not a weapon photograph, not an ornate coat of arms. Avoid skulls, wings, laurels, flames, background discs, gradients outside the emblem, cast shadows, bloom, particles, texture noise, watermark, text, mockup. Genuine alpha transparency.

## Rejected cleanup prompt

Clean this logo's transparency only. Preserve the exact gold broken circular seal, ivory silver vertical sword and tiny cyan gem, shape, framing and proportions. Remove ALL red, yellow and grey speckled fringe pixels around the edges and inside negative space. Every area outside the solid metal emblem must be genuinely fully transparent alpha zero, including all interior openings. Edges clean and crisp with minimal antialiasing. No glow, halo, shadow, particles or background. No text. This is a production game UI emblem with clean alpha.
