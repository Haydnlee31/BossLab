"""Editor-mode import of scoped Smeltery modules. No C++ or existing arena edits."""
import unreal,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
FBX=ROOT/'artifacts/art/bellbreaker-smeltery-2026-11-16/export'
DEST='/Game/BossLab/Smeltery'
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

def texture(path, kind):
    name = 'T_' + os.path.splitext(os.path.basename(path))[0]
    tex = task(path, name)
    if kind in ('normal_gl','normal_dx'):
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb', False)
        tex.set_editor_property('flip_green_channel', kind == 'normal_gl')  # glTF normals are OpenGL (+Y)
    elif kind == 'masks':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
        tex.set_editor_property('srgb', False)
    return tex

def new_material(name):
    path = f'{DEST}/{name}'
    mat = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    return mat

def sample(mat, tex, sampler, y):
    s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -600, y)
    s.set_editor_property('texture', tex); s.set_editor_property('sampler_type', sampler)
    return s

def custom(mat, code, inputs, out_type, x, y):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property('code', code); node.set_editor_property('output_type', out_type)
    pins = []
    for n in inputs:
        pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
    node.set_editor_property('inputs', pins)
    return node


def constant(mat,value,prop):
 if isinstance(value,list):
  n=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-400,0);n.set_editor_property('constant',unreal.LinearColor(*value,1))
 else:
  n=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,0);n.set_editor_property('r',value)
 mel.connect_material_property(n,'',prop)
materials={}
for name,info in json.loads((FBX/'materials.json').read_text()).items():
 mat=new_material(name);mat.set_editor_property('two_sided',False)
 constant(mat,info['color'],unreal.MaterialProperty.MP_BASE_COLOR);constant(mat,info['roughness'],unreal.MaterialProperty.MP_ROUGHNESS);constant(mat,info['metallic'],unreal.MaterialProperty.MP_METALLIC)
 for key in ['diff','arm','normal_gl','normal_dx']:
  if key not in info:continue
  kind='color' if key=='diff' else 'masks' if key=='arm' else key
  sampler=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR if key=='diff' else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS if key=='arm' else unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
  node=sample(mat,texture(str(ROOT/info[key]),kind),sampler,300)
  if key=='diff':mel.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
  elif key=='arm':
   for channel,prop in [('R',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),('G',unreal.MaterialProperty.MP_ROUGHNESS),('B',unreal.MaterialProperty.MP_METALLIC)]:mel.connect_material_property(node,channel,prop)
  else:mel.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_NORMAL)
 if info.get('kind')=='molten':
  uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-900,0)
  node=custom(mat,'float2 q=UV+float2(T*.008,T*.003); float n=.5+.5*sin(q.x*31+sin(q.y*19)*2)*sin(q.y*47+q.x*8); return lerp(float3(.03,.008,.001),float3(5,1.4,.08)*(1+.08*sin(T*1.7)),smoothstep(.35,.72,n));',['UV','T'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-400,0)
  mel.connect_material_expressions(uv,'',node,'UV');tm=mel.create_material_expression(mat,unreal.MaterialExpressionTime,-900,200);mel.connect_material_expressions(tm,'',node,'T');mel.connect_material_property(node,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if info.get('kind')=='wood':
  uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-900,0)
  node=custom(mat,'float g=.5+.5*sin(UV.y*350+sin(UV.x*12)*5); return lerp(float3(.045,.018,.006),float3(.19,.085,.027),g*.6+.2);',['UV'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-400,0)
  mel.connect_material_expressions(uv,'',node,'UV');mel.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
 mel.recompile_material(mat);materials[name]=mat
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
 expected=[v*100 for v in info['size_m']];actual=[size.x,size.y,size.z];actual_bounds=[[box.min.x,box.min.y,box.min.z],[box.max.x,box.max.y,box.max.z]];expected_bounds=[[v*100 for v in q] for q in info['bounds_m']];signed_error=max(abs(a-b) for q,w in zip(actual_bounds,expected_bounds) for a,b in zip(q,w))
 report[piece]={'triangles':mesh.get_num_triangles(0),'size_cm':actual,'expected_size_cm':expected,'signed_bounds_cm':actual_bounds,'expected_signed_bounds_cm':expected_bounds,'signed_bounds_max_error_cm':signed_error,'scale_max_error_cm':max(abs(a-b) for a,b in zip(actual,expected)),'materials':[s.get_editor_property('material_interface').get_name() for s in slots]}
 if report[piece]['scale_max_error_cm']>2:raise RuntimeError('Import scale mismatch '+piece)
 if signed_error>2:raise RuntimeError('Import signed-coordinate mismatch '+piece+': '+str(actual_bounds)+' expected '+str(expected_bounds))
eal.save_directory(DEST,only_if_is_dirty=False,recursive=True)
layout=ROOT/'unreal/BossLabWarden/Content/BossLab/Smeltery/layout.json';layout.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(FBX/'layout.json',layout)
(FBX.parent/'import-report.json').write_text(json.dumps(report,indent=2));unreal.log('SMELTERY IMPORT '+json.dumps(report));unreal.SystemLibrary.quit_editor()
