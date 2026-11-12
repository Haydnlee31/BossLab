"""Import the generated soul-fire censer (TRELLIS.2, prepared by prep_censer_trellis.py).

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/regent/ue_import_censer_gen.py
(the FBX importer asserts in headless commandlets; the script quits the editor, so the
launcher's exit 1 is expected). Input: artifacts/art/censer-2026-11-12/prep. Writes
/Game/BossLab/Regent/Censer (local, not committed), kept apart from /Props because
ue_import_regent_props.py deletes that folder. The game prefers this censer over the
interim SM_RegentCenser when it is present.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, 'artifacts/art/censer-2026-11-12')
PREP = os.path.join(ART, 'prep')
DEST = '/Game/BossLab/Regent/Censer'
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

base = task(os.path.join(PREP, 'T_RegentCenserGen_0.png'), 'T_RegentCenserGen_D')
mr = task(os.path.join(PREP, 'T_RegentCenserGen_1.png'), 'T_RegentCenserGen_MR')
mr.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
mr.set_editor_property('srgb', False)

# Blackened iron and bronze: the generated albedo slightly darkened; glTF packs roughness
# in G and metallic in B. Every mask channel is set explicitly (a new ComponentMask
# defaults to R+G).
mat = tools.create_asset('M_RegentCenserGen', DEST, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property('used_with_instanced_static_meshes', True)
d = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 0)
d.set_editor_property('texture', base)
dark = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -350, 0)
mel.connect_material_expressions(d, 'RGB', dark, 'A'); dark.set_editor_property('const_b', .85)
mel.connect_material_property(dark, '', unreal.MaterialProperty.MP_BASE_COLOR)
s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 300)
s.set_editor_property('texture', mr); s.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
floor = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -700, 550); floor.set_editor_property('r', .3)
rough = mel.create_material_expression(mat, unreal.MaterialExpressionMax, -350, 300)
mel.connect_material_expressions(s, 'G', rough, 'A'); mel.connect_material_expressions(floor, '', rough, 'B')
mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(s, 'B', unreal.MaterialProperty.MP_METALLIC)
# The generator baked the glass panes as opaque near-white panels: treat bright, unsaturated
# albedo as glass lit from inside by the soul fire (blue emissive, flickering).
GLASS_CODE = '''
float3 c=C.rgb; float l=dot(c,float3(.333,.333,.333)); float sat=max(c.r,max(c.g,c.b))-min(c.r,min(c.g,c.b));
float glass=smoothstep(.45,.7,l)*(1-smoothstep(.08,.2,sat));
float flick=.85+.15*sin(Tm.x*11)*sin(Tm.x*6.3+1.7);
return float3(.08,.35,1.6)*glass*(.6+.4*l)*flick*2.2;
'''
glass = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -350, 650)
glass.set_editor_property('code', GLASS_CODE); glass.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
pins = []
for n in ('C', 'Tm'):
    pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
glass.set_editor_property('inputs', pins)
tm = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -700, 800)
mel.connect_material_expressions(d, 'RGB', glass, 'C'); mel.connect_material_expressions(tm, '', glass, 'Tm')
mel.connect_material_property(glass, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
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
mesh = task(os.path.join(PREP, 'SM_RegentCenserGen.fbx'), 'SM_RegentCenserGen', ui)
slots = []
for slot in mesh.get_editor_property('static_materials'):
    slot.set_editor_property('material_interface', mat); slots.append(slot)
mesh.set_editor_property('static_materials', slots)
box = mesh.get_bounding_box(); size = box.max - box.min
report = {'SM_RegentCenserGen': {'size_cm': [round(size.x, 1), round(size.y, 1), round(size.z, 1)],
                                 'min_cm': [round(box.min.x, 1), round(box.min.y, 1), round(box.min.z, 1)],
                                 'triangles': mesh.get_num_triangles(0), 'material': 'M_RegentCenserGen'}}
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'censer-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB censer gen import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
