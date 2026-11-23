import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a-2026-11-16';D=R/'unreal/art-studio/hearth-a-2026-11-16';bpy.ops.wm.open_mainfile(filepath=str(D/'draft02.blend'));S=bpy.context.scene;cam=S.camera;dg=bpy.context.evaluated_depsgraph_get();w=math.tan(cam.data.angle_x/2);h=w*900/1400;rows=[]
for px,py in [(410,667),(430,665),(420,675),(450,655),(500,667),(600,667)]:
 d=cam.matrix_world.to_quaternion()@Vector(((px/1400-.5)*2*w,(.5-py/900)*2*h,-1));hit,loc,n,idx,obj,matrix=S.ray_cast(dg,cam.location,d.normalized());r={'pixel':[px,py],'hit':hit}
 if hit:r.update(object=obj.name,location=list(loc),normal=list(n),face=idx,material=obj.data.materials[obj.data.polygons[idx].material_index].name)
 rows.append(r)
(E/'floor-patch-diagnosis.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
