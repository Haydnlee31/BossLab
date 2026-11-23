"""Import the Bellbreaker effects pass (2026-11-23): FLUX.1-schnell effect textures, their materials and
the extra Stable Audio move sounds.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/bellbreaker/ue_import_bellbreaker_fx_pass.py
(the script quits the editor, so the launcher's exit 1 is expected). Inputs:
  artifacts/art/bellbreaker-fx-2026-11-23/flux/<name>_s<seed>.png  (flux_fx_textures.py; FLUX.1-schnell, Apache-2.0)
  artifacts/audio-bellbreaker-fx-2026-11-23/wav/*.wav               (sfx_generate.py; Stable Audio Open 1.0, "Powered by Stability AI")
Writes /Game/BossLab/Bellbreaker/FX/T_BB_Fx*, M_BB_Fx{Crack,Dust,Fire,Puddle} and /Game/BossLab/Bellbreaker/Sound/S_*
(local, not committed). Every material reads PerInstanceCustomData 0 as its fade/heat (WardenBellbreaker.cpp,
UpdateBellbreakerFx) and masks the square plane with a radial falloff. Presentation only; no combat rules.
"""
import glob, json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
FLUX = os.path.join(ROOT, 'artifacts/art/bellbreaker-fx-2026-11-23/flux')
WAV = os.path.join(ROOT, 'artifacts/audio-bellbreaker-fx-2026-11-23/wav')
FX, SND = '/Game/BossLab/Bellbreaker/FX', '/Game/BossLab/Bellbreaker/Sound'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {'sounds': [], 'materials': {}}

def task(filename, dest, name):
    t = unreal.AssetImportTask()
    t.filename = filename; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    tools.import_asset_tasks([t])
    return unreal.load_asset(f'{dest}/{name}')

for f in sorted(glob.glob(os.path.join(WAV, '*.wav'))):
    name = 'S_' + os.path.splitext(os.path.basename(f))[0]
    a = task(f, SND, name)
    if a:
        report['sounds'].append([name, round(a.get_editor_property('duration'), 2)])

MASK = 'float2 q=UV*2-1; float m=1-smoothstep(.62,.98,length(q));'
# name: (source image, blend, emissive HLSL returning float3, opacity HLSL or None)
SPECS = {
    'Crack': ('crack_glow_s7', 'add',
              MASK + 'float key=saturate((C.r-C.b)*1.8); float h=saturate(F);'
              'float3 col=lerp(float3(.45,.025,0),float3(3.6,1.15,.22),h*h);'
              'return key*m*col*saturate(h*1.6);', None),
    'Dust': ('dust_puff_s9', 'translucent',
             'return float3(.075,.058,.045)+C*.04;',
             MASK + 'float l=saturate((dot(C,float3(.333,.333,.333))-.07)/.9); return l*m*saturate(F)*.85;'),
    'Fire': ('fire_burst_s4', 'add',
             MASK + 'float h=saturate(F); return C*m*h*lerp(float3(1.2,.35,.08),float3(4.5,3.6,3),h);', None),
    'Puddle': ('slag_puddle_s5', 'add',
               MASK + 'float h=saturate(F); float l=saturate(C.r*1.1-C.b*.4);'
               'return l*m*h*lerp(float3(.7,.06,0),float3(5,2.2,.6),h*h);', None),
}

def custom(mat, code, out, inputs, x, y):
    n = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    pins = []
    for key, _ in inputs:
        p = unreal.CustomInput(); p.set_editor_property('input_name', key); pins.append(p)
    n.set_editor_property('inputs', pins)
    n.set_editor_property('output_type', out)
    n.set_editor_property('code', code)
    for i, (key, (node, pin)) in enumerate(inputs):
        mel.connect_material_expressions(node, pin, n, key)
    return n

eal.make_directory(FX)
for name, (image, blend, emissive, opacity) in SPECS.items():
    tex = task(os.path.join(FLUX, image + '.png'), FX, f'T_BB_Fx{name}')
    tex.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
    tex.set_editor_property('max_texture_size', 512)
    path = f'{FX}/M_BB_Fx{name}'
    mat = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(f'M_BB_Fx{name}', FX, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE if blend == 'add' else unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property('two_sided', True)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -1100, 0)
    s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -1100, 150)
    s.set_editor_property('texture', tex)
    mel.connect_material_expressions(uv, '', s, 'UVs')
    fade = mel.create_material_expression(mat, unreal.MaterialExpressionPerInstanceCustomData, -1100, 450)
    fade.set_editor_property('data_index', 0)
    fade.set_editor_property('const_default_value', 1.0)
    ins = [('UV', (uv, '')), ('C', (s, 'RGB')), ('F', (fade, ''))]
    e = custom(mat, emissive, unreal.CustomMaterialOutputType.CMOT_FLOAT3, ins, -600, 0)
    mel.connect_material_property(e, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    if opacity:
        o = custom(mat, opacity, unreal.CustomMaterialOutputType.CMOT_FLOAT1, ins, -600, 300)
        mel.connect_material_property(o, '', unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(mat)
    report['materials'][f'M_BB_Fx{name}'] = image

eal.save_directory(FX, only_if_is_dirty=False, recursive=True)
eal.save_directory(SND, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ROOT, 'artifacts/art/bellbreaker-fx-2026-11-23/import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB fx pass import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
