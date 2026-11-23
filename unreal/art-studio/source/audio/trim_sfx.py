"""Trim Stable Audio Open outputs (the Space pads every clip to ~47 s) to their requested length plus 0.4 s,
fade the tail over 0.35 s and peak-normalise to -1 dBFS. macOS afconvert decodes the FLAC.

Usage: python3 trim_sfx.py <dir with <name>.json and <name>_v<k>.flac>   -> <dir>/wav/<name>_v<k>.wav
"""
import glob, json, os, subprocess, sys, tempfile, wave
import numpy as np

src = sys.argv[1]
out = os.path.join(src, 'wav'); os.makedirs(out, exist_ok=True)
for meta in sorted(glob.glob(os.path.join(src, '*.json'))):
    info = json.load(open(meta))
    for f in info['files']:
        flac = os.path.join(src, os.path.basename(f))
        with tempfile.TemporaryDirectory() as tmp:
            raw = os.path.join(tmp, 'raw.wav')
            subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16@44100', flac, raw], check=True)
            w = wave.open(raw); ch, rate = w.getnchannels(), w.getframerate()
            x = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, ch).astype(np.float32) / 32768
        n = min(len(x), int((info['seconds'] + .4) * rate))
        x = x[:n].copy()
        fade = int(.35 * rate)
        x[-fade:] *= np.linspace(1, 0, fade)[:, None]
        x *= 10 ** (-1 / 20) / max(1e-6, np.abs(x).max())
        dst = os.path.join(out, os.path.splitext(os.path.basename(flac))[0] + '.wav')
        with wave.open(dst, 'wb') as o:
            o.setnchannels(ch); o.setsampwidth(2); o.setframerate(rate)
            o.writeframes((x * 32767).astype('<i2').tobytes())
        print('wrote', dst, round(n / rate, 2), 's')
