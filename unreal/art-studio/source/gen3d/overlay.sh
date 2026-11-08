#!/bin/sh
# Render a joint overlay (front+side) for a fit config or rigged .blend; writes <prefix>-overlay.png.
set -e
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
"$ROOT/unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender" -b --factory-startup \
  -P "$ROOT/unreal/art-studio/source/gen3d/fit_overlay.py" -- "$1" "$2" 2>&1 | grep -E "Error|Traceback" || true
"$ROOT/.venv-gen3d/bin/python" - "$2" <<'PY'
import json, sys
from PIL import Image, ImageDraw
p = sys.argv[1]
J = json.load(open(p + '-joints.json'))
chains = [['pelvis', 'spine_03', 'neck_01', 'head'], ['clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l'],
          ['upperarm_r', 'lowerarm_r', 'hand_r'], ['thigh_l', 'calf_l', 'foot_l', 'ball_l'], ['thigh_r', 'calf_r', 'foot_r', 'ball_r']]
ims = []
for v in ('front', 'side'):
    im = Image.open(f'{p}-{v}.png').convert('RGB'); d = ImageDraw.Draw(im)
    for c in chains:
        d.line([tuple(J[v][n]) for n in c], fill=(0, 255, 90), width=3)
        for n in c:
            x, y = J[v][n]; d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(255, 40, 40), width=3)
    ims.append(im)
s = Image.new('RGB', (ims[0].width * 2, ims[0].height)); s.paste(ims[0], (0, 0)); s.paste(ims[1], (ims[0].width, 0))
s.save(p + '-overlay.png')
PY
