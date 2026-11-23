"""Re-encode mislabeled embedded WebP export copies as real PNG via local ImageIO/sips."""
from pathlib import Path
import hashlib,json,subprocess,struct
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';records=[]
for p in sorted((E/'export/textures').glob('*.png')):
 b=p.read_bytes()
 if b.startswith(b'\x89PNG\r\n\x1a\n'):continue
 old=p.with_suffix('.source-webp');p.rename(old)
 subprocess.run(['/usr/bin/sips','-s','format','png',str(old),'--out',str(p)],check=True,capture_output=True)
 out=p.read_bytes();assert out.startswith(b'\x89PNG\r\n\x1a\n');records.append({'path':str(p.relative_to(R)),'original_copy':str(old.relative_to(R)),'before_sha256':hashlib.sha256(b).hexdigest(),'after_sha256':hashlib.sha256(out).hexdigest(),'png_dimensions':struct.unpack('>II',out[16:24])})
(E/'texture-encoding-correction.json').write_text(json.dumps(records,indent=2));print(json.dumps(records,indent=2))
