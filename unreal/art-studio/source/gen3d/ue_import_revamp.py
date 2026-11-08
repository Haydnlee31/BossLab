"""Import the rigged revamp characters as skeletal meshes on SK_Mannequin.

Run headless: ./scripts/bosslab-unreal python unreal/art-studio/source/gen3d/ue_import_revamp.py
Creates /Game/BossLab/Revamp/{SKM_RevampPlayer, SKM_RevampRegent}, their textures and
one masked material each (base colour + roughness/metal).
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
RIG = os.path.join(ROOT, 'artifacts/art/claude-revamp-2026-11-09/rig')
DEST = '/Game/BossLab/Revamp'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
skeleton = unreal.load_asset('/Game/Characters/Mannequins/Meshes/SK_Mannequin')
report = {}

def import_task(filename, name, options=None):
    t = unreal.AssetImportTask()
    t.filename = filename; t.destination_path = DEST; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    if options:
        t.options = options
    tools.import_asset_tasks([t])
    return [str(p) for p in t.imported_object_paths]

def texture(path, name, srgb):
    import_task(path, name)
    tex = unreal.load_asset(f'{DEST}/{name}')
    tex.set_editor_property('srgb', srgb)
    if not srgb:
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
    return tex

def get_or_create(name, cls, factory):
    # Rebuild in place: deleting an asset the meshes still reference fails silently.
    path = f'{DEST}/{name}'
    asset = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(name, DEST, cls, factory)
    if asset is None:
        raise RuntimeError('could not create ' + path)
    return asset

def character_material(name, base_tex, mr_tex):
    # Direct texture samples, one material per character: headless compiles do not
    # register instance parameters reliably, which left instances on default textures.
    mat = get_or_create(name, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
    mat.set_editor_property('two_sided', True)
    mat.set_editor_property('opacity_mask_clip_value', 0.5)
    # Standalone -game cannot add usage flags at runtime; without this it renders the default material.
    mat.set_editor_property('used_with_skeletal_mesh', True)
    base = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, 0)
    base.set_editor_property('texture', base_tex)
    mr = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -500, 300)
    mr.set_editor_property('texture', mr_tex)
    mr.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    mel.connect_material_property(base, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(base, 'A', unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.connect_material_property(mr, 'G', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(mr, 'B', unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(mat)
    return mat

for key, stem in (('player', 'SKM_RevampPlayer'), ('regent', 'SKM_RevampRegent')):
    folder = os.path.join(RIG, key)
    base_tex = texture(os.path.join(folder, f'{stem}_BaseColor.png'), f'T_{stem[4:]}_BaseColor', True)
    mr_tex = texture(os.path.join(folder, f'{stem}_MetalRough.png'), f'T_{stem[4:]}_MetalRough', False)
    mi = character_material(f'M_{stem[4:]}', base_tex, mr_tex)

    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = True; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    ui.skeleton = skeleton
    ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
    ui.create_physics_asset = False
    sm = ui.skeletal_mesh_import_data
    sm.set_editor_property('import_morph_targets', False)
    sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    sm.set_editor_property('use_t0_as_ref_pose', False)
    paths = import_task(os.path.join(folder, f'{stem}.fbx'), stem, ui)
    mesh = unreal.load_asset(f'{DEST}/{stem}')
    if mesh is None:
        report[key] = {'imported': paths, 'error': 'mesh missing'}
        continue
    slots = []
    for m in mesh.get_editor_property('materials'):
        slots.append(unreal.SkeletalMaterial(material_interface=mi, material_slot_name=m.get_editor_property('material_slot_name')))
    mesh.set_editor_property('materials', slots)
    mesh_mats = [str(m.get_editor_property('material_interface').get_path_name()) if m.get_editor_property('material_interface') else None
                 for m in mesh.get_editor_property('materials')]
    b = mesh.get_bounds()
    report[key] = {'imported': paths, 'skeleton': mesh.get_editor_property('skeleton').get_path_name(),
                   'materials': mesh_mats, 'bounds_extent': [b.box_extent.x, b.box_extent.y, b.box_extent.z],
                   'bounds_origin': [b.origin.x, b.origin.y, b.origin.z]}

# Superseded parameterised material/instances from the first import attempt.
for old in ('M_RevampCharacter', 'MI_RevampPlayer', 'MI_RevampRegent'):
    if eal.does_asset_exist(f'{DEST}/{old}'):
        eal.delete_asset(f'{DEST}/{old}')
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(RIG, 'ue-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB revamp import ' + json.dumps(report))
