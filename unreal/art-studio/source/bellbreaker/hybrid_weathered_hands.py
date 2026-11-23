"""Optional sibling: retain generated body, replace rejected hands with functional donor gloves.
Original ForgeSkin geometry/weights under concealed cuff seam; no runtime skeleton changes.
"""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path.cwd();D=R/'artifacts/unreal/bellbreaker-refit-20261120/sculpt/weathered';F=D/'fit'
bpy.ops.wm.open_mainfile(filepath=str(F/'weathered.blend'))
a=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');body=next(o for o in bpy.context.scene.objects if o.type=='MESH')
rest={b.name:b.matrix_local.copy() for b in a.data.bones};order=list(rest)
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(R/'artifacts/unreal/bellbreaker-dialogue/SKM_BellbreakerForgeSkin.fbx'),use_anim=False,automatic_bone_orientation=False,ignore_leaf_bones=False)
added=[o for o in bpy.data.objects if o not in before];donor=max((o for o in added if o.type=='MESH'),key=lambda o:len(o.data.vertices));da=next(o for o in added if o.type=='ARMATURE')
frames={}
for side in ['l','r']:
 w=a.matrix_world@a.data.bones['hand_'+side].head_local
 f=(a.matrix_world@a.data.bones['middle_01_'+side].head_local-w).normalized()
 frames[side]=(w,f)
def region(p,back):
 return any((p-w).dot(f)>back and (p-w).length<.24 and abs(p.x)>.37 for w,f in frames.values())
# Remove failed generated palm/finger skin, including thin high-weight wrist bridges.
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table()
names={g.index:g.name for g in body.vertex_groups}
remove=[]
for v in body.data.vertices:
 p=body.matrix_world@v.co
 handweight=sum(g.weight for g in v.groups if names[g.group].startswith(('hand_','thumb_','index_','middle_','ring_','pinky_')))
 armweight=sum(g.weight for g in v.groups if names[g.group].startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')))
 if (region(p,-.035) and armweight>.5) or (handweight>.20 and abs(p.x)>.37):remove.append(bm.verts[v.index])
bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(body.data);bm.free()
# Copy donor geometry only distal to wrist/cuff plane; keep original full weight data.
verts=[donor.matrix_world@v.co for v in donor.data.vertices]
dn={g.index:g.name for g in donor.vertex_groups}
keep={i for i,p in enumerate(verts) if region(p,-.050) and sum(g.weight for g in donor.data.vertices[i].groups if dn[g.group].startswith(('lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_')))>.5}
source_faces=[p for p in donor.data.polygons if all(i in keep for i in p.vertices)]
faces=[list(p.vertices) for p in source_faces]
used=sorted({i for face in faces for i in face});lookup={i:k for k,i in enumerate(used)}
me=bpy.data.meshes.new('FunctionalSmithGloves');me.from_pydata([verts[i] for i in used],[],[[lookup[i] for i in face] for face in faces]);me.update()
glove=bpy.data.objects.new('FunctionalSmithGloves',me);bpy.context.collection.objects.link(glove)
for g in donor.vertex_groups:glove.vertex_groups.new(name=g.name)
for old,new in lookup.items():
 for g in donor.data.vertices[old].groups:glove.vertex_groups[g.group].add([new],g.weight,'REPLACE')
for p in me.polygons:p.use_smooth=True
mat=bpy.data.materials.new('SmithGlove');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.055,.032,.019,1);bs.inputs['Roughness'].default_value=.56
# Preserve original donor UVs and original colour atlas as leather-colour source.
uv=me.uv_layers.new(name=body.data.uv_layers.active.name)
for dstpoly,srcpoly in zip(me.polygons,source_faces):
 for dl,sl in zip(dstpoly.loop_indices,srcpoly.loop_indices): uv.data[dl].uv=donor.data.uv_layers.active.data[sl].uv
sourceimage=None
for material in donor.data.materials:
 if material and material.use_nodes:
  for node in material.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.image and ('BaseColor' in node.image.name or 'BaseColor' in node.image.filepath):sourceimage=node.image;break
 if sourceimage:break
sourceimage=bpy.data.images.load(str(R/'artifacts/art/bellbreaker-boss-2026-11-18/rig-v3/out/SKM_BellbreakerRig_BaseColor.png'),check_existing=False)
if sourceimage:
 import shutil
 shutil.copy2(R/'artifacts/art/bellbreaker-boss-2026-11-18/rig-v3/out/SKM_BellbreakerRig_BaseColor.png',F/'SKM_BellbreakerWeathered_GloveBaseColor.png')
 sourceimage.pack()
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=sourceimage
 mix=mat.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.34,.26,.20,1)
 mat.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);mat.node_tree.links.new(mix.outputs[0],bs.inputs['Base Color'])
me.materials.append(mat)
# Concealed flexible leather wrist sleeve bridges generated cuff and donor palm.
vv=[];ff=[];sleeveweights=[]
for side in ['l','r']:
 w,forward=frames[side]; elbow=a.matrix_world@a.data.bones['lowerarm_'+side].head_local
 back=(elbow-w).normalized();axis=forward;u=axis.cross(Vector((0,1,0))).normalized();v=axis.cross(u).normalized()
 start=len(vv)
 for j,t in enumerate([-.075,-.05,-.025,0,.025]):
  centre=w+back*(-t) if t<0 else w+forward*t
  r=[.058,.054,.047,.044,.046][j]
  for k in range(24):
   ang=k*2*math.pi/24;vv.append(centre+u*(math.cos(ang)*r)+v*(math.sin(ang)*r*.8));sleeveweights.append((side,max(0,min(1,(t+.075)/.1))))
 for j in range(4):
  for k in range(24):ff.append((start+j*24+k,start+j*24+(k+1)%24,start+(j+1)*24+(k+1)%24,start+(j+1)*24+k))
wm=bpy.data.meshes.new('LeatherWristSleeves');wm.from_pydata(vv,[],ff);wm.update();wo=bpy.data.objects.new('LeatherWristSleeves',wm);bpy.context.collection.objects.link(wo)
for side in ['l','r']:
 for stem in ['hand_','lowerarm_']:wo.vertex_groups.new(name=stem+side)
for i,(side,wgt) in enumerate(sleeveweights):
 wo.vertex_groups['hand_'+side].add([i],wgt,'REPLACE');wo.vertex_groups['lowerarm_'+side].add([i],1-wgt,'REPLACE')
wm.uv_layers.new(name=body.data.uv_layers.active.name)
wm.materials.append(mat.copy());wm.materials[0].name='SmithWrist';wbs=wm.materials[0].node_tree.nodes['Principled BSDF']
for link in list(wbs.inputs['Base Color'].links):wm.materials[0].node_tree.links.remove(link)
wbs.inputs['Base Color'].default_value=(.055,.032,.019,1)
for poly in wm.polygons:poly.use_smooth=True
wo.modifiers.new('RuntimeSkeleton','ARMATURE').object=a

glove.modifiers.new('RuntimeSkeleton','ARMATURE').object=a
# Join while preserving donor weights and independent material slot.
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);glove.select_set(True);wo.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.object.join()
for o in added:
 if o.name in bpy.data.objects:bpy.data.objects.remove(o,do_unlink=True)
assert [b.name for b in a.data.bones]==order
error=max(max(abs(b.matrix_local[i][j]-rest[b.name][i][j]) for i in range(4) for j in range(4)) for b in a.data.bones)
assert error==0
bpy.ops.wm.save_as_mainfile(filepath=str(F/'weathered-hybrid.blend'))
bpy.ops.object.select_all(action='DESELECT');body.select_set(True);a.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.export_scene.fbx(filepath=str(F/'SKM_BellbreakerWeathered.fbx'),use_selection=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE',use_armature_deform_only=False,primary_bone_axis='Y',secondary_bone_axis='X',axis_forward='-Z',axis_up='Y',path_mode='STRIP',embed_textures=False)
report={'generated_vertices_removed':len(remove),'donor_vertices':len(used),'donor_faces':len(faces),'original_rest_max_error':error,'triangles':sum(len(p.vertices)-2 for p in body.data.polygons),'slots':[m.name for m in body.data.materials],'method':'Original ForgeSkin hand geometry and weights, dark leather material, seam beneath generated cuff; actual grip not yet tested'}
(F/'hybrid-hands.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
