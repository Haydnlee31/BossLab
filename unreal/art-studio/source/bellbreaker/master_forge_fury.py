"""Master the chosen fury take without changing its pitch or flattening shouted syllables."""
import hashlib
import json
from pathlib import Path
import wave
import numpy as np
from master_forge_dialogue import save

OUT = Path(__file__).resolve().parents[4] / 'artifacts/bellbreaker-fury'
EDITS = (
    ('Challenge', 'You came for my bell? Lift it!', 0, 2.91),
    ('PhaseBreak', 'You cracked her! She was all I had!', 2.88, 5.75),
    ('Defeat', 'Ring on.', 5.8, 6.696875),
)
def main():
    with wave.open(str(OUT/'performance.wav')) as source:
        rate = source.getframerate()
        samples = np.frombuffer(source.readframes(source.getnframes()), '<i2').astype(float)/32768
        assert rate == 24000 and len(samples) == 160725 and source.getnchannels() == 1
    receipts = {}
    audition = []
    for name, line, start, end in EDITS:
        clip = samples[round(rate*start):round(rate*end)].copy()
        clip -= clip.mean()
        clip *= min(.84/max(abs(clip)), .145/np.sqrt(np.mean(clip**2)))
        fade = round(rate*.008)
        clip[:fade] *= np.linspace(0,1,fade)
        clip[-fade:] *= np.linspace(1,0,fade)
        destination = OUT/(name+'.wav')
        save(destination,clip,rate)
        receipts[name] = dict(line=line, seconds=len(clip)/rate,
            peak_dbfs=round(20*np.log10(max(abs(clip))),2),
            rms_dbfs=round(10*np.log10(np.mean(clip**2)),2),
            sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
        audition.extend([clip,np.zeros(round(rate*.65))])
    save(OUT/'audition.wav',np.concatenate(audition[:-1]),rate)
    (OUT/'takes.json').write_text(json.dumps(receipts,indent=2)+'\n')

if __name__ == '__main__':
    main()
