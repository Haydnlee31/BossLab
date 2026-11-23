"""Original Bellbreaker performance design. No source samples, TTS, model or third-party voice.
Run: .venv-gen3d/bin/python unreal/art-studio/source/bellbreaker/forge_voice.py
"""
from pathlib import Path
import json, wave
import numpy as np

OUT=Path(__file__).resolve().parents[4]/"artifacts/bellbreaker-voice"
SR=32000
# Duration, fundamental contour, first/second formant (closed throat to open mouth), breath proportion.
TAKES={
 "HeaveA":(.81,[82,76,111,72],[330,420,655,350],[1160,1110,980,1100],.17),
 "HeaveB":(1.03,[72,70,97,63],[300,360,530,320],[1130,1090,970,995],.23),
 "ReleaseA":(.46,[119,148,98,65],[430,820,635,380],[1210,1340,1030,920],.26),
 "ReleaseB":(.53,[104,137,86,58],[400,730,530,345],[1180,1250,980,860],.30),
 "BreakRoar":(1.80,[69,101,137,64],[310,710,795,320],[1120,1060,1350,880],.32),
 "DeathBreath":(1.68,[76,62,53,40],[540,400,330,260],[1120,990,890,780],.53),
}
def curve(t, vals): return np.interp(t,np.linspace(0,1,len(vals)),vals)
def band(noise,lo,hi):
 f=np.fft.rfftfreq(len(noise),1/SR)
 gain=(1-np.exp(-(f/lo)**3))*np.exp(-(f/hi)**3)
 x=np.fft.irfft(np.fft.rfft(noise)*gain,n=len(noise));return x/(np.std(x)+1e-12)
def reson(x,hz,bw):
 r=np.exp(-np.pi*bw/SR);a=2*r*np.cos(2*np.pi*hz/SR);y=np.zeros(len(x));u=v=0.
 for i in range(len(x)):
  q=(1-r)*x[i]+a[i]*u-r*r*v; y[i]=q;v,u=u,q
 return y
def vocal(key, params, seed):
 dur,pitch,f1,f2,breath=params;rng=np.random.default_rng(seed);t=np.arange(round(dur*SR))/SR;u=t/dur
 rnd=curve(u,rng.normal(0,1,round(dur*73)+2))
 hz=curve(u,pitch)*(1+.038*rnd+.025*np.sin(2*np.pi*7*t))
 # Derivative of asymmetric glottal pulse plus alternating-cycle creak and turbulent airflow.
 ph=np.cumsum(hz)/SR; frac=ph%1
 source=(np.exp(-((frac-.10)/.055)**2)-.42*np.exp(-((frac-.26)/.13)**2))*(.7+.30*np.sin(np.pi*ph)+.15*rnd)
 n=band(rng.normal(size=len(t)),230,5100); source+=breath*.18*n
 mouth=1+.014*rnd; x=sum(w*reson(source,curve(u,ff)*mouth,bw) for w,ff,bw in [(1,f1,75),(.88,f2,103),(.53,[2240,2370,2100,1970],153),(.24,[3400,3480,3100,2880],210)])
 # An intake before the squeeze, and an unpitched release rather than a looping buzz.
 opening=curve(u,[0,.16,1,.88,.67,.11,0]) if 'Release' not in key else curve(u,[0,1,.77,.34,.07,0])
 if key=='DeathBreath':opening=curve(u,[0,.8,.43,.22,.10,0])
 air=np.sin(np.pi*u)**1.5*(.13+.9*np.exp(-((u-.13)/.10)**2)+.75*np.exp(-((u-.78)/.2)**2))
 y=x*opening+.16*breath*n*air
 return y
def forge():
 # Circularly generated noise, bellows, coke pops and a low subharmonic furnace draft.
 rng=np.random.default_rng(771);dur=14;n=dur*SR;t=np.arange(n)/SR;u=t/dur
 def noise():return rng.normal(size=n)
 surge=(.5+.5*np.sin(2*np.pi*3*u+.48*np.sin(2*np.pi*u)))**2
 y=.35*band(noise(),35,245)+(.11+.15*surge)*band(noise(),310,1900)
 for start in rng.integers(0,n,94):
  m=rng.integers(80,950);k=np.arange(m)
  np.add.at(y,(start+k)%n,np.exp(-6*k/m)*rng.normal(size=m)*rng.uniform(.05,.28))
 y+=.08*np.sin(2*np.pi*679*u+.3*np.sin(2*np.pi*2*u))*(.45+.55*surge)
 return y
def save(name,x,peak):
 x=x-x.mean();x=np.tanh(x/np.percentile(np.abs(x),99.7)*.85);x=x*(peak/np.max(np.abs(x))); pcm=(x*32767).round().astype('<i2')
 path=OUT/(name+'.wav')
 with wave.open(str(path),'wb') as h:h.setparams((1,2,SR,len(x),'NONE',''));h.writeframes(pcm.tobytes())
 with wave.open(str(path),'rb') as h:z=np.frombuffer(h.readframes(h.getnframes()),'<i2')/32768.
 assert len(z)==len(x) and np.isfinite(z).all() and np.max(np.abs(z))<1
 return dict(seconds=len(z)/SR,peak_dbfs=round(20*np.log10(np.max(np.abs(z))),2),rms_dbfs=round(10*np.log10(np.mean(z*z)),2))
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True); stats={}; reel=[]
 for i,(name,cfg) in enumerate(TAKES.items()):
  x=vocal(name,cfg,1001+i);x[:256]*=np.linspace(0,1,256);x[-640:]*=np.linspace(1,0,640)
  stats[name]=save(name,x,.80 if name!='DeathBreath' else .61)
  with wave.open(str(OUT/(name+'.wav')),'rb') as h:reel.extend([np.frombuffer(h.readframes(h.getnframes()),'<i2'),np.zeros(SR//3,dtype='<i2')])
 stats['forge_breath_v0']=save('forge_breath_v0',forge(),.45)
 with wave.open(str(OUT/'audition.wav'),'wb') as h:h.setparams((1,2,SR,0,'NONE',''));h.writeframes(np.concatenate(reel).tobytes())
 (OUT/'levels.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
