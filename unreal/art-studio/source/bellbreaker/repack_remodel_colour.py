"""Final registered atlas refresh and smooth normals correction. Preserve positions, topology, weights and skeleton; re-export FBX/GLB."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
R=Path.cwd();D=R/'artifacts/art/bellbreaker-remodel-20261120/playable';T=R/'artifacts/art/bellfounder-hires-20261120/Bellfounder_BaseColor_4K.png'
bpy.ops.wm.open_mainfile(filepath=str(D/'BellbreakerRemodel.blend'))
m=next(o for o in bpy.context.scene.objects if o.type=='MESH');a=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
def signature():
 h=hashlib.sha256()
 h.update(np.array([v.co[:] for v in m.data.vertices],dtype='<f4').tobytes())
 h.update(np.array([i for p in m.data.polygons for i in p.vertices],dtype='<i4').tobytes())
 h.update(json.dumps([[(g.group,g.weight) for g in v.groups] for v in m.data.vertices]).encode())
 h.update(json.dumps([(b.name,[list(r) for r in b.matrix_local]) for b in a.data.bones]).encode());return h.hexdigest()
before=signature()
normal_before={'smooth_faces':sum(p.use_smooth for p in m.data.polygons),'faces':len(m.data.polygons),'custom_normals':m.data.has_custom_normals}
# Recompute continuous surface normals; intentional plate borders remain sharp.
for poly in m.data.polygons:poly.use_smooth=True
adj={}
for poly in m.data.polygons:
 for key in poly.edge_keys:adj.setdefault(tuple(sorted(key)),[]).append(poly.index)
sharp=0
for edge in m.data.edges:
 ps=adj.get(tuple(sorted(edge.vertices)),[]);hard=False
 if len(ps)==2:
  p0,p1=(m.data.polygons[i] for i in ps)
  hard=(p0.material_index!=p1.material_index) or (p0.material_index==1 and p1.material_index==1 and p0.normal.angle(p1.normal,0)>.75)
 edge.use_edge_sharp=hard;sharp+=hard
if m.data.has_custom_normals:m.data.normals_split_custom_set([(0.,0.,0.)]*len(m.data.loops))
m.data.update();bpy.context.view_layer.update()
normal_after={'smooth_faces':sum(p.use_smooth for p in m.data.polygons),'sharp_edges':sharp,'custom_normals':m.data.has_custom_normals}
new=bpy.data.images.load(str(T),check_existing=False);new.name='Bellfounder_BaseColor_Final4K';new.pack();count=0
for mat in m.data.materials:
 for node in mat.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image and 'BaseColor' in node.image.name:
   node.image=new;count+=1
assert count==2,count
assert before==signature()
for image in list(bpy.data.images):
 if image.users==0:bpy.data.images.remove(image)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'BellbreakerRemodel.blend'))
bpy.ops.object.select_all(action='DESELECT');m.select_set(True);a.select_set(True);bpy.context.view_layer.objects.active=m
bpy.ops.export_scene.fbx(filepath=str(D/'SKM_BellbreakerRemodel.fbx'),use_selection=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE',use_armature_deform_only=False,primary_bone_axis='Y',secondary_bone_axis='X',axis_forward='-Z',axis_up='Y',path_mode='STRIP',embed_textures=False)
bpy.ops.export_scene.gltf(filepath=str(D/'BellbreakerRemodel.glb'),export_format='GLB',use_selection=True,export_animations=False)
(D/'colour-repack.json').write_text(json.dumps({'unchanged_geometry_weights_skeleton_sha256':before,'colour_sha256':hashlib.sha256(T.read_bytes()).hexdigest(),'material_nodes_replaced':count,'fbx_untouched':False,'normals_before':normal_before,'normals_after':normal_after,'change':'Colour+surface normals only; vertexpositions/topology/weights/rest unchanged'},indent=2))
