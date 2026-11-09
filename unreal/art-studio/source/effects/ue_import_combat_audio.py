"""Import the procedural greatsword cues (make_combat_audio.py) to /Game/BossLab/Effects/Audio.

Run: ./scripts/bosslab-unreal python unreal/art-studio/source/effects/ue_import_combat_audio.py
Local, not committed, like the other generated assets.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
SRC = os.path.join(ROOT, 'artifacts/art/overnight-2026-11-10/audio')
DEST = '/Game/BossLab/Effects/Audio'
tools = unreal.AssetToolsHelpers.get_asset_tools()
done = []
for wav in sorted(os.listdir(SRC)):
    if not wav.endswith('.wav'): continue
    t = unreal.AssetImportTask()
    t.filename = os.path.join(SRC, wav); t.destination_path = DEST; t.destination_name = os.path.splitext(wav)[0]
    t.automated = True; t.replace_existing = True; t.save = True
    tools.import_asset_tasks([t]); done.append(t.destination_name)
unreal.log('BOSSLAB combat audio import ' + json.dumps(done))
