"""Import the Bellbreaker's generated sounds and the shockwave ring material, 2026-11-18.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/bellbreaker/ue_import_bellbreaker_fx.py
Inputs: artifacts/audio-bellbreaker-2026-11-18/wav/*.wav (Stable Audio Open 1.0 via sfx_generate.py, converted
from FLAC with afconvert; Stability AI Community License, see CREDITS.md). Writes /Game/BossLab/Bellbreaker/Sound
(S_<name>_v<k>) and /Game/BossLab/Bellbreaker/FX/M_BB_Shockwave (local, not committed):
unlit additive two-sided ring on a plane's UVs; the luminous annulus follows three runtime world-distance parameters.
Set BOSSLAB_BB_FX_ONLY=1 to update only the material, preserving audio.
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
fx_only = os.environ.get('BOSSLAB_BB_FX_ONLY') == '1'
for directory in ((FX,) if fx_only else (SND, FX)):
    eal.make_directory(directory)
report = {'sounds': []}
for f in ([] if fx_only else sorted(glob.glob(os.path.join(WAV, '*.wav')))):
    name = 'S_' + os.path.splitext(os.path.basename(f))[0]
    t = unreal.AssetImportTask()
    t.filename = f; t.destination_path = SND; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    tools.import_asset_tasks([t])
    a = unreal.load_asset(f'{SND}/{name}')
    if a:
        report['sounds'].append([name, round(a.get_editor_property('duration'), 2)])

m = unreal.load_asset(f'{FX}/M_BB_Shockwave') if eal.does_asset_exist(f'{FX}/M_BB_Shockwave') else tools.create_asset('M_BB_Shockwave', FX, unreal.Material, unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(m)
m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
m.set_editor_property('two_sided', True)
uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, 0)
tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 150)
def scalar(name, default, y):
    node = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, y)
    node.set_editor_property('parameter_name', name)
    node.set_editor_property('default_value', default)
    return node

bindings = [(uv,'UV'),(tm,'T'),(scalar('PlaneRadiusCm',154,300),'Plane'),
            (scalar('BandInnerCm',90,450),'Inner'),(scalar('BandOuterCm',150,600),'Outer')]
n = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -450, 0)
pins = []
for _, key in bindings:
    p = unreal.CustomInput(); p.set_editor_property('input_name', key); pins.append(p)
n.set_editor_property('inputs', pins)
n.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
n.set_editor_property('code',
    'float2 q=UV*2-1; float r=length(q)*Plane; float aa=clamp(fwidth(r),0.5,3.0);'
    'float band=smoothstep(Inner-aa,Inner+aa,r)*(1-smoothstep(Outer-aa,Outer+aa,r));'
    'float edge=1-smoothstep(1.,7.,Outer-r);'
    'float glint=.93+.07*cos(atan2(q.y,q.x)*17.+T*3.);'
    'return band*glint*(float3(1.55,.69,.22)+edge*float3(2.7,2.1,1.5));')
for node, pin in bindings:
    mel.connect_material_expressions(node, '', n, pin)
mel.connect_material_property(n, '', MP.MP_EMISSIVE_COLOR)
mel.recompile_material(m)
if not fx_only: eal.save_directory(SND, only_if_is_dirty=False, recursive=True)
eal.save_directory(FX, only_if_is_dirty=False, recursive=True)
report['material'] = f'{FX}/M_BB_Shockwave'
if not fx_only: json.dump(report, open(os.path.join(ROOT, 'artifacts/audio-bellbreaker-2026-11-18/import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB bellbreaker fx import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
