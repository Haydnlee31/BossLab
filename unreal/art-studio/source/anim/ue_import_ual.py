"""Import the retargeted Quaternius UAL clips (retarget_ual.py) as AnimSequences on SK_Mannequin.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/anim/ue_import_ual.py
(the script quits the editor, so the launcher's exit 1 is expected). Input:
artifacts/art/anim-ual-2026-11-14/UAL_Anims.fbx (one take per clip). Writes
/Game/BossLab/Anim/UAL (local, not committed; CC0 source data, kept local like other assets).
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, 'artifacts/art/anim-ual-2026-11-14')
DEST = '/Game/BossLab/Anim/UAL'
eal = unreal.EditorAssetLibrary
if eal.does_directory_exist(DEST):
    eal.delete_directory(DEST)
ui = unreal.FbxImportUI()
ui.import_mesh = False; ui.import_as_skeletal = True; ui.import_animations = True
ui.import_materials = False; ui.import_textures = False
ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION
ui.skeleton = unreal.load_asset('/Game/Characters/Mannequins/Meshes/SK_Mannequin')
ad = ui.anim_sequence_import_data
ad.set_editor_property('animation_length', unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
ad.set_editor_property('import_bone_tracks', True)
ad.set_editor_property('remove_redundant_keys', False)
t = unreal.AssetImportTask()
t.filename = os.path.join(ART, 'UAL_Anims.fbx'); t.destination_path = DEST
t.automated = True; t.replace_existing = True; t.save = False; t.options = ui
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
report = {}
for path in eal.list_assets(DEST, recursive=True):
    a = unreal.load_asset(path)
    if isinstance(a, unreal.AnimSequence):
        report[a.get_name()] = round(a.get_editor_property('sequence_length') if hasattr(a, 'sequence_length') else unreal.AnimationLibrary.get_sequence_length(a), 3)
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'ue-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB ual import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
