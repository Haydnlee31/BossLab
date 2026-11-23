"""Confirm reverse pixels and close only missing entry-side returns. No layout change."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';D=R/'unreal/art-studio/hearth-a2-2026-11-16'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];base=args[1] if len(args)>1 else 'assembly08'
bpy.ops.wm.open_mainfile(filepath=str(D/(base+'.blend')));S=bpy.context.scene;camera=S.camera;camera.location=(3,10,3.2);camera.rotation_euler=(Vector((0,-4,2.2))-camera.location).to_track_quat('-Z','Y').to_euler();S.render.resolution_x=1280;S.render.resolution_y=720;bpy.context.view_layer.update()
def rays():
 frame=camera.data.view_frame(scene=S);xmin=min(v.x for v in frame);xmax=max(v.x for v in frame);ymin=min(v.y for v in frame);ymax=max(v.y for v in frame);result=[]
 for px,py in [(30,120),(65,110),(80,145),(10,90)]:
  direction=camera.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*px/1280,ymax-(ymax-ymin)*py/720,frame[0].z));hit,loc,norm,idx,ob,mat=S.ray_cast(bpy.context.evaluated_depsgraph_get(),camera.location,direction.normalized());result.append({'pixel':[px,py],'hit':hit,'object':ob.name if ob else None,'world_m':list(loc) if hit else None,'direction':list(direction.normalized())})
 return result
before=rays();added=[]
if any(not v['hit'] for v in before):
 for name,loc,dimensions in [('entry side closure left',(-11.2,-13,4.25),(.9,2.8,8.5)),('entry side closure right',(11.2,-13,4.25),(.9,2.8,8.5)),('right raised-vault wall closure',(11.2,-5.5,7.35),(.9,17,2.3))]:
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(bpy.data.materials['weathered masonry 0']);ob['hearth_a2_group']='masonry';uv=ob.data.uv_layers.active
  for poly in ob.data.polygons:
   axes=(0,1) if abs(poly.normal.z)>.6 else (0,2) if abs(poly.normal.y)>.6 else (1,2)
   for li in poly.loop_indices:
    co=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/4,co[axes[1]]/4)
  added.append(ob.name)
bpy.context.view_layer.update();after=rays();(E/'final-return-diagnostic.json').write_text(json.dumps({'before':before,'after':after},indent=2));assert all(v['hit'] for v in after)
camera.location=(-5.8,-9.8,2.8);camera.rotation_euler=(Vector((-.3,8.5,2.2))-camera.location).to_track_quat('-Z','Y').to_euler();S.render.resolution_x=1536;S.render.resolution_y=630
bpy.ops.wm.save_as_mainfile(filepath=str(D/'final.blend'))
(E/'final-return-readback.json').write_text(json.dumps({'before':before,'after':after,'added_objects':added,'scope':'four reverse-view pixel rays only; no global collision claim','final_scene_sha256':hashlib.sha256((D/'final.blend').read_bytes()).hexdigest(),'evidence_scope':'assembly08 three views precede these entry-side closures only; final-reverse proves corrected area'},indent=2))
camera.location=(3,10,3.2);camera.rotation_euler=(Vector((0,-4,2.2))-camera.location).to_track_quat('-Z','Y').to_euler();S.render.resolution_x=960;S.render.resolution_y=540;S.cycles.samples=8;S.render.filepath=str(E/'final-reverse.png');bpy.ops.render.render(write_still=True)
