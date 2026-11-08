"""One-shot editor bootstrap: create only the project's disposable U0 map."""
import json
from pathlib import Path
import unreal

path = '/Game/BossLab/Maps/MCPProof'
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
unreal.log('BossLab subsystems: ' + repr([(str(c), str(unreal.get_editor_subsystem(c))) for c in [unreal.LevelEditorSubsystem, unreal.EditorActorSubsystem, unreal.UnrealEditorSubsystem]]))
assets = unreal.EditorAssetLibrary
if assets.does_asset_exist(path):
    assert levels.load_level(path), 'Could not load existing project proof map'
else:
    assert levels.new_level(path), 'Could not create clean project proof map'
assert levels.save_current_level(), 'Could not save proof map'
report = {'map': path, 'saved': assets.does_asset_exist(path), 'engine': unreal.SystemLibrary.get_engine_version()}
root = Path(unreal.Paths.project_dir()).resolve().parents[1]
(root / 'artifacts/unreal/map-bootstrap.json').write_text(json.dumps(report, indent=2))
unreal.log('BossLab preflight map ready: ' + json.dumps(report))
