import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path(__file__).resolve().parents[3];D=R/'unreal/art-studio/arena-design-01';E=R/'artifacts/art/arena-design-01/candidate-03';p=D/'court-last-witness-03.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.preferences.filepaths.save_version=0;s=bpy.context.scene
# Restore intentional opening camera in the saved review scene; geometry is unchanged.
cam=s.camera;cam.location=(-11.6,-1.2,1.75);cam.rotation_euler=(Vector((16.6,0,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.sensor_fit='HORIZONTAL';cam.data.lens=22;cam.data.clip_end=300

def geom_digest():
 h=hashlib.sha256()
 for o in sorted(s.objects,key=lambda x:x.name):
  if o.type not in ['MESH','CURVE','FONT']:continue
  h.update(o.name.encode());h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
  if o.type=='MESH':h.update(str([(tuple(v.co)) for v in o.data.vertices]).encode());h.update(str([tuple(f.vertices) for f in o.data.polygons]).encode())
 return h.hexdigest()
digest=geom_digest();dg=bpy.context.evaluated_depsgraph_get();triangles=0;closest=(1e9,None);floorz=[];objects=[];slab_samples=[]
def clip(poly,bound,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ina=a.z>=bound if above else a.z<=bound;inb=b.z>=bound if above else b.z<=bound
  if ina:out.append(a)
  if ina!=inb:out.append(a.lerp(b,(bound-a.z)/(b.z-a.z)))
 return out
def distance(poly):
 pts=[Vector((v.x,v.y)) for v in poly];inside=False
 for a,b in zip(pts,pts[1:]+pts[:1]):
  if (a.y>0)!=(b.y>0) and 0<(b.x-a.x)*(-a.y)/(b.y-a.y)+a.x:inside=not inside
 if inside:return 0
 return min((a+(b-a)*max(0,min(1,-a.dot(b-a)/max(1e-20,(b-a).length_squared)))).length for a,b in zip(pts,pts[1:]+pts[:1]))
for o in s.objects:
 if o.type not in ['MESH','CURVE'] or o.hide_render:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles)
 isfloor=any(k in o.name for k in ['continuous level arena slab','flush bronze','radial stone joint','three witness floor seal','seal upright'])
 if o.name=='continuous level arena slab':
  bv=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(t.vertices) for t in me.loop_triangles],all_triangles=True)
  for rad in [0,3,6,9,12,12.8]:
   for k in range(16 if rad else 1):
    x=rad*math.cos(k*math.tau/16);y=rad*math.sin(k*math.tau/16);hit=bv.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2);slab_samples.append({'xy':[x,y],'z':hit[0].z if hit[0] else None})
 if isfloor:
  floorz.extend((ev.matrix_world@v.co).z for v in me.vertices if (ev.matrix_world@v.co).z>-.01 and math.hypot((ev.matrix_world@v.co).x,(ev.matrix_world@v.co).y)<=12.8)
 else:
  localmin=1e9
  for t in me.loop_triangles:
   poly=[ev.matrix_world@me.vertices[i].co for i in t.vertices];poly=clip(poly,0,True)
   if poly:poly=clip(poly,3,False)
   if len(poly)>=3:localmin=min(localmin,distance(poly))
  if localmin<closest[0]:closest=(localmin,o.name)
  if localmin<1e8:objects.append({'name':o.name,'inner_radius_in_0_to_3m_height_band':localmin})
 ev.to_mesh_clear()
bpy.ops.wm.save_as_mainfile(filepath=str(p));after=hashlib.sha256(p.read_bytes()).hexdigest();assert geom_digest()==digest
report={'scene_before_camera_restore_sha256':before,'scene_sha256':after,'source_sha256':hashlib.sha256((R/'unreal/art-studio/source/arena_design_01.py').read_bytes()).hexdigest(),'geometry_digest_before_after_camera_restore':digest,'visible_evaluated_triangles':triangles,'objects_total':len(s.objects),'closest_nonfloor_geometry':{'radius_m':closest[0],'object':closest[1]},'radius12_8_clear_in_sampled_geometry':closest[0]>=12.8,'scope':'all visible evaluated nonfloor mesh/curve triangles clipped toZ0..3m and projectedXY polygon distance; excludes hidden plan annotations/height rulers and floor slab/inlays; not UEcollision/camera or dynamic gameplay certification','inlay_vertex_z_range_inside_R12_8_m':[min(floorz),max(floorz)],'slab_vertical_ray_samples':slab_samples,'slab_sample_scope':'81 vertical rays through evaluated slab across center and5rings, not arbitrary continuous surface proof','bounded_geometry':objects,'active_opening_camera':'hero-entry restored; no geometry changes','no_runtime_tests':True};(E/'saved-scene-audit.json').write_text(json.dumps(report,indent=2))
g=json.loads((E/'geometry.json').read_text())
for support in g['new_supports']:support['radius_m']=.62
g['min_new_support_inner_radius_m']=min(math.hypot(*x['center_m'])-.62 for x in g['new_supports']);g['new_support_radius_scope']='full plinth radius.62m, not shaft only';g['scoped_all_geometry_clearance']=report['closest_nonfloor_geometry'];(E/'geometry.json').write_text(json.dumps(g,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='bounded_geometry'},indent=2))
