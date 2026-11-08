"""One-shot, project-local U1 arena setup; no background service."""
import json
from pathlib import Path
import unreal
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
path = '/Game/BossLab/Maps/Arena'
if unreal.EditorAssetLibrary.does_asset_exist(path):
    assert levels.load_level(path)
else:
    assert levels.new_level(path)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
mode = unreal.load_class(None, '/Script/BossLabWarden.WardenArenaMode')
assert mode
world.get_world_settings().set_editor_property('default_game_mode', mode)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
starts = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.PlayerStart)]
if not starts:
    start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-450,0,95))
    start.set_actor_label('BossLab_PlayerStart')
assert levels.save_current_level()
blend = unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/BS_Idle_Walk_Run')
report = {'map': path, 'saved': True, 'game_mode': str(mode), 'blend_space_loaded': bool(blend)}
try:
    report['blend_parameters'] = [{'name': str(p.get_editor_property('display_name')), 'min': p.get_editor_property('min'), 'max': p.get_editor_property('max')} for p in blend.get_editor_property('blend_parameters')]
    report['samples'] = [{'animation': str(s.get_editor_property('animation')), 'value': str(s.get_editor_property('sample_value'))} for s in blend.get_editor_property('sample_data')]
except Exception as error:
    report['asset_inspection_error'] = str(error)
root = Path(unreal.Paths.project_dir()).resolve().parents[1]
(root / 'artifacts/unreal/arena-bootstrap.json').write_text(json.dumps(report, indent=2))
unreal.log('BossLab arena ready: ' + json.dumps(report))
