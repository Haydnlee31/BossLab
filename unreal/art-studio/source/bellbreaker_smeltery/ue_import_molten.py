"""Reimport only molten mesh, retaining existing shader/material/textures."""
import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';P=E/'export';DEST='/Game/BossLab/Smeltery';name='SM_SmelteryMolten';info=json.loads((P/'pieces.json').read_text())[name]
ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;ui.import_materials=False;ui.import_textures=False;ui.import_animations=False
sm=ui.static_mesh_import_data
for key,val in [('combine_meshes',True),('import_uniform_scale',100.0),('auto_generate_collision',False),('generate_lightmap_u_vs',False),('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)]:sm.set_editor_property(key,val)
t=unreal.AssetImportTask();t.filename=str(P/(name+'.fbx'));t.destination_path=DEST;t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=False;t.options=ui;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
m=unreal.load_asset(DEST+'/'+name);assert m is not None;slots=[]
for slot in m.get_editor_property('static_materials'):
 s=str(slot.get_editor_property('material_slot_name'));mat=unreal.load_asset(DEST+'/'+s);assert mat is not None,'Existing material missing '+s;slot.set_editor_property('material_interface',mat);slots.append(slot)
m.set_editor_property('static_materials',slots);b=m.get_bounding_box();actual=[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]];expected=[[v*100 for v in q] for q in info['bounds_m']];err=max(abs(a-b) for q,w in zip(actual,expected) for a,b in zip(q,w));assert err<2,'Signed coordinate error '+str(err)
unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
r={'module':name,'triangles':m.get_num_triangles(0),'signed_bounds_cm':actual,'expected_signed_bounds_cm':expected,'signed_bounds_max_error_cm':err,'material_names':[s.get_editor_property('material_interface').get_name() for s in slots],'scope':'Only mesh reimport; existing materials/textures reused'};(E/'molten-import-report.json').write_text(json.dumps(r,indent=2));unreal.log(json.dumps(r));unreal.SystemLibrary.quit_editor()
