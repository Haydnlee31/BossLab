#!/usr/bin/env python3
"""Audit actual engine frame sequences; retain hashes, views and encoded evidence."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
frames=Path(sys.argv[1]).resolve(); output=Path(sys.argv[2]).resolve()
files=sorted(frames.glob('frame-*.png'))
assert len(files) in (180,720),len(files)
assert [p.name for p in files]==[f'frame-{i:06d}.png' for i in range(len(files))]
assert frames.is_relative_to(root/'artifacts/unreal') or frames.is_relative_to(root/'unreal/.cache')
start=output.with_suffix('.start.json')
if start.exists():
 started=json.loads(start.read_text())['started_epoch']
 assert all(p.stat().st_mtime>=started for p in files),'Stale capture frames'
manifest={'kind':'Actual Unreal fixed-30-Hz frame capture; not FPS evidence','frames':len(files),'files':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mtime':p.stat().st_mtime} for p in files]}
manifest['unique_frame_hashes']=len({p['sha256'] for p in manifest['files']})
output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if not output.exists():subprocess.run([str(root/'unreal/.cache/encode-unreal-video'),str(frames),str(output)],check=True)
subprocess.run([str(root/'unreal/.cache/inspect-unreal-video'),str(output),str(len(files))],check=True)
# Preserve chronological visual QA samples, plus four stable views.
keep=set(range(0,len(files),4 if len(files)==180 else 8))|{20,65,110,155}
for i,p in enumerate(files):
 if i not in keep:p.unlink()
print(json.dumps({'video':str(output),'verified_frames':len(files),'retained_raw_samples':len(keep)}))
