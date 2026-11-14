# Windows handoff — 2026-11-14

**A Git pull is not enough to play the current 3D game.** This repository contains source, selected assets and the new interface assets, but no Windows executable. No Windows build or clean-clone Unreal run has been verified. The current local build is UE 5.8.4 on Apple Silicon macOS.

## To develop and build on Windows

1. Install Git and a compatible Windows Unreal Engine installation. The project declares engine association `5.8`; match the verified version where available. Check that the plugins listed in `unreal/BossLabWarden/BossLabWarden.uproject` are available, including its editor tool plugins.
2. Install the Visual Studio C++ game-development workload, MSVC toolchain and Windows SDK supported by that engine version. Follow [Epic's Visual Studio setup guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-visual-studio-development-environment-for-cplusplus-projects-in-unreal-engine); this document does not claim a tested Windows toolchain combination.
3. Restore Epic mannequin dependencies from your own Unreal template installation, using the manifest and destination described in [UNREAL_RESTORE.md](UNREAL_RESTORE.md).
4. Transfer the current generated game assets separately from the original workstation, preserving their paths under `unreal/BossLabWarden/Content/BossLab/`: `Anim`, `Dungeon`, `Effects`, `Regent`, `Revamp`, `Sound`, `Sword`, and `SwordGen`. These are local-only, not included by this push. The repository's generation/import scripts are development workflows, not a complete one-click asset restore. Some depend on external services or licensed source inputs. Transferring existing approved assets avoids regeneration; do not assume a fresh clone matches the current game visually or audibly.
5. Generate/build the project's **Development Editor / Win64** target using the installed Unreal/Visual Studio workflow. Open `BossLabWarden.uproject`, then validate the frontend, assets, controls, sound and combat on Windows. Resolve any platform/plugin issues before calling it supported.

The current `scripts/bosslab-game` and `scripts/bosslab-unreal` launch/build/package routes are Mac-specific. Installing Git Bash or setting `BOSSLAB_UE_ROOT` alone does not fix their hard-coded Mac targets, binaries and `.app` paths. Windows launch/packaging support remains work to do. The local game wrapper selects the `revamp` outfit, `regent` boss, `dungeon` arena and performance preset; those options must be carried into a future Windows launch path.

No Hugging Face token, model download or model server is needed **at runtime** once the game assets are present. Boss combat remains an authored fixed rehearsal; asset generation is separate from combat AI.

## To just play

The intended easy route is a separately built and tested **Windows packaged game**: download it, extract it, install bundled prerequisites if needed, and launch the `.exe`. Players would not need Unreal Editor or Visual Studio. Such a package has **not** been produced, uploaded or tested yet. The existing Mac package cannot run on Windows and predates the new frontend.

The older browser reference is a different game and does not substitute for Windows verification of the Unreal prototype.
