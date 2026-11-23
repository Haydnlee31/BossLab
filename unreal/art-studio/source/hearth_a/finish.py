"""Read-only reload verification of canonical selected Hearth A scene."""
import bpy,json,hashlib,math,sys
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a-2026-11-16';D=R/'unreal/art-studio/hearth-a-2026-11-16';P=E/'export'
args=sys.argv[sys.argv.index('--')+1:];scene=D/((args[1] if len(args)>1 else 'draft04')+'.blend')
bpy.ops.wm.open_mainfile(filepath=str(scene));pieces=json.loads((P/'pieces.json').read_text());r={'scope':'saved static module integrity, not manifold, collision or runtime acceptance','scene':str(scene.relative_to(R)),'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'modules':{},'images':[]}
for name,expected in pieces.items():
 o=bpy.data.objects[name];o.data.calc_loop_triangles();pts=[o.matrix_world@v.co for v in o.data.vertices];bounds=[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]
 r['modules'][name]={'triangles':len(o.data.loop_triangles),'area_le_1e_12':sum(t.area<=1e-12 for t in o.data.loop_triangles),'finite':all(all(math.isfinite(x) for x in p) for p in pts),'signed_bound_error_m':max(abs(bounds[j][i]-expected['bounds_m'][j][i]) for j in range(2) for i in range(3)),'materials':[m.name for m in o.data.materials]}
for im in bpy.data.images:
 if im.type=='IMAGE':r['images'].append({'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)})
r['all_modules_match']=all(v['finite'] and v['signed_bound_error_m']<1e-6 and v['triangles']==pieces[k]['triangles'] for k,v in r['modules'].items());r['all_images_packed']=all(v['packed'] for v in r['images']);(E/'readback.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
assert r['all_modules_match'] and r['all_images_packed']
