"""Measure a recorded game mix (artifacts/unreal/audio-mix.wav from `benchmark record-audio`).

Run: .venv-gen3d/bin/python unreal/art-studio/source/audio/measure_mix.py <mix.wav>
Reports overall level, 3 s short-term loudness (an approximation of LUFS: RMS after a
100 Hz high-pass, in dBFS) and peaks. Game mixes commonly target about -23 to -16 LUFS
integrated, with loud moments near -12 to -9 short-term; a mix well below that sounds quiet.
"""
import sys, wave
import numpy as np

with wave.open(sys.argv[1]) as w:
    ch, sr, width = w.getnchannels(), w.getframerate(), w.getsampwidth()
    raw = w.readframes(w.getnframes())
x = (np.frombuffer(raw, np.int16).astype(np.float64) / 32768 if width == 2 else np.frombuffer(raw, np.int32).astype(np.float64) / 2**31).reshape(-1, ch)
mono = x.mean(1)
a = np.exp(-2 * np.pi * 100 / sr); y = np.empty_like(mono); p = 0.0
for i in range(len(mono)): p = (1 - a) * mono[i] + a * p; y[i] = mono[i] - p
def db(v): return 20 * np.log10(max(v, 1e-9))
win = 3 * sr
st = [db(np.sqrt((y[i:i + win] ** 2).mean())) for i in range(0, len(y) - win, sr)]
print(f'{len(mono) / sr:.1f} s, {ch} ch, {sr} Hz')
print(f'integrated (approx) {db(np.sqrt((y ** 2).mean())):.1f} dBFS, peak {db(np.abs(x).max()):.1f} dBFS')
print(f'short-term 3 s: loudest {max(st):.1f}, median {np.median(st):.1f}, quietest {min(st):.1f} dBFS')
print('short-term per 3 s:', ' '.join(f'{v:.0f}' for v in st[::3]))
