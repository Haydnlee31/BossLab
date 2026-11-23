"""Actual generated-mesh orientation/depth probes, no source-image substitution."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';O=E/'mesh-probes';O.mkdir(exist_ok=True)
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.samples=8;S.cycles.device='CPU';S.cycles.use_denoising=True;S.world.color=(.25,.25,.25);S.render.resolution_x=512;S.render.resolution_y=512;S.render.resolution_percentage=100
report=[]
for p in sorted((E/'generated').glob('*/model.glb')):
 if p.parent.name not in ['great-furnace','forge-toolbench']:continue
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(p));obs=[o for o in bpy.data.objects if o.type=='MESH'];bpy.context.view_layer.update();coords={o:[o.matrix_world@v.co for v in o.data.vertices] for o in obs};vs=[v for a in coords.values() for v in a];lo=Vector([min(v[i] for v in vs) for i in range(3)]);hi=Vector([max(v[i] for v in vs) for i in range(3)]);scale=2.5/(hi.z-lo.z);c=(lo+hi)/2
 for o in obs:
  o.parent=None;o.matrix_world=Matrix.Identity(4)
  for v,co in zip(o.data.vertices,coords[o]):v.co=(co-Vector((c.x,c.y,lo.z)))*scale
 for loc,energy in [((2,-4,5),500),((-3,1,4),400)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.shape='DISK';o.data.size=4;o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();S.camera=bpy.context.object;S.camera.data.type='ORTHO';S.camera.data.ortho_scale=max(3.3,(hi.x-lo.x)*scale*1.25,(hi.y-lo.y)*scale*1.25)
 for label,loc in [('plus-x',(6,0,2.1)),('minus-x',(-6,0,2.1))]:
  S.camera.location=loc;S.camera.rotation_euler=(Vector((0,0,1.25))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(O/(p.parent.name+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
 report.append({'source':str(p.relative_to(R)),'raw_import_bounds':[list(lo),list(hi)],'probe_scale':scale})
(O/'readback.json').write_text(json.dumps(report,indent=2))
