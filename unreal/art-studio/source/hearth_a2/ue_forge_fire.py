"""Hearth A2 forge fire from a generated video (2026-11-17).

Source: LTX-Video (Lightricks/ltx-video-distilled Space) text-to-video, 4 s of fire on black
(artifacts/art/hearth-a2-dressing-2026-11-17/fire/fire-1.mp4 + .json prompt). 64 frames -> an 8x8
flipbook with a 12-frame cross-fade loop (T_A2_ForgeFlipbook.png). This script imports it to
/Game/BossLab/HearthA2/Fire and builds M_A2_ForgeFlipbook: unlit additive, two-sided, frame-blended
flipbook at ~24 fps, per-mouth phase from world position, soft edge mask. WardenSmeltery.cpp puts it
on crossed planes in each furnace mouth (replacing the orange sphere glow).
Run: ./scripts/bosslab-unreal editor unreal/art-studio/source/hearth_a2/ue_forge_fire.py
"""
from pathlib import Path
import unreal
ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'artifacts/art/hearth-a2-dressing-2026-11-17/fire/T_A2_ForgeFlipbook.png'
DEST = '/Game/BossLab/HearthA2/Fire'
eal = unreal.EditorAssetLibrary; mel = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
if eal.does_directory_exist(DEST): eal.delete_directory(DEST)
t = unreal.AssetImportTask(); t.filename = str(SRC); t.destination_path = DEST; t.destination_name = 'T_A2_ForgeFlipbook'
t.automated = True; t.replace_existing = True; t.save = False
tools.import_asset_tasks([t])
tex = unreal.load_asset(DEST + '/T_A2_ForgeFlipbook')
tex.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
m = tools.create_asset('M_A2_ForgeFlipbook', DEST, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
m.set_editor_property('two_sided', True)
obj = mel.create_material_expression(m, unreal.MaterialExpressionTextureObject, -900, 0); obj.set_editor_property('texture', tex)
uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -900, 200)
tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 350)
pos = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, 500)
node = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -400, 0)
pins = []
for k in ('Tex', 'UV', 'T', 'P'):
    p = unreal.CustomInput(); p.set_editor_property('input_name', k); pins.append(p)
node.set_editor_property('inputs', pins)
node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
node.set_editor_property('code', '''
float2 u=saturate(UV);
float ph=frac(P.x*.0137+P.y*.0071);
float k=frac(T*24.0/64.0+ph)*64.0;
float f0=floor(k), f1=fmod(f0+1,64), w=k-f0;
float2 c0=float2(fmod(f0,8),floor(f0/8)), c1=float2(fmod(f1,8),floor(f1/8));
float2 inset=lerp(float2(.004,.004),float2(.996,.996),u);
float3 a=Texture2DSample(Tex,TexSampler,(c0+inset)/8).rgb;
float3 b=Texture2DSample(Tex,TexSampler,(c1+inset)/8).rgb;
float mask=smoothstep(0,.2,u.x)*smoothstep(1,.8,u.x)*smoothstep(0,.08,u.y)*smoothstep(1,.92,u.y);
return lerp(a,b,w)*mask*float3(3.2,2.4,1.6);''')
for n, pin in ((obj, 'Tex'), (uv, 'UV'), (tm, 'T'), (pos, 'P')):
    mel.connect_material_expressions(n, '', node, pin)
mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(m)
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
unreal.log('BOSSLAB forge fire flipbook done')
unreal.SystemLibrary.quit_editor()
