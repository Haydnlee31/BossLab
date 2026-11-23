"""Exact-triangle pose audit; declared held-out synthetic poses are not engine tests."""
from pathlib import Path
import json,numpy as np
from repair_arm_weights import geometry,parse_fbx
R=Path(__file__).resolve().parents[4];O=R/'artifacts/art/bellbreaker-shoulder-2026-11-20';P=np.load(O/'measured-pose.npz');v=P['vertices'];f=P['faces'];names=P['names'].tolist();old=P['weights'];m=P['matrix'];region=P['region']
_,ff,_,nn,new=geometry(parse_fbx.parse(str(O/'SKM_BellbreakerForgeShoulder.fbx'))[0]);assert np.array_equal(ff,f) and names==nn
r=np.c_[v*[1,-1,1],np.ones(len(v))]
def area(p):return np.linalg.norm(np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]),axis=1)
rest=area(v);valid=rest>4e-6
edges=np.unique(np.sort(np.vstack((f[:,[0,1]],f[:,[1,2]],f[:,[2,0]])),axis=1),axis=0);rl=np.linalg.norm(v[edges[:,0]]-v[edges[:,1]],axis=1);good=rl>.0025

def rot(axis,deg):
 axis=np.array(axis,float);axis/=np.linalg.norm(axis);x,y,z=axis;C=np.array([[0,-z,y],[z,0,-x],[-y,x,0]]);t=np.radians(deg);return np.eye(3)+np.sin(t)*C+(1-np.cos(t))*C@C

def pose(w,axis,la,ra,el):
 pts=v.copy()
 for side,sg,ang in [('l',1,la),('r',-1,ra)]:
  sh=np.array([sg*.263,.026,1.413]);ep=np.array([sg*.375,.019,1.186]);R=rot(axis,ang);E=rot([1,0,0],el)
  upper=[i for i,n in enumerate(names) if n=='upperarm_'+side];lower=[i for i,n in enumerate(names) if n.endswith('_'+side) and not n.startswith(('ball','foot','calf','thigh','clavicle','upperarm'))]
  arm=(v-sh)@R.T+sh;fore=(((v-ep)@E.T+ep)-sh)@R.T+sh
  pts+=(arm-v)*w[:,upper].sum(1)[:,None]+(fore-v)*w[:,lower].sum(1)[:,None]
 return pts
cases=[('recorded_quake',None,True),('partial_lift',([.25,1,0],-70,45,30),True),('uneven_overhead',([.5,1,.1],-112,83,40),True),('sweep_followthrough',([.8,.3,.25],-52,-64,65),True),('heldout_forward_reach',([1,0,0],-55,-55,75),False),('heldout_side_raise',([0,1,0],-85,85,15),False),('heldout_crossbody',([.4,.6,.7],-45,65,90),False)]
out={'area_threshold_doubled_m2':4e-6,'edge_threshold_m':.0025,'same_triangles':len(f),'shoulder_region_triangles':int(region.sum()),'cases':{}}
for name,params,training in cases:
 rec={'used_by_weight_solver':training}
 for label,w in [('before',old),('after',new)]:
  pts=sum(w[:,j,None]*(r@m[j]) for j in range(len(names)))/[100,-100,100] if params is None else pose(w,*params)
  ratios=area(pts)/np.maximum(rest,1e-15);er=np.linalg.norm(pts[edges[:,0]]-pts[edges[:,1]],axis=1)/np.maximum(rl,1e-15)
  rec[label]={'whole_above2':int((valid&(ratios>2)).sum()),'whole_belowhalf':int((valid&(ratios<.5)).sum()),'shoulder_above2':int((region&(ratios>2)).sum()),'shoulder_belowhalf':int((region&(ratios<.5)).sum()),'shoulder_area_p01_p50_p99':np.quantile(ratios[region],[.01,.5,.99]).tolist(),'edge_log_rms':float(np.sqrt(np.mean(np.log(np.maximum(er[good],1e-10))**2)))}
 out['cases'][name]=rec
(O/'same-triangle-pose-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
