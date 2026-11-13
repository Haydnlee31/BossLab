# Overnight run, 2026-11-14 (03:59–04:40 +08): what to keep or drop

The run used three agents: research, graphics and quality of life (QoL). The lead also made one change. Every feature is its own commit on `regent-moveset-01`, and nothing is pushed. To drop a feature, revert its commit, newest first within each group, because later QoL commits build on `0e88254`. All of it is presentation or UI only: combat rules and timing are unchanged.

## Verification

- **Tests:** native suite 39/39. That is the 35 existing tests plus 4 new `BossLab.QoL.*` tests. One test logs an unrelated HTTP-timeout warning.
- **Real input:** nothing has been tried with real keyboard and mouse input. The menus have never been seen on screen.
- **Performance:** all benchmarks ran on a shared, loaded machine.

## Research

- **Document:** [research/ELDEN_RING_COMBAT_2026-11-14.md](research/ELDEN_RING_COMBAT_2026-11-14.md), with sourced comparisons and a top-10 list.
- **Rules:** our rules already match the Elden Ring frame data, as far as community sources go (roll i-frames, stamina, buffering).
- **Stiffness causes:**
  - no authored locomotion clips (sprint, start, stop or pivot);
  - the turntable roll;
  - a rigid camera;
  - a hit-stop that freezes everything.
- **Bigger next steps:** authored greatsword locomotion clips (these need an asset source and licence approval) and a replacement roll animation.

## Lead: pivot plant (`9781bf6`)

- **What:** when the player turns at the full 540°/s rate for 6 ticks while moving (a turn of more than about 90°), the hips drop 5 cm and the body leans against the facing the turn started from for about 0.2 s. The normal acceleration lean then pushes off into the new direction.
- **Evidence:** before and after sheets in `artifacts/art/overnight-2026-11-14/pivot/` (local).
- **How it looks:** subtle.

## Quality of life ([OVERNIGHT_2026-11-14_QOL.md](OVERNIGHT_2026-11-14_QOL.md))

- `0e88254` **Options panel:** sensitivity, invert Y, camera distance, three volumes, damage numbers and hints, saved to the project's `Saved/Config/BossLabSettings.ini`. **H** toggles the control hints.
- `712a4e3` **Fight record:** a fight timer, an attempt counter and a death recap ("Killed by …").
- `cdb3bd0` **Camera follow:** camera lag plus a gentle re-centre behind your heading. On by default; it can be turned off in Options.
- `92f772b` **Practice options:** infinite health, start at phase two, and restart now. All are off by default and never saved.

## Graphics ([OVERNIGHT_2026-11-14_GRAPHICS.md](OVERNIGHT_2026-11-14_GRAPHICS.md))

- **Commits:**
  - `210fe7f` volumetric fog shaft in the dungeon (about 2 ms);
  - `91e7f33` grade, bloom and contact shadows;
  - `63f609d` rim lights on both fighters;
  - `26d5b8c` hit sparks.
- **Total cost:** about 3.5–4 ms, measured on the loaded machine.
- **Toggle:** `BOSSLAB_GRAPHICS=off` turns all four off, or switch them off one at a time with, for example, `BOSSLAB_GRAPHICS=-volumetric,-rim`.

## Review command

```
BOSSLAB_OUTFIT=revamp BOSSLAB_BOSS=regent BOSSLAB_ARENA=dungeon ./scripts/bosslab-unreal play
```

To compare, add `BOSSLAB_GRAPHICS=off`.
