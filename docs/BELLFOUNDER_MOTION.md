# Bellbreaker grip and walk review

The previous Bellfounder replay kept both hands in contact with the weapon across all 662 sampled poses. The fingers could still reverse along the shaft and the elbow could swing across the chest. In the rejected build the largest change in a hand axis relative to the weapon in one 30 Hz interval was 178° on the left and 166° on the right.

The regression check reads the direction from the index knuckle to the pinky and the normal of the back of each hand on the posed skeleton. It rotates these axes into the weapon's moving coordinate system and compares consecutive frames. It also checks the signed direction of each grasp and the wrist rotation against the fitted neutral wrist. Large turns of the bell itself are therefore distinct from the hand twisting around its grip. This check cannot detect a loose finger or a compressed upper arm on its own. The close-camera replay is needed for those defects.

The camera-on-player combat exercise runs through the fixed encounter while a scripted player circles, reverses direction, rolls and tries three strikes. Health is replenished for recording. The 16-second pursuit exercise omits strikes and sends the player through six locations with two pauses by the boss. It exercises roughly 22 metres of walking in this layout. An optional side view follows the same route with the boots and upper body in frame. All three exercises use the Unreal character and environment.

From the project root, the following commands reproduce the study captures. They overwrite the launcher's scratch captures and log, so archive each result before starting the next.

```sh
export BOSSLAB_BOSS=bellbreaker BOSSLAB_ARENA=forge BOSSLAB_OUTFIT=revamp BOSSLAB_QUALITY=performance
BOSSLAB_BELL_AUDIT=1 BOSSLAB_BELL_AUDIT_ONLY=1 ./scripts/bosslab-unreal capture bellbreaker-study
python3 scripts/review-bellbreaker-grip.py artifacts/unreal/capture.log
BOSSLAB_BB_HAND_CAMERA=1 ./scripts/bosslab-unreal capture bellbreaker-study
./scripts/bosslab-unreal capture bellbreaker-footwork
BOSSLAB_BELL_AUDIT=1 ./scripts/bosslab-unreal capture bellbreaker-walk side
python3 scripts/review-bellbreaker-walk.py artifacts/unreal/capture.log
```

The walking check measures the lowest skinned boot vertex from the bottom 8 cm of the bind mesh, in world centimetres for each declared single-support pose after the gait entry blend. It reports both feet independently. Looking only at the lower of the two can miss a support leg hovering while the unloaded leg touches the floor.

## Pursuit replay

In the matched 16-second side-camera pursuit, the earlier version raised the pelvis by as much as 31.71 cm in a tenth of a second while walking. The corrected clip measures 2.95 cm over the same window at the worst established-gait sample. The corrected pose uses the visible boot soles to place each loaded leg. All 295 established single-support samples had a lowest tread vertex within 0.57 cm above the floor. The greatest supported toe drift between consecutive samples was 0.90 cm. These figures describe the saved pursuit trajectory, including two planned pauses. Rapid lock-on reversals in a fight impose a different load on the legs.

The combat replay uses scripted movement and button requests with the normal third-person lock-on camera. It produced two rolls and three player strikes, four boss attack entries and one player hit reaction on the recorded 16-second route. A separate four-attack rehearsal, including the phase change, supplies the hand close-ups. Performance is measured in a separate real-time run.

## Arm and weapon replay

The smith keeps distinct rear and guide grips. The forearms rotate into their load, fingers wrap around the measured curved haft, and each thumb opposes the fingers. During the floor strikes the torso stays behind the rear fist. In the rejected intermediate landing, the chest pitched through the rear hand and forced the elbow to change sides during one frame. Preserving the elbow plane through that impact and settling the chest away from the pommel keeps the shaft clear of the trunk.

| Maximum change between adjacent 30 Hz poses | Prior left | Final left | Prior right | Final right |
|---|---:|---:|---:|---:|
| Wrist rotation relative to forearm | 140.31° | 18.95° | 149.65° | 26.23° |
| Elbow rotation relative to upper arm | 176.93° | 29.21° | 175.14° | 53.81° |
| Shoulder rotation relative to its parent | 172.19° | 46.31° | 122.64° | 45.70° |
| Largest hand-axis change relative to the weapon | 178.33° | 21.05° | 165.60° | 35.89° |

Each column covers all 662 complete instrumented poses in the four-attack rehearsal, including carry and recovery. The maximum can occur in a different pose in each column. The original capture had 14 hand-axis quarter-turns relative to the weapon. The final capture had zero. Both hand meshes contacted the weapon in all sampled poses. On the final build no weapon triangles intersected the head, torso or legs. Cuff/forearm triangles still contacted the haft or pommel in 244 poses and a few upper-arm triangles in three poses. Some shoulder-border stretching remains on the inward Sweep. A separate change to the shoulder weights redistributed the distortion in two measured poses and was rejected. The production mesh and its 4K maps are preserved.

Results and complete logs are under `artifacts/unreal/bellfounder-anatomy-20261120`. The original-fit comparison and player-camera exercise are under `artifacts/unreal/bellbreaker-human-motion-20261120`. Independent timestamped visual review and the rejected skin-weight experiment are under `artifacts/art/bellbreaker-motion-visual-review-20261120`.

## What changed in the pursuit

The stride follows the distance the smith travels. As the weight settles on one leg, the supporting tread stays near the floor while the other boot clears it. The chest and bell settle into the next step. The final side-camera take covers the same path through six starts and two pauses as the earlier pursuit.

Across 295 established single-support samples in the final take, the lowest point of the supporting tread ranged from 0.27 cm below the floor to 0.57 cm above it. The largest change in hip height over 100 ms of continuous walking fell from 31.71 cm in the earlier candidate to 2.95 cm. The largest movement of the planted toe between consecutive eligible samples was 0.90 cm on that route. Tight combat reversals are a separate exercise.

The player-camera route also exposed two places where a forge storage rack could hide the whole fight. The camera now retracts at the combat perimeter before entering the props. It eases upward when space gets tight. A high backswing can still leave the frame at close range.

The final player-camera exercise recorded 542 poses per hand through two rolls, three player strikes, one hit reaction and four boss attack entries. It recorded zero quarter-turns or reversed grips on either hand. The maximum planted-toe movement between eligible combat samples was 1.22 cm. There were 69 established single-support samples, with the lowest point of the supporting tread at most 0.57 cm above the floor. The combat sample includes sharper reversals than the pursuit. Hip height changed by up to 10.5 cm in 100 ms. The previous camera had 40 out of 160 sampled frames with over 80% of the centre near-black. The final camera had zero, with a peak near-black fraction of 7.6%.

### Replay files

- `artifacts/unreal/bellbreaker-human-motion-20261120/final-player.mp4` — normal lock-on camera during the forge fight.
- `artifacts/unreal/bellfounder-anatomy-20261120/final-close.mp4` — grip through all four attacks. At 9.3 seconds the rear glove briefly shifts on the downswing. The previous flip appeared on landing immediately afterward.
- `artifacts/unreal/bellbreaker-human-motion-20261120/final-walk.mp4` — side view of starts, pursuit, turns and stops.

The final native suite passed all 54 tests, including one engine connectivity-check timeout warning. Both dedicated forge tests passed cleanly. The earlier refit run’s native console wrapper output was overwritten during verification. Its full engine log and automation results are retained. New results live under `artifacts/unreal/bellfounder-anatomy-20261120`.

The final 1280×720 performance-preset editor-game benchmark recorded 2,885 active frames, 51.11 FPS from mean frame time, and 28.39 ms at p95. The prior remodel run recorded 59.65 FPS. These are single local runs, and the cause of the difference was not isolated. The unchanged warm repeat measured 56.26 FPS over 3,213 frames and 24.59 ms p95. Both current runs were slower than the previous remodel benchmark.
