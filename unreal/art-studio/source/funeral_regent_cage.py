import bpy,bmesh,math,json,sys,hashlib
from mathutils import Vector
from pathlib import Path
R=Path('/Users/haydn/Documents/BossLab');D=R/'unreal/art-studio/regent-cage-2026-11-09';E=R/'artifacts/art/regent-cage-2026-11-09';D.mkdir(exist_ok=True);E.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:];A=int(args[0]) if args else 1;O=E/f'attempt-{A:02}';O.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=640;s.render.resolution_y=800;s.render.resolution_percentage=100;s.world.color=(.15,.15,.15);s.render.film_transparent=False
def material(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8;return m
skin=material('anatomical clay',(.28,.29,.30));metal=material('plate clay',(.46,.47,.48));cloth=material('mantle clay',(.16,.17,.19));bone=material('mask clay',(.62,.60,.55));recess=material('recess clay',(.035,.04,.045))
def mesh(n,v,f,ma,sub=0,thick=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);me.materials.append(ma)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=True
 if sub:m=o.modifiers.new('control cage smoothing','SUBSURF');m.levels=sub
 if thick:m=o.modifiers.new('sewn shell thickness','SOLIDIFY');m.thickness=thick
 return o
# Explicit torso rings. Two side patches omitted and their boundary loops bridged into arms.
v=[];f=[];N=12
rows=[(.99,.15,.095),(1.10,.145,.095),(1.25,.165,.105),(1.40,.205,.115),(1.52,.215,.095),(1.60,.055,.052),(1.65,.048,.047),(1.68,.052,.055),(1.72,.074,.072),(1.80,.078,.077),(1.87,.063,.065),(1.90,.030,.032)]
for z,rx,ry in rows:
 for j in range(N):t=j*math.tau/N;v.append((rx*math.cos(t),ry*math.sin(t),z))
for i in range(len(rows)-1):
 for j in range(N):
  if i==3 and j in [11,0,5,6]:continue
  f.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
f.append(tuple(range((len(rows)-1)*N,len(rows)*N)))
def bridge(old,coords):
 new=list(range(len(v),len(v)+len(coords)));v.extend(coords)
 for j in range(len(old)):f.append((old[j],old[(j+1)%len(old)],new[(j+1)%len(old)],new[j]))
 return new
for sign,loop in [(1,[3*N+11,3*N,3*N+1,4*N+1,4*N,4*N+11]),(-1,[3*N+5,3*N+6,3*N+7,4*N+7,4*N+6,4*N+5])]:
 # Six true boundary vertices continue to shoulder/elbow/wrist/palm/tip sections.
 for x,z,ry,rz in [(sign*.245,1.46,.069,.087),(sign*.28,1.36,.062,.073),(sign*.32,1.23,.049,.056),(sign*.335,1.20,.047,.052),(sign*.37,1.10,.044,.05),(sign*.395,1.015,.028,.03),(sign*.405,.975,.036,.042),(sign*.41,.93,.037,.044),(sign*.415,.88,.023,.022)]:
  coords=[]
  for j in range(6):t=math.radians([-135,-180,-225,-315,-360,-405][j]);coords.append((x+sign*rz*.93*math.cos(t),ry*math.sin(t),z+rz*.37*math.cos(t)))
  loop=bridge(loop,coords)
 f.append(tuple(reversed(loop)))
# Crotch partition: two bottom outlines share a deliberate central bridge, not overlapping tubes.
c=len(v);v.append((0,0,.99))
for sign,loop in [(1,[9,10,11,0,1,2,3,c]),(-1,[3,4,5,6,7,8,9,c])]:
 for z,x,rx,ry,cy in [(.91,sign*.10,.078,.079,0),(.73,sign*.11,.070,.073,0),(.56,sign*.12,.052,.056,-.008),(.52,sign*.12,.052,.052,-.008),(.32,sign*.13,.048,.052,.008),(.13,sign*.13,.033,.039,0),(.075,sign*.13,.057,.105,-.055),(.008,sign*.13,.058,.13,-.07),(.0,sign*.13,.058,.13,-.07),(.0,sign*.13,.050,.12,-.07)]:
  coords=[]
  for j in range(8):t=math.radians(([-135,-90,-45,0,45,90,135,180] if sign==1 else [45,90,135,180,225,270,315,360])[j]);coords.append((x+rx*math.cos(t),cy+ry*math.sin(t),z))
  loop=bridge(loop,coords)
 f.append(tuple(reversed(loop)))
body=mesh('ONE explicitly bridged body cage',v,f,skin,1)
# Deliberate connected thumb branches extruded from palm side faces, not separate spheres.
bm=bmesh.new();bm.from_mesh(body.data)
for sign in [-1,1]:
 target=Vector((sign*.39,-.025,.97));face=min((q for q in bm.faces if sign*q.calc_center_median().x>.32 and .93<q.calc_center_median().z<1.01),key=lambda q:(q.calc_center_median()-target).length)
 result=bmesh.ops.extrude_face_region(bm,geom=[face]);new=[x for x in result['geom'] if isinstance(x,bmesh.types.BMVert)];bmesh.ops.delete(bm,geom=[face],context='FACES_ONLY')
 for q in new:q.co+=Vector((-sign*.035,-.015,-.008))
 cap=[q for q in bm.faces if all(x in new for x in q.verts)][0];result=bmesh.ops.extrude_face_region(bm,geom=[cap]);tip=[x for x in result['geom'] if isinstance(x,bmesh.types.BMVert)];center=sum((q.co for q in tip),Vector())/len(tip);bmesh.ops.delete(bm,geom=[cap],context='FACES_ONLY')
 for q in tip:q.co=center+(q.co-center)*.48+Vector((-sign*.016,-.008,-.02))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()

# Audit topology before ANY render. No voxel/remesh/join operations.
bm=bmesh.new();bm.from_mesh(body.data);unseen=set(bm.verts);comp=0
while unseen:
 comp+=1;todo=[unseen.pop()]
 while todo:
  for edge in todo.pop().link_edges:
   for q in edge.verts:
    if q in unseen:unseen.remove(q);todo.append(q)
audit={'components':comp,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'signed_volume_m3':bm.calc_volume(signed=True),'vertices':len(bm.verts),'faces':len(bm.faces),'method':'explicit shared torso rings, omitted side patches bridged to arms, shared crotch partition bridged to legs; no voxel union','no_rig':True};bm.free();(O/'body-topology.json').write_text(json.dumps(audit,indent=2));assert comp==1 and audit['boundary_edges']==0 and audit['nonmanifold_edges']==0,audit
# Rib cuirass: shaped front/side shell over body, narrow sternum point and diagonal rib sweep.
for row in range(6):
 vv=[]
 for k in range(3):
  for j in range(25):
   t=math.pi+(j/24)*math.pi;x=(.157+.009*row)*math.cos(t);y=(.112+.002*row)*math.sin(t)-.008;z=1.12+.061*row+k*.014+.045*(abs(x)/(.157+.009*row))**1.3;vv.append((x,y,z))
 mesh('rib wrap %d'%row,vv,[(i*25+j,i*25+j+1,(i+1)*25+j+1,(i+1)*25+j) for i in range(2) for j in range(24)],metal,1,.004)
# Closed sculpted mask shell with actual nose/brow/cheek contour, no overlapping base head in front.
vv=[];profile=[(1.66,.027,-.067),(1.69,.052,-.081),(1.735,.064,-.091),(1.78,.065,-.087),(1.81,.063,-.091),(1.86,.051,-.071)]
for row,(z,w,y) in enumerate(profile):
 for j in range(9):
  u=j/8*2-1;proj=[.007,.014,.037,.022,.012,.004][row]*max(0,1-abs(u)*3);eye=(.012 if row==3 and .2<abs(u)<.8 else 0);vv.append((u*w,y+.037*abs(u)**1.1-proj+eye,z))
mask=mesh('planar funerary mask',vv,[(i*9+j,i*9+j+1,(i+1)*9+j+1,(i+1)*9+j) for i in range(5) for j in range(8) if not(i==3 and j in [1,2,5,6])],bone,0,.004)
# Hood extends across temples/nape onto shoulders; opening remains front-facing.
vv=[]
for z,rx,ry,cy in [(1.52,.15,.10,.02),(1.59,.10,.08,.012),(1.69,.088,.082,.0),(1.83,.086,.082,-.005),(1.90,.072,.07,0),(1.925,.018,.02,0)]:
 for j in range(25):t=-.32+j/24*(math.pi+.64);vv.append((rx*math.cos(t),cy+ry*math.sin(t),z))
mesh('hood with nape shoulder gusset',vv,[(i*25+j,i*25+j+1,(i+1)*25+j+1,(i+1)*25+j) for i in range(5) for j in range(24)],cloth,1,.004)
# One wraparound mantle pattern around back/flanks, open front and independent lower rear split.
# Curved angular rows form shoulder support then gravity fall; paired half patterns meet at back above hips.
for sign in [-1,1]:
 vv=[]
 for r,(z,rx,ry) in enumerate([(1.56,.12,.09),(1.51,.22,.13),(1.39,.255,.15),(1.12,.215,.16),(.85,.27,.19),(.53,.29,.21),(.18,.30,.23),(.10,.30,.23)]):
  for j in range(17):
   u=j/16;t=-1.13+u*(math.pi/2+1.13);t=t if sign==1 else math.pi-t
   x=rx*math.cos(t);y=ry*math.sin(t);z-=.035*math.sin(u*math.pi) if r in [1,2] else 0
   # broad unequal seam-driven valleys, no separate rectangular front strips
   fold=(.035*math.exp(-((u-(.22+.035*r))/.105)**2)-.045*math.exp(-((u-(.62-.025*r))/.12)**2))*min(1,r/2);x+=sign*fold;y+=fold*.6
   if r>=4 and j==16:x+=sign*.012
   vv.append((x,y,z+.025*math.sin(u*math.pi)*(r/7)))
 mesh('sewn wrap mantle '+str(sign),vv,[(i*17+j,i*17+j+1,(i+1)*17+j+1,(i+1)*17+j) for i in range(7) for j in range(16)],cloth,2,.004)
# Narrow crown, true band and pointed plates, no spherical cap.
vv=[]
for z in [1.87,1.89]:
 for j in range(32):t=j*math.tau/32;vv.append((.073*math.cos(t),.071*math.sin(t),z))
mesh('crown band',vv,[(j,(j+1)%32,32+(j+1)%32,32+j) for j in range(32)],metal,0,.003)
for j in range(7):
 t=j*math.tau/7;x=.073*math.cos(t);y=.071*math.sin(t);mesh('crown point%d'%j,[(x-.007,y,1.885),(x+.007,y,1.885),(x,y,1.985 if j%2 else 1.96)],[(0,1,2)],metal,0,.003)
# Neutral placeholders for mechanism, sword and exactly three skulls. Anatomical left=+X.
def sphere(n,c,sc,ma):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=c);o=bpy.context.object;o.name=n;o.scale=sc;o.data.materials.append(ma);return o
sphere('left forearm reel',(.38,.025,1.075),(.052,.04,.07),metal)
vv=[(-.415+x,-.04+y,z) for z,w in [(.90,.027),(.15,.022),(.065,0)] for x,y in [(-w,0),(0,-.006),(w,0),(0,.006)]];mesh('right straight sword',vv,[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j) for i in range(2) for j in range(4)],metal)
sphere('right grip',(-.415,-.04,.94),(.016,.018,.065),cloth)
for i,(x,y,z) in enumerate([(-.34,.15,1.94),(.34,.15,2.04),(.0,.24,2.17)]):
 sphere('Witness core%d'%i,(x,y,z),(.055,.045,.065),bone)
 for dx in [-.021,.021]:sphere('Witness socket%d'%i,(x+dx,y-.04,z+.008),(.014,.007,.016),recess)
# evaluated body sole correction only: subdiv is above ground, relocate sole control edge down to preserve contact via mesh modifier?
# Keep exact control sole0; audit evaluated minima explicitly instead of claiming contact from control coordinates.
dg=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(dg);audit['evaluated_min_z']=min(v.co.z for v in ev.data.vertices);audit['evaluated_sole_by_side']={str(sign):min(v.co.z for v in ev.data.vertices if sign*v.co.x>0) for sign in [-1,1]};(O/'body-topology.json').write_text(json.dumps(audit,indent=2))
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(material('floor',(.12,.13,.14)))
for loc,p in [((3,-4,5),650),((-3,-1,3),400),((1,3,4),600)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=p;o.data.size=3;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2.6
scene=D/f'regent-cage-{A:02}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
for name,loc in [('front',(0,-5,1.2)),('side',(5,0,1.2)),('back',(0,5,1.2)),('threequarter',(3,-5,2.4)),('body-front',(0,-5,1.2)),('body-side',(5,0,1.2)),('head',(2,-5,2.0))]:
 
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH' and ob!=body and ob.name!='Plane':ob.hide_render=name.startswith('body-')
 cam.data.ortho_scale=.65 if name=='head' else 2.6
 cam.location=loc;cam.rotation_euler=(Vector((0,0,1.77 if name=='head' else 1.12))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(scene));(O/'readback.json').write_text(json.dumps({'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'body_topology':audit,'rigs':sum(o.type=='ARMATURE' for o in bpy.context.scene.objects)},indent=2))
