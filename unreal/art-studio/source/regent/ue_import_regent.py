"""Build the Funeral Regent moveset greybox materials.

Run: ./scripts/bosslab-unreal python unreal/art-studio/source/regent/ue_import_regent.py
Writes /Game/BossLab/Regent (local, not committed, like the Dungeon assets):
  M_RegentFlame  unlit additive blue soul-fire card (same noise tongue as M_DungeonFlame)
  M_RegentRune   unlit additive floor circle; MID params Radius (cm), Intensity, Tint
  M_RegentBone   lit ivory for the greybox skulls
No textures. See docs/REGENT_MOVESET.md.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
DEST = '/Game/BossLab/Regent'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
report = {}

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

def unlit_additive(mat):
    mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property('two_sided', True)
    mat.set_editor_property('used_with_instanced_static_meshes', True)

# Same tongue as M_DungeonFlame (ue_import_dungeon.py) with a cold soul-fire palette:
# deep blue edges, cyan body, near-white core.
FLAME_CODE = '''
float2 uv=UV.xy; float tm=Tm.x; float sd=Seed.x; float glow=Glow.x;
float h=saturate(1-uv.y);
float2 p=float2(uv.x*2.6+sd*7.1, uv.y*2.2+tm*(2.3+frac(sd*3.7)*.6)+sd*13.3);
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
// Keep the core blue-white rather than white, so stacked cards read as soul fire, not candles.
float3 col=lerp(float3(.01,.08,.75),float3(.12,.45,1),saturate(flame*1.4));
col=lerp(col,float3(.45,.75,1),core*.6);
return col*flame*glow;
'''

def flame():
    mat = get_or_create('M_RegentFlame')
    unlit_additive(mat)
    uv = mel.create_material_expression(mat, unreal.MaterialExpressionTextureCoordinate, -900, 0)
    time = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -900, 150)
    seed = mel.create_material_expression(mat, unreal.MaterialExpressionPerInstanceRandom, -900, 300)
    pos = mel.create_material_expression(mat, unreal.MaterialExpressionObjectPositionWS, -1200, 450)
    mask = mel.create_material_expression(mat, unreal.MaterialExpressionComponentMask, -1000, 450)
    mask.set_editor_property('r', True)
    mel.connect_material_expressions(pos, '', mask, '')
    scaled = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -850, 450)
    scaled.set_editor_property('const_b', .0137)
    mel.connect_material_expressions(mask, '', scaled, 'A')
    add = mel.create_material_expression(mat, unreal.MaterialExpressionAdd, -700, 350)
    mel.connect_material_expressions(seed, '', add, 'A')
    mel.connect_material_expressions(scaled, '', add, 'B')
    glow = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -900, 600)
    glow.set_editor_property('r', 3.5)
    node = custom(mat, FLAME_CODE, ['UV', 'Tm', 'Seed', 'Glow'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -450, 200)
    for src, pin in ((uv, 'UV'), (time, 'Tm'), (add, 'Seed'), (glow, 'Glow')):
        mel.connect_material_expressions(src, '', node, pin)
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_RegentFlame'] = {'blend': 'additive unlit', 'glow': 3.5}

# Floor circle drawn in world space around the object's centre: a bright rim, a slow
# swirling fill and radial spokes. Radius comes from the MID so any disc scale works.
RUNE_CODE = '''
float2 d=(W.xy-O.xy)/max(R.x,1);
float r=length(d); float tm=Tm.x;
if(r>1) return float3(0,0,0);
float ang=atan2(d.y,d.x);
float rim=smoothstep(.86,.97,r)*(1-smoothstep(.97,1,r));
float inner=smoothstep(.70,.74,r)*(1-smoothstep(.74,.78,r))*.6;
float spokes=pow(saturate(cos(ang*6+tm*.8)),24)*smoothstep(.2,.72,r)*(1-smoothstep(.72,.8,r))*.5;
float2 q=d*3.1+float2(tm*.21,-tm*.17);
float n=frac(sin(dot(floor(q),float2(127.1,311.7)))*43758.5453);
float fill=(.25+.25*n)*(1-r*.5)*(.75+.25*sin(tm*5+r*9));
return Tint.rgb*(rim*2+inner+spokes+fill*.6)*I.x;
'''

def rune():
    mat = get_or_create('M_RegentRune')
    unlit_additive(mat)
    world = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -1100, 0)
    obj = mel.create_material_expression(mat, unreal.MaterialExpressionObjectPositionWS, -1100, 150)
    time = mel.create_material_expression(mat, unreal.MaterialExpressionTime, -1100, 300)
    radius = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -1100, 450)
    radius.set_editor_property('parameter_name', 'Radius'); radius.set_editor_property('default_value', 250.0)
    intensity = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -1100, 600)
    intensity.set_editor_property('parameter_name', 'Intensity'); intensity.set_editor_property('default_value', 1.0)
    tint = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -1100, 750)
    tint.set_editor_property('parameter_name', 'Tint'); tint.set_editor_property('default_value', unreal.LinearColor(.15, .45, 1, 1))
    node = custom(mat, RUNE_CODE, ['W', 'O', 'Tm', 'R', 'I', 'Tint'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 300)
    for src, pin in ((world, 'W'), (obj, 'O'), (time, 'Tm'), (radius, 'R'), (intensity, 'I'), (tint, 'Tint')):
        mel.connect_material_expressions(src, '', node, pin)
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_RegentRune'] = {'blend': 'additive unlit', 'params': ['Radius', 'Intensity', 'Tint']}

def bone():
    mat = get_or_create('M_RegentBone')
    mat.set_editor_property('used_with_instanced_static_meshes', True)
    col = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -500, 0)
    col.set_editor_property('constant', unreal.LinearColor(.62, .57, .47, 1))
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 200)
    rough.set_editor_property('r', .62)
    glow = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -500, 350)
    glow.set_editor_property('constant', unreal.LinearColor(.004, .012, .04, 1))
    mel.connect_material_property(col, '', unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(glow, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_RegentBone'] = {'base': [.62, .57, .47], 'roughness': .62}

flame(); rune(); bone()
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
out = os.path.join(ROOT, 'artifacts/art/regent-moveset-2026-11-09')
os.makedirs(out, exist_ok=True)
json.dump(report, open(os.path.join(out, 'ue-import-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB regent import ' + json.dumps(report))
