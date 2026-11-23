"""A2-only visual correction after actual cold-study rejection. No geometry/global edits."""
import unreal,json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'artifacts/unreal/hearth-a2-walkthrough-2026-11-16/runtime-tuning-final'
OUT.mkdir(exist_ok=True)
P=ROOT/'unreal/BossLabWarden/Content/BossLab/HearthA2/layout.json'
original=P.read_bytes();layout=json.loads(original)
backup=OUT/'layout-before.json'
if not backup.exists():backup.write_bytes(original)
for light in layout['lights']:
    key=light['fixture_id']
    if key=='furnace-mouths':light.update(location_cm=[420,950,180],intensity_lumens=1000,attenuation_radius_cm=1500,source_radius_cm=60,soft_source_radius_cm=100)
    elif key=='bellows-lantern':light.update(location_cm=[-330,1000,265],source_radius_cm=30,soft_source_radius_cm=60)
    elif key=='gothic-window':light.update(location_cm=[-1020,680,600],intensity_lumens=2500)
    else:light.update(source_radius_cm=30,soft_source_radius_cm=60)
layout['lights']=[l for l in layout['lights'] if l['fixture_id']!='entry-window-bounce']
layout['lights'].append({'fixture_id':'entry-window-bounce','type':'point','casts_shadows':False,'location_cm':[0,-600,450],'color_rgb':[.55,.62,.72],'intensity_lumens':600,'attenuation_radius_cm':1900,'source_radius_cm':150,'soft_source_radius_cm':200,'role':'Approximate diffuse bounce from window toward closed entry wall; no invented visible lamp'})
mel=unreal.MaterialEditingLibrary;eal=unreal.EditorAssetLibrary
D='/Game/BossLab/HearthA2/'
def constant(mat,v,prop):
    if isinstance(v,list):
        n=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector);n.set_editor_property('constant',unreal.LinearColor(*v,1))
    else:
        n=mel.create_material_expression(mat,unreal.MaterialExpressionConstant);n.set_editor_property('r',v)
    mel.connect_material_property(n,'',prop)
wood=unreal.load_asset(D+'M_A2_aged_oak');sky=unreal.load_asset(D+'M_A2_daylit_exterior_aperture')
if not wood or not sky:raise RuntimeError('A2 scoped material assets must already exist')
for name in ['M_A2_aged_oak','M_A2_daylit_exterior_aperture']:
    source=ROOT/'unreal/BossLabWarden/Content/BossLab/HearthA2'/(name+'.uasset')
    if not (OUT/(name+'-before.uasset')).exists():shutil.copy2(source,OUT/(name+'-before.uasset'))
# Source noise was never pixel-identical; reduce the over-contrasted runtime conversion.
mel.delete_all_material_expressions(wood)
uv=mel.create_material_expression(wood,unreal.MaterialExpressionTextureCoordinate)
n=mel.create_material_expression(wood,unreal.MaterialExpressionCustom)
n.set_editor_property('code','float g=.5+.5*sin(UV.y*350+sin(UV.x*12)*5);return float3(.095,.045,.018)*(.9+.2*g);')
n.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
pin=unreal.CustomInput();pin.set_editor_property('input_name','UV');n.set_editor_property('inputs',[pin])
mel.connect_material_expressions(uv,'',n,'UV');mel.connect_material_property(n,'',unreal.MaterialProperty.MP_BASE_COLOR)
constant(wood,.8,unreal.MaterialProperty.MP_ROUGHNESS);constant(wood,0.,unreal.MaterialProperty.MP_METALLIC)
mel.recompile_material(wood);eal.save_loaded_asset(wood)
mel.delete_all_material_expressions(sky);sky.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);sky.set_editor_property('two_sided',True)
constant(sky,[.075,.12,.18],unreal.MaterialProperty.MP_EMISSIVE_COLOR);mel.recompile_material(sky);eal.save_loaded_asset(sky)
P.write_text(json.dumps(layout,indent=2));(OUT/'layout-after.json').write_text(P.read_text())
(OUT/'receipt.json').write_text(json.dumps({'before_layout_sha256':hashlib.sha256(original).hexdigest(),'after_layout_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'materials_changed':[wood.get_path_name(),sky.get_path_name()],'scope':'A2 only; no mesh or combat change; canonical Blender/export unchanged; direct runtime tuning based on actual image rejection','source_radius_limit':'Affects source/specular shape; does not guarantee diffuse area-light parity','full_export_reimport_would_restore_earlier_materials':True},indent=2))
unreal.SystemLibrary.quit_editor()
