"""Hearth A2: new asymmetric masonry/workshop construction. DCC-only review."""
import bpy,math,random,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';D=R/'unreal/art-studio/hearth-a2-2026-11-16';E.mkdir(exist_ok=True);D.mkdir(exist_ok=True)
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'architecture01'
rng=random.Random(2411);bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
S=bpy.context.scene;S.unit_settings.system='METRIC';S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True;S.cycles.max_bounces=5;S.world.color=(.045,.05,.06)
groups={}
def mat(name,color,rough=.8,metal=0,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if texture:
  im=bpy.data.images.load(str(R/texture),check_existing=True);im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.links.new(n.outputs['Color'],b.inputs['Base Color'])
 return m
stones=[mat('weathered masonry '+str(i),(.15+i*.015,.125+i*.013,.095+i*.011)) for i in range(5)]
mortar=mat('deep charcoal mortar',(.035,.030,.025));wood=mat('aged oak',(.095,.045,.018));iron=mat('forged iron',(.04,.035,.03),.65,.7);cloth=mat('faded oxblood',(.11,.018,.009));floor=mat('irregular flagstone',(.19,.17,.14),.85,texture='artifacts/art/hearth-a-2026-11-16/inputs/irregular-flagstone-basecolor.png')
# Reference-specific generated base colour only; geometry supplies actual relief.
ashlar=bpy.data.images.load(str(E/'inputs/ashlar-basecolor.png'),check_existing=True);ashlar.pack()
for m in stones:
 nt=m.node_tree;b=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=ashlar
 nt.links.new(tex.outputs['Color'],b.inputs['Base Color']);b.inputs['Roughness'].default_value=.88
cutstone=mat('joint-free weathered cut stone',(.16,.14,.11),.88,texture='artifacts/art/hearth-a2-2026-11-16/inputs/joint-free-stone.png')
# Six deliberately varied stone values and scoped wet paths; shared authored shader contract.
floor_mats=[]
damp_paths=[{'centre_m':[6.5,5.0],'radii_m':[3.0,4.5]},{'centre_m':[-4.5,7.0],'radii_m':[2.7,3.0]}]
for index,tint in enumerate([(1.0,.94,.83),(.79,.80,.79),(.91,.83,.71),(1.13,1.06,.93),(.74,.70,.63),(.98,.99,1.0)]):
 m=cutstone.copy();m.name='worn floor stone '+str(index);nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*tint,1);nt.links.new(tex.outputs['Color'],mul.inputs[1]);nt.links.new(mul.outputs[0],bs.inputs['Base Color']);dry=.78+index*.025
 pos=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(pos.outputs['Position'],sep.inputs[0]);masks=[]
 def mathnode(op,a=None,b=None):
  n=nt.nodes.new('ShaderNodeMath');n.operation=op
  for i,v in enumerate([a,b]):
   if v is None:continue
   if isinstance(v,(int,float)):n.inputs[i].default_value=v
   else:nt.links.new(v,n.inputs[i])
  return n.outputs[0]
 for path in damp_paths:
  xx=mathnode('DIVIDE',mathnode('SUBTRACT',sep.outputs['X'],path['centre_m'][0]),path['radii_m'][0]);yy=mathnode('DIVIDE',mathnode('SUBTRACT',sep.outputs['Y'],path['centre_m'][1]),path['radii_m'][1]);dist=mathnode('SQRT',mathnode('ADD',mathnode('MULTIPLY',xx,xx),mathnode('MULTIPLY',yy,yy)));masks.append(mathnode('MAXIMUM',0,mathnode('SUBTRACT',1,dist)))
 wet=mathnode('MAXIMUM',masks[0],masks[1]);rough=mathnode('SUBTRACT',dry,mathnode('MULTIPLY',wet,.48));nt.links.new(rough,bs.inputs['Roughness']);shade=mathnode('SUBTRACT',1,mathnode('MULTIPLY',wet,.17));darker=nt.nodes.new('ShaderNodeMixRGB');darker.blend_type='MULTIPLY';darker.inputs[0].default_value=1;nt.links.new(mul.outputs[0],darker.inputs[1]);nt.links.new(shade,darker.inputs[2]);nt.links.new(darker.outputs[0],bs.inputs['Base Color']);m['hearth_a2_floor_tint']=list(tint);m['hearth_a2_floor_dry_roughness']=dry;floor_mats.append(m)
(E/'floor-shader-contract.json').write_text(json.dumps({'scope':'artistic surface variation, not calibrated PBR','author_world_paths':damp_paths,'mask':'max(saturate(1-length((P.xy-centre)/radii)))','roughness':'dry_roughness - 0.48*mask','basecolor':'joint_free_texture * stone_tint * (1-0.17*mask)','runtime_coordinate_rule':'reflect centre X once for Unreal'},indent=2))
# Subtle elongated wood grain is authored background shading, not a scanned wood claim.
nt=wood.node_tree;b=nt.nodes.get('Principled BSDF');tc=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(4,4,.15);nt.links.new(tc.outputs['Generated'],mapping.inputs[0]);noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=14;nt.links.new(mapping.outputs[0],noise.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.025,.012,.004,1);ramp.color_ramp.elements[1].color=(.16,.075,.025,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],b.inputs['Base Color'])
def mesh(name,vs,fs,m,group):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);S.collection.objects.link(ob);ob.data.materials.append(m);groups.setdefault(group,[]).append(ob);return ob
def box(name,loc,sz,m,group,bev=0):
 x,y,z=[a/2 for a in sz];v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)];o=mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,group);o.location=loc
 if bev:b=o.modifiers.new('rounded working edges','BEVEL');b.width=bev;b.segments=2
 return o
def beam(name,a,b,w,d,m=wood):
 a,b=Vector(a),Vector(b);o=box(name,(a+b)/2,(w,d,(a-b).length),m,'timber',.025);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def stone(name,loc,sz):
 # Eight-sided chipped plan perimeter: controlled missing corners, not a noise-displaced face.
 x,y,z=[v/2 for v in sz];cuts=[rng.uniform(.025,.075)*min(sz[0],sz[1]) for _ in range(4)]
 a,b,c,d=cuts;ring=[(-x+a,-y),(x-b,-y),(x,-y+b),(x,y-c),(x-c,y),(-x+d,y),(-x,y-d),(-x,-y+a)]
 v=[(xx,yy,zz) for zz in [-z,z] for xx,yy in ring];f=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
 ob=mesh(name,v,f,rng.choice(stones),'masonry');ob.location=loc;mod=ob.modifiers.new('soft chipped stone arris','BEVEL');mod.width=.018;mod.segments=2;return ob
def arch(name,cx,y,half,spring,rise,depth,thick,count=23,pointed=False):
 # Actual wedge voussoirs, with normal-depth extrusion and recessed mortar core.
 for j in range(count):
  a=math.pi*j/count+.004;b=math.pi*(j+1)/count-.004;v=[]
  for yy in [y-depth/2,y+depth/2]:
   for rr,rz,t in [(half,rise,a),(half,rise,b),(half+thick,rise+thick,b),(half+thick,rise+thick,a)]:v.append((cx+rr*math.cos(t),yy,spring+rz*math.sin(t)))
  o=mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],rng.choice(stones),'masonry');mod=o.modifiers.new('worn voussoir arris','BEVEL');mod.width=.022;mod.segments=2
 for side in [-1,1]:
  for k in range(math.ceil(spring/.6)):
   z0=k*.6;h=min(.6,spring-z0)
   if h>0:stone(name+' pier',(cx+side*(half+thick/2),y,z0+h/2),(thick,depth,h-.018))
# Floor full-support base, no stacked coplanar decals.
box('level continuous walking foundation',(0,1,-.21),(25,31,.30),mortar,'floor')
# Real tessellated flagstones: shared irregular cell lattice, recessed joints, level tops.
# Artistic geometry, not inferred photogrammetric height from generated colour.
# Irregular polygonal flagstones via bounded planar nearest-centre cells.
# This is authored paving topology, not displacement or a texture-derived height claim.
seeds=[]
for j in range(23):
 for i in range(20):seeds.append((-12.5+(i+.5)*1.25+rng.uniform(-.38,.38),-14.5+(j+.5)*31/23+rng.uniform(-.40,.40)))
def clip_cell(poly,nx,ny,offset):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=a[0]*nx+a[1]*ny-offset;db=b[0]*nx+b[1]*ny-offset
  if da<=1e-9:out.append(a)
  if (da<=0)!=(db<=0):
   t=da/(da-db);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
 return out
for sx,sy in seeds:
 poly=[(-12.5,-14.5),(12.5,-14.5),(12.5,16.5),(-12.5,16.5)]
 for tx,ty in sorted(seeds,key=lambda p:(p[0]-sx)**2+(p[1]-sy)**2)[1:]:
  poly=clip_cell(poly,tx-sx,ty-sy,(tx*tx+ty*ty-sx*sx-sy*sy)/2)
  if not poly:break
 if len(poly)<3:continue
 cx=sum(p[0] for p in poly)/len(poly);cy=sum(p[1] for p in poly)/len(poly);poly=[(cx+(x-cx)*.981,cy+(y-cy)*.981) for x,y in poly];n=len(poly);vs=[(x,y,z) for z in [-.055,0] for x,y in poly]
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 ob=mesh('individual level worn flagstone',vs,fs,floor,'floor');mod=ob.modifiers.new('actual worn slab chamfer','BEVEL');mod.width=.014;mod.segments=2
box('deep forge continuous footing',(-4.2,16.5,-.21),(13,8,.30),mortar,'floor')
# Unequal flagstone boundary courses are real bevelled slabs, outside clear walking field.
for side in [-1,1]:
 for j in range(12):
  y=-11+j*2.1;x=side*(9.0+rng.uniform(0,.5));o=stone('edge paving slab',(x,y,.035),(rng.uniform(.8,1.4),rng.uniform(1.3,1.9),.07));o.rotation_euler.z=rng.uniform(-.08,.08)
# Giant asymmetrical forge hood and smaller attached bellows portal.
arch('great hearth receiving hood',-4.2,12,4.6,2.8,6.2,2.4,.8,29)
arch('low bellows alcove',3.3,11.5,2.15,1.6,2.8,2.0,.65,17)
box('closed deep hearth chamber ceiling',(-4.0,16.0,9.65),(13.4,8.0,.65),stones[0],'masonry')
# Deep alcove back/side masonry, not a wall across the opening.
box('forge dark rear masonry',(-3.8,19.7,4.7),(12.2,.9,9.4),stones[0],'masonry')
for xx in [-10.3,2.5]:box('forge thick return',(xx,16.0,4.5),(.9,8.5,9),stones[0],'masonry')
box('bellows dark back',(3.3,14.1,2.5),(5.5,.7,5),mortar,'masonry')
# Rear infill obeys arch envelope: no square grey panel or stones crossing the vault.
for row in range(18):
 z=.3+row*.55
 for i in range(23):
  x=-10.4+i*.9+(.45 if row%2 else 0)
  in_forge=any(abs((xx+4.2)/5.5)<1 and z-.3<2.8+7.1*math.sqrt(max(0,1-((xx+4.2)/5.5)**2)) for xx in [x-.5,x,x+.5])
  in_bell=any(abs((xx-3.3)/2.85)<1 and z-.3<1.6+3.5*math.sqrt(max(0,1-((xx-3.3)/2.85)**2)) for xx in [x-.5,x,x+.5])
  if not in_forge and not in_bell:stone('rear fitted spandrel',(x,12.5,z),(.86,.95,.52))
# Continuous fitted structural spandrel core follows BOTH outer arch envelopes.
# Narrow sampled columns close mortar hearts without crossing either open vault.
def rear_lower(x):
 heights=[0]
 for cx,half,spring,rise in [(-4.2,5.4,2.8,7.0),(3.3,2.8,1.6,3.45)]:
  if abs(x-cx)<=half:heights.append(spring+rise*math.sqrt(max(0,1-((x-cx)/half)**2)))
 return max(heights)
for j in range(220):
 x0=-10.5+j*.1;x1=x0+.102;z0=rear_lower(x0);z1=rear_lower(x1)
 v=[(x0,y,z0),(x1,y,z1),(x1,y,10.6),(x0,y,10.6)] if False else []
 for y in [12.0,13.0]:v.extend([(x0,y,z0),(x1,y,z1),(x1,y,10.6),(x0,y,10.6)])
 mesh('fitted arch spandrel core',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stones[0],'masonry')
# Main asymmetric segmental roof, fewer stronger load ribs; web physically recessed.
def roofpoint(t,y,offset=0):
 x=-10.7+22*t;z=4.5+2.9*t+4.2*math.sin(math.pi*t)+offset;return(x,y,z)
for y in [-9,-1.5,6.0]:
 for j in range(32):
  t0=j/32+.001;t1=(j+1)/32-.001;v=[]
  for yy in [y-.42,y+.42]:
   for t,off in [(t0,0),(t1,0),(t1,.55),(t0,.55)]:v.append(roofpoint(t,yy,off))
  o=mesh('segmental structural vault rib',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],rng.choice(stones),'masonry');mod=o.modifiers.new('rib stone arris','BEVEL');mod.width=.018;mod.segments=1
for k in range(4):
 y0=-13+k*6.6;y1=y0+6.6;v=[roofpoint(j/40,y,.38) for y in [y0,y1] for j in range(41)];mesh('continuous recessed stone vault web',v,[(j,j+1,42+j,41+j) for j in range(40)],stones[1],'vault')
# Entry-end wall is real closed architecture, not an open studio backdrop.
arch('entry stone doorway',0,-13.3,1.65,2.6,1.9,.75,.48,19)
for row in range(20):
 z=.28+row*.56;x=-11.5-rng.uniform(0,.5)
 while x<11.6:
  width=rng.uniform(.65,1.35);left=max(-11.5,x);right=min(11.6,x+width-.018);x+=width
  roofz=min(roofpoint((left+10.7)/22,0)[2] if 0<=(left+10.7)/22<=1 else 4.4,roofpoint((right+10.7)/22,0)[2] if 0<=(right+10.7)/22<=1 else 7.3)
  if z+.28>roofz:continue
  middle=(left+right)/2
  if abs(middle)<2.15 and z<2.6+2.4*math.sqrt(max(0,1-(middle/2.15)**2))+.3:continue
  stone('entry staggered ashlar',(middle,-13.55,z),(right-left,.65,.54))
# Closed structural heart, recessed oak door, and load-bearing reveal.
box('entry continuous backing',(0,-14.0,6.0),(24,.35,12.0),mortar,'masonry')
for j in range(12):
 x=-1.57+j*.285;top=2.6+1.85*math.sqrt(max(0,1-(x/1.65)**2))
 box('entry pegged oak door',(x,-13.65,top/2),(.27,.12,top),wood,'timber',.012)
for z in [.8,2.1,3.1]:beam('entry iron strap',(-1.55,-13.55,z),(1.55,-13.55,z),.11,.07,iron)
# Side enclosure masonry and low gallery; no tall empty showroom bay.
for side in [-1,1]:
 for row in range(11):
  z=.29+row*.57;y=-12
  while y<12:
   length=min(rng.uniform(.75,1.45),12-y)
   # Window replaces wall at right rear, actual opening not emissive wall decal.
   if not(side==1 and 3.5<y<11):stone('side thick laid wall',(side*11.2,y+length/2,z),(.9,length-.02,.54))
   y+=length
 for y in [-10,-4,2,9.5]:
  beam('gallery oak post',(side*10.2,y,0),(side*10.2,y,4.3),.35,.38)
  beam('gallery knee brace',(side*10.2,y,1.95),(side*11.1,y,3.1),.22,.25)
 for j in range(9):box('gallery floorboard',(side*(10.05+j*.19),-4.5 if side==1 else -.5,3.15),(.18,15 if side==1 else 24,.15),wood,'timber',.015)
 beam('gallery front bearer',(side*10,-12,3.0),(side*10,3.0 if side==1 else 11.5,3.0),.32,.38)
 for z in [3.6,4.2]:beam('gallery irregular rail',(side*10,-12,z),(side*10,3.0 if side==1 else 11.5,z),.12,.16)
# Actual generated Gothic frame replaces the coarse arch and Y tracery.
# Complete angled window bay wall; actual opening is the only daylight path.
for row in range(15):
 z=.3+row*.6;x=-4.4-rng.uniform(0,.5)
 while x<4.4:
  width=rng.uniform(.58,1.23);a=max(-4.4,x);b=min(4.4,x+width-.018);x+=width
  opening=1.6*max(0,1-(max(0,z-.3-2.0)/5.5)**(1/.36)) if 1.8<z<7.8 else 0
  spans=[(a,min(b,-opening)),(max(a,opening),b)] if opening else [(a,b)]
  for left,right in spans:
   if right-left<.15:continue
   cx=(left+right)/2
   ob=stone('staggered window bay ashlar',(11.4+.7071*cx,8.2-.7071*cx,z),(right-left,.9,rng.uniform(.558,.58)));ob.rotation_euler.z=-math.pi/4
box('recessed quench bay support',(11.7,8,-.21),(7,9,.30),mortar,'floor')
# Closed mortar heart behind window stones: light only through intended aperture.
for j in range(80):
 x0=-4+j*.1;x1=x0+.102
 def topopening(x):return 2.8+4.3*(1-min(1,abs(x)/1.14))**.45 if abs(x)<1.14 else 0
 z0,z1=topopening(x0),topopening(x1)
 bands=[(0,2.8,0,2.8),(z0,9.4,z1,9.4)] if abs((x0+x1)/2)<1.14 else [(0,9.4,0,9.4)]
 for za,ta,zb,tb in bands:
  vs=[]
  for dep in [.48,.95]:
   for x,z in [(x0,za),(x1,zb),(x1,tb),(x0,ta)]:vs.append((11.4+.7071*x+.7071*dep,8.2-.7071*x+.7071*dep,z))
  mesh('solid window mortar heart',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mortar,'masonry')
# Solid window sill and wall below aperture, not an open doorway to floor.
for row in range(4):
 x=-2.0-rng.uniform(0,.4)
 while x<2.0:
  width=rng.uniform(.55,1.05);left=max(-2,x);right=min(2,x+width-.018);x+=width
  if right-left<.12:continue
  localx=(left+right)/2;xx=11.4+.7071*localx;yy=8.2-.7071*localx
  ob=stone('staggered window sill wall',(xx,yy,.3+row*.6),(right-left,1.0,.58));ob.rotation_euler.z=-math.pi/4
ob=stone('deep window sill',(11.4,8.2,2.5),(4.1,1.1,.27));ob.rotation_euler.z=-math.pi/4
# Foreground and gallery working-storage layer, independent of forthcoming HF hero props.
endwood=mat('exposed cut oak end',(.22,.13,.055));rope=mat('rough hemp rope',(.18,.13,.075),.96)
def cylinder_between(name,a,b,radius,material,group='storage',sides=10):
 a,b=Vector(a),Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,0,1)))
 if u.length<.1:u=axis.cross(Vector((0,1,0)))
 u.normalize();v=axis.cross(u);vs=[tuple(p+radius*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*v)) for p in [a,b] for j in range(sides)];fs=[tuple(range(sides-1,-1,-1)),tuple(range(sides,2*sides))]+[(j,(j+1)%sides,(j+1)%sides+sides,j+sides) for j in range(sides)];return mesh(name,vs,fs,material,group)
for side,y in [(-1,-7),(-1,6),(1,-5),(1,1)]:
 for row in range(4):
  for j in range(5-row):
   x=side*(10.2+j*.28);z=3.45+row*.23
   cylinder_between('stored oak log',(x,y,z),(x,y+1.4,z),.14,wood)
   cylinder_between('visible fresh log end',(x,y-.015,z),(x,y-.025,z),.125,endwood)
# Close timber framing: short diagonal braces, iron straps and pegs.
for side in [-1,1]:
 x=side*9.6;beam('near entry framing post',(x,-6,0),(x,-6,7.8),.46,.48)
 beam('near arch-to-post brace',(x,-6,4.7),(side*7.8,-6,6.3),.31,.35)
 for z in [1.15,3.05,5.4]:
  box('forged post binding',(x,-6,z),(.49,.51,.13),iron,'iron',.012)
  for yy in [-6.27,-5.73]:cylinder_between('peened binding bolt',(x,yy,z),(x,yy+(.04 if yy< -6 else -.04),z),.035,iron,'iron',8)
# Suspended real chain links at the entry framing, alternating planes.
for i in range(18):
 bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=4,major_radius=.10,minor_radius=.019,location=(-9.3,-5.8,3.8+i*.17));ob=bpy.context.object;ob.rotation_euler.x=math.pi/2;ob.rotation_euler.z=(i%2)*math.pi/2;ob.data.materials.append(iron);groups.setdefault('iron',[]).append(ob)
# Coiled rope on the side post, distinct from metal chain.
for i in range(4):
 bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=5,major_radius=.28+i*.014,minor_radius=.026,location=(9.55,-5.72,2.5+i*.035));ob=bpy.context.object;ob.rotation_euler.x=math.pi/2;ob.data.materials.append(rope);groups.setdefault('storage',[]).append(ob)
# An actual folded hanging apron/cloth silhouette, not a flat rectangular decal.
for side,y,z in [(-1,-6.2,4.8),(1,.4,4.0)]:
 vs=[]
 for row in range(10):
  t=row/9
  for col in range(9):
   u=col/8;vs.append((side*(9.7+.12*math.sin(u*math.tau*2)*(.3+t)),y+(u-.5)*1.25,z-t*1.85-.12*t*u))
 ob=mesh('folded worker cloth',vs,[(r*9+c,r*9+c+1,(r+1)*9+c+1,(r+1)*9+c) for r in range(9) for c in range(8)],cloth,'cloth');mod=ob.modifiers.new('cloth edge thickness','SOLIDIFY');mod.thickness=.008
# Long oxblood cloth anchors forge-to-bellows transition, with broad sewn folds.
vs=[]
for row in range(13):
 t=row/12
 for col in range(9):
  u=col/8;vs.append((1.45+u*1.25,10.85+.10*math.sin(u*math.tau*2)*(.4+t),7.1-t*2.7-.18*t*u))
ob=mesh('hearth hanging oxblood banner',vs,[(r*9+c,r*9+c+1,(r+1)*9+c+1,(r+1)*9+c) for r in range(12) for c in range(8)],cloth,'cloth');mod=ob.modifiers.new('banner hem thickness','SOLIDIFY');mod.thickness=.008
heat=mat('contained molten metal',(.22,.025,.002),.5);bs=heat.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.09,.002,1);bs.inputs['Emission Strength'].default_value=2.5
for x,y,sx,sy in [(-9.4,11.6,.48,3.4),(-7.5,9.95,4.2,.48)]:
 box('local L casting route',(x,y,.22),(sx,sy,.06),heat,'hotmetal',.012)
 if sx>sy:
  for yy in [y-.39,y+.39]:stone('casting run protective coping',(x,yy,.22),(sx+.35,.29,.44))
 else:
  for xx in [x-.39,x+.39]:stone('casting run protective coping',(xx,y,.22),(.29,sy+.35,.44))
water=mat('cool quench water',(.035,.065,.075),.2,.08)
rot=-math.pi/4;vs=[]
for x,y in [(-1.3,-.65),(1.3,-.65),(1.3,.65),(-1.3,.65)]:vs.append((10.7+x*math.cos(rot)-y*math.sin(rot),7.5+x*math.sin(rot)+y*math.cos(rot),.75))
mesh('real cistern water surface',vs,[(0,1,2,3)],water,'water')
sky=mat('daylit exterior aperture',(.18,.27,.4));bs=sky.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.25,.40,.6,1);bs.inputs['Emission Strength'].default_value=.6
outline=[(-1.14,2.8),(1.14,2.8)]+[(1.14*math.cos(t),2.8+4.3*(1-abs(math.cos(t)))**.45) for t in [math.pi*j/24 for j in range(25)]]
vs=[(11.4+.7071*x+.9,8.2-.7071*x+.9,z) for x,z in outline];mesh('sky beyond pointed opening',vs,[tuple(range(len(vs)))],sky,'window')
# Suspension joins the real generated lantern loop; opaque panels remain a stated limit.
for x,y,z in [(3.3,10.7,2.35),(-6.7,-2.5,2.6),(6.2,.5,2.7)]:
 cylinder_between('lantern suspension',(x,y,z+.63),(x,y,z+1.1),.016,iron,'fixtures')
# Small diagnostic scale ruler, not a player model; exclude from runtime exports.
scale_mat=mat('scale marker ivory',(.7,.7,.65))
cylinder_between('1.8m human-height ruler',(-4,-4,0),(-4,-4,1.8),.018,scale_mat,'diagnostics',8)
for z in [0,.9,1.8]:cylinder_between('height ruler tick',(-4.1,-4,z),(-3.9,-4,z),.012,scale_mat,'diagnostics',8)
bpy.ops.object.text_add(location=(-3.85,-4,1.85));ob=bpy.context.object;ob.data.body='1.8 m';ob.data.size=.13;ob.rotation_euler.x=math.pi/2;ob.data.materials.append(scale_mat);groups.setdefault('diagnostics',[]).append(ob)
# Five restrained per-stone values; retained explicitly in export metadata.
cut_variants=[]
for index,tint in enumerate([(.87,.88,.89),(1,.96,.90),(.94,.91,.86),(1.04,1.02,.97),(.81,.82,.81)]):
 m=cutstone.copy();m.name='cut stone value '+str(index);nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');tex=next(n for n in nt.nodes if n.type=='TEX_IMAGE');mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*tint,1);nt.links.new(tex.outputs['Color'],mul.inputs[1]);nt.links.new(mul.outputs[0],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.82+index*.025;m['hearth_a2_color_multiplier']=list(tint);cut_variants.append(m)
# Each modeled stone uses joint-free rock; only continuous wall/web infill uses ashlar.
for ob in groups.get('masonry',[]):
 if not ob.name.startswith(('fitted arch spandrel core','forge dark rear masonry','forge thick return')):ob.data.materials[0]=rng.choice(cut_variants)
for ob in groups.get('floor',[]):
 if ob.name.startswith('individual level worn flagstone'):ob.data.materials[0]=rng.choice(floor_mats)
bpy.context.view_layer.update()
# Flush UVs in metres; no reference-image projection.
for obs in groups.values():
 for ob in obs:
  if ob.type!='MESH':continue
  uv=ob.data.uv_layers.new(name='physical metre mapping')
  for poly in ob.data.polygons:
   n=poly.normal;axes=(0,1) if abs(n.z)>.6 else (0,2) if abs(n.y)>.6 else (1,2)
   for li in poly.loop_indices:
    p=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/4,p[axes[1]]/4)
if not mode.startswith('architecture'):
 sys.path.insert(0,str(Path(__file__).parent));from asset_loader import load_assets
 load_assets(R,E,json.loads((Path(__file__).parent/'assets.json').read_text()),groups)
from enclosure import close_window_bay
groups.setdefault('masonry',[]).extend(close_window_bay(stones[0]))
# Explicitly no old bottle furnace or generic hero substitute in this architecture proof.
(E/'architecture-plan.json').write_text(json.dumps({'units':'m','clear_floor':[16,18],'hero_assets_pending':True,'forge':{'centre':[-4,12.8,0],'target_bounds':[7,5,7.2]},'window':[11.05,6.2,4.6],'group_objects':{k:len(v) for k,v in groups.items()}},indent=2))
def light(n,p,target,power,size,color):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.size=size;d.color=color;ob=bpy.data.objects.new(n,d);S.collection.objects.link(ob);ob.location=p;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
light('hearth work light',(-4,10,3),(-4,13,3),420,3,(1,.62,.36));light('window daylight',(11.0,7.8,5.7),(-2,0,0),1800,3,(.63,.78,1));light('bellows work lamp',(3.3,10.7,2.1),(3.3,12,1.3),180,1.3,(1,.65,.3))
for xx in [-5.45,-2.95]:
 d=bpy.data.lights.new('contained furnace mouth heat','POINT');d.energy=100;d.color=(1,.23,.035);d.shadow_soft_size=.45;ob=bpy.data.objects.new(d.name,d);S.collection.objects.link(ob);ob.location=(xx,11.7,1.3)
light('near anvil task light',(-6.7,-2.5,2.86),(-5.8,-2.5,.9),170,1,(1,.68,.38))
light('stock workbay task light',(6.2,.5,3.0),(7.2,.5,1.1),180,1.2,(1,.69,.42))
light('quiet entry fill',(-5,-9,3),(0,9,3),450,6,(.8,.83,1))
bpy.ops.object.camera_add(location=(-5.8,-9.8,2.8));S.camera=bpy.context.object;S.camera.rotation_euler=(Vector((-.3,8.5,2.2))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.sensor_fit='HORIZONTAL';S.camera.data.angle=math.radians(75)
S.render.resolution_x=1536;S.render.resolution_y=630;S.render.resolution_percentage=100
from bpy_extras.object_utils import world_to_camera_view
def projection_report(label):
 bpy.context.view_layer.update();out={}
 for key,obs in groups.items():
  if not key.startswith('generated_'):continue
  pp=[world_to_camera_view(S,S.camera,o.matrix_world@Vector(c)) for o in obs for c in o.bound_box]
  out[key]={'projected_aabb_uv':[[min(p[i] for p in pp) for i in range(2)],[max(p[i] for p in pp) for i in range(2)]],'all_corners_in_front':all(p.z>0 for p in pp)}
 (E/(mode+'-'+label+'-projection.json')).write_text(json.dumps(out,indent=2))
projection_report('entry')
for group,obs in groups.items():
 for ob in obs:ob['hearth_a2_group']=group
(E/(mode+'-groups.json')).write_text(json.dumps({k:[o.name for o in v] for k,v in groups.items()},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(D/(mode+'.blend')));S.render.filepath=str(E/(mode+'-entry.png'));bpy.ops.render.render(write_still=True)

S.camera.location=(-5.5,-8.5,3.0);S.camera.rotation_euler=(Vector((0,4.5,.3))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.angle=math.radians(75);S.render.resolution_x=1280;S.render.resolution_y=720;S.render.filepath=str(E/(mode+'-gameplay.png'));projection_report('gameplay');bpy.ops.render.render(write_still=True)

# Reverse chamber proof from the rear, with the same saved geometry/materials.
S.camera.location=(3,10,3.2);S.camera.rotation_euler=(Vector((0,-4,2.2))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(E/(mode+'-reverse.png'));bpy.ops.render.render(write_still=True)
