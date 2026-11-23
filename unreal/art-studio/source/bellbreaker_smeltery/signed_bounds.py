"""Read-only saved Unreal signed bounds; diagnose FBX axis mapping."""
import unreal,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';parts=json.loads((E/'export/pieces.json').read_text());rows={}
for n,p in parts.items():
 m=unreal.load_asset('/Game/BossLab/Smeltery/'+n)
 if not m:continue
 b=m.get_bounding_box();lo=[b.min.x,b.min.y,b.min.z];hi=[b.max.x,b.max.y,b.max.z];ex=[[x*100 for x in q] for q in p['bounds_m']]
 rows[n]={'min_cm':lo,'max_cm':hi,'source_min_cm':ex[0],'source_max_cm':ex[1],'identity_max_error_cm':max(abs(a-b) for q,w in zip([lo,hi],ex) for a,b in zip(q,w)),'reflected_y_max_error_cm':max(abs(a-b) for q,w in zip([lo,hi],[[ex[0][0],-ex[1][1],ex[0][2]],[ex[1][0],-ex[0][1],ex[1][2]]]) for a,b in zip(q,w))}
p=E/'import-signed-bounds-before-fix.json';p.write_text(json.dumps(rows,indent=2));unreal.log(json.dumps(rows));unreal.SystemLibrary.quit_editor()
