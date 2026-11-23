"""Import the Bellbreaker rig (rig_fit.py, custom-proportion skeleton) as a skeletal mesh on its OWN
skeleton, 2026-11-17. The arms were lengthened (joint_offsets) to the mesh's ~1.6x mannequin arms,
so it is not index-compatible with SK_Mannequin: mannequin clips need an IK retargeter next.
Static study: no moves, AI or game wiring. Run in the editor:
./scripts/bosslab-unreal editor unreal/art-studio/source/bellbreaker/ue_import_bellbreaker_rig.py
Writes /Game/BossLab/Bellbreaker/Rig (local). Adapted from ue_import_dead_gen.py.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
ART = os.path.join(ROOT, os.environ.get('BOSSLAB_BB_ART', 'artifacts/art/bellbreaker-boss-2026-11-18'))   # 2026-11-18 refined model (11-17 rig kept for rollback)
SRC = os.path.join(ART, os.environ.get('BOSSLAB_BB_RIG_OUT', 'rig-v3/out'))   # 2026-11-18 v3 model (bald, proportional); 'rig/out' = the earlier bulky v2
DEST = '/Game/BossLab/Bellbreaker/Rig'
STEM = 'SKM_BellbreakerRig'
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

base = task(os.path.join(SRC, f'{STEM}_BaseColor.png'), 'T_BellbreakerRig_D')
mr = task(os.path.join(SRC, f'{STEM}_MetalRough.png'), 'T_BellbreakerRig_MR')
mr.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
mr.set_editor_property('srgb', False)

# Old bone: generated albedo slightly darkened, never metallic, rough. No emissive: the
# generated shins are near-black, so any dark-crevice glow lit the legs solid blue (two tries).
mat = tools.create_asset('M_BellbreakerRig', DEST, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property('two_sided', True)
mat.set_editor_property('used_with_skeletal_mesh', True)
d = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -700, 0)
d.set_editor_property('texture', base)
dark = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -350, 0)
mel.connect_material_expressions(d, 'RGB', dark, 'A'); dark.set_editor_property('const_b', .92)
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
ui.skeleton = None   # its own skeleton (custom arm lengths)
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
    # Modelled iron brow band (rig_fit headband, 2026-11-18): its own dark forged-iron material.
    band = tools.create_asset('M_BellbreakerBand', DEST, unreal.Material, unreal.MaterialFactoryNew())
    band.set_editor_property('used_with_skeletal_mesh', True)
    pos = mel.create_material_expression(band, unreal.MaterialExpressionWorldPosition, -800, 0)
    cn = mel.create_material_expression(band, unreal.MaterialExpressionCustom, -400, 0)
    pin = unreal.CustomInput(); pin.set_editor_property('input_name', 'P'); cn.set_editor_property('inputs', [pin])
    cn.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    cn.set_editor_property('code', 'float n=frac(sin(dot(floor(P.xy*.35+P.z*.2),float2(12.9898,78.233)))*43758.5453);'
                                   'float h=frac(sin(dot(floor(P.yz*1.7),float2(39.3,11.1)))*9731.1);'
                                   'return lerp(float3(.035,.031,.028),float3(.075,.062,.05),n*.6+h*.25);')
    mel.connect_material_expressions(pos, '', cn, 'P'); mel.connect_material_property(cn, '', unreal.MaterialProperty.MP_BASE_COLOR)
    for prop, v in ((unreal.MaterialProperty.MP_METALLIC, .85), (unreal.MaterialProperty.MP_ROUGHNESS, .46)):
        k = mel.create_material_expression(band, unreal.MaterialExpressionConstant, -400, 300); k.set_editor_property('r', v)
        mel.connect_material_property(k, '', prop)
    mel.recompile_material(band)
    slots = []
    for m in mesh.get_editor_property('materials'):
        name = m.get_editor_property('material_slot_name')
        slots.append(unreal.SkeletalMaterial(material_interface=band if str(name) == 'Band' else mat, material_slot_name=name))
    mesh.set_editor_property('materials', slots)
    b = mesh.get_bounds()
    report = {STEM: {'skeleton': mesh.get_editor_property('skeleton').get_path_name(), 'slots': len(slots),
                     'bounds_extent': [round(b.box_extent.x, 1), round(b.box_extent.y, 1), round(b.box_extent.z, 1)],
                     'bounds_origin': [round(b.origin.x, 1), round(b.origin.y, 1), round(b.origin.z, 1)],
                     'material': 'M_BellbreakerRig', 'slot_names': [str(m.get_editor_property('material_slot_name')) for m in slots]}}
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ART, 'rig-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB bellbreaker rig import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
