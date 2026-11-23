"""Import only the repaint as a sibling skeletal mesh. Keep the original rig and assets."""
from pathlib import Path
import unreal
import os,json,hashlib

root = Path(__file__).resolve().parents[4]
name = "SKM_BellbreakerForgeShoulder"
dst = "/Game/BossLab/Bellbreaker/ForgeShoulder"
original = unreal.load_asset("/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig")
original_skeleton = original.get_editor_property("skeleton")
options = unreal.FbxImportUI()
options.import_mesh = True
options.import_as_skeletal = True
options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
options.skeleton = original_skeleton
options.import_materials = False
options.import_textures = False
options.import_animations = False
options.create_physics_asset = False
sm = options.skeletal_mesh_import_data
sm.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
sm.set_editor_property("use_t0_as_ref_pose", False)
sm.set_editor_property("update_skeleton_reference_pose", False)
unreal.EditorAssetLibrary.make_directory(dst)
task = unreal.AssetImportTask()
task.filename = str(root/"artifacts/art/bellbreaker-shoulder-2026-11-20"/(name+".fbx"))
task.destination_path = dst
task.destination_name = name
task.options = options
task.automated = True
task.replace_existing = True
task.save = False
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh = unreal.load_asset(dst+"/"+name)
assert mesh and mesh.get_editor_property("skeleton")==original_skeleton
slots = original.get_editor_property("materials")
assert len(mesh.get_editor_property("materials"))==len(slots)
mesh.set_editor_property("materials", slots)
assert unreal.EditorAssetLibrary.save_loaded_asset(mesh, False)
receipt={"asset":dst+"/"+name,"source_fbx":task.filename,"fbx_sha256":hashlib.sha256(Path(task.filename).read_bytes()).hexdigest(),"skeleton":original_skeleton.get_path_name(),"material_slots":len(slots),"saved":True}
(root/"artifacts/art/bellbreaker-shoulder-2026-11-20/ue-import.json").write_text(json.dumps(receipt,indent=2))
unreal.log("BOSSLAB FORGE SHOULDER saved sibling on unchanged skeleton/materials")
if os.environ.get("BOSSLAB_IMPORT_KEEP_EDITOR")!="1":unreal.SystemLibrary.quit_editor()
