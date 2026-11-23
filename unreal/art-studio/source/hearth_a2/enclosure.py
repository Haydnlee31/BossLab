"""Physical return and ceiling for the angled window alcove beyond the main vault."""
import bpy,math
from mathutils import Vector

def close_window_bay(material):
 obs=[]
 def solid(name,ring,z0,z1):
  vs=[(x,y,z) for z in [z0,z1] for x,y in ring];n=len(ring);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(material);ob['hearth_a2_group']='masonry';uv=me.uv_layers.new(name='physical metre mapping')
  for p in me.polygons:
   axes=(0,1) if abs(p.normal.z)>.6 else (0,2) if abs(p.normal.y)>.6 else (1,2)
   for li in p.loop_indices:
    co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/4,co[axes[1]]/4)
  obs.append(ob);return ob
 a=Vector((11.0,3.05));b=Vector((14.95,5.0));v=(b-a).normalized();n=Vector((-v.y,v.x))*.24
 solid('window bay closed gallery return',[a-n,b-n,b+n,a+n],0,8.55)
 solid('window bay supported ceiling',[(9.8,3.0),(15.2,4.9),(15.2,12.1),(7.0,12.1)],8.15,8.55)
 return obs
