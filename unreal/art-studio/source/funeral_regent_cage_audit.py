import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path('/Users/haydn/Documents/BossLab');D=R/'unreal/art-studio/regent-cage-2026-11-09';E=R/'artifacts/art/regent-cage-2026-11-09/attempt-03';p=D/'regent-cage-03.blend';bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects['ONE explicitly bridged body cage'];bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);components=0
while unseen:
 components+=1;stack=[unseen.pop()]
 while stack:
  for ed in stack.pop().link_edges:
   for v in ed.verts:
    if v in unseen:unseen.remove(v);stack.append(v)
r={'scene_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'components':components,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_control_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume_m3':bm.calc_volume(signed=True),'rig_count':sum(x.type=='ARMATURE' for x in bpy.data.objects),'scope':'reload recomputation; no self-intersection/full contact or deformation certificate'};bm.free();dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();areas=[]
for tri in me.loop_triangles:
 a,b,c=[me.vertices[i].co for i in tri.vertices];areas.append((b-a).cross(c-a).length*.5)
r['evaluated_triangles']=len(areas);r['evaluated_zero_area_triangles_lt_1e_12']=sum(a<1e-12 for a in areas);r['evaluated_min_triangle_area_m2']=min(areas);r['evaluated_sole_min_z_m']={str(sign):min(v.co.z for v in me.vertices if v.co.x*sign>0) for sign in [-1,1]};r['local_arm_slab_samples']={}
for sign in [-1,1]:
 axis=Vector((sign*.34,0,-.94)).normalized();u=Vector((sign*.94,0,.34)).normalized()
 for label,c in [('elbow',(sign*.332,0,1.22)),('wrist',(sign*.395,0,1.015))]:
  c=Vector(c);pts=[v.co-c for v in me.vertices if abs((v.co-c).dot(axis))<.018 and (v.co-c).length<.11];r['local_arm_slab_samples'][str(sign)+label]={'vertices':len(pts),'cross_axis_extent_m':max(v.dot(u) for v in pts)-min(v.dot(u) for v in pts),'y_extent_m':max(v.y for v in pts)-min(v.y for v in pts),'scope':'finite nearby evaluated-vertex slab bounds, not exact plane intersection'}
ev.to_mesh_clear();(E/'saved-scene-audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
