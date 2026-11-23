"""Effect sprite/decal source images for the Bellbreaker (2026-11-23 effects pass) via the free
black-forest-labs/FLUX.1-schnell Hugging Face Space (Apache-2.0). Token only via HF_TOKEN; outputs stay local.

Usage: flux_fx_textures.py <out_dir> [name ...]
Writes <name>_s<seed>.png and <name>_s<seed>.json (exact prompt, seed, steps, size, timing).
Every prompt asks for a pure black background: the importer uses luminance as emission/opacity.
"""
import json, os, shutil, sys, time
from gradio_client import Client

PROMPTS = {
    'crack_glow': ('top-down orthographic view of a single radial impact crater crack pattern in dark stone, '
                   'thin jagged cracks radiating from the centre glowing bright orange molten lava light, '
                   'isolated on a pure black background, no stone texture outside the cracks, game VFX decal texture', (3, 7)),
    'dust_puff': ('a single soft billowing cloud of pale grey dust and smoke, round puff, isolated in the centre '
                  'on a pure black background, soft edges fading to black, game VFX sprite texture, no ground', (2, 9)),
    'fire_burst': ('a single burst of bright orange and yellow fire flame with embers, round explosion, '
                   'isolated in the centre on a pure black background, edges fade to black, game VFX sprite texture', (4, 11)),
    'slag_puddle': ('top-down orthographic view of a single splash puddle of glowing molten metal slag, bright orange '
                    'centre cooling to dark red crust at the splattered edges, isolated on a pure black background, '
                    'game VFX decal texture', (5, 8)),
}
SPACE = 'black-forest-labs/FLUX.1-schnell'
out = sys.argv[1]
names = sys.argv[2:] or list(PROMPTS)
os.makedirs(out, exist_ok=True)
c = Client(SPACE, token=os.environ.get('HF_TOKEN'), verbose=False, httpx_kwargs={'timeout': 600})
for name in names:
    prompt, seeds = PROMPTS[name]
    for seed in seeds:
        t0 = time.time()
        img, used = c.predict(prompt=prompt, seed=seed, randomize_seed=False, width=1024, height=1024,
                              num_inference_steps=4, api_name='/infer')
        img = img['path'] if isinstance(img, dict) else img
        dst = os.path.join(out, f'{name}_s{seed}.png')
        shutil.copy(img, dst)
        json.dump({'space': SPACE, 'prompt': prompt, 'seed': seed, 'steps': 4, 'size': [1024, 1024],
                   'seconds': round(time.time() - t0)}, open(dst[:-4] + '.json', 'w'), indent=1)
        print('done', name, seed, round(time.time() - t0), flush=True)
