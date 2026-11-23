"""Coordinator-authorized editor only. Optional sibling, no existing assets deleted.
Run after fitted weathered FBX and texture review. Uses existing Bellbreaker skeleton.
"""
import unreal,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[4]
D=R/'artifacts/unreal/bellbreaker-refit-20261120/sculpt/weathered/fit'
DEST='/Game/BossLab/Bellbreaker/WeatheredStudy';STEM='SKM_BellbreakerWeathered'
eal=unreal.EditorAssetLibrary;mel=unreal.MaterialEditingLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools()
report={'ok':False,'optional_only':True}
try:
 assert not eal.does_directory_exist(DEST),'Preserve study destination; choose new suffix for a new revision'
 skeleton=unreal.load_asset('/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig_Skeleton')
 assert skeleton, 'Existing exact runtime skeleton required'
 def task(file,name,options=None):
  t=unreal.AssetImportTask();t.filename=str(file);t.destination_path=DEST;t.destination_name=name
  t.automated=True;t.replace_existing=False;t.save=True
  if options:t.options=options
  tools.import_asset_tasks([t]);return unreal.load_asset(DEST+'/'+name)
 base=task(D/(STEM+'_BaseColor.png'),'T_Weathered_D')
 mr=task(D/(STEM+'_MetalRough.png'),'T_Weathered_MR')
 assert base and mr
 mr.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_MASKS);mr.set_editor_property('srgb',False)
 mats={}
 for name,masked in [('Solid',False),('Cloth',True)]:
  m=tools.create_asset('M_Weathered_'+name,DEST,unreal.Material,unreal.MaterialFactoryNew())
  m.set_editor_property('used_with_skeletal_mesh',True);m.set_editor_property('two_sided',True)
  if masked:m.set_editor_property('blend_mode',unreal.BlendMode.BLEND_MASKED)
  d=mel.create_material_expression(m,unreal.MaterialExpressionTextureSample,-500,0);d.set_editor_property('texture',base)
  s=mel.create_material_expression(m,unreal.MaterialExpressionTextureSample,-500,250);s.set_editor_property('texture',mr);s.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
  mel.connect_material_property(d,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
  mel.connect_material_property(s,'G',unreal.MaterialProperty.MP_ROUGHNESS)
  mel.connect_material_property(s,'B',unreal.MaterialProperty.MP_METALLIC)
  if masked:mel.connect_material_property(d,'A',unreal.MaterialProperty.MP_OPACITY_MASK)
  mel.recompile_material(m);mats[name]=m
 glove=tools.create_asset('M_Weathered_SmithGlove',DEST,unreal.Material,unreal.MaterialFactoryNew())
 glove.set_editor_property('used_with_skeletal_mesh',True);glove.set_editor_property('two_sided',True)
 c=mel.create_material_expression(glove,unreal.MaterialExpressionConstant3Vector,-300,0);c.set_editor_property('constant',unreal.LinearColor(.055,.032,.019,1))
 mel.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
 r=mel.create_material_expression(glove,unreal.MaterialExpressionConstant,-300,180);r.set_editor_property('r',.56);mel.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
 atlas=task(D/(STEM+'_GloveBaseColor.png'),'T_Weathered_Glove_D')
 assert atlas
 gt=mel.create_material_expression(glove,unreal.MaterialExpressionTextureSample,-650,0);gt.set_editor_property('texture',atlas)
 tint=mel.create_material_expression(glove,unreal.MaterialExpressionConstant3Vector,-650,150);tint.set_editor_property('constant',unreal.LinearColor(.34,.26,.20,1))
 mul=mel.create_material_expression(glove,unreal.MaterialExpressionMultiply,-300,0);mel.connect_material_expressions(gt,'RGB',mul,'A');mel.connect_material_expressions(tint,'',mul,'B');mel.connect_material_property(mul,'',unreal.MaterialProperty.MP_BASE_COLOR)
 mel.recompile_material(glove);mats['SmithGlove']=glove
 wrist=tools.create_asset('M_Weathered_SmithWrist',DEST,unreal.Material,unreal.MaterialFactoryNew());wrist.set_editor_property('used_with_skeletal_mesh',True);wrist.set_editor_property('two_sided',True)
 wc=mel.create_material_expression(wrist,unreal.MaterialExpressionConstant3Vector,-300,0);wc.set_editor_property('constant',unreal.LinearColor(.055,.032,.019,1));mel.connect_material_property(wc,'',unreal.MaterialProperty.MP_BASE_COLOR)
 wr=mel.create_material_expression(wrist,unreal.MaterialExpressionConstant,-300,180);wr.set_editor_property('r',.56);mel.connect_material_property(wr,'',unreal.MaterialProperty.MP_ROUGHNESS);mel.recompile_material(wrist);mats['SmithWrist']=wrist
 ui=unreal.FbxImportUI();ui.import_mesh=True;ui.import_as_skeletal=True;ui.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
 ui.skeleton=skeleton;ui.import_materials=False;ui.import_textures=False;ui.import_animations=False;ui.create_physics_asset=False
 ui.skeletal_mesh_import_data.set_editor_property('normal_import_method',unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
 ui.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose',False)
 mesh=task(D/(STEM+'.fbx'),STEM,ui);assert mesh
 assert mesh.get_editor_property('skeleton')==skeleton,'Skeleton changed'
 mesh.set_editor_property('materials',[unreal.SkeletalMaterial(material_interface=mats[str(m.material_slot_name).split('.')[0].split('_')[0]],material_slot_name=m.material_slot_name) for m in mesh.get_editor_property('materials')])
 eal.save_directory(DEST,only_if_is_dirty=False,recursive=True)
 b=mesh.get_bounds();report.update(ok=True,asset=DEST+'/'+STEM,skeleton=skeleton.get_path_name(),extent=[b.box_extent.x,b.box_extent.y,b.box_extent.z])
except Exception:
 import traceback
 report['error']=traceback.format_exc()
(D/'ue-import-report.json').write_text(json.dumps(report,indent=2))
unreal.log('BOSSLAB weathered study '+str(report['ok']))
if os.environ.get('BOSSLAB_IMPORT_KEEP_EDITOR')!='1': unreal.SystemLibrary.quit_editor()
