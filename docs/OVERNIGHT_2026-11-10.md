# Overnight 3D and refinement run, 2026-11-10 (02:37–03:45)

The owner asked for modelling and refinements while they slept, with optimisation afterwards. Their priorities, in order:

1. the player's sword (enchanted glow);
2. the boss: abilities first (skulls), then looks and motion;
3. the map: ground look and elevation.

Everything is on branch `regent-moveset-01`. Imported Unreal assets stay local, as before.

## Generation (free TRELLIS Space)

- **Anonymous attempt:** refused. Anonymous use allows almost no ZeroGPU quota.
- **With the owner's token,** passed only as a temporary environment variable on the generator command and never written to a file, the free account allowed one run that day:
  - **Skull:** the concept's skull is about 40 px wide, so I upscaled it to 1024 px and painted out its flame (`inputs/skull-input.png`). The run produced `skull-trellis2/model.glb`, which [prep_skull_trellis.py](../unreal/art-studio/source/regent/prep_skull_trellis.py) prepared.
  - **Rejected:** the result is a flat relief, a sliver seen from the front (`skull-gen/skull-gen-previews.png`), and would look like a cut-out as it orbits. The Blender skull stays.
  - **Greatsword:** refused ("exceeded your free ZeroGPU quota… try again in 23:56").
- **Recommendation:** revoke this token, because it was pasted into chat. Image-to-3D needs clean, large, single-object inputs; the skull crop was too small.

## Player greatsword (priority 1)

- **Model.** [prep_greatsword.py](../unreal/art-studio/source/sword/prep_greatsword.py) builds it in project-local Blender from the approved concept, in about 10.8k triangles:
  - a diamond-section blade with a fuller;
  - a curved crossguard with ball finials, a half-ring and a centre langet;
  - a leather grip with a raised spiral wrap, bronze ferrules and a faceted pommel;
  - six glyphs inlaid on both faces of the fuller.

  It sits in the game's sword frame (grip at the hand, point at the existing 148 cm reach), so contact and balance are unchanged.
- **Materials.** [ue_import_greatsword.py](../unreal/art-studio/source/sword/ue_import_greatsword.py) builds them:
  - pattern-welded steel (object-space folded bands, varied roughness);
  - blackened iron, oxblood leather and aged bronze;
  - `M_SwordRune`, emissive amber with a `Glow` parameter.
- **The enchantment** ([WardenEffects.cpp](../unreal/BossLabWarden/Source/BossLabWarden/WardenEffects.cpp)):
  - **Runes:** they breathe at rest, build through each wind-up, blaze on contact (more on heavy moves) and flash when a blow lands.
  - **Light:** an amber light rides the blade during swings.
  - **Trail:** a soft amber trail (`M_SwordTrail`) follows the blade during contact.
  - **Rejected first trail:** it drew solid bright slabs; it is now dim, narrow and soft-edged.
- **Bug found and fixed.** `DressFighter` re-showed every `Sword*` part after the new weapon hid it. The primitive blade drew through the greatsword, and through the Regent's estoc after every reset; that explains the orange crossbar seen in earlier captures.
- **Evidence:** `greatsword-in-hand-sheet.png`, `greatsword-runes-closeup.png`, `greatsword-swing-trail-sheet.png`.

## Boss abilities, looks and motion (priority 2)

- **Witness Circle** (new, phase two; Regent move 15).
  - **How it works:** the skulls circle the player at 3.2 m for 0.9 s (a clear tell), then dive in together from three sides. One timed roll beats all three.
  - **Test:** standing still takes 48 damage; one timed roll takes 0.
  - **Evidence:** `witness-circle-sheet.png`.
- **Fan volley.** In phase two, Witness Volley launches every ready skull at once in a 25° fan.
- **Skull trails.** Flying skulls stream soul-fire trails.
- **Stagger critical** (Elden Ring stance break):
  - a broken stance now staggers for 1.4 s (was 0.6);
  - blows on a staggered boss deal 2.5× damage, with a long hit-stop and a "CRITICAL BLOW" message;
  - the boss visibly buckles forward, blade dropped and hips sunk, until three quarters of the stagger (`stagger-critical-window-sheet.png`).
- **Looks.** The Regent's mask eyes glow with soul fire, brighter and flaming in phase two.
- **Tests:** the Regent fight now uses 13 of 13 moves. The test bot wins in about 70 s (Regent) and about 16 s (Warden).

## Map: ground and elevation (priority 3)

- **Floor.** [ue_import_floor.py](../unreal/art-studio/source/arena/ue_import_floor.py) layers it as:
  - cobbles in the centre and outer band, with a worn flagstone fight ring and an irregular boundary;
  - soft-edged puddles;
  - soot and grime, cracks, and old dried bloodstains toward the centre.

  The masks are baked offline by [bake_floor_masks.py](../unreal/art-studio/source/arena/bake_floor_masks.py), so the floor needs one texture lookup per pixel instead of about 100 noise evaluations.
- **Floor problems fixed:**
  - puddles first reflected the sky fill as flat blue paint, then read as black holes; they are now soft wet stains;
  - blood splats were too vivid.
- **Elevation, all outside the fight floor:**
  - the great door behind the boss stands on a stone dais above the parapet, with side steps down into the trench;
  - a balustraded gallery on corbels rings the hall at about 8 m, except over the doors (`raised-door-gallery.png`).
- **Fight floor:** still flat by design. Movement, jumps and tests assume one ground height, so playable elevation needs ground-following movement and step-up first.
- **Dungeon check:** 1,165 instances, 0 colliding, 0 inside the wall line.

## Extension (03:42–03:50): sound and presentation

- **Greatsword sound.** [make_combat_audio.py](../unreal/art-studio/source/effects/make_combat_audio.py) synthesises five original cues, imported by [ue_import_combat_audio.py](../unreal/art-studio/source/effects/ue_import_combat_audio.py) into `/Game/BossLab/Effects/Audio` (local):
  - `SwordWhooshLight` and `SwordWhooshHeavy`: swing whooshes at the start of contact, heavier for the finisher and the running cut;
  - `SwordSlam`: the jump attack's landing;
  - `SwordHit` plus `RuneHum`: a blow landing on the boss;
  - `SwordHit`, quieter: you being hit.

  They have not been listened to, only generated and wired.
- **Boss title card.** The boss's name and an epithet ("THE FUNERAL REGENT, Keeper of the Last Rites") fade in and out over the first 4 s of a fight (`boss-title-card-sheet.png`).
- **Victory banner.** "GREAT ENEMY FELLED" in gold when the boss dies. The first version overlapped the results panel; it now sits above it (`great-enemy-felled.png`).

## Optimisation and verification

- **Tests:** native suite **33/33** after every change.
- **Performance changes:**
  - the floor noise is baked into a texture;
  - the heal light is hidden when dark;
  - the sword light is on only during swings or flashes.
- **Benchmarks:** confounded tonight. macOS overnight jobs were running alongside: `mediaanalysisd` at up to 146% CPU, Bluetooth `BTLEServer` at about 100%, storage management, and the animated wallpaper. Load average went from 5 to 40. Full-build runs measured 19.7–26.7 ms mean. The quiet-machine baseline from earlier tonight was 16.8 ms. An old-floor/new-floor A/B was inconclusive under that load. Reports are kept in `artifacts/art/overnight-2026-11-10/benchmark-*.json`. There is no 60 FPS claim; re-measure on a quiet machine.
- **Final fight capture:** `final-fight-sheet.png` and `final-fight-closeups.png`.

## Late benchmarks (03:50–04:00)

All runs below are at 720p with the performance preset, the Regent and the revamp characters.

| Run | Mean / p95 (ms) | Load during run |
|---|---|---|
| Original arena (back to back with the next row) | 17.9 / 25.2 | about 17 |
| Dungeon (back to back with the previous row) | 21.8 / 30.6 | about 17–24 |
| Dungeon, old floor, run 1 | 23.3 / 33.2 | rising to 52 |
| Dungeon, old floor, run 2 | 24.9 / 41.6 | rising to 52 |
| Dungeon, new floor | 24.0 / 33.9 | rising to 52 |

- **Dungeon cost:** the dungeon now costs about 3.9 ms over the original arena in the back-to-back pair, against about 1.5 ms on the quieter machine earlier.
- **Floor:** the floor A/B shows no measurable floor cost.
- **Conclusion:** the extra cost could not be attributed under this load. The suspects to profile on a quiet machine are the dynamic lights, then the hall geometry (gallery, dais), the Regent's flame cards and the translucent blood.
- **Reports:** `benchmark-ab-*.json` and `benchmark-ab2-*.json`.

## Next

- **Generated skull:** a cleaner skull input image (large, single, neutral background), when the quota allows.
- **Regent weapons:** a generated or modelled censer and estoc.
- **Playable elevation:** ground-following movement with step-up and slopes, then a raised dais or sunken ring on the fight floor.
- **Performance:** benchmark on a quiet machine. If the full build is below 60, the first suspects are the dynamic lights (the 17 dungeon lights, plus the censer and sword).
- **Feel:** owner playtest of everything above.

**Correction (2026-11-11):** `M_SwordSteel` failed to compile until 2026-11-11 (ComponentMask channel defaults), so the greatsword evidence above shows the blade with the engine default material; see `artifacts/art/soulfire-runes-2026-11-11/README.md`.
