"""Image-to-3D via the free microsoft/TRELLIS.2 Hugging Face Space.

Usage: trellis2_generate.py <input.png> <out_dir> [seed] [resolution]
Writes preprocessed.png, model.glb and run.json into out_dir.
"""
import json, os, shutil, sys, time
from pathlib import Path
from gradio_client import Client, handle_file

src, out = Path(sys.argv[1]), Path(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
res = sys.argv[4] if len(sys.argv) > 4 else '1536'
out.mkdir(parents=True, exist_ok=True)
t0 = time.time()
c = Client('microsoft/TRELLIS.2', token=os.environ.get('HF_TOKEN'), verbose=False)
c.predict(api_name='/start_session')
pre = c.predict(input=handle_file(str(src)), api_name='/preprocess_image')
pre_path = pre['path'] if isinstance(pre, dict) else pre
shutil.copy(pre_path, out / 'preprocessed.png')
print('preprocessed', round(time.time() - t0), flush=True)
c.predict(image=handle_file(pre_path), seed=seed, resolution=res, api_name='/image_to_3d')
print('generated', round(time.time() - t0), flush=True)
glb, _ = c.predict(decimation_target=300000, texture_size=2048, api_name='/extract_glb')
glb = glb['value'] if isinstance(glb, dict) else glb
shutil.copy(glb, out / 'model.glb')
json.dump({'space': 'microsoft/TRELLIS.2', 'input': str(src), 'seed': seed, 'resolution': res,
           'decimation_target': 300000, 'texture_size': 2048, 'seconds': round(time.time() - t0)},
          open(out / 'run.json', 'w'), indent=1)
print('done', out / 'model.glb', flush=True)
