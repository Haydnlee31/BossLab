# Bellbreaker — the Last Casting smeltery revision

2026-11-16. Owner supersedes the cathedral-foundry direction: medieval blacksmith smeltery, huge working furnace, anvils, leather bellows and molten channels. **Remove the monumental scenic bell.** The bell belongs solely to the boss's handcrafted legendary weapon, made of finest steel; no duplicate bell iconography or bronze bell shrine. This document is art direction, not a claim of completed assets, safe combat rules or successful Unreal integration.

## Four dominant reads

1. **A huge rear stone furnace**, centred toward +Y: an irregular masonry mass about 9 m wide × 6 m deep × 11 m high, with a 3.5 m arched working mouth and broad chimney receding into the vault. The mouth provides the principal amber glow. Thick soot-black voussoirs, repaired iron straps and deep hearth establish medieval construction; no sheet-metal chimney, factory gantry, plate-glass windows or modern trusses.
2. **A low, heavy stone smeltery enclosure**, with successive deep masonry arches, rough dark fieldstone and timber lofts along the sides. Vault spring approximately 7–9 m; crown 11–13 m where practical. The roof must feel weight-bearing and smoke-stained, not a modern shed with a decorative arch pasted on it. Narrow high slits introduce restrained cold daylight. The main forge stays the strongest focus.
3. **Believable side workstations**, clustered into two or three bays: anvils seated on scarred oak blocks, small secondary hearth, tongs/hammers hanging from timber, ingot stacks, quench trough and worn leather aprons. Anvil tops approximately 0.85–1 m high; each complete working group fits roughly 2.5 × 2 m. Group tools where a smith could reach them, not random floor scatter. Furniture can supply dense detail outside movement space without compromising the central field.
4. **A controlled molten route**, visually linking furnace tap to covered side collection basins: narrow recessed channels approximately 0.35–0.6 m wide, outside the proposed fight boundary and away from the initial walkthrough route. Use actual dark stone channel beds, coping and iron grates/bridges where any route crosses. Hot metal should be white-yellow at the pour, orange within the channel and dark crust at the edges, not a uniformly luminous red ribbon. These are scenic molten-metal effects, not new damage mechanics. Lava-like appearance is acceptable, but foundry construction should explain the flow.

## Layout and walkthrough contract

Implemented walkthrough revision: flat 28 × 36 m rectangular central floor. This supersedes the earlier r4 studio outline for exploration only; future fight boundaries remain unvalidated. XY origin remains centre, +Y rear forge. The previous six-metre reserve is superseded by closer low workstations and masonry supports outside the walking rectangle, with engine camera/pawn blockers at the visible coping. This is not a guarantee of camera comfort at every setting. The large furnace occupies a rear recess; nearby anvil and toolbench bays can be viewed from the bordered floor. Expand recesses rather than plant props into the arena. No open pits, channel crossings or glowing seams across the central combat floor. Keep the boss absent from the requested first Unreal walkthrough.

Arrival from −Y should reveal a dark foreground arch, the broad traversable floor and the rear furnace mouth. A secondary side approach reveals anvil/bellows construction at human height. Walkthrough priorities: entry-to-forge approach, both workstation bays, channel edge/bridge, reverse view and one close furnace view. Verify actual engine floor continuity, blocking and camera motion; Blender stills alone cannot satisfy the walkthrough request. Do not claim lava damage, charge fairness or performance until separately tested.

## Material/light hierarchy

Sooted dark stone, worn charcoal iron, oak end grain, cracked oxblood leather and ash-dusted floor; restrained warm steel highlights. Hot amber furnace and channels contrast with weak cool slit light. Keep most surfaces dark/matte but retain floor and doorway readability. Add heat scale, clinker, hammer dents and soot at physically motivated locations. No blue necromancy, gold ceremonial trim, clean tiled mall floor, bright untextured wall panels or repeated flame emitters everywhere. Protect player silhouettes from overexposure and deep black crush. Medieval material variation and large masonry depth matter more than increasing generic noise.

## Four bounded generation prompts

Each is an original isolated asset, complete visible base, three-quarter view, neutral background, even diffuse illumination, no text or people, no baked environmental cast shadows. Texture/color from generation is not calibrated PBR. Root owns HF calls; inspect actual meshes on all sides and normalize to measured dimensions before assembly.

### 1. Great stone smelting forge

“Original medieval blacksmith smelting furnace, massive irregular soot-dark fieldstone body, nine metres wide six metres deep eleven metres tall in intended scale, deep broad pointed stone hearth arch with thick wedge-shaped voussoirs, recessed firebrick interior, heavy rough stone chimney, repaired wrought-iron binding straps, low tapping spout and clinker-stained stone collection lip, believable masonry support and complete heavy foundation. Cold unlit asset with dark interior; fire and molten metal will be added separately. No cathedral altar, bells, modern factory ducting, steel shed, pipes, electric lights or machinery. Isolated complete architectural prop, three-quarter view, neutral background, diffuse lighting, no text, no people.”

### 2. Anvil workstation

“Original medieval master blacksmith workstation, forged iron double-horn anvil with squared hardy hole and worn polished striking face, seated firmly on a heavy scarred oak stump with iron securing staples, small timber tool rack holding three distinct tongs and two hammers, a modest stack of rectangular dark steel billets beside the block, compact coherent two-and-a-half-metre by two-metre working group, human-scale waist-high anvil, actual support contacts and believable tool handles. No floating tools, fantasy glyphs, bells, machinery or clutter pile. Complete isolated asset with base visible, neutral background, diffuse lighting, three-quarter view, no text, no people.”

### 3. Leather bellows apparatus

“Original medieval forge bellows apparatus, large elongated teardrop oxblood leather accordion bellows between two thick oak boards, stitched leather seams and iron nail heads, oak trestle support, simple pivoted wooden lever with rope pull, short tapered iron nozzle projecting horizontally toward a forge, visibly compressible folded leather sides, complete stable feet. Rough handmade construction, approximately three metres long and two metres high, soot at nozzle, otherwise restrained wear. No engine, fan, hydraulics, modern pump, bells or glowing parts. Complete isolated prop, neutral background, diffuse lighting, three-quarter view, no text, no people.”

### 4. Medieval load-bearing arch bay

“Original medieval smeltery stone arch bay, two massive rough fieldstone piers on broad square footings supporting one deep pointed masonry arch built from distinct wedge-shaped stones, approximately eight metres clear span and nine metres total height, one-and-a-half-metre structural depth, smoke-dark inner soffit, restrained chipped edges and lime-mortar joints, simple impost courses, believable continuous compression load path, complete front and rear returns. No decorative unsupported arch tails, cathedral tracery, gold, modern metal beams, window glass, bells or attached floor. Complete isolated architectural module, neutral background, diffuse lighting, three-quarter view, no text, no people.”

## Review gate

Actual Unreal walkthrough must read immediately as a working medieval smeltery, with no giant scenic bell and no boss. Assess the furnace as a dominant volumetric structure, human-scale workstations, contained molten routes, traversable quiet floor and masonry weight from several moving viewpoints. Generated props, cinematic fire and material polish do not substitute for coherent construction or actual engine verification. Preserve the previous foundry draft separately as superseded evidence.


## First actual architecture review — not accepted

Inspected `artifacts/art/bellbreaker-smeltery-2026-11-16/architecture-preview.png` before generated props. The unobstructed floor is useful, but the broad straight roof facets, repeated pale roof strips, huge rectangular framed masonry grids and blank triangular rear infill read as a modern warehouse. Warm light and stone textures do not resolve that structural identity. This preview does **not** pass the requested medieval smeltery direction.

Correction handed to technical art: author a genuinely curved pointed barrel section with visible haunches, lower side work aisles and substantial perimeter abutments; all support footprints remain outside the protected floor/reserve. Recess vault webs between load-bearing masonry ribs rather than applying pale bands to a gabled plane. Replace garage-door-like rear panels with one thick continuous masonry rear wall, a deep dominant furnace alcove and two smaller unequal arched work niches. Remove rectangular black panel frames and exposed blank triangular infill. Keep small doors, anvils and alcoves at believable human scale so the main volume feels monumental rather than empty. The generated furnace should strengthen an already coherent structure, not conceal an unresolved shed. No added columns or obstacles in the28×36m floor and no material-only substitute for this correction.

Preview SHA-256: `62a170c89dfac1bb37c3881b5a4753fed03b5ccedbb7a773595357a3df55f0aa`. This is a critique of actual rendered geometry, not a claim that the correction has been built or tested. Actual Unreal walkthrough remains required.
