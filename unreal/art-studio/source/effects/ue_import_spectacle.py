"""Materials for the spectacle pass (WardenSpectacle.cpp), presentation only.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/effects/ue_import_spectacle.py
(the script quits the editor, so the launcher's exit 1 is expected). Writes /Game/BossLab/Effects
(local, not committed):
  M_BossTrail   additive soul-fire ribbon (white-hot core, blue edges) for the boss's estoc,
                censer and sword swings
  M_SoulEmber   additive soft blue-white ember, per-instance flicker from its world position
The game falls back to M_SwordTrail / M_HealMote when these are absent.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
DEST = '/Game/BossLab/Effects'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {}

def fresh(name):
    path = f'{DEST}/{name}'
    mat = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property('two_sided', True)
    return mat

def custom(mat, code, inputs, x, y):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property('code', code)
    node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    pins = []
    for n in inputs:
        p = unreal.CustomInput(); p.set_editor_property('input_name', n); pins.append(p)
    node.set_editor_property('inputs', pins)
    return node

TRAIL = '''
float2 uv=UV.xy; float across=1-abs(uv.y*2-1);
float core=pow(saturate(across),6), body=pow(saturate(across),2.2);
float fade=1-uv.x*.85;
return (float3(.15,.45,1.6)*body*.45+float3(.9,.95,1.2)*core*.6)*fade;   // half of the first try, which read as a solid slab
'''
EMBER = '''
float2 d=UV.xy*2-1; float r=dot(d,d);
float glow=exp(-r*5.5), hot=exp(-r*22);
float flick=.75+.25*sin(T.x*13+dot(P,float3(.13,.07,.11)));
return (float3(.2,.5,1.5)*glow+float3(1,1,1.2)*hot)*flick*1.6;
'''

m = fresh('M_BossTrail')
uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -800, 0)
n = custom(m, TRAIL, ['UV'], -400, 0)
mel.connect_material_expressions(uv, '', n, 'UV')
mel.connect_material_property(n, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(m); report['M_BossTrail'] = 'additive soul-fire ribbon'

m = fresh('M_SoulEmber')
uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -800, 0)
tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -800, 150)
wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -800, 300)
n = custom(m, EMBER, ['UV', 'T', 'P'], -400, 0)
mel.connect_material_expressions(uv, '', n, 'UV'); mel.connect_material_expressions(tm, '', n, 'T'); mel.connect_material_expressions(wp, '', n, 'P')
mel.connect_material_property(n, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(m); report['M_SoulEmber'] = 'additive soul ember'

eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
out = os.path.join(ROOT, 'artifacts/art/spectacle-2026-11-14')
os.makedirs(out, exist_ok=True)
json.dump(report, open(os.path.join(out, 'spectacle-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB spectacle import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
