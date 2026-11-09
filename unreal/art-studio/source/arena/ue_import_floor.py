"""Rebuild the dungeon floor material with layered ground detail.

Run: ./scripts/bosslab-unreal python unreal/art-studio/source/arena/ue_import_floor.py
(after ue_import_dungeon.py, whose Poly Haven textures it reuses, and after
bake_floor_masks.py, whose mask texture it imports). Replaces
/Game/BossLab/Dungeon/M_DungeonFloor (local, not committed). World-space layers:
  - cobbles in the ritual centre and the outer band; large worn flagstones in the fight
    ring between them, with a noisy boundary;
  - standing puddles (dark, mirror-smooth, flattened normal) that reflect the firelight;
  - soot/grime patches and fine cracks (voronoi edges);
  - a few old dried bloodstains toward the centre.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
DEST = '/Game/BossLab/Dungeon'
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()

def custom(mat, code, inputs, out_type, x, y):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property('code', code); node.set_editor_property('output_type', out_type)
    pins = []
    for n in inputs:
        pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
    node.set_editor_property('inputs', pins)
    return node

# The masks are baked offline by bake_floor_masks.py (R ring, G puddle, B grime/blood,
# A crack): one texture lookup instead of ~100 noise evaluations per floor pixel.
MASK_CODE = '''
float b=T.z;
return float4(T.x,T.y,b<=.5 ? b*2 : 1+(b-.5)*2,T.w);
'''
MASK_UV_CODE = '''
return float2(P.x/2900+.5,.5-P.y/2900);
'''
BASE_CODE = '''
float3 col=lerp(Dc.rgb*float3(.34,.31,.29),Df.rgb*float3(.3,.28,.27),M.x);
col*=1-M.w*.55;
float g=saturate(M.z); float blood=saturate(M.z-1);
col*=1-.35*min(g,1);
col=lerp(col,float3(.07,.012,.01),blood*.7);
// Wet stone darkens; the puddle itself is nearly black so it shows reflections, not a tint.
col=lerp(col,col*.16,M.y);
return col;
'''
ROUGH_CODE = '''
float r=lerp(Rc.x,Rf.x,M.x)+.05+M.w*.15;
return lerp(r,.16,M.y);
'''
NORMAL_CODE = '''
float3 s=normalize(lerp(Sc.xyz,Sf.xyz,M.x));
s=normalize(lerp(s,float3(0,0,1),saturate(M.y*.9)));
s.xy*=Flat;
float3 n=normalize(N);
float3 T,B;
if(abs(n.z)>0.6) { T=float3(1,0,0); B=float3(0,1,0); }
else { float2 t=normalize(float2(-n.y,n.x)+1e-5); T=float3(t,0); B=float3(0,0,1); }
return normalize(T*s.x+B*s.y+n*s.z);
'''
UV_CODE = '''
float3 n=normalize(N); float2 uv;
if(abs(n.z)>0.6) uv=float2(P.x,-P.y);
else { float2 t=normalize(float2(-n.y,n.x)+1e-5); uv=float2(dot(P.xy,t),-P.z); }
return uv/Tile.x;
'''

mat = unreal.load_asset(f'{DEST}/M_DungeonFloor')
mel.delete_all_material_expressions(mat)
mat.set_editor_property('tangent_space_normal', False)
mat.set_editor_property('used_with_instanced_static_meshes', True)
wp = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -1800, 0)
vn = mel.create_material_expression(mat, unreal.MaterialExpressionVertexNormalWS, -1800, 200)
def uv(tile, y):
    t = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -1800, y); t.set_editor_property('r', tile)
    node = custom(mat, UV_CODE, ['P', 'N', 'Tile'], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1500, y)
    for src, pin in ((wp, 'P'), (vn, 'N'), (t, 'Tile')): mel.connect_material_expressions(src, '', node, pin)
    return node
def samples(stem, coords, y):
    out = {}
    for i, (key, suffix, sampler) in enumerate((('d', 'D', unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),
                                                ('n', 'N', unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL),
                                                ('m', 'ARM', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS))):
        s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -1200, y + i * 250)
        s.set_editor_property('texture', unreal.load_asset(f'{DEST}/T_{stem}_{suffix}')); s.set_editor_property('sampler_type', sampler)
        mel.connect_material_expressions(coords, '', s, 'UVs')
        out[key] = s
    return out
cob = samples('cobblestone_pavement', uv(240, 0), 0)
flag = samples('castle_wall_varriation', uv(330, 800), 800)
task = unreal.AssetImportTask()
task.filename = os.path.join(ROOT, 'artifacts/art/overnight-2026-11-10/T_DungeonFloorMasks.png')
task.destination_path = DEST; task.destination_name = 'T_DungeonFloorMasks'; task.automated = True; task.replace_existing = True; task.save = False
tools.import_asset_tasks([task])
masks = unreal.load_asset(f'{DEST}/T_DungeonFloorMasks')
masks.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
masks.set_editor_property('srgb', False)
masks.set_editor_property('address_x', unreal.TextureAddress.TA_CLAMP); masks.set_editor_property('address_y', unreal.TextureAddress.TA_CLAMP)
eal.save_asset(f'{DEST}/T_DungeonFloorMasks', only_if_is_dirty=False)
muv = custom(mat, MASK_UV_CODE, ['P'], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1500, -400)
mel.connect_material_expressions(wp, '', muv, 'P')
mtex = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -1300, -400)
mtex.set_editor_property('texture', masks); mtex.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
mel.connect_material_expressions(muv, '', mtex, 'UVs')
mask = custom(mat, MASK_CODE, ['T'], unreal.CustomMaterialOutputType.CMOT_FLOAT4, -1100, -400)
mel.connect_material_expressions(mtex, 'RGBA', mask, 'T')
base = custom(mat, BASE_CODE, ['Dc', 'Df', 'M'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -700, 0)
for src, pin in ((cob['d'], 'Dc'), (flag['d'], 'Df'), (mask, 'M')): mel.connect_material_expressions(src, 'RGB' if pin != 'M' else '', base, pin)
rough = custom(mat, ROUGH_CODE, ['Rc', 'Rf', 'M'], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -700, 300)
mel.connect_material_expressions(cob['m'], 'G', rough, 'Rc'); mel.connect_material_expressions(flag['m'], 'G', rough, 'Rf'); mel.connect_material_expressions(mask, '', rough, 'M')
flat = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -1000, 1600); flat.set_editor_property('r', 1.4)
normal = custom(mat, NORMAL_CODE, ['Sc', 'Sf', 'M', 'N', 'Flat'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -700, 600)
for src, pin, out in ((cob['n'], 'Sc', 'RGB'), (flag['n'], 'Sf', 'RGB'), (mask, 'M', ''), (vn, 'N', ''), (flat, 'Flat', '')):
    mel.connect_material_expressions(src, out, normal, pin)
mel.connect_material_property(base, '', unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(normal, '', unreal.MaterialProperty.MP_NORMAL)
mel.connect_material_property(cob['m'], 'R', unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
# Lower specular in puddles: the blue sky-fill mirrored as flat blue paint at full spec.
spec = custom(mat, 'return lerp(.5,.3,M.y);', ['M'], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -700, 900)
mel.connect_material_expressions(mask, '', spec, 'M')
mel.connect_material_property(spec, '', unreal.MaterialProperty.MP_SPECULAR)
mel.recompile_material(mat)
eal.save_asset(f'{DEST}/M_DungeonFloor', only_if_is_dirty=False)
report = {'M_DungeonFloor': 'cobble centre/outer, flagstone ring, puddles, grime, cracks, old blood'}
json.dump(report, open(os.path.join(ROOT, 'artifacts/art/overnight-2026-11-10/floor-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB floor import ' + json.dumps(report))
