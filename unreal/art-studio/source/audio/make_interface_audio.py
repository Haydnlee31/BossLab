"""Original procedural interface score/cues; no samples, models, or downloads.
Run from project root: .venv-gen3d/bin/python unreal/art-studio/source/audio/make_interface_audio.py
"""
from pathlib import Path
import hashlib
import json
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'artifacts/audio-interface-2026-11-14/out'
RATE = 48000


def note(midi, duration, velocity=1., pan=0.):
    """Soft struck strings: deterministic partials with independent exponential tails.

    No noise source or sustained oscillator: all partials decay. The 12ms raised
    cosine attack and 120ms release eliminate discontinuities at note boundaries.
    """
    t = np.arange(round(duration * RATE), dtype=np.float64) / RATE
    f = 440. * 2. ** ((midi - 69) / 12.)
    mono = np.zeros_like(t)
    for harmonic, strength in [(1, 1.), (2, .27), (3, .105), (4, .035), (5, .014)]:
        # Slight string inharmonicity, subtle enough to avoid metallic beating.
        freq = f * harmonic * np.sqrt(1 + .000025 * harmonic * harmonic)
        tail = np.exp(-t / (1.05 / harmonic ** .58))
        mono += strength * np.sin(2 * np.pi * freq * t) * tail
    attack = .5 - .5 * np.cos(np.pi * np.minimum(t / .012, 1.))
    release = .5 - .5 * np.cos(np.pi * np.clip((duration - t) / .12, 0, 1))
    mono *= attack * release * velocity * .15
    return mono[:, None] * np.array([np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)])[None, :]


def place(track, start, midi, duration=3., velocity=1., pan=0.):
    source = note(midi, duration, velocity, pan)
    offset = round(start * RATE)
    length = min(len(source), len(track) - offset)
    if length > 0:
        track[offset:offset + length] += source[:length]


def encode(name, samples):
    assert np.isfinite(samples).all()
    assert np.max(np.abs(samples)) < .95, 'No clipping/limiter needed'
    pcm = np.round(samples * 32767).astype('<i2')
    path = OUT / f'{name}.wav'
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())
    decoded = pcm.astype(np.float64) / 32768.
    rms = float(np.sqrt(np.mean(decoded ** 2)))
    return {'file': str(path.relative_to(ROOT)), 'seconds': len(pcm) / RATE,
            'sample_rate': RATE, 'channels': 2, 'pcm_bits': 16,
            'peak_dbfs': float(20 * np.log10(max(np.max(np.abs(decoded)), 1e-12))),
            'rms_dbfs': float(20 * np.log10(max(rms, 1e-12))),
            'seam_max_channel_step': float(np.max(np.abs(decoded[-1] - decoded[0]))),
            'first_250ms_peak': float(np.max(np.abs(decoded[:RATE // 4]))),
            'last_250ms_peak': float(np.max(np.abs(decoded[-RATE // 4:]))),
            'clipped_samples': int(np.sum(np.abs(pcm.astype(np.int32)) >= 32767)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    music = np.zeros((32 * RATE, 2), dtype=np.float64)
    # Original D-minor modal miniature, four separated phrases. No bass drone,
    # percussion, noise bed or dense looping arpeggio. Final note ends at 30s.
    melody = [(1., 62, .92), (2.5, 69, .63), (4., 65, .73), (5.75, 64, .56),
              (9., 62, .79), (10.5, 60, .65), (12.5, 57, .62),
              (16.5, 65, .76), (18., 69, .60), (19.5, 72, .54), (21.25, 70, .52),
              (25., 69, .65), (26.5, 65, .65), (28., 62, .72)]
    for i, (onset, pitch, strength) in enumerate(melody):
        place(music, onset, pitch, min(3., 30. - onset), strength, (-.18, .12, -.05)[i % 3])
    for onset, pitch in [(1., 50), (9., 46), (16.5, 48), (25., 50)]:
        place(music, onset, pitch, 3.5, .34, -.25)
    confirm = np.zeros((round(.36 * RATE), 2))
    place(confirm, 0., 74, .29, .42, -.12)
    place(confirm, .065, 81, .295, .25, .12)
    adjust = np.zeros((round(.20 * RATE), 2))
    place(adjust, 0., 69, .20, .29, 0.)
    results = {name: encode(name, signal) for name, signal in
               [('MenuMusic_0', music*10**(10/20)), ('UIConfirm_0', confirm*2), ('UIAdjust_0', adjust*2)]}
    report = {'provenance': 'Original BossLab procedural composition and additive struck-string synthesis. No external samples, models, downloads or paid services.',
              'composition': 'D minor; fourteen melody notes, four quiet low notes; sparse four-phrase 32-second loop; silence at both loop boundaries.',
              'processing': 'Music +10dB, cues +6dB after actual Unreal mix measurement; 48kHz stereo PCM16; natural exponential partial decay, cosine attack/release; no noise, distortion, compressor or limiter.',
              'listening_status': 'Numerical checks only; human listening and in-game mix validation pending.',
              'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'sounds': results}
    (OUT.parent / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
