# BossLab visual direction — 2026-11-07

Status: working art direction for the player revision, not owner acceptance or a finished-asset claim. Applies to original BossLab assets. The user's role guides are workflow guidance; they do not authorize downloads, spending, rule changes, or boss AI. Character, animation, gameplay and performance acceptance must precede boss AI work.

## Identity

A sanctuary guard wearing equipment that was made well, used for years, and repaired with care. The player is an armed person inside fitted clothing and plate, not a stack of ornamental primitives. The Last Vigil and Oathwake remain original designs; no copied wolf head, lion pauldron, named-game crest or recognisable source-game armor set.

The supplied screenshots establish the desired richness of overlapping construction, controlled irregularity and material separation. They do not prescribe a literal costume. Detail must emerge from construction: plate overlaps, rolled edges, hinges, straps, stitched seams, hammered surface and wear at contact points. Ornament is subordinate to the body and weapon.

## Palette and material hierarchy

Hex values below are sRGB appearance guides, not raw linear shader input values. Judge under the unchanged neutral review lights before any dramatic lighting.

| Material | Appearance guide | Starting shader intent |
|---|---|---|
| Blackened steel fields | `#32383C` | Metallic 0.9–1; roughness 0.42–0.58, narrow low-contrast variation |
| Worn steel edges | `#92948E` | Metallic 1; roughness 0.28–0.42; narrow broken edge exposure |
| Old electrum | `#857044` | Metallic 0.85–1; roughness 0.4–0.58; small focal fittings only |
| Charcoal arming cloth | `#26282A` | Metallic 0; roughness 0.85–0.95; low sheen |
| Oxblood wool | `#392028` | Metallic 0; roughness 0.88–0.96; diffuse fold gradients, no satin bands |
| Oiled leather | `#30261F` | Metallic 0; roughness 0.5–0.7; compression/wear near seams and buckles |
| Ash mantle | `#777266` | Dark roots and varied grey-brown tips; matte irregular clumps |
| Old linen repair | `#827561` | Localized desaturated patch, rough fibrous edge, not a white sticker |

At gameplay scale, the silhouette and sword edge must read before embroidery. Keep roughly two thirds of large armor fields quiet. Concentrate bright contrast at brow, hands/guard and selected cutting edges. Do not outline every plate or seam in bright gold. The cape should be darker than the exposed steel. Preserve shadow detail; do not make the costume black to hide modeling weaknesses.

## Shape and construction rules

- Seat the helmet into the protective collar; avoid a tall exposed neck tube. Distinguish crown, brow, cheek plane, jaw and nape.
- Shoulder protection follows the deltoid and shoulder blade in layered shells. A broad left rear wing may counterbalance a compact right sword-side shoulder; no arbitrary giant spike.
- Taper limbs around anatomy. Joint pieces must appear to permit elbow, wrist, knee and ankle movement. No floating circular joint balls.
- Hands require a thumb, a palm/knuckle arch, different finger lengths and a relaxed curl. An ornate glove cannot replace anatomy.
- Cloth hangs from sewn attachments, changes fold scale along its length and has a visible edge/lining. Asymmetry comes from fastening, repair and wear, not random vertex noise.
- Fur grows in clumps with varied direction and length. Break its silhouette locally; avoid a continuous fringe of identical straight strands.
- Sword blade, guard, grip and pommel must have a credible continuous structural axis. Sacred fittings attach to that structure. Lore marks are subdued inlays or engravings, not wires laid on top.

## Surface wear

Use three scales with different causes: large material/repair zones; small scuffs at overlapping edges, grip contact and hems; very fine roughness/hammering. Large cloudy noise over every plate is forbidden. Most metal color should remain stable; roughness can carry subtle variation. A repaired left shoulder, polished thumb contact, blade sharpening and dust along a cloth hem tell more than randomly distributed scratches. Maintain an intact cutting edge. Never copy dirt texture onto every material.

## Motif hierarchy

One main motif: the interrupted gate/halo. One subordinate rhythm: seven keeper marks. On armor, retain a small chest seal or narrow border detail; remove repeated scroll stickers across every limb. The cape device can be partly interrupted by folds and a repair. Oathwake's repaired seam and incomplete hilt reliquary are the story focus; they should remain recognisable without emissive glow.

## Lighting and review

Keep existing studio camera framing and neutral key/fill for before/after comparisons. Also inspect grey/clay silhouette and flat-lit material views when available; dramatic fog, bloom or crushed shadows cannot close a modeling defect. Future sanctuary lighting remains restrained warm practicals against cool neutral darkness; no new Lumen/fog cost is authorized by this document. Check arm/weapon silhouettes against both dark and medium backgrounds before integration.

## Performance and scope

Current target is a static studio revision. Preserve prior scenes and evidence. No new downloaded meshes/textures or 3D generation services. Stay within the existing 10 GB unreal directory allowance and 24 GiB free reserve; serialize heavy jobs. Do not increase geometry simply to claim detail. Working ceiling for this revision: no more evaluated geometry than the prior approximately 985k-triangle studio master unless a documented visible benefit warrants it; this is not a runtime budget. Prefer reworking existing shapes, fewer better fibers, and authored masks. Runtime retopology, atlases, LODs, skinning and measured frame cost remain later acceptance work.

## Primary construction references

These are construction references, not assets to reproduce or import. Sources inspected 2026-11-07.

- [Denver Art Museum: Age of Armor — Reality](https://www.denverartmuseum.org/en/age-armor-access-guide-reality): explains fitted overlapping plates, arming-jacket attachment and joint mail; identifies the rear shoulder wing's gap coverage. Our inference: believable articulation and attachment should drive the model before decoration.
- [V&A: Dressed to kill — fashion and armour](https://www.vam.ac.uk/articles/fashion-and-armour): describes armor as fitted, mobile clothing, with deliberate shape and decorated bands. Our inference: plate form and restrained ornament hierarchy are stronger than uniform surface noise.
- [The Met: Arms and Armor — Common Misconceptions](https://www.metmuseum.org/essays/arms-and-armor-common-misconceptions-and-frequently-asked-questions): distinguishes practical, fitted armor and the sophistication of functional weapons from popular caricatures. Our fantasy design remains original and is not a historical reconstruction.
