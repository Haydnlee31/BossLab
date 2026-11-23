"""Derived DCC(x,y,z)->UE(-x,y,z); frozen author scene remains untouched."""
import bpy,bmesh,json,hashlib,shutil
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a-2026-11-16';P=E/'export';H=E/'pre-x-reflection';H.mkdir(exist_ok=True)
scene=R/'unreal/art-studio/hearth-a-2026-11-16/draft04.blend';before=hashlib.sha256(scene.read_bytes()).hexdigest()
for name in ['pieces.json','layout.json']:
 if not (H/name).exists():shutil.copy2(P/name,H/name)
for name in ['import-report.json','export-audit.json','delivery-manifest.json','readback.json']:
 if (E/name).exists() and not (H/name).exists():shutil.copy2(E/name,H/name)
pieces=json.loads((H/'pieces.json').read_text());layout=json.loads((H/'layout.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(scene));report={}
for name,info in pieces.items():
 o=bpy.data.objects[name];copy=o.copy();copy.data=o.data.copy();bpy.context.scene.collection.objects.link(copy);copy.hide_set(False);copy.hide_render=False;copy.name=name+'_UEHandednessCopy';copy.matrix_world=Matrix.Identity(4)
 # Two reflections give determinant +1: do NOT reverse winding.
 # Discard potentially stale imported custom normals after prior normalization.
 copy.data.normals_split_custom_set([(0,0,0)]*len(copy.data.loops));copy.data.update()
 normal_matrix=Matrix.Diagonal((-1,-1,1));normals=[(normal_matrix@n.vector).normalized() for n in copy.data.corner_normals]
 for vertex in copy.data.vertices:vertex.co=normal_matrix@vertex.co
 copy.data.update();copy.data.normals_split_custom_set(normals)
 normal_error=max(((a.vector-b).length for a,b in zip(copy.data.corner_normals,normals)),default=0)
 bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);bpy.context.view_layer.objects.active=copy
 path=P/(name+'.fbx');oldhash=hashlib.sha256(path.read_bytes()).hexdigest()
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='STRIP',embed_textures=False)
 bpy.data.objects.remove(copy,do_unlink=True)
 lo,hi=info['bounds_m'];info['author_bounds_m']=[lo[:],hi[:]];info['ue_expected_bounds_m']=[[-hi[0],lo[1],lo[2]],[-lo[0],hi[1],hi[2]]]
 report[name]={'before_fbx_sha256':oldhash,'after_fbx_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'transformed_corner_normals':len(normals),'max_corner_normal_readback_error':normal_error,'author_bounds_m':info['author_bounds_m'],'ue_expected_bounds_m':info['ue_expected_bounds_m']}
for instance in layout['instances']:
 instance['location_cm'][0]*=-1;instance['rotation_deg'][1]*=-1
layout['lights'][0].update(intensity_lumens=1600,attenuation_radius_cm=1500)
layout['lights'][1]['location_cm'][1]=1605
for light,radius in zip(layout['lights'][2:],[1000,1000,850]):light['attenuation_radius_cm']=radius
for light in layout['lights']:
 light['location_cm'][0]*=-1
 if 'target_cm' in light:light['target_cm'][0]*=-1
for box in layout.get('camera_collision',[]):box['location_cm'][0]*=-1
layout['axis']='UE coordinates derived from DCC (-x,y,z); +Y rear';layout['coordinate_map']='DCC(x,y,z)->UE(-x,y,z)'
(P/'pieces.json').write_text(json.dumps(pieces,indent=2));(P/'layout.json').write_text(json.dumps(layout,indent=2))
assert hashlib.sha256(scene.read_bytes()).hexdigest()==before
(E/'handedness-export.json').write_text(json.dumps({'source_scene_sha256':before,'source_scene_unchanged':True,'mapping':'DCC(x,y,z)->UE(-x,y,z)','fbx_vertex_map':'(-x,-y,z)','fbx_transform_determinant':1,'winding_reversed':False,'normal_policy':'derived geometry normals recomputed using retained smooth/hard flags, then inverse-transpose XY rotation; source custom normals not trusted','module_reports':report,'limitation':'runtime image validation pending; canonical DCC scene and render coordinates retained'},indent=2))
print('HANDOFF X REFLECTION COMPLETE',len(report))
