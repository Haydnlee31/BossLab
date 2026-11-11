# Soul fire and rune mandalas, 2026-11-11

Owner feedback: the soul fire looked too simple and its colour was not strong enough, and the summoned circles should carry runes "like a Dr Strange spell".

## Changes

- **Soul fire** (`M_RegentFlame`, [ue_import_regent.py](../../../unreal/art-studio/source/regent/ue_import_regent.py)):
  - **Shape:** a domain-warped, swaying tongue with detail noise scrolling faster than the warp.
  - **Colour:** an HDR palette from indigo edges through electric blue and cyan to a white-cyan core.
  - **Extras:** a soft halo, rising embers and flicker.
  - **Card width:** cards are 1.3× wider in C++ to make room for the halo.
  - **Hall fire:** phase two turns the hall fire to soul fire with the same material, so the hall fires change too.
- **Skull trails** (`WardenRegent.cpp`): a flying skull trailed a row of upright cones. It now streams one long tongue back along its flight line (a camera-facing card aligned to the velocity), with a shorter rising tongue and two small licks.
- **Rune mandala** (`M_RegentRune`):
  - **Layout:** an outer rim, a band of 24 procedural rune glyphs (staves with branches, some with rings) turning one way, a tick ring turning the other, an octagram of two squares, an inner ring of 14 glyphs, a hexagram, spokes and a hot centre.
  - **Glow:** thin lines with a soft glow; the tint is deepened so the lines stay coloured under bloom.
  - **Reveal:** a new MID parameter, `Reveal`, draws the circle in with an angular sweep and a bright leading edge.
  - **Where it appears:** the pools, eruptions and pyre circles all use it.
- **New circles** (presentation only):
  - **Spell wind-ups:** a summoning circle (R 175 cm) under the Regent during every spell wind-up (Volley, Furrow, Circle). It draws in over 60% of the wind-up and fades just after release.
  - **Witness Circle:** a mandala (R 320 cm) forms under the player while the skulls orbit, brightening toward the dive.
- **Bug found:** `M_SwordSteel` had never compiled. A new ComponentMask defaults to R+G, giving `float2 × float3`, so since 2026-11-10 the greatsword blade drew with Unreal's default material. That includes the overnight greatsword evidence. [ue_import_greatsword.py](../../../unreal/art-studio/source/sword/ue_import_greatsword.py) now sets each mask channel explicitly. After reimport, the logs show 0 "Failed to compile" materials.

## Evidence

- `mandalas-and-soulfire.png`: the Ashen Furrow marks, the violet Pyre circle, burning pools, and the summoning circle at the Witness Circle wind-up.
- `witness-circle-under-player.png`: the mandala under the player during the orbit, then the dive.
- `skull-comet-trails.png`: the new flying-skull trails.
- `before-first-mandala-overbright.png`: the rejected first pass, with thick white lines.

## Verification and limits

- **Tests:** native suite 33/33.
- **Gameplay:** combat timing and hitboxes are unchanged.
- **Not owner-tested.** The circles cost shader time while visible; there is no new benchmark.
- **Disk:** one capture stopped at the new 15 GiB reserve because earlier capture frames had accumulated in the scratchpad (~1.2 GB per 30 s study). Frames are now deleted after inspection.
