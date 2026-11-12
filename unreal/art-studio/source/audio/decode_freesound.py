"""Decode the owner-downloaded Freesound sources (WAV/FLAC) with Blender's aud module to
44.1 kHz 16-bit WAV: mono for sound effects (Unreal spatialises mono only) and stereo for
the music bed. Licences and credits: docs/AUDIO.md, CREDITS.md.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/audio/decode_freesound.py -- <src_dir> <out_dir>
"""
import aud, os, sys

src, out = sys.argv[sys.argv.index('--') + 1:][:2]
os.makedirs(out, exist_ok=True)
NAMES = {'423869': 'fs_whispers', '423008': 'fs_scream', '211646': 'fs_scatteredghost'}
done = []
for f in sorted(os.listdir(src)):
    key = f.split('__')[0]
    if key not in NAMES or not f.lower().endswith(('.wav', '.flac')): continue
    sound = aud.Sound(os.path.join(src, f))
    mono = sound.rechannel(1).resample(44100, False)
    mono.write(os.path.join(out, NAMES[key] + '.wav'), 44100, aud.CHANNELS_MONO, aud.FORMAT_S16, aud.CONTAINER_WAV, aud.CODEC_PCM)
    done.append(NAMES[key])
    if key == '211646':
        stereo = sound.rechannel(2).resample(44100, False)
        stereo.write(os.path.join(out, NAMES[key] + '_stereo.wav'), 44100, aud.CHANNELS_STEREO, aud.FORMAT_S16, aud.CONTAINER_WAV, aud.CODEC_PCM)
        done.append(NAMES[key] + '_stereo')
print('BOSSLAB decoded', done)
