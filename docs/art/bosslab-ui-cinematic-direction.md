# BossLab cinematic frontend direction — 2026-11-14

Owner rejected the dashboard treatment. This revision uses a game title-screen composition: one atmospheric environment, a dominant title, a quiet vertical action list and one clear focal character. No new imagegen call was made by art direction; root is producing the backdrop through the requested Hugging Face workflow. No menu code edited here.

## Composition handoff

Home: full-bleed artwork with the left40% quiet and dark; architectural/Regent focus in the right60%. Place a modest72–100px emblem above or beside a live serif B O S S L A B wordmark, approximately48–64px at desktop reference scale. Menu begins near x8%/y48%;44–52px rows and generous spacing. Use ivory type and an antique-gold rule/diamond to mark selection. Challenge, Creative, Settings and Quit are navigation, not dashboard cards. Do not add metrics, dense status chips, decorative panels or huge logo discs to the home screen. Bottom hints/version/credits remain subordinate but legible.

Boss selection: one dominant Regent portrait on the right and concise title/lore/mode action on the left. Only actual available bosses are selectable; no fake content grid. Settings: aligned rows in one restrained dark translucent field, tab/category hierarchy and visible Back; retain keyboard focus and clear adjustment feedback. Results: one outcome heading, attempt/mode context and3–4 meaningful statistics. Creative results explicitly identify practice and remain separate from Challenge records. Decorative imagery cannot obscure state, focus, error messages or accessibility settings.

Backdrop target for root: sealed funerary tribunal at night, monumental distant pointed arches and weathered burial walls, tiny cold blue witness flames, indigo/charcoal shadow with narrow warm bronze highlights. Strong scene depth concentrated to right, no lettering, no baked buttons, no central glare across title/menu. Quiet floor and walls on the left. Prefer one compelling light composition over many glowing objects. Generated atmosphere is artwork, not a screenshot of the playable arena.

## Existing portrait asset and provenance

Copied unchanged: `artifacts/art/claude-revamp-2026-11-09/inputs/regent-input.png` → `unreal/BossLabWarden/Content/UI/RegentPortrait.png`. This is the existing approved-B-derived generation input, not a new photograph, runtime render or newly generated portrait. It is opaque artwork on beige, not a transparent cutout. The previous source preprocessing removed floating skulls/title and leaves faint rectangular background patches near the upper sides; those are present in the copied image. Do not stretch it across a dark background or describe it as clean isolated art.

Use it only as a temporary portrait within an intentional narrow artwork area, maintaining its aspect ratio. A dark edge gradient/frame may integrate the beige ground in presentation, but cannot repair source detail. If the HF backdrop supplies a cleaner matching character composition, prefer that rather than forcing this image into the home screen. Preserve the original source and copy; no image manipulation was performed for this task.

## Critique boundary

The owner's dashboard rejection is accepted. The recommendations above address information hierarchy and composition, not a claim that art direction viewed a captured rejected screen: no current frontend screenshot was available in the discovered artifact paths. Final judgment requires actual home, boss selection, settings and both result modes at desktop and720p, with keyboard selection visible. Check text contrast and artwork crop after the builder integrates assets. This document does not assert runtime or owner acceptance.
