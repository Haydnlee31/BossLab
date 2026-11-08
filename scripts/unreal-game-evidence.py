"""Read a real PIE pawn and request an engine-rendered gameplay screenshot."""
from pathlib import Path
import json
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
assert world, 'No running game world; cannot capture gameplay evidence'
pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
assert pawn, 'No possessed pawn'
root = Path(unreal.Paths.project_dir()).resolve().parents[1]
position = pawn.get_actor_location()
report = {'world': world.get_path_name(), 'pawn': pawn.get_path_name(),
          'position': {'x': position.x, 'y': position.y, 'z': position.z},
          'rotation': str(pawn.get_actor_rotation()),
          'controller': str(pawn.get_controller()),
          'time_seconds': unreal.GameplayStatics.get_time_seconds(world)}
(root / 'artifacts/unreal/u1-game-state.json').write_text(json.dumps(report, indent=2))
unreal.SystemLibrary.execute_console_command(world, 'viewmode lit')
unreal.SystemLibrary.execute_console_command(world, 'HighResShot 1 filename=' + str(root / 'artifacts/unreal/u1-gameplay.png'))
unreal.log('BossLab game evidence requested: ' + json.dumps(report))
