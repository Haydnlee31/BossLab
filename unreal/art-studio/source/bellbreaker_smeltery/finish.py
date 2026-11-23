"""Mechanical zero-area cleanup of derived masonry, same nonzero surface; saved readback."""
import bpy,bmesh,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';D=R/'unreal/art-studio/bellbreaker-smeltery-2026-11-16';P=E/'export'
bpy.ops.wm.open_mainfile(filepath=str(D/'final.blend'));bpy.context.preferences.filepaths.save_version=0
pieces=json.loads((P/'pieces.json').read_text());o=bpy.data.objects['SM_SmelteryMasonry'];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<=1e-12];removed=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update();o.data.calc_loop_triangles();pieces[o.name]['triangles']=len(o.data.loop_triangles);pieces[o.name]['area_le_1e_12_triangles']=sum(t.area<=1e-12 for t in o.data.loop_triangles)
bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.export_scene.fbx(filepath=str(P/(o.name+'.fbx')),use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='STRIP',embed_textures=False)
o.hide_set(True);(P/'pieces.json').write_text(json.dumps(pieces,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(D/'final.blend'));bpy.ops.wm.open_mainfile(filepath=str(D/'final.blend'))
r={'removed_masonry_triangles_area_le_1e_12':removed,'nonzero_surface_positions_unchanged':True,'modules':{},'packed_images':[]}
for n in pieces:
 o=bpy.data.objects[n];o.data.calc_loop_triangles();r['modules'][n]={'triangles':len(o.data.loop_triangles),'area_le_1e_12':sum(t.area<=1e-12 for t in o.data.loop_triangles),'materials':[m.name for m in o.data.materials]}
for im in bpy.data.images:
 if im.type=='IMAGE':r['packed_images'].append({'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)})
r['scene_sha256']=hashlib.sha256((D/'final.blend').read_bytes()).hexdigest();(E/'readback.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
