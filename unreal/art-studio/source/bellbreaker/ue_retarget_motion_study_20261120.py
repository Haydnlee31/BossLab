"""Import selected HY performances and retarget them to the existing forge skeleton."""
import json
import traceback
from pathlib import Path
import unreal

root = Path(__file__).resolve().parents[4]
folder = root / 'artifacts/unreal/bellbreaker-refit-20261120/motion'
base = '/Game/BossLab/Bellbreaker/MotionStudy20261120'
assets = unreal.EditorAssetLibrary
report = {'clips': [], 'ok': False}
try:
    choices = json.loads((folder / 'chosen.json').read_text())
    source = unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
    target = unreal.load_asset('/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig')
    retargeter = unreal.load_asset('/Game/BossLab/Bellbreaker/Anim/RTG_MannyToBellbreaker')
    assert source and target and retargeter
    for filename, selections in choices.items():
        source_path = base + '/Source/' + Path(filename).stem
        existing = [str(a).split('.')[0] for a in assets.list_assets(source_path, recursive=False)] if assets.does_directory_exist(source_path) else []
        if any(not any(p.endswith(suffix) for p in existing) for suffix in selections):
            opts = unreal.FbxImportUI()
            opts.import_mesh = False
            opts.import_as_skeletal = opts.import_animations = True
            opts.import_materials = opts.import_textures = False
            opts.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION
            opts.skeleton = source.get_editor_property('skeleton')
            anim = opts.anim_sequence_import_data
            anim.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
            anim.set_editor_property('import_bone_tracks',True)
            anim.set_editor_property('remove_redundant_keys',False)
            task = unreal.AssetImportTask()
            task.filename = str(folder / filename)
            task.destination_path = source_path
            task.replace_existing = True
            task.options = opts
            task.automated = task.save = True
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        assets.save_directory(source_path, only_if_is_dirty=False, recursive=True)
        paths = [str(a).split('.')[0] for a in assets.list_assets(source_path, recursive=False)]
        assets.make_directory(base + '/Anim')
        for suffix, alias in selections.items():
            path, = [p for p in paths if p.endswith(suffix) and not p.rsplit('/',1)[-1].startswith('BB_')]
            destination = base + '/Anim/' + alias
            if not assets.does_asset_exist(destination):
                batch = unreal.IKRetargetBatchOperation
                made = batch.duplicate_and_retarget([assets.find_asset_data(path)], source, target, retargeter, '', '', 'BB_', '')
                result, = [str(a.get_editor_property('package_name')) for a in made]
                assert assets.rename_asset(result, destination)
            clip = unreal.load_asset(destination)
            assert isinstance(clip, unreal.AnimSequence)
            assert clip.get_editor_property('skeleton') == target.get_editor_property('skeleton')
            assert clip.get_play_length()>3.5
            assert assets.save_loaded_asset(clip, False)
            report['clips'].append({'from': path, 'asset': destination, 'duration': clip.get_play_length()})
    report['ok'] = bool(report['clips'])
except Exception:
    report['error'] = traceback.format_exc()
(folder / 'ue-study-import-report.json').write_text(json.dumps(report, indent=2))
unreal.log('BOSSLAB motion import ' + str(report))
unreal.SystemLibrary.quit_editor()
