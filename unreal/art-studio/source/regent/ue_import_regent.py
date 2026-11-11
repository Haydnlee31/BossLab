"""Build the Funeral Regent moveset greybox materials.

Run: ./scripts/bosslab-unreal python unreal/art-studio/source/regent/ue_import_regent.py
Writes /Game/BossLab/Regent (local, not committed, like the Dungeon assets):
  M_RegentFlame  unlit additive soul-fire card (warped tongue, halo, embers, HDR blue palette)
  M_RegentRune   unlit additive spell mandala; MID params Radius (cm), Intensity, Tint, Reveal
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

# Soul fire: a domain-warped, swaying tongue in a narrower body (the C++ cards are 1.3x
# wider to leave room for a soft halo), rising embers and flicker. HDR palette from
# indigo edges through electric blue and cyan to a white-cyan core, so it blooms.
FLAME_CODE = '''
float2 uv=UV.xy; float tm=Tm.x; float sd=Seed.x; float glow=Glow.x;
float h=saturate(1-uv.y);
// Low-frequency warp: pushes the whole tongue sideways, more toward the tip.
float2 p=float2(uv.x*1.7+sd*7.1, uv.y*1.3+tm*1.2+sd*13.3);
float w=0, a=.5;
for(int i=0;i<3;i++)
{
    float2 ip=floor(p), f=frac(p); f=f*f*(3-2*f);
    float h00=frac(sin(dot(ip,float2(127.1,311.7)))*43758.5453);
    float h10=frac(sin(dot(ip+float2(1,0),float2(127.1,311.7)))*43758.5453);
    float h01=frac(sin(dot(ip+float2(0,1),float2(127.1,311.7)))*43758.5453);
    float h11=frac(sin(dot(ip+float2(1,1),float2(127.1,311.7)))*43758.5453);
    w+=a*lerp(lerp(h00,h10,f.x),lerp(h01,h11,f.x),f.y);
    p=p*2.03+float2(1.7,0); a*=.5;
}
// Detail noise, scrolling up faster than the warp.
p=float2(uv.x*3.1+sd*3.3+w*.8, uv.y*2.6+tm*(2.9+frac(sd*3.7)*.8)+sd*5.9);
float n=0; a=.55;
for(int j=0;j<4;j++)
{
    float2 ip=floor(p), f=frac(p); f=f*f*(3-2*f);
    float h00=frac(sin(dot(ip,float2(127.1,311.7)))*43758.5453);
    float h10=frac(sin(dot(ip+float2(1,0),float2(127.1,311.7)))*43758.5453);
    float h01=frac(sin(dot(ip+float2(0,1),float2(127.1,311.7)))*43758.5453);
    float h11=frac(sin(dot(ip+float2(1,1),float2(127.1,311.7)))*43758.5453);
    n+=a*lerp(lerp(h00,h10,f.x),lerp(h01,h11,f.x),f.y);
    p=p*2.07+float2(0,tm*.9); a*=.5;
}
float x=(uv.x-.5)*2+(w-.5)*1.2*h*h+sin(h*6.5-tm*7+sd*20)*.07*h+(n-.5)*.45*h;
float width=.6*pow(saturate(1-h),.6)*(.8+.4*n)+.015;
float body=pow(saturate(1-abs(x)/width),.75);
float flame=body*saturate(n*1.8-h*1.3+.3)*saturate(h*12+.1);
float core=saturate(flame*2.6-1.45);
// Soft halo hugging the lower body; fades at the card bottom so no edge shows.
float hx=(uv.x-.5)*2;
float halo=exp(-hx*hx*4)*saturate(1-h*1.4)*saturate(h*6)*(.75+.25*n);
// Embers: sparse sparks rising past the tip.
float2 eg=float2(uv.x*5+sd*3.1, uv.y*4.5+tm*3.4+sd*7.7);
float2 ec=floor(eg), ef=frac(eg)-.5;
float er=frac(sin(dot(ec,float2(12.9898,78.233)))*43758.5453);
float2 eo=float2(er-.5,frac(er*7.31)-.5)*.55;
float ember=step(.8,er)*smoothstep(.13,0,length(ef-eo))*saturate(h*2.2-.35)*saturate(1.2-h);
float t=saturate(flame*1.3);
float3 col=lerp(float3(.16,.02,1.0),float3(.01,.22,1.9),smoothstep(0,.45,t));
col=lerp(col,float3(.05,.6,2.4),smoothstep(.45,.9,t));
col=lerp(col,float3(.7,1.3,2.6),core);
float flick=.86+.14*sin(tm*13+sd*31)*sin(tm*7.3+sd*11);
return (col*flame*1.15+float3(.03,.12,1.1)*halo*.5+float3(.4,.8,2.4)*ember*2.2)*glow*flick;
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

# Floor circle drawn in world space around the object's centre, a spell mandala: an outer
# rim, two counter-rotating rune bands (procedural staves with branches), a tick ring, an
# octagram of two squares, an inner hexagram, spokes and a hot centre. Reveal (0-1) draws it
# in with an angular sweep (outer clockwise, inner counter-clockwise). Radius comes from the
# MID so any disc scale works.
RUNE_CODE = '''
struct G
{
    float hash(float v) { return frac(sin(v)*43758.5453); }
    float seg(float2 p,float2 a,float2 b) { float2 pa=p-a, ba=b-a; float t=saturate(dot(pa,ba)/dot(ba,ba)); return length(pa-ba*t); }
    float stroke(float d,float w,float aa) { return 1-smoothstep(w,w+aa,d)+.28*exp(-d*d*2500); }
    float ring(float r,float c,float w,float aa) { return stroke(abs(r-c),w,aa); }
    float glyphs(float r,float a01,float r0,float r1,float n,float aa,float salt)
    {
        float v=(r-r0)/(r1-r0);
        if(v<0 || v>1) return 0;
        float t=a01*n; float cid=fmod(floor(t),n); float u=frac(t);
        float asp=(6.2831853*(r0+r1)*.5/n)/(r1-r0);
        float2 g=float2((u-.5)*asp/.7+.5,(v-.1)/.8);
        if(g.x<-.15 || g.x>1.15) return 0;
        float d=seg(g,float2(.5,0),float2(.5,1));
        for(int k=0;k<12;k++)
        {
            if(hash(cid*17.13+k*3.71+salt)>.7)
            {
                float y=(k%3==0)?.85:((k%3==1)?.5:.15);
                float side=float((k/3)%2);
                float dir=(k<6)?1:-1;
                d=min(d,seg(g,float2(.5,y),float2(side,saturate(y+.32*dir))));
            }
        }
        if(hash(cid*5.3+salt)>.8) d=min(d,abs(length(g-float2(.5,.5))-.22));
        float ag=aa/((r1-r0)*.8);
        return 1-smoothstep(.055,.055+ag*1.5,d)+.25*exp(-d*d*60);
    }
};
G g;
float2 dd=(W.xy-O.xy)/max(R.x,1);
float r=length(dd);
if(r>1.03) return float3(0,0,0);
float tm=Tm.x; float rv=saturate(Rv.x);
float aa=max(fwidth(r),.0015)*1.2;
float a01=atan2(dd.y,dd.x)/6.2831853+.5;
float rot1=tm*.045, rot2=-tm*.065, rot3=tm*.025;
float outer=0, inner=0;
outer+=g.ring(r,.985,.006,aa)*1.3;
outer+=g.ring(r,.885,.0025,aa);
outer+=g.glyphs(r,frac(a01+rot1),.895,.972,24,aa,1.3)*(.75+.25*sin(tm*3+a01*40));
outer+=g.ring(r,.835,.0025,aa);
float tc=(a01+rot2)*144; float tk=frac(tc);
float tl=(fmod(floor(tc),4)==0)?.878:.858;
float ta=aa/max(r*6.2831853/144,.0001);
outer+=(1-smoothstep(.06,.06+ta,abs(tk-.5)))*smoothstep(.84,.84+aa,r)*(1-smoothstep(tl,tl+aa,r))*.7;
for(int q=0;q<2;q++)
{
    float th=rot3*6.2831853+q*.7853982; float c=cos(th), s=sin(th);
    float2 pq=float2(c*dd.x+s*dd.y,-s*dd.x+c*dd.y);
    outer+=g.stroke(abs(max(abs(pq.x),abs(pq.y))-.587),.0025,aa)*.8;
}
inner+=g.ring(r,.60,.003,aa);
inner+=g.ring(r,.515,.002,aa);
inner+=g.glyphs(r,frac(a01+rot2*1.4),.522,.592,14,aa,7.7)*.9;
for(int e2=0;e2<2;e2++)
{
    float base=-rot3*9.42+e2*3.14159265; float m=-9;
    for(int e=0;e<3;e++) { float an=base+1.5707963+e*2.0943951; m=max(m,dot(dd,float2(cos(an),sin(an)))); }
    inner+=g.stroke(abs(m-.25),.0025,aa)*.75;
}
inner+=g.ring(r,.30,.003,aa);
inner+=g.ring(r,.12,.004,aa);
float sp=frac((a01+rot1*2)*8);
inner+=(1-smoothstep(.03,.03+aa/max(r*.785,.0001),abs(sp-.5)))*smoothstep(.12,.13,r)*(1-smoothstep(.29,.30,r))*.6;
// Draw-in sweep with a bright leading edge.
float fa=frac(a01-.25), fb=frac(.75-a01);
float sa=smoothstep(rv*1.02,rv*1.02-.015,fa), sb=smoothstep(rv*1.02,rv*1.02-.015,fb);
float head=exp(-pow((fa-rv)*60,2))*(rv<1)*smoothstep(.84,.86,r)*(1-smoothstep(.99,1,r));
float lines=saturate(outer)*sa+saturate(inner)*sb;
float2 q2=dd*3.1+float2(tm*.21,-tm*.17);
float nz=frac(sin(dot(floor(q2),float2(127.1,311.7)))*43758.5453);
float drawn=max(sa*step(.6,r),sb*step(r,.6));
float fill=((.025+.02*nz)*(1-r*.6)*(.8+.2*sin(tm*5+r*9))+exp(-r*r*70)*.6+exp(-pow((r-.985)*40,2))*.15)*drawn;
float lift=smoothstep(0,.12,rv);
// Deepen the tint so the lines stay coloured under bloom; only the brightest crossings go pale.
float3 deep=pow(saturate(Tint.rgb),1.6)*1.7;
float3 col=deep*(lines*1.5+fill*lift+head*1.5)+float3(.35,.55,.9)*saturate(lines-1)*.3;
return col*I.x;
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
    reveal = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -1100, 900)
    reveal.set_editor_property('parameter_name', 'Reveal'); reveal.set_editor_property('default_value', 1.0)
    node = custom(mat, RUNE_CODE, ['W', 'O', 'Tm', 'R', 'I', 'Tint', 'Rv'], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 300)
    for src, pin in ((world, 'W'), (obj, 'O'), (time, 'Tm'), (radius, 'R'), (intensity, 'I'), (tint, 'Tint'), (reveal, 'Rv')):
        mel.connect_material_expressions(src, '', node, pin)
    mel.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mat)
    report['M_RegentRune'] = {'blend': 'additive unlit', 'params': ['Radius', 'Intensity', 'Tint', 'Reveal'], 'style': 'rune mandala'}

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
