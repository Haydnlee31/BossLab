"""Complete only the entry wall's hidden structural backing; no new art layout."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';D=R/'unreal/art-studio/hearth-a2-2026-11-16'
bpy.ops.wm.open_mainfile(filepath=str(D/'assembly06.blend'));S=bpy.context.scene;o=bpy.data.objects['entry continuous backing'];before={'location':list(o.location),'dimensions':list(o.dimensions)}
o.location.z=6
for v in o.data.vertices:v.co.z*=12/9.6
bpy.context.view_layer.update();after={'location':list(o.location),'dimensions':list(o.dimensions)}
bpy.ops.wm.save_as_mainfile(filepath=str(D/'assembly07.blend'))
(E/'assembly07-construction-receipt.json').write_text(json.dumps({'change':'extend continuous entry backing above vault crown; foreground geometry and materials unchanged','object':o.name,'before':before,'after':after,'source_previous_sha256':hashlib.sha256((D/'assembly06.blend').read_bytes()).hexdigest()},indent=2))
for name,eye,target,w,h in [('entry',(-5.8,-9.8,2.8),(-.3,8.5,2.2),1536,630),('gameplay',(-5.5,-8.5,3),(0,4.5,.3),1280,720),('reverse',(3,10,3.2),(0,-4,2.2),1280,720)]:
 S.camera.location=eye;S.camera.rotation_euler=(Vector(target)-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.angle=math.radians(75);S.render.resolution_x=w;S.render.resolution_y=h;S.render.filepath=str(E/('assembly07-'+name+'.png'));bpy.ops.render.render(write_still=True)
