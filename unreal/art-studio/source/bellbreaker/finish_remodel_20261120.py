"""Four-view remodel: authored hard/soft binding, packed registered maps, exact existing skeleton.
Finite isolated DCC delivery, never writes Unreal packages or gameplay code.
"""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path.cwd();D=R/'artifacts/art/bellbreaker-remodel-20261120/playable';T=R/'artifacts/art/bellfounder-hires-20261120'
bpy.ops.wm.open_mainfile(filepath=str(D/'body-fit.blend'))
a=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');m=next(o for o in bpy.context.scene.objects if o.type=='MESH')
rest={b.name:b.matrix_local.copy() for b in a.data.bones};order=list(rest)
# Materials preserve the original four-tile UV layout; surface maps are authored estimates.
imgs={n:bpy.data.images.load(str(T/f'Bellfounder_{n}_4K.png'),check_existing=False) for n in ['BaseColor','ORM','Normal']}
for n in ['ORM','Normal']:imgs[n].colorspace_settings.name='Non-Color'
for im in imgs.values():im.pack()
def material(name):
 mat=bpy.data.materials.new(name);mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
 tex={n:nt.nodes.new('ShaderNodeTexImage') for n in imgs}
 for n,node in tex.items():node.image=imgs[n]
 nt.links.new(tex['BaseColor'].outputs['Color'],bs.inputs['Base Color'])
 sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(tex['ORM'].outputs['Color'],sep.inputs[0])
 nt.links.new(sep.outputs['Green'],bs.inputs['Roughness']);nt.links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
 normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55;nt.links.new(tex['Normal'].outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
 return mat
m.data.materials.clear()
for name in ['RemodelBody','RemodelHardplate']:m.data.materials.append(material(name))
# Arm and cuff ownership follows the calibrated existing skeleton.
vg={g.name:g for g in m.vertex_groups};verts=np.array([m.matrix_world@v.co for v in m.data.vertices])
hard=np.zeros(len(verts),bool);counts={}
def assign(i,weights):
 for group_index in [int(g.group) for g in m.data.vertices[i].groups]:m.vertex_groups[group_index].remove([i])
 for name,value in weights.items():
  if name not in vg:vg[name]=m.vertex_groups.new(name=name)
  if value>0:vg[name].add([i],float(value),'REPLACE')
for side,sign in [('l',1),('r',-1)]:
 elbow=np.array(a.matrix_world@a.data.bones['lowerarm_'+side].head_local);wrist=np.array(a.matrix_world@a.data.bones['hand_'+side].head_local)
 axis=wrist-elbow;u=((verts-elbow)@axis)/(axis@axis);rad=np.linalg.norm(verts-elbow-u[:,None]*axis,axis=1)
 # Central bracer field is rigid. Soft skin around elbow/wrist retains existing blended weights.
 sel=np.where((u>.18)&(u<.68)&(rad>.055)&(rad<.16)&(verts[:,0]*sign>.27))[0]
 for i in sel:assign(int(i),{'lowerarm_'+side:1});hard[i]=True
 counts['rigid_bracer_'+side]=len(sel)
# Raised metal shoulder shell on the left, kept clear of inner axilla.
sel=np.where((verts[:,0]>.18)&(verts[:,0]<.43)&(verts[:,2]>1.39)&(verts[:,2]<1.59)&(verts[:,1]>-.20)&(verts[:,1]<.17))[0]
for i in sel:assign(int(i),{'upperarm_l':1});hard[i]=True
counts['left_shell_vertices']=len(sel)
# Anatomical palm stays coherent; distal digit weights remain independently articulated.
for side,sign in [('l',1),('r',-1)]:
 wrist=np.array(a.matrix_world@a.data.bones['hand_'+side].head_local);middle=np.array(a.matrix_world@a.data.bones['middle_01_'+side].head_local);axis=middle-wrist;L=np.linalg.norm(axis);axis/=L
 along=(verts-wrist)@axis;rad=np.linalg.norm(verts-wrist-along[:,None]*axis,axis=1)
 sel=np.where((along>-.012)&(along<L*.6)&(rad<.075)&(verts[:,0]*sign>.4))[0]
 for i in sel:assign(int(i),{'hand_'+side:1})
 counts['coherent_palm_'+side]=len(sel)
# Numerical skin gate before any export.
sums=[sum(g.weight for g in v.groups) for v in m.data.vertices]
assert max(abs(x-1) for x in sums)<1e-5, (min(sums),max(sums))
assert max(len(v.groups) for v in m.data.vertices)<=4
for p in m.data.polygons:p.material_index=int(sum(hard[i] for i in p.vertices)>=len(p.vertices)*.75)
# Verify original rest data hasn't been altered by weighting/construction.
assert [b.name for b in a.data.bones]==order
err=max(max(abs(b.matrix_local[i][j]-rest[b.name][i][j]) for i in range(4) for j in range(4)) for b in a.data.bones);assert err==0
# Actual captured Quake palette: sampled runtime pose, not a fabricated animation.
P=np.load(R/'artifacts/art/bellbreaker-shoulder-2026-11-20/measured-pose.npz');pn=list(P['names']);pm={n:i for i,n in enumerate(pn)}
W=np.zeros((len(verts),len(pn)));missing={}
for v in m.data.vertices:
 for g in v.groups:
  n=m.vertex_groups[g.group].name
  if n in pm:W[v.index,pm[n]]+=g.weight
  elif g.weight>1e-6:missing[n]=missing.get(n,0)+1
assert not missing,missing
vh=np.c_[verts[:,0],-verts[:,1],verts[:,2],np.ones(len(verts))]
posed=np.einsum('vj,vk,jkl->vl',W,vh,P['matrix'])/np.array([100,-100,100])
# Export a separate actual-palette deformed preview mesh after the rigged final is saved.
report={'triangles':sum(len(p.vertices)-2 for p in m.data.polygons),'vertices':len(verts),'weight_sum_min':min(sums),'weight_sum_max':max(sums),'original_rest_max_error':err,'bone_order_preserved':True,'slots':[x.name for x in m.data.materials],'region_counts':counts,'missing_palette_groups':missing,'hand_method':'Native four-view hand geometry; coherent hand-owned palm, separate original finger groups retained','material_limit':'Registered illustrated colour, estimated ORM and colour-derived tangent microrelief; not scanned PBR'}
(D/'remodel-report.json').write_text(json.dumps(report,indent=2))
for o in bpy.context.scene.objects:o.select_set(False)
m.select_set(True);a.select_set(True);bpy.context.view_layer.objects.active=m
bpy.ops.wm.save_as_mainfile(filepath=str(D/'BellbreakerRemodel.blend'))
bpy.ops.export_scene.fbx(filepath=str(D/'SKM_BellbreakerRemodel.fbx'),use_selection=True,add_leaf_bones=False,bake_anim=False,mesh_smooth_type='FACE',use_armature_deform_only=False,primary_bone_axis='Y',secondary_bone_axis='X',axis_forward='-Z',axis_up='Y',path_mode='STRIP',embed_textures=False)
bpy.ops.export_scene.gltf(filepath=str(D/'BellbreakerRemodel.glb'),export_format='GLB',use_selection=True,export_animations=False)
np.savez_compressed(D/'captured-quake-vertices.npz',rest=verts,posed=posed,weights=W,names=P['names'])
preview=m.copy();preview.data=m.data.copy();preview.name='ActualCapturedQuake';bpy.context.collection.objects.link(preview)
preview.parent=None;preview.matrix_world=Matrix.Identity(4)
for mod in list(preview.modifiers):preview.modifiers.remove(mod)
for v,p in zip(preview.data.vertices,posed):v.co=p
m.hide_render=True;a.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(D/'captured-quake-preview.blend'))
print(json.dumps(report))
