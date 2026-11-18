"""Import the Bellbreaker's generated sounds and the shockwave ring material, 2026-11-18.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/bellbreaker/ue_import_bellbreaker_fx.py
Inputs: artifacts/audio-bellbreaker-2026-11-18/wav/*.wav (Stable Audio Open 1.0 via sfx_generate.py, converted
from FLAC with afconvert; Stability AI Community License, see CREDITS.md). Writes /Game/BossLab/Bellbreaker/Sound
(S_<name>_v<k>) and /Game/BossLab/Bellbreaker/FX/M_BB_Shockwave (local, not committed):
unlit additive two-sided ring on a plane's UVs; scalar parameter Fade (0-1) dims it as it expands.
Presentation only; no combat rules.
"""
import glob, json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
WAV = os.path.join(ROOT, 'artifacts/audio-bellbreaker-2026-11-18/wav')
SND, FX = '/Game/BossLab/Bellbreaker/Sound', '/Game/BossLab/Bellbreaker/FX'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
MP = unreal.MaterialProperty
for d in (SND, FX):
    if eal.does_directory_exist(d):
        eal.delete_directory(d)
report = {'sounds': []}
for f in sorted(glob.glob(os.path.join(WAV, '*.wav'))):
    name = 'S_' + os.path.splitext(os.path.basename(f))[0]
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = SND; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    tools.import_asset_tasks([t])
    a = unreal.load_asset(f'{SND}/{name}')
    if a:
        report['sounds'].append([name, round(a.get_editor_property('duration'), 2)])

m = tools.create_asset('M_BB_Shockwave', FX, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
m.set_editor_property('two_sided', True)
uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, 0)
tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 150)
fade = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, 300)
fade.set_editor_property('parameter_name', 'Fade'); fade.set_editor_property('default_value', 1.0)
n = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -450, 0)
pins = []
for k in ('UV', 'T', 'F'):
    p = unreal.CustomInput(); p.set_editor_property('input_name', k); pins.append(p)
n.set_editor_property('inputs', pins)
n.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
n.set_editor_property('code',
    'float2 q=UV*2-1; float d=length(q); float a=atan2(q.y,q.x);'
    # Thin travelling crest with a ragged, flickering edge (value noise along the angle, not radial
    # stripes) and a faint dust wash just behind it; nothing inside 60% or outside the crest. v2 2026-11-18:
    # the first version filled the disc with bright wedges.
    'float u=a*6+T*2; float i0=floor(u); float fr=frac(u);'
    'float h0=frac(sin(i0*127.1)*43758.5); float h1=frac(sin((i0+1)*127.1)*43758.5);'
    'float rag=lerp(h0,h1,smoothstep(0,1,fr));'
    'float crest=exp(-pow((d-.955+.03*rag)/.022,2))*(.55+.45*rag);'
    'float wash=.10*smoothstep(.6,.93,d)*smoothstep(1.0,.95,d);'
    'return float3(1.5,.95,.42)*(crest*1.3+wash)*F;')
for node, pin in ((uv, 'UV'), (tm, 'T'), (fade, 'F')):
    mel.connect_material_expressions(node, '', n, pin)
mel.connect_material_property(n, '', MP.MP_EMISSIVE_COLOR)
mel.recompile_material(m)
eal.save_directory(SND, only_if_is_dirty=False, recursive=True)
eal.save_directory(FX, only_if_is_dirty=False, recursive=True)
report['material'] = f'{FX}/M_BB_Shockwave'
json.dump(report, open(os.path.join(ROOT, 'artifacts/audio-bellbreaker-2026-11-18/import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB bellbreaker fx import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
