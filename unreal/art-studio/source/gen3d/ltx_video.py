"""Text-to-video via the Lightricks/ltx-video-distilled Hugging Face Space.

Usage: ltx_video.py <out.mp4> <seed> <seconds> <width> <height> <prompt...>
Token only via HF_TOKEN. Writes <out>.json with the exact prompt and settings.
"""
import json, os, shutil, sys, time
from gradio_client import Client
out, seed, secs, w, h, prompt = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), ' '.join(sys.argv[6:])
t0 = time.time()
c = Client('Lightricks/ltx-video-distilled', token=os.environ.get('HF_TOKEN'), verbose=False)
res = c.predict(prompt=prompt, negative_prompt='worst quality, inconsistent motion, blurry, jittery, distorted, text, logo, background objects, camera motion',
                input_image_filepath=None, input_video_filepath=None, height_ui=h, width_ui=w, mode='text-to-video', duration_ui=secs,
                ui_frames_to_use=9, seed_ui=seed, randomize_seed=False, ui_guidance_scale=1, improve_texture_flag=True, api_name='/text_to_video')
vid = res[0] if isinstance(res, (list, tuple)) else res
path = vid['video'] if isinstance(vid, dict) else vid
shutil.copy(path, out)
json.dump({'space': 'Lightricks/ltx-video-distilled', 'prompt': prompt, 'seed': seed, 'seconds': secs, 'size': [w, h], 'wall_seconds': round(time.time() - t0)}, open(out + '.json', 'w'), indent=1)
print('done', out, round(time.time() - t0), flush=True)
