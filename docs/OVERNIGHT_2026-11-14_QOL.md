# Overnight 2026-11-14: quality-of-life features

Quality-of-life agent, 03:59-04:50 +08. Each feature is a separate commit so the owner can keep
or revert it on its own (`git revert <hash>`). Revert in reverse order (later commits build on the
Options panel and `WardenQoL.cpp`). None of these change combat rules, timing or damage in
`WardenCombat`; the default game plays the same except for the camera-follow option (on by default,
requested by the lead) and the extra HUD lines.

**Verification:** native automation tests and a clean build only. No feature here was tried with
real keyboard/mouse input or watched in a running game. The Slate menus have not been seen on
screen. Owner play-testing is still needed for all of them.

Already there before tonight (left as is): R restarts after death/victory (and asks to confirm
mid-fight), M mute, F4 cycles sensitivity, Esc/P pause menu with Resume/Quit.

## 1. Options panel with saved settings, H toggles hints (`0e88254`)

- Pause menu (Esc/P) now has an **OPTIONS** block. Each row has `<` / `>` buttons: mouse
  sensitivity (0.25-3x), invert look Y, camera distance (70-150 % of the 500 cm arm), master /
  music / effects volume, damage numbers on/off, control hints on/off.
- **H** (new binding; H was unbound) shows or hides the two control-hint lines at the bottom of the HUD.
- Saved to `Saved/Config/BossLabSettings.ini` in the project's Saved directory (for editor-game
  that is `unreal/.cache/unreal-user/Saved/...`). Nothing machine-wide. Tests, captures
  (`-BossLabCapture`) and benchmarks ignore the saved file and use the defaults, so evidence stays
  comparable.
- Defaults match the old game exactly. Master volume uses the audio device's transient primary
  volume. Effects scale `SfxMaster` (default 2.5). Music scales `MusicLevel()`. Ambience beds
  follow master volume only.
- Known limitation: F4 still cycles sensitivity directly. Its value is not saved, and the next
  Options change overwrites it with the panel's value.
- Tested by `BossLab.QoL.SettingsPersistAndApply` (defaults, save/load round trip, clamping, H bound
  once with no other action on it, values reach the player and the mix).

## 2. Fight timer, attempt counter and death recap (`712a4e3`)

- Top right during a human fight: `TIME m:ss | ATTEMPT n`.
- Results screen adds `Killed by: <boss move name or hazard>` with the boss health left, and a
  session line: attempts, deaths, victories, best (lowest) boss health, fastest win.
- "Killed by": a blade hit uses `WardenRules::Strike(boss move).Name`. Regent magic or hazards use
  the first sentence of the hit event (for example "Caught in the Funeral Pyre").
- Only human attempts count. Demo, the F6 scripted pilot and captures are skipped. Records last for
  the session only and are not saved.
- Tested by `BossLab.QoL.AttemptsAndDeathRecap`.

## 3. Camera follow: spring-arm lag + idle re-centre (`cdb3bd0`)

- Requested by the lead (research doc `docs/research/ELDEN_RING_COMBAT_2026-11-14.md`, rec. #3).
  Options row "Camera follow (lag + re-centre)", **default ON**. Switching it off restores the old
  camera exactly.
- Spring-arm lag: speed 11, max 60 cm. After about 1 s with no mouse look, while unlocked and
  moving faster than 60 cm/s, the camera yaw eases behind the player's heading. It ramps up to
  60 deg/s. It does nothing when the heading is more than 100 deg away, so it never swings round
  while you run toward the camera. Pitch, lock-on framing and the 500 cm arm are unchanged.
- Only applied through the game mode's `ApplySettings`. Bare fighters in other tests keep the old
  camera, and `CloseCameraFullBodyFraming` and wall-retraction still pass.
- Tested by `BossLab.QoL.CameraRecentreBehindHeading` (off: yaw untouched; on: eases to the heading;
  standing still: no change; running toward the camera: no 180 deg swing). How it feels is unverified.

## 4. Practice options (`92f772b`)

- Pause menu **PRACTICE** block (session only, never saved, everything **default off**):
  - *Infinite health*: the player is refilled to full before each fixed step resolves, so hits
    still flinch but chip damage never kills. A single hit over 100 would still kill; no current
    move does that. The HUD shows `PRACTICE / INFINITE HEALTH` in red while it is on.
  - *Start at second phase* (Regent only): the next restart opens at the phase threshold. This is the
    same as `BOSSLAB_REGENT_PHASE=2`.
  - *Restart fight now*.
- The pause menu was widened to 860 px with Options beside Practice (same commit).
- Practice attempts show `PRACTICE (not recorded)` and never set deaths, best health or fastest win.
  The command-line phase-two start also counts as practice.
- Tested by `BossLab.QoL.PracticeOptionsOptInAndUnrecorded` (defaults off, the default game does not
  refill, practice refills and is marked, no records, the phase-two start opens at 300 hp).

## Test results

Native suite at the last commit: 39/39 pass, 0 failed (35 before tonight plus 4 new `BossLab.QoL.*` tests). The suite passed before each commit: 36, 37, 38, then 39. The only warning is an existing
`LogHttp ... generate_204` timeout logged inside `BossLab.Regent.SequenceBudgetAndDeterminism`
(network check, not related to these changes).

## Not verified / open

- None of the UI has been seen on screen or clicked with a real mouse. The pause menu is now
  860 px wide, with Options on the left and Practice on the right (changed in `92f772b`) so it should
  fit at 720p. Layout and readability are unchecked.
- Camera follow feel (lag speed, re-centre delay and rate) needs owner tuning.
- Volume sliders have not been listened to.
