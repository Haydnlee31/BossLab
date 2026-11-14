"""Text-to-motion via the HY-Motion 1.0 Hugging Face Space (Tencent Hunyuan community licence:
not for use in the EU, UK or South Korea; >1M MAU needs a licence; outputs may not train other
models). Token only via HF_TOKEN. Outputs stay local (artifacts/, gitignored).

Usage: hy_motion_generate.py <out_dir> <name> <seconds> <seeds e.g. 0,1> <prompt...>
Writes <name>_s<seed>.fbx and <name>.json (exact prompt, seeds, timing).
"""
import json, os, shutil, sys, time
from gradio_client import Client

out, name, seconds, seeds, prompt = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], ' '.join(sys.argv[5:])
os.makedirs(out, exist_ok=True)
t0 = time.time()
c = Client('tencent/HY-Motion-1.0', token=os.environ.get('HF_TOKEN'), verbose=False)
_, files = c.predict(original_text=prompt, rewritten_text=prompt, seed_input=seeds, motion_duration=seconds,
                     cfg_scale=5.0, api_name='/generate_motion_func')
fbx = [f if isinstance(f, str) else f.get('path') for f in (files or [])]
fbx = sorted(p for p in fbx if p and p.endswith('.fbx'))
saved = []
for p, s in zip(fbx, seeds.split(',')):
    dst = os.path.join(out, f'{name}_s{s.strip()}.fbx'); shutil.copy(p, dst); saved.append(dst)
json.dump({'space': 'tencent/HY-Motion-1.0', 'prompt': prompt, 'seconds': seconds, 'seeds': seeds, 'files': saved,
           'wall_seconds': round(time.time() - t0)}, open(os.path.join(out, f'{name}.json'), 'w'), indent=1)
print('done', name, len(saved), round(time.time() - t0), flush=True)
