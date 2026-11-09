"""Build the small presentation-effect materials (heal flask, heal motes, landing dust).

Run: ./scripts/bosslab-unreal python unreal/art-studio/source/effects/ue_import_effects.py
Writes /Game/BossLab/Effects (local, not committed). No textures.
  M_HealMote    additive soft round mote, warm crimson-gold, per-instance flicker
  M_FlaskGlass  additive crimson glow for the flask (drawn over a dark glass shell)
  M_ImpactDust  translucent soft dust puff, grey-brown, per-instance variation
See docs/SOULS_CONTROLS.md.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
DEST = '/Game/BossLab/Effects'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {}

def get_or_create(name):
    path = f'{DEST}/{name}'
    mat = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('two_sided', True)
    return mat

def custom(mat, code, inputs, out_type, x, y):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property('code', code)
    node.set_editor_property('output_type', out_type)
    pins = []
    for n in inputs:
        pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
    node.set_editor_property('inputs', pins)
    return node

# Soft round glow on a card: bright core, crimson-to-gold by instance, gentle flicker.
MOTE_CODE = '''
float2 d=UV.xy*2-1; float r=length(d);
float core=saturate(1-r); core=core*core*core;
float s=Seed.x; float flick=.75+.25*sin(Tm.x*(9+s*7)+s*40);
// Crimson, a few amber; kept below white so the motes read red, not gold.
float3 col=lerp(float3(1,.06,.03),float3(1,.3,.08),frac(s*3.7)*frac(s*3.7));
return col*core*flick*2.6;
'''

def mote():
    mat = get_or_create('M_HealMote')
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -800, 0)
    seed = mel.create_material_expression(mat, unreal.MaterialExpressionPerInstanceRandom, -800, 150)
    time = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -800, 300)
    node = custom(mat, MOTE_CODE, ['UV', 'Seed', 'Tm'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -400, 100)
    for src, pin in ((uv, 'UV'), (seed, 'Seed'), (time, 'Tm')):
        mel.connect_material_expressions(src, '', node, pin)
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_HealMote'] = 'additive soft mote, crimson-gold'

def flask():
    mat = get_or_create('M_FlaskGlass')
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    # Dim enough to stay crimson under bloom (2.2 read as a white dot in the capture).
    c.set_editor_property('constant', unreal.LinearColor(.9, .07, .03, 1))
    mel.connect_material_property(c, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_FlaskGlass'] = 'additive crimson glow'

DUST_CODE = '''
float2 d=UV.xy*2-1; float r=length(d);
float n=frac(sin(dot(floor(UV.xy*6+Seed.x*9),float2(12.9898,78.233)))*43758.5453);
return saturate((1-r)*(.6+.4*n))*.55;
'''

def dust():
    mat = get_or_create('M_ImpactDust')
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
    uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -800, 0)
    seed = mel.create_material_expression(mat, unreal.MaterialExpressionPerInstanceRandom, -800, 150)
    node = custom(mat, DUST_CODE, ['UV', 'Seed'], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -400, 200)
    for src, pin in ((uv, 'UV'), (seed, 'Seed')):
        mel.connect_material_expressions(src, '', node, pin)
    col = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    col.set_editor_property('constant', unreal.LinearColor(.16, .13, .1, 1))
    mel.connect_material_property(col, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(mat)
    report['M_ImpactDust'] = 'translucent soft puff'

mote(); flask(); dust()
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
out = os.path.join(ROOT, 'artifacts/art/souls-controls-2026-11-10')
os.makedirs(out, exist_ok=True)
json.dump(report, open(os.path.join(out, 'effects-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB effects import ' + json.dumps(report))
