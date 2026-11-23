"""Small artifact hash inventory, no asset duplication or deletion."""
import json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a-2026-11-16';D=R/'unreal/art-studio/hearth-a-2026-11-16';S=Path(__file__).parent
mode=sys.argv[1] if len(sys.argv)>1 else 'draft04'
paths=[D/(mode+'.blend'),E/(mode+'-preview.png'),E/(mode+'-gameplay.png'),E/(mode+'-process.json'),E/'readback.json',E/'export-audit.json',E/'CONTRACT.md',E/'inventory.json',E/'fixture-light-pairs.json',E/'TECHART.md']+list(S.glob('*.py'))+[S/'assets.json']
entries=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths if p.is_file()]
(E/'delivery-manifest.json').write_text(json.dumps({'scope':'DCC handoff; runtime assets/captures separate; no overall art acceptance implied','scene_mode':mode,'files':entries},indent=2))
print('Manifest:',len(entries),'files')
