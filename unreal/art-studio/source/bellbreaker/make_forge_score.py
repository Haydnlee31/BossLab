"""Anvil Measure — original sample-free workshop processional, stereo PCM loop."""
from pathlib import Path
import math, wave
import numpy as np
root=Path(__file__).resolve().parents[4]
sr=32000; beat=60/80; bar=beat*3; duration=16*bar; n=round(sr*duration)
mix=np.zeros((n,2)); rng=np.random.default_rng(963)
def note(pos,pitch,length,gain,kind,pan):
 t=np.arange(round(length*sr))/sr; f=440*2**((pitch-69)/12)
 if kind=='wire':
  # Paired iron strings: inharmonic partials and a small sympathetic after-ring.
  y=sum((1/k**1.5)*np.sin(2*np.pi*f*k*(1+.00065*k*k)*t)*np.exp(-t*(1.5+k*.7)) for k in range(1,7)); attack=.008
 elif kind=='skin':
  y=np.sin(2*np.pi*(f*t+f*.042*(1-np.exp(-t/.042))))*np.exp(-6*t)
  y+=.12*rng.standard_normal(len(t))*np.exp(-42*t);attack=.004
 else:
  # Low bowed string, with a finite bow stroke and a little hand vibrato.
  phase=2*np.pi*f*t+.09*np.sin(2*np.pi*4.2*t);y=sum(np.sin(k*phase)*(.68**(k-1))/k for k in range(1,7));attack=.18
 env=np.minimum(t/attack,1)*np.minimum((length-t)/(.22 if kind=='bow' else .04),1)
 ix=(round(pos*sr)+np.arange(len(t)))%n; y*=gain*env
 for ch,p in enumerate((1-pan,pan)): np.add.at(mix[:,ch],ix,y*math.sqrt(p))
for i,bass in enumerate([38,38,41,36,38,43,41,36,38,38,41,43,46,43,36,38]):
 p=i*bar
 note(p,bass-8,.7,.29,'skin',.49)
 if i%4!=3: note(p+beat*2.25,43,.4,.11,'skin',.64)
 if i%2==0: note(p+.11,bass,bar*1.65,.13,'bow',.35)
 for j,offset in enumerate(([0,1.5],[.5,2],[0,1,2.5],[1.5])[i%4]):
  note(p+offset*beat,bass+[19,12,24][j],1.25,.095 if j==0 else .065,'wire',.28 if j%2 else .7)
# Circular early reflections preserve periodicity across the export boundary.
dry=mix.copy()
for sec,g in ((.049,.11),(.093,.07),(.151,.04)): mix+=np.roll(dry[:,::-1],round(sec*sr),axis=0)*g
mix*=.65/max(np.abs(mix).max(),1e-6)
out=root/'artifacts/unreal/bellbreaker-weight/anvil-measure.wav';out.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(out),'wb') as w:w.setparams((2,2,sr,n,'NONE',''));w.writeframes((mix*32767).astype('<i2').tobytes())
