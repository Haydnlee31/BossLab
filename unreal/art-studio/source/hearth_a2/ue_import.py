"""Editor-mode import of scoped Smeltery modules. No C++ or existing arena edits."""
import unreal,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
FBX=ROOT/'artifacts/art/hearth-a2-2026-11-16/export'
DEST='/Game/BossLab/HearthA2'
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
  if key=='diff':
   if 'color_multiplier' in info:
    mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-250,0);col=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-400,100);col.set_editor_property('constant',unreal.LinearColor(*info['color_multiplier'],1));mel.connect_material_expressions(node,'RGB',mul,'A');mel.connect_material_expressions(col,'',mul,'B');mel.connect_material_property(mul,'',unreal.MaterialProperty.MP_BASE_COLOR)
   else:mel.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
  elif key=='arm':
   for channel,prop in [('G',unreal.MaterialProperty.MP_ROUGHNESS),('B',unreal.MaterialProperty.MP_METALLIC)]:mel.connect_material_property(node,channel,prop)
   if info.get('arm_occlusion',False):mel.connect_material_property(node,'R',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
   if 'roughness_multiplier' in info:
    mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-250,300);mul.set_editor_property('const_b',info['roughness_multiplier']);mel.connect_material_expressions(node,'G',mul,'A');mel.connect_material_property(mul,'',unreal.MaterialProperty.MP_ROUGHNESS)
  else:mel.connect_material_property(node,'RGB',unreal.MaterialProperty.MP_NORMAL)
 if 'emission' in info:constant(mat,info['emission'],unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if info.get('kind')=='molten':
  uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-900,0)
  node=custom(mat,'float2 q=UV+float2(T*.008,T*.003); float n=.5+.5*sin(q.x*31+sin(q.y*19)*2)*sin(q.y*47+q.x*8); return lerp(float3(.03,.008,.001),float3(5,1.4,.08)*(1+.08*sin(T*1.7)),smoothstep(.35,.72,n));',['UV','T'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-400,0)
  mel.connect_material_expressions(uv,'',node,'UV');tm=mel.create_material_expression(mat,unreal.MaterialExpressionTime,-900,200);mel.connect_material_expressions(tm,'',node,'T');mel.connect_material_property(node,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if info.get('kind')=='wood':
  uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-900,0)
  node=custom(mat,'float g=.5+.5*sin(UV.y*350+sin(UV.x*12)*5); return lerp(float3(.025,.012,.004),float3(.16,.075,.025),g*.6+.2);',['UV'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-400,0)
  mel.connect_material_expressions(uv,'',node,'UV');mel.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
 if info.get('kind')=='floor_a2':
  pos=mel.create_material_expression(mat,unreal.MaterialExpressionWorldPosition,-900,500)
  wet=custom(mat,'float2 p=P.xy*.01;return max(saturate(1-length((p-float2(-6.5,5))/float2(3,4.5))),saturate(1-length((p-float2(4.5,7))/float2(2.7,3))));',['P'],unreal.CustomMaterialOutputType.CMOT_FLOAT1,-600,500);mel.connect_material_expressions(pos,'',wet,'P')
  rough=custom(mat,'return '+str(info['roughness'])+'-.48*W;',['W'],unreal.CustomMaterialOutputType.CMOT_FLOAT1,-300,500);mel.connect_material_expressions(wet,'',rough,'W');mel.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
  src=sample(mat,texture(str(ROOT/info['diff']),'color'),unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,700)
  tint=info['color_multiplier'];code='return C*float3('+','.join(str(v) for v in tint)+')*(1-.17*W);'
  shade=custom(mat,code,['C','W'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-300,700);mel.connect_material_expressions(src,'RGB',shade,'C');mel.connect_material_expressions(wet,'',shade,'W');mel.connect_material_property(shade,'',unreal.MaterialProperty.MP_BASE_COLOR)
 if info.get('kind')=='amber_panel':
  src=sample(mat,texture(str(ROOT/info['diff']),'color'),unreal.MaterialSamplerType.SAMPLERTYPE_COLOR,700)
  em=custom(mat,'return C*((C.r>C.b*1.5 && C.r>.055)?3.0:0.0);',['C'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-300,700);mel.connect_material_expressions(src,'RGB',em,'C');mel.connect_material_property(em,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if info.get('kind')=='window':
  mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',True);constant(mat,info.get('emission',[.15,.24,.36]),unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 if info.get('kind')=='water':
  uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-900,0);tm=mel.create_material_expression(mat,unreal.MaterialExpressionTime,-900,200)
  node=custom(mat,'return normalize(float3(.035*sin(UV.x*65+T*.7)+.018*sin(UV.y*34-T*.4),.03*cos(UV.y*57-T*.5),1));',['UV','T'],unreal.CustomMaterialOutputType.CMOT_FLOAT3,-400,0)
  mel.connect_material_expressions(uv,'',node,'UV');mel.connect_material_expressions(tm,'',node,'T');mel.connect_material_property(node,'',unreal.MaterialProperty.MP_NORMAL)
 if info.get('kind')=='steam':
  mat.set_editor_property('blend_mode',unreal.BlendMode.BLEND_TRANSLUCENT);mat.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);mat.set_editor_property('two_sided',True)
  uv=mel.create_material_expression(mat,unreal.MaterialExpressionTextureCoordinate,-900,0);tm=mel.create_material_expression(mat,unreal.MaterialExpressionTime,-900,200)
  node=custom(mat,'float2 q=UV-float2(.5,.5);float n=.5+.5*sin(UV.x*17+sin(UV.y*12-T*.4)*2)*sin(UV.y*19-T*.6);return pow(saturate(1-length(q*float2(2.2,1.8))),2)*(.04+.09*n);',['UV','T'],unreal.CustomMaterialOutputType.CMOT_FLOAT1,-400,0)
  mel.connect_material_expressions(uv,'',node,'UV');mel.connect_material_expressions(tm,'',node,'T');fade=mel.create_material_expression(mat,unreal.MaterialExpressionDepthFade,-200,0);fade.set_editor_property('fade_distance_default',100.0);mel.connect_material_expressions(node,'',fade,'Opacity');mel.connect_material_property(fade,'',unreal.MaterialProperty.MP_OPACITY);constant(mat,[.22,.25,.28],unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 mel.recompile_material(mat);materials[name]=mat
for piece,info in json.loads((FBX/'pieces.json').read_text()).items():
 ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_as_skeletal=False;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;ui.import_materials=False;ui.import_textures=False;ui.import_animations=False
 sm=ui.static_mesh_import_data;sm.set_editor_property('combine_meshes',True);sm.set_editor_property('import_uniform_scale',100.0);sm.set_editor_property('auto_generate_collision',False);sm.set_editor_property('generate_lightmap_u_vs',False);sm.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
 mesh=task(str(FBX/(piece+'.fbx')),piece,ui)
 if not mesh:raise RuntimeError('Missing imported mesh '+piece)
 slots=[]
 for slot in mesh.get_editor_property('static_materials'):
  name=str(slot.get_editor_property('material_slot_name'));mat=materials.get(name) or next((materials[k] for k in sorted(materials,key=len,reverse=True) if name.startswith(k)),None)
  if not mat:raise RuntimeError('Unassigned material '+name)
  slot.set_editor_property('material_interface',mat);slots.append(slot)
 mesh.set_editor_property('static_materials',slots);box=mesh.get_bounding_box();size=box.max-box.min
 expected=[v*100 for v in info['size_m']];actual=[size.x,size.y,size.z];actual_bounds=[[box.min.x,box.min.y,box.min.z],[box.max.x,box.max.y,box.max.z]];expected_bounds=[[v*100 for v in q] for q in info.get('ue_expected_bounds_m',info['bounds_m'])];signed_error=max(abs(a-b) for q,w in zip(actual_bounds,expected_bounds) for a,b in zip(q,w))
 report[piece]={'triangles':mesh.get_num_triangles(0),'size_cm':actual,'expected_size_cm':expected,'signed_bounds_cm':actual_bounds,'expected_signed_bounds_cm':expected_bounds,'signed_bounds_max_error_cm':signed_error,'scale_max_error_cm':max(abs(a-b) for a,b in zip(actual,expected)),'materials':[s.get_editor_property('material_interface').get_name() for s in slots]}
 if report[piece]['scale_max_error_cm']>2:raise RuntimeError('Import scale mismatch '+piece)
 if signed_error>2:raise RuntimeError('Import signed-coordinate mismatch '+piece+': '+str(actual_bounds)+' expected '+str(expected_bounds))
eal.save_directory(DEST,only_if_is_dirty=False,recursive=True)
layout=ROOT/'unreal/BossLabWarden/Content/BossLab/HearthA2/layout.json';layout.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(FBX/'layout.json',layout)
(FBX.parent/'import-report.json').write_text(json.dumps(report,indent=2));unreal.log('SMELTERY IMPORT '+json.dumps(report));unreal.SystemLibrary.quit_editor()
