"""Import the generated raised-dead skeleton (TRELLIS.2, rigged by rig_fit.py) as a skeletal
mesh on the mannequin's own skeleton, so the walk/attack clips play on it unchanged.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/regent/ue_import_dead_gen.py
(the FBX importer asserts in headless commandlets; the script quits the editor, so the
launcher's exit 1 is expected). Input: artifacts/art/skeleton-2026-11-13/rig/out. Writes
/Game/BossLab/Regent/Dead (local, not committed). rig_fit.py keeps every bone's name,
order and local translation identical to SKM_Manny_Simple (rotations-only re-rest of the
forearms), which is what makes SK_Mannequin valid for it. The game prefers this mesh over
the gaunt mannequin + separate skull when present.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, 'artifacts/art/skeleton-2026-11-13')
SRC = os.path.join(ART, 'rig/out')
DEST = '/Game/BossLab/Regent/Dead'
STEM = 'SKM_RegentDeadGen'
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

base = task(os.path.join(SRC, f'{STEM}_BaseColor.png'), 'T_RegentDeadGen_D')
mr = task(os.path.join(SRC, f'{STEM}_MetalRough.png'), 'T_RegentDeadGen_MR')
mr.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
mr.set_editor_property('srgb', False)

# Old bone: generated albedo slightly darkened, never metallic, rough. No emissive: the
# generated shins are near-black, so any dark-crevice glow lit the legs solid blue (two tries).
mat = tools.create_asset('M_RegentDeadGen', DEST, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property('two_sided', True)
mat.set_editor_property('used_with_skeletal_mesh', True)
d = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 0)
d.set_editor_property('texture', base)
dark = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -350, 0)
mel.connect_material_expressions(d, 'RGB', dark, 'A'); dark.set_editor_property('const_b', .8)
mel.connect_material_property(dark, '', unreal.MaterialProperty.MP_BASE_COLOR)
s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 300)
s.set_editor_property('texture', mr); s.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
floor = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -700, 550); floor.set_editor_property('r', .6)
rough = mel.create_material_expression(mat, unreal.MaterialExpressionMax, -350, 300)
mel.connect_material_expressions(s, 'G', rough, 'A'); mel.connect_material_expressions(floor, '', rough, 'B')
mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
mel.recompile_material(mat)

ui = unreal.FbxImportUI()
ui.import_mesh = True; ui.import_as_skeletal = True; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
ui.skeleton = unreal.load_asset('/Game/Characters/Mannequins/Meshes/SK_Mannequin')
ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
ui.create_physics_asset = False
sm = ui.skeletal_mesh_import_data
sm.set_editor_property('import_morph_targets', False)
sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
sm.set_editor_property('use_t0_as_ref_pose', False)
mesh = task(os.path.join(SRC, f'{STEM}.fbx'), STEM, ui)
report = {}
if mesh is None:
    report = {'error': 'mesh missing'}
else:
    slots = []
    for m in mesh.get_editor_property('materials'):
        slots.append(unreal.SkeletalMaterial(material_interface=mat, material_slot_name=m.get_editor_property('material_slot_name')))
    mesh.set_editor_property('materials', slots)
    b = mesh.get_bounds()
    report = {STEM: {'skeleton': mesh.get_editor_property('skeleton').get_path_name(), 'slots': len(slots),
                     'bounds_extent': [round(b.box_extent.x, 1), round(b.box_extent.y, 1), round(b.box_extent.z, 1)],
                     'bounds_origin': [round(b.origin.x, 1), round(b.origin.y, 1), round(b.origin.z, 1)],
                     'material': 'M_RegentDeadGen'}}
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'dead-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB dead gen import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
