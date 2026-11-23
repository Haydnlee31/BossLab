"""Lightweight manifest and last-two-scene retention; run only after readback."""
from pathlib import Path
import hashlib,json,struct,re,shutil
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-arena-2026-11-16';D=R/'unreal/art-studio/bellbreaker-arena-2026-11-16';S=Path(__file__).parent
assert (E/'saved-readback.json').exists()
removed=[]
for name in ['bell-probe.blend','final.blend','final-v2.blend']:
 p=D/name
 if p.exists():
  b=p.read_bytes();removed.append({'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});p.unlink()
(E/'scene-retention.json').write_text(json.dumps({'reason':'Owner/root latest-two meaningful arena scenes: initial blockout and final-v3. Probe/rejected images, exact source snapshots and receipts preserved. No other asset touched.','removed':removed,'retained':['blockout.blend','final-v3.blend']},indent=2))
views=['entry-hero','reverse','gameplay-height','near-boundary','clay-architecture','prop-detail','furnace-detail','top-plan']
paths=list(S.glob('*.py'))+[S/'assets.json',D/'final-v3.blend',D/'last-casting.glb',E/'saved-readback.json',E/'final-v3/manifest.json',E/'final-v3/clearance.json',E/'TECHART.md',E/'index.html',E/'scene-retention.json',E/'final-v3-process.json',E/'readback-process.json',E/'plan-process.json',E/'plan-recapture.json']+[E/'final-v3'/f'{v}.png' for v in views]
entries=[]
for p in paths:
 b=p.read_bytes();v={'path':str(p.relative_to(R)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 if p.suffix=='.png':v['dimensions']=struct.unpack('>II',b[16:24])
 entries.append(v)
missing=[]
for link in re.findall(r'(?:href|src)="([^"]+)"',(E/'index.html').read_text()):
 if not link.startswith(('http','#')) and not (E/link).exists():missing.append(link)
assert not missing,missing
(E/'delivery-manifest.json').write_text(json.dumps({'status':'Frozen standalone actual3D environment draft; no runtime/quality acceptance inferred','canonical_views':views,'files':entries,'gallery_missing_links':missing,'free_bytes':shutil.disk_usage(R).free},indent=2));print('Frozen',len(entries),'files;8actualfinalviews;linksverified')
