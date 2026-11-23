"""Read-only derived module/layout integrity; not runtime collision validation."""
import json,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a-2026-11-16';P=E/'export'
pieces=json.loads((P/'pieces.json').read_text());layout=json.loads((P/'layout.json').read_text());checks=[]
for instance in layout['instances']:
 name=instance['asset'].split('/')[-1];p=pieces[name];a=math.radians(instance['rotation_deg'][1]);c,s=math.cos(a),math.sin(a);loc=[v/100 for v in instance['location_cm']];lo,hi=p.get('ue_expected_bounds_m',p['bounds_m']);points=[]
 for x in [lo[0],hi[0]]:
  for y in [lo[1],hi[1]]:
   for z in [lo[2],hi[2]]:points.append([x*c-y*s+loc[0],x*s+y*c+loc[1],z+loc[2]])
 low=[min(v[i] for v in points) for i in range(3)];high=[max(v[i] for v in points) for i in range(3)]
 if p['source']=='derived generated prop':checks.append({'name':name,'bounds_m':[low,high],'walk_rectangle_axis_separation_m':max(low[0]-10,-10-high[0],low[1]-12,-12-high[1])})
r={'scope':'Export integrity and conservative full-prop AABB separation, not gameplay/triangle collision certification','unique_triangles':sum(v['triangles'] for v in pieces.values()),'instance_count':len(layout['instances']),'module_count':len(pieces),'generated_prop_bounds':checks,'all_generated_props_clear_0_5m':all(x['walk_rectangle_axis_separation_m']>=.5 for x in checks),'finite':all(v.get('finite_vertices',False) for v in pieces.values()),'area_le_1e_12_triangles':sum(v.get('area_le_1e_12_triangles',0) for v in pieces.values()),'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(P.rglob('*')) if p.is_file()]}
(E/'export-audit.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='files'},indent=2))
