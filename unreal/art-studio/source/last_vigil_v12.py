"""V12 geometry-first independent bust. No projection, physics, rig or game changes."""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];D=R/'unreal/art-studio/revision-v12-2026-11-07';E=R/'artifacts/art/last-vigil-v12';D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:];mode=args[0] if args else 'draft';A=3;S=bpy.context.scene
GUIDE=E/'design/shared-landmarks.json';g=json.loads(GUIDE.read_text())
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
 rows=[(0,.165,-.110,.100),(.100,.180,-.125,.110),(.240,.220,-.145,.115),(.330,.215,-.125,.110),(.355,.170,-.095,.095),(.375,.102,-.102,.102)]
 vs=[];fs=[];N=96
 for j,(z,rx,fy,by) in enumerate(rows):
  for k in range(N):
   a=2*math.pi*k/N;st=math.sin(a);ct=math.cos(a);x=rx*st;y=(-abs(fy)*ct if ct>=0 else -by*ct);zz=z+(.035 if j==4 else .015 if j==5 else 0)*st*st
   if not under:y-=.008*max(ct,0)**14*math.sin(math.pi*min(1,z/.4))
   else:x*=.94;y*=.90;zz-=.008 if j==5 else 0
   vs.append((x,y,zz))
 for j in range(len(rows)-1):
  for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 if under:fs.extend([tuple(reversed(range(N))),tuple((len(rows)-1)*N+k for k in range(N))])
 o=mesh('V12 | continuous connected underbody' if under else 'V12 | continuous hollow cuirass front and back',vs,fs,mat)
 if not under:thick(o)
 return o

def arm_r(z):
 t=max(0,min(1,(z-.17)/.14));return blend(.047,.056,t),blend(.063,.075,t)

def build():
 global S
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True;S.render.resolution_x=900;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
 plate=material('V12 neutral armor clay',(.24,.26,.28));lining=material('V12 dark neutral underbody clay',(.07,.08,.09));tor=torso(plate);body=torso(lining,True)
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
 gorget=mesh('V12 | hollow seated gorget',vs,fs,plate);thick(gorget)
 for sign in [-1,1]:
  # Open medial cup, wrapping front/lateral/rear over the exact shared arm envelope.
  N=64;M=18;vs=[(sign*.245,0,.39)];fs=[]
  for row in range(1,M+1):
   phi=(math.pi/2)*row/M
   for k in range(N+1):
    t=phi/(math.pi/2);span=math.pi-(math.pi-1.92)*t*t;a=-span+2*span*k/N;vs.append((sign*(.245+.070*math.sin(phi)*math.cos(a)),.089*math.sin(phi)*math.sin(a),.30+.09*math.cos(phi)))
  for k in range(N):fs.append((0,1+k,2+k))
  for row in range(M-1):
   for k in range(N):i=1+row*(N+1)+k;fs.append((i,i+1,i+N+2,i+N+1))
  cup=mesh('V12 | wrapping hollow shoulder cup '+str(sign),vs,fs,plate);thick(cup)
  for j,bottom in enumerate([.270,.240,.210]):
   top=bottom+.042;vs=[];fs=[];M=8
   for row in range(M+1):
    z=blend(top,bottom,row/M);rx,ry=arm_r(z);t=row/M;step=max(0,min(1,(t-.32)/.30));step=step*step*(3-2*step);offset=.006+.005*step;rx+=offset;ry+=offset
    for k in range(N+1):a=-1.92+3.84*k/N;vs.append((sign*(.245+rx*math.cos(a)),ry*math.sin(a),z))
   for row in range(M):
    for k in range(N):i=row*(N+1)+k;fs.append((i,i+1,i+N+2,i+N+1))
   lame=mesh('V12 | shared-envelope overlapping lame '+str(sign)+' '+str(j),vs,fs,plate);thick(lame)
 # Restrained actual rear closure line, same continuous shell beneath it.
 curve=bpy.data.curves.new('rear closure','CURVE');curve.dimensions='3D';curve.bevel_depth=.001;curve.bevel_resolution=2;sp=curve.splines.new('POLY');sp.points.add(4)
 for p,co in zip(sp.points,[(0,.102,.02),(0,.112,.10),(0,.117,.24),(0,.112,.33),(0,.097,.35)]):p.co=(*co,1)
 o=bpy.data.objects.new('V12 | centre rear closure seam',curve);bpy.context.collection.objects.link(o);curve.materials.append(lining)
 world=bpy.data.worlds.new('V12 neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.04,.04,.04,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;S.world=world
 for name,loc,power,size in [('key',(-1,-2,1.5),100,2),('fill',(1.2,-.5,1),70,2),('rim',(0,1,1.4),120,1.5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='V12 '+name;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.25))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();S.camera=bpy.context.object;S.camera.name='V12 geometry review camera';S.camera.data.type='ORTHO';S.camera.data.ortho_scale=.76
 camera('front');bpy.ops.wm.save_as_mainfile(filepath=str(D/f'v12-attempt-{A:02d}.blend'))
 (E/f'attempt-{A:02d}-construction.json').write_text(json.dumps({'attempt':A,'maximum_candidates':3,'guide_sha256':hashlib.sha256(GUIDE.read_bytes()).hexdigest(),'method':'Shared torso/arm envelope, real boolean-open armholes, unioned underbody, hollow gorget/cups, three offset lames each side. No silhouette extrusion or image mapping.','nominal_sheet_m':.003,'nominal_arm_clearance_m':.008,'nominal_lame_overlap_m':.012,'overlap_tongue_offset_m':[.006,.011],'hidden_tongue_intended_inner_clearance_m':.003,'correction2':'Hidden tongues remain recessed beyond full12mm overlap before rising, addressing parity-confirmed shell penetration.', 'correction1':'Recessed tongues separate overlapping shells; extended medial upper cup return, exposed outer span315mm.','neckline_flange':'Base z375mm +15mm lateral rise shared by torso neckline and gorget.','physics':False,'projection':False,'geometry_gate':'Requires actual front/side/back/oblique plus turntable review; numerical offsets alone are not a pass.'},indent=2)+'\n')

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
 body=bpy.data.objects['V12 | continuous connected underbody'];bt=tree(body);records=[];closed=[]
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
  prior=bpy.data.objects['V12 | wrapping hollow shoulder cup '+str(sign)]
  for j in range(3):
   current=bpy.data.objects['V12 | shared-envelope overlapping lame '+str(sign)+' '+str(j)];pt=tree(prior);ds=[]
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
  ob.data.uv_layers.new(name='V12 packed piece UV');ob.data.uv_layers.active_index=len(ob.data.uv_layers)-1
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
  slug=ob.name.replace('V12 | ','').replace(' ','-');im=bpy.data.images.new('V12 UV layout '+slug,width=N,height=N);im.pixels.foreach_set(pic.ravel());im.filepath_raw=str(E/('uv-'+slug+'.png'));im.file_format='PNG';im.save();bpy.data.images.remove(im)
  report={'object':ob.name,'layer':uv.name,'triangles':len(areas),'degenerate_uv_triangles_area_lt_1e-12':degenerate,'uv_area_sum':sum(areas),'geometry_area_m2':geom_area,'charts':len(counts),'smallest_chart_faces':min(counts.values()),'largest_chart_faces':max(counts.values()),'sample_resolution':N,'strict_interior_overlap_pixels':int((cover>1).sum()),'covered_pixel_fraction':float((cover>0).mean()),'finite':all(math.isfinite(c) for x in uv.data for c in x.uv),'layout':'uv-'+slug+'.png'}
  reports.append(report)
  mat=material('V12 20mm UV checker '+slug,(.2,.2,.2));nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map=uv.name;check=nt.nodes.new('ShaderNodeTexChecker');check.inputs['Color1'].default_value=(.025,.045,.06,1);check.inputs['Color2'].default_value=(.62,.65,.68,1)
  # Mean areal normalization only, not a guarantee of equal local texel density.
  check.inputs['Scale'].default_value=math.sqrt(geom_area/sum(areas))/.020;nt.links.new(uvn.outputs['UV'],check.inputs['Vector']);nt.links.new(check.outputs['Color'],bs.inputs['Base Color']);ob.data.materials.clear();ob.data.materials.append(mat)
 after=geometry_digest();assert before==after
 (E/'uv-audit.json').write_text(json.dumps({'method':('Continuous surface angle-based unwrap;55degree geometric edge seams separate outer/inner/thickness returns; rear median seam on cuirass/gorget; independently packed piece atlases. One bounded UV-only correction, not geometry change.' if mode=='uv-continuity' else 'Blender Smart UV Project66deg,2.5percentmargin, independently packed atlas per piece; not hand-authored production seam unwrap. Intentional texture repetition between pieces.'),'scope':'1024px strict-interior triangle raster overlap sampling, not exact/subpixel proof. Checker20mm uses mean areal normalization, local distortion must be visually reviewed.','geometry_digest_before':before,'geometry_digest_after':after,'pieces':reports},indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'v12-uv-checker.blend'))
 for view in ['front','side','back','three-quarter']:
  camera(view);S.render.filepath=str(E/f'uv-checker-{view}.png');bpy.ops.render.render(write_still=True)

def sample():
 source=Path(args[1]).resolve();assert source.is_relative_to(R) and source.is_file()
 before=geometry_digest();uvreport=json.loads((E/'uv-audit.json').read_text());records={r['object']:r for r in uvreport['pieces']}
 im=bpy.data.images.load(str(source),check_existing=False);im.name='V12 generated flat steel color - unmeasured material study';im.colorspace_settings.name='sRGB';im.pack()
 for ob in S.objects:
  if ob.name not in records:continue
  r=records[ob.name];mat=material('V12 generated steel sample '+ob.name,(.2,.2,.2));nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Metallic'].default_value=1
  uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map=r['layer'];scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=math.sqrt(r['geometry_area_m2']/r['uv_area_sum'])/.400
  tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';tex.label='Original generated flat color, not concept photograph';nt.links.new(uvn.outputs['UV'],scale.inputs[0]);nt.links.new(scale.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  gray=nt.nodes.new('ShaderNodeRGBToBW');rough=nt.nodes.new('ShaderNodeMapRange');rough.label='Illustrative luminance-derived roughness, NOT measured';rough.inputs['From Min'].default_value=.015;rough.inputs['From Max'].default_value=.35;rough.inputs['To Min'].default_value=.68;rough.inputs['To Max'].default_value=.32;rough.clamp=True
  nt.links.new(tex.outputs['Color'],gray.inputs[0]);nt.links.new(gray.outputs[0],rough.inputs['Value']);nt.links.new(rough.outputs[0],bs.inputs['Roughness']);ob.data.materials.clear();ob.data.materials.append(mat)
 assert geometry_digest()==before
 camera('three-quarter');bpy.ops.wm.save_as_mainfile(filepath=str(D/'v12-material-study.blend'))
 for view in ['front','side','back','three-quarter']:
  camera(view);S.render.filepath=str(E/f'material-{view}.png');bpy.ops.render.render(write_still=True)
 camera('three-quarter');key=bpy.data.objects['V12 key'];oldloc=key.location.copy();oldrot=key.rotation_euler.copy();key.location=(1.3,-1.3,.8);key.rotation_euler=(Vector((0,0,.25))-key.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();S.render.filepath=str(E/'material-three-quarter-light-B.png');bpy.ops.render.render(write_still=True);key.location=oldloc;key.rotation_euler=oldrot
 S.render.resolution_x=1400;S.render.resolution_y=1400;S.cycles.samples=32;S.render.filepath=str(E/'material-detail.png');bpy.ops.render.render(write_still=True)
 (E/'material-study.json').write_text(json.dumps({'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'image_size':list(im.size),'image_packed':bool(im.packed_file),'geometry_digest':before,'uv_source':'v12-uv-checker.blend','texture_scope':'Generated flat steel color mapped through actual per-piece UVs over all sides, repeated with mean400mm tile scale; no concept image projection. Not measured albedo/PBR or built geometric relief.','roughness':'Illustrative inverse luminance mapping .68 to .32, not a measured roughness map. No image-derived displacement or bump.','two_light_scope':'Same geometry/material/camera; only key position changes for lightB. Base light restored for1400detail.','uv_limits':'Derived tiny-tolerance Boolean cleanup precedes automatic atlas mapping; see UV audit. Final coherent chart layout retains sampled foldovers and local density differences; see UV audit. No clean or production-UV claim.'},indent=2)+'\n')

def sample_audit():
 uvreport=json.loads((E/'uv-audit.json').read_text());records=[]
 for ob in S.objects:
  if ob.type!='MESH' or 'underbody' in ob.name:continue
  mat=ob.data.materials[0];nt=mat.node_tree;images=[n for n in nt.nodes if n.type=='TEX_IMAGE'];uvnodes=[n for n in nt.nodes if n.type=='UVMAP'];bs=nt.nodes.get('Principled BSDF')
  records.append({'object':ob.name,'material':mat.name,'uv_layers':[u.name for u in ob.data.uv_layers],'uv_nodes':[n.uv_map for n in uvnodes],'image_nodes':len(images),'packed':all(n.image and n.image.packed_file for n in images),'color_linked':bool(bs.inputs['Base Color'].links),'roughness_linked':bool(bs.inputs['Roughness'].links),'metallic':bs.inputs['Metallic'].default_value})
 report={'counts':{'mesh_objects':sum(o.type=='MESH' for o in S.objects),'vertices':sum(len(o.data.vertices) for o in S.objects if o.type=='MESH'),'faces':sum(len(o.data.polygons) for o in S.objects if o.type=='MESH')},'packed_images':[{'name':im.name,'size':list(im.size),'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE'],'saved_scene_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'geometry_digest':geometry_digest(),'uv_geometry_digest':uvreport['geometry_digest_after'],'assignments':records,'scope':'Saved-scene reload confirms same geometry and actual UV/image/roughness wiring. Not image quality, calibrated reflectance or production-UV validation.'}
 assert report['geometry_digest']==report['uv_geometry_digest'] and all(r['packed'] and r['image_nodes']==1 and r['color_linked'] and r['roughness_linked'] for r in records)
 (E/'material-reload-audit.json').write_text(json.dumps(report,indent=2)+'\n')

if mode=='draft':build()
else:bpy.ops.wm.open_mainfile(filepath=str(D/('v12-material-study.blend' if mode=='sample-audit' else 'v12-uv-checker.blend' if mode in ['uvinspect','sample','uv-audit'] else f'v12-attempt-{A:02d}.blend')));S=bpy.context.scene
if mode in ['audit','uv-audit']:audit()
if mode in ['uv','uv-continuity']:uv_study()
if mode=='sample':sample()
if mode=='sample-audit':sample_audit()
if mode in ['draft','probe']:
 for view in args[1:] or ['front','side','back','three-quarter','neck']:still(view)
elif mode=='turntable':
 folder=E/f'attempt-{A:02d}-turntable';folder.mkdir(exist_ok=True);S.render.resolution_x=480;S.render.resolution_y=480;S.cycles.samples=8
 for frame in range(36):
  camera('orbit',frame/36*2*math.pi);S.render.filepath=str(folder/f'{frame:03d}.png');bpy.ops.render.render(write_still=True)
 # Encode already-rendered frames through Blender's built-in video sequencer; no external install.
 seq=bpy.data.scenes.new('V12 turntable encoding');seq.render.resolution_x=480;seq.render.resolution_y=480;seq.render.resolution_percentage=100;seq.render.fps=12;seq.frame_start=1;seq.frame_end=36;ed=seq.sequence_editor_create();strip=ed.strips.new_image('actual clay orbit',filepath=str(folder/'000.png'),channel=1,frame_start=1)
 for frame in range(1,36):strip.elements.append(f'{frame:03d}.png')
 seq.render.image_settings.file_format='FFMPEG';seq.render.ffmpeg.format='MPEG4';seq.render.ffmpeg.codec='H264';seq.render.ffmpeg.constant_rate_factor='MEDIUM';seq.render.filepath=str(E/f'attempt-{A:02d}-turntable.mp4');seq.view_settings.view_transform='Standard';bpy.ops.render.render(animation=True,scene=seq.name)
 clip=bpy.data.movieclips.load(str(E/f'attempt-{A:02d}-turntable.mp4'));(E/f'attempt-{A:02d}-turntable-audit.json').write_text(json.dumps({'frames_rendered':36,'unique_png_hashes':len({hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.png')}),'decoded_movie_frames':clip.frame_duration,'fps':12,'scope':'Untextured camera orbit around static geometry, not character or cloth animation'},indent=2)+'\n')

if mode=='uvinspect':
 report=[]
 for ob in S.objects:
  if ob.type!='MESH' or not ob.data.uv_layers:continue
  me=ob.data;me.calc_loop_triangles();uv=me.uv_layers.active
  for tr in me.loop_triangles:
   a,b,c=[uv.data[i].uv for i in tr.loops];area=abs((b-a).cross(c-a))/2
   if area<1e-12:report.append({'object':ob.name,'polygon':tr.polygon_index,'uv_area':area,'geometry_area':tr.area,'vertices':[list(me.vertices[i].co) for i in tr.vertices],'uvs':[list(uv.data[i].uv) for i in tr.loops]})
 (E/'uv-degenerate-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n')
