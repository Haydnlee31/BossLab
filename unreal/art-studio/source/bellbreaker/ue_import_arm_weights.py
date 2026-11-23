"""Import only the repaint as a sibling skeletal mesh. Keep the original rig and assets."""
from pathlib import Path
import unreal

root = Path(__file__).resolve().parents[4]
name = "SKM_BellbreakerForgeSkin"
dst = "/Game/BossLab/Bellbreaker/ForgeSkin"
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
task.filename = str(root/"artifacts/unreal/bellbreaker-dialogue"/(name+".fbx"))
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
unreal.log("BOSSLAB FORGE SKIN saved sibling on original skeleton with original material slots")
unreal.SystemLibrary.quit_editor()
