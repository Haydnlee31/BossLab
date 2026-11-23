"""Editor-mode import of scoped Smeltery modules. No C++ or existing arena edits."""
import unreal,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
FBX=ROOT/'artifacts/art/hearth-a-2026-11-16/export'
DEST='/Game/BossLab/HearthA'
tools=unreal.AssetToolsHelpers.get_asset_tools();mel=unreal.MaterialEditingLibrary;eal=unreal.EditorAssetLibrary
import os
report={}
for png in (FBX/'textures').glob('*.png'):
    if not png.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):raise RuntimeError('Run fix_texture_encoding.py before import: '+str(png))
def task(filename, name, options=None):
    t = unreal.AssetImportTask()
    t.filename = filename; t.destination_path = DEST; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    if options:
        t.options = options
    tools.import_asset_tasks([t])
    return unreal.load_asset(f'{DEST}/{name}')

materials={name:unreal.load_asset(DEST+'/'+name) for name in json.loads((FBX/'materials.json').read_text())}
assert all(materials.values()), 'Existing material missing; full importer required'
# Scoped coordinate correction: replace only the floor roughness connection.
# Existing colour/normal/metallic inputs and all other materials remain untouched.
wet_patch=[]
for name,info in json.loads((FBX/'materials.json').read_text()).items():
 if info.get('kind')!='floor_wet':continue
 mat=materials[name]
 pos=mel.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-900,700)
 wet=mel.create_material_expression(mat,unreal.MaterialExpressionCustom,-500,700)
 code='float2 d=(P.xy*.01-float2(-7.5,13.5))/float2(3.0,2.2);return .8-.45*saturate(1-length(d));'
 wet.set_editor_property('code',code);wet.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT1)
 pin=unreal.CustomInput();pin.set_editor_property('input_name','P');wet.set_editor_property('inputs',[pin])
 assert mel.connect_material_expressions(pos,'',wet,'P'), 'Floor world position connection failed'
 assert mel.connect_material_property(wet,'',unreal.MaterialProperty.MP_ROUGHNESS), 'Floor roughness replacement failed'
 mel.recompile_material(mat);eal.save_loaded_asset(mat)
 wet_patch.append({'material':name,'centre_runtime_m':[-7.5,13.5],'code':code,'scope':'roughness input only; prior unconnected roughness nodes retained'})
assert len(wet_patch)==1, 'Expected exactly one floor wet material'
(FBX.parent/'wetmask-reflection-patch.json').write_text(json.dumps(wet_patch,indent=2))
for piece,info in json.loads((FBX/'pieces.json').read_text()).items():
 ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;ui.import_materials=False;ui.import_textures=False;ui.import_animations=False
 sm=ui.static_mesh_import_data;sm.set_editor_property('combine_meshes',True);sm.set_editor_property('import_uniform_scale',100.0);sm.set_editor_property('auto_generate_collision',False);sm.set_editor_property('generate_lightmap_u_vs',False);sm.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
 mesh=task(str(FBX/(piece+'.fbx')),piece,ui)
 if not mesh:raise RuntimeError('Missing imported mesh '+piece)
 slots=[]
 for slot in mesh.get_editor_property('static_materials'):
  name=str(slot.get_editor_property('material_slot_name'));mat=next((m for k,m in materials.items() if k==name or name.startswith(k)),None)
  if not mat:raise RuntimeError('Unassigned material '+name)
  slot.set_editor_property('material_interface',mat);slots.append(slot)
 mesh.set_editor_property('static_materials',slots);box=mesh.get_bounding_box();size=box.max-box.min
 expected=[v*100 for v in info['size_m']];actual=[size.x,size.y,size.z];actual_bounds=[[box.min.x,box.min.y,box.min.z],[box.max.x,box.max.y,box.max.z]];expected_bounds=[[v*100 for v in q] for q in info.get('ue_expected_bounds_m',info['bounds_m'])];signed_error=max(abs(a-b) for q,w in zip(actual_bounds,expected_bounds) for a,b in zip(q,w))
 report[piece]={'triangles':mesh.get_num_triangles(0),'size_cm':actual,'expected_size_cm':expected,'signed_bounds_cm':actual_bounds,'expected_signed_bounds_cm':expected_bounds,'signed_bounds_max_error_cm':signed_error,'scale_max_error_cm':max(abs(a-b) for a,b in zip(actual,expected)),'materials':[s.get_editor_property('material_interface').get_name() for s in slots]}
 if report[piece]['scale_max_error_cm']>2:raise RuntimeError('Import scale mismatch '+piece)
 if signed_error>2:raise RuntimeError('Import signed-coordinate mismatch '+piece+': '+str(actual_bounds)+' expected '+str(expected_bounds))
eal.save_directory(DEST,only_if_is_dirty=False,recursive=True)
layout=ROOT/'unreal/BossLabWarden/Content/BossLab/HearthA/layout.json';layout.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(FBX/'layout.json',layout)
(FBX.parent/'import-reflected-report.json').write_text(json.dumps(report,indent=2));unreal.log('SMELTERY IMPORT '+json.dumps(report));unreal.SystemLibrary.quit_editor()
