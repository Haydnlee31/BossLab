"""Import the player's generated greatsword (TRELLIS.2, prepared by prep_estoc_trellis.py with
name SM_GreatswordGen and the sword-root frame: grip at origin, guard 8 cm, point 148 cm).

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/sword/ue_import_greatsword_gen.py
(the FBX importer asserts in headless commandlets; the script quits the editor, so the
launcher's exit 1 is expected). Input: artifacts/art/greatsword-2026-11-14/prep-7. Writes
/Game/BossLab/SwordGen (local, not committed), kept apart from /Sword because
ue_import_greatsword.py deletes that folder. The game prefers this greatsword over the
Blender-modelled SM_Greatsword when it is present. The material keeps the enchanted rune
channel: a scalar Glow parameter (driven by the game, like M_SwordRune) lights six glyph
segments down the blade's centre line, found from the mesh's local position.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, 'artifacts/art/greatsword-2026-11-14')
PREP = os.path.join(ART, 'prep-7')
DEST = '/Game/BossLab/SwordGen'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
# Start clean: replacing an existing mesh reuses its stored import settings (scale).
if eal.does_directory_exist(DEST):
    eal.delete_directory(DEST)

def task(filename, name, options=None):
    t = unreal.AssetImportTask()
    t.filename = filename; t.destination_path = DEST; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    if options:
        t.options = options
    tools.import_asset_tasks([t])
    return unreal.load_asset(f'{DEST}/{name}')

base = task(os.path.join(PREP, 'T_GreatswordGen_0.png'), 'T_GreatswordGen_D')
mr = task(os.path.join(PREP, 'T_GreatswordGen_1.png'), 'T_GreatswordGen_MR')
mr.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
mr.set_editor_property('srgb', False)

# Aged steel: generated albedo; glTF packs roughness in G and metallic in B. A roughness
# floor keeps the blade from turning into a mirror under the torches. Every mask channel is
# set explicitly (a new ComponentMask defaults to R+G).
mat = tools.create_asset('M_GreatswordGen', DEST, unreal.Material, unreal.MaterialFactoryNew())
d = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 0)
d.set_editor_property('texture', base)
mel.connect_material_property(d, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 300)
s.set_editor_property('texture', mr); s.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
floor = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -700, 550); floor.set_editor_property('r', .28)
rough = mel.create_material_expression(mat, unreal.MaterialExpressionMax, -350, 300)
mel.connect_material_expressions(s, 'G', rough, 'A'); mel.connect_material_expressions(floor, '', rough, 'B')
mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(s, 'B', unreal.MaterialProperty.MP_METALLIC)
# Rune channel: blade centre line (|x| < 0.9 cm, the fuller), between 22 and 118 cm up the
# blade, broken into six glyph segments; soul-blue emissive scaled by Glow.
RUNE_CODE = '''
float x=abs(P.x), z=P.z;
float lane=1-smoothstep(.5,.9,x);   // (not "line": an HLSL keyword)
float span=smoothstep(20,24,z)*(1-smoothstep(114,120,z));
float seg=frac((z-22)/16); float glyph=smoothstep(.12,.2,seg)*(1-smoothstep(.62,.7,seg));
return float3(.25,.6,1.6)*lane*span*glyph*G;
'''
glow = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -700, 800)
glow.set_editor_property('parameter_name', 'Glow'); glow.set_editor_property('default_value', 1.0)
lp = mel.create_material_expression(mat, unreal.MaterialExpressionLocalPosition, -700, 650)
rune = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -350, 700)
rune.set_editor_property('code', RUNE_CODE); rune.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
pins = []
for n in ('P', 'G'):
    pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
rune.set_editor_property('inputs', pins)
mel.connect_material_expressions(lp, '', rune, 'P'); mel.connect_material_expressions(glow, '', rune, 'G')
mel.connect_material_property(rune, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)

ui = unreal.FbxImportUI()
ui.import_mesh = True; ui.import_as_skeletal = False; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
sm = ui.static_mesh_import_data
sm.set_editor_property('combine_meshes', True)
sm.set_editor_property('import_uniform_scale', 100.0)   # Blender metres -> cm
sm.set_editor_property('auto_generate_collision', False)
sm.set_editor_property('generate_lightmap_u_vs', False)
sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS)
mesh = task(os.path.join(PREP, 'SM_GreatswordGen.fbx'), 'SM_GreatswordGen', ui)
slots = []
for slot in mesh.get_editor_property('static_materials'):
    slot.set_editor_property('material_interface', mat); slots.append(slot)
mesh.set_editor_property('static_materials', slots)
box = mesh.get_bounding_box(); size = box.max - box.min
report = {'SM_GreatswordGen': {'size_cm': [round(size.x, 1), round(size.y, 1), round(size.z, 1)],
                                 'min_cm': [round(box.min.x, 1), round(box.min.y, 1), round(box.min.z, 1)],
                                 'triangles': mesh.get_num_triangles(0), 'material': 'M_GreatswordGen'}}
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'greatsword-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB greatsword gen import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
