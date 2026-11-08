"""Lightweight runtime file contract verification, no Blender or Unreal launched."""
import json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];p=R/'unreal/BossLabWarden/Content/BossLab/V13/v13-runtime.json';r=json.loads(p.read_text());rows=[]
for part in r['parts']:
 n=len(part['vertices']);assert len(part['normals'])==len(part['uvs'])==n
 assert all(math.isfinite(v) for field in ['vertices','normals','uvs'] for pt in part[field] for v in pt)
 assert all(len(t)==4 and all(0<=i<n for i in t[:3]) and 0<=t[3]<len(r['materials']) for t in part['triangles'])
 if 'target_child' in part:assert math.sqrt(sum(v*v for v in part['source_axis']))>1
 else:assert part['source_axis']==[0,0,1]
 rows.append({'name':part['name'],'bone':part['bone'],'vertices':n,'triangles':len(part['triangles']),'target_child':part.get('target_child'),'axis_length_cm':math.sqrt(sum(v*v for v in part['source_axis'])),'scale_length':part['scale_length']})
assert sum(x['triangles'] for x in rows)<=120000
assert any(x['name']=='V13_cape' and x['bone']=='spine_05' for x in rows)
a={'schema':r['schema'],'runtime_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parts':rows,'finite_and_indices_pass':True,'triangle_total':sum(x['triangles'] for x in rows),'scope':'JSON integrity/contract only, not Unreal rendering/deformation/performance verification.'}
(R/'artifacts/art/v13-unreal-test-2026-11-08/export-contract-check.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({'parts':len(rows),'triangles':a['triangle_total'],'sha256':a['runtime_sha256'],'passed':True},indent=2))
