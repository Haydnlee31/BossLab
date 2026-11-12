"""Build the game's sound set: layered variations from CC0 Kenney recordings plus
procedural layers (magic, fire, air), following the usual game-audio recipe of
transient + body + texture + tail (+ sweetener), several variations per event, and
loopable ambience beds. See docs/AUDIO.md for the event list and the mix.

Run: .venv-gen3d/bin/python unreal/art-studio/source/audio/make_game_audio.py <wav_src> <out_dir>
<wav_src> holds decode_ogg.py output (impact_*.wav, rpg_*.wav). Writes 16-bit mono 44.1 kHz
<Name>_<n>.wav (loops: <Name>_0.wav) and manifest.json (layers per file).
"""
import json, os, sys, wave
import numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
SR = 44100
rng = np.random.default_rng(2026)
manifest = {}

def load(name):
    with wave.open(os.path.join(SRC, name + '.wav')) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768

def t(seconds): return np.arange(int(SR * seconds)) / SR

def pitch(x, semitones):
    # Resampling pitch shift (also changes length, like a varispeed tape).
    if semitones == 0: return x
    r = 2 ** (semitones / 12)
    idx = np.arange(0, len(x) - 1, r)
    return np.interp(idx, np.arange(len(x)), x)

def onepole(x, cutoff, high=False, stages=1):
    # One-pole low/high-pass; stages > 1 cascades it for a steeper (-6 dB/oct per stage) slope.
    for _ in range(stages - 1): x = _onepole(x, cutoff, high)
    return _onepole(x, cutoff, high)

def _onepole(x, cutoff, high=False):
    cutoff = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.empty_like(x); prev = 0.0
    for i in range(len(x)):
        prev = (1 - a[i]) * x[i] + a[i] * prev; y[i] = prev
    return x - y if high else y

def bandpass(x, centre, q, stages=2):
    # Cascaded state-variable band-pass; one stage leaves too much hiss outside the band.
    for _ in range(stages - 1): x = _bandpass(x, centre, q)
    return _bandpass(x, centre, q)

def _bandpass(x, centre, q):
    # State-variable filter; centre may vary per sample (sweeps).
    centre = np.broadcast_to(np.asarray(centre, float), x.shape)
    f = 2 * np.sin(np.pi * np.minimum(centre, SR / 6) / SR); damp = 1 / q
    low = band = 0.0; y = np.empty_like(x)
    for i in range(len(x)):
        high = x[i] - low - damp * band
        band += f[i] * high; low += f[i] * band; y[i] = band
    return y

def env(n, attack, release, shape=2.0):
    e = np.ones(n); a = max(1, int(SR * attack)); r = max(1, int(SR * release))
    e[:a] = np.linspace(0, 1, a) ** .7
    e[-r:] *= np.linspace(1, 0, r) ** shape
    return e

def mix(length, *layers):
    out = np.zeros(int(SR * length))
    for x, at, gain in layers:
        s = int(SR * at); x = x[:max(0, len(out) - s)]
        out[s:s + len(x)] += x * gain
    return out

def noise(seconds): return rng.standard_normal(int(SR * seconds))

def sub(freq_start, freq_end, seconds, decay):
    s = t(seconds); f = freq_end + (freq_start - freq_end) * np.exp(-s * 18)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-s * decay)

def presence(x, gain=.6):
    # Small-speaker "presence": a band-passed copy (~0.7-3 kHz) of the hit layered back in,
    # so impacts still read on laptop speakers that cannot reproduce the low body.
    return x + bandpass(x, 1500, .8) * gain * 4

def treble(x, db, corner=2500):
    # High-shelf boost: add a high-passed copy (about +db above the corner).
    return x + onepole(x, corner, high=True, stages=2) * (10 ** (db / 20) - 1)

def save(name, x, layers, peak=.9, loop=False, present=0.0, drive=1.8):
    # Subsonic high-pass (~45 Hz): rumble no speaker reproduces only eats headroom.
    x = onepole(x, 45, high=True, stages=2)
    if present: x = presence(x, present); layers = layers + [f'presence band x{present}']
    # Gentle saturation lifts the body of one-shots a few dB (the first mix measured about
    # -36 dBFS integrated, far under typical game loudness). Loops stay clean.
    if not loop and drive > 0:
        x = np.tanh(drive * x / (np.max(np.abs(x)) + 1e-9)) / np.tanh(drive)
    x = x / (np.max(np.abs(x)) + 1e-9) * max(peak, .8)
    if not loop:
        n = min(len(x), int(SR * .012)); x[-n:] *= np.linspace(1, 0, n)
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    manifest[name] = {'seconds': round(len(x) / SR, 3), 'layers': layers, 'loop': loop}

def pick(prefix, k): return f'{prefix}_{k % 5:03d}'

# --- Player greatsword -----------------------------------------------------------------
def whoosh(seconds, lo, hi, body_cut, ring):
    # Air pushed by a long blade: a resonant band sweeping up then down (the pass), a low
    # air body, and a faint blade sing near the peak.
    n = int(SR * seconds); s = np.arange(n) / n
    pass_curve = np.sin(np.pi * s) ** 1.5
    band = bandpass(noise(seconds), lo + (hi - lo) * pass_curve, 2.2) * pass_curve
    body = onepole(noise(seconds), body_cut, stages=3) * pass_curve ** 2 * 6
    sing = np.sin(2 * np.pi * ring * np.arange(n) / SR) * np.exp(-((s - .55) / .12) ** 2) * .08
    return band + body + sing

for k in range(5):
    sec = .3 + .025 * k
    x = whoosh(sec, 450 + 60 * k, 2100 + 150 * (k % 3), 260, 1700 + 120 * k)
    save(f'SwordWhooshLight_{k}', x, [f'procedural band sweep {450 + 60 * k}-{2100 + 150 * (k % 3)} Hz', 'air body', 'blade sing'], .55)
for k in range(4):
    sec = .52 + .04 * k
    x = whoosh(sec, 260 + 40 * k, 1300 + 120 * k, 180, 1300 + 90 * k)
    cloth = pitch(load(f'rpg_cloth{k + 1}'), -3)
    save(f'SwordWhooshHeavy_{k}', mix(sec, (x, 0, 1), (cloth, 0, .35)),
         [f'procedural band sweep {260 + 40 * k}-{1300 + 120 * k} Hz', f'rpg_cloth{k + 1} -3 st'], .7)

# Blade into the boss: body (heavy punch), slice texture, armour ring, sub thump, short tail.
for k in range(5):
    body = pitch(load(pick('impact_impactPunch_heavy', k)), -2 - k % 2)
    slice_ = pitch(load('rpg_knifeSlice' if k % 2 else 'rpg_knifeSlice2'), -5)
    ring = pitch(load(pick('impact_impactPlate_medium', k + 2)), -3)
    thump = sub(110, 52, .35, 10)
    tail = onepole(noise(.3), 900, stages=2) * np.exp(-t(.3) * 14)
    save(f'SwordHit_{k}', mix(.75, (body, 0, 1), (slice_, .005, .55), (ring, .01, .3), (thump, 0, .35), (tail, .02, .25)),
         [pick('impactPunch_heavy', k) + ' -2/-3 st', 'rpg_knifeSlice -5 st', pick('impactPlate_medium', k + 2) + ' -3 st', 'sub 110->52 Hz', 'noise tail'], .9, present=0.6)

# Jump attack landing: ground crunch, punch, sub boom, scattered debris.
for k in range(3):
    crunch = pitch(load(pick('impact_impactMining', k)), -5)
    punch = pitch(load(pick('impact_impactPunch_heavy', k + 3)), -6)
    boom = sub(80, 38, .9, 4.5)
    layers = [(crunch, 0, 1), (punch, 0, .8), (boom, 0, .45)]
    for j in range(4):
        layers.append((pitch(load(pick('impact_impactGeneric_light', j + k)), 4 + 2 * j), .08 + .07 * j + .02 * k, .18))
    save(f'SwordSlam_{k}', mix(1.2, *layers), [pick('impactMining', k) + ' -5 st', pick('impactPunch_heavy', k + 3) + ' -6 st', 'sub 80->38 Hz', '4x impactGeneric_light debris'], .95, present=0.8)

# Enchantment flare on a landed blow: detuned bright partials with a sparkle.
for k in range(3):
    s = t(.8); x = np.zeros_like(s)
    for j, f in enumerate((660, 990, 1320, 1980)):
        f *= 1 + .01 * k
        x += (np.sin(2 * np.pi * f * s) + np.sin(2 * np.pi * f * 1.004 * s)) / (j + 1)
    x *= np.sin(np.pi * np.clip(s / .8, 0, 1)) ** 2
    spark = bandpass(noise(.8), 6000, 4) * np.exp(-s * 6) * .5
    save(f'RuneHum_{k}', x + spark, ['detuned partials 660/990/1320/1980 Hz', 'bandpassed sparkle'], .35)

# --- Bodies, armour, movement ------------------------------------------------------------
for k in range(5):
    body = pitch(load(pick('impact_impactPunch_heavy', k)), -2)
    armour = pitch(load(pick('impact_impactPlate_light', k)), -2)
    save(f'BodyHit_{k}', mix(.7, (body, 0, 1), (armour, .01, .5), (sub(95, 50, .3, 12), 0, .3)),
         [pick('impactPunch_heavy', k) + ' -2 st', pick('impactPlate_light', k) + ' -2 st', 'sub 95->50 Hz'], .85, present=0.7)
for k in range(4):
    cloth = load(f'rpg_cloth{k + 1}'); belt = pitch(load('rpg_beltHandle1' if k % 2 else 'rpg_beltHandle2'), -2)
    save(f'GearSwing_{k}', mix(.6, (cloth, 0, 1), (belt, .03, .35)), [f'rpg_cloth{k + 1}', 'rpg_beltHandle -2 st'], .45)
for k in range(4):
    cloth = pitch(load(f'rpg_cloth{(k + 2) % 4 + 1}'), -2); belt = load('rpg_clothBelt' if k % 2 else 'rpg_clothBelt2')
    thump = pitch(load(pick('impact_impactSoft_heavy', k)), -3)
    scrape = pitch(load(pick('impact_footstep_concrete', k + 1)), -2)
    save(f'RollCloth_{k}', mix(.75, (cloth, 0, 1), (belt, .02, .5), (thump, .22, .35), (scrape, .3, .5)),
         [f'rpg_cloth -2 st', 'rpg_clothBelt', pick('impactSoft_heavy', k) + ' -3 st @0.22 s', 'concrete scrape @0.30 s'], .6, present=0.5)
for k in range(8):
    src = pick('impact_footstep_concrete', k) if k < 5 else f'rpg_footstep0{(k - 5) * 3}'
    step = pitch(load(src), -1 - (k % 3) * .5)
    save(f'StepStone_{k}', step, [src + ' pitched'], .5)
for k in range(5):
    step = pitch(load(pick('impact_footstep_concrete', k)), -4)
    weight = pitch(load(pick('impact_impactSoft_heavy', k)), -5)
    jingle = pitch(load('rpg_handleCoins'), -5)[int(SR * .1 * k):int(SR * (.1 * k + .25))]
    save(f'StepHeavy_{k}', mix(.6, (step, 0, 1), (weight, 0, .3), (jingle * env(len(jingle), .01, .2), .02, .25)),
         [pick('footstep_concrete', k) + ' -4 st', pick('impactSoft_heavy', k) + ' -5 st', 'rpg_handleCoins -5 st slice (armour jingle)'], .6, present=0.8)
for k in range(3):
    a = pitch(load(pick('impact_footstep_concrete', k)), -3); b = pitch(load(pick('impact_footstep_concrete', k + 2)), -3)
    thud = pitch(load(pick('impact_impactSoft_heavy', k + 1)), -4); armour = pitch(load(pick('impact_impactPlate_light', k + 3)), -1)
    save(f'LandHeavy_{k}', mix(.7, (a, 0, 1), (b, .045, .8), (thud, 0, .55), (armour, .03, .4), (sub(70, 40, .3, 10), 0, .25)),
         ['2x footstep_concrete -3 st', 'impactSoft_heavy -4 st', 'impactPlate_light', 'sub'], .65, present=0.8)

# Flask: glass clink, cork pop, two or three gulps, a warm shimmer as it takes hold.
for k in range(3):
    clink = load(pick('impact_impactGlass_light', k)); s = t(1.6)
    pop = bandpass(noise(.06), 900, 3) * np.exp(-t(.06) * 60)
    gulps = []
    for j in range(2 + k % 2):
        g = t(.16); gulp = onepole(noise(.16), 380, stages=3) * 4 * np.sin(np.pi * g / .16) ** 2 + np.sin(2 * np.pi * (140 - 200 * g) * g) * np.exp(-g * 20) * .5
        gulps.append((gulp, .35 + .24 * j, 1.1))
    shimmer = sum(np.sin(2 * np.pi * f * s) / (i + 1) for i, f in enumerate((523, 784, 1046))) * np.sin(np.pi * np.clip((s - .8) / .8, 0, 1)) ** 2
    save(f'FlaskDrink_{k}', mix(1.6, (clink, 0, .5), (pop, .12, .8), *gulps, (shimmer, 0, .25)),
         [pick('impactGlass_light', k), 'cork pop', f'{2 + k % 2} procedural gulps', 'shimmer 523/784/1046 Hz'], .55)

# --- Funeral Regent ----------------------------------------------------------------------
for k in range(3):
    bell = pitch(load(pick('impact_impactBell_heavy', k)), -9 - k)
    s = t(3.2); toll = sum(np.sin(2 * np.pi * f * s) * np.exp(-s * d) / (i + 1)
                           for i, (f, d) in enumerate(((98 - 4 * k, .9), (196.7 - 8 * k, 1.4), (247 - 8 * k, 2.0), (392, 2.6))))
    save(f'RegentBell_{k}', mix(3.2, (bell, 0, .9), (toll, 0, .8)), [pick('impactBell_heavy', k) + f' {-9 - k} st', 'procedural toll partials'], .85)
for k in range(4):
    sec = .7 + .05 * k
    x = whoosh(sec, 200 + 30 * k, 1000 + 80 * k, 150, 900)
    chain = pitch(load('rpg_handleCoins2' if k % 2 else 'rpg_handleCoins'), -3 - k % 2)[:int(SR * sec)]
    latch = pitch(load('rpg_metalLatch'), -4)
    save(f'RegentWhoosh_{k}', mix(sec + .2, (x, 0, 1), (chain * env(len(chain), .02, .3), .05, .7), (latch, sec * .5, .3)),
         ['procedural heavy sweep', 'rpg_handleCoins -3/-4 st (chain rattle)', 'rpg_metalLatch -4 st'], .75)
for k in range(4):
    x = whoosh(.28, 700 + 100 * k, 3000, 400, 2400)
    scrape = load(f'rpg_drawKnife{k % 3 + 1}')
    save(f'RegentThrust_{k}', mix(.5, (x, 0, 1), (scrape / (np.abs(scrape).max() + 1e-9), 0, .25)),
         ['procedural fast thin sweep', f'rpg_drawKnife{k % 3 + 1} (normalised blade scrape)'], .7)

def flicker(seconds, rate, depth, r):
    # Random loudness flutter (real flames flutter several times a second; steady filtered
    # noise reads as electronic hiss).
    m = onepole(r.standard_normal(int(SR * seconds)), rate, stages=2)
    return 1 + depth * m / (np.abs(m).max() + 1e-9)

def crackles(seconds, per_second, r):
    # Fire crackle is wood snapping: short grains of real CC0 wood/stone impacts, pitched up,
    # each a different source, pitch, length and level, at a natural density. (The old
    # version used ~175-530 identical filtered clicks a second, which fuses into a buzz.)
    out = np.zeros(int(SR * seconds))
    sources = [pick('impact_impactWood_light', j) for j in range(5)] + [pick('impact_impactGeneric_light', j) for j in range(5)] + [pick('impact_impactWood_medium', j) for j in range(5)]
    for _ in range(int(seconds * per_second)):
        grain = pitch(load(sources[r.integers(len(sources))]), r.uniform(5, 13))[:int(SR * r.uniform(.01, .045))]
        grain = grain * np.exp(-np.linspace(0, r.uniform(4, 9), len(grain)))
        at = int(r.uniform(0, max(1e-3, seconds - .05)) * SR)
        out[at:at + len(grain)] += grain * r.uniform(.1, 1) ** 2
    return out

def fire(seconds, rumble=220, per_second=12, seed=0):
    # Organic fire bed: a broadband roar (no resonant band) with fast flutter, a slower low
    # body, and wood-grain crackle.
    r = np.random.default_rng(seed)
    roar = onepole(onepole(r.standard_normal(int(SR * seconds)), 1600, stages=2), 140, high=True) * 2.2 * flicker(seconds, 9, .45, r)
    body = onepole(r.standard_normal(int(SR * seconds)), rumble, stages=3) * 4 * flicker(seconds, 3.5, .35, r)
    return roar + body + crackles(seconds, per_second, r) * .9

def fire_whoosh(seconds, seed):
    # Flame rushing past or igniting: a real cloth flap pitched down (the classic fire-whoosh
    # source) under noise whose low-pass cutoff opens and closes (no resonance, so no laser
    # sweep), with flutter.
    r = np.random.default_rng(seed); n = int(SR * seconds); u = np.arange(n) / n
    arc = np.sin(np.pi * u) ** 1.3
    air = onepole(r.standard_normal(n), 250 + 2600 * arc, stages=2) * arc * 2.5 * flicker(seconds, 11, .3, r)
    cloth = pitch(load(f'rpg_cloth{seed % 4 + 1}'), -7 - seed % 3)[:n]
    return mix(seconds, (air, 0, 1), (cloth / (np.abs(cloth).max() + 1e-9), 0, .55))

for k in range(4):
    sec = .9
    flame = fire(sec, 300, 18, k) * env(int(SR * sec), .12, .5)
    rush = fire_whoosh(sec, k)
    bone = pitch(load(pick('impact_impactWood_light', k)), 3)
    save(f'RegentSkull_{k}', mix(sec, (flame, 0, .8), (rush, 0, 1), (bone, 0, .45)),
         ['organic fire bed (flutter roar, wood-grain crackle 18/s)', f'fire whoosh (rpg_cloth{k % 4 + 1} {-7 - k % 3} st + opening low-pass noise)', pick('impactWood_light', k) + ' +3 st (bone clack)'], .65)
for k in range(3):
    s = t(.9); swell = onepole(noise(.9), 1200, stages=2) * (s / .9) ** 3 * 3
    swell[-int(SR * .05):] *= np.linspace(1, 0, int(SR * .05))
    shimmer = bandpass(noise(.9), 5000 + 600 * k, 6) * (s / .9) ** 2
    thud = pitch(load(pick('impact_impactSoft_heavy', k)), -7)
    save(f'RegentBlink_{k}', mix(1.3, (swell, 0, 1), (shimmer, 0, .25), (thud, .88, .9)),
         ['reversed-style noise swell', 'high shimmer', pick('impactSoft_heavy', k) + ' -7 st'], .7)
for k in range(3):
    roar = (fire(1.4, 260, 26, 10 + k) + fire_whoosh(1.4, 10 + k) * .8) * env(int(SR * 1.4), .01, 1.0)
    crunch = pitch(load(pick('impact_impactMining', k + 2)), -8)
    save(f'RegentEruption_{k}', mix(1.4, (roar, 0, 1), (crunch, 0, 1.2), (sub(90, 40, .8, 5), 0, .4)),
         ['organic fire bed + fire whoosh', pick('impactMining', k + 2) + ' -8 st', 'sub'], .9, present=0.5)
for k in range(2):
    roar = (fire(2.4, 200, 30, 20 + k) + fire_whoosh(2.4, 20 + k) * .9) * env(int(SR * 2.4), .02, 1.8)
    crunch = pitch(load(pick('impact_impactMining', k)), -10)
    bell = pitch(load(pick('impact_impactBell_heavy', k + 3)), -12)
    save(f'RegentPyre_{k}', mix(2.6, (roar, 0, 1), (crunch, 0, 1.2), (sub(70, 30, 1.6, 2.5), 0, .5), (bell, .05, .45)),
         ['organic fire bed + fire whoosh', pick('impactMining', k) + ' -10 st', 'sub 70->30 Hz', pick('impactBell_heavy', k + 3) + ' -12 st'], .95, present=0.5)
for k in range(3):
    roar = (fire(1.6, 340, 20, 30 + k) + fire_whoosh(1.6, 30 + k) * .7) * env(int(SR * 1.6), .25, .8)
    save(f'RegentWakes_{k}', roar, ['organic rolling fire (flutter, wood-grain crackle 20/s)', 'fire whoosh'], .7)

# --- Ambience beds (seamless loops: crossfade the tail into the head) -------------------------
def loopable(x, fade):
    n = int(SR * fade); head, body = x[:n], x[n:]
    body[-n:] = body[-n:] * np.linspace(1, 0, n) + head * np.linspace(0, 1, n)
    return body

secs = 24
room = onepole(noise(secs + 2), 140, stages=3) * 10
wind = bandpass(noise(secs + 2), 420, 3) * (.5 + .5 * np.sin(2 * np.pi * t(secs + 2) / 9.0)) * .8
drips = np.zeros(int(SR * (secs + 2)))
at = 1.5
while at < secs:
    s = t(.08); f = 1800 + 1400 * rng.random()
    drip = np.sin(2 * np.pi * (f + 900 * s / .08) * s) * np.exp(-s * 60)
    i = int(SR * at); drips[i:i + len(drip)] += drip * (.05 + .06 * rng.random())
    at += 2.5 + 4 * rng.random()
save('AmbDungeon_0', loopable(room + wind + drips, 2), ['brown-noise room tone', 'slow wind band', 'random water drips'], .5, loop=True)
crackle = fire(10, 180, 7, 99) * .6
save('AmbFire_0', loopable(crackle, 2), ['organic brazier bed (flutter roar, wood-grain crackle 7/s)'], .6, loop=True)

# --- Voices of the dead (Freesound sources the owner downloaded; see CREDITS.md) ----------
# Research recipe: the scary layer is a human voice made "recognisable but wrong" (reversed,
# smeared, pitched); a high shriek over a low copy reads as something large; casting is a
# charge-up (reversed swell / riser / drone) that peaks on the release.
def smear(x, seconds, seed):
    # Cheap reverb-like smear: FFT convolution with a decaying noise burst.
    r = np.random.default_rng(seed); ir = r.standard_normal(int(SR * seconds)) * np.exp(-np.linspace(0, 6, int(SR * seconds)))
    n = len(x) + len(ir); y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)
    return y / (np.abs(y).max() + 1e-9)

def varispeed(x, start, end, seconds):
    # Pitch glide: playback rate moves from start to end over the output length.
    n = int(SR * seconds); rate = np.linspace(start, end, n)
    idx = np.cumsum(rate); idx = idx[idx < len(x) - 1]
    return np.interp(idx, np.arange(len(x)), x)

def fade(x, a, r):
    return x * env(len(x), a, r, 1.5)

def screech(x, seed):
    # The scream recording is a low moan (~2% of its energy above 2.5 kHz), so a treble shelf
    # alone adds little. Make it shrill: an octave-up copy, an exciter (a distorted high-passed
    # copy creates upper harmonics the recording lacks), a hiss through teeth that follows the
    # scream's loudness, then a +9 dB shelf above 2.5 kHz.
    r = np.random.default_rng(seed)
    up = pitch(x, 12)[:len(x)]; up = np.pad(up, (0, len(x) - len(up)))
    hp = onepole(x, 1500, high=True, stages=2)
    excite = np.tanh(6 * hp / (np.abs(hp).max() + 1e-9))
    follow = onepole(np.abs(x), 30, stages=2); follow /= follow.max() + 1e-9
    hiss = bandpass(r.standard_normal(len(x)), 4500, 1.5) * follow
    y = x / (np.abs(x).max() + 1e-9) + up / (np.abs(up).max() + 1e-9) * .45 + excite * .3 + hiss / (np.abs(hiss).max() + 1e-9) * .3
    return treble(y, 9)

def stereo_save(name, lr, layers, peak=.7, fade_s=4.0):
    # Music bed: seamless stereo loop (tail crossfaded into the head).
    n = int(SR * fade_s); head, body = lr[:n].copy(), lr[n:].copy()
    w = np.linspace(0, 1, n)[:, None]; body[-n:] = body[-n:] * (1 - w) + head * w
    body = body / (np.abs(body).max() + 1e-9) * peak
    with wave.open(os.path.join(OUT, name + '.wav'), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(body, -1, 1) * 32767).astype(np.int16).tobytes())
    manifest[name] = {'seconds': round(len(body) / SR, 3), 'layers': layers, 'loop': True, 'channels': 2}

if os.path.exists(os.path.join(SRC, 'fs_scream.wav')):
    scream, whispers, ghost = load('fs_scream'), load('fs_whispers'), load('fs_scatteredghost')
    vr = np.random.default_rng(77)
    def slice_(x, at, seconds): return x[int(SR * at):int(SR * (at + seconds))].copy()
    # Skull launch: a shriek (scream slice pitched up), the same slice an octave down for weight,
    # the fire rush and crackle, and the bone clack.
    for k in range(5):
        at = 2.2 + 1.4 * k + vr.uniform(0, .5); sec = .62 + .06 * (k % 3)
        cry = fade(pitch(slice_(scream, at, sec * 1.4), 4 + k % 4), .01, .35)
        low = fade(pitch(slice_(scream, at, sec * .6), -12), .02, .3)
        rush = fire_whoosh(.9, 40 + k); crack = crackles(.9, 14, np.random.default_rng(50 + k))
        bone = pitch(load(pick('impact_impactWood_light', k)), 3)
        cry = screech(cry, k)
        save(f'RegentSkull_{k}', mix(.95, (cry, 0, 1), (low, 0, .15), (rush, 0, .45), (crack, 0, .35), (bone, 0, .4)),
             [f'fs_scream {at:.1f}s +{4 + k % 4} st, screech (octave-up copy, exciter, hiss, +9 dB shelf)', 'fs_scream -12 st (weight)', 'fire whoosh', 'wood-grain crackle', pick('impactWood_light', k) + ' +3 st'], .98, drive=3.2)
    # Witness Circle dive: the scream glides upward as the skulls converge.
    for k in range(3):
        at = 3.0 + 2.2 * k
        cry = fade(varispeed(slice_(scream, at, 1.4), .85, 1.45, .8), .01, .25)
        save(f'RegentSkullDive_{k}', mix(.85, (screech(cry, 20 + k), 0, 1), (fire_whoosh(.85, 60 + k), 0, .4), (pitch(slice_(scream, at, .5), -12), 0, .12)),
             [f'fs_scream {at:.1f}s gliding x0.85->1.45, screech', 'fire whoosh', 'fs_scream -12 st'], .98, drive=3.2)
    # Orbiting skulls: smeared, doubled whispers.
    for k in range(4):
        at = 9 + 17 * k + vr.uniform(0, 4)
        w = slice_(whispers, at, 1.6); w = w / (np.abs(w).max() + 1e-9)
        dbl = pitch(w, -5)
        sm = smear(w, .6, k)[:int(SR * 2.2)]
        save(f'RegentWhisper_{k}', fade(mix(2.2, (w, 0, .8), (dbl, .04, .45), (sm, 0, .5)), .25, .8),
             [f'fs_whispers {at:.1f}s', 'same -5 st doubled', 'smeared tail'], .6)
    # Casting: whispers smeared then reversed so they swell INTO the release, an opening
    # riser and a ghost drone an octave down; a short soul-fire bloom on the release.
    for name, rise, count in (('RegentCast', .72, 4), ('RegentCastLong', 1.22, 2)):
        for k in range(count):
            at = 20 + 13 * k + (8 if rise > 1 else 0)
            w = slice_(whispers, at, rise); w = w / (np.abs(w).max() + 1e-9)
            swell = smear(w, .9, 10 + k)[::-1][-int(SR * rise):]
            swell = swell * np.linspace(0, 1, len(swell)) ** 1.6
            n = int(SR * rise); u = np.arange(n) / n
            riser = onepole(rng.standard_normal(n), 300 + 3500 * u ** 2, stages=2) * u ** 2 * 3
            drone = fade(pitch(slice_(ghost, 5 + 9 * k, rise * 2.2), -12), .2, .1)[:n]
            bloom = fire_whoosh(.5, 70 + k) * env(int(SR * .5), .005, .45)
            save(f'{name}_{k}', mix(rise + .5, (swell, 0, 1), (riser, 0, .55), (drone, 0, .5), (bloom, rise - .02, .7)),
                 [f'fs_whispers {at}s smeared + reversed (swell)', 'opening low-pass riser', 'fs_scatteredghost -12 st drone', 'soul-fire bloom on release'], .75)
    # Choir of the dead: wailing slices under the Witness Circle and the Pyre.
    for k in range(3):
        at = 6 + 18 * k
        c = fade(pitch(slice_(ghost, at, 3.4), -3), .6, 1.2)
        save(f'RegentChoir_{k}', mix(3.2, (c, 0, 1), (smear(c, .8, 30 + k)[:int(SR * 3.2)], 0, .35)),
             [f'fs_scatteredghost {at}s -3 st', 'smeared tail'], .6)
    # Boss music bed: the Scattered Ghost recording as a seamless stereo loop.
    with wave.open(os.path.join(SRC, 'fs_scatteredghost_stereo.wav')) as f:
        lr = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float64).reshape(-1, 2) / 32768
    stereo_save('MusicBoss_0', lr[int(SR * 1.5):int(SR * 68.5)], ['fs_scatteredghost_stereo 1.5-68.5 s, 4 s crossfade loop'])

json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
print('BOSSLAB game audio', len(manifest), 'files')
