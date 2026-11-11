"""Import the generated witness skull (TRELLIS.2, prepared by prep_skull_trellis.py).

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/regent/ue_import_skull_gen.py
(the FBX importer asserts in headless commandlets; the script quits the editor, so the
launcher's exit 1 is expected). Input: artifacts/art/skull-2026-11-11/prep. Writes
/Game/BossLab/Regent/Skull (local, not committed), kept apart from /Props because
ue_import_regent_props.py deletes that folder. The game prefers this skull over the
interim SM_RegentSkull when it is present.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, 'artifacts/art/skull-2026-11-11')
PREP = os.path.join(ART, 'prep')
DEST = '/Game/BossLab/Regent/Skull'
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

base = task(os.path.join(PREP, 'T_RegentSkullGen_0.png'), 'T_RegentSkullGen_D')
orm = task(os.path.join(PREP, 'T_RegentSkullGen_1.png'), 'T_RegentSkullGen_MR')
orm.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
orm.set_editor_property('srgb', False)

# Bone: the generated albedo, slightly darkened and cooled to sit under the blue soul-fire;
# glTF packs roughness in G. Never metallic.
mat = tools.create_asset('M_RegentSkullGen', DEST, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property('used_with_instanced_static_meshes', True)
d = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 0)
d.set_editor_property('texture', base)
tint = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -700, 250)
tint.set_editor_property('constant', unreal.LinearColor(.78, .78, .82, 1))
mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -350, 100)
mel.connect_material_expressions(d, 'RGB', mul, 'A'); mel.connect_material_expressions(tint, '', mul, 'B')
mel.connect_material_property(mul, '', unreal.MaterialProperty.MP_BASE_COLOR)
r = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 450)
r.set_editor_property('texture', orm); r.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
lift = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -700, 700); lift.set_editor_property('r', .55)
mx = mel.create_material_expression(mat, unreal.MaterialExpressionMax, -350, 450)
mel.connect_material_expressions(r, 'G', mx, 'A'); mel.connect_material_expressions(lift, '', mx, 'B')
mel.connect_material_property(mx, '', unreal.MaterialProperty.MP_ROUGHNESS)
spec = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -350, 700); spec.set_editor_property('r', .35)
mel.connect_material_property(spec, '', unreal.MaterialProperty.MP_SPECULAR)
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
mesh = task(os.path.join(PREP, 'SM_RegentSkullGen.fbx'), 'SM_RegentSkullGen', ui)
slots = []
for s in mesh.get_editor_property('static_materials'):
    s.set_editor_property('material_interface', mat); slots.append(s)
mesh.set_editor_property('static_materials', slots)
box = mesh.get_bounding_box(); size = box.max - box.min
report = {'SM_RegentSkullGen': {'size_cm': [round(size.x, 1), round(size.y, 1), round(size.z, 1)],
                                'min_cm': [round(box.min.x, 1), round(box.min.y, 1), round(box.min.z, 1)],
                                'triangles': mesh.get_num_triangles(0), 'material': 'M_RegentSkullGen'}}
interim = unreal.load_asset('/Game/BossLab/Regent/Props/SM_RegentSkull')
if interim:
    ib = interim.get_bounding_box(); isz = ib.max - ib.min
    report['SM_RegentSkull (interim)'] = {'size_cm': [round(isz.x, 1), round(isz.y, 1), round(isz.z, 1)]}
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'skull-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB skull gen import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
