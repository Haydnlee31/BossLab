# BossLab: The Warden — greatsword fundamentals

The owner deferred adaptive AI. This revision uses original Ashbound armor/Oathwake over the Epic player rig, the existing boss placeholder, two-handed greatsword poses and a clearly labeled fixed boss rehearsal in the enclosed sanctuary. No API key, Aura subscription, model server, network inference or download is required.

From `/Users/haydn/Documents/BossLab`:

```sh
./scripts/bosslab-unreal doctor
./scripts/bosslab-unreal package-play
```

The staged Development app is signature-verified and passes 18 graphical cooked checks. Previous physical controls were owner-confirmed; the outfit revision was verified through automated tests and actual runtime captures. The final package command stopped at the storage reserve; the matching staged app was independently verified afterward. `play` remains the compiled editor-executable fallback. The launcher stops on Ctrl-C, at 30 minutes, at 10,000,000,000 bytes under `unreal/`, or below 24 GiB free. No auto-start service is created. Keep the generated `unreal/Package/Mac/` folder intact; local Development packaging is not notarized public distribution.

| Control | Action |
|---|---|
| Enter | Start from title |
| WASD / mouse | Move / orbit camera |
| Tab or middle mouse | Target lock on/off |
| J or left mouse | Committed two-handed greatsword cut |
| Space | Directional roll; backwards without movement input |
| Hold left/right Shift + movement | Sprint while ready; 1.5× normal speed, 12 stamina/s |
| E | Committed heal, three charges |
| P or Escape | Pause/resume; releases the cursor and shows Resume / Quit |
| Q while paused | Quit game; inactive during play |
| R | Fresh encounter; second press confirms during a live fight |
| I | Controls and actual grip diagnostics |
| F5 | Fixed boss rehearsal / practice dummy; confirms and resets |
| F6 | Human / visibly labeled development test pilot; confirms and resets |
| F1 | Compact HUD |
| F2 | Reduced damage flash |
| F3 | Actual blade-contact geometry |
| F4 | Mouse sensitivity .5× / 1× / 1.5× |
| M | Mute/unmute subsequent sound cues |
| F9 | Export actual encounter state |
| F10 | Pause and capture actual PNG plus state JSON |

F7 adaptive demo is inactive. Tab no longer opens the inspector. Project config removes inherited Unreal debug bindings that conflicted with F1–F5/F9. The active inspector is a controls/pose panel; it does not present learning evidence.

Player cut: 30 anticipation, 20 contact, 36 recovery ticks; 32 damage and 22 stamina. Roll: 36 ticks, 300 cm maximum travel before collision, 14 invulnerable ticks, 28 stamina. Eight-tick post-action gap; a twelve-tick (200 ms) input buffer accepts late inputs without canceling commitments. Fixed 60 Hz simulation owns movement, timing and damage. Collision sweeps five samples along the actual rendered blade and checks wall occlusion. Each attack damages at most once. Death cancels actions and prevents healing resurrection.

Current gameplay rework: actual locomotion playback, acceleration/braking, eased roll travel, directional tuck/landing, hit recoil and death collapse. Player damage interrupts into an 18-tick hurt; each third boss hit breaks poise for 36 ticks. Boss poise resets after 300 damage-free ticks. Close lock framing eases toward the pair midpoint with wider arm and oblique orbit; camera ignores fighters but retains walls. Moving-strike support anchors/reach correction reduce foot skating; contact overlap can remain. These are explicit fixed combat rules, not learning. Current evidence: [REFINEMENTS_2026-11-06.md](REFINEMENTS_2026-11-06.md); previous gameplay work: [GAMEPLAY_REWORK.md](GAMEPLAY_REWORK.md).

The Warden repeats broad sweep → held overhead → rising cleave with committed aim and fixed rules. It approaches using ordinary visible distance. This is an authored rehearsal controller, with no opponent modeling, adaptive selection, RL or LLM inference. Old policy code and unarmed evaluation remain historical, inactive evidence.

Useful commands:

```sh
./scripts/bosslab-unreal build
./scripts/bosslab-unreal test
./scripts/bosslab-unreal capture
./scripts/bosslab-unreal package
./scripts/bosslab-unreal package-test
./scripts/bosslab-unreal package-play
./scripts/bosslab-unreal package-benchmark
```

`test` runs 18 gameplay/outfit checks plus three editor/preflight checks (21 total). `package-test` runs the 18 gameplay/outfit checks with rendering enabled: runtime mesh resources require a renderer. The launcher requires fresh passing JSON, because Unreal can exit 0 after a failed test. `evaluate` is explicitly deferred in this revision; old held-out scenarios are preserved and have not been retuned.

`capture` records 180 actual 1280×720 frames at fixed 30 Hz; this is not a rendering benchmark. `package-benchmark` measures wall-clock frame intervals in an actual 1920×1080 window over 60 simulated seconds after warmup, with a labeled test pilot and disclosed round resets. Do not compile or capture simultaneously. See [FUNDAMENTALS.md](FUNDAMENTALS.md) for actual evidence and limits.

Editor evidence: `artifacts/unreal/`. Packaged saves stay inside the macOS app container; the launcher copies them to `artifacts/unreal/packaged-runtime/` on exit. App sandbox remains enabled. The packaged optional HTML report template is absent; the actual fresh JSON report is valid and checked separately. Native Epic MCP is available only through the explicit bounded `editor` command; no custom Aura clone was needed.

No native RL training or model adapter is connected. The original browser PPO is a separate headless smoke experiment and cannot control this fight. Final art, finger/detail refinement, human combat-feel sessions, audio-quality assessment, gamepad/mobile, open world and public deployment remain outside this verified prototype.

Rendering presets are launch-local and reversible, not machine settings. `BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-play` reduces internal render scale to 75%, uses one 512px shadow cascade, disables ambient occlusion and caps at 60 FPS; it does not promise that rate. Balanced remains the default. `BOSSLAB_QUALITY=original ./scripts/bosslab-unreal package-play` uses the original shadows. `package-benchmark 720p` measures the default window; `package-benchmark profile` enables a bounded 1,200-frame built-in CSV capture. `package-capture` records 180 real frames from the standalone package. Frame directories are reusable: preserve/rename existing frames before another capture. Historical fundamentals performance was approximately 39.7 FPS mean at 720p and 42.4 at 1080p in separate shared-machine runs, with significant spikes; do not infer stable 60 FPS or a resolution speedup.

## Historical animation refinement evidence

`./scripts/bosslab-unreal package-capture motion` runs a labeled isolated motion study against a passive dummy: two swings and side/back rolls through normal action acceptance/stamina. It uses a diagnostic camera only; normal game framing is unchanged. Both capture modes overwrite the reusable raw capture folder, so preserve existing frames before rerunning. At that revision: native 11/11, cooked 8/8. Latest benchmark and clips: [ANIMATION_REFINEMENT.md](ANIMATION_REFINEMENT.md); older performance numbers above are historical.

Historical stiffness correction: [ANIMATION_FLUIDITY.md](ANIMATION_FLUIDITY.md), native 11/11 and packaged 8/8. Earlier clips/performance above remain historical.

Historical directional-roll pass: [SOULS_COMBAT_RESEARCH.md](SOULS_COMBAT_RESEARCH.md). **W/A/S/D plus Space**, including diagonal combinations; **Tab** toggles lock. No-direction Space remains backward roll. Native 13/13, cooked 10/10. `package-capture rolls-cardinal` and `package-capture rolls-diagonal` produce disclosed normal-cost studies with real protection labels/CSV. Preserve the reusable capture folder before rerunning.

`package-capture exchange` records a disclosed 24-second / 720-frame actual fight and per-tick state CSV. Capture is fixed 30 Hz with no audio; use the separate real-time benchmark for FPS. Current human-review evidence is in [REFINEMENTS_2026-11-06.md](REFINEMENTS_2026-11-06.md); historical appendices above do not certify this revision.

Historical November4 performance was inconsistent: performance preset40.95 then26.53 FPS mean; balanced25.23. `BOSSLAB_QUALITY=minimal` is a diagnostic (50%scale,no shadows/AA/bloom);31.61FPS with spikes and poorer visual grounding, not a recommended review mode. See the complete current performance ledger in GAMEPLAY_REWORK.md.

Historical pre-outfit2026-11-06 performance preset720p: baseline58.49 and final59.44FPS mean; finalp95 16.8215ms,6/3253 frames above33.3ms. Recommended review launch is `BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-play`. Native18/18,cooked15/15; candidate ready for focused human review, with overall animation acceptance and longer-session stability pending. No locked60 guarantee.

## Prior controls and animation research

[Controls evidence](CONTROLS_2026-11-06.md): native 20/20, cooked 17/17. Sprint starts with at least 10 stamina; exhaustion requires releasing Shift before restarting. Stationary Shift costs nothing; sprint cannot cancel a committed roll/attack/heal. Esc/P pauses and releases the cursor; click Resume/Quit or use Esc/P and Q. Pause clears held movement, sprint and queued actions. Actual keyboard pause/resume/quit was verified; the owner subsequently confirmed physical Resume, Shift sprint and Quit work. Earlier automation supplied stale mouse coordinates and no Shift event; those attempts remain failed automation checks.

[Animation research](ANIMATION_WORKFLOW_RESEARCH.md) records a full-body authoring workflow and source-grounded diagnosis. Boss swing poses are unchanged this pass; previous artistic acceptance gates remain open.

## Current outfit and performance

[Outfit delivery](PLAYER_OUTFIT_IMPLEMENTATION.md): original26-part armor/sword, 15,448 triangles; native21/21 and cooked18/18. First stylized pass with rigid clothing; final garment skinning, fur, texture detail and finger polish remain open. `package-capture outfit` records four inspection angles and exports the static OBJ assembly. Captures use a capture-only PSO proxy override; normal play/benchmark retains the default and can show brief startup warmup.

Final single-instance720p performance preset: **59.07FPS mean,16.7936ms p95**,11/3233frames>33.3ms. Initial37.88/profiler38.19FPS runs had a second game open; owner authorized its closure before retesting the unchanged build. Short-session review is supported, locked60 is not claimed. Use `BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal package-play` for review, without a performance guarantee. No new training or model connection.
