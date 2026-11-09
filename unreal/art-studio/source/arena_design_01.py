"""Court of the Last Witness: original architectural concept, not Unreal integration."""
import bpy,math,json,sys,hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[3];D=R/'unreal/art-studio/arena-design-01';E=R/'artifacts/art/arena-design-01';D.mkdir(exist_ok=True);E.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:];A=int(args[0]) if args else 1;O=E/f'candidate-{A:02}';O.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3;s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=800;s.render.resolution_percentage=100;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.13,.17,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.18
s.view_settings.view_transform='AgX'
def material(name,col,rough=.7,metal=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emit
 return m
stone=material('warm pale weathered limestone',(.24,.205,.155));dark=material('charcoal funerary basalt',(.042,.050,.062));floor=material('honed neutral combat stone',(.19,.18,.16),.5);bronze=material('aged bronze inlay',(.22,.105,.034),.38,.78);ivory=material('ivory sealed oculus',(.67,.61,.45),.5,0,.7);indigo=material('recessed indigo wool',(.018,.025,.065));blue=material('restricted witness blue',(.035,.27,.52),.4,0,3);black=material('burial niche darkness',(.008,.011,.014));label=material('plan annotation ivory',(.8,.69,.4),.8,0,1)
# restrained physical stone grain, never a substitute for construction geometry
for m in [stone,dark,floor]:
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=16;noise.inputs['Detail'].default_value=2;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.17;b.inputs['Distance'].default_value=.025;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])
roof=[];annotations=[];new_supports=[]
def mesh(n,v,f,ma):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);me.materials.append(ma);return o
def cube(n,loc,scale,ma,bevel=.05,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;o.rotation_euler.z=rot;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bevel:m=o.modifiers.new('cut stone arris','BEVEL');m.width=bevel;m.segments=2;o.modifiers.new('weighted stone normals','WEIGHTED_NORMAL')
 return o
def cyl(n,loc,r,depth,ma,N=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=N,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(ma);m=o.modifiers.new('soft stone arris','BEVEL');m.width=.035;m.segments=2;o.modifiers.new('weighted normals','WEIGHTED_NORMAL');return o
def path(n,pts,ma,r=.04,closed=False):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(n,cu);s.collection.objects.link(o);cu.materials.append(ma);return o
def circle(n,r,z,ma,thick=.025,center=(0,0)):
 return path(n,[(center[0]+r*math.cos(j*math.tau/128),center[1]+r*math.sin(j*math.tau/128),z) for j in range(128)],ma,thick,True)
def radial(a,r,t,z):return (r*math.cos(a)-t*math.sin(a),r*math.sin(a)+t*math.cos(a),z)
def arch(n,a,r,width,spring,rise,ma,thick=.16):
 # Actual wedge-shaped voussoir blocks; rectangular depth instead of pipe ribs.
 v=[];f=[];steps=28
 def point(u):return Vector((-width/2+width*u,spring+rise*(1-abs(2*u-1)**1.25)))
 for j in range(steps):
  u0=j/steps+.001;u1=(j+1)/steps-.001;p0=point(u0);p1=point(u1);d=(p1-p0).normalized();normal=Vector((-d.y,d.x))*thick
  section=[p0-normal,p1-normal,p1+normal,p0+normal];base=len(v)
  for depth in [-.18,.18]:
   for q in section:v.append(radial(a,r+depth,q.x,q.y))
  f.extend(tuple(base+k for k in face) for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 o=mesh(n+' masonry voussoirs',v,f,ma);be=o.modifiers.new('worn stone block edges','BEVEL');be.width=.018;be.segments=1;o.modifiers.new('weighted block normals','WEIGHTED_NORMAL')
 for t in [-width/2,width/2]:cube(n+' jamb',radial(a,r,t,(spring+.7)/2),(.36,thick*2,spring-.7),ma,.025,a)
def flat_ring(n,r,width,ma,center=(0,0)):
 v=[(center[0]+rr*math.cos(j*math.tau/128),center[1]+rr*math.sin(j*math.tau/128),.001) for rr in [r-width/2,r+width/2] for j in range(128)]
 return mesh(n,v,[(j,(j+1)%128,128+(j+1)%128,128+j) for j in range(128)],ma)
def flat_line(n,a,b,width,ma):
 d=Vector(b)-Vector(a);u=Vector((-d.y,d.x,0)).normalized()*width/2;return mesh(n,[Vector(a)+u,Vector(a)-u,Vector(b)-u,Vector(b)+u],[(0,1,2,3)],ma)
# Flat 28m disk, continuous no raised center ornament. Flush lines are visual study offsets<=3mm.
cyl('continuous level arena slab',(0,0,-.24),14,.48,floor,128)
for rr in [3.6,7.8,12.1,13.45]:flat_ring('flush bronze witness ring',rr,.024,bronze)
for j in range(24):
 a=j*math.tau/24;flat_line('radial stone joint',(3.62*math.cos(a),3.62*math.sin(a),.001),(13.42*math.cos(a),13.42*math.sin(a),.001),.016,dark)
# three low-contrast seals, flat within the central medallion
for j in range(3):
 a=j*math.tau/3;cx=1.5*math.cos(a);cy=1.5*math.sin(a);flat_ring('three witness floor seal',.63,.026,bronze,(cx,cy));flat_line('seal upright',(cx,cy-.42,.001),(cx,cy+.42,.001),.024,bronze)
# Existing visual boundary at R13.6: no new interior pillars or cover.
for i in range(32):
 a=i*math.tau/32
 # axis portals retain closed bronze gates at current wall line
 if i in [0,16]:
  cube('closed threshold gate at existing wall',radial(a,13.6,0,1.3),(.55,2.8,2.6),bronze,.03,a)
 else:
  cube('existing-line stone arena boundary',radial(a,13.6,0,1.3),(.55,2.8,2.6),dark,.05,a)
  cube('boundary capstone',radial(a,13.6,0,2.62),(.67,2.80,.16),stone,.04,a)
# Existing eight pillar envelopes retained visibly, not silently removed from proposal.
for i in range(8):
 a=i*math.tau/8;x,y,z=radial(a,13.6,0,2.7)
 cyl('EXISTING envelope memorial pier shaft',(x,y,2.65),.51,5.10,dark,8)
 cyl('EXISTING envelope memorial pier base',(x,y,.15),.55,.30,stone,8)
 cyl('EXISTING envelope memorial pier capital',(x,y,5.25),.55,.30,stone,8)
 cyl('memorial pier bronze inset band',(x,y,4.72),.515,.09,bronze,8)
 # Restrained shallow plaque faces inward and stays inside the original radius.
 cube('memorial pier inward tablet',radial(a,13.15,0,3.6),(.065,.30,.68),stone,.025,a)
# Larger apse arch gives the court a focal hierarchy beyond repeating bays.
arch('great judgment apse arch',0,17.0,7.6,7.0,5.0,stone,.30)
arch('great apse bronze inset',0,16.96,7.0,7.0,4.6,bronze,.06)
# Processional annulus architecture beyond the fighting wall; 16bay rhythm, supports>=16.5m.
for i in range(16):
 a=i*math.tau/16;r=16.8
  # wall backing and vertical masonry courses
 cube('enclosed outer wall bay',radial(a,18.0,0,5.5),(1.1,7.2,11),dark,.05,a)
 for z in [.4,3.0,6.0,9.0,10.6]:cube('masonry belt course',radial(a,17.37,0,z),(.22,6.9,.17),stone,.025,a)
 # paired shafts define arcades; centers are outside17m radial envelope including tangent
 for t in [-2.65,2.65]:
  x,y,z=radial(a,r,t,0);new_supports.append({'center_m':[x,y],'radius_m':.62})
  cyl('octagonal pier plinth',(x,y,.35),.62,.7,dark,8);cyl('clustered stone pier',(x,y,3.8),.34,6.3,stone,12)
  for delta in [-.24,.24]:
   xx,yy,zz=radial(a,r+delta,t,3.8);cyl('engaged slender shaft',(xx,yy,zz),.11,6.4,stone,12)
  cyl('pier capital',(x,y,7.02),.52,.26,stone,8)
 arch('pointed tribunal arcade',a,r,5.3,6.9,3.1,stone,.23)
 arch('bronze inner arch fillet',a,r-.04,4.93,6.88,2.9,bronze,.035)
 # burial niches: quiet sealed boxes, no clutter on floor
 if i not in [0,8]:
  for t in [-1.25,1.25]:
   cube('recessed burial opening',radial(a,17.39,t,4.1),(.08,1.55,2.5),black,.02,a)
   arch('burial niche lancet',a,17.27,1.55,4.7,1.0,stone,.07) if t==0 else None
   for zz in [3.05,5.2]:cube('niche slab lip',radial(a,17.22,t,zz),(.33,1.55,.13),stone,.02,a)
   cube('sealed name tablet',radial(a,17.20,t,3.8),(.12,1.08,.56),dark,.035,a)
  # inset hanging banner outside gameplay space
  vv=[radial(a,17.15,t,z) for z in [7.9,6.2] for t in [-.6,.6]];mesh('indigo recessed funerary banner',vv,[(0,1,3,2)],indigo)
 # rising vault ribs meet oculus at16m, not flat roof
 pts=[]
 for j in range(25):
  t=j/24;rr=16.8*(1-t)+4.1*t;z=9.9+6.0*math.sin(t*math.pi/2);pts.append(radial(a,rr,0,z))
 roof.append(path('radial ribbed vault',pts,stone,.16))
# Vault infill and sealed translucent-looking but opaque ivory oculus.
vv=[];N=96
for j in range(13):
 t=j/12;rr=17.9*(1-t)+4.05*t;z=10.5+5.65*math.sin(t*math.pi/2)
 for k in range(N):a=k*math.tau/N;vv.append((rr*math.cos(a),rr*math.sin(a),z))
roof.append(mesh('enclosed carved vault shell',vv,[(j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k) for j in range(12) for k in range(N)],dark))
roof.append(cyl('SEALED ivory oculus',(0,0,16.17),4.05,.18,ivory,96));roof.append(circle('oculus bronze structural ring',4.15,16.03,bronze,.16))
for i in range(12):
 a=i*math.tau/12;roof.append(path('oculus radial lead rib',[(0,0,16.04),(4*math.cos(a),4*math.sin(a),16.04)],bronze,.035))
# Empty judgment dais beyond wall on+X. No throne is inside the playable disk.
cube('high apse plinth behind barrier',(16.6,0,1.45),(3.0,6.0,2.9),dark,.06)
for step in range(3):cube('apse stair '+str(step),(15.7+step*.28,0,2.95+.10*step),(2.8-step*.4,5.6-step*.25,.20),stone,.04)
cube('judge seat',(17.1,2.2,3.70),(1.1,1.6,.35),dark,.06);cube('tall empty judgment back',(17.57,2.2,4.90),(.42,1.8,3.0),dark,.08)
for y in [-.94,.94]:cube('throne narrow pilaster',(17.55,y+2.2,5.15),(.50,.18,3.5),stone,.03)
path('throne pointed crown',[(17.29,1.16,6.55),(17.29,2.2,7.45),(17.29,3.24,6.55)],bronze,.065)
for y in [-.9,.9]:cube('empty throne arm',(16.98,y+2.2,4.05),(1.1,.22,.24),stone,.05)
cube('deep indigo apse funerary field',(17.39,0,6.6),(.04,7.4,6.0),indigo,.01)
for y in [-3.55,3.55]:cube('apse carved vertical bronze border',(17.31,y,6.6),(.07,.07,6.0),bronze,.01)
for z in [4.5,5.1,5.7]:
 for y in [-2.1,2.1]:cube('apse relief offering tablet',(17.29,y,z),(.13,.52,.22),stone,.025)
# Three small blue-lit empty skull reliquaries, not new character models or hazards.
for y,z in [(-2.5,4.2),(0,7.8),(2.5,4.2)]:
 x=16.7;cyl('witness reliquary base',(x,y,z-.35),.38,.4,dark,8);cyl('witness blue chamber',(x,y,z),.20,.42,blue,16)
 for k in range(6):
  a=k*math.tau/6;path('reliquary bronze cage',[(x+.29*math.cos(a),y+.29*math.sin(a),z-.25),(x+.29*math.cos(a),y+.29*math.sin(a),z+.35)],bronze,.035)
 cyl('reliquary lid',(x,y,z+.37),.34,.08,bronze,8)
 bpy.ops.object.light_add(type='POINT',location=(x-.35,y,z));o=bpy.context.object;o.data.energy=70;o.data.color=(.17,.45,1);o.data.shadow_soft_size=.65
# Lighting: large neutral overhead field, warm perimeter; restrained blue accents only.
def area(n,loc,target,power,size,col):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=n;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=col;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('oculus soft downlight',(0,0,15.7),(0,0,0),5200,7,(1,.88,.69));area('entrance bounce',(-12,0,7),(4,0,3),1300,6,(.70,.78,1));area('apse reveal',(12,0,8),(17,0,3),2200,5,(1,.73,.45))
for i in range(8):
 a=i*math.tau/8;area('soft arcade pool',radial(a,16.0,0,8),radial(a,17.3,0,4),330,3,(1,.76,.5))
heightmarkers=[]
for name,x,height in [('PLAYER HEIGHT ONLY',-4.5,1.8),('BOSS HEIGHT ONLY',3,2.43)]:
 heightmarkers.append(path(name,[(x,0,0),(x,0,height)],ivory,.035));heightmarkers.append(path(name+' shoulders',[(x,-.22,height-.3),(x,.22,height-.3)],ivory,.028));heightmarkers.append(circle(name+' base',.25,.01,bronze,.02,(x,0)))
for ob in heightmarkers:ob.hide_render=True
# Orthographic plan annotations are actual scene objects, visible only in plan render.
def text(n,body,loc,size=.48):
 cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';o=bpy.data.objects.new(n,cu);s.collection.objects.link(o);o.location=loc;cu.materials.append(label);annotations.append(o)
annotations.append(circle('ANNOTATION primary tactical band',12.0,.055,label,.018));
annotations.append(circle('ANNOTATION proposed clear disk',12.8,.05,label,.045));text('plan clearlabel','PROPOSED CLEAR FLOOR  R12.8m',(0,-5,.06),.58);text('plan throne','EMPTY JUDGE / +X',(17,5,.07),.45);text('plan entrance','ENTRY / -X',(-15,-4,.07),.45);text('plan noobstacles','R12 TACTICAL / R12.8 CLEAR GEOMETRY',(0,-6,.06),.44)
for i in range(32):
 a=i*math.tau/32;pts=[radial(a,13.6+dr,dt,.08) for dr,dt in [(-.275,-1.4),(-.275,1.4),(.275,1.4),(.275,-1.4)]];annotations.append(path('ANNOTATION exact existing wall collider',pts,label,.025,True))
for i in range(8):
 a=i*math.tau/8;annotations.append(circle('ANNOTATION exact existing pillar collider',.55,.09,label,.035,(13.6*math.cos(a),13.6*math.sin(a))))
for name,x,y in [('PLAYER',-4.5,0),('WARDEN',3,0)]:
 annotations.append(circle('spawn reference '+name,.35,.05,label,.04,(x,y)));text('spawn text '+name,name,(x,y+.65,.06),.4)
text('plan roofnote','ROOF HIDDEN FOR PLAN | METRES | VISUAL DRAFT',(0,-20,.1),.50)
for o in annotations:o.hide_render=True;o.location.z+=12 # diagnostic overlay plane above walls; hidden in scene beauty
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.lens=24
scene=D/f'court-last-witness-{A:02}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
views=[('hero-entry',(-11.6,-1.2,1.75),(16.6,0,5),22),('gameplay-height',(-9,-3,2.35),(4,0,2),23.46),('side-architecture',(0,-11.5,3.3),(0,0,10.5),22),('near-boundary-inward',(11.8,2.2,1.75),(-4,0,2.5),24),('annotated-plan',(0,0,45),(0,0,0),45)]
for name,pos,target,lens in views:
 plan=name=='annotated-plan';s.render.resolution_y=1280 if plan else 800;cam.data.type='ORTHO' if plan else 'PERSP';cam.data.ortho_scale=44;cam.data.lens=lens;cam.data.sensor_fit='HORIZONTAL'
 if name=='gameplay-height':cam.data.angle=math.radians(75)
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 for ob in heightmarkers:ob.hide_render=name not in ['gameplay-height','near-boundary-inward']
 for o in roof:o.hide_render=plan
 for o in annotations:o.hide_render=not plan
 s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
geometry={'units':'metres; +X apse, -X entry, floorZ0','status':'original Blender concept only, NOT gameplay/collision/FPS tested','primary_tactical_guide_radius_m':12.0,'proposed_clear_disk_radius_m':12.8,'floor_radius_m':14,'existing_wall':{'count':32,'center_radius_m':13.6,'dimensions_radial_tangent_height_m':[.55,2.8,2.6],'inner_face_m':13.325},'existing_pillar':{'count':8,'center_radius_m':13.6,'radius_m':.55,'inner_extent_m':13.05},'nominal_inner_boundary_band_m':[12.8,13.05],'camera_boom_reference_m':[5,6.2],'camera_clearance':'not certified; existing collision probes remain necessary; band is NOT a full unobstructed boom','new_supports':new_supports,'min_new_support_inner_radius_m':min(math.hypot(*p['center_m'])-p['radius_m'] for p in new_supports),'spawn_references_m':{'player':[-4.5,0,.95],'boss':[3,0,1.28]},'oculus':'sealed opaque ivory geometry, diameter8.1m atZ16.17m; deliberate larger disk than early3.5mbrief','floor_inlay':'coplanar flat mesh inlays atZ0.001m; no thickness/raised curve geometry; runtime transfer untested','height_proxies':'simple1.8mplayer/2.43mboss rulers, NOT actual characters or exact skeletal bounds','empty_throne_center_m':[17.1,2.2,3.70],'throne_offset_reason':'tangential+2.2m avoids original+X pillar occlusion; collider unchanged','new_support_radius_scope':'full.62m plinth','throne_and_blue_reliquaries':'outside existing barrier; three passive empty chambers, not skull character assets'}
(O/'geometry.json').write_text(json.dumps(geometry,indent=2));bpy.ops.wm.open_mainfile(filepath=str(scene));(O/'readback.json').write_text(json.dumps({'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'objects':len(bpy.context.scene.objects),'meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'cameras':views,'no_runtime_changes':True},indent=2))
