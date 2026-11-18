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
