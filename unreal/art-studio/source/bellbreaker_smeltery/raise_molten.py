"""Raise only low channel/basin vertices; preserve ember beds and all other modules."""
import bpy,bmesh,json,hashlib,struct,shutil
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';P=E/'export';D=R/'unreal/art-studio/bellbreaker-smeltery-2026-11-16';F=E/'pre-molten-height';F.mkdir(exist_ok=True)
for n in ['readback.json','export-audit.json','import-report.json','dcc-delivery-manifest.json','export-axis-correction.json']:
 if (E/n).exists() and not (F/n).exists():shutil.copy2(E/n,F/n)
for n in ['SM_SmelteryMolten.fbx','pieces.json','layout.json']:
 if not (F/n).exists():shutil.copy2(P/n,F/n)
def digest(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:
  h.update(struct.pack('<I',p.material_index));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices))
 return h.hexdigest()
before_scene=hashlib.sha256((D/'final.blend').read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(D/'final.blend'));bpy.context.preferences.filepaths.save_version=0
parts=json.loads((P/'pieces.json').read_text());before={n:digest(bpy.data.objects[n]) for n in parts};o=bpy.data.objects['SM_SmelteryMolten'];changed=[];embers=[]
for v in o.data.vertices:
 if v.co.z<.1:changed.append({'index':v.index,'before_z':float(v.co.z)});v.co.z+=.2825
 else:embers.append((v.index,tuple(v.co)))
assert len(changed)==24,'Only three original channel/basin boxes expected'
o.data.update();o.data.calc_loop_triangles();lo=[min(v.co[i] for v in o.data.vertices) for i in range(3)];hi=[max(v.co[i] for v in o.data.vertices) for i in range(3)];parts[o.name]['bounds_m']=[lo,hi];parts[o.name]['size_m']=[hi[i]-lo[i] for i in range(3)]
source=o;copy=o.copy();copy.data=o.data.copy();bpy.context.scene.collection.objects.link(copy);copy.name='SM_SmelteryMolten_UEAxisCopy';copy.hide_set(False);copy.matrix_world=Matrix.Identity(4)
bm=bmesh.new();bm.from_mesh(copy.data);bm.transform(Matrix.Diagonal((1,-1,1,1)));bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(copy.data);bm.free();copy.data.update()
bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);bpy.context.view_layer.objects.active=copy
bpy.ops.export_scene.fbx(filepath=str(P/'SM_SmelteryMolten.fbx'),use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='STRIP',embed_textures=False)
bpy.data.objects.remove(copy,do_unlink=True);(P/'pieces.json').write_text(json.dumps(parts,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(D/'final.blend'));bpy.ops.wm.open_mainfile(filepath=str(D/'final.blend'))
after={n:digest(bpy.data.objects[n]) for n in parts};assert all(before[n]==after[n] for n in parts if n!='SM_SmelteryMolten')
o=bpy.data.objects['SM_SmelteryMolten'];assert all(tuple(o.data.vertices[i].co)==v for i,v in embers)
zs=[o.data.vertices[v['index']].co.z for v in changed]
r={'scope':'Readback of low channel/receiving basin height only, no geometry/material/light redesign','changed_vertex_count':len(changed),'changed_vertices':changed,'delta_z_m':.2825,'surface_z_range_m':[min(zs),max(zs)],'side_coping_top_m':.5,'minimum_side_coping_above_surface_m':.5-max(zs),'ember_vertex_count_unchanged':len(embers),'all_other_module_geometry_material_indices_unchanged':True,'before_module_digests':before,'after_module_digests':after,'before_scene_sha256':before_scene,'scene_sha256':hashlib.sha256((D/'final.blend').read_bytes()).hexdigest(),'molten_fbx_sha256':hashlib.sha256((P/'SM_SmelteryMolten.fbx').read_bytes()).hexdigest(),'export_basis':'Y reflected copy, winding reversed, positive identity transform'}
(E/'molten-height-audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
