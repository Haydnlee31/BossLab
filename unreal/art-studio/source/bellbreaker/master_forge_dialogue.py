"""Master and split the selected 24 kHz Bellbreaker performance at its measured breath gaps."""
from pathlib import Path
import hashlib
import json
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[4] / 'artifacts/bellbreaker-dialogue'
LINES = (
    ('Challenge', "I've buried better steel than that.", 0, 2.25),
    ('PhaseBreak', "Hear that crack? She'll ring once more.", 2.51, 5.86),
    ('Defeat', "Good steel.", 6.57, 7.75),
)
def save(path,signal,rate):
    pcm=np.rint(signal*32767).astype('<i2')
    with wave.open(str(path),'wb') as out:
        out.setparams((1,2,rate,0,'NONE',''))
        out.writeframes(pcm.tobytes())

def main():
    with wave.open(str(ROOT/'performance.wav')) as source:
        assert source.getnchannels()==1 and source.getsampwidth()==2
        rate=source.getframerate()
        samples=np.frombuffer(source.readframes(source.getnframes()),'<i2').astype(float)/32768
    assert rate==24000 and len(samples)==191445, 'New generated performances need a new edit.'
    receipts={}; reel=[]
    for name,line,start,end in LINES:
        clip=samples[round(start*rate):round(end*rate)].copy()
        # Leave vocal grit, attack and pitch intact. Set conservative headroom for the busy game mix.
        clip-=np.mean(clip)
        clip*=min(.82/np.max(np.abs(clip)),10**(-19/20)/np.sqrt(np.mean(clip**2)))
        fade=round(rate*.009)
        clip[:fade]*=np.linspace(0,1,fade)
        clip[-fade:]*=np.linspace(1,0,fade)
        path=ROOT/(name+'.wav')
        save(path,clip,rate)
        receipts[name]={'line':line,'seconds':len(clip)/rate,'peak_dBFS':float(20*np.log10(max(abs(clip)))),
                        'rms_dBFS':float(10*np.log10(np.mean(clip**2))),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        reel.extend((clip,np.zeros(round(rate*.65))))
    save(ROOT/'audition.wav',np.concatenate(reel[:-1]),rate)
    (ROOT/'takes.json').write_text(json.dumps(receipts,indent=2)+'\n')

if __name__=='__main__':
    main()
