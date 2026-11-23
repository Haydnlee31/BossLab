"""Read-only canonical-vs-export normal comparison; no scene save/render/mutation on disk."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';scene=R/'unreal/art-studio/hearth-a2-2026-11-16/final.blend';beforehash=hashlib.sha256(scene.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(scene));dg=bpy.context.evaluated_depsgraph_get();rot=Matrix.Diagonal((-1,-1,1));result={}
def key(v):return tuple(round(float(x),4) for x in v)
def summary(values):
 s=sorted(values);return {'count':len(s),'min':s[0] if s else None,'p01':s[int(.01*(len(s)-1))] if s else None,'median':s[len(s)//2] if s else None,'mean':sum(s)/len(s) if s else None,'below_0_5':sum(v<.5 for v in s),'negative':sum(v<0 for v in s)}
def quality(mesh):
 mesh.calc_loop_triangles();dots=[];uv=mesh.uv_layers.active;uvbad=0
 for t in mesh.loop_triangles:
  for li in t.loops:dots.append(mesh.corner_normals[li].vector.dot(t.normal))
  if uv:
   a,b,c=[uv.data[i].uv for i in t.loops];uvbad+=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<=1e-12
 return {'triangles':len(mesh.loop_triangles),'smooth_polygons':sum(p.use_smooth for p in mesh.polygons),'has_custom_normals':mesh.has_custom_normals,'corner_vs_face_dot':summary(dots),'uv_area_le_1e_12_triangles':uvbad}
for family in ['SteppedFurnace','AnvilWorkstation']:
 originals=[o for o in bpy.data.objects if o.get('hearth_a2_group')=='generated_'+family];expected={};source_quality=[]
 for o in originals:
  eo=o.evaluated_get(dg);me=eo.to_mesh();source_quality.append(quality(me));normalmat=o.matrix_world.to_3x3().inverted().transposed()
  for loop in me.loops:
   p=rot@(o.matrix_world@me.vertices[loop.vertex_index].co);n=(rot@normalmat@me.corner_normals[loop.index].vector).normalized();expected.setdefault(key(p),[]).append(n.copy())
  eo.to_mesh_clear()
 prior=set(bpy.data.objects);path=E/'export'/('SM_A2_generated_'+family+'.fbx');bpy.ops.import_scene.fbx(filepath=str(path),use_custom_normals=True);bpy.context.view_layer.update();imported=[o for o in set(bpy.data.objects)-prior if o.type=='MESH'];dots=[];missing=0;import_quality=[];bounds=[]
 for o in imported:
  me=o.data;import_quality.append(quality(me));nm=o.matrix_world.to_3x3().inverted().transposed()
  for loop in me.loops:
   p=o.matrix_world@me.vertices[loop.vertex_index].co;bounds.append(p.copy());n=(nm@me.corner_normals[loop.index].vector).normalized();candidates=expected.get(key(p))
   if candidates:dots.append(max(n.dot(v) for v in candidates))
   else:missing+=1
 result[family]={'source':source_quality,'fbx_import':import_quality,'position_key_precision_m':.0001,'matched_corner_normal_dot':summary(dots),'unmatched_corners':missing,'import_bounds_m':[[min(p[i] for p in bounds) for i in range(3)],[max(p[i] for p in bounds) for i in range(3)]],'fbx_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
assert hashlib.sha256(scene.read_bytes()).hexdigest()==beforehash
(E/'normal-audit.json').write_text(json.dumps({'source_scene_sha256':beforehash,'scene_unchanged':True,'scope':'Blender canonical evaluated corners versus actual FBX reimport; not Unreal render-buffer normals','results':result},indent=2));print(json.dumps(result,indent=2))
