"""Text-to-image via the free black-forest-labs/FLUX.1-schnell Hugging Face Space.

Usage: flux_generate.py <out.png> <seed> <prompt...>
Used to make clean image-to-3D inputs (one object, plain background, large in frame).
Token only via the HF_TOKEN environment variable. Writes <out>.json with the exact prompt.
"""
import json, os, shutil, sys, time
from gradio_client import Client

out, seed, prompt = sys.argv[1], int(sys.argv[2]), ' '.join(sys.argv[3:])
t0 = time.time()
c = Client('black-forest-labs/FLUX.1-schnell', token=os.environ.get('HF_TOKEN'), verbose=False)
img, used = c.predict(prompt=prompt, seed=seed, randomize_seed=False, width=1024, height=1024,
                      num_inference_steps=4, api_name='/infer')
shutil.copy(img['path'] if isinstance(img, dict) else img, out)
json.dump({'space': 'black-forest-labs/FLUX.1-schnell', 'prompt': prompt, 'seed': int(used), 'steps': 4,
           'size': [1024, 1024], 'seconds': round(time.time() - t0)}, open(out + '.json', 'w'), indent=1)
print('done', out, round(time.time() - t0), flush=True)
