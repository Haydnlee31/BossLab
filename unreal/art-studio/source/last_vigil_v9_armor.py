"""Independent rigid-lame authoring branch from frozen V8. No V9 cloth imported."""
from pathlib import Path
previous=Path(__file__).with_name('last_vigil_v8.py')
exec(compile(previous.read_text().split("\nif mode=='baseline':")[0],str(previous),'exec'))
D=R/'unreal/art-studio/revision-v9-armor-2026-11-07';E=R/'artifacts/art/last-vigil-v9-armor';D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
V8=R/'unreal/art-studio/revision-v8-2026-11-07/last-vigil-v8.blend'
oldcamera=camera
def camera(view):
 if view=='shoulder_side':
  pos=Vector((-2.2,.04,1.62));target=Vector((-.29,.015,1.43));S.camera.location=pos;S.camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=115
 else:oldcamera(view)

def build_armor():
 global S
 from mathutils.bvhtree import BVHTree
 bpy.ops.wm.open_mainfile(filepath=str(V8));S=bpy.context.scene;setdevice();root=bpy.data.objects['CHARACTER | shoulder-turn study'];verts=[];faces=[];removed=[];deleted_plate_points=[]
 for ob in list(S.objects):
  if ob.type=='MESH' and any(t in ob.name.lower() for t in ['arming sleeve',' | rerebrace']):
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();off=len(verts);verts.extend([ev.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(off+i for i in p.vertices) for p in me.polygons]);ev.to_mesh_clear()
  lower=any(ob.name.startswith('V4 | sloping forged shoulder lame '+str(j)) for j in [1,2,3])
  oldreturn=ob.name.startswith('V7 | turned shoulder perimeter') and sum(v.co.z for v in ob.data.vertices)/len(ob.data.vertices)<1.47
  if lower or oldreturn:
   if lower:deleted_plate_points.extend([ob.matrix_world@v.co for v in ob.data.vertices])
   removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 for ob in list(S.objects):
  if ob.name.startswith('Peened rivet') and deleted_plate_points:
   point=ob.matrix_world.translation
   if min((point-p).length for p in deleted_plate_points)<.008:removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 sections=[]
 for z in [1.33,1.36,1.39,1.42,1.45,1.48,1.51,1.54]:
  pts=[p for p in verts if abs(p.z-z)<.026]
  rx=max([abs(p.x)-(.334-(p.z-1.22)*.25) for p in pts] or [.028]);ry=max([abs(p.y-.015) for p in pts] or [.045]);sections.append((z,rx+.002,ry+.002))
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=False);ma=bpy.data.materials['V7 forged shoulder'];records=[]
 for sg in [-1,1]:
  for j in range(3):
   vs=[];fs=[];rows=10;cols=48;hits=0
   for row in range(rows+1):
    t=row/rows
    for k in range(cols+1):
     theta=-1.47+2.94*k/cols;z=1.52-j*.035-.049*t-.035*sin(theta)**2
     cx=.334-(z-1.22)*.25;cy=.015;direction=Vector((sg*cos(theta),sin(theta),0));centre=Vector((sg*cx,cy,z));origin=centre+direction*.25
     section=v5_curve(sections,(z-1.33)/.21);rx,ry=section[1],section[2]
     p=centre+Vector((sg*rx*cos(theta),ry*sin(theta),0))+direction*(.010-j*.003)
     vs.append(tuple(p))
   # Integral short turned lower return in the same mesh, not a second wire object.
   for k in range(cols+1):
    p=Vector(vs[rows*(cols+1)+k]);theta=-1.47+2.94*k/cols;p-=Vector((sg*cos(theta),sin(theta),0))*.0015;p.z-=.002;vs.append(tuple(p))
   for row in range(rows+1):
    for k in range(cols):
     a=row*(cols+1)+k;f=(a,a+1,a+cols+2,a+cols+1);fs.append(f if sg>0 else tuple(reversed(f)))
   ob=plate_patch('V9 armor | shared-shell lame '+str(sg)+' '+str(j),vs,fs,ma,.002);ob.parent=root
   uv=ob.data.uv_layers.new(name='V7 forged UV');xs=[p[0] for p in vs];ys=[p[1] for p in vs]
   for face in ob.data.polygons:
    for li in face.loop_indices:
     p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((p.x-min(xs))/(max(xs)-min(xs)),(p.y-min(ys))/(max(ys)-min(ys)))
   records.append({'object':ob.name,'vertices':len(vs),'support_section_count':len(sections),'main_samples':(rows+1)*(cols+1),'nominal_upper_overlap_m':.014,'sheet_thickness_m':.002,'integral_return_depth_m':.002,'body_clearance_source_m':.010-j*.003})
 (E/'armor-construction.json').write_text(json.dumps({'scope':'Independent V8 rigid shoulder branch; shared smooth loft fitted to measured arm cross-section bounds, not cloth or rig','input_scene':str(V8.relative_to(R)),'removed':removed,'lames':records,'measured_support_sections_z_rx_ry':sections,'materials':'Inherited V7 shoulder material/maps with same planar sample UV convention; no new finish claim','limits':'Source overlap and radial offsets are construction intent, require actual view and clearance review'},indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v9-armor.blend'))

def audit_armor():
 global S
 import hashlib,struct
 from mathutils.bvhtree import BVHTree
 def original_objects():
  out={};root=bpy.data.objects['CHARACTER | shoulder-turn study']
  for ob in S.objects:
   if ob.parent!=root or ob.type not in ['MESH','CURVE']:continue
   h=hashlib.sha256();h.update(str([list(r) for r in ob.matrix_world]).encode());h.update(str([m.name if m else None for m in ob.data.materials]).encode())
   if ob.type=='MESH':
    for v in ob.data.vertices:h.update(struct.pack('<3f',*v.co))
    for f in ob.data.polygons:h.update(str(tuple(f.vertices)).encode())
   else:
    for sp in ob.data.splines:
     for v in sp.points:h.update(struct.pack('<4f',*v.co))
     for v in sp.bezier_points:h.update(struct.pack('<3f',*v.co))
   out[ob.name]=h.hexdigest()
  return out
 bpy.ops.wm.open_mainfile(filepath=str(V8));S=bpy.context.scene;before=original_objects();protected_before=protected_state()
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v9-armor.blend'));S=bpy.context.scene;after=original_objects();protected_after=protected_state()
 removed=json.loads((E/'armor-construction.json').read_text())['removed'];changed=[n for n in before if n in after and before[n]!=after[n]];missing=[n for n in before if n not in after and n not in removed]
 verts=[];faces=[]
 for ob in S.objects:
  if ob.type=='MESH' and any(t in ob.name.lower() for t in ['arming sleeve',' | rerebrace']):
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();off=len(verts);verts.extend([ev.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(off+i for i in p.vertices) for p in me.polygons]);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=False);clearances=[]
 for ob in S.objects:
  if not ob.name.startswith('V9 armor | shared-shell lame'):continue
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();ds=[]
  for v in me.vertices:
   p=ev.matrix_world@v.co;hit,n,idx,dist=tree.find_nearest(p)
   if hit is not None:ds.append(dist if (p-hit).dot(n)>=0 else -dist)
  ev.to_mesh_clear();clearances.append({'object':ob.name,'samples':len(ds),'min_signed_nearest_m':min(ds),'samples_below_minus_1mm':sum(d<-.001 for d in ds)})
 result={'scope':'Exact retained original character geometry/material-name/transform hashes plus protected camera/sword comparison; signed vertex nearest-arm surfaces only, not arbitrary triangle or motion collision proof','retained_original_objects':len(set(before)&set(after)),'changed_retained_objects':changed,'unexpected_missing_original_objects':missing,'explicitly_removed_old_plate_hardware':removed,'protected_before':protected_before,'protected_after':protected_after,'protected_match':protected_before==protected_after,'sampled_arm_fit':clearances,'no_v9_cloth_objects':not any(o.name.startswith('V9 | actual cloth') or o.name.startswith('V9 | settled static cloth') for o in S.objects)}
 (E/'armor-reload-audit.json').write_text(json.dumps(result,indent=2)+'\n');assert not changed and not missing and result['protected_match'] and result['no_v9_cloth_objects']

if mode=='draft':build_armor()
elif mode=='baseline':
 E=E/'baseline-v8';E.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(V8));S=bpy.context.scene;setdevice()
else:
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v9-armor.blend'));S=bpy.context.scene;setdevice()
if mode in ['draft','probe','render','baseline']:
 S.render.resolution_x=1400 if mode=='render' else 720;S.render.resolution_y=1800 if mode=='render' else 920;S.cycles.samples=48 if mode=='render' else 16
 for v in args[1:] or ['clay_shoulder','clay_shoulder_side']:render(v)
if mode=='audit':audit_armor()
asset_audit();audit_static_clearance()
