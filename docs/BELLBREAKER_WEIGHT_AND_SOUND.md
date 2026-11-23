# Bellbreaker: weight and sound
Local Unreal editor-game. The boss still follows the fixed rehearsal. This revision deliberately changes his attack timing; it is not a cosmetic-only revision. Damage, roll invulnerability and quake wave speed are unchanged.

| Move | Wind-up | Active | Recovery | Minimum time between starts |
|---|---:|---:|---:|---:|
| Hammer Fall | 84 ticks | 12 | 94 | 10 s |
| Forge Sweep | 68 | 18 | 80 | 8 s |
| Bell Quake | 106 | 4 | 108 | 16 s |
| The Bell Breaks | 90 | 4 | 88 | One phase transition |

60 combat ticks per simulated second; hit-stop and slow motion can extend wall-clock durations. Repeat limits include the action itself. The boss takes an additional breath after recovery. Slams trigger a short vertical camera displacement with a smaller rebound, attenuated over distance, without altering aim. Reduced motion suppresses it.

The visible boss uses the hammer/forge motion batch. The old stagger/death takes were replaced by a forge stagger and the held kneeling portion of the shockwave reaction. The phase break, Fall, Sweep and Quake use the existing individually authored Bellbreaker attacks. Player equipment, controls and shared interface music remain separate.

Anvil Measure is an original, sample-free 36-second instrumental loop in triple time, with drum skin, struck wire and a bowed bass line. Six original synthesized vocal efforts and a separate cycling furnace/bellows bed were authored without a model service or actor recording. No spoken dialogue. Forge routes have no fallback to MusicBoss, AmbDungeon or Regent voice assets. Imported Unreal sound assets stay local. Source generators/importers live under unreal/art-studio/source/bellbreaker; source and recorded audio are distinct. See artifacts/bellbreaker-voice and artifacts/unreal/bellbreaker-weight.

The first 600-frame side view exposed a phase-break lift that crossed the torso. Moving the brace outside the weapon shoulder and blending into it earlier reduced the same pose solver's worst phase-break intrusion from 30.3 cm to 0.5 cm. Across all four moves the worst sampled body intrusion was 0.6 cm, floor intrusion was 0.0 cm and left-hand grip gap reached 6.0 cm on Hammer Fall. These measurements use the solver's body proxies. Both shockwave strikes registered 0.00 cm horizontal separation between rim and blast centre and 2.00–2.01 cm of vertical rim clearance. The side camera shows the motion and ground contact. Camera-shake strength and the audio mix still need a player feel/listening review.

Native automation passed 54/54 (one engine warning), separate forge automation passed 2/2. Side capture decoded 600/600 frames. The separate 61.4 s stereo runtime recording includes the forge bed, score and loaded voice bank. Its peak was near full scale, with zero full-scale samples. The same 720p editor-game performance pass measured 16.6906 ms mean and 16.7478 ms p95 over 3,443 frames. Results and local playback files are under artifacts/unreal/bellbreaker-weight.
