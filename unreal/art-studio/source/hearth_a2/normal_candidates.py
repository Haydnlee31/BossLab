"""Read-only angle-limited normals experiment on disposable copies, plus authored arch normals."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';scene=R/'unreal/art-studio/hearth-a2-2026-11-16/final.blend';sourcehash=hashlib.sha256(scene.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(scene));report={}
def quality(me):
 me.calc_loop_triangles();count=neg=0;area=badarea=0;mins=1;uvbad=0;uv=me.uv_layers.active
 for t in me.loop_triangles:
  ds=[me.corner_normals[i].vector.dot(t.normal) for i in t.loops];count+=3;neg+=sum(d<0 for d in ds);mins=min(mins,*ds);area+=t.area;badarea+=t.area*sum(d<0 for d in ds)/3
  if uv:
   a,b,c=[uv.data[i].uv for i in t.loops];uvbad+=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<=1e-12
 return {'triangles':len(me.loop_triangles),'negative_corners':neg,'corner_count':count,'min_corner_face_dot':mins,'negative_corner_area_fraction':badarea/area if area else None,'uv_degenerate_triangles':uvbad,'area':area,'has_custom_normals':me.has_custom_normals,'smooth_faces':sum(p.use_smooth for p in me.polygons)}
for key in ['SteppedFurnace','AnvilWorkstation']:
 o=next(o for o in bpy.data.objects if o.get('hearth_a2_group')=='generated_'+key);me=o.data;baseline=quality(me);candidates={}
 for degrees in [60,45,30]:
  copy=me.copy();copy.normals_split_custom_set([(0,0,0)]*len(copy.loops));copy.set_sharp_from_angle(angle=math.radians(degrees));copy.update();candidates[str(degrees)]=quality(copy);bpy.data.meshes.remove(copy)
 # Compare retained raw source normals to geometric normal recomputation before decimation.
 cfg=json.loads((Path(__file__).parent/'assets.json').read_text())[key];prior=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/cfg['path']));raw=next(o for o in set(bpy.data.objects)-prior if o.type=='MESH');raw_quality=quality(raw.data);raw.data.normals_split_custom_set([(0,0,0)]*len(raw.data.loops));raw.data.update();raw_recomputed=quality(raw.data)
 report[key]={'canonical':baseline,'angle_limited_copy':candidates,'raw_imported':raw_quality,'raw_recomputed_no_decimation':raw_recomputed}
# Authored small-arch fronts are deliberately flat; inspect world-space normals and light direction.
arch=[]
for o in bpy.data.objects:
 if 'bellows' not in o.name.lower() or o.type!='MESH' or o.get('hearth_a2_group')!='masonry':continue
 eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();q=quality(me);q['object']=o.name;front=[]
 for poly in me.polygons:
  n=(o.matrix_world.to_3x3().inverted().transposed()@poly.normal).normalized()
  if n.y<-.7:
   p=o.matrix_world@poly.center;to_light=(Vector((3.3,10.7,2.65))-p).normalized();front.append({'normal':list(n),'dot_to_task_light':n.dot(to_light)})
 q['front_faces']=front;arch.append(q);eo.to_mesh_clear()
report['authored_bellows_arch']=arch
assert hashlib.sha256(scene.read_bytes()).hexdigest()==sourcehash
(E/'normal-candidates.json').write_text(json.dumps({'source_scene_sha256':sourcehash,'unchanged':True,'scope':'geometry and disk scene unchanged; candidates alter only disposable sharp-edge/custom-normal state','results':report},indent=2));print('NORMAL CANDIDATES COMPLETE')
