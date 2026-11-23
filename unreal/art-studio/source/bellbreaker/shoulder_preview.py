from pathlib import Path
import bpy,numpy as np,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[4];O=R/'artifacts/art/bellbreaker-shoulder-2026-11-20'
p=np.load(O/'measured-pose.npz');v=p['vertices'];f=p['faces'];w=p['weights'];m=p['matrix'];r=np.c_[v*[1,-1,1],np.ones(len(v))]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.resolution_x=720;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.world=bpy.data.worlds.new('Neutral');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
mat=bpy.data.materials.new('Clay');mat.diffuse_color=(.38,.42,.46,1);mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.65
mesh=bpy.data.meshes.new('Same92450Triangles');mesh.from_pydata(v.tolist(),[],f.tolist());mesh.update();ob=bpy.data.objects.new('MeasuredPoseSurface',mesh);sc.collection.objects.link(ob);ob.data.materials.append(mat)
for poly in mesh.polygons:poly.use_smooth=True
for loc,power,size in [((1,-3,4),500,3),((-3,0,3),350,3)]:
 d=bpy.data.lights.new('Softbox','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new('Softbox',d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1.4))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Diagnostic');co=bpy.data.objects.new('Diagnostic',c);sc.collection.objects.link(co);sc.camera=co;c.type='ORTHO';c.ortho_scale=1.1
for label,q in [('baseline',w),('diffusion20',np.load(O/'weights-diffuse-20.npy')),('anatomy',np.load(O/'weights-anatomy.npy'))]:
 sk=sum(q[:,j,None]*(r@m[j]) for j in range(len(q[0])))/[100,-100,100]
 for vert,pos in zip(mesh.vertices,sk):vert.co=pos
 mesh.update()
 for view,loc in [('front',(0,-4,1.5)),('oblique',(3,-4,1.8))]:
  co.location=loc;co.rotation_euler=(Vector((0,0,1.42))-co.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(O/f'{label}-{view}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'diagnostic.blend'))
