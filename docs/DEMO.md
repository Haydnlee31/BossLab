# Showcase procedure

Start `./scripts/bosslab demo`, open http://127.0.0.1:5173/?demo=1. Stop Ctrl-C. Use a desktop 16:9 browser. Tab shows the inspector, F1 hides diagnostic UI for recording, Escape pauses. Reduced motion is in pause settings. There is no audio.

The displayed player is a reactive script, not a human. It uses actual stamina, attacks once per punish opportunity when reserves allow, attempts real healing, and can die. It tries an early response at cue age 8, then later responses at wind-up minus 7. Failed/missed response opportunities are still counted honestly. The stage changes at **2,400 elapsed simulation ticks**, independent of health or boss success. Policy DTOs never contain this schedule.

At death/victory, the browser announces the result and pauses two real seconds before a new round. Both actors get ordinary starting resources; statistical evidence is explicitly retained. Resets appear in exported logs. Normal human restart clears evidence. Browser focus loss pauses simulation. Ninety simulation seconds may take longer than ninety wall-clock seconds with pauses/resets or a slow browser.

## 60–90 second storyboard

1. 0–12s: show the title and enter the demonstration; keep the SCRIPTED PLAYER label in view. Show amber cue and distinct quick/held attacks. Do not claim immediate learning at cold start.
2. 12–35s: reveal the actual inspector. After enough completed exchanges, show sample count, early estimate and selected-action distribution. Disclose any death/reset.
3. At 40 simulation seconds: show the script's visible switch to later timing. Nothing tells the boss to change its selection directly.
4. 40–70s: follow the actual evidence; later responses replace early estimates. At 60s in saved headless evidence, early fell to .141 and late rose to .735. The overhead utility contribution changed from +1.493 just before the switch to −.650. These are response estimates/utility contributions, not hit probabilities.
5. End: show the controller label and View saved comparison. Both controllers won 6/18; no win-rate advantage is established. PPO is a separate, small headless experiment, not the controller in this video.

Editing pauses for length is acceptable only with reset/controller transitions disclosed. Never imply a preselected successful outcome. To regenerate real demo evidence: `node scripts/demo-evidence.mjs` → `artifacts/demo-evidence.json`.

## Existing captured images

- `artifacts/title-1280x720.jpg`: genuine Chrome title view.
- `artifacts/demo-inspector-1280x720.jpg`: genuine active early-stage inspector.
- `artifacts/recording-1920x1080.jpg`: genuine recording layout during combat.
- `artifacts/defeat-1920x1080.jpg`: genuine idle human defeat/recap.

These are rendered screenshots, not generated concept art. No video recording was captured. Use your usual recorder while the local browser runs.
