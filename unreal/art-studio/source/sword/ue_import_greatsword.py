"""Import the player's enchanted greatsword and build its materials.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/sword/ue_import_greatsword.py
(FBX import needs the editor; the script quits it, so the launcher's exit 1 is expected).
Input: prep_greatsword.py output in artifacts/art/overnight-2026-11-10/sword. Writes
/Game/BossLab/Sword (local, not committed):
  M_SwordSteel   dark pattern-welded steel: object-space folded bands, roughness variation
  M_SwordIron    blackened iron (guard, ring, langet)
  M_SwordLeather dark oxblood leather
  M_SwordBronze  aged bronze (ferrules, pommel)
  M_SwordRune    the enchantment: emissive amber glyphs; scalar parameter Glow (MID)
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
SRC = os.path.join(ROOT, 'artifacts/art/overnight-2026-11-10/sword')
DEST = '/Game/BossLab/Sword'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {}
if eal.does_directory_exist(DEST):
    eal.delete_directory(DEST)

def new_material(name):
    return tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())

def const(mat, value, x, y):
    if isinstance(value, (int, float)):
        n = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, x, y); n.set_editor_property('r', value)
    else:
        n = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, x, y); n.set_editor_property('constant', unreal.LinearColor(*value, 1))
    return n

def custom(mat, code, inputs, out_type, x, y):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property('code', code); node.set_editor_property('output_type', out_type)
    pins = []
    for n in inputs:
        pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
    node.set_editor_property('inputs', pins)
    return node

def plain(name, colour, metal, rough):
    mat = new_material(name)
    mel.connect_material_property(const(mat, colour, -400, 0), '', unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(const(mat, metal, -400, 150), '', unreal.MaterialProperty.MP_METALLIC)
    mel.connect_material_property(const(mat, rough, -400, 300), '', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    report[name] = {'colour': colour, 'metal': metal, 'rough': rough}
    return mat

# Pattern-welded steel: wavy folded bands along the blade in object space (they stay on
# the sword as it swings), darker crests, slightly varied roughness.
STEEL_CODE = '''
float3 p=P.xyz;
float w=sin(p.z*.9+sin(p.x*1.7+p.z*.23)*2.2+p.x*.6);
float bands=w*.5+.5;
float grain=frac(sin(dot(floor(p.xz*float2(3,.6)),float2(12.9898,78.233)))*43758.5453);
return float3(lerp(.07,.16,bands)+.02*grain, lerp(.5,.3,bands)+.08*grain, bands);
'''

def steel():
    mat = new_material('M_SwordSteel')
    pos = mel.create_material_expression(mat, unreal.MaterialExpressionLocalPosition, -900, 0)
    node = custom(mat, STEEL_CODE, ['P'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -650, 0)
    mel.connect_material_expressions(pos, '', node, 'P')
    r = mel.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -400, 0); r.set_editor_property('r', True)
    g = mel.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -400, 150); g.set_editor_property('g', True)
    mel.connect_material_expressions(node, '', r, ''); mel.connect_material_expressions(node, '', g, '')
    tint = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -200, 0)
    mel.connect_material_expressions(r, '', tint, 'A'); mel.connect_material_expressions(const(mat, (1, 1, 1.06), -400, -150), '', tint, 'B')
    mel.connect_material_property(tint, '', unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(g, '', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(const(mat, .92, -400, 300), '', unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(mat)
    report['M_SwordSteel'] = 'pattern-welded bands, metallic .92'
    return mat

def rune():
    mat = new_material('M_SwordRune')
    glow = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -700, 200)
    glow.set_editor_property('parameter_name', 'Glow'); glow.set_editor_property('default_value', 1.0)
    emissive = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -400, 200)
    mel.connect_material_expressions(const(mat, (6, 2.4, .5), -700, 0), '', emissive, 'A')
    mel.connect_material_expressions(glow, '', emissive, 'B')
    mel.connect_material_property(const(mat, (.2, .1, .03), -400, 0), '', unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(emissive, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_SwordRune'] = 'emissive amber, MID parameter Glow'
    return mat

materials = {
    'sword_steel': steel(),
    'sword_iron': plain('M_SwordIron', (.035, .035, .04), .85, .55),
    'sword_leather': plain('M_SwordLeather', (.07, .022, .014), 0, .78),
    'sword_bronze': plain('M_SwordBronze', (.38, .25, .1), .95, .36),
    'sword_rune': rune(),
}
ui = unreal.FbxImportUI()
ui.import_mesh = True; ui.import_as_skeletal = False; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
sm = ui.static_mesh_import_data
sm.set_editor_property('combine_meshes', True)
sm.set_editor_property('import_uniform_scale', 100.0)
sm.set_editor_property('auto_generate_collision', False)
sm.set_editor_property('generate_lightmap_u_vs', False)
sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
t = unreal.AssetImportTask()
t.filename = os.path.join(SRC, 'SM_Greatsword.fbx'); t.destination_path = DEST; t.destination_name = 'SM_Greatsword'
t.automated = True; t.replace_existing = True; t.save = False; t.options = ui
tools.import_asset_tasks([t])
mesh = unreal.load_asset(f'{DEST}/SM_Greatsword')
slots = []
for s in mesh.get_editor_property('static_materials'):
    slot = str(s.get_editor_property('material_slot_name'))
    key = next((k for k in materials if slot.startswith(k)), None)
    s.set_editor_property('material_interface', materials.get(key)); slots.append(s)
mesh.set_editor_property('static_materials', slots)
box = mesh.get_bounding_box()
report['SM_Greatsword'] = {'slots': [str(s.get_editor_property('material_slot_name')) for s in slots],
                           'min_cm': [round(box.min.x, 1), round(box.min.y, 1), round(box.min.z, 1)],
                           'max_cm': [round(box.max.x, 1), round(box.max.y, 1), round(box.max.z, 1)],
                           'triangles': mesh.get_num_triangles(0)}
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(SRC, 'import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB greatsword import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
