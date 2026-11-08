#!/usr/bin/env python3
"""Save a real native viewport capture and metadata; never synthesizes evidence."""
import base64
import json
from pathlib import Path
import runpy
import sys
ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[1] if len(sys.argv) > 1 else 'viewport'
assert name.replace('-', '').replace('_', '').isalnum()
client = runpy.run_path(str(ROOT / 'scripts/unreal-mcp.py'))['Client']()
client.connect()
result = client.request('tools/call', {'name': 'call_tool', 'arguments': {
    'toolset_name': 'EditorToolset.EditorAppToolset', 'tool_name': 'CaptureViewport',
    'arguments': {'bShowUI': True, 'captureTransform': None, 'annotations': None}}})
if result.get('isError'):
    raise RuntimeError(str(result))
metadata = {}
data = None
for block in result['content']:
    if block['type'] == 'image':
        data = block['data']
    elif block['type'] == 'text':
        metadata = json.loads(block['text'])
        value = metadata.get('returnValue', {})
        if isinstance(value, dict) and isinstance(value.get('image'), dict):
            data = value['image'].pop('data', None) or data
assert data, 'Native capture returned no image'
image_path = ROOT / f'artifacts/unreal/{name}.png'
image_path.write_bytes(base64.b64decode(data))
(ROOT / f'artifacts/unreal/{name}.json').write_text(json.dumps(metadata, indent=2))
print(json.dumps({'image': str(image_path), 'bytes': image_path.stat().st_size}))
