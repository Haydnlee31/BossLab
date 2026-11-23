"""Export-only Y reflection compensates measured Blender-FBX→UE Y reflection.
Copies only: positive object transforms, reversed winding, preserved per-loop UVs.
Authored scene and original generated GLBs remain unchanged.
"""
import bpy,bmesh,json,hashlib,shutil
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';P=E/'export';D=R/'unreal/art-studio/bellbreaker-smeltery-2026-11-16';F=E/'failed-y-reflection';F.mkdir(exist_ok=True)
proof=json.loads((E/'import-signed-bounds-before-fix.json').read_text());floor=proof['SM_SmelteryFloor']
assert floor['reflected_y_max_error_cm']<.02 and floor['identity_max_error_cm']>100, 'Actual importer Y reflection must be measured first'
bpy.ops.wm.open_mainfile(filepath=str(D/'final.blend'));parts=json.loads((P/'pieces.json').read_text());rows=[]
for name,p in parts.items():
 old=P/(name+'.fbx')
 if not (F/old.name).exists():shutil.copy2(old,F/old.name)
 src=bpy.data.objects[name];o=src.copy();o.data=src.data.copy();bpy.context.scene.collection.objects.link(o);o.name=name+'_UEAxisCopy';o.hide_set(False);o.hide_render=False;o.matrix_world=Matrix.Identity(4)
 bm=bmesh.new();bm.from_mesh(o.data);bm.transform(Matrix.Diagonal((1,-1,1,1)));bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(old),use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='STRIP',embed_textures=False)
 maxerr=max(abs(o.data.vertices[v.index].co.x-v.co.x)+abs(o.data.vertices[v.index].co.y+v.co.y)+abs(o.data.vertices[v.index].co.z-v.co.z) for v in src.data.vertices)
 rows.append({'module':name,'export_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'copy_coordinate_residual_m':maxerr,'object_determinant':o.matrix_world.determinant(),'vertices':len(o.data.vertices),'uv_layers':[u.name for u in o.data.uv_layers]})
 bpy.data.objects.remove(o,do_unlink=True)
r={'scope':'Measured importer compensation on disposable export copies only','export_transform':'x=x,y=-y,z=z; reverse winding; positive identity object transforms','studio_scene_unchanged':True,'scene_sha256':hashlib.sha256((D/'final.blend').read_bytes()).hexdigest(),'modules':rows};(E/'export-axis-correction.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
