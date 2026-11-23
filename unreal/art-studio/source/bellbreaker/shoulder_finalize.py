"""Save editable imported weighted rig plus same-triangle measured-pose clay proof."""
from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[4];O=R/'artifacts/art/bellbreaker-shoulder-2026-11-20';p=np.load(O/'measured-pose.npz');v=p['vertices'];f=p['faces'];w=p['weights'];m=p['matrix'];r=np.c_[v*[1,-1,1],np.ones(len(v))]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(O/'SKM_BellbreakerForgeShoulder.fbx'),use_anim=False)
arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
rig_objects=list(bpy.context.scene.objects)
audit={'imported_objects':[{'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None} for o in rig_objects],'bone_count':len(arm.data.bones),'armature_modifiers':[{'object':o.name,'target':a.object.name if a.object else None} for o in rig_objects for a in o.modifiers if a.type=='ARMATURE'],'pose':'saved armature remains in rest pose; diagnostic meshes use recorded-pose linear skin palette, not animation clips'}
tex=R/'artifacts/art/bellbreaker-boss-2026-11-18/rig-v3/out'
for im in bpy.data.images:
 name=Path(im.filepath).name
 candidate=tex/name
 if candidate.exists():im.filepath=str(candidate);im.reload()
 try:im.pack()
 except RuntimeError:pass
for o in rig_objects:o.hide_render=True
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=720;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('Neutral');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.3
mat=bpy.data.materials.new('DiagnosticClay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.28,.33,.38,1);bs.inputs['Roughness'].default_value=.65
mesh=bpy.data.meshes.new('Same92450Triangles');mesh.from_pydata(v.tolist(),[],f.tolist());mesh.update();ob=bpy.data.objects.new('RecordedPoseDiagnostic',mesh);sc.collection.objects.link(ob);ob.data.materials.append(mat)
for poly in mesh.polygons:poly.use_smooth=True
for loc,power,size in [((1,-3,4),300,3),((-3,0,3),150,3)]:
 d=bpy.data.lights.new('Softbox','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new('Softbox',d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Diagnostic');co=bpy.data.objects.new('Diagnostic',c);sc.collection.objects.link(co);sc.camera=co;c.type='ORTHO';c.ortho_scale=1.1
for label,q in [('final-before',w),('final-after',np.load(O/'weights-constrained.npy'))]:
 sk=sum(q[:,j,None]*(r@m[j]) for j in range(len(q[0])))/[100,-100,100]
 for vert,pos in zip(mesh.vertices,sk):vert.co=pos
 mesh.update()
 for view,loc in [('front',(0,-4,1.5)),('oblique',(3,-4,1.8))]:
  co.location=loc;co.rotation_euler=(Vector((0,0,1.42))-co.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(O/f'{label}-{view}.png');bpy.ops.render.render(write_still=True)
ob.hide_render=True;ob.hide_set(True)
for o in rig_objects:o.hide_render=False
bpy.context.preferences.filepaths.save_version=0
blend=O/'ForgeShoulder.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.wm.open_mainfile(filepath=str(blend));audit['saved_scene_reload']=True;audit['images']=[{'name':im.name,'packed':bool(im.packed_file),'filepath':im.filepath} for im in bpy.data.images];audit['scene_sha256']=hashlib.sha256(blend.read_bytes()).hexdigest();audit['fbx_sha256']=hashlib.sha256((O/'SKM_BellbreakerForgeShoulder.fbx').read_bytes()).hexdigest();(O/'blender-readback.json').write_text(json.dumps(audit,indent=2))
