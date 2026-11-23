"""Import the opt-in Bellfounder. Use BOSSLAB_BELLFOUNDER_READBACK=1 to check a fresh reload."""
import hashlib
import json
import os
import re
import struct
import traceback
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[4]
STUDY = ROOT / 'artifacts/art/bellbreaker-remodel-20261120'
PLAYABLE = STUDY / 'playable'
MAPS = ROOT / 'artifacts/art/bellfounder-hires-20261120'
DEST = '/Game/BossLab/Bellbreaker/Bellfounder'
RIG = '/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig'
MESH = 'SKM_Bellfounder'
SOURCE = PLAYABLE / 'SKM_BellbreakerRemodel.fbx'
MATERIAL = unreal.MaterialProperty
SAMPLER = unreal.MaterialSamplerType
COMPRESS = unreal.TextureCompressionSettings
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
TEXTURES = {
    'BaseColor': (MAPS / 'Bellfounder_BaseColor_4K.png', COMPRESS.TC_DEFAULT, True, SAMPLER.SAMPLERTYPE_COLOR),
    'ORM': (MAPS / 'Bellfounder_ORM_4K.png', COMPRESS.TC_MASKS, False, SAMPLER.SAMPLERTYPE_MASKS),
    'Normal': (MAPS / 'Bellfounder_Normal_4K.png', COMPRESS.TC_NORMALMAP, False, SAMPLER.SAMPLERTYPE_NORMAL),
}
CHANNELS = {'BASE_COLOR': ('BaseColor', 'RGB'), 'AMBIENT_OCCLUSION': ('ORM', 'R'),
            'ROUGHNESS': ('ORM', 'G'), 'METALLIC': ('ORM', 'B'), 'NORMAL': ('Normal', 'RGB')}
BODY_SLOTS = {'RemodelBody', 'RemodelHardplate'}


def asset(name):
    return unreal.load_asset(DEST + '/' + name)


def slot_kind(slot):
    return re.sub(r'[._]\d+$', '', str(slot.material_slot_name))


def material_path(kind):
    return DEST + '/M_Bellfounder_' + kind


def import_asset(source, name, options=None):
    assert source.is_file(), source
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = DEST
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = False
    if options:
        task.options = options
    TOOLS.import_asset_tasks([task])
    result = asset(name)
    assert result, f'Failed to import {name}: {task.imported_object_paths}'
    return result


def build_body_material(kind, textures):
    name = 'M_Bellfounder_' + kind
    mat = asset(name) if EAL.does_asset_exist(DEST + '/' + name) else None
    if mat:
        MEL.delete_all_material_expressions(mat)
    else:
        mat = TOOLS.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property('used_with_skeletal_mesh', True)
    mat.set_editor_property('two_sided', False)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_OPAQUE)
    nodes = {}
    for row, (key, tex) in enumerate(textures.items()):
        node = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -450, 230 * row)
        node.set_editor_property('texture', tex)
        node.set_editor_property('sampler_type', TEXTURES[key][3])
        nodes[key] = node
    for prop, (key, channel) in CHANNELS.items():
        assert MEL.connect_material_property(nodes[key], channel, getattr(MATERIAL, 'MP_' + prop)), prop
    MEL.recompile_material(mat)
    return mat


def perform_import(skeleton):
    for source, _, _, _ in TEXTURES.values():
        with source.open('rb') as stream:
            header = stream.read(24)
        assert header[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', header[16:24]) == (4096, 4096), source
    assert SOURCE.is_file(), SOURCE
    EAL.make_directory(DEST)
    textures = {}
    for key, (source, mode, srgb, _) in TEXTURES.items():
        if os.environ.get('BOSSLAB_BELLFOUNDER_MESH_ONLY') == '1':
            textures[key] = asset('T_Bellfounder_' + key)
            assert textures[key]
            continue
        tex = import_asset(source, 'T_Bellfounder_' + key)
        tex.set_editor_property('compression_settings', mode)
        tex.set_editor_property('srgb', srgb)
        if key == 'Normal':
            tex.set_editor_property('flip_green_channel', False)  # authored in DirectX tangent convention
        textures[key] = tex
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = True
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    options.skeleton = skeleton
    options.import_materials = options.import_textures = options.import_animations = options.create_physics_asset = False
    options.skeletal_mesh_import_data.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    options.skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose', False)
    options.skeletal_mesh_import_data.set_editor_property('update_skeleton_reference_pose', False)
    mesh = import_asset(SOURCE, MESH, options)
    assert mesh.get_editor_property('skeleton') == skeleton
    slots = list(mesh.get_editor_property('materials'))
    kinds = {slot_kind(s) for s in slots}
    assert kinds == BODY_SLOTS, kinds
    if os.environ.get('BOSSLAB_BELLFOUNDER_MESH_ONLY') == '1':
        bound = {kind: unreal.load_asset(material_path(kind)) for kind in BODY_SLOTS}
    else:
        bound = {kind: build_body_material(kind, textures) for kind in BODY_SLOTS}
    for i, slot in enumerate(slots):
        slots[i] = unreal.SkeletalMaterial(material_interface=bound[slot_kind(slot)], material_slot_name=slot.material_slot_name)
    mesh.set_editor_property('materials', slots)
    if os.environ.get('BOSSLAB_BELLFOUNDER_MESH_ONLY') == '1':
        assert EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
    else:
        assert EAL.save_directory(DEST, only_if_is_dirty=False, recursive=True)


def imported_size(tex):
    tags = EAL.get_tag_values(tex.get_path_name())
    return list(map(int, str(tags['Dimensions']).split('x')))


def readback(skeleton, report):
    mesh = asset(MESH)
    assert mesh and mesh.get_editor_property('skeleton') == skeleton
    report.update(asset=mesh.get_path_name(), skeleton=skeleton.get_path_name(), textures={}, slots={}, channels={})
    for key, (_, mode, srgb, _) in TEXTURES.items():
        tex = asset('T_Bellfounder_' + key)
        spec = {'size': imported_size(tex), 'sampled_size_at_readback': [tex.blueprint_get_size_x(), tex.blueprint_get_size_y()], 'sRGB': tex.get_editor_property('srgb'),
                'compression': str(tex.get_editor_property('compression_settings')), 'flip_green': tex.get_editor_property('flip_green_channel'),
                'lod_bias': tex.get_editor_property('lod_bias'), 'max_texture_size': tex.get_editor_property('max_texture_size')}
        report['textures'][key] = spec
        assert spec['size'] == [4096, 4096] and spec['sRGB'] == srgb and tex.get_editor_property('compression_settings') == mode, spec
        assert key != 'Normal' or spec['flip_green'] is False
    for slot in mesh.get_editor_property('materials'):
        kind = slot_kind(slot)
        mat = slot.material_interface
        report['slots'][str(slot.material_slot_name)] = mat.get_path_name() if mat else None
        assert mat and mat == unreal.load_asset(material_path(kind)), (kind, str(mat))
        if kind in BODY_SLOTS:
            channels = report['channels'][kind] = {}
            for prop, (key, channel) in CHANNELS.items():
                p = getattr(MATERIAL, 'MP_' + prop)
                node = MEL.get_material_property_input_node(mat, p)
                out = MEL.get_material_property_input_node_output_name(mat, p)
                channels[prop] = {'texture': node.texture.get_name(), 'output': out, 'sampler': str(node.sampler_type)}
                assert node.texture == asset('T_Bellfounder_' + key) and node.sampler_type == TEXTURES[key][3]
                assert out == channel or (channel == 'RGB' and out == ''), (prop, key, out)
    assert {slot_kind(s) for s in mesh.get_editor_property('materials')} == BODY_SLOTS
    editor_mesh = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    if editor_mesh:
        report['lod0_vertices'] = editor_mesh.get_num_verts(mesh, 0)
        report['lod0_sections'] = editor_mesh.get_num_sections(mesh, 0)
        report['lod_count'] = unreal.SkeletalMeshEditorSubsystem.get_lod_count(mesh)
    extent = mesh.get_bounds().box_extent
    report['half_extent_cm'] = [extent.x, extent.y, extent.z]
    old = unreal.load_asset('/Game/BossLab/Bellbreaker/ForgeShoulder/SKM_BellbreakerForgeShoulder')
    old_materials = {}
    for old_slot in old.get_editor_property('materials'):
        old_mat = old_slot.material_interface
        if isinstance(old_mat, unreal.Material):
            old_materials[str(old_slot.material_slot_name)] = {
                t.get_name(): imported_size(t)
                for t in MEL.get_used_textures(old_mat) if isinstance(t, unreal.Texture2D)}
    report['default_mesh_material_textures'] = old_materials
    report['original_rig_atlas_imported_dimensions'] = {
        name: imported_size(unreal.load_asset('/Game/BossLab/Bellbreaker/Rig/' + name))
        for name in ('T_BellbreakerRig_D', 'T_BellbreakerRig_MR')}
    report['source_fbx_sha256'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()


readonly = os.environ.get('BOSSLAB_BELLFOUNDER_READBACK') == '1'
report = {'ok': False, 'fresh_readback': readonly}
try:
    skeleton = unreal.load_asset(RIG).get_editor_property('skeleton')
    if not readonly:
        perform_import(skeleton)
    readback(skeleton, report)
    report['ok'] = True
except Exception:
    report['error'] = traceback.format_exc()
finally:
    (STUDY / ('ue-readback.json' if readonly else 'ue-import.json')).write_text(json.dumps(report, indent=2))
    unreal.log('BOSSLAB bellfounder ' + str(report))
    if not readonly:
        unreal.SystemLibrary.quit_editor()
