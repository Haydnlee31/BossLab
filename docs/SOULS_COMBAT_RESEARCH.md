# Souls combat research and directional-roll pass — 2026-11-03

Owner feedback: motion still needs substantial polish; rolling must work in all directions with brief invulnerability. Research completed before further game edits. Prior technical tests are not artistic acceptance.

## Primary sources and conclusions

- [FromSoftware Dark Souls III PC manual](https://www.fromsoftware.jp/manual/darksouls3/win/action1.html): directional input selects rolling direction; lock-on keeps ordinary movement facing the target; no-direction dodge is a backstep; sprint consumes stamina. The manual also distinguishes one/two-handed attacks. Japanese source read directly.
- [Bandai Namco Elden Ring starter guide](https://en.bandainamcoent.eu/elden-ring/news/elden-ring-starter-guide-tips-know-playing-the-game): rolls follow stick direction, stamina limits actions and regenerates, and targeting is separately controlled. This supports directional movement independent of lock-on.
- [Bandai Namco Elden Ring combat guide](https://www.bandainamcoent.com/news/elden-ring-introduction-part-4-combat-guide): actions commit and buffered inputs can execute afterward; dodge invulnerability avoids damage; spacing, enemy openings and stamina matter. Weapon attacks have distinct movement contexts. This is a publisher-hosted guest guide, not a frame-data specification.

No exact source-game iframe count is asserted. Published guides do not establish exact current frame windows, and source-game frames must not be confused with BossLab's 60 Hz simulation ticks. No unsupported claim about original Dark Souls lock-on restrictions or backstep invulnerability is used. The supplied Godfrey recording remains the visual reference; its sampled frames cannot reveal inputs or invulnerability.

## Current code audit and deliberate choices

BossLab already captures camera-relative WASD intent when Space is pressed, normalizes diagonals and commits that direction. Lock-on does not override the roll request. With no movement it rolls backward; keep this existing prototype choice rather than silently add a different backstep action. Space is dedicated to roll on press, not a shared hold-to-sprint/release-to-roll button. Tab remains targeting.

Existing protection: Dodge age >=4 and <18, i.e. 14 ticks / 0.2333 seconds in a 36-tick / 0.6-second roll. Actual Damage() rejects hits in that interval. These are BossLab values, not claimed Elden Ring values. Preserve them, the 300 cm travel, 28 stamina cost and eight-tick recovery gap. Invulnerability applies only briefly; collision with walls still applies. Exact balance remains subject to play review.

The previous clip deliberately requested side/back rolls only. It did not prove all directions. More importantly, rotating the body around a travel-relative axis while keeping its chest facing the enemy produced a barrel-like sideways tumble. The next original pose turns the visual body into the travel direction before the compact tumble, then recovers toward the prior facing. Camera stays upright; capsule/rules remain authoritative. This pose construction is a design application, not a recovered FromSoftware algorithm.

## Verification gate

1. Eight directions including diagonals, varied actor facing, finite poses, same 300 cm travel/cost, coherent exit and head/blade floor clearance.
2. Real swept-blade collisions at roll ages 3, 4, 17, 18: damage before/after, rejected during the exact protected interval. Prove contact occurred, not merely that the opponent missed.
3. Two explicitly labeled four-direction capture sequences using normal requests, stamina and commitment, with actual protected/vulnerable state in HUD and CSV. Preserve prior clips.
4. Native and cooked tests, frame inspection and status/claims. No quality approval inferred from tests. AI, final models and added weapon systems remain deferred.

## Implemented and verified

The travel-facing tumble is now packaged. Direction selection and protection existed previously; this revision corrects presentation and supplies much broader proof. Roll/attack timing, cost, displacement and damage definitions were not changed. Normal camera framing remains unchanged.

- Native **13/13**, cooked standalone **10/10**, zero test warnings/failures. Fresh JSON reports independently checked; optional engine HTML report template remains unavailable.
- Sixteen ordinary queued requests: all eight headings with lock-on enabled and disabled, each 300 cm and 28 stamina. This exercises the actual gameplay request/step path, not manual keyboard input injection. WASD camera-relative mapping was inspected in source.
- Eight-direction pose continuity with varied actor facing: maximum joint step 39.718 cm, exit jump 0.558 cm, minimum head height 20.000 cm, minimum blade point 32.124 cm. Existing thresholds retained. These are sampled joints/blade, not all vertices or artistic approval.
- Actual blade-capsule collisions at held defender roll ages 3/4/17/18: contact confirmed in every case; health 208/240/240/208 from 240. Thus damage is rejected only at the tested protected boundaries, not explained by a miss. The boundary test intentionally holds defender age/position to isolate damage gating; ordinary moving-roll behavior is separately tested/traced.
- [Cardinal roll clip](../artifacts/unreal/warden-rolls-cardinal.mp4) and [diagonal roll clip](../artifacts/unreal/warden-rolls-diagonal.mp4): four normal requests per clip, all eight directions represented. Actual trace confirms 300 cm per roll, ordinary stamina, and exactly ages 4–17 protected. HUD derives protection directly from combat state. Directions are world-relative labels in this scripted study, not a demonstration of keys physically pressed.
- Each clip: 180 fresh unique engine frames, independently encoded/decoded, six seconds, 720p, fixed 30 Hz, no audio. All three chronological contact sheets per clip (48 sampled frames each) inspected. Body turns into the tumble and returns to its prior facing; protected/vulnerable labels appear. Not continuous audiovisual playback or FPS evidence.

The first capture CSV validator incorrectly omitted the preceding ready-state regeneration tick when comparing stamina snapshots. Runtime capture succeeded. The validator was corrected to apply the existing 26/60 regeneration capped at 100 before the next cost; all traced rolls then verify a cost of 28. `rolls-validator-failure.json` and the first validator are preserved. No game rule or test threshold changed for this correction.

## Remaining limits and next action

Owner has not approved the overall animation. Procedural tuck/landing, fast turn-back during recovery, support/weight transfer, locomotion transitions, fingers/cape and close-range silhouette overlap still need polish. Flat-floor clearance correction is not general terrain IK. Only this prototype's rules are verified; no exact Souls reproduction or animation-quality guarantee.

No fresh FPS benchmark in this roll-only pass. Last stiffness-pass run was 53.9 FPS mean, p95 29.6155 ms at 720p; previous 59.7 and slower runs remain historical. Fixed-step video is not performance evidence. Current work stays below the 10 GB ceiling and above the 24 GiB reserve.

Launch: `./scripts/bosslab-unreal package-play`. Hold W/A/S/D or a diagonal combination and press Space; Tab toggles target lock. Space with no direction retains the prototype backward roll. Next action: owner reviews all-direction roll readability, then refine landing/turn-back and full-body weight transfer without introducing AI or final models.

Evidence under `artifacts/unreal/`: `rolls-native-tests.json`, `rolls-packaged-tests.json`, process reports, both `rolls-*-manifest.json`, CSV traces/raw frames/review sheets and MP4 encode/decode reports; `rolls-final-audit.json`. Source/config/docs checkpoint: `checkpoint-2026-11-03-directional-rolls.tar.gz`. Previous checkpoints and rejected animation evidence preserved. No new models, RL, adaptation, deployment or persistent jobs.
