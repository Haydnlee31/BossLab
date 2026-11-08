import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];D=R/'unreal/art-studio/revision-v5-2026-11-07';E=R/'artifacts/art/last-vigil-v5'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(D/'last-vigil-v5.blend'),link=False) as (a,b):
 b.objects=[n for n in a.objects if n=='Padded arming doublet' or n.startswith('V4 | articulated gorget') or n.startswith('FOCAL | ') and any(t in n for t in ['skull','visor','occiput','crown','neck','eye'])]
for ob in b.objects:
 if ob:bpy.context.collection.objects.link(ob);ob.parent=None
S=bpy.context.scene;S.view_layers[0].update();result=[]
for y in [-.025,0,.025,.05,.075]:
 for z in [1.635,1.65,1.665]:
  hit,loc,n,idx,ob,mat=S.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((-1,y,z)),Vector((1,0,0)))
  result.append({'ray_y':y,'ray_z':z,'object':ob.name if hit else None,'location':list(loc) if hit else None,'materials':[m.name for m in ob.data.materials if m] if hit else []})
(E/'neck-fit-probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
