"""Import the Bellbreaker readiness-pass assets (2026-11-23): move sounds and forge arena props.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/bellbreaker/ue_import_readiness.py
(the FBX importer asserts in headless commandlets; the script quits the editor, so the launcher's exit 1 is
expected). Inputs:
  artifacts/audio-bellbreaker-moves-2026-11-23/wav/*.wav  (Stable Audio Open 1.0 via sfx_generate.py; Stability AI
      Community License, "Powered by Stability AI", see CREDITS.md) -> /Game/BossLab/Bellbreaker/Sound/S_<name>
  artifacts/art/bellbreaker-arena-props-2026-11-23/prepped (FLUX.1-schnell image -> TRELLIS.2 -> prep_arena_prop.py)
      -> /Game/BossLab/Bellbreaker/ArenaProps (SM_BB_*, M_BB_*; local, not committed)
Presentation only; no combat rules.
"""
import glob, json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
WAV = os.path.join(ROOT, 'artifacts/audio-bellbreaker-moves-2026-11-23/wav')
PREP = os.path.join(ROOT, 'artifacts/art/bellbreaker-arena-props-2026-11-23/prepped')
SND, DEST = '/Game/BossLab/Bellbreaker/Sound', '/Game/BossLab/Bellbreaker/ArenaProps'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {'sounds': [], 'props': {}}

def task(filename, dest, name, options=None):
    t = unreal.AssetImportTask()
    t.filename = filename; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    if options:
        t.options = options
    tools.import_asset_tasks([t])
    return unreal.load_asset(f'{dest}/{name}')

for f in sorted(glob.glob(os.path.join(WAV, '*.wav'))):
    name = 'S_' + os.path.splitext(os.path.basename(f))[0]
    a = task(f, SND, name)
    if a:
        report['sounds'].append([name, round(a.get_editor_property('duration'), 2)])

if eal.does_directory_exist(DEST):
    eal.delete_directory(DEST)
eal.make_directory(DEST)
for name in ('SM_BB_CrackedBell', 'SM_BB_BellMould', 'SM_BB_BellFrame', 'SM_BB_BellShards', 'SM_BB_Crucible'):
    stem = name[3:]
    if not os.path.isfile(os.path.join(PREP, name + '.fbx')):
        continue
    base = task(os.path.join(PREP, f'T_{stem}_0.png'), DEST, f'T_{stem}_D')
    mr = task(os.path.join(PREP, f'T_{stem}_1.png'), DEST, f'T_{stem}_MR')
    mr.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
    mr.set_editor_property('srgb', False)
    mat = tools.create_asset(f'M_{stem}', DEST, unreal.Material, unreal.MaterialFactoryNew())
    d = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 0)
    d.set_editor_property('texture', base)
    dark = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -350, 0)
    mel.connect_material_expressions(d, 'RGB', dark, 'A'); dark.set_editor_property('const_b', .8)
    mel.connect_material_property(dark, '', unreal.MaterialProperty.MP_BASE_COLOR)
    s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 300)
    s.set_editor_property('texture', mr); s.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    floor = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -700, 550); floor.set_editor_property('r', .35)
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
    mesh = task(os.path.join(PREP, name + '.fbx'), DEST, name, ui)
    slots = []
    for slot in mesh.get_editor_property('static_materials'):
        slot.set_editor_property('material_interface', mat); slots.append(slot)
    mesh.set_editor_property('static_materials', slots)
    box = mesh.get_bounding_box(); size = box.max - box.min
    report['props'][name] = {'size_cm': [round(size.x, 1), round(size.y, 1), round(size.z, 1)], 'triangles': mesh.get_num_triangles(0)}

# Performance: the 180k-triangle Bellfounder shipped with a single LOD. Generate two reduced LODs so the boss
# costs less when he fills less of the screen (reversible: regenerate_lod(mesh, 1)).
boss = unreal.load_asset('/Game/BossLab/Bellbreaker/Bellfounder/SKM_Bellfounder')
if boss and os.environ.get('BOSSLAB_BB_SKIP_LOD') != '1':
    ok = unreal.EditorSkeletalMeshLibrary.regenerate_lod(boss, 3, False, False)
    report['boss_lods'] = {'ok': bool(ok), 'lods': boss.get_lod_num() if hasattr(boss, 'get_lod_num') else None}
    eal.save_asset('/Game/BossLab/Bellbreaker/Bellfounder/SKM_Bellfounder', only_if_is_dirty=False)
eal.save_directory(SND, only_if_is_dirty=False, recursive=True)
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ROOT, 'artifacts/art/bellbreaker-arena-props-2026-11-23/import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB readiness import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
