from pathlib import Path
import sys,json,struct,numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'unreal/art-studio/source/bellbreaker'))
from repair_arm_weights import geometry,parse_fbx
D=ROOT/'artifacts/unreal/bellbreaker-dialogue';O=ROOT/'artifacts/art/bellbreaker-shoulder-2026-11-20'
v,f,_,names,w=geometry(parse_fbx.parse(str(D/'SKM_BellbreakerForgeSkin.fbx'))[0])
raw=(D/'surface-final.bin').read_bytes();bn=(D/'surface-bones.txt').read_text().splitlines();nv,ni=struct.unpack_from('<2i',raw);dt=np.dtype([('geom','<f4',(9,)),('inf','<u2',(4,2))]);buf=np.frombuffer(raw,dt,count=nv,offset=8)
g=buf['geom'];rw=buf['inf'][:,:,1]/65535.;bi=np.array([names.index(b) if b in names else -1 for b in bn])[buf['inf'][:,:,0]];assert ((bi>=0)|(rw==0)).all();bi=np.maximum(bi,0)
r=np.c_[g[:,:3]/100,np.ones(nv)];n=len(names)*4;lhs=np.zeros((n,n));rhs=np.zeros((n,3))
for start in range(0,nv,2000):
 sl=slice(start,min(start+2000,nv));N=len(r[sl]);a=np.zeros((N,n))
 for j in range(4):
  for k in range(4):a[np.arange(N),bi[sl,j]*4+k]+=rw[sl,j]*r[sl,k]
 lhs+=a.T@a;rhs+=a.T@g[sl,3:6]
m=np.linalg.lstsq(lhs,rhs,rcond=1e-12)[0].reshape(-1,4,3)
pred=sum(rw[:,j,None]*np.einsum('ij,ijk->ik',r,m[bi[:,j]]) for j in range(4));err=np.linalg.norm(pred-g[:,3:6],axis=1)
vr=np.c_[v*[1,-1,1],np.ones(len(v))];sk=sum(w[:,j,None]*(vr@m[j]) for j in range(len(names)))
def area(p):return np.linalg.norm(np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]),axis=1)
a0=area(v);ratio=area(sk)/10000/np.maximum(a0,1e-15);cent=v[f].mean(1);should=(abs(cent[:,0])>.16)&(abs(cent[:,0])<.44)&(cent[:,2]>1.30)&(cent[:,2]<1.55)&(a0>4e-6)
rows=[]
for i in np.flatnonzero(should)[np.argsort(ratio[should])[-25:]]:
 weights=w[f[i]].mean(0);rows.append({'face':int(i),'ratio':float(ratio[i]),'center':cent[i].tolist(),'weights':{names[j]:round(float(weights[j]),3) for j in np.flatnonzero(weights>.02)}})
out={'vertices':len(v),'triangles':len(f),'palette_fit_cm':np.quantile(err,[.5,.99,1]).tolist(),'shoulder_triangles':int(should.sum()),'shoulder_above2':int((should&(ratio>2)).sum()),'shoulder_belowhalf':int((should&(ratio<.5)).sum()),'largest_shoulder_faces':rows}
(O/'diagnosis.json').write_text(json.dumps(out,indent=2));np.savez(O/'measured-pose.npz',matrix=m,vertices=v,faces=f,weights=w,names=names,sk=sk,region=should,ratios=ratio,rawgeom=g)
print(json.dumps(out,indent=2))
