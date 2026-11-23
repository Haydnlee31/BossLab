"""Enclose the actual projecting window bay; ray check before final three renders."""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';D=R/'unreal/art-studio/hearth-a2-2026-11-16';sys.path.insert(0,str(Path(__file__).parent));from enclosure import close_window_bay
bpy.ops.wm.open_mainfile(filepath=str(D/'assembly07.blend'));S=bpy.context.scene
obs=close_window_bay(bpy.data.materials['weathered masonry 0']);bpy.context.view_layer.update()
# Test actual wall and overhead rays from inside the alcove, rather than image brightness.
checks=[]
for origin,direction in [((12,6,4),(1,-1,0)),((12,7,7),(0,0,1)),((10,10,7.8),(0,0,1))]:
 hit,loc,norm,index,ob,mat=S.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(origin),Vector(direction).normalized());checks.append({'origin_m':origin,'direction':direction,'hit':hit,'object':ob.name if ob else None,'location_m':list(loc) if hit else None})
assert all(x['hit'] for x in checks)
(E/'assembly08-enclosure-readback.json').write_text(json.dumps({'scope':'three static enclosure rays, not global watertight/collision certification','objects':[o.name for o in obs],'checks':checks},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(D/'assembly08.blend'))
for name,eye,target,w,h in [('entry',(-5.8,-9.8,2.8),(-.3,8.5,2.2),1536,630),('gameplay',(-5.5,-8.5,3),(0,4.5,.3),1280,720),('reverse',(3,10,3.2),(0,-4,2.2),1280,720)]:
 S.camera.location=eye;S.camera.rotation_euler=(Vector(target)-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.angle=math.radians(75);S.render.resolution_x=w;S.render.resolution_y=h;S.render.filepath=str(E/('assembly08-'+name+'.png'));bpy.ops.render.render(write_still=True)
