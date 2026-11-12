"""Import the layered game sound set (make_game_audio.py) to /Game/BossLab/Sound.

Run: ./scripts/bosslab-unreal python unreal/art-studio/source/audio/ue_import_game_audio.py
Input: artifacts/audio-2026-11-12/out (<Name>_<n>.wav). Ambience beds (Amb*) are set to loop.
Local, not committed, like the other imported assets. The game picks a random variation per
play (AWardenArenaMode::PlaySfx) and falls back to the older single sounds when absent.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
SRC = os.path.join(ROOT, 'artifacts/audio-2026-11-12/out')
DEST = '/Game/BossLab/Sound'
tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
if eal.does_directory_exist(DEST):
    eal.delete_directory(DEST)
tasks = []
for wav in sorted(os.listdir(SRC)):
    if not wav.endswith('.wav'): continue
    t = unreal.AssetImportTask()
    t.filename = os.path.join(SRC, wav); t.destination_path = DEST; t.destination_name = os.path.splitext(wav)[0]
    t.automated = True; t.replace_existing = True; t.save = False
    tasks.append(t)
tools.import_asset_tasks(tasks)
done, loops = [], []
for t in tasks:
    sound = unreal.load_asset(f'{DEST}/{t.destination_name}')
    if not sound: continue
    if t.destination_name.startswith('Amb'):
        sound.set_editor_property('looping', True); loops.append(t.destination_name)
    done.append(t.destination_name)
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
report = {'imported': len(done), 'loops': loops}
json.dump(report, open(os.path.join(ROOT, 'artifacts/audio-2026-11-12/import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB game audio import ' + json.dumps(report))
