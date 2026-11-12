# Game audio, 2026-11-12

The owner said the audio was "a bit plain" and asked how game audio engineers work out a game's sound and how to integrate it.

## How game audio is usually made (research)

- **Spotting list.** Start from every gameplay event that needs a sound. Each event is played through the engine or middleware (FMOD, Wwise, Unreal Sound Cues or MetaSounds), which randomises, layers and attenuates it ([Krotos](https://krotos.studio/blog/sound-effects-for-games)).
- **Layering.** Build each sound from separate layers: transient, body, texture, tail and an optional sweetener. Align the attack and tail to the animation frames ([layering guide](https://claudskills.com/skills/game-sound-design/SKILL.md)).
- **Variation against repetition.** Repetition causes listening fatigue and is the clearest sign of cheap audio.
  - An AAA sound designer describes five variations per layer, giving 125 combinations, or 625 with a sweetener ([A Sound Effect](https://www.asoundeffect.com/game-audio-immersion/)).
  - A common rule of thumb is 3–5 variations per sound, with random pitch and volume ([game audio principles](https://www.mdskills.ai/de/skills/game-audio)).
- **Mix.** Mixes follow a priority order (player over enemy over ambience), with voice limits, distance attenuation and room reverb ([game audio principles](https://www.mdskills.ai/fr/skills/game-audio)).
- **Elden Ring.** I found no public interview on its combat sound design. One interview only notes that FromSoftware was not pursuing 3D audio at the time ([Kitao](https://ungeek.ph/2021/08/full-interview-fromsoftwares-yasuhiro-kitao-shares-big-elden-ring-details)).

## Sources (all CC0 or original)

- **Kenney packs:** [Kenney RPG Audio](https://kenney.nl/assets/rpg-audio) (50 files) and [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) (130 files). Both pages and the bundled `License.txt` state Creative Commons CC0.
  - The owner downloaded them to `artifacts/audio-sources/`, because Kenney blocks scripted downloads.
  - The zips, the extracted files and every generated WAV or Unreal asset stay local and are not committed.
- **Procedural layers:** magic, fire, air passes, gulps and the ambience beds are synthesised in [make_game_audio.py](../unreal/art-studio/source/audio/make_game_audio.py). There is no CC0 magic library in the two packs.
- **Not used:**
  - OpenGameArt packs: the site refused automated access, so their licences could not be checked.
  - The 2 GB "fantasy" CC0 pack: too large for the project's storage rules.

## Pipeline

1. **Decode.** [decode_ogg.py](../unreal/art-studio/source/audio/decode_ogg.py) uses Blender's bundled `aud` decoder, since the project has no ffmpeg. It writes mono 44.1 kHz WAV, because Unreal only spatialises mono.
2. **Build.** [make_game_audio.py](../unreal/art-studio/source/audio/make_game_audio.py) builds 80 files (22 events) with layer recipes. `manifest.json` records every layer, its source and its pitch shift.
   - **Subsonic high-pass:** a 45 Hz high-pass on everything.
   - **Presence band:** about 0.7–3 kHz on heavy impacts.
   - **Why:** before this pass the hits, slams, landings, rolls and boss steps had 70–90% of their energy below 150 Hz. Laptop speakers cannot play that range, so on a MacBook these sounds would have sounded weak.
   - **After rebalancing (laptop loudness, peak 50 ms RMS above 150 Hz):**

     | Group | Laptop loudness |
     |---|---|
     | Impacts | 0.10–0.19 |
     | Whooshes | 0.14–0.24 |
     | Footsteps and ambience | lower |

   - **Variations:** distinct from one another (mean cross-correlation 0.02–0.59).
   - **Loops:** seams are below the typical sample step.
3. **Import.** [ue_import_game_audio.py](../unreal/art-studio/source/audio/ue_import_game_audio.py) runs in headless python mode and writes `/Game/BossLab/Sound`. `Amb*` files are set to loop.

## Spotting list (event → layers)

| Event | Trigger | Variations | Layers |
|---|---|---|---|
| SwordWhooshLight / Heavy | player cut contact | 5 / 4 | resonant noise band sweeping up then down, air body, faint blade sing; heavy adds cloth |
| SwordHit | blade lands on the boss | 5 | heavy punch body, knife-slice texture, plate ring, sub thump, noise tail, presence |
| RuneHum | enchantment flare on a hit | 3 | detuned bright partials and sparkle |
| SwordSlam | jump attack lands | 3 | ground crunch (mining), punch, sub boom, four debris ticks |
| BodyHit | a fighter is hurt | 5 | punch, armour plate, sub |
| GearSwing | swing or jump starts | 4 | cloth and belt leather |
| RollCloth | roll | 4 | cloth, belt, body thump at 0.22 s, stone scrape at 0.30 s |
| StepStone / StepHeavy | each foot plant while moving (player / bosses) | 8 / 5 | stone steps; boss steps lower and weightier, with an armour jingle |
| LandHeavy | plain jump landing | 3 | two quick steps, thud, armour |
| FlaskDrink | heal | 3 | glass clink, cork pop, 2–3 gulps, warm shimmer |
| RegentBell | bell moves | 3 | Kenney bell 9–11 semitones down, with procedural toll partials |
| RegentWhoosh | censer swings | 4 | heavy sweep, chain rattle (coins pitched down), latch |
| RegentThrust | estoc | 4 | fast thin sweep, blade scrape |
| RegentSkull | skull launch | 4 | soul-fire, sweep, bone clack (wood pitched up) |
| RegentBlink | vanish / ash step | 3 | rising swell, shimmer, landing thud |
| RegentEruption / Pyre / Wakes | fire magic | 3 / 2 / 3 | fire roar and crackle, ground crunch, sub; the pyre adds a deep bell |
| AmbDungeon | always (loop, 24 s) | 1 | room tone, slow wind band, random water drips |
| AmbFire | six braziers nearest the centre (dungeon, loop, 8 s) | 1 | crackle and roar, random start offsets and ±8% pitch so they never phase |

## Engine (WardenAudio.cpp)

- **One play path.** `PlaySfx` handles every one-shot:
  - **Variation:** picks a random variation, never the one that just played (`SfxPick`).
  - **Jitter:** pitch ±4–7% and volume −12–0%.
  - **Voice limit:** 3 per sound (4 for steps), stopping the oldest.
  - **Distance and reverb:** distance attenuation by category, with the reverb send on.
  - **Routing:** the older `EffectSound`, `RegentSound` and `PlayCue` now route through it.
  - **Fallback:** each falls back to the older single sounds when the layered set is absent, as on a fresh clone.
- **Room reverb.** `ActivateReverbEffect` with a runtime `UReverbEffect`: a 2.6 s dark stone hall for the dungeon, 1.4 s for the original court.
- **Mix.** The player's own sounds sit on top: hit 0.8, whooshes 0.6–0.8, body hit 0.75. The Regent's sounds are scaled ×0.9. Steps (0.4 / 0.55, scaled by pace) and ambience (room 0.32, fires 0.5 with an 11 m falloff) sit underneath. Mute (M) also silences the loops.
- **Footsteps.** Footsteps come from the existing foot-lock plant detection, when moving faster than 60 cm/s. There is at most one per foot per 0.2 s, since render frames can re-plant within a stride.

## Verification

- **Tests:** native suite 34/34. The new `BossLab.Audio.VariationsNeverRepeat` test checks two things:
  - over 400 picks there are no immediate repeats, and every variation is used;
  - every event in the spotting list has its variation count.
- **Real run with the audio device on** (benchmark mode, which, unlike capture, does not pass `-NoSound`), dungeon, Regent and revamp:
  - the log shows "reverb hall, 7 ambience beds, 26 variations across 5 sample events";
  - there are no BossLab audio errors;
  - the only warning is the engine's CoreAudio sample-rate query.
- **Benchmark:** the same run measured 16.67 ms mean / 16.74 ms p95 at 720p on a quieter machine (load about 3–4). It is not an audio on/off A/B and makes no 60 FPS claim.
- **Not verified: nothing has been listened to.** The agent cannot hear the output, so the checks are numeric: spectrum, loudness, clipping, variation and loop seams. Owner listening is required, especially for:
  - the whoosh character;
  - the bell;
  - the overall balance against the boss's magic.

## Soul-fire rebuild (2026-11-12, owner: "the summoning soul fire sometimes still has a robotic sound")

- **Causes found:**
  - **Click crackle.** The old fire crackle was a per-sample probability of 0.004–0.012, which is **about 175–530 identical filtered clicks per second**. At that density the clicks fuse into a buzzing rasp.
  - **Steady roar.** The roar was steady filtered noise, with a resonant band at 700 Hz and no flutter. It read as electronic hiss.
  - **Laser sweep.** The skull swish was a resonant band-pass sweep.
  - **Stacked copies.** The phase-two fan volley and the Witness Circle dive play three near-identical skull sounds on the same tick.
- **Fix:** standard fire sound design, using organic sources.
  - **Crackle:** grains of the CC0 wood and stone impacts (10–45 ms, pitched up 5–13 semitones, all different) at natural densities: braziers 7/s, skull 18/s, Wakes 20/s, eruption 26/s, pyre 30/s.
  - **Roar:** a broadband roar with no resonance, with 9 Hz random flutter, plus a low body with 3.5 Hz flutter.
  - **Fire whoosh:** a real cloth flap pitched down 7–9 semitones under noise whose low-pass opens and closes, with no resonance.
  - **One sound per skull group:** `RegentSound` plays each Regent sound at most once per 3 ticks, so simultaneous skulls make one sound.
- **Measured buzz:** the ratio of 30–300 Hz loudness modulation (roughness, which reads as buzz) to 1–30 Hz (flame flutter), old → new:

  | Sound | Old | New |
  |---|---|---|
  | RegentSkull | 0.67 | 0.34 |
  | RegentWakes (the phase-two soul-fire ring) | 3.16 | 0.69 |
  | RegentEruption | 1.88 | 0.96 |
  | RegentPyre | 5.77 | 2.31 |
  | AmbFire | 6.56 | 2.63 |

- **Verification:** native suite 34/34. Not listened to.
