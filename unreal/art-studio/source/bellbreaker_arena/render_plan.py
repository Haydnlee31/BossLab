"""Annotation-only saved-scene recapture; does not change canonical geometry or save."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];D=R/'unreal/art-studio/bellbreaker-arena-2026-11-16';E=R/'artifacts/art/bellbreaker-arena-2026-11-16';p=D/'final-v3.blend';before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
label=bpy.data.materials.new('legible diagram label');label.use_nodes=True;n=label.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.95,.85,.65,1);em.inputs['Strength'].default_value=1;out=n.new('ShaderNodeOutputMaterial');label.node_tree.links.new(em.outputs[0],out.inputs[0])
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=False
 elif o.name.startswith('PLAN '):o.hide_render=False;o.data.materials.clear();o.data.materials.append(label)
 elif o.type in ['MESH','CURVE']:
  bounds=[o.matrix_world@Vector(v) for v in o.bound_box]
  if min(v.z for v in bounds)>7:o.hide_render=True
s.camera.location=(0,0,55);s.camera.rotation_euler=(Vector((0,0,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=64;s.render.resolution_x=1000;s.render.resolution_y=1200;s.cycles.samples=16
old=E/'final-v3/top-plan.png';old.replace(E/'final-v3/dark-plan-diagnostic.png');s.render.filepath=str(old);bpy.ops.render.render(write_still=True)
assert hashlib.sha256(p.read_bytes()).hexdigest()==before
(E/'plan-recapture.json').write_text(json.dumps({'scene_sha256':before,'geometry_unchanged_saved_scene':True,'changes':'Plan-only: lights kept on; overhead geometry minboundZ>7 hidden; labels emissive. No scene save or architecture edits. Original dark plan retained.'},indent=2))
