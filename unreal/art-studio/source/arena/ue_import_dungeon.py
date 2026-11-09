"""Import the dungeon arena surfaces and build their materials.

Run: ./scripts/bosslab-unreal python unreal/art-studio/source/arena/ue_import_dungeon.py
Textures are CC0 Poly Haven 2K maps in artifacts/art/arena-dungeon-2026-11-09/textures
(diffuse, DirectX normal, AO/rough/metal). Each stone material projects its texture in
world space (top-down on floors, along the wall on vertical faces), so scaled engine cubes
tile at a fixed real size without UVs. M_DungeonFlame is an unlit additive card with
procedural fire; no texture, no particle system.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
TEX = os.path.join(ROOT, 'artifacts/art/arena-dungeon-2026-11-09/textures')
DEST = '/Game/BossLab/Dungeon'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {}

def import_texture(path, name, kind):
    t = unreal.AssetImportTask()
    t.filename = path; t.destination_path = DEST; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    tools.import_asset_tasks([t])
    tex = unreal.load_asset(f'{DEST}/{name}')
    if kind == 'normal':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb', False)
    elif kind == 'masks':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
        tex.set_editor_property('srgb', False)
    return tex

def get_or_create(name):
    path = f'{DEST}/{name}'
    mat = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    return mat

def custom(mat, code, inputs, out_type, x, y):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property('code', code)
    node.set_editor_property('output_type', out_type)
    pins = []
    for n in inputs:
        pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
    node.set_editor_property('inputs', pins)
    return node

# World projection: floors use (x, -y); vertical faces run along the wall and down Z.
# The tangent frame matches that projection so the DirectX normal map lights correctly.
UV_CODE = '''
float3 n=normalize(N);
float2 uv;
if(abs(n.z)>0.6) uv=float2(P.x,-P.y);
else { float2 t=normalize(float2(-n.y,n.x)+1e-5); uv=float2(dot(P.xy,t),-P.z); }
return uv/Tile;
'''
# Round pillars: wrap around the object's own axis instead (arc length, height).
COLUMN_UV_CODE = '''
float2 d=P.xy-O.xy;
return float2(atan2(d.y,d.x)*length(d),-P.z)/Tile;
'''
COLUMN_NORMAL_CODE = '''
float3 n=normalize(N);
float3 T=normalize(float3(-n.y,n.x,0)+1e-5), B=float3(0,0,1);
return normalize(T*S.x+B*S.y+n*S.z*Flat);
'''
NORMAL_CODE = '''
float3 n=normalize(N);
float3 T,B;
if(abs(n.z)>0.6) { T=float3(1,0,0); B=float3(0,1,0); }
else { float2 t=normalize(float2(-n.y,n.x)+1e-5); T=float3(t,0); B=float3(0,0,1); }
return normalize(T*S.x+B*S.y+n*S.z*Flat);
'''

def stone(name, stem, tile_cm, tint, rough_bias, column=False):
    base = import_texture(os.path.join(TEX, f'{stem}_diff_2k.jpg'), f'T_{stem}_D', 'color')
    nor = import_texture(os.path.join(TEX, f'{stem}_nor_dx_2k.jpg'), f'T_{stem}_N', 'normal')
    arm = import_texture(os.path.join(TEX, f'{stem}_arm_2k.jpg'), f'T_{stem}_ARM', 'masks')
    mat = get_or_create(name)
    mat.set_editor_property('tangent_space_normal', False)
    wp = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -1400, 0)
    vn = mel.create_material_expression(mat, unreal.MaterialExpressionVertexNormalWS, -1400, 200)
    tile = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -1400, 400)
    tile.set_editor_property('r', tile_cm)
    if column:
        uv = custom(mat, COLUMN_UV_CODE, ['P', 'O', 'Tile'], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1100, 200)
        obj = mel.create_material_expression(mat, unreal.MaterialExpressionObjectPositionWS, -1400, 600)
        mel.connect_material_expressions(obj, '', uv, 'O')
    else:
        uv = custom(mat, UV_CODE, ['P', 'N', 'Tile'], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1100, 200)
        mel.connect_material_expressions(vn, '', uv, 'N')
    mel.connect_material_expressions(wp, '', uv, 'P')
    mel.connect_material_expressions(tile, '', uv, 'Tile')
    samples = {}
    for i, (key, tex, sampler) in enumerate((('d', base, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),
                                             ('n', nor, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL),
                                             ('m', arm, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS))):
        s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -800, i * 300)
        s.set_editor_property('texture', tex); s.set_editor_property('sampler_type', sampler)
        mel.connect_material_expressions(uv, '', s, 'UVs')
        samples[key] = s
    color = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -800, -250)
    color.set_editor_property('constant', unreal.LinearColor(*tint, 1))
    mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -400, -100)
    mel.connect_material_expressions(samples['d'], 'RGB', mul, 'A')
    mel.connect_material_expressions(color, '', mul, 'B')
    mel.connect_material_property(mul, '', unreal.MaterialProperty.MP_BASE_COLOR)
    flat = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -800, 900)
    flat.set_editor_property('r', 0.6)  # <1 deepens the relief under grazing firelight
    normal = custom(mat, COLUMN_NORMAL_CODE if column else NORMAL_CODE, ['S', 'N', 'Flat'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -400, 300)
    mel.connect_material_expressions(samples['n'], 'RGB', normal, 'S')
    mel.connect_material_expressions(vn, '', normal, 'N')
    mel.connect_material_expressions(flat, '', normal, 'Flat')
    mel.connect_material_property(normal, '', unreal.MaterialProperty.MP_NORMAL)
    bias = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -400, 600)
    mel.connect_material_expressions(samples['m'], 'G', bias, 'A')
    bias.set_editor_property('const_b', rough_bias)
    mel.connect_material_property(bias, '', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(samples['m'], 'R', unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    mel.recompile_material(mat)
    report[name] = {'texture': stem, 'tile_cm': tile_cm, 'tint': tint}
    return mat

# Fire: scrolling 4-octave value noise shaped into a tapering tongue. PerInstanceRandom
# (instanced cards) or the object position (single cards) desynchronises neighbours.
FLAME_CODE = '''
// Inputs may arrive wider than declared; take the components we need.
float2 uv=UV.xy; float tm=Tm.x; float sd=Seed.x; float glow=Glow.x;
float h=saturate(1-uv.y);
float2 p=float2(uv.x*2.6+sd*7.1, uv.y*2.2+tm*(1.9+frac(sd*3.7)*.6)+sd*13.3);
float n=0, a=.55;
for(int i=0;i<4;i++)
{
    float2 ip=floor(p), f=frac(p); f=f*f*(3-2*f);
    float h00=frac(sin(dot(ip,float2(127.1,311.7)))*43758.5453);
    float h10=frac(sin(dot(ip+float2(1,0),float2(127.1,311.7)))*43758.5453);
    float h01=frac(sin(dot(ip+float2(0,1),float2(127.1,311.7)))*43758.5453);
    float h11=frac(sin(dot(ip+float2(1,1),float2(127.1,311.7)))*43758.5453);
    n+=a*lerp(lerp(h00,h10,f.x),lerp(h01,h11,f.x),f.y);
    p=p*2.07+float2(0,tm*.7); a*=.5;
}
float x=abs(uv.x-.5)*2+(n-.5)*.7*h;
float width=.92*pow(saturate(1-h),.55)+.02;
float body=saturate((width-x)/max(width,.05)*2.2);
float flame=body*saturate(n*1.5-h*1.15+.25)*saturate((1-h)*3)*saturate(h*14+.15);
float core=saturate(flame*1.8-.35);
float3 col=lerp(float3(.9,.11,.008),float3(1,.55,.12),saturate(flame*1.4));
col=lerp(col,float3(1,.68,.3),core*.8);
return col*flame*glow;
'''

def flame():
    mat = get_or_create('M_DungeonFlame')
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('two_sided', True)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    time = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -900, 150)
    seed = mel.create_material_expression(mat, unreal.MaterialExpressionPerInstanceRandom, -900, 300)
    pos = mel.create_material_expression(mat, unreal.MaterialExpressionObjectPositionWS, -1200, 450)
    mask = mel.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -1000, 450)
    mask.set_editor_property('r', True)
    mel.connect_material_expressions(pos, '', mask, '')
    frac_pos = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -850, 450)
    frac_pos.set_editor_property('const_b', .0137)
    mel.connect_material_expressions(mask, '', frac_pos, 'A')
    add = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -700, 350)
    mel.connect_material_expressions(seed, '', add, 'A')
    mel.connect_material_expressions(frac_pos, '', add, 'B')
    glow = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -900, 600)
    glow.set_editor_property('r', 5.0)
    node = custom(mat, FLAME_CODE, ['UV', 'Tm', 'Seed', 'Glow'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -450, 200)
    for src, pin in ((uv, 'UV'), (time, 'Tm'), (add, 'Seed'), (glow, 'Glow')):
        mel.connect_material_expressions(src, '', node, pin)
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_DungeonFlame'] = {'blend': 'additive unlit', 'glow': 5.0}
    return mat

# Dark, slightly warm tints keep stone well below the fighters in value; firelight
# supplies the colour. Tile sizes are the real-world size of one texture repeat.
stone('M_DungeonFloor', 'cobblestone_pavement', 240.0, (.34, .31, .29), 0.05)
stone('M_DungeonWall', 'castle_wall_slates', 260.0, (.30, .28, .27), 0.0)
stone('M_DungeonPier', 'castle_wall_varriation', 220.0, (.26, .24, .23), 0.0)
stone('M_DungeonColumn', 'castle_wall_varriation', 200.0, (.26, .24, .23), 0.0, column=True)
flame()
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
out = os.path.join(ROOT, 'artifacts/art/arena-dungeon-2026-11-09/ue-import-report.json')
json.dump(report, open(out, 'w'), indent=1)
unreal.log('BOSSLAB dungeon import ' + json.dumps(report))
