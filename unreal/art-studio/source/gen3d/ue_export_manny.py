"""Export SKM_Manny_Simple (mesh + skeleton) to FBX and its bone order to JSON."""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
OUT = os.path.join(ROOT, 'artifacts/art/claude-revamp-2026-11-09/rig')
mesh = unreal.load_asset('/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple')
task = unreal.AssetExportTask()
task.object = mesh
task.filename = os.path.join(OUT, 'manny.fbx')
task.automated = True
task.replace_identical = True
task.prompt = False
opts = unreal.FbxExportOption()
opts.ascii = False
opts.export_morph_targets = False
opts.level_of_detail = False
opts.collision = False
task.options = opts
ok = unreal.Exporter.run_asset_export_task(task)
skeleton = mesh.get_editor_property('skeleton')
bones = []
i = 0
while True:
    n = skeleton.get_bone_name(i) if hasattr(skeleton, 'get_bone_name') else None
    if not n or str(n) == 'None':
        break
    bones.append(str(n)); i += 1
json.dump({'export_ok': bool(ok), 'bones': bones}, open(os.path.join(OUT, 'manny-bones.json'), 'w'), indent=1)
unreal.log('BOSSLAB manny export ok=%s bones=%d' % (ok, len(bones)))
unreal.SystemLibrary.quit_editor()
