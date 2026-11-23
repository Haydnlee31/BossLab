"""Reweight the existing shoulder support across four fixed poses; preserve geometry/bind/UV.
The recorded pose is diagnostic, not a guarantee over every gameplay pose.
Run shoulder_diagnose.py first using the preserved original engine probe.
"""
from pathlib import Path
import sys,json,array,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[4];O=ROOT/'artifacts/art/bellbreaker-shoulder-2026-11-20'
from repair_arm_weights import geometry,parse_fbx,field,write_doc,unchanged_signature
p=np.load(O/'measured-pose.npz');m=p['matrix'];f=p['faces'];v=p['vertices'];w=p['weights'];names=p['names'].tolist();region=p['region'];vr=np.c_[v*[1,-1,1],np.ones(len(v))]
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
mask=smooth((v[:,2]-1.28)/.07)*(1-smooth((v[:,2]-1.55)/.05))*smooth((abs(v[:,0])-.12)/.05)*(1-smooth((abs(v[:,0])-.40)/.07))
rest=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1);valid=rest>4e-6
# Multi-pose edge-length regularization, not one-frame shape fitting.
sel=np.flatnonzero(mask>.001);active=np.flatnonzero(w[sel].sum(0)>1e-6);ids={a:i for i,a in enumerate(sel)}
e=np.unique(np.sort(np.vstack((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]])),axis=1),axis=0);restlen=np.linalg.norm(v[e[:,1]]-v[e[:,0]],axis=1);e=e[(restlen>.0025)&((mask[e[:,0]]>.001)|(mask[e[:,1]]>.001))];rl=np.linalg.norm(v[e[:,1]]-v[e[:,0]],axis=1);a,b=e.T
N=len(v);K=len(active)
T=np.zeros((4,N,K,3));T[0]=np.stack([vr@m[j]/[100,-100,100] for j in active],axis=1)
def rot(axis,deg):
 axis=np.array(axis,float);axis/=np.linalg.norm(axis);x,y,z=axis;C=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);t=np.radians(deg);return np.eye(3)+np.sin(t)*C+(1-np.cos(t))*C@C
for k,(axis,la,ra,el) in enumerate([([.25,1,0],-70,45,30),([.5,1,.1],-112,83,40),([.8,.3,.25],-52,-64,65)],1):
 T[k]=v[:,None,:]
 for side,sg,ang in [('l',1,la),('r',-1,ra)]:
  sh=np.array([sg*.263,.026,1.413]);ep=np.array([sg*.375,.019,1.186]);R=rot(axis,ang);E=rot([1,0,0],el)
  for ci,j in enumerate(active):
   n=names[j]
   if n=='upperarm_'+side:T[k,:,ci]=(v-sh)@R.T+sh
   elif n.endswith('_'+side) and not n.startswith(('ball','foot','calf','thigh','clavicle','upperarm')):T[k,:,ci]=(((v-ep)@E.T+ep)-sh)@R.T+sh
q=w[:,active].copy();base=q.copy();allowed=q>0;fixed=np.stack([sum(w[:,j,None]*(vr@m[j]/[100,-100,100]) for j in range(len(names)) if j not in active)]+[np.zeros_like(v) for _ in range(3)])
# Active columns include all weights in modified vertices; frozen outside vertices keep their original transforms.
tf=f[region];ta=np.linalg.norm(np.cross(v[tf[:,1]]-v[tf[:,0]],v[tf[:,2]]-v[tf[:,0]]),axis=1)
M=np.zeros((len(sel),K));V=M.copy();history=[]
for it in range(350):
 grad=np.zeros((N,K));loss=0
 for k in range(4):
  pts=np.einsum('nk,nkj->nj',q,T[k])+fixed[k]
  ed=pts[b]-pts[a];L=np.maximum(np.linalg.norm(ed,axis=1),.0001);log=np.log(L/rl);loss+=np.mean(log**2)
  force=2*np.clip(log,-3,3)[:,None]*ed/L[:,None]**2
  gp=np.zeros((N,3))
  for j in range(3):gp[:,j]=np.bincount(b,weights=force[:,j],minlength=N)-np.bincount(a,weights=force[:,j],minlength=N)
  u=pts[tf[:,1]]-pts[tf[:,0]];z=pts[tf[:,2]]-pts[tf[:,0]];cr=np.cross(u,z);ar=np.maximum(np.linalg.norm(cr,axis=1),1e-9);normal=cr/ar[:,None];lg=np.log(ar/ta);coef=.35*2*np.clip(lg,-3,3)/ar;gu=np.cross(z,normal)*coef[:,None];gz=np.cross(normal,u)*coef[:,None]
  for j in range(3):gp[:,j]+=np.bincount(tf[:,1],weights=gu[:,j],minlength=N)+np.bincount(tf[:,2],weights=gz[:,j],minlength=N)-np.bincount(tf[:,0],weights=gu[:,j]+gz[:,j],minlength=N)
  loss+=.35*np.mean(lg**2)
  grad+=np.einsum('nj,nkj->nk',gp,T[k]-pts[:,None,:])
 grad=grad[sel]/4+0.4*(q[sel]-base[sel]);grad*=mask[sel,None]
 M=.9*M+.1*grad;V=.999*V+.001*grad**2
 q[sel]-=.002*(M/(1-.9**(it+1)))/(np.sqrt(V/(1-.999**(it+1)))+1e-8)
 q[sel]=np.maximum(q[sel],0)*allowed[sel];q[sel]/=np.maximum(q[sel].sum(1)[:,None],1e-10)
 if it%50==0:history.append([it,loss]);print(it,loss,flush=True)
new=w.copy();new[sel]=0;new[np.ix_(sel,active)]=q[sel];ix=np.argsort(new,axis=1)[:,:-4];np.put_along_axis(new,ix,0,axis=1);new/=new.sum(1)[:,None]
np.save(O/'weights-constrained.npy',new);(O/'constrained-optimizer-history.json').write_text(json.dumps({'objective':'four-pose log edge length + prior; edges >2.5mm; 350 fixed steps','history':history,'vertices':len(sel),'bones':[names[i] for i in active]}))
sk=sum(new[:,j,None]*(vr@m[j]) for j in range(len(names)));ratio=np.linalg.norm(np.cross(sk[f[:,1]]-sk[f[:,0]],sk[f[:,2]]-sk[f[:,0]]),axis=1)/10000/np.maximum(rest,1e-15)
print('FINAL',int((region&(ratio>2)).sum()),int((region&(ratio<.5)).sum()),int((valid&(ratio>2)).sum()),int((valid&(ratio<.5)).sum()))

source=ROOT/'artifacts/unreal/bellbreaker-dialogue/SKM_BellbreakerForgeSkin.fbx'
doc,version=parse_fbx.parse(str(source));sig=unchanged_signature(doc);_,_,clusters,_,old=geometry(doc)
new[mask<=.001]=old[mask<=.001]
for j,c in enumerate(clusters):
 ids=np.flatnonzero(new[:,j]>0)
 field(c,b'Indexes').props[0]=array.array('i',ids.astype('<i4').tobytes())
 field(c,b'Weights').props[0]=array.array('d',new[ids,j].astype('<f8').tobytes())
target=O/'SKM_BellbreakerForgeShoulder.fbx';write_doc(doc,version,target)
check=parse_fbx.parse(str(target))[0];vv,ff,_,nn,ww=geometry(check)
assert np.array_equal(vv,v) and np.array_equal(ff,f) and nn==names
assert unchanged_signature(check)==sig and np.allclose(ww,new,atol=0,rtol=0)
report={'source':str(source.relative_to(ROOT)),'target':str(target.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'vertices':len(v),'triangles':len(f),'geometry_and_triangles_exact':True,'non_geometry_bind_signature':sig,'changed_weight_vertices':int((abs(old-new).max(1)>1e-9).sum()),'max_influences':int((new>0).sum(1).max()),'weight_sum_max_error':float(abs(new.sum(1)-1).max()),'original_bone_support_only':bool(((new>0)&(old==0)).sum()==0),'scope':'Weights only on existing shoulder geometry; no new rest mesh, UV, normals, skeleton or engine-pose changes.'}
(O/'model-handoff.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
