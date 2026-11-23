"""Reload the final studio blend and exported GLB, without changing either."""
import bpy,json,hashlib,math,struct
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[4];D=R/'unreal/art-studio/bellbreaker-arena-2026-11-16';E=R/'artifacts/art/bellbreaker-arena-2026-11-16'
scene=D/'final-v3.blend';glb=D/'last-casting.glb'
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(scene))
deps=bpy.context.evaluated_depsgraph_get();objects=[]
for o in bpy.context.scene.objects:
 if o.type not in {'MESH','CURVE'}:continue
 ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();objects.append({'name':o.name,'triangles':len(m.loop_triangles),'area_le_1e_12_m2':sum(1 for t in m.loop_triangles if ((m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co)).length*.5<=1e-12),'finite':all(math.isfinite(a) for v in m.vertices for a in v.co),'uv_finite':all(math.isfinite(a) for layer in m.uv_layers for item in layer.data for a in item.uv)});ev.to_mesh_clear()
images=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file)} for i in bpy.data.images if i.type=='IMAGE' and i.size[0]>0]
report={'scene_sha256':hashfile(scene),'source_sha256':hashfile(Path(__file__).with_name('assemble.py')),'scene_mesh_curve_triangles':sum(x['triangles'] for x in objects),'finite':all(x['finite'] for x in objects),'uv_finite':all(x['uv_finite'] for x in objects),'degenerate_area_le_1e_12_m2':sum(x['area_le_1e_12_m2'] for x in objects),'per_object_geometry':objects,'packed_images':images,'scope':'static scene/image/GLB integrity, not runtime, collision, camera, topology/manifold or artistic acceptance'}
b=glb.read_bytes();assert b[:4]==b'glTF';n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);report['glb']={'sha256':hashfile(glb),'bytes':len(b),'meshes':len(doc.get('meshes',[])),'materials':len(doc.get('materials',[])),'images':len(doc.get('images',[])),'all_images_embedded':all('bufferView' in i for i in doc.get('images',[])),'no_external_buffers':all('uri' not in x for x in doc.get('buffers',[])),'material_limit':'glTF transfers basecolor/metallic/roughness/imported textures; procedural Blender bump is not baked or transferred'}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));meshes=[o for o in bpy.data.objects if o.type=='MESH'];tri=0
for o in meshes:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
report['glb_reload']={'world_bounds_m':[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]],'objects':len(meshes),'triangles':tri,'finite':all(math.isfinite(a) for o in meshes for v in o.data.vertices for a in v.co)}
assert report['finite'] and report['glb_reload']['finite'] and report['glb']['all_images_embedded']
(E/'saved-readback.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
