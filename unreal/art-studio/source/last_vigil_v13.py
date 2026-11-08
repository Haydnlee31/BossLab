"""V13 geometry-first independent bust. No projection, physics, rig or game changes."""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];D=R/'unreal/art-studio/revision-v13-2026-11-07';E=R/'artifacts/art/last-vigil-v13';D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:];mode=args[0] if args else 'draft';A=4;C=16;S=bpy.context.scene
GUIDE=R/'artifacts/art/last-vigil-v12/design/shared-landmarks.json';g=json.loads(GUIDE.read_text())
def material(name,color):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.8;bs.inputs['Specular IOR Level'].default_value=.2;return m

def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat)
 for p in me.polygons:p.use_smooth=True
 return o

def apply(o,mod):
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
def thick(o,t=.003):
 m=o.modifiers.new('Actual hollow plate thickness','SOLIDIFY');m.thickness=t;m.offset=-1;apply(o,m)
def blend(a,b,t):return a+(b-a)*t

def torso(mat,under=False):
 rows=[(0,.148,-.100,.096),(.012,.145,-.100,.098),(.100,.160,-.118,.104),(.240,.211,-.139,.113),(.330,.204,-.122,.108),(.355,.170,-.095,.095),(.375,.102,-.102,.102)]
 vs=[];fs=[];N=96
 for j,(z,rx,fy,by) in enumerate(rows):
  for k in range(N):
   a=2*math.pi*k/N;st=math.sin(a);ct=math.cos(a);x=rx*st;y=(-abs(fy)*ct if ct>=0 else -by*ct);zz=z+(.035 if j==len(rows)-2 else .015 if j==len(rows)-1 else 0)*st*st
   if ct>=0:
    t=abs(st);fraction=(1-.18*t if t<=.58 else .8956*((1-t)/.42)**.68)
    # Actual broad swept front fields with a narrow sternum keel; no texture illusion.
    y=-abs(fy)*fraction-.009*max(0,1-t/.18)*math.sin(math.pi*min(1,z/.40))-.0048*math.exp(-((t-.58)/.035)**2)*math.sin(math.pi*min(1,z/.40))
   if under:x*=.94;y*=.88;zz-=.008 if j==len(rows)-1 else 0
   vs.append((x,y,zz))
 for j in range(len(rows)-1):
  for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 if under:fs.extend([tuple(reversed(range(N))),tuple((len(rows)-1)*N+k for k in range(N))])
 o=mesh('V13 | continuous connected underbody' if under else 'V13 | continuous hollow cuirass front and back',vs,fs,mat)
 if not under:thick(o)
 return o

def arm_r(z):
 t=max(0,min(1,(z-.17)/.14));return blend(.047,.056,t),blend(.063,.075,t)

def cap_profile(t):
 points=[(0,0,.380),(.15,.50,.375),(.35,.78,.360),(.60,.95,.330),(1,1,.300)]
 for a,b in zip(points,points[1:]):
  if t<=b[0]:u=(t-a[0])/(b[0]-a[0]);return blend(a[1],b[1],u),blend(a[2],b[2],u)
 return 1,.30

def reliquary(tor,plate):
 from mathutils.bvhtree import BVHTree
 bt=BVHTree.FromPolygons([v.co.copy() for v in tor.data.vertices],[tuple(p.vertices) for p in tor.data.polygons])
 def seated(x,z,offset):
  hit,n,index,d=bt.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
  assert hit is not None
  return (x,hit.y-offset,z)
 # A mounted closed pointed-arch frame, with a lower recessed plate and seven actual fasteners.
 outline=[(-.040,.072),(-.040,.230),(-.039,.246),(-.032,.263),(-.019,.283),(0,.305),(.019,.283),(.032,.263),(.039,.246),(.040,.230),(.040,.072)]
 outer=[]
 for a,b in zip(outline,outline[1:]+outline[:1]):
  for j in range(12):u=j/12;outer.append((blend(a[0],b[0],u),blend(a[1],b[1],u)))
 inner=[(x*.80,.188+(z-.188)*.95) for x,z in outer];N=len(outer)
 vs=[seated(x,z,.005) for x,z in outer]+[seated(x,z,.005) for x,z in inner];fs=[]
 for i in range(N):j=(i+1)%N;fs.append((i,j,N+j,N+i))
 frame=mesh('V13 | seated pointed arch reliquary frame',vs,fs,plate);thick(frame,.002)
 dark=material('V13 recessed reliquary steel',(.09,.10,.11));vs=[];fs=[];nz=65;nx=17
 # Densely sample the interior, not just outline: convex sternum cannot be covered by a broad planar fan.
 zmin=min(z for x,z in inner);zmax=max(z for x,z in inner)
 for j in range(nz):
  z=blend(zmin,zmax-.0002,j/(nz-1));cross=[]
  for a,b in zip(inner,inner[1:]+inner[:1]):
   if min(a[1],b[1])<=z<=max(a[1],b[1]) and abs(a[1]-b[1])>1e-9:cross.append(blend(a[0],b[0],(z-a[1])/(b[1]-a[1])))
  width=max(abs(x) for x in cross) if cross else .0002
  for i in range(nx):vs.append(seated(blend(-width,width,i/(nx-1)),z,.003))
 for j in range(nz-1):
  for i in range(nx-1):k=j*nx+i;fs.append((k,k+1,k+nx+1,k+nx))
 field=mesh('V13 | recessed mounted reliquary field',vs,fs,dark);thick(field,.0015)

 studs=[]
 for i,z in enumerate([.090,.115,.140,.165,.190,.215,.240]):
  loc=seated(0,z,.0042);bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=loc);ob=bpy.context.object;ob.name='V13 | reliquary seated peened stud '+str(i+1);ob.scale=(.0026,.0016,.0026);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(plate);studs.append({'object':ob.name,'centre':list(ob.location)})
 (E/f'attempt-{A:02d}-reliquary.json').write_text(json.dumps({'method':'Real closed2mm arch frame over1.5mm mounted dark field, both sampled onto actual front plate; field3mm below frame face, not a painted engraving or a cut recess in main shell.','stud_count':7,'studs':studs,'outer_width_m':.080,'outer_height_m':.233},indent=2)+'\n')

def neck_layers(plate):
 base=bpy.data.objects['V13 | hollow seated gorget'];base.hide_render=True
 controls=[(.375,.105,.105),(.395,.102,.102),(.435,.079,.084),(.455,.073,.078)]
 def radius(z):
  for a,b in zip(controls,controls[1:]):
   if z<=b[0]:t=(z-a[0])/(b[0]-a[0]);return blend(a[1],b[1],t),blend(a[2],b[2],t)
  return .073,.078
 for n,(bottom,top) in enumerate([(.375,.405),(.399,.432),(.426,.455)]):
  vs=[];fs=[];N=96;M=12
  for row in range(M+1):
   t=row/M;z=blend(top,bottom,t);rx,ry=radius(z);step=max(0,min(1,(t-.20)/.15));off=.0015+.0035*step
   for k in range(N):
    a=2*math.pi*k/N;zz=z+.010*(1-(z-.375)/.080)*math.sin(a)**2-.006*max(0,math.cos(a))**2
    vs.append(((rx+off)*math.sin(a),-(ry+off)*math.cos(a),zz))
  for row in range(M):
   for k in range(N):a=row*N+k;b=row*N+(k+1)%N;fs.append((a,b,b+N,a+N))
  ob=mesh('V13 | fitted layered gorget '+str(n),vs,fs,plate);thick(ob,.002)
  for f in ob.data.polygons:
   if f.index>=2*N*M:f.use_smooth=False

def build():
 global S
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True;S.render.resolution_x=900;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
 plate=material('V13 neutral armor clay',(.24,.26,.28));lining=material('V13 dark neutral underbody clay',(.07,.08,.09));tor=torso(plate);body=torso(lining,True)
 # Actual side arm sockets; no intact ellipse pushed through the arm roots.
 for sign in [-1,1]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(sign*.255,0,.305));cut=bpy.context.object;cut.scale=(.090,.098,.096);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  m=tor.modifiers.new('Open anatomical arm socket '+str(sign),'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;apply(tor,m);bpy.data.objects.remove(cut,do_unlink=True)
  vs=[];fs=[];N=64
  for z,rx,ry in [(.17,.047,.063),(.24,.0515,.069),(.31,.056,.075),(.35,.045,.060),(.365,.012,.016)]:
   for k in range(N):a=2*math.pi*k/N;vs.append((sign*(.245+rx*math.cos(a)),ry*math.sin(a),z))
  for j in range(4):
   for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
  fs.extend([tuple(reversed(range(N))),tuple(4*N+k for k in range(N))]);arm=mesh('temporary arm union',vs,fs,lining)
  m=body.modifiers.new('Connected arm root union '+str(sign),'BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=arm;apply(body,m);bpy.data.objects.remove(arm,do_unlink=True)
 # Hollow seated gorget with the same variable-height neckline flange.
 vs=[];fs=[];N=96
 for j,(z,rx,ry) in enumerate([(.375,.105,.105),(.395,.102,.102),(.435,.079,.084),(.455,.073,.078)]):
  for k in range(N):
   a=2*math.pi*k/N;vs.append((rx*math.sin(a),-ry*math.cos(a),z+(.015*(1-j/3))*math.sin(a)**2))
 for j in range(3):
  for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 gorget=mesh('V13 | hollow seated gorget',vs,fs,plate);thick(gorget)
 for sign in [-1,1]:
  # Open medial cup, wrapping front/lateral/rear over the exact shared arm envelope.
  N=64;M=18;vs=[(sign*.245,0,.38)];fs=[]
  for row in range(1,M+1):
   phi=(math.pi/2)*row/M
   for k in range(N+1):
    t=phi/(math.pi/2);rad,height=cap_profile(t);span=math.pi-(math.pi-1.92)*t*t;a=-span+2*span*k/N;vs.append((sign*(.245+.070*rad*math.copysign(abs(math.cos(a))**.55,math.cos(a))),.089*rad*math.copysign(abs(math.sin(a))**.55,math.sin(a)),height-.009*abs(math.sin(a))**4*t))
  for k in range(N):fs.append((0,1+k,2+k))
  for row in range(M-1):
   for k in range(N):i=1+row*(N+1)+k;fs.append((i,i+1,i+N+2,i+N+1))
  cup=mesh('V13 | wrapping hollow shoulder cup '+str(sign),vs,fs,plate);thick(cup)
  for j,bottom in enumerate([.270,.240,.210]):
   top=bottom+.042;vs=[];fs=[];M=8
   for row in range(M+1):
    z=blend(top,bottom,row/M);rx,ry=arm_r(z);t=row/M;step=max(0,min(1,(t-.32)/.10));step=step*step*(3-2*step);offset=.006+.005*step;rx+=offset;ry+=offset
    for k in range(N+1):a=-1.92+3.84*k/N;vs.append((sign*(.245+rx*math.cos(a)),ry*math.sin(a),z-.014*(row/M)**2*max(0,1-abs(a+1.0)/.75)-.007*(row/M)**2*max(0,1-abs(a-1.0)/.75)))
   for row in range(M):
    for k in range(N):i=row*(N+1)+k;fs.append((i,i+1,i+N+2,i+N+1))
   lame=mesh('V13 | shared-envelope overlapping lame '+str(sign)+' '+str(j),vs,fs,plate);thick(lame,.002)
   for poly in lame.data.polygons:
    if poly.index>=2*N*M:poly.use_smooth=False
 # Restrained actual rear closure line, same continuous shell beneath it.
 curve=bpy.data.curves.new('rear closure','CURVE');curve.dimensions='3D';curve.bevel_depth=.001;curve.bevel_resolution=2;sp=curve.splines.new('POLY');sp.points.add(4)
 for p,co in zip(sp.points,[(0,.102,.02),(0,.112,.10),(0,.117,.24),(0,.112,.33),(0,.097,.35)]):p.co=(*co,1)
 o=bpy.data.objects.new('V13 | centre rear closure seam',curve);bpy.context.collection.objects.link(o);curve.materials.append(lining)
 world=bpy.data.worlds.new('V13 neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.04,.04,.04,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;S.world=world
 for name,loc,power,size in [('key',(-1,-2,1.5),100,2),('fill',(1.2,-.5,1),70,2),('rim',(0,1,1.4),120,1.5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='V13 '+name;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.25))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();S.camera=bpy.context.object;S.camera.name='V13 geometry review camera';S.camera.data.type='ORTHO';S.camera.data.ortho_scale=.76
 reliquary(tor,plate);neck_layers(plate);camera('front');bpy.ops.wm.save_as_mainfile(filepath=str(D/f'v13-attempt-{A:02d}.blend'))
 (E/f'attempt-{A:02d}-construction.json').write_text(json.dumps({'attempt':A,'phase':'V13 sustained reference authoring','maximum_candidates':None,'guide_sha256':hashlib.sha256(GUIDE.read_bytes()).hexdigest(),'method':'Shared torso/arm envelope, real boolean-open armholes, unioned underbody, hollow gorget/cups, three offset lames each side. No silhouette extrusion or image mapping.','nominal_sheet_m':.003,'nominal_arm_clearance_m':.008,'nominal_lame_overlap_m':.012,'overlap_tongue_offset_m':[.006,.011],'hidden_tongue_intended_inner_clearance_m':.003,'inherited_v12_correction2':'Hidden tongues remain recessed beyond full12mm overlap before rising, addressing parity-confirmed shell penetration.', 'inherited_v12_correction1':'Recessed tongues separate overlapping shells; extended medial upper cup return, exposed outer span315mm.','neckline_flange':'Base z375mm +15mm lateral rise shared by torso neckline and gorget.','physics':False,'projection':False,'geometry_gate':'Requires actual front/side/back/oblique plus turntable review; numerical offsets alone are not a pass.'},indent=2)+'\n')

def camera(view,angle=None):
 target=Vector((0,0,.245));pos={'front':(0,-3,.35),'side':(3,0,.35),'back':(0,3,.35),'three-quarter':(1.7,-2.4,.55),'neck':(.7,-1.1,1.0)}.get(view,(0,-3,.35))
 if angle is not None:pos=(3*math.sin(angle),-3*math.cos(angle),.48)
 S.camera.location=pos;S.camera.rotation_euler=(target-Vector(pos)).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
def still(view):
 camera(view);S.render.filepath=str(E/f'attempt-{A:02d}-{view}.png');bpy.ops.render.render(write_still=True)
def audit():
 from mathutils.bvhtree import BVHTree
 def tree(ob):
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();vs=[ev.matrix_world@v.co for v in me.vertices];fs=[tuple(p.vertices) for p in me.polygons];ev.to_mesh_clear();return BVHTree.FromPolygons(vs,fs,all_triangles=False)
 body=bpy.data.objects['V13 | continuous connected underbody'];bt=tree(body);records=[];closed=[]
 for ob in S.objects:
  if ob.type!='MESH':continue
  ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data);closed.append({'object':ob.name,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'triangles':len(ob.data.loop_triangles),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'finite':all(math.isfinite(c) for v in ob.data.vertices for c in v.co)});bm.free()
  if 'shoulder cup' not in ob.name and 'overlapping lame' not in ob.name:continue
  ds=[]
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;hit,n,idx,d=bt.find_nearest(p);ds.append(d if (p-hit).dot(n)>=0 else -d)
  records.append({'object':ob.name,'sampled_vertices':len(ds),'min_signed_body_distance_m':min(ds),'negative_samples':sum(d<-.0001 for d in ds)})
 def inside(bt,p):
  votes=[]
  for direction in [Vector((.913,.317,.257)).normalized(),Vector((.173,.937,.299)).normalized(),Vector((.251,.193,.948)).normalized()]:
   origin=p.copy();hits=0
   for _ in range(50):
    hit,n,idx,d=bt.ray_cast(origin,direction,2)
    if hit is None:break
    hits+=1;origin=hit+direction*1e-7
   votes.append(hits%2)
  return sum(votes)>=2
 overlaps=[]
 for sign in [-1,1]:
  prior=bpy.data.objects['V13 | wrapping hollow shoulder cup '+str(sign)]
  for j in range(3):
   current=bpy.data.objects['V13 | shared-envelope overlapping lame '+str(sign)+' '+str(j)];pt=tree(prior);ds=[]
   for v in current.data.vertices:
    p=current.matrix_world@v.co;hit,n,idx,d=pt.find_nearest(p);ds.append(d if (p-hit).dot(n)>=0 else -d)
   overlaps.append({'lower':current.name,'upper':prior.name,'vertex_samples':len(ds),'ray_parity_inside_upper_shell':sum(inside(pt,current.matrix_world@v.co) for v in current.data.vertices),'legacy_nearest_normal_negative_count_not_containment':sum(d<-.0001 for d in ds),'legacy_nearest_normal_min_m_not_containment':min(ds)});prior=current
 report={'attempt':A,'saved_scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'geometry':closed,'arm_envelope_vertex_clearance':records,'overlap_vertex_checks':overlaps,'scope':'Body uses signed nearest vertex samples. Shell containment uses majority of three non-axis-aligned ray parity tests at lower-shell vertices (ray epsilon1e-7m); legacy nearest-normal values are NOT containment and produce false signs beyond thin-shell ends. Neither is an exhaustive triangle intersection or motion test.','no_projection':not any(n.type=='TEX_IMAGE' for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes),'physics':False}
 (E/('uv-geometry-audit.json' if mode=='uv-audit' else f'attempt-{A:02d}-geometry-audit.json')).write_text(json.dumps(report,indent=2)+'\n')
 assert all(x['finite'] for x in closed) and report['no_projection']

def geometry_digest():
 return hashlib.sha256(json.dumps({o.name:{'v':[list(v.co) for v in o.data.vertices],'f':[list(f.vertices) for f in o.data.polygons]} for o in S.objects if o.type=='MESH'},sort_keys=True).encode()).hexdigest()

def uv_study():
 """Automatic piecewise planar islands, honestly not a production seam unwrap."""
 import numpy as np
 original=geometry_digest();cleanup=[]
 from mathutils.kdtree import KDTree
 for ob in S.objects:
  if ob.type!='MESH' or 'cuirass' not in ob.name:continue
  old=[v.co.copy() for v in ob.data.vertices];kd=KDTree(len(old))
  for i,p in enumerate(old):kd.insert(p,i)
  kd.balance();pairs=[]
  for i,p in enumerate(old):
   for q,j,d in kd.find_range(p,1e-7):
    if j>i:pairs.append({'vertices':[i,j],'distance_m':d})
  bm=bmesh.new();bm.from_mesh(ob.data);bv=len(bm.verts);bf=len(bm.faces);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
  tiny=[f for f in bm.faces if f.calc_area()<1e-14]
  if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nonmanifold=sum(not e.is_manifold for e in bm.edges)
  assert nonmanifold==0, 'Cleanup broke closed shell; do not save'
  bm.to_mesh(ob.data);bm.free();ob.data.update();newkd=KDTree(len(ob.data.vertices))
  for i,v in enumerate(ob.data.vertices):newkd.insert(v.co,i)
  newkd.balance();displacement=max(newkd.find(p)[2] for p in old)
  assert displacement<=1e-7
  cleanup.append({'object':ob.name,'merge_tolerance_m':1e-7,'confirmed_near_pairs':pairs,'vertices_before':bv,'vertices_after':len(ob.data.vertices),'faces_before':bf,'faces_after':len(ob.data.polygons),'removed_tiny_faces':len(tiny),'max_old_vertex_to_clean_vertex_distance_m':displacement,'nonmanifold_edges_after':nonmanifold})
 before=geometry_digest();reports=[]
 (E/'uv-topology-cleanup.json').write_text(json.dumps({'original_frozen_geometry_digest':original,'derived_clean_geometry_digest':before,'scope':'Derived UV-preparation only; original attempt03 retained. Merge confirmed nearly coincident Boolean vertices at100nm tolerance; no visual design candidate. Geometry/topology NOT identical.','objects':cleanup},indent=2)+'\n')
 for ob in list(S.objects):
  if ob.type!='MESH' or 'underbody' in ob.name:continue
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
  ob.data.uv_layers.new(name='V13 packed piece UV');ob.data.uv_layers.active_index=len(ob.data.uv_layers)-1
  if mode=='uv-continuity':
   bm=bmesh.new();bm.from_mesh(ob.data)
   for edge in bm.edges:
    edge.seam=len(edge.link_faces)!=2 or edge.calc_face_angle(0)>math.radians(55)
    if 'cuirass' in ob.name or 'gorget' in ob.name:
     if all(abs(v.co.x)<1e-6 and v.co.y>0 for v in edge.verts):edge.seam=True
   bm.to_mesh(ob.data);bm.free()
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
  if mode=='uv-continuity':
   bpy.ops.uv.unwrap(method='ANGLE_BASED',margin=.025);bpy.ops.uv.pack_islands(rotate=False,margin=.025)
  else:bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.025,area_weight=0,correct_aspect=True,scale_to_bounds=True)
  bpy.ops.object.mode_set(mode='OBJECT')
  me=ob.data;me.calc_loop_triangles();uv=me.uv_layers.active;uv.active_render=True
  N=1024;cover=np.zeros((N,N),dtype=np.uint16);pic=np.full((N,N,4),.075,dtype=np.float32);pic[:,:,3]=1
  areas=[];geom_area=0;degenerate=0
  for tri in me.loop_triangles:
   pts=np.array([uv.data[i].uv[:] for i in tri.loops]);a,b,c=pts;det=float(np.cross(b-a,c-a));area=abs(det)/2;areas.append(area);geom_area+=tri.area
   if area<1e-12:degenerate+=1;continue
   lo=np.maximum(0,np.floor(pts.min(axis=0)*N-.5).astype(int));hi=np.minimum(N-1,np.ceil(pts.max(axis=0)*N-.5).astype(int))
   if np.any(hi<lo):continue
   xx,yy=np.meshgrid((np.arange(lo[0],hi[0]+1)+.5)/N,(np.arange(lo[1],hi[1]+1)+.5)/N);px=xx-a[0];py=yy-a[1]
   u=(px*(c-a)[1]-py*(c-a)[0])/det;v=((b-a)[0]*py-(b-a)[1]*px)/det;mask=(u>1e-7)&(v>1e-7)&(u+v<1-1e-7)
   cover[lo[1]:hi[1]+1,lo[0]:hi[0]+1]+=mask
   for p,q in zip(pts,np.roll(pts,-1,axis=0)):
    k=max(2,int(np.linalg.norm(q-p)*N*2));line=p[None,:]+(q-p)[None,:]*np.linspace(0,1,k)[:,None];ij=np.clip((line*N).astype(int),0,N-1);pic[ij[:,1],ij[:,0],:3]=(.25,.7,.8)
  # Connected chart counts via shared edge UV agreement, not file count.
  parent=list(range(len(me.polygons)))
  def root(x):
   while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
   return x
  edges={}
  for poly in me.polygons:
   loops=list(poly.loop_indices)
   for i,j in zip(loops,loops[1:]+loops[:1]):
    vi,vj=me.loops[i].vertex_index,me.loops[j].vertex_index;key=tuple(sorted((vi,vj)));coords={vi:tuple(uv.data[i].uv),vj:tuple(uv.data[j].uv)}
    if key in edges:
     old,oc=edges[key]
     if all(sum((coords[k][axis]-oc[k][axis])**2 for axis in range(2))<1e-12 for k in key):parent[root(poly.index)]=root(old)
    else:edges[key]=(poly.index,coords)
  counts={}
  for f in me.polygons:k=root(f.index);counts[k]=counts.get(k,0)+1
  slug=ob.name.replace('V13 | ','').replace(' ','-');im=bpy.data.images.new('V13 UV layout '+slug,width=N,height=N);im.pixels.foreach_set(pic.ravel());im.filepath_raw=str(E/('uv-'+slug+'.png'));im.file_format='PNG';im.save();bpy.data.images.remove(im)
  report={'object':ob.name,'layer':uv.name,'triangles':len(areas),'degenerate_uv_triangles_area_lt_1e-12':degenerate,'uv_area_sum':sum(areas),'geometry_area_m2':geom_area,'charts':len(counts),'smallest_chart_faces':min(counts.values()),'largest_chart_faces':max(counts.values()),'sample_resolution':N,'strict_interior_overlap_pixels':int((cover>1).sum()),'covered_pixel_fraction':float((cover>0).mean()),'finite':all(math.isfinite(c) for x in uv.data for c in x.uv),'layout':'uv-'+slug+'.png'}
  reports.append(report)
  mat=material('V13 20mm UV checker '+slug,(.2,.2,.2));nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map=uv.name;check=nt.nodes.new('ShaderNodeTexChecker');check.inputs['Color1'].default_value=(.025,.045,.06,1);check.inputs['Color2'].default_value=(.62,.65,.68,1)
  # Mean areal normalization only, not a guarantee of equal local texel density.
  check.inputs['Scale'].default_value=math.sqrt(geom_area/sum(areas))/.020;nt.links.new(uvn.outputs['UV'],check.inputs['Vector']);nt.links.new(check.outputs['Color'],bs.inputs['Base Color']);ob.data.materials.clear();ob.data.materials.append(mat)
 after=geometry_digest();assert before==after
 (E/'uv-audit.json').write_text(json.dumps({'method':('Continuous surface angle-based unwrap;55degree geometric edge seams separate outer/inner/thickness returns; rear median seam on cuirass/gorget; independently packed piece atlases. One bounded UV-only correction, not geometry change.' if mode=='uv-continuity' else 'Blender Smart UV Project66deg,2.5percentmargin, independently packed atlas per piece; not hand-authored production seam unwrap. Intentional texture repetition between pieces.'),'scope':'1024px strict-interior triangle raster overlap sampling, not exact/subpixel proof. Checker20mm uses mean areal normalization, local distortion must be visually reviewed.','geometry_digest_before':before,'geometry_digest_after':after,'pieces':reports},indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'v13-uv-checker.blend'))
 for view in ['front','side','back','three-quarter']:
  camera(view);S.render.filepath=str(E/f'uv-checker-{view}.png');bpy.ops.render.render(write_still=True)

def sample():
 source=Path(args[1]).resolve();assert source.is_relative_to(R) and source.is_file()
 before=geometry_digest();uvreport=json.loads((E/'uv-audit.json').read_text());records={r['object']:r for r in uvreport['pieces']}
 im=bpy.data.images.load(str(source),check_existing=False);im.name='V13 generated flat steel color - unmeasured material study';im.colorspace_settings.name='sRGB';im.pack()
 for ob in S.objects:
  if ob.name not in records:continue
  r=records[ob.name];mat=material('V13 generated steel sample '+ob.name,(.2,.2,.2));nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=1
  uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map=r['layer'];scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=math.sqrt(r['geometry_area_m2']/r['uv_area_sum'])/.400
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';tex.label='Original generated flat color, not concept photograph';nt.links.new(uvn.outputs['UV'],scale.inputs[0]);nt.links.new(scale.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  gray=nt.nodes.new('ShaderNodeRGBToBW');rough=nt.nodes.new('ShaderNodeMapRange');rough.label='Illustrative luminance-derived roughness, NOT measured';rough.inputs['From Min'].default_value=.015;rough.inputs['From Max'].default_value=.35;rough.inputs['To Min'].default_value=.68;rough.inputs['To Max'].default_value=.32;rough.clamp=True
  nt.links.new(tex.outputs['Color'],gray.inputs[0]);nt.links.new(gray.outputs[0],rough.inputs['Value']);nt.links.new(rough.outputs[0],bs.inputs['Roughness']);ob.data.materials.clear();ob.data.materials.append(mat)
 assert geometry_digest()==before
 camera('three-quarter');bpy.ops.wm.save_as_mainfile(filepath=str(D/'v13-material-study.blend'))
 for view in ['front','side','back','three-quarter']:
  camera(view);S.render.filepath=str(E/f'material-{view}.png');bpy.ops.render.render(write_still=True)
 camera('three-quarter');key=bpy.data.objects['V13 key'];oldloc=key.location.copy();oldrot=key.rotation_euler.copy();key.location=(1.3,-1.3,.8);key.rotation_euler=(Vector((0,0,.25))-key.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();S.render.filepath=str(E/'material-three-quarter-light-B.png');bpy.ops.render.render(write_still=True);key.location=oldloc;key.rotation_euler=oldrot
 S.render.resolution_x=1400;S.render.resolution_y=1400;S.cycles.samples=32;S.render.filepath=str(E/'material-detail.png');bpy.ops.render.render(write_still=True)
 (E/'material-study.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'image_size':list(im.size),'image_packed':bool(im.packed_file),'geometry_digest':before,'uv_source':'v13-uv-checker.blend','texture_scope':'Generated flat steel color mapped through actual per-piece UVs over all sides, repeated with mean400mm tile scale; no concept image projection. Not measured albedo/PBR or built geometric relief.','roughness':'Illustrative inverse luminance mapping .68 to .32, not a measured roughness map. No image-derived displacement or bump.','two_light_scope':'Same geometry/material/camera; only key position changes for lightB. Base light restored for1400detail.','uv_limits':'Derived tiny-tolerance Boolean cleanup precedes automatic atlas mapping; see UV audit. Final coherent chart layout retains sampled foldovers and local density differences; see UV audit. No clean or production-UV claim.'},indent=2)+'\n')

def sample_audit():
 uvreport=json.loads((E/'uv-audit.json').read_text());records=[]
 for ob in S.objects:
  if ob.type!='MESH' or 'underbody' in ob.name:continue
  mat=ob.data.materials[0];nt=mat.node_tree;images=[n for n in nt.nodes if n.type=='TEX_IMAGE'];uvnodes=[n for n in nt.nodes if n.type=='UVMAP'];bs=nt.nodes.get('Principled BSDF')
  records.append({'object':ob.name,'material':mat.name,'uv_layers':[u.name for u in ob.data.uv_layers],'uv_nodes':[n.uv_map for n in uvnodes],'image_nodes':len(images),'packed':all(n.image and n.image.packed_file for n in images),'color_linked':bool(bs.inputs['Base Color'].links),'roughness_linked':bool(bs.inputs['Roughness'].links),'metallic':bs.inputs['Metallic'].default_value})
 report={'counts':{'mesh_objects':sum(o.type=='MESH' for o in S.objects),'vertices':sum(len(o.data.vertices) for o in S.objects if o.type=='MESH'),'faces':sum(len(o.data.polygons) for o in S.objects if o.type=='MESH')},'packed_images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE'],'saved_scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'geometry_digest':geometry_digest(),'uv_geometry_digest':uvreport['geometry_digest_after'],'assignments':records,'scope':'Saved-scene reload confirms same geometry and actual UV/image/roughness wiring. Not image quality, calibrated reflectance or production-UV validation.'}
 assert report['geometry_digest']==report['uv_geometry_digest'] and all(r['packed'] and r['image_nodes']==1 and r['color_linked'] and r['roughness_linked'] for r in records)
 (E/'material-reload-audit.json').write_text(json.dumps(report,indent=2)+'\n')

def path_point(points,t):
 n=len(points)-1;i=min(n-1,max(0,int(t*n)));u=min(1,max(0,t*n-i));a,b,c,d=[Vector(points[max(0,min(n,k))]) for k in [i-1,i,i+1,i+2]]
 return .5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)

def thread_curve(name,points,radius,ma):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=1;cu.use_fill_caps=True;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(ma);return ob

def collar_wrap(root):
 import random
 removed=[]
 for ob in list(S.objects):
  if ob.name.startswith(('V10 | mantle','V5 | bound yoke')):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 wool=material('V13 dense charcoal woven wool',(.0028,.0025,.0022));bs=wool.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92;bs.inputs['Specular IOR Level'].default_value=.08
 diff=wool.node_tree.nodes.new('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(.008,.007,.006,1);diff.inputs['Roughness'].default_value=.8;wool.node_tree.links.new(diff.outputs[0],wool.node_tree.nodes.get('Material Output').inputs['Surface'])
 noise=wool.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=950;noise.inputs['Detail'].default_value=2;co=wool.node_tree.nodes.new('ShaderNodeTexCoord');wool.node_tree.links.new(co.outputs['Object'],noise.inputs['Vector']);bump=wool.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00018;bump.inputs['Strength'].default_value=.25;wool.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);wool.node_tree.links.new(bump.outputs[0],diff.inputs['Normal'])
 points=[(-.045,-.12,1.565),(-.11,-.09,1.590),(-.14,-.02,1.600),(-.11,.075,1.610),(0,.115,1.615),(.11,.075,1.610),(.14,-.02,1.590),(.105,-.10,1.570),(.045,-.145,1.555)]
 def surf(t,a):
  p=path_point(points,t);out=Vector((p.x,p.y,0)).normalized();end=min(1,.35+min(t,1-t)*7);width=(.036+.005*math.sin(math.pi*t))*end;height=.023*end
  lobe=1+.12*math.exp(-((t-.22)/.08)**2)+.18*math.exp(-((t-.68)/.09)**2)-.12*math.exp(-((t-.44)/.035)**2)
  drop=(.023+.012*math.sin(math.pi*t))*max(0,math.cos(a))
  z=height*lobe*math.sin(a)-drop-.003*math.exp(-((a-.72)/.095)**2)-.0025*math.exp(-((a-1.20)/.09)**2)
  return p+out*(width*math.cos(a))+Vector((0,0,z))
 N=96;M=32;vs=[];fs=[]
 for i in range(N+1):
  for j in range(M):vs.append(tuple(surf(i/N,2*math.pi*j/M)))
 for i in range(N):
  for j in range(M):a=i*M+j;b=i*M+(j+1)%M;fs.append((a,b,b+M,a+M))
 fs.extend([tuple(reversed(range(M))),tuple(N*M+j for j in range(M))]);ob=mesh('V13 | sewn compressed horseshoe collar',vs,fs,wool);ob.parent=root
 thread=material('V13 subdued wool stitching',(.055,.049,.039))
 for a in [.72,1.20]:
  for i in range(90):
   t=(i+.15)/90;end=min(1,t+.005);o=thread_curve('V13 | collar recessed stitch',[surf(t,a)+Vector((0,0,.0003)),surf(end,a)+Vector((0,0,.0003))],.00035,thread);o.parent=root
 # Coherent irregular lock groups plus short root cover; no planar cards or uniform hanging fringe.
 rng=random.Random(1302);guides=[(.04,.019),(.12,.033),(.22,.046),(.31,.025),(.43,.039),(.53,.029),(.65,.045),(.77,.035),(.88,.026),(.96,.017)];count=0
 for shade,color in enumerate([(.018,.016,.014),(.038,.033,.028),(.064,.055,.044)]):
  ma=material('V13 grouped rim fur '+str(shade),color);cu=bpy.data.curves.new('V13 curved lock fibers','CURVE');cu.dimensions='3D';cu.bevel_depth=.00028;cu.bevel_resolution=0;cu.use_fill_caps=True
  for i in range(1800):
   centre,length=guides[rng.randrange(len(guides))];t=max(.001,min(.999,rng.gauss(centre,.024)));a=rng.uniform(.05,1.36);p=surf(t,a);out=Vector((p.x,p.y,0)).normalized();tangent=(path_point(points,min(1,t+.002))-path_point(points,max(0,t-.002))).normalized();direction=(out*.85+tangent*(.25*math.sin(centre*19))).normalized();short=i%3==0;length=(rng.uniform(.008,.016) if short else length*rng.uniform(.65,1.15));sp=cu.splines.new('NURBS');sp.points.add(6);sp.order_u=3;sp.use_endpoint_u=True
   for k,q in enumerate(sp.points):
    u=k/6;pos=p+direction*length*u+Vector((0,0,.009*math.sin(math.pi*u)-length*.65*u*u));q.co=(*pos,1);q.radius=max(.06,1-u*.94)
   count+=1
  ob=bpy.data.objects.new('V13 | grouped curved fur rim '+str(shade),cu);bpy.context.collection.objects.link(ob);cu.materials.append(ma);ob.parent=root
 leather=material('V13 collar attachment leather',(.021,.014,.009));path=[(-.048,-.133,1.565),(-.016,-.152,1.555),(.020,-.163,1.553),(.046,-.155,1.555)];vs=[]
 for i in range(33):
  p=path_point(path,i/32);vs.extend([tuple(p+Vector((0,0,-.006))),tuple(p+Vector((0,0,.006)))])
 ob=mesh('V13 | seated collar retention strap',vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(32)],leather);thick(ob,.002);ob.parent=root
 bronze=bpy.data.materials['V13 restrained aged reliquary bronze'];ob=thread_curve('V13 | collar single clasp',[(-.014,-.158,1.548),(-.014,-.158,1.565),(.006,-.164,1.565),(.006,-.164,1.548),(-.014,-.158,1.548)],.0014,bronze);ob.parent=root
 (E/f'context-{C:02d}-collar.json').write_text(json.dumps({'method':'Closed padded horseshoe mesh with compressed ends, actual shallow seam valleys and stitching, root-following curved fur clusters. Authored static geometry, no cloth physics.','removed':removed,'support_vertices':len(bpy.data.objects['V13 | sewn compressed horseshoe collar'].data.vertices),'fiber_count':count,'guide_centres_lengths':guides,'limits':'No dynamic grooming/collision guarantee; visual softness requires review.'},indent=2)+'\n')

def limb_craft(root,steel):
 from mathutils import Matrix
 changed=[];removed=[]
 # Replace spherical cops with a shallow broad dorsal shield and continuous short side wings.
 for ob in list(S.objects):
  if ob.name.startswith(('Couter |','Couter wing','Poleyn |','Poleyn wing','Knee raised arris')):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 for kind,z,rx,rz,yback,depth,cx in [('Couter',1.187,.059,.059,-.018,.036,.351),('Poleyn',.559,.078,.062,-.068,.040,.118)]:
  for sign in [-1,1]:
   name=('L' if sign<0 else 'R')+' | sculpted '+kind;old=bpy.data.objects.get(name)
   if old:bpy.data.objects.remove(old,do_unlink=True)
   outline=[(0,1),(.50,.90),(.80,.56),(1.18,.28),(1.30,.05),(1.13,-.18),(.72,-.40),(.38,-.82),(0,-1),(-.40,-.80),(-.76,-.37),(-.94,.02),(-.80,.48),(-.48,.88)]
   vs=[(sign*cx,yback-depth,z)];fs=[];N=len(outline);M=10
   for j in range(1,M+1):
    r=j/M
    for u,v in outline:
     # Shield field is nearly planar through its middle; only the perimeter returns around the joint.
     factor=(1-.06*(r/.58)**2 if r<=.58 else .94*max(0,1-(r-.58)/.42)**.65)
     keel=.002*max(0,1-abs(u*r)/.25)*(1-r)
     vs.append((sign*(cx+rx*r*u),yback-depth*factor-keel,z+rz*r*v))
   for k in range(N):fs.append((0,k+1,(k+1)%N+1))
   for j in range(M-1):
    for k in range(N):a=1+j*N+k;b=1+j*N+(k+1)%N;fs.append((a,b,b+N,a+N))
   ob=mesh(name,vs,fs,steel);thick(ob,.002);ob.parent=root;changed.append(name)
   # Dark flexible support joins the existing limb sleeves behind the armor, not a metal ball.
   pad=bpy.data.materials.get('V13 joint arming wool') or material('V13 joint arming wool',(.009,.008,.007))
   bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(sign*cx,.012 if kind=='Couter' else -.015,z));ob=bpy.context.object;ob.name='V13 | '+kind+' connected joint padding '+str(sign);ob.scale=(rx*.78,.045 if kind=='Couter' else .065,rz*.9);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(pad);ob.parent=root
 # Forearm plates/rolled lips retain wrist and elbow centres, but gain a broad dorsal field.
 for ob in S.objects:
  if not ('vambrace' in ob.name.lower()):continue
  if ob.type not in ['MESH','CURVE']:continue
  inv=ob.matrix_world.inverted()
  def warp(v):
   p=ob.matrix_world@Vector(v);sg=1 if p.x>0 else -1;t=max(0,min(1,(p.z-.96)/.20));cx=sg*blend(.385,.358,t);rx=blend(.046,.063,t);ry=blend(.049,.066,t);u=max(-.999,min(.999,(p.x-cx)/rx))
   if p.y<.008:
    original=math.sqrt(max(0,1-u*u));q=abs(u);target=(.96-.08*q/.60 if q<=.60 else .88*((1-q)/.40)**.62);p.y+=ry*(original-target)
   p.x=cx+(p.x-cx)*(1-.08*(1-t));return inv@p
  if ob.type=='MESH':
   for v in ob.data.vertices:v.co=warp(v.co)
  else:
   for sp in ob.data.splines:
    if sp.type=='BEZIER':
     for v in sp.bezier_points:
      v.co=warp(v.co);v.handle_left=warp(v.handle_left);v.handle_right=warp(v.handle_right)
    else:
     for v in sp.points:v.co=(*warp(v.co[:3]),v.co.w)
  if ob.type=='MESH' and 'tapered vambrace' in ob.name:
   bm=bmesh.new();bm.from_mesh(ob.data);caps=[f for f in bm.faces if len(f.verts)>4];bmesh.ops.delete(bm,geom=caps,context='FACES');bm.to_mesh(ob.data);bm.free()
   sol=ob.modifiers.new('V13 actual hollow forearm sheet','SOLIDIFY');sol.thickness=.0018;sol.offset=-1;bpy.context.view_layer.objects.active=ob
   while ob.modifiers.find(sol.name)>0:bpy.ops.object.modifier_move_up(modifier=sol.name)
  changed.append(ob.name)
 # Same authored steel source on old armor; leather, cloth, bronze and the sword stay separate.
 unified=[]
 for ob in S.objects:
  if ob.type not in ['MESH','CURVE'] or ob.name.startswith('STUDIO'):continue
  lo=ob.name.lower()
  if any(x in lo for x in ['oathwake','guard','cape','surcoat','buckle','rivet','stud','frame','clasp','leather','fur','collar','stitch','reliquary field']):continue
  points=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  if points and abs(sum(v.x for v in points)/len(points))>.55:continue
  metallic=False
  for ma in ob.data.materials:
   if ma and ma.use_nodes:
    bs=ma.node_tree.nodes.get('Principled BSDF')
    if bs and bs.inputs['Metallic'].default_value>=.5:metallic=True
  if metallic:ob.data.materials.clear();ob.data.materials.append(steel);unified.append(ob.name)
 (E/f'context-{C:02d}-limb-craft.json').write_text(json.dumps({'method':'Actual shallow shield joint cops with integrated side widening, dorsal-plane forearm deformation and8percent distal-width taper; joint/wrist centres and hand size unchanged.','changed':changed,'removed_old_cop_trim_wings':removed,'steel_unified_objects':unified,'limits':'Static fit requires actual multiangle review; no articulation or production rig claim.'},indent=2)+'\n')

def garment_mass(root):
 from mathutils.bvhtree import BVHTree
 def tree(predicate):
  vs=[];fs=[];dg=bpy.context.evaluated_depsgraph_get()
  for ob in S.objects:
   if ob.type!='MESH' or ob.hide_render or not predicate(ob.name):continue
   ev=ob.evaluated_get(dg);me=ev.to_mesh();off=len(vs);vs.extend(ev.matrix_world@v.co for v in me.vertices);fs.extend(tuple(off+i for i in f.vertices) for f in me.polygons);ev.to_mesh_clear()
  return BVHTree.FromPolygons(vs,fs)
 covered_hardware=[]
 for name in ['Leather retention strap.002','Retention buckle.002','Leather retention strap.005','Retention buckle.005']:
  ob=bpy.data.objects.get(name)
  if ob:ob.hide_render=True;covered_hardware.append(name)
 # Fit the actual upper mail attachment under the belt before deriving its envelope.
 mailboxes=[];mail_changes=[]
 for ob in S.objects:
  if 'mail skirt' not in ob.name.lower() or ob.type!='MESH':continue
  inv=ob.matrix_world.inverted();maxshift=0
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;t=max(0,min(1,(p.z-1.0)/.038));t=t*t*(3-2*t);old=p.copy();p.y+=.030*t;p.x*=1-.10*t;v.co=inv@p;maxshift=max(maxshift,(p-old).length)
  points=[ob.matrix_world@v.co for v in ob.data.vertices];mailboxes.append({'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]});mail_changes.append({'object':ob.name,'max_vertex_displacement_m':maxshift})
 bpy.context.view_layer.update()
 belt=tree(lambda n:n=='Waist | double stitched belt')
 body=tree(lambda n:any(s in n.lower() for s in ['poleyn','joint padding','arming doublet']));plates=tree(lambda n:'shaped suspended tasset' in n)
 removed=[]
 for ob in list(S.objects):
  if ob.name.startswith(('V10 | authored static split','V10 | surcoat')):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 cloth=material('V13 dense dark surcoat wool',(.009,.008,.006));bs=cloth.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9;bs.inputs['Specular IOR Level'].default_value=.1
 co=cloth.node_tree.nodes.new('ShaderNodeTexCoord');noise=cloth.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1150;noise.inputs['Detail'].default_value=2;cloth.node_tree.links.new(co.outputs['Object'],noise.inputs['Vector']);bump=cloth.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00016;bump.inputs['Strength'].default_value=.3;cloth.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);cloth.node_tree.links.new(bump.outputs[0],bs.inputs['Normal'])
 seam=material('V13 subdued bound wool hem',(.023,.019,.013));records=[]
 for sign in [-1,1]:
  vs=[];fs=[];N=40;M=64;infeasible=0;bodymin=[];platemin=[]
  for j in range(M+1):
   v=j/M;outer=.165+.040*min(1,v/.060)+.015*math.sin(math.pi*v)
   for i in range(N+1):
    u=i/N;hem=.525+(.025 if sign>0 else 0)+.055*u**1.5;z=blend(1.065,hem,v);x=sign*blend(.021,outer,u)
    depth=blend(.112,.158,min(1,v/.20)) if v<.20 else blend(.158,.125,(v-.20)/.80);y=blend(-depth,-.015,u**3.5)
    q1=.25+.32*v;q2=.76-.15*v;amplitude=math.sin(math.pi*min(1,v/.85))**.65
    y+=amplitude*(-.024*math.exp(-((u-q1)/.14)**2)+.009*math.exp(-((u-q1-.16)/.12)**2)-.014*math.exp(-((u-q2)/.13)**2))
    p=Vector((x,y,z));bh,bn,bi,bd=body.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2);ph,pn,pi,pd=plates.ray_cast(Vector((x,1,z)),Vector((0,-1,0)),2)
    hi=bh.y-.006 if bh is not None else 1;lo=ph.y+.006 if ph is not None else -1
    # Smooth conservative thigh bridge; no discontinuous copying of cuisse end faces.
    if .57<z<.96:
     lateral=(abs(x)-.11)/.111
     if abs(lateral)<1:
      envelope=-.006-.118*math.sqrt(max(0,1-lateral*lateral))
      hi=min(hi,envelope-.006)
    for box in mailboxes:
     if box['min'][0]-.002<=x<=box['max'][0]+.002 and box['min'][2]-.14<=z<=box['max'][2]+.002:
      # Conservative filled front envelope, adjusted continuously for the upper attachment fit.
      t=max(0,min(1,(z-1.0)/.038));t=t*t*(3-2*t);edge=max(0,min(1,(z-box['min'][2]+.14)/.14));edge=edge*edge*(3-2*edge);mail_limit=box['min'][1]+.030*t-.006;hi=min(hi,blend(-.006-.118*math.sqrt(max(0,1-((abs(x)-.11)/.111)**2))-.006,mail_limit,edge))
    belt_hit,_,_,_=belt.ray_cast(Vector((x,-1,z)),Vector((0,1,0)),2)
    if belt_hit is not None:lo=max(lo,belt_hit.y+.008)
    if lo>hi:infeasible+=1
    p.y=max(lo,min(hi,p.y)-math.log1p(math.exp(-abs(hi-p.y)*180))/180);vs.append(tuple(p))
    if bh is not None:bodymin.append(bh.y-p.y)
    if ph is not None:platemin.append(p.y-ph.y)
  for j in range(M):
   for i in range(N):k=j*(N+1)+i;fs.append((k,k+1,k+N+2,k+N+1))
  ob=mesh('V13 | thigh wrapping static surcoat '+str(sign),vs,fs,cloth);thick(ob,.0012);ob.parent=root
  for side in [0,N]:
   pts=[Vector(vs[j*(N+1)+side])+Vector((0,-.0008,0)) for j in range(M+1)];ob=thread_curve('V13 | sewn surcoat side hem',pts,.0008,seam);ob.parent=root
  pts=[Vector(vs[M*(N+1)+i])+Vector((0,-.0008,0)) for i in range(N+1)];ob=thread_curve('V13 | unequal sloped surcoat hem',pts,.0009,seam);ob.parent=root
  records.append({'side':sign,'infeasible_body_plate_gaps':infeasible,'sampled_body_front_gap_min_m':min(bodymin) if bodymin else None,'sampled_tasset_back_gap_min_m':min(platemin) if platemin else None,'control_vertices':len(vs)})
 # Bend all retained cape surfaces/hem/seams together into real flank returns.
 changed=[];rear_shell=tree(lambda n:n=='V13 | continuous hollow cuirass front and back');cape_reseat=[]
 for ob in S.objects:
  if 'cape' not in ob.name.lower() or ob.type not in ['MESH','CURVE']:continue
  inv=ob.matrix_world.inverted()
  def warp(v):
   p=ob.matrix_world@Vector(v);t=max(0,min(1,(1.526-p.z)/1.32));width=.18+.23*t;u=max(-1.2,min(1.2,(p.x-.015)/width));old=.15+.30*t-.10*t*u*u;w=min(1,t/.52);target=.15+.040*t-.28*w*abs(u)**3
   target+=w*(-.035*math.exp(-((u-(-.55+.12*t))/.13)**2)+.025*math.exp(-((u-(-.37+.12*t))/.13)**2)-.025*math.exp(-((u-(.45-.07*t))/.15)**2)+.018*math.exp(-((u-(.63-.07*t))/.12)**2));p.y+=target-old
   # Keep upper side return behind the actual hip pouch; broad cage limit, not a local emboss.
   upper=max(0,min(1,(p.z-.55)/.35));upper=upper*upper*(3-2*upper);limit=blend(-.16,.065,upper);p.y=max(p.y,limit)+math.log1p(math.exp(-abs(p.y-limit)*70))/70
   # Curved sewn shoulder yoke: tuck beneath collar, shoulder anchors above central sag.
   attach=max(0,min(1,(p.z-1.375)/.15));attach=attach*attach*(3-2*attach);ux=max(-1,min(1,(p.x-.015)/.18));top=1.585+.008*abs(ux)**1.4
   p.z+=attach*(top-1.525);p.x=.015+(p.x-.015)*(1-.40*attach);arc=.135*math.sqrt(max(.05,1-((p.x-.015)/.14)**2));p.y=blend(p.y,arc,attach)
   if p.z>1.35:
    hit,_,_,_=rear_shell.ray_cast(Vector((p.x,1,p.z)),Vector((0,-1,0)),2)
    if hit is not None:
     prior=p.y;limit=hit.y+.006;p.y=max(p.y,limit)+math.log1p(math.exp(-abs(p.y-limit)*180))/180;cape_reseat.append(p.y-prior)
   hemweight=max(0,min(1,(.60-p.z)/.33));p.z=blend(p.z,.10+.40*(p.z-.20),hemweight)
   return inv@p
  if ob.type=='MESH':
   for v in ob.data.vertices:v.co=warp(v.co)
  else:
   for sp in ob.data.splines:
    if sp.type=='BEZIER':
     for v in sp.bezier_points:v.co=warp(v.co);v.handle_left=warp(v.handle_left);v.handle_right=warp(v.handle_right)
    else:
     for v in sp.points:v.co=(*warp(v.co[:3]),v.co.w)
  changed.append(ob.name)
 (E/f'context-{C:02d}-garment.json').write_text(json.dumps({'method':'Authored static thigh-wrapping panels with broad unequal diagonal folds, sloped asymmetric hems and1.2mm thickness. Retained cape and seams receive shared flank-return warp. NOT simulated.','removed':removed,'covered_hardware_hidden_preserved':covered_hardware,'actual_upper_mail_fit':mail_changes,'mail_envelope':'Filled front envelope using actual post-fit bounds plus known upper attachment shift, prevents rays through ring holes from declaring false clearance.','surcoat_samples':records,'cape_changed':changed,'cape_upper_shell_reseat_max_m':max(cape_reseat) if cape_reseat else 0,'cape_upper_shell_reseat_samples':len(cape_reseat),'scope':'Cloth control-vertex front body and back tasset ray envelopes, not full triangle or motion certification. Cape clearance requires actual views and final scoped audit.'},indent=2)+'\n')

def sword_craft():
 root=bpy.data.objects['OATHWAKE | display assembly'];hidden=[]
 for ob in S.objects:
  if ob.name.startswith(('Oathwake ivory grip splint','Oathwake | spiral leather binding seam','V2 | flattened lantern guard terminal')):
   ob.hide_render=True;hidden.append(ob.name)
 leather=material('V13 Oathwake compressed dark leather',(.014,.009,.006));bs=leather.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.68
 grip=bpy.data.objects['Oathwake | long two-handed leather grip'];grip.data.materials.clear();grip.data.materials.append(leather)
 # Real overlapping ribbon, broad crown and compressed edges, around continuous grip core.
 vs=[];fs=[];N=1080;W=8
 for j in range(N+1):
  t=j/N;a=t*2*math.pi*15
  for k in range(W+1):
   u=k/W;z=1.446+.228*t+(u-.5)*.017
   radius=.001+.0007*math.sin(math.pi*u)**.7
   rx=.017-.002*max(0,min(1,(z-1.48)/.14));ry=.012-.001*max(0,min(1,(z-1.48)/.14))
   vs.append((.71+(rx+radius)*math.cos(a),-.01+(ry+radius)*math.sin(a),z))
 for j in range(N):
  for k in range(W):a=j*(W+1)+k;fs.append((a,a+1,a+W+2,a+W+1))
 ob=mesh('V13 | Oathwake overlapping cut leather ribbon',vs,fs,leather);thick(ob,.0006);ob.parent=root
 steel=bpy.data.materials['V13 contextual generated steel preview']
 for ob in S.objects:
  if ob.name.startswith(('V2 | Oathwake forged swept guard','V2 | guard worn crest')):ob.hide_render=True;hidden.append(ob.name)
 for sign in [-1,1]:
  vs=[];fs=[];N=64;M=16
  for j in range(N+1):
   t=j/N;flare=max(0,(t-.80)/.20);z=1.398-.022*math.sin(math.pi*t)+.008*t*t
   for k in range(M):
    a=2*math.pi*k/M;depth=.009*(1-.55*flare);height=.009+.007*flare
    vs.append((.71+sign*.192*t,-.01+.012*math.sin(math.pi*t)+depth*math.cos(a),z+height*math.sin(a)))
  for j in range(N):
   for k in range(M):a=j*M+k;b=j*M+(k+1)%M;fs.append((a,b,b+M,a+M))
  fs.extend([tuple(reversed(range(M))),tuple(N*M+k for k in range(M))]);ob=mesh('V13 | continuous swept forged quillon',vs,fs,steel);ob.parent=root
 # Shape blade shoulders into the seated ricasso while preserving lower blade and total endpoints.
 for ob in S.objects:
  if ob.type=='MESH' and ob.name.startswith(('OATHWAKE | forged blade','Oathwake | tempered cutting bevel')):
   for v in ob.data.vertices:
    if v.co.z>1.30:
     t=max(0,min(1,(v.co.z-1.30)/.07));v.co.z-=.025*t*max(0,(abs(v.co.x-.71)-.020)/.029)
 # Preserve continuous tang, actual fullered blade, brazed fracture and seven oath marks.
 (E/f'context-{C:02d}-sword.json').write_text(json.dumps({'hidden_preserved':hidden,'added':['real overlapping leather ribbon','two flattened swept quillon fins'],'preserved':'Lower blade/tip and grip/pommel endpoints, tang socket, ferrules and lore-bearing fracture/seven marks preserved; upper blade shoulders explicitly chamfered into ricasso. No new lore or projected detail.','runtime':False},indent=2)+'\n')

def gauntlet_craft(root,steel):
 from mathutils.bvhtree import BVHTree
 dg=bpy.context.evaluated_depsgraph_get();leather_trees={};seated=[]
 for label in ['L','R']:
  ob=bpy.data.objects['FOCAL | '+label+' unified leather palm thumb and fingers'];ev=ob.evaluated_get(dg);me=ev.to_mesh();leather_trees[label]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
 hidden=[]
 for ob in S.objects:
  if ob.type=='MESH' and ob.name.startswith(('FOCAL | dorsal finger lame','FOCAL | curved thumb dorsal plate')):
   ob.data.materials.clear();ob.data.materials.append(steel);pts=[ob.matrix_world@v.co for v in ob.data.vertices];bt=leather_trees['R' if sum(p.x for p in pts)>0 else 'L'];offset=0
   for p in pts:
    hit,_,_,_=bt.ray_cast(Vector((p.x,-1,p.z)),Vector((0,1,0)),2)
    if hit is not None:offset=max(offset,p.y-hit.y+.0016)
   offset=min(.006,max(0,offset));inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:v.co=inv@(ob.matrix_world@v.co-Vector((0,offset,0)))
   seated.append({'object':ob.name,'front_reseat_m':offset})
  if 'formed metacarpal plate' in ob.name:ob.hide_render=True;hidden.append(ob.name)
 for sign in [-1,1]:
  for band in range(3):
   vs=[];fs=[];N=32;M=8
   for j in range(M+1):
    v=j/M;zbase=.959-band*.019-v*.025
    for i in range(N+1):
     u=i/N;xx=blend(.357,.431,u);arc=.006*math.exp(-((u-.34)/.24)**2)-.008*u*u
     # Conforming knuckle arc, quiet low ridges over index/middle rather than one slab.
     z=zbase+arc*(.3+.7*(band+v)/3)
     y=-.0275-.009*math.sin(math.pi*u)**.7-.0015*math.sin(math.pi*v)
     y-=.0018*(math.exp(-((u-.15)/.08)**2)+math.exp(-((u-.40)/.08)**2))*((band+v)/3)
     vs.append((sign*xx,y,z))
   for j in range(M):
    for i in range(N):a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
   ob=mesh('V13 | articulated metacarpal lame '+str(sign)+' '+str(band),vs,fs,steel);thick(ob,.0012);ob.parent=root
 (E/f'context-{C:02d}-gauntlet.json').write_text(json.dumps({'hidden_preserved':hidden,'finger_plate_reseating':seated,'method':'Three actual overlapping curved metacarpal plates with staggered knuckle arc and index/middle ridges. Existing connected leather palm/thumb and dorsal finger plates retained, no anatomy success claim.','unchanged':'Palm/finger size, finger endpoints and hand center preserved.','scope':'Static construction study, not articulated animation.'},indent=2)+'\n')

def helmet_craft(root):
 records=[]
 for name in ['FOCAL | forged landmark skull','FOCAL | crown closure']:
  ob=bpy.data.objects[name];inv=ob.matrix_world.inverted();maximum=0
  for v in ob.data.vertices:
   p=ob.matrix_world@v.co;old=p.copy();t=max(0,min(1,(p.z-1.751)/.123));w=math.sin(math.pi*t)
   # Reshape the broad crown fields toward a peaked section, keeping eye rim and apex.
   p.x*=1-.12*t;p.y+=.010*w*max(0,min(1,-p.y/.09));v.co=inv@p;maximum=max(maximum,(p-old).length)
  records.append({'object':name,'maximum_vertex_displacement_m':maximum})
 (E/f'context-{C:02d}-helmet.json').write_text(json.dumps({'method':'Broad crown field taper and receding forehead, no attached decorative ridge. Existing eye aperture, hollow visor, hinges and vents preserved.','changes':records,'limits':'Static silhouette study, not a head fit/rig or historical accuracy claim.'},indent=2)+'\n')

def context_camera(view):
 views={'hero':((2.55,-5.4,2.35),(.16,0,1.0),78),'front':((.15,-6,2.0),(.16,0,1.0),75),'back':((-2.5,5.1,2.5),(0,.1,1.04),75),'side':((-4,-.3,1.9),(0,0,1),60),'torso':((1.1,-2.3,1.55),(0,-.04,1.37),105),'hilt':((1.28,-1.65,1.75),(.71,0,1.48),95),'head':((1.1,-2.3,1.82),(0,-.02,1.65),110),'hand':((.85,-1.1,1.0),(.39,-.02,.94),115),'palm':((.85,1.1,1.0),(.39,.01,.91),115),'garment':((1.3,-2,1.10),(0,-.12,.80),100)}
 pos,target,lens=views[view];S.camera.location=pos;S.camera.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=lens;bpy.context.view_layer.update()

def context_build():
 global S
 from mathutils import Matrix
 from mathutils.bvhtree import BVHTree
 base=R/'unreal/art-studio/revision-v10-2026-11-07/last-vigil-v10.blend';focal=D/f'v13-attempt-{A:02d}.blend'
 bpy.ops.wm.open_mainfile(filepath=str(base));S=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0;root=bpy.data.objects['CHARACTER | shoulder-turn study'];removed=[]
 prefixes=['V6 | fitted ','V6 | rolled ','V6 | returned breastplate','V6 | rib retention','V2 | recessed gate','V2 | forged gate','V2 | gate panel','V2 | shallow field scuff','V4 | articulated gorget','V4 | sloping forged shoulder','V7 | turned shoulder','V9 armor | shared-shell lame']
 for ob in list(S.objects):
  remove=any(ob.name.startswith(q) for q in prefixes) or ob.name=='V5 | bound yoke opening.001'
  if ob.name.startswith('Peened rivet'):
   pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];z=sum(v.z for v in pts)/len(pts)
   if 1.20<z<1.59:remove=True
  if remove:removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 with bpy.data.libraries.load(str(focal),link=False) as (data,to):
  to.objects=[n for n in data.objects if n.startswith('V13 |') and 'underbody' not in n and n!='V13 | hollow seated gorget']
 added=[]
 for ob in to.objects:
  if not ob:continue
  bpy.context.collection.objects.link(ob)
  if 'shoulder cup' in ob.name or 'overlapping lame' in ob.name:
   for v in ob.data.vertices:
    sign=1 if v.co.x>0 else -1;v.co.x+=sign*(-.010+.55*(.31-v.co.z))
  ob.matrix_world=Matrix.Translation((0,0,1.18))@ob.matrix_basis.copy();world=ob.matrix_world.copy();ob.parent=root;ob.matrix_world=world;added.append(ob.name)
 bpy.context.view_layer.update()
 # Fit only the inherited hidden doublet surface under the replacement shell.
 tor=bpy.data.objects['V13 | continuous hollow cuirass front and back'];bt=BVHTree.FromPolygons([tor.matrix_world@v.co for v in tor.data.vertices],[tuple(f.vertices) for f in tor.data.polygons])
 core=bpy.data.objects['Padded arming doublet'];bpy.context.view_layer.objects.active=core
 for mod in list(core.modifiers):
  if mod.type=='SUBSURF':bpy.ops.object.modifier_apply(modifier=mod.name)
 fitted=0;invm=core.matrix_world.inverted()
 for v in core.data.vertices:
  p=core.matrix_world@v.co
  if 1.18<=p.z<=1.56:
   direction=Vector((p.x,p.y,0));length=direction.length
   if length>.0001:
    direction.normalize();hit,n,idx,d=bt.ray_cast(Vector((0,0,p.z)),direction,.5)
    if hit is not None and length>d-.006:v.co=invm@(hit-direction*.006);fitted+=1
 # Explicit box-mapped preview avoids inheriting the failed V12 UV atlas. No clean-UV claim.
 imagepath=R/'artifacts/art/last-vigil-v12/texture-study/generated-aged-steel-albedo.png';im=bpy.data.images.load(str(imagepath),check_existing=True);im.pack()
 steel=material('V13 contextual generated steel preview',(.15,.15,.15));nt=steel.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=.95;co=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=2.5;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.projection='BOX';tex.projection_blend=.25;nt.links.new(co.outputs['Object'],scale.inputs[0]);nt.links.new(scale.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.47
 bronze=material('V13 restrained aged reliquary bronze',(.17,.105,.044));bronze.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.8;bronze.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.48
 dark=material('V13 reliquary dark protected steel',(.025,.027,.029));dark.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.75
 for name in added:
  ob=bpy.data.objects[name]
  if ob.type not in ['MESH','CURVE']:continue
  ob.data.materials.clear();ob.data.materials.append(bronze if 'frame' in name or 'stud' in name else dark if 'reliquary field' in name else steel)
 collar_wrap(root);limb_craft(root,steel);garment_mass(root);sword_craft();gauntlet_craft(root,steel);helmet_craft(root);S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.render.resolution_x=720;S.render.resolution_y=920;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';context_camera('hero');bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v13-context.blend'))
 (E/'context-construction.json').write_text(json.dumps({'base':str(base.relative_to(R)),'base_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),'focal':str(focal.relative_to(R)),'focal_sha256':hashlib.sha256(focal.read_bytes()).hexdigest(),'removed':removed,'added':added,'fitted_old_doublet_vertices':fitted,'placement_z_m':1.18,'shoulder_pose':'LocalX shift sign*(-10mm +.55*(.31-localZ)); retains coherent connected shell, follows existing angled arms.','material':'Packed V12 original generated flat steel, object-space box mapping preview only; not production UV/PBR. Existing V10 head/limbs/cape/sword retained for context assessment.','physics':False,'runtime':False},indent=2)+'\n')
 for view in args[1:] or ['hero','front','side','back','torso']:
  context_camera(view);S.render.filepath=str(E/f'context-{C:02d}-{view}.png');bpy.ops.render.render(write_still=True)

if mode=='draft':build()
else:bpy.ops.wm.open_mainfile(filepath=str(D/f'v13-attempt-{A:02d}.blend'));S=bpy.context.scene
if mode=='audit':audit()
if mode in ['draft','probe']:
 for view in args[1:] or ['front','side','back','three-quarter','neck']:still(view)

if mode=='context-inventory':
 bpy.ops.wm.open_mainfile(filepath=str(R/'unreal/art-studio/revision-v10-2026-11-07/last-vigil-v10.blend'));S=bpy.context.scene
 out=[]
 for o in S.objects:
  if o.type not in ['MESH','CURVE']:continue
  points=[o.matrix_world@Vector(v) for v in o.bound_box]
  out.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)],'hidden':o.hide_render})
 (E/'v10-context-inventory.json').write_text(json.dumps(out,indent=2)+'\n')

if mode=='context':context_build()

if mode=='context-diagnose':
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v13-context.blend'));S=bpy.context.scene;context_camera(args[1] if len(args)>1 else 'torso');cam=S.camera;frame=cam.data.view_frame(scene=S);records=[]
 for x,y in ([(int(args[2]),int(args[3]))] if len(args)>3 else [(260,203),(453,212),(475,292),(220,243),(500,204),(275,190)]):
  u=(x+.5)/720;v=(y+.5)/920;direction=Vector((min(p.x for p in frame)+(max(p.x for p in frame)-min(p.x for p in frame))*u,max(p.y for p in frame)-(max(p.y for p in frame)-min(p.y for p in frame))*v,frame[0].z));direction=cam.matrix_world.to_quaternion()@direction.normalized();hit,loc,n,face,obj,m=S.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.matrix_world.translation,direction)
  records.append({'pixel':[x,y],'hit':obj.name if hit else None,'location':list(loc) if hit else None,'materials':[{'name':ma.name,'basecolor':list(ma.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value),'metallic':ma.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value,'roughness':ma.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value} for ma in obj.data.materials if ma and ma.use_nodes and ma.node_tree.nodes.get('Principled BSDF')] if hit else []})
 (E/f'context-{C:02d}-neck-ray-diagnosis.json').write_text(json.dumps(records,indent=2)+'\n');print(records)

if mode=='context-probe':
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v13-context.blend'));S=bpy.context.scene
 for view in args[1:]:
  context_camera(view);S.render.filepath=str(E/f'context-{C:02d}-{view}.png');bpy.ops.render.render(write_still=True)

if mode=='context-audit':
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v13-context.blend'));S=bpy.context.scene;bpy.context.view_layer.update()
 visible=[o for o in S.objects if o.type in ['MESH','CURVE'] and not o.hide_render and not o.name.startswith('COLLIDER')]
 records=[];finite=True
 for ob in visible:
  if ob.type=='MESH':
   points=[ob.matrix_world@v.co for v in ob.data.vertices];finite=finite and all(math.isfinite(c) for p in points for c in p)
   records.append({'name':ob.name,'vertices':len(points),'faces':len(ob.data.polygons),'min':[min(p[i] for p in points) for i in range(3)] if points else None,'max':[max(p[i] for p in points) for i in range(3)] if points else None})
 cameras={}
 for view in ['hero','front','side','back','head','hand','palm','hilt','garment']:
  context_camera(view);cameras[view]={'world_matrix':[list(row) for row in S.camera.matrix_world],'lens_mm':S.camera.data.lens}
 steel=bpy.data.materials['V13 contextual generated steel preview'];nodes=steel.node_tree.nodes
 report={'scene':str(Path(bpy.data.filepath).relative_to(R)),'scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'finite_visible_control_vertices':finite,'visible_control_meshes':len(records),'visible_control_vertices':sum(r['vertices'] for r in records),'visible_control_faces':sum(r['faces'] for r in records),'meshes':records,'cameras':cameras,'packed_images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE'],'steel_preview':{'projection':[n.projection for n in nodes if n.type=='TEX_IMAGE'],'image_names':[n.image.name for n in nodes if n.type=='TEX_IMAGE'],'roughness':nodes.get('Principled BSDF').inputs['Roughness'].default_value,'metallic':nodes.get('Principled BSDF').inputs['Metallic'].default_value,'scope':'Actual packed image/object box mapping, not clean UV or calibrated PBR; variable inherited object scales remain.'},'scope':'Saved scene readback, control-mesh finite/count/bounds, actual camera and packed material wiring only. Not evaluated polygon count, all-triangle collision, runtime deformation or production topology. Garment gap evidence is independently scoped control-point rays in construction JSON.'}
 assert finite
 (E/'context-reload-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','cameras','packed_images']},indent=2))

if mode in ['context-final','context-detail']:
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v13-context.blend'));S=bpy.context.scene
 for view in args[1:]:
  clay=view.startswith('clay_');base=view[5:] if clay else view;context_camera(base)
  if clay:
   ma=material('V13 audit neutral clay',(.35,.35,.35));S.view_layers[0].material_override=ma
  else:S.view_layers[0].material_override=None
  if mode=='context-detail':S.render.resolution_x=1400;S.render.resolution_y=1800;S.cycles.samples=40
  else:S.render.resolution_x=720;S.render.resolution_y=920;S.cycles.samples=16
  S.render.filepath=str(E/('final-'+view.replace('_','-')+('-detail' if mode=='context-detail' else '')+'.png'));bpy.ops.render.render(write_still=True)
