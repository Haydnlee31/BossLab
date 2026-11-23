"""Medieval smeltery modules for an opt-in UE human walkthrough. No engine edits."""
import bpy,math,json,sys,hashlib,random,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a-2026-11-16';D=R/'unreal/art-studio/hearth-a-2026-11-16';OUT=E/'export';TEX=OUT/'textures'
for p in [D,OUT,TEX]:p.mkdir(parents=True,exist_ok=True)
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'architecture'
rng=random.Random(6184)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1;S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.device='CPU';S.cycles.use_denoising=True;S.cycles.max_bounces=5;S.world.color=(.08,.09,.10)
materials={};groups={};pieces={};instances=[];source_assets=[]
def material(name,color,rough=.8,metal=0,stem=None,kind='pbr'):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 meta={'color':list(color),'roughness':rough,'metallic':metal,'kind':kind}
 if stem:
  folder=R/'artifacts/art/arena-dungeon-2026-11-09/textures'
  for suffix,key in [('diff','diff'),('arm','arm'),('nor_dx','normal_dx')]:
   p=folder/f'{stem}_{suffix}_2k.jpg'
   if not p.exists():continue
   meta[key]=str(p.relative_to(R));im=bpy.data.images.load(str(p),check_existing=True);im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im
   if key=='diff':m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
   elif key=='arm':
    im.colorspace_settings.name='Non-Color';sep=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(n.outputs['Color'],sep.inputs['Color']);m.node_tree.links.new(sep.outputs['Green'],bs.inputs['Roughness'])
  # Blender view uses gentle actual high-frequency bump; UE uses the genuine normal map.
  noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=60;bu=m.node_tree.nodes.new('ShaderNodeBump');bu.inputs['Distance'].default_value=.015;bu.inputs['Strength'].default_value=.15;m.node_tree.links.new(noise.outputs['Fac'],bu.inputs['Height']);m.node_tree.links.new(bu.outputs['Normal'],bs.inputs['Normal'])
 if kind=='molten':bs.inputs['Base Color'].default_value=(.19,.027,.003,1);bs.inputs['Emission Color'].default_value=(1,.12,.005,1);bs.inputs['Emission Strength'].default_value=4
 materials[name]=meta;return m
stone=material('M_SmeltStone',(.16,.135,.10),stem='castle_wall_varriation');floor=material('M_SmeltFloor',(.20,.18,.15),stem='cobblestone_pavement');dark=material('M_SmeltSoot',(.045,.038,.031),.96);roof=material('M_SmeltVault',(.075,.062,.048),stem='castle_wall_slates');wood=material('M_SmeltOak',(.12,.055,.020),.86,kind='wood');iron=material('M_SmeltIron',(.055,.045,.032),.58,.72);lava=material('M_SmeltMolten',(.25,.035,.002),.8,kind='molten');slag=material('M_SmeltSlag',(.025,.022,.018),.97)
def register(o,group):groups.setdefault(group,[]).append(o);return o
def mesh(n,v,f,m,g):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.data.materials.append(m);return register(o,g)
def box(n,loc,size,m,g,bevel=0):
 sx,sy,sz=[q/2 for q in size];v=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
 o=mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,g);o.location=loc
 if bevel:mod=o.modifiers.new('worn stone edge','BEVEL');mod.width=bevel;mod.segments=1
 return o
def beam(n,a,b,width,depth,m,g):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(width,depth,(b-a).length),m,g,.035);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def stoneblock(n,loc,size,g='SM_SmelteryMasonry'):
 o=box(n,loc,size,stone,g,.045);o.rotation_euler.z=rng.uniform(-.012,.012);return o
# Approved generated irregular-flagstone basecolor, approximate non-calibrated albedo.
fp=E/'inputs/irregular-flagstone-basecolor.png';im=bpy.data.images.load(str(fp),check_existing=True);im.pack();nt=floor.node_tree;bs=nt.nodes.get('Principled BSDF')
for socket in [bs.inputs['Base Color'],bs.inputs['Roughness'],bs.inputs['Metallic'],bs.inputs['Normal']]:
 for link in list(socket.links):nt.links.remove(link)
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.8;bs.inputs['Metallic'].default_value=0
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=80;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.001;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
materials[floor.name]={'color':[.2,.2,.2],'roughness':.8,'metallic':0,'kind':'floor_wet','diff':str(fp.relative_to(R)),'wet_center_m':[7.5,13.5]}
# A coherent, compact workshop shell: no continuous visible combat fence.
cloth=material('M_HearthOxblood',(.13,.025,.014),.93);water=material('M_HearthQuenchWater',(.025,.055,.065),.19,.1,kind='water');sky=material('M_HearthWindow',(.36,.5,.64),.8,kind='window')
bs=sky.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.35,.5,.7,1);bs.inputs['Emission Strength'].default_value=1.5
box('continuous flat flagstone foundation',(0,0,-.2),(37,40,.4),floor,'SM_HearthFloor')
box('rear recessed hearth footing',(-6,22,-.2),(15,9,.4),floor,'SM_HearthFloor')
def arch(n,cx,cy,half,spring,rise,depth,thick,count=28):
 for k in range(count):
  a=math.pi*k/count+.003;b=math.pi*(k+1)/count-.003;v=[]
  for yy in [cy-depth/2,cy+depth/2]:
   for r,zr,t in [(half,rise,a),(half,rise,b),(half+thick,rise+thick,b),(half+thick,rise+thick,a)]:v.append((cx+r*math.cos(t),yy,spring+zr*math.sin(t)))
  o=mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone,'SM_HearthMasonry');mod=o.modifiers.new('worn stone arris','BEVEL');mod.width=.024;mod.segments=1
for side in [-1,1]:
 for row in range(14):
  y=-19.5
  while y<20:
   length=min(rng.uniform(1.0,1.75),20-y);z=.35+row*.7
   # Real high right-hand light opening; no wall placed across it.
   opening=False
   if not opening:stoneblock('hand laid workshop wall',(side*18.2,y+length/2,z),(.85,length-.025,.68),'SM_HearthMasonry')
   y+=length
 for y in [-17,-9,-1,7,15]:
  for row in range(7):stoneblock('low vault abutment',(side*17.2,y,.36+row*.71),(1.6,1.8,.69),'SM_HearthMasonry')
  stoneblock('bearing impost',(side*17.1,y,5.0),(1.95,2.1,.5),'SM_HearthMasonry')
for y in [-17,-9,-1,7,15]:arch('vault dressed wedge',0,y,17.2,5.15,7.0,.9,.6,38)
for i in range(44):
 a=math.pi*i/44;b=math.pi*(i+1)/44
 mesh('smoke stained curved vault',[(17.9*math.cos(a),-20,5.1+7.7*math.sin(a)),(17.9*math.cos(b),-20,5.1+7.7*math.sin(b)),(17.9*math.cos(b),24,5.1+7.7*math.sin(b)),(17.9*math.cos(a),24,5.1+7.7*math.sin(a))],[(0,1,2,3)],roof,'SM_HearthVault')
# Rear irregular masonry has a large left furnace recess and a smaller bellows vault.
arch('recessed great hearth portal',-6,17.6,5.0,3.7,5.8,1.5,.7,28)
arch('bellows working alcove',2.7,18,3.0,2.5,2.8,1.0,.5,20)
for row in range(18):
 z=.35+row*.7;x=-18.5
 while x<18.5:
  w=min(rng.uniform(.9,1.6),18.5-x);xc=x+w/2
  h1=5.1 if z<3.7 else 5.1*math.sqrt(max(0,1-((z-3.7)/5.9)**2));h2=3.05 if z<2.5 else 3.05*math.sqrt(max(0,1-((z-2.5)/2.9)**2))
  if not (abs(xc+6)<h1 or abs(xc-2.7)<h2 or (7.5<xc<13.3 and 5.0<z<10.0)):stoneblock('rear fitted hearth masonry',(xc,20.5 if xc>5 else 18.2,z),(max(.04,w-.025),1.0,.68),'SM_HearthMasonry')
  x+=w
for row in range(19):
 for i in range(23):stoneblock('deep closed workshop rear wall',(-17.7+i*1.6,25.7,.35+row*.7),(1.57,.8,.68),'SM_HearthMasonry')
# Entry arch and masonry piers, not a modern garage wall.
arch('entry stone arch',0,-19.5,4.4,3.8,4.0,1.2,.6,22)
for side in [-1,1]:
 for row in range(12):
  for i in range(7):stoneblock('entry side wall',(side*(5.4+i*1.8),-19.7,.35+row*.7),(1.76,.9,.68),'SM_HearthMasonry')
# Timber lofts with real posts, joists, knee braces, rails and storage, close to workshops.
for side in [-1,1]:
 for yy in [-12,-4,4,12]:
  beam('aged loft bearer',(side*14.9,yy,3.5),(side*18.1,yy,3.5),.30,.36,wood,'SM_HearthTimber')
  beam('loft knee brace',(side*17.5,yy,2.1),(side*15.5,yy,3.35),.22,.26,wood,'SM_HearthTimber')
  beam('iron bound loft upright',(side*17.7,yy,0),(side*17.7,yy,5.0),.34,.38,wood,'SM_HearthTimber')
  for zz in [.5,2.6,4.7]:box('wrought post collar',(side*17.7,yy,zz),(.39,.43,.12),iron,'SM_HearthIron')
 for j in range(10):box('loft worn plank',(side*(15+j*.30),0,3.62),(.28,30,.16),wood,'SM_HearthTimber')
 for yy in [-14,-10,-6,-2,2,6,10,14]:
  beam('loft short baluster',(side*14.9,yy,3.7),(side*14.9,yy,4.5),.10,.12,wood,'SM_HearthTimber')
 beam('loft hand rail',(side*14.9,-15,4.5),(side*14.9,15,4.5),.14,.16,wood,'SM_HearthTimber')
# Cylindrical construction with deliberate tapered sections for staves, logs and baskets.
def lathe(n,loc,profile,sides,m,g,closed=True):
 v=[]
 for z,r in profile:
  for j in range(sides):a=2*math.pi*j/sides;v.append((loc[0]+r*math.cos(a),loc[1]+r*math.sin(a),loc[2]+z))
 f=[]
 for row in range(len(profile)-1):
  for j in range(sides):a=row*sides+j;b=row*sides+(j+1)%sides;f.append((a,b,b+sides,a+sides))
 if closed:f += [tuple(reversed(range(sides))),tuple((len(profile)-1)*sides+j for j in range(sides))]
 return mesh(n,v,f,m,g)
def barrel(loc,scale=1):
 x,y,z=loc
 # Individual bulging staves, hoop bands and recessed lid.
 for j in range(14):
  a=2*math.pi*j/14+.006;b=2*math.pi*(j+1)/14-.006;v=[]
  for zz,r in [(0,.32),(.15,.37),(.52,.40),(.9,.36),(1.02,.31)]:
   for t in [a,b]:v.append((x+scale*r*math.cos(t),y+scale*r*math.sin(t),z+scale*zz))
  mesh('individual oak barrel stave',v,[(k,k+1,k+3,k+2) for k in [0,2,4,6]],wood,'SM_HearthStorage')
 for zz,r in [(.13,.378),(.87,.374)]:lathe('barrel forged hoop',(x,y,z),[(scale*(zz-.035),scale*r),(scale*(zz+.035),scale*r)],28,iron,'SM_HearthStorage',False)
 lathe('barrel recessed head',(x,y,z),[(scale*.985,scale*.30)],14,wood,'SM_HearthStorage')
def chain(a,b):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();length=(b-a).length;u=axis.cross(Vector((0,1,0))).normalized();w=axis.cross(u).normalized()
 for k in range(max(1,int(length/.115))):
  centre=a+axis*(k*.115);across=u if k%2 else w;verts=[]
  for j in range(12):
   t=j*2*math.pi/12;rad=across*math.cos(t)+axis*math.sin(t);p=centre+across*(.053*math.cos(t))+axis*(.078*math.sin(t))
   for q in range(4):f=q*math.pi/2;verts.append(tuple(p+rad*(.011*math.cos(f))+rad.cross(across.cross(axis))*(.011*math.sin(f))))
  mesh('forged interlocking chain',verts,[(j*4+q,j*4+(q+1)%4,((j+1)%12)*4+(q+1)%4,((j+1)%12)*4+q) for j in range(12) for q in range(4)],iron,'SM_HearthIron')
def lantern(x,y,z):
 lathe('lantern roof',(x,y,z),[(.5,.18),(.65,.05)],8,iron,'SM_HearthFixtures');lathe('lantern foot',(x,y,z),[(0,.17),(.05,.17)],8,iron,'SM_HearthFixtures')
 for j in range(4):a=j*math.pi/2;beam('lantern forged bar',(x+.13*math.cos(a),y+.13*math.sin(a),z+.03),(x+.13*math.cos(a),y+.13*math.sin(a),z+.53),.025,.025,iron,'SM_HearthFixtures')
 lathe('contained lantern light',(x,y,z),[(.08,.09),(.47,.09)],8,lava,'SM_HearthFixtures');chain((x,y,z+.65),(x,y,z+1.6))
for loc in [(-15.5,-14,0),(-16,-13.4,0),(16.3,-12,0),(16.5,13,0),(-16.2,7,3.73),(16.4,1,3.73)]:barrel(loc,.85 if loc[2] else 1)
# Stored cut logs on loft: bark geometry and visible end grain palette.
for side in [-1,1]:
 for cluster in [-9,8]:
  for row in range(3):
   for j in range(4-row):
    o=lathe('seasoned firewood log',(0,0,0),[(0,.14),(1.1,.14)],9,wood,'SM_HearthStorage');o.rotation_euler.x=math.pi/2;o.location=(side*(15.7+j*.29),cluster,3.92+row*.25)
# Woven coal baskets, actual open rims and sparse contents at functional stations.
for x,y in [(-15.5,11),(-16.2,11.7),(15.9,-5),(13,16.8)]:
 lathe('woven basket base',(x,y,0),[(.05,.27),(.68,.37)],20,wood,'SM_HearthStorage',False)
 for z in [.10,.20,.30,.40,.50,.60,.69]:lathe('basket horizontal wicker',(x,y,0),[(z,.27+z*.15),(z+.018,.273+z*.15)],24,wood,'SM_HearthStorage',False)
 for j in range(10):
  a=j*math.pi/5;beam('basket upright',(x+.27*math.cos(a),y+.27*math.sin(a),.06),(x+.38*math.cos(a),y+.38*math.sin(a),.72),.018,.018,wood,'SM_HearthStorage')
# Functional blank sword and ingot racks; distinct forged profiles, no hero weapon substitute.
for side,yy in [(1,-10),(-1,5)]:
 for z in [.35,1.2]:beam('blank stock rack crossrail',(side*15.8,yy-1,z),(side*15.8,yy+1,z),.12,.15,wood,'SM_HearthTools')
 for j in range(6):
  x=side*15.7;y=yy-.8+j*.32;v=[(x-.04,y-.045,.12),(x+.04,y-.045,.12),(x+.04,y-.045,1.15),(x,y-.045,1.4),(x-.04,y-.045,1.15)]
  ob=mesh('unfinished tapered sword blank',v,[(0,1,2,3,4)],iron,'SM_HearthTools');mod=ob.modifiers.new('actual blank thickness','SOLIDIFY');mod.thickness=.016
 for j in range(10):box('stacked steel billet',(side*15.8,yy+1.1+(j%3)*.14,.10+(j//3)*.10),(.45,.12,.09),iron,'SM_HearthTools',.01)
# Cloth hangs where a worker can reach it; unequal hems and broad support folds.
for side,y,z,width,height in [(-1,-12,4.7,1.3,1.8),(1,3,5.0,1.1,2.3),(1,-8,2.1,1.2,.9)]:
 v=[]
 for row in range(7):
  t=row/6
  for col in range(7):u=col/6;v.append((side*(15.9+.10*math.sin(u*math.pi*3)*(t+.2)),y+(u-.5)*width,z-t*height-(.08 if row==6 and col%3 else 0)))
 f=[(r*7+c,r*7+c+1,(r+1)*7+c+1,(r+1)*7+c) for r in range(6) for c in range(6)];o=mesh('hanging oxblood workshop cloth',v,f,cloth,'SM_HearthCloth');mod=o.modifiers.new('cloth thickness','SOLIDIFY');mod.thickness=.006
for loc in [(-15,-11,3),(14.8,0,3.1),(2,17,3.2)]:lantern(*loc)
chain((-15.5,-15,2),(-15.5,-15,5.5));chain((15.8,11,2.8),(15.8,11,5.5))
# Only localized hot-metal route on left rear, retaining actual safety containment.
for x,y,sx,sy in [(-11.5,16.8,8.0,.55),(-12.6,14.0,.55,5.6)]:
 box('contained hot casting run',(x,y,.3075),(sx,sy,.025),lava,'SM_HearthMolten')
 if sx>sy:
  for yy in [y-.5,y+.5]:stoneblock('localized hot channel coping',(x,yy,.28),(sx+.6,.38,.56),'SM_HearthMasonry')
 else:
  for xx in [x-.5,x+.5]:stoneblock('localized hot channel coping',(xx,y,.28),(.38,sy+.6,.56),'SM_HearthMasonry')
# Do not place hot metal in clear floor: shift inward-left branch entirely outside X−14.
for ob in groups.get('SM_HearthMolten',[]):
 if ob.location.x< -12:ob.location.x=-15.5
for ob in groups.get('SM_HearthMasonry',[]):
 if ob.name.startswith('localized hot channel coping') and ob.location.x< -12:ob.location.x-=2.9
# Two contained furnace ember beds; generated furnace correctly normalized to front−Y.
for side in [-1,1]:
 for k in range(13):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rng.uniform(.10,.17),location=(-6+side*1.15+rng.uniform(-.35,.35),17.28+rng.uniform(-.10,.25),1.10+rng.uniform(0,.18)));o=bpy.context.object;o.scale.z=.6;o.data.materials.append(lava);register(o,'SM_HearthMolten')
runtime_lights=[{'type':'point','location_cm':[-450,1150,230],'color_rgb':[1,.38,.12],'intensity_lumens':1600,'attenuation_radius_cm':1500},{'type':'spot','location_cm':[750,1605,640],'target_cm':[-100,0,0],'color_rgb':[.60,.74,1],'intensity_lumens':16000,'attenuation_radius_cm':4000,'inner_angle_deg':16,'outer_angle_deg':27,'casts_shadows':True},{'type':'point','location_cm':[-1040,-720,270],'color_rgb':[1,.60,.28],'intensity_lumens':500,'attenuation_radius_cm':1000},{'type':'point','location_cm':[1065,0,270],'color_rgb':[1,.6,.28],'intensity_lumens':550,'attenuation_radius_cm':1000},{'type':'point','location_cm':[145,1360,290],'color_rgb':[1,.6,.28],'intensity_lumens':400,'attenuation_radius_cm':850}]
camera_collision=[{'location_cm':[-1310,0,370],'extent_cm':[40,1600,370]},{'location_cm':[1310,0,370],'extent_cm':[40,1600,370]},{'location_cm':[0,1950,450],'extent_cm':[1400,40,450]}]
# Root-approved compact room revision: architecture/control dimensions only.
# Generated props below retain their independently measured uniform scales.
bpy.context.view_layer.update()
compact=Matrix.Diagonal((.72,.8,.82,1))
for ob in [ob for members in groups.values() for ob in members]:
 transform=compact@ob.matrix_world
 for v in ob.data.vertices:v.co=transform@v.co
 ob.matrix_world=Matrix.Identity(4)
# Existing ember beds seated into the normalized six-metre forge mouths.
for ob in groups.get('SM_HearthMolten',[]):
 if ob.name.startswith('Icosphere'):
  for v in ob.data.vertices:v.co.x-=.18;v.co.y+=.25
# Rear-right quench/window bay, authored in final compact world coordinates.
# Closed returns connect the recessed bay to the hearth/bellows wall.
for zz in [0.35+i*.7 for i in range(13)]:
 stoneblock('right bay deep return',(3.8,15.5,zz),(.65,2.0,.68),'SM_HearthMasonry')
for xx in [5.35,9.75]:stoneblock('window reveal',(xx,16.3,6.0),(.45,.9,4.4),'SM_HearthMasonry')
stoneblock('high window sill',(7.55,16.15,3.95),(4.8,1.15,.3),'SM_HearthMasonry')
for xx in [5.9,6.7,7.5,8.3,9.1]:beam('high window forged bar',(xx,16.15,4.1),(xx,16.15,8.1),.055,.055,iron,'SM_HearthIron')
mesh('visible overcast window',[(5.7,16.7,4.1),(9.4,16.7,4.1),(9.4,16.7,8.2),(5.7,16.7,8.2)],[(0,1,2,3)],sky,'SM_HearthWindow')
# Occupied rear loft below opening, not a blank wall field.
for xx in [4.7,12.0]:
 beam('rear loft upright',(xx,15.6,0),(xx,15.6,5.4),.28,.32,wood,'SM_HearthTimber')
 beam('rear loft knee brace',(xx,15.6,2.2),(xx,17.3,3.45),.22,.24,wood,'SM_HearthTimber')
for j in range(9):box('rear loft floorboard',(8.2,15.8+j*.25,3.5),(8.2,.23,.13),wood,'SM_HearthTimber')
beam('rear loft front bearer',(4.1,15.7,3.35),(12.3,15.7,3.35),.3,.32,wood,'SM_HearthTimber')
for xx in [4.7,11.4]:
 for row in range(3):
  for j in range(3-row):
   ob=lathe('rear loft cut log',(0,0,0),[(0,.13),(1,.13)],9,wood,'SM_HearthStorage');ob.rotation_euler.x=math.pi/2;ob.location=(xx+j*.28,16.7,3.7+row*.23)
barrel((11.2,17,3.6),.8)
# Quench water below actual cistern rim; no overlapping floor decal geometry.
mesh('quench water within real rim',[(5.95,13.55,.88),(9.05,13.55,.88),(9.05,15.45,.88),(5.95,15.45,.88)],[(0,1,2,3)],water,'SM_HearthQuenchSurface')
steam=material('M_HearthSteam',(.18,.22,.24),1,kind='steam');bs=steam.node_tree.nodes.get('Principled BSDF');bs.inputs['Alpha'].default_value=.04
for vertices in [[(7.1,14.5,.95),(7.9,14.5,.95),(7.9,14.5,2.05),(7.1,14.5,2.05)],[(7.5,14.1,.95),(7.5,14.9,.95),(7.5,14.9,2.05),(7.5,14.1,2.05)]]:mesh('subtle quench vapor card',vertices,[(0,1,2,3)],steam,'SM_HearthSteam')
# Foreground suspended fixture frames actual left-offset entry without floor clutter.
lantern(-9.2,-5.5,3.25);chain((-9.2,-5.5,4.9),(-9.2,-5.5,8.3))
# Final readable rear-right workplace dressing; all floor objects outside clear field.
lantern(4.8,13.6,2.7);chain((4.8,13.6,4.3),(4.8,13.6,8.1))
lantern(11.2,13.8,2.9);chain((11.2,13.8,4.5),(11.2,13.8,7.5))
for x in [10.2,11.1]:barrel((x,16.1,3.6),.95)
for row in range(4):
 for j in range(5-row):
  ob=lathe('visible loft stacked log',(0,0,0),[(0,.16),(1.3,.16)],10,wood,'SM_HearthStorage');ob.rotation_euler.x=math.pi/2;ob.location=(4.7+j*.32,16.4,3.73+row*.28)
for j in range(6):
 x=10+j*.22;y=15.1
 ob=mesh('rear workbay sword stock',[(x-.05,y,.25),(x+.05,y,.25),(x+.05,y,1.65),(x,y,1.95),(x-.05,y,1.65)],[(0,1,2,3,4)],iron,'SM_HearthTools');mod=ob.modifiers.new('stock plate thickness','SOLIDIFY');mod.thickness=.02
beam('rear stock support',(9.85,15.25,.5),(11.3,15.25,.5),.10,.14,wood,'SM_HearthTools')
v=[]
for row in range(9):
 for col in range(9):
  t=row/8;u=col/8;v.append((3.9+u*1.25,15.5+.09*math.sin(u*math.pi*4)*t,5.8-t*2.2-.1*t*u))
ob=mesh('visible workshop hanging banner',v,[(r*9+c,r*9+c+1,(r+1)*9+c+1,(r+1)*9+c) for r in range(8) for c in range(8)],cloth,'SM_HearthCloth');mod=ob.modifiers.new('sewn cloth thickness','SOLIDIFY');mod.thickness=.006
# Match light origins to actual final-space lantern emitter centres.
for item,pos in zip(runtime_lights[2:],[[-920,-550,352.5],[480,1360,297.5],[1120,1380,317.5]]):item['location_cm']=pos
(E/'fixture-light-pairs.json').write_text(json.dumps({'scope':'three selected lanterns; emitter midpoint z+0.275m','positions_cm':[i['location_cm'] for i in runtime_lights[2:]]},indent=2))
# Export physical planar UVs for authored architecture.
bpy.context.view_layer.update()
for g,obs in groups.items():
 for o in obs:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='physical scale UV')
  for poly in o.data.polygons:
   n=o.matrix_world.to_3x3()@poly.normal;axis=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=axis];tile=5.0 if g=='SM_HearthFloor' else 3.0
   for li in poly.loop_indices:
    co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/tile,co[axes[1]]/tile)
for ob in groups.get('SM_HearthSteam',[]):
 for li,uv in zip(ob.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):ob.data.uv_layers.active.data[li].uv=uv
# Optional actual generated assets; no placeholder mesh masquerading as final generated art.
config=Path(__file__).with_name('assets.json');cfg=json.loads(config.read_text()) if config.exists() else {}
if mode.startswith('architecture'):cfg={}
if mode=='final':
 missing=[e['path'] for e in cfg.values() if not (R/e['path']).exists()]
 if missing:raise RuntimeError('Final assembly missing generated source meshes: '+str(missing))
def find_image(sock,seen=None):
 seen=seen or set()
 for link in sock.links:
  node=link.from_node
  if node in seen:continue
  seen.add(node)
  if node.type=='TEX_IMAGE' and node.image:return node.image
  for inp in node.inputs:
   im=find_image(inp,seen)
   if im:return im
 return None
def import_asset(key,entry):
 p=R/entry['path']
 if not p.exists():return
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));obs=[o for o in set(bpy.data.objects)-before if o.type=='MESH'];allnew=set(bpy.data.objects)-before
 rot=Matrix.Rotation(math.radians(entry.get('rotate_z_deg',0)),4,'Z');coords={o:[rot@o.matrix_world@v.co for v in o.data.vertices] for o in obs};ps=[v for a in coords.values() for v in a];lo=Vector(tuple(min(v[i] for v in ps) for i in range(3)));hi=Vector(tuple(max(v[i] for v in ps) for i in range(3)));size=hi-lo;fit=min(entry['bounds_m'][i]/max(1e-8,size[i]) for i in range(3));center=(lo+hi)/2
 total=0
 for o in obs:o.data.calc_loop_triangles();total+=len(o.data.loop_triangles)
 asset='SM_'+key
 for o in obs:
  o.data=o.data.copy();o.parent=None
  for v,co in zip(o.data.vertices,coords[o]):v.co=(co-Vector((center.x,center.y,lo.z)))*fit
  o.matrix_world.identity();o.name=asset
  mod=o.modifiers.new('derived mesh budget','DECIMATE');mod.ratio=min(1,entry.get('triangles',40000)/max(1,total));bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  # Remove confirmed area-zero faces on derived copies, preserve original HF file.
  bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if f.calc_area()<=1e-12];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free()
  for slot in o.material_slots:
   if not slot.material:continue
   m=slot.material;m.name=asset+'_'+m.name.replace('.','_');bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   if not bs:continue
   info={'color':list(bs.inputs['Base Color'].default_value)[:3],'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'kind':'pbr'}
   for channel,socket in [('diff','Base Color'),('arm','Roughness'),('normal_gl','Normal')]:
    im=find_image(bs.inputs[socket])
    if im:
     path=TEX/(m.name+'_'+channel+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();im.pack();info[channel]=str(path.relative_to(R))
   materials[m.name]=info
  register(o,asset)
 for o in allnew:
  if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
 source_assets.append({'key':key,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_triangles':total,'fit_scale':fit,'fitted_size_m':list(size*fit),'placements':entry['instances']})
 for placement in entry['instances']:instances.append({'asset':'/Game/BossLab/HearthA/'+asset,'location_cm':[v*100 for v in placement['location_m']],'rotation_deg':[0,placement.get('yaw_deg',0),0],'scale':[1,1,1]})
for key,entry in cfg.items():import_asset(key,entry)
# Export each mesh family, apply modifiers once, keep separate reusable prop pivots.
for g,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=g;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-12],context='FACES');bm.to_mesh(o.data);bm.free();o.data.update();o.data.calc_loop_triangles();points=[v.co for v in o.data.vertices];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
 pieces[g]={'triangles':len(o.data.loop_triangles),'area_le_1e_12_triangles':sum(t.area<=1e-12 for t in o.data.loop_triangles),'finite_vertices':all(all(math.isfinite(c) for c in v.co) for v in o.data.vertices),'bounds_m':[lo,hi],'size_m':[hi[i]-lo[i] for i in range(3)],'materials':[m.name for m in o.data.materials],'source':'derived generated prop' if any('/'+g==i['asset'][-len(g)-1:] for i in instances) else 'authored modular architecture'}
 copy=o.copy();copy.data=o.data.copy();S.collection.objects.link(copy);copy.name=g+'_UECopy';copy.matrix_world=Matrix.Identity(4)
 bm=bmesh.new();bm.from_mesh(copy.data);bm.transform(Matrix.Diagonal((1,-1,1,1)));bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(copy.data);bm.free();copy.data.update()
 bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);bpy.context.view_layer.objects.active=copy
 bpy.ops.export_scene.fbx(filepath=str(OUT/(g+'.fbx')),use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='STRIP',embed_textures=False)
 bpy.data.objects.remove(copy,do_unlink=True)
 if not any(i['asset'].endswith('/'+g) for i in instances):instances.append({'asset':'/Game/BossLab/HearthA/'+g,'location_cm':[0,0,0],'rotation_deg':[0,0,0],'scale':[1,1,1]})
# Place mesh instances only after local-pivot exports; source assets remain untouched.
for i in instances:
 name=i['asset'].split('/')[-1];source=bpy.data.objects.get(name)
 if not source:continue
 ob=source.copy();ob.data=source.data;S.collection.objects.link(ob);ob.name=name+'_PLACED';ob.location=Vector(i['location_cm'])/100;ob.rotation_euler.z=math.radians(i['rotation_deg'][1])
for name in pieces:bpy.data.objects[name].hide_render=True;bpy.data.objects[name].hide_set(True)
(OUT/'pieces.json').write_text(json.dumps(pieces,indent=2));(OUT/'materials.json').write_text(json.dumps(materials,indent=2));(OUT/'layout.json').write_text(json.dumps({'schema':1,'units':'cm','axis':'+X width,+Y rear','walkable_cm':[2000,2400],'instances':instances,'lights':runtime_lights,'camera_collision':camera_collision},indent=2));(OUT/'sources.json').write_text(json.dumps(source_assets,indent=2))
# One efficient preview, not a substitute for the real Unreal walkthrough.
def light(n,loc,power,size,col,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('Furnace reflected amber',(-4.5,11.5,2.3),1800,3,(1,.46,.18),(-4.5,15.5,3))
light('High window cold daylight',(7.5,16.4,6.4),3500,3,(.62,.77,1),(-1,0,0))
light('Warm entry bounce',(-6,-10,3),500,6,(1,.65,.35),(0,8,2))
bpy.ops.object.camera_add(location=(-6,-8,1.8));S.camera=bpy.context.object;S.camera.rotation_euler=(Vector((0,8,2.5))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=24
S.render.resolution_x=1400;S.render.resolution_y=900;S.render.resolution_percentage=100
for im in bpy.data.images:
 if im.type=='IMAGE' and im.size[0]>0 and not im.packed_file:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(D/(mode+'.blend')));S.render.filepath=str(E/(mode+'-preview.png'));bpy.ops.render.render(write_still=True)
S.camera.location=(-8.1,-11.8,2.8);S.camera.rotation_euler=(Vector((0,8,2.1))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.type='PERSP';S.camera.data.sensor_fit='HORIZONTAL';S.camera.data.angle=math.radians(75);S.render.filepath=str(E/(mode+'-gameplay.png'));bpy.ops.render.render(write_still=True)
print(json.dumps({'mode':mode,'pieces':len(pieces),'instances':len(instances),'triangles_unique':sum(v['triangles'] for v in pieces.values()),'source_assets':source_assets},indent=2))
