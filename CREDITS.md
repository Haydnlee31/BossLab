# Credits

## Sound

The audio files are not in this repository; they are downloaded locally and built by
`unreal/art-studio/source/audio/` (see `docs/AUDIO.md`). Attribution for the sounds the game uses:

| Sound | Author | Licence | Used for |
|---|---|---|---|
| [Ghost Manifestation 1 - Scream from the Tomb](https://freesound.org/s/423008) | OGsoundFX (Olivier Girardot) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | skull screams (pitched, sliced, layered) |
| [Scattered Ghost](https://freesound.org/s/211646) | Iwan "qubodup" Gabovitch | CC BY (the page states 3.0 in its text and 4.0 on its badge) | boss music bed; choir of the dead; cast drone |
| [Whispers, "Schizophrenic" or Ghost-like voices](https://freesound.org/s/423869) | belarathbone | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) | casting swells, orbiting-skull whispers |
| [RPG Audio](https://kenney.nl/assets/rpg-audio), [Impact Sounds](https://kenney.nl/assets/impact-sounds) | Kenney | CC0 | footsteps, impacts, cloth, chains, crackle grains |

All CC BY sounds were modified (sliced, pitch-shifted, reversed, filtered and layered).
The in-game title screen carries the same attribution.

### Generated sounds: the Bellbreaker (2026-11-18)

The 26 bell, impact, shockwave and ear-ringing sounds in `/Game/BossLab/Bellbreaker/Sound` were generated with
**Stable Audio Open 1.0** (Stability AI), through the `1inkusFace/Stable-Audio-Open-Zero` Hugging Face Space
(`unreal/art-studio/source/audio/sfx_generate.py`). The exact prompts are in `artifacts/audio-bellbreaker-2026-11-18/raw/*.json`.

**Powered by Stability AI.** The model is used under the [Stability AI Community License](https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md). It is free for individuals and organisations with under USD 1M in annual revenue; above that, a Stability AI enterprise licence is required.

The sounds were trimmed, faded and peak-normalised. TangoFlux was considered and not used: its checkpoints are for non-commercial research only.

The readiness pass (2026-11-23) added 15 more Bellbreaker move sounds from the same model and Space (toll ring, stamp, slag fling and landing, cyclone, charge, upswing scrape, triple knell); prompts in `artifacts/audio-bellbreaker-moves-2026-11-23/*.json`. **Powered by Stability AI.**

### Generated forge props: the Bellbreaker arena (2026-11-23)

The cracked bell, casting mould, bell frame and other forge dressing under `/Game/BossLab/Bellbreaker/ArenaProps` were made from
original text prompts with **FLUX.1-schnell** (Black Forest Labs, Apache-2.0) and converted to 3D with **TRELLIS.2** (Microsoft, MIT),
both through their free Hugging Face Spaces, then decimated in Blender. Prompts and run records: `artifacts/art/bellbreaker-arena-props-2026-11-23`.

### The Bellbreaker's spoken performance

The challenge, cracked-bell and defeat lines were written for BossLab and synthesized from one original male voice design with Qwen3-TTS. The performance was edited into three local game assets. The source audio, casting direction and edit history are under `artifacts/bellbreaker-fury`. [Qwen3-TTS VoiceDesign model card](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign)
