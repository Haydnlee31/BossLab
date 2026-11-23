"""Forge-fire spectacle materials for the Bellbreaker (WardenSpectacle.cpp, 2026-11-23), presentation only.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/bellbreaker/ue_import_bellbreaker_spectacle.py
(the script quits the editor, so the launcher's exit 1 is expected). Writes /Game/BossLab/Bellbreaker/FX (local,
not committed):
  M_BB_HammerTrail  additive molten ribbon (white-yellow core, orange-red edges) behind the bell
  M_BB_ForgeEmber   additive orange ember with per-instance flicker; also the pre-contact flare
Without them the spectacle keeps the Regent's soul-fire M_BossTrail / M_SoulEmber.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
DEST = '/Game/BossLab/Bellbreaker/FX'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary

def fresh(name):
    path = f'{DEST}/{name}'
    mat = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property('two_sided', True)
    return mat

def custom(mat, code, inputs):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -400, 0)
    node.set_editor_property('code', code)
    node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    pins = []
    for n, _ in inputs:
        p = unreal.CustomInput(); p.set_editor_property('input_name', n); pins.append(p)
    node.set_editor_property('inputs', pins)
    for n, src in inputs:
        mel.connect_material_expressions(src, '', node, n)
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    return node

TRAIL = '''
float2 uv=UV.xy; float across=1-abs(uv.y*2-1);
float core=pow(saturate(across),9), body=pow(saturate(across),3);   // a soft streak, not a slab
// no fade along uv.x: each ribbon segment is its own quad (fading per quad drew beads); the
// ribbon already narrows with age in WardenSpectacle.cpp
return float3(1.4,.28,.04)*body*.28+float3(1.8,1.25,.55)*core*.45;
'''
EMBER = '''
float2 d=UV.xy*2-1; float r=dot(d,d);
float glow=exp(-r*5.5), hot=exp(-r*22);
float flick=.7+.3*sin(T.x*17+dot(P,float3(.13,.07,.11)));
return (float3(1.5,.38,.06)*glow+float3(1.6,1.15,.55)*hot)*flick*1.6;
'''
report = {}
m = fresh('M_BB_HammerTrail')
custom(m, TRAIL, [('UV', mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -800, 0))])
mel.recompile_material(m); report['M_BB_HammerTrail'] = 'additive molten ribbon'
m = fresh('M_BB_ForgeEmber')
custom(m, EMBER, [('UV', mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -800, 0)),
                  ('T', mel.create_material_expression(m, unreal.MaterialExpressionTime, -800, 150)),
                  ('P', mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -800, 300))])
mel.recompile_material(m); report['M_BB_ForgeEmber'] = 'additive forge ember'
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
out = os.path.join(ROOT, 'artifacts/art/bellbreaker-fx-2026-11-23')
os.makedirs(out, exist_ok=True)
json.dump(report, open(os.path.join(out, 'spectacle-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB bellbreaker spectacle import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
