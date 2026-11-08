# Restoring the Unreal project from a source checkout

This repository is a source handoff, not a self-contained packaged game or a clean-clone build certification. The working local prototype was tested on Apple Silicon macOS with installed Unreal Engine **5.8.4** and Xcode **26.1.1**. No fresh-clone build was performed for publication. Historical local test results in `docs/STATUS.md` do not establish that another engine version or operating system works.

## Public source boundary

Project-authored C++, `.uproject`, configuration, setup scripts, original `SourceAudio/*.wav`, original `/Game/BossLab` surfaces/map and the V13 geometry JSON can be handed off as project material, subject to the repository owner's chosen license. The original synthetic audio provenance and asset inventory are documented in `docs/UNREAL_ASSETS.md`.

**Excluded dependency:** `unreal/BossLabWarden/Content/Characters/Mannequins/` contains Epic template skeletal meshes, skeleton/physics asset, materials/textures, locomotion/idle and historical unarmed animations. They are not original BossLab art. This handoff conservatively excludes their raw files and restores them from the recipient's own installed Unreal template content. This document does not grant redistribution rights or resolve Unreal licensing for the recipient.

Also exclude installed engine/tool binaries, local Blender application, caches, Intermediate/Saved/Binaries directories, packaged apps and engine bundles. Do not publish the downloaded reference gameplay video or reference screenshots as original project assets. Existing local originals are preserved; publication exclusions are not deletion instructions.

Keep these two small provenance manifests in the checkout:

- `artifacts/unreal/asset-manifest.json` —49 original template files.
- `artifacts/unreal/physics-asset-manifest.json` —additional `PA_Mannequin` dependency.

Their recorded absolute source path is historical provenance, not the restore destination. On2026-11-09, read-only verification matched all50 installed source files and local copied files against the recorded SHA256 hashes:82,098,363 bytes. No engine files were modified.

## Prerequisites

1. Obtain and install Unreal Engine5.8.4 and its template resources through your own supported installation/access. This repository does not install or redistribute the engine. The installed version used here includes the `ModelContextProtocol`, `EditorToolset` and `AutomationTestToolset` editor plugins as well as PythonScriptPlugin, ACLPlugin, AnimationData and ControlRig listed in the `.uproject`. An installation missing those plugins is not equivalent; do not silently disable plugins and call that the verified setup.
2. On the verified Mac route, install a matching supported Xcode toolchain, Python3 and normal command-line build tools. Engine binaries are arm64. The launcher is currently Mac-specific: `Mac` targets, mac-arm64 DotNet, `.app` paths and macOS package handling are hard-coded. `BOSSLAB_UE_ROOT` relocates the engine but does **not** make the launcher portable to Windows/Linux. Those platforms require a separately implemented/tested launch/build path.
3. Keep the existing limits: under10,000,000,000 allocated bytes in `unreal/`, at least24GiB free throughout heavy work. Allow extra build headroom above that reserve; roughly0.9GB of local compiler intermediates were reclaimed and must regenerate, with additional shader/swap/temp demand possible. `doctor` reports storage but does not guarantee the next build will fit.
4. Clone this repository and run all following commands from its root. An API key or model server is not required. Adaptive boss AI/model adapters remain deferred.

Set the path to the engine root containing `Engine/` and `Templates/`:

```sh
export BOSSLAB_UE_ROOT="/absolute/path/to/your/UE_5.8"
./scripts/bosslab-unreal doctor
```

The original Mac installation default is `/Users/Shared/Epic Games/UE_5.8/UE_5.8`; do not assume that path exists on another machine.

## Restore the excluded Epic template subset

The exact installed source used was:

```text
$BOSSLAB_UE_ROOT/Templates/TemplateResources/High/Characters/Content/Mannequins/
```

Restore to **`Content/Characters/Mannequins`**, not `Content/Mannequins`: C++ and asset references use `/Game/Characters/Mannequins/...`. A different folder name breaks references.

The following explicit local-copy procedure validates all source hashes and existing destinations before copying. It downloads nothing, copies only the50 manifest entries, and refuses to overwrite a differing existing asset. It has been reviewed against the current manifest structure; the copy operation itself was not rerun during this publication assessment.

```sh
python3 - <<'PY'
import hashlib, json, os, shutil
from pathlib import Path

root = Path.cwd()
engine = Path(os.environ['BOSSLAB_UE_ROOT']).expanduser().resolve()
source = engine / 'Templates/TemplateResources/High/Characters/Content/Mannequins'
manifest = json.loads((root / 'artifacts/unreal/asset-manifest.json').read_text())
physics = json.loads((root / 'artifacts/unreal/physics-asset-manifest.json').read_text())
rows = manifest['files'] + [{
    'path': physics['destination'], 'sha256': physics['sha256'], 'bytes': physics['bytes']
}]
prefix = 'unreal/BossLabWarden/Content/Characters/Mannequins/'
checked = []
for row in rows:
    assert row['path'].startswith(prefix), row['path']
    relative = Path(row['path'][len(prefix):])
    assert not relative.is_absolute() and '..' not in relative.parts
    src, dst = source / relative, root / row['path']
    assert src.is_file(), f'Missing installed template resource: {src}'
    assert src.stat().st_size == row['bytes'], f'Size mismatch: {src}'
    assert hashlib.sha256(src.read_bytes()).hexdigest() == row['sha256'], f'Version/hash mismatch: {src}'
    if dst.exists():
        assert dst.is_file() and hashlib.sha256(dst.read_bytes()).hexdigest() == row['sha256'], f'Refusing to overwrite different asset: {dst}'
    checked.append((src, dst, row['sha256']))
for src, dst, digest in checked:
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest() == digest
print(f'Restored/verified {len(checked)} template assets from the installed engine.')
PY
```

If a file or hash differs, stop and resolve engine/template version provenance. Do not bypass the check by downloading mannequin assets from an arbitrary mirror or renaming unrelated animation assets. Current gameplay specifically loads:

```text
/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple
/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run
/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle
```

Restoring the whole recorded dependency subset is more reliable than copying only those three files. Historical unarmed attack sequences are retained dependencies/evidence; actual current greatsword/roll motion is project-authored C++.

## Build and start

With the dependency subset restored and original `Content/BossLab` assets present:

```sh
BOSSLAB_BUILD_JOBS=1 ./scripts/bosslab-unreal build
./scripts/bosslab-unreal test
BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

The default native test filter is `BossLab`. Dedicated `V13Trial` tests require their explicit flags/fixtures and are separate. The launcher writes project-local caches but installed UBT also uses its normal per-user trace/log location; do not redirect HOME or change global settings to bypass a permission failure.

For the optional actual V13 player costume trial, if its JSON is included:

```sh
BOSSLAB_OUTFIT=v13 BOSSLAB_QUALITY=performance ./scripts/bosslab-unreal play
```

This is an **editor-game** trial with a project-local JSON dependency. It uses rigid attachments and simplified materials, with known cloth/hand limitations. `BOSSLAB_OUTFIT=v13` is intentionally rejected with `package*` modes. No packaged executable is supplied in this source handoff. `package-play` cannot work on a fresh clone until a separate packaging task completes; historical local packaged-app verification is not a supplied binary.

Enter starts; WASD/mouse movement/camera, Shift sprint, Tab target, Space roll, left-click/J greatsword, E heal, Esc/P menu. Esc menu restores access to Resume/Quit. Game fundamentals and art acceptance remain incomplete; see current STATUS rather than old screenshots for limitations.

## If original BossLab binary assets are omitted or missing

The small original material/map/audio `.uasset` files are separate from the excluded Epic directory. Existing authoring scripts provide a recovery route, but this publication pass did not test rebuilding them from a fresh checkout:

```sh
./scripts/bosslab-unreal editor scripts/unreal-create-surfaces.py
# Inspect the editor log and saved surface/audio assets, then close this editor.
./scripts/bosslab-unreal editor scripts/unreal-setup-arena.py
# Inspect the arena-bootstrap report and saved map, then close this editor.
```

Build the C++ editor module first. These scripts run inside Unreal, not ordinary Python. The surface script creates `/Game/BossLab/Materials/M_WardenSurface` and eight instances and imports the original `SourceAudio/*.wav`; the arena script creates/loads `/Game/BossLab/Maps/Arena`, sets the project game mode and verifies locomotion load. They do not terminate the editor automatically. Keep one heavy job/editor instance at a time and inspect results before gameplay tests. Other helper scripts are historical diagnostics, not mandatory bootstrap steps.

## Portability and reproducibility limits

- `BOSSLAB_UE_ROOT`, `BOSSLAB_BUILD_JOBS`, `BOSSLAB_QUALITY` and `BOSSLAB_OUTFIT` are supported launcher settings; `BOSSLAB_V13_DATA` selects a local trial JSON. Paths inside old logs/manifests/docs may still identify the original workstation.
- The launch-only single-shader-worker configuration reserves seven cores and was verified on this eight-core Mac. Other core counts need review; it is not a universal worker-count abstraction.
- Art scripts may reference project-local Blender binaries, excluded saved scenes, packed image dependencies or earlier studies. Source availability alone does not make every historical render reproducible. Do not call the rejected Funeral Regent art studies integrated game assets.
- Map/material assets saved with the verified engine may not load in older versions. A newer engine may require project/plugin/source migration and fresh tests.
- No new build, test suite, rendering, benchmark or packaging operation was run for this restore document. The read-only50-file provenance check above is the only new asset-validation result.
