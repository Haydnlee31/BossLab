"""The Last Casting: standalone measured studio architecture, no game edits."""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[4]; E=R/'artifacts/art/bellbreaker-arena-2026-11-16'; D=R/'unreal/art-studio/bellbreaker-arena-2026-11-16'
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'blockout'
O=E/mode; O.mkdir(parents=True,exist_ok=True);D.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
S=bpy.context.scene;S.unit_settings.system='METRIC';S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True;S.cycles.max_bounces=5
S.render.resolution_x=1200;S.render.resolution_y=800;S.render.resolution_percentage=100
S.world.color=(.19,.22,.25)
assets=[]
def mat(n,c,rough=.75,metal=0,grain=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if grain:
  no=m.node_tree.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=grain;no.inputs['Detail'].default_value=3
  b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=.025;m.node_tree.links.new(no.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 return m
stone=mat('ash limestone dressed blocks',(.18,.165,.14),grain=5);dark=mat('soot recessed masonry',(.075,.066,.055),grain=8);floor=mat('worn warm limestone floor',(.25,.225,.18),grain=14);iron=mat('oxidized gantry iron',(.07,.055,.04),.6,.65,20);bronze=mat('old casting bronze',(.24,.13,.045),.48,.78,25);glass=mat('overcast clerestory glass',(.37,.43,.45),.4);line=mat('flush casting survey inlay',(.12,.09,.045),.65,.4);proxy=mat('scale marker ivory',(.55,.51,.42))
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.data.materials.append(m);return o
def box(n,loc,scale,m,bev=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if bev:md=o.modifiers.new('small worn arris','BEVEL');md.width=bev;md.segments=2;o.modifiers.new('weighted corner normals','WEIGHTED_NORMAL')
 return o
def tube(n,pts,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=1;p=c.splines.new('POLY');p.points.add(len(pts)-1)
 for q,co in zip(p.points,pts):q.co=(*co,1)
 o=bpy.data.objects.new(n,c);S.collection.objects.link(o);o.data.materials.append(m);return o
def rr(w,h,r,z):
 return [(cx+r*math.cos(a),cy+r*math.sin(a),z) for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)] for a in [math.radians(start+i*90/12) for i in range(13)]]
def flatband(n,pts,width,m):
 # Narrow flat horizontal strips, no vertical hazard relief.
 v=[];f=[]
 for i,p in enumerate(pts):
  a=Vector(pts[(i-1)%len(pts)]);b=Vector(pts[(i+1)%len(pts)]);t=(b-a).normalized();q=Vector((-t.y,t.x,0))*width/2;v.extend([Vector(p)+q,Vector(p)-q])
 for i in range(len(pts)):j=(i+1)%len(pts);f.append((2*i,2*j,2*j+1,2*i+1))
 return mesh(n,v,f,m)
box('level floor substrate',(0,0,-.2),(46,58,.4),floor)
box('rear apse support floor substrate',(0,30,-.2),(10.5,2.1,.4),floor)
for side in [-1,1]:
 for y in [-10,10]:box('furnace pocket support floor substrate',(side*23.75,y,-.2),(2.5,6.5,.4),floor)
flatband('fight boundary flush bronze',rr(28,36,4,.002),.045,bronze);flatband('buffer outer flush guide',rr(40,48,10,.002),.025,line)
# Quiet large paving joints; no individual raised floor tiles.
for x in range(-21,22,3):box('flush longitudinal paving joint',(x,0,.001),( .018,58,.001),line)
for y in range(-27,28,3):box('flush transverse paving joint',(0,y,.001),(46,.018,.001),line)
# Continuous exterior walls with inset bay construction.
for side in [-1,1]:
 box('upper continuous nave wall',(side*23,0,10.9),(.6,58,9),dark)
 for ya,yb in [(-29,-13),(-7,7),(13,29)]:box('lower wall between furnace recesses',(side*23,(ya+yb)/2,3.2),(.6,yb-ya,6.4),dark)
 for yy in [-10,10]:
  box('furnace pocket rear wall',(side*24.45,yy,3.2),(.4,6,6.4),dark)
  for edge in [-3,3]:box('furnace pocket return',(side*23.7,yy+edge,3.2),(1.5,.4,6.4),dark)
  box('furnace pocket lintel lid',(side*23.7,yy,6.4),(1.5,6,.3),stone)
 for y in [-24,-16,-8,0,8,16,24]:
  box('masonry pilaster',(side*22,y,6),(.65,1.0,12),stone,.06)
  box('pilaster footing',(side*22,y,.55),(1.05,1.4,1.1),dark,.04)
  box('springer bearing',(side*22,y,11.6),(1.05,1.5,.55),stone,.04)
 for y in [-20,-12,-4,4,12,20]:
  box('recessed foundry bay lintel',(side*22.55,y,6.1),(.5,6.9,.5),stone,.025)
  box('clerestory glazing',(side*22.63,y,10.4),(.05,5.4,3.2),glass)
  for yy in [-1.8,0,1.8]:box('clerestory iron mullion',(side*22.53,y+yy,10.4),(.13,.08,3.4),iron)
  # Regular masonry courses authored as broad blocks, outside buffer.
  for row in range(5):
   for j in range(4):
    yy=y-2.7+j*1.8+(row%2)*.12
    if min(abs(yy-10),abs(yy+10))>3.9:box('coursed bay ashlar',(side*22.68,yy,.5+row*1.02),(.35,1.75,.96),stone,.015)
# End walls, doorway and tall bell niche.
for y in [-29,29]:
 if y<0:box('entry end gable wall',(0,y,7.6),(46,.6,15.2),dark)
 else:
  for x in [-14,14]:box('rear gable flanking bell recess',(x,y,7.6),(18,.6,15.2),dark)
  box('rear bell recess wall',(0,30.5,7.6),(10,.6,15.2),dark)
  for x in [-5,5]:box('rear bell recess return',(x,29.75,7.6),(.5,1.5,15.2),dark)
 for x in [-15,-9,9,15]:box('gable vertical buttress',(x,y-.35 if y>0 else y+.35,6.5),(1.0,.8,13),stone,.05)
box('entry sealed industrial door',(0,-28.55,3.4),(7,.25,6.8),iron,.05)
for x in [-3.8,3.8]:box('entry door jamb',(x,-28.35,3.7),(.6,.65,7.4),stone,.04)
box('entry lintel',(0,-28.35,7.5),(8.2,.7,.6),stone,.04)
# True transverse arch ribs with a broad vaulted roof, all overhead.
for y in [-24,-16,-8,0,8,16,24]:
 pts=[(-22+44*i/32,y,11.8+5.2*math.sin(math.pi*i/32)**.72) for i in range(33)]
 for i in range(32):
  a,b=Vector(pts[i]),Vector(pts[i+1]);mid=(a+b)/2;o=box('vault stone rib segment',mid,((b-a).length+.035,.6,.5),stone,.018);o.rotation_euler.y=-math.atan2(b.z-a.z,b.x-a.x)
# roof strips following same arch, outside ceiling8m minimum
for i in range(32):
 x0=-23+46*i/32;x1=-23+46*(i+1)/32;z0=12+5.4*math.sin(math.pi*i/32)**.72;z1=12+5.4*math.sin(math.pi*(i+1)/32)**.72
 mesh('sooted barrel vault panel',[(x0,-29,z0),(x1,-29,z1),(x1,29,z1),(x0,29,z0)],[(0,1,2,3)],dark)
# Broad pointed foundry arch: actual wedge blocks, not decorative tubes.
def pointed_arch(name,cx,cy,width,spring,rise,depth,axis='Y'):
 pts=[(-width/2+width*i/24,spring+rise*(1-abs(-1+2*i/24))**.65) for i in range(25)]
 for i in range(24):
  x0,z0=pts[i];x1,z1=pts[i+1];d=Vector((x1-x0,z1-z0));n=Vector((-d.y,d.x)).normalized()*.34
  verts=[]
  for dep in [-depth/2,depth/2]:
   for xx,zz in [(x0,z0),(x1,z1),(x1+n.x,z1+n.y),(x0+n.x,z0+n.y)]:verts.append((cx+xx,cy+dep,zz) if axis=='Y' else (cx+dep,cy+xx,zz))
  mesh(name+' carved voussoir',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone)
pointed_arch('great bell casting niche',0,28.0,12,8,6.0,.7)
for x in [-22.5,22.5]:
 for y in [-10,10]:
  pointed_arch('cold furnace masonry surround',x,y,5.5,3.8,2.4,.6,'X')
  for yy in [y-2.85,y+2.85]:
   box('furnace jamb',(x,yy,1.9),(.6,.6,3.8),dark,.04)
   box('furnace arch bearing springer',(x,yy,3.8),(.85,1.05,.35),stone,.025)
# Sparse old workshop standards outside buffer, no movement or gameplay meaning.
cloth=mat('faded oxblood workshop cloth',(.10,.035,.025),.93,0,24)
for x in [-12,12]:box('hanging workshop standard',(x,28.40,8.3),(1.65,.035,4.4),cloth)
# Historic gantry rails and arrested lifting beam, safely overhead.
for x in [-8,8]:box('longitudinal crane rail',(x,0,12.4),(.35,54,.55),iron,.025)
box('dead crane crossbeam',(0,13,12.0),(17,.6,.8),iron,.035)
for x in [-2.4,2.4]:
 tube('arrested hoist chain',[(x,13,11.7),(x,13,8.8)],.065,iron)
 for z in [9+i*.23 for i in range(12)]:
  pts=[(x+.095*math.cos(a),13+.035*math.sin(a),z+.14*math.sin(a)) for a in [i*math.tau/12 for i in range(13)]];tube('chain link',pts,.022,iron)
# Hero imported meshes use copied/decimated datablocks; placement dimensions explicit.
def import_prop(key,path,target,loc):
 if not path.exists():return False
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));imported=set(bpy.data.objects)-before;objs=[o for o in imported if o.type=='MESH']
 if not objs:return False
 bpy.context.view_layer.update()
 # Material coordinates retained; world coordinates baked into DERIVED copies only.
 rotation=Matrix.Rotation((-math.pi/2 if loc[0]>0 else math.pi/2) if 'furnace' in key else 0,4,'Z')
 world={o:[rotation@o.matrix_world@v.co for v in o.data.vertices] for o in objs}
 coords=[v for vs in world.values() for v in vs];lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)));hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)));dims=hi-lo
 bounds=Vector((3.0,5.0,5.5)) if 'furnace' in key else Vector((5.6,5.6,5.5))
 scale=min(bounds[i]/max(.000001,dims[i]) for i in range(3));center=(lo+hi)/2
 total=0
 for o in objs:o.data.calc_loop_triangles();total+=len(o.data.loop_triangles)
 aftertris=0
 for o in objs:
  o.data=o.data.copy();o.parent=None
  for v,co in zip(o.data.vertices,world[o]):v.co=(co-Vector((center.x,center.y,lo.z)))*scale+Vector(loc)
  o.matrix_world.identity();o.name=key+' imported '+o.name
  md=o.modifiers.new('derived studio budget decimation','DECIMATE');md.ratio=min(1,50000/max(1,total))
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=md.name);o.data.calc_loop_triangles();aftertris+=len(o.data.loop_triangles)
 for o in imported:
  if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
 assets.append({'key':key,'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_triangles':total,'derived_triangles':aftertris,'placement':loc,'source_dimensions_m':list(dims),'orientation_radians_z':(-math.pi/2 if loc[0]>0 else math.pi/2) if 'furnace' in key else 0,'uniform_fit_scale':scale,'fitted_dimensions_m':list(dims*scale),'max_bounds_m':list(bounds),'materials':'imported glTF materials, not calibrated PBR'})
 return True
config=Path(__file__).with_name('assets.json');cfg=json.loads(config.read_text()) if config.exists() else {}
if mode not in ['blockout','bell-probe']:
 for key in ['bell','furnace']:
  assert cfg.get(key) and (R/cfg[key]).is_file(), 'Final assembly requires actual HF '+key+' mesh; reserved boxes are not final assets'
bell=import_prop('HF broken bell',R/cfg['bell'],5.5,(0,27,0)) if cfg.get('bell') else False
if not bell:
 # Explicit reserved envelope, not a claimed HF mesh.
 box('BELL ASSET RESERVED envelope',(0,27,2.7),(5.6,4,5.4),bronze,.12)
for x in [-22.5,22.5]:
 for y in [-10,10]:
  if cfg.get('furnace'):import_prop('HF cold furnace',R/cfg['furnace'],5.5,(x,y,0))
  else:box('FURNACE ASSET RESERVED envelope',(x,y,2.75),(3,4,5.5),iron,.08)
# Bell backplate framing, casting channels stay outside floor.
box('bell apse bronze backing',(0,30.25,6),(8,.15,11.5),iron)
for x in [-6.1,6.1]:
 box('great bell arch loadbearing pier',(x,28.0,4.0),(.95,.9,8.0),stone,.04)
 box('great bell arch seated springer',(x,28.0,8.0),(1.2,1.05,.36),stone,.025)
 box('great bell arch pier footing',(x,28.0,.4),(1.35,1.15,.8),dark,.04)
def text(n,body,loc,size,rot=(0,0,0)):
 c=bpy.data.curves.new(n,'FONT');c.body=body;c.size=size;c.align_x='CENTER';o=bpy.data.objects.new(n,c);S.collection.objects.link(o);o.location=loc;o.rotation_euler=rot;o.data.materials.append(proxy);return o
markers=[]
for n,h,loc in [('PLAYER 1.8m',1.8,(-1,-5)),('BOSS 2.7m',2.7,(1,5))]:
 x,y=loc;markers.append(box('HEIGHT PROXY '+n,(x,y,h/2),(.18,.18,h),proxy,.02));markers.append(box('proxy shoulder ruler',(x,y,h*.78),(.75,.12,.10),proxy));markers.append(text('scale label',n,(x,y-.3,.015),.45))
annotations=[]
for label,loc in [('THE LAST CASTING / +Y BOSS',(0,30,18)),('FIGHT FLOOR 28 x 36 m / r4 corners',(0,-2,18)),('6 m EMPTY CAMERA BUFFER / NOT BOOM VALIDATION',(0,-24.7,18)),('HALL 46 x 58 m',(0,-30,18)),('ENTRY / -Y',(0,-18.5,18))]:
 o=text('PLAN '+label,label,loc,.65);o.hide_render=True;annotations.append(o)
def area(n,loc,power,size,color,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('overcast vault soft light',(0,0,14),6500,16,(.80,.87,1),(0,0,0));area('entry bounce',(0,-20,8),2600,12,(1,.84,.65),(0,8,4));area('bell grazing skylight',(0,25,12),3300,7,(1,.88,.70),(0,27,3))
for x in [-21,21]:area('clerestory diffuse',(x,0,11),3000,12,(.85,.90,1),(0,0,3))
# Reuse owner-approved local CC0 Poly Haven maps with explicit physical-scale UVs.
texture_sources=[]
def local_surface(material,stem,tile_m):
 folder=R/'artifacts/art/arena-dungeon-2026-11-09/textures';nt=material.node_tree;p=nt.nodes.get('Principled BSDF')
 for suffix in ['diff','arm']:
  path=folder/(stem+'_'+suffix+'_2k.jpg')
  if not path.exists():continue
  im=bpy.data.images.load(str(path),check_existing=True)
  if material==floor and suffix=='diff':
   import numpy as np
   original=im;pix=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pix);a=pix.reshape(-1,4);lum=a[:,:3]@np.array([.2126,.7152,.0722],dtype=np.float32);a[:,:3]=(.25*a[:,:3]+.75*lum[:,None])*.78
   im=bpy.data.images.new('derived desaturated ash paving albedo',width=original.size[0],height=original.size[1]);im.pixels.foreach_set(pix);im.pack()
  else:im.pack()
  node=nt.nodes.new('ShaderNodeTexImage');node.image=im
  if suffix=='diff':nt.links.new(node.outputs['Color'],p.inputs['Base Color'])
  else:
   im.colorspace_settings.name='Non-Color';sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(node.outputs['Color'],sep.inputs['Color']);nt.links.new(sep.outputs['Green'],p.inputs['Roughness'])
  texture_sources.append({'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'license':'CC0 Poly Haven; existing approved local dungeon asset','tile_m':tile_m,'use':suffix})
 for o in list(S.objects):
  if o.type!='MESH' or material.name not in [m.name for m in o.data.materials]:continue
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='Physical planar masonry')
  for poly in o.data.polygons:
   normal=o.matrix_world.to_3x3()@poly.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in poly.loop_indices:
    co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/tile_m,co[axes[1]]/tile_m)
local_surface(stone,'castle_wall_varriation',3.2)
local_surface(floor,'cobblestone_pavement',4.5)
# Crane bridge diagonals and axle drums explain the hoist support, all overhead.
for x in [-8,8]:
 for y in [12.4,13.6]:tube('gantry diagonal iron brace',[(x,y,11.6),(x*.6,y,13.3)],.10,iron)
for x in [-2.4,2.4]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.45,depth=.6,location=(x,13,11.7),rotation=(math.pi/2,0,0));bpy.context.object.name='hoist winding drum';bpy.context.object.data.materials.append(iron)
clay=mat('neutral untextured diagnostic clay',(.35,.35,.35),.8)
bpy.ops.object.camera_add();cam=bpy.context.object;S.camera=cam
views={'entry-hero':((0,-24,2.1),(0,18,5.4),28),'reverse':((0,23,3.0),(0,-20,5),28),'gameplay-height':((-1,-10,2.7),(1,5,1.8),24),'near-boundary':((12,14,2),(0,-4,2.4),24),'clay-architecture':((12,-15,5),(0,12,6),24),'furnace-detail':((14,5,2.6),(22.5,10,2.0),32),'prop-detail':((9,21,3.4),(0,27,3.0),35),'top-plan':((0,0,55),(0,0,0),45)}
def camera(k):
 p,t,l=views[k];cam.location=p;cam.rotation_euler=(Vector(t)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if k=='top-plan' else 'PERSP';cam.data.ortho_scale=64;cam.data.lens=l
 if k=='gameplay-height':cam.data.sensor_fit='HORIZONTAL';cam.data.angle=math.radians(75)
 bpy.context.view_layer.update()
for im in bpy.data.images:
 if im.type=='IMAGE' and im.size[0]>0 and not im.packed_file:im.pack()
camera('entry-hero');bpy.ops.wm.save_as_mainfile(filepath=str(D/(mode+'.blend')))
for k in (['entry-hero','top-plan'] if mode=='blockout' else ['prop-detail'] if mode=='bell-probe' else ['furnace-detail','entry-hero','reverse','gameplay-height','near-boundary','clay-architecture','prop-detail','top-plan']):
 camera(k);hidden=[]
 for o in annotations:o.hide_render=(k!='top-plan')
 S.view_layers[0].material_override=clay if k=='clay-architecture' else None
 if k=='top-plan':
  for o in S.objects:
   if any(s in o.name for s in ['vault','crane','hoist','chain link']):o.hide_render=True;hidden.append(o)
  S.render.resolution_x=1000;S.render.resolution_y=1200
 else:S.render.resolution_x=1600 if mode!='blockout' and k in ['entry-hero','prop-detail','furnace-detail'] else 1200;S.render.resolution_y=1000 if mode!='blockout' and k in ['entry-hero','prop-detail','furnace-detail'] else 800
 S.cycles.samples=32 if mode!='blockout' and k in ['entry-hero','prop-detail','furnace-detail'] else 16
 S.render.filepath=str(O/(k+'.png'));bpy.ops.render.render(write_still=True)
 for o in hidden:o.hide_render=False
camera('entry-hero');S.view_layers[0].material_override=None
for o in annotations:o.hide_render=True
S.render.resolution_x=1200;S.render.resolution_y=800
bpy.ops.wm.save_as_mainfile(filepath=str(D/(mode+'.blend')))
# Export geometry/materials only, not camera/light actors. Evaluated modifiers used.
if mode not in ['blockout','bell-probe']:
 bpy.ops.object.select_all(action='DESELECT')
 export_curve_copies=[]
 for original in list(S.objects):
  if original.type=='CURVE' and not original.hide_render:
   ob=original.copy();ob.data=original.data.copy();S.collection.objects.link(ob);ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob.select_set(False);export_curve_copies.append(ob)
 for o in S.objects:
  if o.type=='MESH' and not o.name.startswith(('HEIGHT PROXY','proxy shoulder')):o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(D/'last-casting.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
 for ob in export_curve_copies:bpy.data.objects.remove(ob,do_unlink=True)
counts=[];deps=bpy.context.evaluated_depsgraph_get()
for o in S.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();pts=[o.matrix_world@v.co for v in me.vertices];counts.append({'name':o.name,'triangles':len(me.loop_triangles),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]] if pts else [],'materials':[m.name for m in o.data.materials]});ev.to_mesh_clear()
# Conservative complete-object AABB separation from the entire buffer rectangle.
# Stronger than rounded-corner separation, but static and limited to below5m.
clearance=[]
for rec in counts:
 n=rec['name'];bounds=rec['bounds']
 if not bounds or any(k in n for k in ['floor substrate','flush','HEIGHT PROXY','proxy shoulder','scale label','PLAN ']):continue
 lo,hi=bounds
 if lo[2]>=5 or hi[2]<=0:continue
 gap=max(lo[0]-20,-20-hi[0],lo[1]-24,-24-hi[1])
 clearance.append({'object':n,'axis_separation_margin_to_rectangular_buffer_m':gap,'bounds':bounds,'outside':gap>=-1e-5})
(O/'clearance.json').write_text(json.dumps({'scope':'complete evaluated object AABB separation from40x48 rectangle below5m, conservative vsrounded corners; excludes floor/inlays/labelled rulers; no dynamic camera/collision claim','objects':clearance,'all_outside':all(x['outside'] for x in clearance)},indent=2))
report={'status':'actual standalone studio architecture; no runtime integration or camera validation','mode':mode,'fight_floor_m':[28,36],'corner_radius_m':4,'camera_buffer_m':6,'outer_buffer_m':[40,48],'hall_m':[46,58],'roof_m':[12,17.4],'axis':'+Y boss, -Y entrance','proxies':'height rulers only,1.8m and2.7m','assets':assets,'texture_sources':texture_sources,'objects':counts,'triangles':sum(o['triangles'] for o in counts),'materials':[m.name for m in bpy.data.materials],'views':views,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scene_sha256':hashlib.sha256((D/(mode+'.blend')).read_bytes()).hexdigest()}
(O/'manifest.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['objects','views','materials']},indent=2))
