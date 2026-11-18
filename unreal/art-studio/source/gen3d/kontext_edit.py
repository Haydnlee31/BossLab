"""Image editing via the FLUX.1-Kontext-Dev Hugging Face Space (instruction + reference image).

Usage: kontext_edit.py <input.png> <out.png> <seed> <instruction...>
Token only via HF_TOKEN. Writes <out>.json with the exact instruction and seed.
"""
import json, os, shutil, sys, time
from gradio_client import Client, handle_file
src, out, seed, prompt = sys.argv[1], sys.argv[2], int(sys.argv[3]), ' '.join(sys.argv[4:])
t0 = time.time()
c = Client('black-forest-labs/FLUX.1-Kontext-Dev', token=os.environ.get('HF_TOKEN'), verbose=False)
res = c.predict(input_image=handle_file(src), prompt=prompt, seed=seed, randomize_seed=False, guidance_scale=2.5, steps=28, api_name='/infer')
img = res[0] if isinstance(res, (list, tuple)) else res
path = img['path'] if isinstance(img, dict) else img
shutil.copy(path, out)
json.dump({'space': 'black-forest-labs/FLUX.1-Kontext-Dev', 'input': src, 'prompt': prompt, 'seed': seed, 'seconds': round(time.time() - t0)}, open(out + '.json', 'w'), indent=1)
print('done', out, round(time.time() - t0), flush=True)
