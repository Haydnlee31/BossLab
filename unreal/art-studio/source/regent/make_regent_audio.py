"""Synthesise the Funeral Regent greybox sound cues (original, procedural; no samples).

Run: .venv-gen3d/bin/python unreal/art-studio/source/regent/make_regent_audio.py <out_dir>
Writes 16-bit mono 44.1 kHz WAVs; ue_import_regent.py imports them to /Game/BossLab/Regent/Audio.
"""
import os, sys, wave
import numpy as np

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SR = 44100
rng = np.random.default_rng(7)

def t(seconds):
    return np.arange(int(SR * seconds)) / SR

def env(x, attack, release):
    n = len(x); a = max(1, int(SR * attack)); r = max(1, int(SR * release))
    e = np.ones(n); e[:a] = np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r)
    return x * e

def lowpass(x, cutoff):
    # One-pole low-pass; cutoff may be an array for sweeps.
    cutoff = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); prev = 0.0
    for i in range(len(x)):
        prev = (1 - a[i]) * x[i] + a[i] * prev; y[i] = prev
    return y

def bandpass(x, low, high):
    return lowpass(x, high) - lowpass(x, low)

def save(name, x, gain=.9):
    x = x / (np.max(np.abs(x)) + 1e-9) * gain
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

# Grave Bell: an inharmonic funeral bell partial set with a dull impact thud.
s = t(4.5); x = np.zeros_like(s)
for ratio, amp, decay in ((.5, .6, 1.6), (1, 1, 1.2), (1.19, .55, .9), (1.56, .45, .7), (2, .5, .6), (2.51, .3, .45), (3.01, .25, .35), (4.1, .15, .25)):
    x += amp * np.sin(2 * np.pi * 98 * ratio * s + rng.uniform(0, 6)) * np.exp(-s / decay)
thud = lowpass(rng.standard_normal(len(s)), 180) * np.exp(-s / .08) * 6
save('RegentBell', env(x + thud, .002, .3))

# Censer whoosh: band-passed noise whose centre sweeps up then down with the swing.
s = t(.75); sweep = 300 + 1500 * np.sin(np.pi * s / .75) ** 2
x = lowpass(rng.standard_normal(len(s)), sweep) - lowpass(rng.standard_normal(len(s)) * 0, 1)
save('RegentWhoosh', env(x * np.sin(np.pi * s / .75) ** 1.5, .01, .1), .7)

# Estoc thrust: a short bright swish.
s = t(.28); x = bandpass(rng.standard_normal(len(s)), 1800, 6500) * np.exp(-((s - .08) / .06) ** 2)
save('RegentThrust', env(x, .005, .05), .6)

# Witness skull launch: a gliding wail with vibrato over breathy noise.
s = t(1.0); f = 620 * np.exp(-s * .9) + 220 + 12 * np.sin(2 * np.pi * 6 * s)
x = np.sin(2 * np.pi * np.cumsum(f) / SR) + .4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
x = x * np.sin(np.pi * np.minimum(s / 1.0, 1)) + .5 * bandpass(rng.standard_normal(len(s)), 500, 3000) * np.exp(-s * 2)
save('RegentSkull', env(x, .03, .25), .6)

# Furrow eruption: low whoomp plus crackle.
s = t(.8); x = np.sin(2 * np.pi * (60 + 80 * np.exp(-s * 8)) * s) * np.exp(-s * 5) * 1.5
crackle = (rng.random(len(s)) > .995) * rng.standard_normal(len(s)) * np.exp(-s * 3) * 3
x += lowpass(rng.standard_normal(len(s)), 900) * np.exp(-s * 4) + bandpass(crackle, 800, 5000)
save('RegentEruption', env(x, .004, .15), .8)

# Ash step: a rising glassy shimmer that cuts off at the vanish.
s = t(.6); x = np.zeros_like(s)
for k, f in enumerate((880, 1320, 1760, 2350, 2960)):
    x += np.sin(2 * np.pi * f * (1 + .25 * s) * s + k) / (k + 1)
x *= (s / .6) ** 2 + .05
x += bandpass(rng.standard_normal(len(s)), 2500, 9000) * (s / .6) ** 3 * .6
save('RegentBlink', env(x, .02, .03), .55)

# Funeral Pyre: a roaring blast with a rumble tail.
s = t(1.8); x = lowpass(rng.standard_normal(len(s)), 400 + 1800 * np.exp(-s * 2.5)) * np.exp(-s * 1.4) * 2
x += np.sin(2 * np.pi * 42 * s) * np.exp(-s * 1.2) * .8
save('RegentPyre', env(x, .006, .3), .9)

# The Pyre Wakes: a swelling, detuned low drone (choir-like) for the phase change.
s = t(3.2); x = np.zeros_like(s)
for f in (55, 55.4, 82.4, 110.2, 164.6, 220.5, 329.2):
    x += np.sin(2 * np.pi * f * s) + .3 * np.sin(2 * np.pi * 2 * f * s + 1)
x *= np.sin(np.pi * np.minimum(s / 3.2, 1)) ** 1.2
x += lowpass(rng.standard_normal(len(s)), 300) * np.sin(np.pi * s / 3.2) * 1.5
save('RegentWakes', env(x, .2, .6), .85)
print('BOSSLAB regent audio', sorted(os.listdir(OUT)))
