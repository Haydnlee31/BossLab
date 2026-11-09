"""Import the prepared CC0 dungeon props and build their materials, plus the procedural
banner, fog-gate, light-shaft and dust materials.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/arena/ue_import_props.py
(the FBX importer reports through Slate, which asserts in headless commandlets; the
script quits the editor when done, so the launcher's exit 1 is expected).
Inputs come from prep_props.py: artifacts/art/arena-dungeon-2026-11-09/props/fbx/*.fbx,
pieces.json and materials.json (Poly Haven, CC0). Each texture set gets one direct
material (base colour, OpenGL normal with green flipped, AO/rough/metal or roughness).
Writes props-import-report.json with each mesh's slots and bounds in cm.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
FBX = os.path.join(ROOT, 'artifacts/art/arena-dungeon-2026-11-09/props/fbx')
DEST = '/Game/BossLab/Dungeon/Props'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {}
# Start clean: replacing an existing mesh reuses its stored import settings (scale).
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

def texture(path, kind):
    name = 'T_' + os.path.splitext(os.path.basename(path))[0]
    tex = task(path, name)
    if kind == 'normal':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb', False)
        tex.set_editor_property('flip_green_channel', True)  # glTF normals are OpenGL (+Y)
    elif kind == 'masks':
        tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
        tex.set_editor_property('srgb', False)
    return tex

def new_material(name):
    path = f'{DEST}/{name}'
    mat = unreal.load_asset(path) if eal.does_asset_exist(path) else tools.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(mat)
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    return mat

def sample(mat, tex, sampler, y):
    s = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSample, -600, y)
    s.set_editor_property('texture', tex); s.set_editor_property('sampler_type', sampler)
    return s

def custom(mat, code, inputs, out_type, x, y):
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, x, y)
    node.set_editor_property('code', code); node.set_editor_property('output_type', out_type)
    pins = []
    for n in inputs:
        pin = unreal.CustomInput(); pin.set_editor_property('input_name', n); pins.append(pin)
    node.set_editor_property('inputs', pins)
    return node

def pbr(name, maps):
    mat = new_material(name)
    mat.set_editor_property('two_sided', True)  # gate bars and candle cards are thin shells
    d = sample(mat, texture(maps['diff'], 'color'), unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, 0)
    mel.connect_material_property(d, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
    if 'nor' in maps:
        n = sample(mat, texture(maps['nor'], 'normal'), unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, 300)
        mel.connect_material_property(n, 'RGB', unreal.MaterialProperty.MP_NORMAL)
    if 'arm' in maps:
        m = sample(mat, texture(maps['arm'], 'masks'), unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, 600)
        mel.connect_material_property(m, 'R', unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
        mel.connect_material_property(m, 'G', unreal.MaterialProperty.MP_ROUGHNESS)
        mel.connect_material_property(m, 'B', unreal.MaterialProperty.MP_METALLIC)
    elif 'rough' in maps:
        r = sample(mat, texture(maps['rough'], 'masks'), unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, 600)
        mel.connect_material_property(r, 'R', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    return mat

def candle_flame(name, maps):
    # Flame cards painted on black: additive unlit emissive.
    mat = new_material(name)
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('two_sided', True)
    d = sample(mat, texture(maps['diff'], 'color'), unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, 0)
    mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -250, 0)
    mul.set_editor_property('const_b', 6.0)
    mel.connect_material_expressions(d, 'RGB', mul, 'A')
    mel.connect_material_property(mul, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    return mat

materials = {}
for mname, maps in json.load(open(os.path.join(FBX, 'materials.json'))).items():
    materials[mname] = candle_flame('M_Prop_' + mname, maps) if mname.endswith('_flame') else pbr('M_Prop_' + mname, maps)

for piece, info in json.load(open(os.path.join(FBX, 'pieces.json'))).items():
    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = False; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
    sm = ui.static_mesh_import_data
    sm.set_editor_property('combine_meshes', True)
    # Blender writes metres with a 1.0 unit factor; import at 100x so 1 m = 100 cm. At 1/100
    # scale the importer's vertex weld collapsed thin parts.
    sm.set_editor_property('import_uniform_scale', 100.0)
    sm.set_editor_property('auto_generate_collision', False)
    sm.set_editor_property('generate_lightmap_u_vs', False)
    sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    mesh = task(os.path.join(FBX, piece + '.fbx'), piece, ui)
    if mesh is None:
        report[piece] = {'error': 'missing'}
        continue
    slots = []
    for s in mesh.get_editor_property('static_materials'):
        slot = str(s.get_editor_property('material_slot_name'))
        mat = next((m for k, m in materials.items() if k == slot or slot.startswith(k)), None)
        s.set_editor_property('material_interface', mat)
        slots.append(s)
    mesh.set_editor_property('static_materials', slots)
    box = mesh.get_bounding_box(); size = box.max - box.min
    report[piece] = {'slots': [str(s.get_editor_property('material_slot_name')) for s in slots],
                     'materials': [s.get_editor_property('material_interface').get_name() if s.get_editor_property('material_interface') else None for s in slots],
                     'size_cm': [round(size.x, 1), round(size.y, 1), round(size.z, 1)],
                     'min_cm': [round(box.min.x, 1), round(box.min.y, 1), round(box.min.z, 1)],
                     'triangles': mesh.get_num_triangles(0)}

# Tattered banner: dark wool weave, torn ragged hem and moth holes, slow sway (WPO).
BANNER_CODE = '''
float2 uv=UV.xy;
float hn=frac(sin(floor(uv.x*38)*91.7)*4375.85)*.10+frac(sin(floor(uv.x*9)*13.1)*917.3)*.08;
float hem=step(uv.y,.80+hn);
float2 c=floor(uv*float2(7,11)); float2 f=frac(uv*float2(7,11))-.5;
float hole=step(.92,frac(sin(dot(c,float2(12.9898,78.233)))*43758.5453))*step(length(f),.28);
return hem*(1-hole)*step(.02,uv.x)*step(uv.x,.98);
'''
WEAVE_CODE = '''
float2 uv=UV.xy;
float w=.82+.18*sin(uv.x*900)*sin(uv.y*900);
float blotch=.75+.25*sin(uv.x*13.1+sin(uv.y*7.3)*2)*sin(uv.y*9.7+uv.x*3.1);
float dirt=lerp(1,.35,saturate(uv.y*1.1-.1))*blotch;
float band=1-.35*step(abs(uv.y-.12),.012)-.35*step(abs(uv.y-.16),.006);
return lerp(Col*w*dirt*band,float3(.03,.027,.024),.25);  // soot greys the dye
'''
SWAY_CODE = '''
float h=saturate(UV.y);
return float3(sin(T*.9+P.x*.01+P.y*.013)*7*h*h, cos(T*.7+P.y*.01)*4*h*h, 0);
'''
banner = new_material('M_DungeonBanner')
banner.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
banner.set_editor_property('two_sided', True)
uv = mel.create_material_expression(banner, unreal.MaterialExpressionTextureCoordinate, -900, 0)
col = mel.create_material_expression(banner, unreal.MaterialExpressionConstant3Vector, -900, 150)
col.set_editor_property('constant', unreal.LinearColor(.065, .014, .012, 1))
weave = custom(banner, WEAVE_CODE, ['UV', 'Col'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 0)
mel.connect_material_expressions(uv, '', weave, 'UV'); mel.connect_material_expressions(col, '', weave, 'Col')
mel.connect_material_property(weave, '', unreal.MaterialProperty.MP_BASE_COLOR)
mask = custom(banner, BANNER_CODE, ['UV'], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -500, 200)
mel.connect_material_expressions(uv, '', mask, 'UV')
mel.connect_material_property(mask, '', unreal.MaterialProperty.MP_OPACITY_MASK)
rough = mel.create_material_expression(banner, unreal.MaterialExpressionConstant, -500, 350); rough.set_editor_property('r', .95)
mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
t = mel.create_material_expression(banner, unreal.MaterialExpressionTime, -900, 450)
wp = mel.create_material_expression(banner, unreal.MaterialExpressionWorldPosition, -900, 550)
sway = custom(banner, SWAY_CODE, ['UV', 'T', 'P'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 500)
for src, pin in ((uv, 'UV'), (t, 'T'), (wp, 'P')):
    mel.connect_material_expressions(src, '', sway, pin)
mel.connect_material_property(sway, '', unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
mel.recompile_material(banner)

# Fog gate: pale swirling translucent wall across the boss door.
FOG_NOISE = '''
float2 uv=UV.xy; float tm=T.x;
float n=0,a=.5; float2 p=uv*float2(3,5);
for(int i=0;i<4;i++)
{
    float2 q=p+float2(sin(p.y*1.7+tm*.6),cos(p.x*1.3-tm*.5))*.6;
    n+=a*(.5+.5*sin(q.x*2.1+tm*.4)*sin(q.y*1.7-tm*.7));
    p*=2.03; a*=.5;
}
'''
# Colour and opacity as separate nodes (a float4 split through component masks left the
# opacity pin effectively unconnected: the wall rendered opaque).
FOG_COLOR = FOG_NOISE + 'return lerp(float3(.4,.45,.5),float3(.8,.82,.8),n)*.7;'
FOG_ALPHA = FOG_NOISE + '''
float2 e=min(uv,1-uv);
return saturate(pow(n,1.4)*.85*smoothstep(0,.3,e.x)*smoothstep(0,.35,e.y));
'''
fog = new_material('M_DungeonFogGate')
fog.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
fog.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
fog.set_editor_property('two_sided', True)
uv = mel.create_material_expression(fog, unreal.MaterialExpressionTextureCoordinate, -900, 0)
t = mel.create_material_expression(fog, unreal.MaterialExpressionTime, -900, 150)
color = custom(fog, FOG_COLOR, ['UV', 'T'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 0)
alpha = custom(fog, FOG_ALPHA, ['UV', 'T'], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -500, 200)
for node in (color, alpha):
    mel.connect_material_expressions(uv, '', node, 'UV'); mel.connect_material_expressions(t, '', node, 'T')
mel.connect_material_property(color, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.connect_material_property(alpha, '', unreal.MaterialProperty.MP_OPACITY)
mel.recompile_material(fog)

# Light shaft: soft additive cone, brightest near the ceiling and along its axis; fades
# by world height because the engine cone's UVs are not laid out along its length.
SHAFT_CODE = '''
float facing=saturate(abs(dot(normalize(N),normalize(V))));
float top=saturate(Z.x/1600);
return Col*pow(facing,2.5)*lerp(.2,1,top*top)*saturate(Z.x/60)*Glow;
'''
shaft = new_material('M_DungeonShaft')
shaft.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
shaft.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
shaft.set_editor_property('two_sided', True)
wp = mel.create_material_expression(shaft, unreal.MaterialExpressionWorldPosition, -1100, 0)
uv = mel.create_material_expression(shaft, unreal.MaterialExpressionComponentMask, -900, 0)
uv.set_editor_property('b', True)
mel.connect_material_expressions(wp, '', uv, '')
vn = mel.create_material_expression(shaft, unreal.MaterialExpressionVertexNormalWS, -900, 150)
cam = mel.create_material_expression(shaft, unreal.MaterialExpressionCameraVectorWS, -900, 300)
col = mel.create_material_expression(shaft, unreal.MaterialExpressionConstant3Vector, -900, 450)
col.set_editor_property('constant', unreal.LinearColor(.55, .65, .85, 1))
g = mel.create_material_expression(shaft, unreal.MaterialExpressionConstant, -900, 600); g.set_editor_property('r', .22)
node = custom(shaft, SHAFT_CODE, ['Z', 'N', 'V', 'Col', 'Glow'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 200)
for src, pin in ((uv, 'Z'), (vn, 'N'), (cam, 'V'), (col, 'Col'), (g, 'Glow')):
    mel.connect_material_expressions(src, '', node, pin)
mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(shaft)

# Dust motes drifting in the shaft.
dust = new_material('M_DungeonDust')
dust.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
c = mel.create_material_expression(dust, unreal.MaterialExpressionConstant3Vector, -400, 0)
c.set_editor_property('constant', unreal.LinearColor(.35, .38, .45, 1))
mel.connect_material_property(c, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(dust)

eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
json.dump(report, open(os.path.join(ROOT, 'artifacts/art/arena-dungeon-2026-11-09/props-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB dungeon props ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
