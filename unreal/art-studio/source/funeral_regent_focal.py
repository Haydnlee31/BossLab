import bpy,bmesh,math,json,sys,hashlib
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from pathlib import Path
R=Path('/Users/haydn/Documents/BossLab');L=R/'unreal/art-studio/source/regent_focal_landmarks.json';J=json.loads(L.read_text());D=R/'unreal/art-studio/regent-focal-2026-11-09';E=R/'artifacts/art/regent-focal-2026-11-09';D.mkdir(exist_ok=True);E.mkdir(parents=True,exist_ok=True);args=sys.argv[sys.argv.index('--')+1:];A=int(args[0]);O=E/f'attempt-{A:02}';O.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
S=.075;Z=1.65;Y=-.065
def world(p):return (p[0]*S,Y-p[1]*S,Z+p[2]*S)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.76;return m
ivory=mat('neutral ivory clay',(.56,.54,.49));cloth=mat('neutral cloth clay',(.17,.18,.20));dark=mat('inner lining clay',(.025,.028,.032));steel=mat('neutral clasp clay',(.32,.34,.35))
def mesh(n,v,f,ma,sub=0,thick=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(ma)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=True
 if sub:m=o.modifiers.new('surface continuity','SUBSURF');m.levels=sub
 if thick:m=o.modifiers.new('actual inward shell thickness','SOLIDIFY');m.thickness=thick;m.offset=-1
 return o
# Shared facial constraints are actual mesh edges, all transformed together.
def samples(points,closed=False,steps=3):
 out=[]
 for i in range(len(points) if closed else len(points)-1):
  a=Vector(points[i]);b=Vector(points[(i+1)%len(points)])
  for k in range(steps):out.append(tuple(a.lerp(b,k/steps)))
 if not closed:out.append(tuple(points[-1]))
 return out
C=J['curves'];pos=C['outer_boundary_positive']['points_xyz'];outer=pos+[[-x,y,z] for x,y,z in pos[-2:0:-1]];eyes=[];paths=[(outer,True,'outer')]
for name,data in C.items():
 if name.startswith(('outer','hood')):continue
 pts=data['points_xyz'];closed=data['closed']
 if name.endswith('positive'):
  for sign in [1,-1]:
   pp=[(sign*x,y,z) for x,y,z in pts];paths.append((pp,closed,name+str(sign)))
   if name=='eye_positive':eyes.append(pp)
 else:paths.append((pts,closed,name))
for name,p in J['landmarks'].items():
 if name.endswith('positive'):paths.extend([([p],False,name),([[-p[0],p[1],p[2]]],False,name+'mirror')])
 else:paths.append(([p],False,name))
verts=[];depth=[];edges=[];lookup={};pathindices={}
def add(p):
 k=(round(p[0],7),round(p[2],7))
 if k in lookup:return lookup[k]
 lookup[k]=len(verts);verts.append(Vector((p[0],p[2])));depth.append(p[1]);return len(verts)-1
for pts,closed,name in paths:
 pp=samples(pts,closed,3) if len(pts)>1 else pts;ids=[add(p) for p in pp];pathindices[name]=ids
 edges.extend((ids[i],ids[(i+1)%len(ids)]) for i in range(len(ids) if closed else len(ids)-1))
# Smooth interpolating field fitted to authored 3D paths; dense unstructured interior
# sampling improves triangle aspect ratios without replacing explicit eye/feature topology.
control={}
for pts,closed,name in paths:
 for x,y,z in pts:control[(x,z)]=y
base=np.array(list(control));values=np.array(list(control.values()));delta=base[:,None,:]-base[None,:,:];rr=np.linalg.norm(delta,axis=2);K=rr**3;P=np.column_stack([np.ones(len(base)),base]);system=np.block([[K+np.eye(len(base))*.005,P],[P.T,np.zeros((3,3))]]);coef=np.linalg.solve(system,np.r_[values,[0,0,0]])
def field(x,z):
 r=np.linalg.norm(base-np.array([x,z]),axis=1);return float((r**3)@coef[:len(base)]+np.array([1,x,z])@coef[len(base):])
# Fixed low-discrepancy points; their location samples a field, never adds random relief.
for k in range(900):
 x=-1+2*((k*.61803398875)%1);z=3.2*((k*.41421356237)%1)
 if min((q-Vector((x,z))).length for q in verts)>.065:
  add((x,field(x,z),z))
v2,e2,f2,origv,orige,origf=delaunay_2d_cdt(verts,edges,[],1,1e-7)
def inside(q,poly):
 x,z=q;yes=False
 for i in range(len(poly)):
  a=poly[i];b=poly[i-1];ax,az=a[0],a[2];bx,bz=b[0],b[2]
  if ((az>z)!=(bz>z)) and x<(bx-ax)*(z-az)/(bz-az)+ax:yes=not yes
 return yes
vv=[]
for i,q in enumerate(v2):
 if origv[i]:d=field(q.x,q.y)
 else:
  nearby=sorted(((q-v).length_squared,k) for k,v in enumerate(verts))[:3];d=sum(depth[k]/max(a,1e-12) for a,k in nearby)/sum(1/max(a,1e-12) for a,k in nearby)
 vv.append(world((q.x,d,q.y)))
ff=[]
for face in f2:
 q=sum((v2[i] for i in face),Vector((0,0)))/len(face)
 if inside(q,outer) and not any(inside(q,eye) for eye in eyes):ff.append(face)
mask=mesh('continuous landmark mask with almond eyelid boundaries',vv,ff,ivory,1,.0025)
# Inspectable line constraints retained as metadata; no separate feature decoration.
mask['landmark_schema']=J['schema'];mask['landmark_file_sha256']=hashlib.sha256(L.read_bytes()).hexdigest();mask['feature_paths']=json.dumps(pathindices)
# Real closed fitted cranial volume, inset from temples/eye aperture; separate dark lining.
vv=[]
for z,rx,ry,cy in [(1.61,.035,.035,.005),(1.66,.045,.04,.008),(1.74,.060,.050,.012),(1.83,.062,.052,.015),(1.89,.040,.04,.012)]:
 for j in range(24):t=j*math.tau/24;vv.append((rx*math.cos(t),cy+ry*math.sin(t),z))
ff=[(i*24+j,i*24+(j+1)%24,(i+1)*24+(j+1)%24,(i+1)*24+j) for i in range(4) for j in range(24)]+[tuple(reversed(range(24))),tuple(range(96,120))];mesh('closed recessed skull volume',vv,ff,dark,1)
# Hood boundary follows exact JSON opening; arcs turn around measured cranial depth.
opening=samples(C['hood_opening_positive']['points_xyz'],False,3);back=J['hood']['crown_back_profile']
def backdepth(z):
 for a,b in zip(back,back[1:]):
  if a[2]>=z>=b[2]:return a[1]+(b[1]-a[1])*(a[2]-z)/(a[2]-b[2])
 return back[0 if z>back[0][2] else -1][1]
vv=[];N=32
for x,y,z in opening:
 for j in range(N+1):
  t=j/N*math.pi;xx=x*math.cos(t);yy=y+(backdepth(z)-y)*math.sin(t);zz=z-.26*math.sin(t)**2*max(0,min(1,(z-2.5)/.8))
  p=world((xx,yy,zz));rearfit=.055 if z<.5 else (.075-.04*max(0,min(1,(z-2.5)/.8)));p=(p[0],p[1]*(1-math.sin(t)**2)+max(p[1],rearfit)*math.sin(t)**2,p[2]);vv.append(p)
ff=[]
for i in range(len(opening)-1):
 for j in range(N):
  a=i*(N+1)+j;b=a+1;c=b+N+1;d=a+N+1
  ff.append((a,b,c,d))
hood_bottom=vv[-(N+1):]
hood=mesh('sewn hood opening crown and nape shell',vv,ff,cloth,1,.004)
bm=bmesh.new();bm.from_mesh(hood.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(hood.data);bm.free()
# Yoke actual support arcs: rear bridge + outer drape returns, front asymmetric load toward right clavicle.
def resample_curve(pts,n):
 lengths=[0]
 for a,b in zip(pts,pts[1:]):lengths.append(lengths[-1]+(Vector(b)-Vector(a)).length)
 result=[]
 for j in range(n):
  d=lengths[-1]*j/(n-1);i=next((k for k in range(len(lengths)-1) if lengths[k+1]>=d),len(lengths)-2);result.append(Vector(pts[i]).lerp(Vector(pts[i+1]),(d-lengths[i])/max(1e-8,lengths[i+1]-lengths[i])))
 return result
# Fitted sewn nape bridge joins the actual hood lower arc to yoke support.
rear32=resample_curve(J['shoulder_yoke']['rear_support_arc'],N+1)[::-1];bridge_v=[]
for r in range(5):
 t=r/4
 for j,(h,p) in enumerate(zip(hood_bottom,rear32)):
  a=Vector(h);b=Vector(world(p));q=a.lerp(b,t);q.y+=.006*math.sin(math.pi*t);bridge_v.append(q)
mesh('continuous sewn nape to yoke bridge',bridge_v,[(i*(N+1)+j,i*(N+1)+j+1,(i+1)*(N+1)+j+1,(i+1)*(N+1)+j) for i in range(4) for j in range(N)],cloth,1,.004)
rear=resample_curve(J['shoulder_yoke']['rear_support_arc'],25);outerarc=resample_curve(J['shoulder_yoke']['outer_drape_arc'],25);vv=[]
for r in range(7):
 t=r/6
 for j,(a,b) in enumerate(zip(rear,outerarc)):
  p=a.lerp(b,t);p.z-=.18*t;p.z+=.045*math.sin(t*math.pi)-.10*math.exp(-((j/24-.34)/.13)**2)*math.sin(t*math.pi);vv.append(world(p))
mesh('shoulder loaded rear yoke',vv,[(i*25+j,i*25+j+1,(i+1)*25+j+1,(i+1)*25+j) for i in range(6) for j in range(24)],cloth,2,.004)
front=resample_curve(J['shoulder_yoke']['front_support_arc'],25);vv=[]
for r in range(9):
 t=r/8
 for j,a in enumerate(front):
  u=j/24;p=a.copy();p.z-=t*(1.3+.7*(1-u));p.x*=1+.12*t;p.y+=.15*t+.16*math.sin(math.pi*t)*math.exp(-((u-.3-.20*t)/.14)**2)-.14*math.sin(math.pi*t)*math.exp(-((u-.60+.15*t)/.12)**2)
  vv.append(world(p))
mesh('diagonal clasp supported front shoulder fall',vv,[(i*25+j,i*25+j+1,(i+1)*25+j+1,(i+1)*25+j) for i in range(8) for j in range(24)],cloth,2,.004)
# Clasp supports reinforced tab at anatomical right (-X), modest geometry only.
bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.017,depth=.005,location=world((-.8,.47,-1.04)),rotation=(math.pi/2,0,0));bpy.context.object.name='right clavicle attachment clasp';bpy.context.object.data.materials.append(steel)
# No previous body scene is loaded or changed; focal study only.
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=760;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world.color=(.15,.15,.15)
for loc,power,size in [((2,-3,4),450,2),((-2,-1,2),180,2),((1,2,3),450,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.7))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO'
scene=D/f'regent-focal-{A:02}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
for name,loc,target,scale in [('head-front',(0,-3,1.78),(0,0,1.77),.40),('head-side',(3,0,1.78),(0,0,1.77),.40),('head-threequarter',(2,-3,2),(0,0,1.77),.43),('bust-front',(0,-3,1.7),(0,0,1.66),.70),('bust-back',(0,3,1.7),(0,0,1.66),.70)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(scene));mask=bpy.data.objects['continuous landmark mask with almond eyelid boundaries'];bm=bmesh.new();bm.from_mesh(mask.data);report={'landmark_sha256':hashlib.sha256(L.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'mask_vertices':len(bm.verts),'mask_faces':len(bm.faces),'mask_boundary_edges_before_solidify':sum(e.is_boundary for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'rigs':0,'method':'explicit director feature curves form constrained triangulation; genuine eye-loop holes, physical solidify rim, shared uniform transform','limits':'neutral focal construction only; no production retopology, global collision or artistic pass'};bm.free();(O/'readback.json').write_text(json.dumps(report,indent=2))
