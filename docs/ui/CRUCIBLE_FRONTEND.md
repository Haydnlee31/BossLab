# BossLab — The Crucible front end

Owner request 2026-11-14: a real game home, expandable boss roster, organised settings, distinct Challenge/Creative modes and Challenge victory statistics.

Visual system: ink-blue black, warm ivory, antique gold, sparing soul blue. Broken-seal sword emblem and a spaced BossLab wordmark. Cinematic 1440×900 logical foreground scales to the viewport over full-bleed artwork; settings scroll in a quiet left column. Separate screens avoid the old crowded pause menu. Native Slate buttons support focus; player-facing screens use no browser or remote service.

Flow: Home → Challenge → Funeral Regent → fight → result → retry/home. Two noninteractive Coming soon labels reserve future roster slots without pretending other bosses exist. Home → Creative → assists → fight. Pause → Settings or (Creative only) assists. Esc returns from subpages, resumes from pause, and does not bypass home/results.

Challenge: normal full-health Regent, no assistance, fixed authored rehearsal. Track simulation fight time, damage dealt/taken, hits taken and consumed flasks. Records are session-local. Creative is unranked even with all assists off; infinite health/stamina and phase-two start are session options. Starting Challenge clears assists. Debug/pilot paths do not establish eligible challenge wins. Generated assets/animations are not runtime boss AI.

Launch current local editor-game build with `./scripts/bosslab-game`. This wrapper selects revamp characters, Regent and dungeon with the performance preset; the original development launcher and packaged app remain separate. Generated game assets remain local. No Hugging Face call or token required by the UI.

Validation results will be recorded in docs/STATUS.md after build and inspection. This document does not itself claim passing tests or owner acceptance.

## Verification completed

Two native suites:40/40 each, zero failed/notRun. Final layout-only rebuild succeeds. Actual keyboard navigation across home/roster/creative/settings, launch into Challenge, real defeat statistics and clean quit inspected. Native test fixtures verify eligible victory stats and Creative exclusion; no human victory claim. Settings category headings and final home inspected in the live window. Engine F10 captures at720p compress multiline text spacing compared with the Retina window; retained honestly as capture limitation. Desktop synthetic mouse clicks did not reliably activate buttons, so physical mouse acceptance is pending. No frame-rate measurement or packaged delivery in this pass.

Launch `./scripts/bosslab-game`. Menu keyboard: Tab moves focus, Enter/Space activates, Esc backs out/resumes. Gameplay controls remain WASD, mouse, Shift sprint, Tab lock, Space roll, LMB attack, F jump, E heal, Esc pause.

## Cinematic revision after owner rejection

The first panel-based design was rejected as dashboard-like. Replaced with fullscreen illustrated environments, Cinzel display typography, transparent navigation, gold focus diamonds, a large Regent key-art selection page, and ceremonial centered results with five horizontal statistics. Settings/practice controls now share the same style. There are no looping transitions or navigation delays. Applied local emil-design-eng and animate skill principles to native Slate.

Actual Hugging Face FLUX.1-schnell generated two1536×864 images (seeds47/53,4steps); prompts, original returnedWebP, runtimePNG and provenance under artifacts/ui/cinematic-2026-11-14. FLUX produced artwork; C++design/interaction implementation is authored locally. Regent art is illustrative and differs in weapon/hand detail from the built model. No token persisted, no runtimeHFdependency, no combatAI change. Cinzel/OFL bundled in Content/UI/Fonts.

Final build succeeded without the earlier deprecated font-constructor warnings. Native40/40,0warnings/failures/notRun. Live Retina inspection: Home, Regent selection, Settings, Creative, pause, challenge start, actual defeat and returnHome. Real defeat snapshot545ticks,100damage taken,6hits,0flasks. R in Settings stays in Settings; ineligible wins now use EncounterComplete rather than falsely reporting death. Challenge success/Creative exclusion remains covered by state fixtures, not a human win.

Engine captures saved as home.png,regent-selection.png,settings.png,creative.png,defeat-result.png in the evidence directory. Live UI is the visual inspection authority; F10's720p output can compress multiline type spacing. Physical mouse review remains open: desktop synthetic clicking did not reliably activate. No package update or FPS claim. Records remain session-local. Final project-only focus configuration suppresses engine blue rectangles while retaining explicit gold focus on controls.
