#!/bin/sh
# Render four review views of a GLB and combine them into sheet.png.
# Usage: review.sh <model.glb> <out_dir> [size]
set -e
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
"$ROOT/unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender" -b --factory-startup \
  -P "$ROOT/unreal/art-studio/source/gen3d/render_glb.py" -- "$1" "$2" "${3:-1000}" 2>&1 | grep -E "Error|Traceback" || true
"$ROOT/.venv-gen3d/bin/python" - "$2" <<'PY'
import sys
from PIL import Image
d = sys.argv[1]
ims = [Image.open(f'{d}/{n}.png') for n in ['front', 'threequarter', 'side', 'back']]
w, h = ims[0].size
s = Image.new('RGB', (w * 4, h))
for i, im in enumerate(ims):
    s.paste(im, (i * w, 0))
s.save(f'{d}/sheet.png')
PY
