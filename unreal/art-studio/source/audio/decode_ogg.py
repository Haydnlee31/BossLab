"""Decode the CC0 Kenney OGG sources to mono 44.1 kHz 16-bit WAV with Blender's aud module
(the project has no ffmpeg; Blender bundles the decoder). Mono so Unreal can spatialise them.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/audio/decode_ogg.py -- <src_dir> <out_dir>
"""
import aud, os, sys

src, out = sys.argv[sys.argv.index('--') + 1:][:2]
os.makedirs(out, exist_ok=True)
done = 0
for root, _, files in os.walk(src):
    for f in sorted(files):
        if not f.endswith('.ogg'): continue
        pack = os.path.basename(root)
        s = aud.Sound(os.path.join(root, f)).rechannel(1).resample(44100, False)
        s.write(os.path.join(out, f'{pack}_{f[:-4]}.wav'), 44100, aud.CHANNELS_MONO, aud.FORMAT_S16, aud.CONTAINER_WAV, aud.CODEC_PCM)
        done += 1
print('BOSSLAB decoded', done)
