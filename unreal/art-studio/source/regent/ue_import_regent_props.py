"""Import the Funeral Regent greybox props and sound cues.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/regent/ue_import_regent_props.py
(the FBX importer reports through Slate, which asserts in headless commandlets; the script
quits the editor when done, so the launcher's exit 1 is expected). Run ue_import_regent.py
first: the skull uses its M_RegentBone.
Inputs: prep_regent_props.py FBX (artifacts/art/regent-moveset-2026-11-09/props/fbx) and
make_regent_audio.py WAVs (.../audio). Writes /Game/BossLab/Regent/Props and /Audio (local,
not committed) and props-import-report.json.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, 'artifacts/art/regent-moveset-2026-11-09')
FBX = os.path.join(ART, 'props/fbx')
TEX = os.path.join(ART, 'props/brass_diya_lantern/textures')
DEST, AUDIO = '/Game/BossLab/Regent/Props', '/Game/BossLab/Regent/Audio'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {}
# Start clean: replacing an existing mesh reuses its stored import settings (scale).
for folder in (DEST, AUDIO):
    if eal.does_directory_exist(folder):
        eal.delete_directory(folder)

def task(filename, dest, name, options=None):
    t = unreal.AssetImportTask()
    t.filename = filename; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    if options:
        t.options = options
    tools.import_asset_tasks([t])
    return unreal.load_asset(f'{dest}/{name}')

def texture(kind):
    tex = task(os.path.join(TEX, f'brass_diya_lantern_{kind}_1k.jpg'), DEST, f'T_RegentLantern_{kind}')
    if kind == 'nor_gl':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb', False)
        tex.set_editor_property('flip_green_channel', True)  # glTF normals are OpenGL (+Y)
    elif kind == 'arm':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
        tex.set_editor_property('srgb', False)
    return tex

def new_material(name):
    mat = tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    return mat

def sample(mat, tex, sampler, y):
    s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -600, y)
    s.set_editor_property('texture', tex); s.set_editor_property('sampler_type', sampler)
    return s

def brass():
    # Darkened, slightly greened funeral brass from the lantern's own PBR set.
    mat = new_material('M_RegentLanternBrass')
    d = sample(mat, texture('diff'), unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, 0)
    tint = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -250, 0)
    tint.set_editor_property('const_b', .55)
    mel.connect_material_expressions(d, 'RGB', tint, 'A')
    mel.connect_material_property(tint, '', unreal.MaterialProperty.MP_BASE_COLOR)
    n = sample(mat, texture('nor_gl'), unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, 300)
    mel.connect_material_property(n, 'RGB', unreal.MaterialProperty.MP_NORMAL)
    m = sample(mat, texture('arm'), unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, 600)
    mel.connect_material_property(m, 'R', unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    mel.connect_material_property(m, 'G', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(m, 'B', unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(mat)
    return mat

def glow(name, colour, blend, opacity=None):
    mat = new_material(name)
    mat.set_editor_property('blend_mode', blend)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('two_sided', True)
    c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    c.set_editor_property('constant', unreal.LinearColor(*colour, 1))
    mel.connect_material_property(c, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    if opacity is not None:
        o = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
        o.set_editor_property('r', opacity)
        mel.connect_material_property(o, '', unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(mat)
    return mat

materials = {
    'brass_diya_lantern': brass(),
    # Dim enough not to bloom into a white blob at the Regent's feet (study capture, 2026-11-09).
    'brass_diya_lantern_glass': glow('M_RegentLanternGlass', (.015, .045, .13), unreal.BlendMode.BLEND_TRANSLUCENT, .35),
    'brass_diya_lantern_flame': glow('M_RegentLanternCore', (.3, .8, 2.4), unreal.BlendMode.BLEND_ADDITIVE),
    'regent_bone': unreal.load_asset('/Game/BossLab/Regent/M_RegentBone'),
    'regent_iron': unreal.load_asset('/Game/BossLab/Materials/MI_BlackIron'),
}

for piece, info in json.load(open(os.path.join(FBX, 'pieces.json'))).items():
    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = False; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
    sm = ui.static_mesh_import_data
    sm.set_editor_property('combine_meshes', True)
    sm.set_editor_property('import_uniform_scale', 100.0)   # Blender metres -> cm
    sm.set_editor_property('auto_generate_collision', False)
    sm.set_editor_property('generate_lightmap_u_vs', False)
    sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    mesh = task(os.path.join(FBX, piece + '.fbx'), DEST, piece, ui)
    if mesh is None:
        report[piece] = {'error': 'missing'}
        continue
    slots = []
    for s in mesh.get_editor_property('static_materials'):
        slot = str(s.get_editor_property('material_slot_name'))
        # Longest matching key first, so "_glass"/"_flame" win over the plain brass name.
        key = max((k for k in materials if slot == k or slot.startswith(k)), key=len, default=None)
        s.set_editor_property('material_interface', materials.get(key))
        slots.append(s)
    mesh.set_editor_property('static_materials', slots)
    box = mesh.get_bounding_box(); size = box.max - box.min
    report[piece] = {'slots': [str(s.get_editor_property('material_slot_name')) for s in slots],
                     'materials': [s.get_editor_property('material_interface').get_name() if s.get_editor_property('material_interface') else None for s in slots],
                     'size_cm': [round(size.x, 1), round(size.y, 1), round(size.z, 1)],
                     'min_cm': [round(box.min.x, 1), round(box.min.y, 1), round(box.min.z, 1)],
                     'triangles': mesh.get_num_triangles(0)}

sounds = []
for wav in sorted(os.listdir(os.path.join(ART, 'audio'))):
    if wav.endswith('.wav'):
        name = os.path.splitext(wav)[0]
        if task(os.path.join(ART, 'audio', wav), AUDIO, name):
            sounds.append(name)
report['audio'] = sounds

for folder in (DEST, AUDIO):
    eal.save_directory(folder, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'props-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB regent props import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
