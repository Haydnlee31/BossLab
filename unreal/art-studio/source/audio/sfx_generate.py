"""Text-to-audio sound effects via Stable Audio Open 1.0 on the 1inkusFace/Stable-Audio-Open-Zero
Hugging Face Space (Stability AI Community License: free under USD 1M annual revenue, "Powered by Stability AI"
attribution; see CREDITS.md). Token only via HF_TOKEN. Outputs stay local (artifacts/, gitignored).

Usage: sfx_generate.py <out_dir> <name> <seconds> <variations> <prompt...>
Writes <name>_v<k>.wav and <name>.json (exact prompt, settings, timing).
"""
import json, os, shutil, sys, time
from gradio_client import Client

out, name, seconds, n, prompt = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), ' '.join(sys.argv[5:])
os.makedirs(out, exist_ok=True)
SPACE = '1inkusFace/Stable-Audio-Open-Zero'
c = Client(SPACE, token=os.environ.get('HF_TOKEN'), verbose=False, httpx_kwargs={'timeout': 600})
files, t0 = [], time.time()
for k in range(n):
    p = c.predict(prompt=prompt, seconds_total=seconds, steps=100, cfg_scale=7, api_name='/predict')
    p = p['path'] if isinstance(p, dict) else p
    dst = os.path.join(out, f'{name}_v{k}' + os.path.splitext(p)[1]); shutil.copy(p, dst); files.append(dst)
json.dump({'space': SPACE, 'model': 'stabilityai/stable-audio-open-1.0', 'prompt': prompt, 'seconds': seconds, 'steps': 100,
           'cfg_scale': 7, 'files': files, 'wall_seconds': round(time.time() - t0)}, open(os.path.join(out, f'{name}.json'), 'w'), indent=1)
print('done', name, len(files), round(time.time() - t0), flush=True)
