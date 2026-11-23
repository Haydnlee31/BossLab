"""Lightweight canonical handoff hashes and owner-authorized latest-two A2 retention."""
import json,hashlib,struct,time
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';D=R/'unreal/art-studio/hearth-a2-2026-11-16';P=E/'export';src=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=json.loads((E/'export-readback.json').read_text());assert read['source_scene_sha256']==sha(D/'final.blend')
for name in ['entry','gameplay','reverse']:
 p=E/('assembly08-'+name+'.png');assert p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
for p in (P/'textures').glob('*.png'):assert p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
removed=[]
for p in sorted(D.glob('*.blend*')):
 if p.name in ['assembly08.blend','final.blend']:continue
 removed.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)});p.unlink()
(E/'scene-retention.json').write_text(json.dumps({'authority':'owner/parent latest-two meaningful A2 scenes; old Hearth A and all other lines untouched','kept':['assembly08.blend','final.blend'],'removed':removed,'bytes_reclaimed':sum(x['bytes'] for x in removed),'retained_evidence':'all previous images, logs and timestamped source snapshots'},indent=2))
files=list(src.glob('*.py'))+[src/'assets.json',D/'final.blend']+[E/('assembly08-'+n+'.png') for n in ['entry','gameplay']]+[E/'final-reverse.png',E/'final-return-readback.json',E/'final_returns-process.json']+[E/n for n in ['export-readback.json','assembly08-enclosure-readback.json','assembly08-process.json','export-process.json','texture-encoding-correction.json','floor-shader-contract.json','asset-fit.json','scene-retention.json','INTEGRATION_CONTRACT.md']]+[p for p in P.rglob('*') if p.is_file()]
manifest={'status':'DCC construction frozen for engine trial; not reference-quality acceptance','scene':str((D/'final.blend').relative_to(R)),'source_reproduction':'run_guarded.py rebuild; run_guarded.py final_returns rebuild; run_guarded.py export. assembly08 entry/gameplay precede only the hidden entry-side return correction; final-reverse verifies that correction.','canonical_views':['assembly08-entry.png','assembly08-gameplay.png','final-reverse.png'],'files':[]}
for p in sorted(set(files)):
 q={'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}
 if p.suffix=='.png':q['dimensions']=list(struct.unpack('>II',p.read_bytes()[16:24]))
 manifest['files'].append(q)
(E/'delivery-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({'files':len(manifest['files']),'scene_sha256':sha(D/'final.blend'),'manifest_sha256':sha(E/'delivery-manifest.json'),'reclaimed':sum(x['bytes'] for x in removed)},indent=2))
