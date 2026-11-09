"""Synthesise the player's greatsword cues (original, procedural; no samples).

Run: .venv-gen3d/bin/python unreal/art-studio/source/effects/make_combat_audio.py <out_dir>
Writes 16-bit mono 44.1 kHz WAVs; ue_import_combat_audio.py imports them to /Game/BossLab/Effects/Audio.
  SwordWhooshLight  cut I/II, rolling thrust: a quick airy swish
  SwordWhooshHeavy  cut III, running cut: a deeper, longer sweep with a low body
  SwordSlam         jump attack landing: stone thump with debris rattle
  SwordHit          a landed blow: a wet, heavy impact with a short metallic ring
  RuneHum           the enchantment flaring on a landed blow: a soft rising shimmer
"""
import os, sys, wave
import numpy as np

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SR = 44100
rng = np.random.default_rng(11)
def t(s): return np.arange(int(SR * s)) / SR
def lowpass(x, cutoff):
    cutoff = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); prev = 0.0
    for i in range(len(x)):
        prev = (1 - a[i]) * x[i] + a[i] * prev; y[i] = prev
    return y
def save(name, x, gain=.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    fade = np.ones_like(x); n = min(len(x), int(SR * .01)); fade[-n:] = np.linspace(1, 0, n)
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * fade * 32767).astype(np.int16).tobytes())

s = t(.32); env = np.sin(np.pi * np.clip(s / .32, 0, 1)) ** 2
save('SwordWhooshLight', lowpass(rng.standard_normal(len(s)), 900 + 3200 * env) * env, .55)
s = t(.6); env = np.sin(np.pi * np.clip(s / .6, 0, 1)) ** 1.6
x = lowpass(rng.standard_normal(len(s)), 400 + 1800 * env) * env + np.sin(2 * np.pi * (70 + 40 * env) * s) * env * .6
save('SwordWhooshHeavy', x, .7)
s = t(1.0); x = np.sin(2 * np.pi * (48 + 60 * np.exp(-s * 12)) * s) * np.exp(-s * 6) * 2
x += lowpass(rng.standard_normal(len(s)), 1200) * np.exp(-s * 9)
rattle = (rng.random(len(s)) > .992) * rng.standard_normal(len(s)) * np.exp(-s * 3)
x += lowpass(rattle, 5000) - lowpass(rattle, 900)
save('SwordSlam', x, .9)
s = t(.45); x = lowpass(rng.standard_normal(len(s)), 700) * np.exp(-s * 18) * 2.5
x += np.sin(2 * np.pi * 95 * s) * np.exp(-s * 14) * 1.2
for f, a in ((1850, .25), (2730, .18), (4100, .1)):
    x += np.sin(2 * np.pi * f * s) * np.exp(-s * 16) * a
save('SwordHit', x, .85)
s = t(.7); x = np.zeros_like(s)
for k, f in enumerate((660, 990, 1320, 1980)):
    x += np.sin(2 * np.pi * f * (1 + .04 * s) * s + k) / (k + 1)
x *= np.sin(np.pi * np.clip(s / .7, 0, 1)) ** 2
save('RuneHum', x, .35)
print('BOSSLAB combat audio', sorted(os.listdir(OUT)))
