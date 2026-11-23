# Bellbreaker dialogue mix and weapon path

## Listening evidence

The voice plays dry and centered. During a line the forge score fades to 13% of its usual level, the furnace to 17%, and other effects to 22%. The mix yields to speech over 35 ms and comes back over 380 ms. Bell impacts retain their own attack outside dialogue. Sustained floor scraping has a 1.45 kHz low-pass, a 0.62 s duration limit and a 2.4 s retrigger interval. Speech blocks new scrapes.

The audio-enabled phase-two benchmark recorded 60 seconds of the actual game. On “You cracked her. She was all I had,” the estimated voice-to-residual ratio over 180–3400 Hz rose from −10.82 to +6.69 dB. This compares the recorded mix against the source voice and includes other sounds and any unmatched voice energy in the residual. An on-device English speech transcriber recovered two of eight words from the old mix and eight of eight from the new one. Both figures describe that line and recording. Listening comfort across headphones and speakers still needs player feedback.

Evidence lives under `artifacts/unreal/bellbreaker-weighted-arc/`. `phase-before-after.wav` plays the earlier and revised excerpts at recorded levels, separated by one second. `phase-live.wav` contains the revised excerpt alone. `live-mix.wav` contains the full benchmark. See `voice-comparison.json` and `phase-intelligibility.json` for the measured results.

## Weapon study

The editor study plays Hammer Fall, Forge Sweep, Bell Quake and The Bell Breaks with the production pose code. Its triangle-intersection diagnostic compares the rendered bell mesh against the currently skinned costume at the displayed level of detail. Hands touching the grip can be desirable. Counts describe sampled poses containing one or more mesh-surface crossings. They do not measure penetration depth or establish complete clearance between samples.

The previous sweep turned 240 degrees. The new sweep covers 116 degrees across the front. Hammer Fall, Bell Quake and the phase transition lift the bell, accelerate down and hold the planted contact before recovery. A shared weapon pose now locates the visible mouth and the damaging melee trace. The solver fits the hands to the imported curved shaft, positions the elbows on opposite sides of the grip, and allows the guide hand to slide during the loaded sweep. The revised strike geometry changes the area the bell covers. Damage values, attack durations, cooldowns, roll rules and phase triggers retain their previous definitions.

During development, a narrower swing still missed the damaging point by up to 104.5 cm, and a later version let both hands miss the shaft in 58 poses. A subsequent version restored two-hand contact at the expense of intersections with the chest. These versions were rejected. The intermediate arc6 native run recorded 53 passing tests and one failure: the new sweep regression subtracted the moving grip position twice when calculating shaft heading. The corrected check independently verifies that the mouth stays in front, the shaft faces forward, the turn goes one way and the measured turn falls between 110 and 120 degrees.

## Final attack capture

| Poses with a weapon crossing | Previous | Revised |
| --- | ---: | ---: |
| Torso | 460 | 0 |
| Head or neck | 46 | 0 |
| Legs | 192 | 0 |
| Upper arms or clavicles | 111 | 11 |
| Forearms | 662 | 166 |

Each study sampled 662 poses including carry and transitions. Both hands touched the handle in 659 revised poses. Every Hammer Fall and Forge Sweep sample had contact at both hands. In three downward slam samples the guide hand lost surface contact. The largest guide-pocket error was 22.6 cm on the phase-break descent. Nine sweep anticipation poses show the pommel brushing shoulder or upper-arm armour. Forearm counts include shallow cuff contact. In the final sweep the worst individual forearm had one intersecting face, compared with 419 during intermediate fitting. Player perception and poses outside this study still require review.

The visible bell mouth and damaging centre coincided to the nearest 0.1 cm in all 19 active melee samples. During the two floor blasts, the measured rim was 2 cm above the floor and horizontally aligned with the blast origin. The historical proxy-only clearance numbers in earlier reports undercount physical intersections.

Watch `final.mp4` for the 20-second three-quarter attack study and see `final-measurements.json` for the per-move results. It is a silent fixed-timestep capture. Listen to `phase-before-after.wav` for the in-game sound comparison.

The separate six-second release study forces a stagger and defeat using the game presentation path. All 180 rendered frames decoded. The final fallen pose shows the bell at rest on the floor, with zero measured body or hand crossings. See `release.mp4` and `release-study.log`.

Final Mac editor automation passed 54/54 native tests and 2/2 dedicated forge tests, all without test warnings. Result summaries and the per-test reports are saved as final-native and final-forge JSON files beside the clips. Launch with `./scripts/bosslab-game`, choose Challenge, select the Bellbreaker and begin the challenge.
