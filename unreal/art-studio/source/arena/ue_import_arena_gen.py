"""Import the generated arena props (TRELLIS.2, prepared by prep_arena_gen.py).

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/arena/ue_import_arena_gen.py
(the FBX importer asserts in headless commandlets; the script quits the editor, so the
launcher's exit 1 is expected). Input: artifacts/art/arena-props-2026-11-14/prep. Writes
/Game/BossLab/Dungeon/Gen (local, not committed), apart from /Props, which
ue_import_props.py deletes. One material per prop: generated albedo, roughness from G (at
least .45: stone and bone, never glossy), metallic from B. WardenDungeon.cpp places them as
NoCollision dressing outside the fight floor when present.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, 'artifacts/art/arena-props-2026-11-14')
PREP = os.path.join(ART, 'prep')
DEST = '/Game/BossLab/Dungeon/Gen'
NAMES = ['Throne', 'Sarcophagus', 'Angel', 'Ossuary', 'Candelabrum', 'Bier']
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
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

report = {}
for name in NAMES:
    stem = f'{name}Gen'
    base = task(os.path.join(PREP, f'T_{stem}_0.png'), f'T_{stem}_D')
    mr = task(os.path.join(PREP, f'T_{stem}_1.png'), f'T_{stem}_MR')
    mr.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
    mr.set_editor_property('srgb', False)
    mat = tools.create_asset(f'M_{stem}', DEST, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    d = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 0)
    d.set_editor_property('texture', base)
    mel.connect_material_property(d, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
    s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 300)
    s.set_editor_property('texture', mr); s.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    floor = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -700, 550); floor.set_editor_property('r', .45)
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionMax, -350, 300)
    mel.connect_material_expressions(s, 'G', rough, 'A'); mel.connect_material_expressions(floor, '', rough, 'B')
    mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(s, 'B', unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(mat)
    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = False; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
    sm = ui.static_mesh_import_data
    sm.set_editor_property('combine_meshes', True)
    sm.set_editor_property('import_uniform_scale', 100.0)
    sm.set_editor_property('auto_generate_collision', False)
    sm.set_editor_property('generate_lightmap_u_vs', False)
    sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS)
    mesh = task(os.path.join(PREP, f'SM_{stem}.fbx'), f'SM_{stem}', ui)
    if mesh is None:
        report[name] = {'error': 'mesh missing'}; continue
    slots = []
    for slot in mesh.get_editor_property('static_materials'):
        slot.set_editor_property('material_interface', mat); slots.append(slot)
    mesh.set_editor_property('static_materials', slots)
    box = mesh.get_bounding_box(); size = box.max - box.min
    report[name] = {'size_cm': [round(size.x, 1), round(size.y, 1), round(size.z, 1)], 'triangles': mesh.get_num_triangles(0)}
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'arena-gen-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB arena gen import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
