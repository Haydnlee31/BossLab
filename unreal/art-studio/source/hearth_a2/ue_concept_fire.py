"""Hearth A2 concept pass (2026-11-17), part 2: hot metal and forge fire.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/hearth_a2/ue_concept_fire.py
- M_A2_contained_molten_metal: mostly glowing metal with dark crust veins (it read as a dark bar;
  the concept's channel is a bright orange river). Backed up first.
- M_A2_ForgeFire (new): unlit additive flicker for the furnace mouths; WardenSmeltery.cpp places it
  at layout.json `hearth_effect_anchors_cm` (A2 only).
- Softens the concept-grade damp roughness (0.22 -> 0.34): hard light-shaped ovals appeared on the floor.
"""
import shutil
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[4]
CONTENT = ROOT / 'unreal/BossLabWarden/Content/BossLab/HearthA2'
BACKUP = ROOT / 'artifacts/art/hearth-a2-dressing-2026-11-17/material-backup'
BACKUP.mkdir(parents=True, exist_ok=True)
D = '/Game/BossLab/HearthA2/'
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
MP = unreal.MaterialProperty
tools = unreal.AssetToolsHelpers.get_asset_tools()

def custom(mat, code, inputs, out_type, x=-400, y=0):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    pins = []
    for name in inputs:
        p = unreal.CustomInput(); p.set_editor_property('input_name', name); pins.append(p)
    n.set_editor_property('inputs', pins); n.set_editor_property('code', code); n.set_editor_property('output_type', out_type)
    return n

# Molten channel.
name = 'M_A2_contained_molten_metal'
if not (BACKUP / (name + '.uasset')).exists():
    shutil.copy2(CONTENT / (name + '.uasset'), BACKUP / (name + '.uasset'))
mat = unreal.load_asset(D + name)
mel.delete_all_material_expressions(mat)
pos = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -900, 0)
tm = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -900, 200)
code = ('float2 q=P.xy*.012+float2(T*.05,T*.02);'
        'float v=sin(q.x*3.1+sin(q.y*2.3)*1.7)*sin(q.y*4.7+q.x*.8+T*.3);'
        'float crust=smoothstep(.55,.9,abs(v));'
        'float pulse=1+.12*sin(T*2.1+P.x*.01);'
        'return lerp(float3(9,2.6,.35)*pulse,float3(.06,.015,.004),crust);')
em = custom(mat, code, ['P', 'T'], unreal.CustomMaterialOutputType.CMOT_FLOAT3)
mel.connect_material_expressions(pos, '', em, 'P'); mel.connect_material_expressions(tm, '', em, 'T')
mel.connect_material_property(em, '', MP.MP_EMISSIVE_COLOR)
base = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 300)
base.set_editor_property('constant', unreal.LinearColor(.05, .02, .01, 1))
mel.connect_material_property(base, '', MP.MP_BASE_COLOR)
r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 400); r.set_editor_property('r', .6)
mel.connect_material_property(r, '', MP.MP_ROUGHNESS)
mel.recompile_material(mat); eal.save_loaded_asset(mat)

# Forge fire.
fire_path = D + 'M_A2_ForgeFire'
if eal.does_asset_exist(fire_path):
    eal.delete_asset(fire_path)
fire = tools.create_asset('M_A2_ForgeFire', D.rstrip('/'), unreal.Material, unreal.MaterialFactoryNew())
fire.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
fire.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
fire.set_editor_property('two_sided', True)
pos = mel.create_material_expression(fire, unreal.MaterialExpressionWorldPosition, -900, 0)
tm = mel.create_material_expression(fire, unreal.MaterialExpressionTime, -900, 200)
uv = mel.create_material_expression(fire, unreal.MaterialExpressionTextureCoordinate, -900, 400)
nrm = mel.create_material_expression(fire, unreal.MaterialExpressionVertexNormalWS, -900, 600)
cam = mel.create_material_expression(fire, unreal.MaterialExpressionCameraVectorWS, -900, 800)
code = ('float facing=saturate(dot(N,V));'
        'float rise=frac(P.z*.02-T*.9);'
        'float flick=.75+.25*sin(T*11+P.x*.07)*sin(T*7.3+P.z*.05);'
        'float tongue=.6+.4*sin(P.x*.11+T*3+sin(P.z*.08-T*4)*2);'
        'float core=pow(facing,1.6);'
        'return float3(6,1.7,.25)*core*flick*tongue;')
em = custom(fire, code, ['P', 'T', 'N', 'V'], unreal.CustomMaterialOutputType.CMOT_FLOAT3)
for node, pin in ((pos, 'P'), (tm, 'T'), (nrm, 'N'), (cam, 'V')):
    mel.connect_material_expressions(node, '', em, pin)
mel.connect_material_property(em, '', MP.MP_EMISSIVE_COLOR)
mel.recompile_material(fire); eal.save_loaded_asset(fire)

# Softer damp highlight in the graded floor materials.
for i in range(6):
    m = unreal.load_asset(D + f'M_A2_worn_floor_stone_{i}')
    node = mel.get_material_property_input_node(m, MP.MP_ROUGHNESS)
    if node and 'BOSSLAB_GRADE' in (node.get_editor_property('desc') or ''):
        node.set_editor_property('code', node.get_editor_property('code').replace(',.22,damp)', ',.34,damp)'))
        mel.recompile_material(m); eal.save_loaded_asset(m)
unreal.log('BOSSLAB concept fire done')
unreal.SystemLibrary.quit_editor()
