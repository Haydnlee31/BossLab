import bpy, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
R=Path('/Users/haydn/Documents/BossLab'); E=R/'artifacts/art/funeral-regent-clay-2026-11-09'; D=R/'unreal/art-studio/funeral-regent-clay-2026-11-09'; E.mkdir(parents=True,exist_ok=True);D.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []; attempt=int(args[0]) if args else 1; O=E/('attempt-%02d'%attempt);O.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=640;s.render.resolution_y=800;s.render.resolution_percentage=100
s.world.color=(.16,.16,.16)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72;return m
clay=mat('neutral plate clay',(.43,.45,.46));cloth=mat('dark neutral cloth clay',(.19,.20,.22));ivory=mat('light mask clay',(.64,.62,.56));dark=mat('recess clay',(.035,.04,.045))
# Coordinates meters, front -Y. Explicit rest anchors, not Unreal retargeting.
B={ 'root':((0,0,.98),(0,0,1.10)), 'spine':((0,0,1.1),(0,0,1.56)), 'head':((0,0,1.56),(0,0,1.88)) }
for side,sign in [('l',-1),('r',1)]:
 sh=(sign*.235,0,1.53);el=(sign*.35,0,1.22);wr=(sign*.40,-.025,.98);hip=(sign*.105,0,1.02);k=(sign*.125,0,.55);an=(sign*.13,0,.12)
 B.update({f'upper_{side}':(sh,el),f'lower_{side}':(el,wr),f'hand_{side}':(wr,(sign*.40,-.045,.86)),f'thigh_{side}':(hip,k),f'calf_{side}':(k,an),f'foot_{side}':(an,(sign*.13,-.18,.06))})
for n,x,y in [('rear_l',-.15,.14),('rear_r',.15,.14),('front_l',-.18,-.12),('front_r',.18,-.12)]: B[n]=((x,y,1.25),(x,y,.15))
a=bpy.data.armatures.new('Regent anatomical pose skeleton');rig=bpy.data.objects.new('Regent weighted clay rig',a);s.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for n,(h,t) in B.items():
 b=a.edit_bones.new(n);b.head=h;b.tail=t
for n in B:
 if n!='root': a.edit_bones[n].parent=a.edit_bones['root']
bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False);rig.show_in_front=True
objects=[]
def mesh(n,v,f,material=clay,weights=None,sub=0,thick=0):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);s.collection.objects.link(o);o.data.materials.append(material);objects.append(o)
 for p in me.polygons:p.use_smooth=True
 if weights:
  for i,w in enumerate(weights):
   for bone,val in w.items():
    g=o.vertex_groups.get(bone) or o.vertex_groups.new(name=bone);g.add([i],val,'REPLACE')
  mod=o.modifiers.new('Actual armature weights','ARMATURE');mod.object=rig
 if sub: mod=o.modifiers.new('Continuous surface subdivision','SUBSURF');mod.levels=sub
 if thick:mod=o.modifiers.new('Physical shell thickness','SOLIDIFY');mod.thickness=thick
 return o

def loft(n,rows,bone,material=clay,N=24):
 v=[]
 for z,rx,ry,cy in rows:
  for j in range(N):
   t=2*math.pi*j/N;v.append((rx*math.cos(t),cy+ry*math.sin(t),z))
 f=[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(rows)-1) for j in range(N)]
 return mesh(n,v,f,material,[{bone:1} for p in v],1,.003)
def ellipsoid(n,center,scale,bone,material=clay):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=center);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);objects.append(o)
 # bake world positions into mesh for shared armature origin
 for v in o.data.vertices:v.co+=o.location
 o.location=(0,0,0)
 if bone:
  g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE');m=o.modifiers.new('Actual armature weights','ARMATURE');m.object=rig
 for p in o.data.polygons:p.use_smooth=True
 return o
loft('continuous tapered torso vest',[(.99,.14,.09,0),(1.12,.15,.105,0),(1.34,.20,.12,0),(1.5,.22,.10,0),(1.56,.10,.08,0)],'spine',cloth)
loft('hollow neck collar',[(1.51,.105,.085,0),(1.61,.082,.078,0)],'spine')
for i in range(6):
 z=1.14+i*.061;w=.153+i*.012;v=[]
 for row in range(3):
  for j in range(25):
   t=-math.pi/2+(j/24-.5)*math.pi*1.6
   x=w*math.cos(t);y=.124*math.sin(t);zz=z+row*.019+.032*(abs(x)/w)**1.4
   v.append((x,y,zz))
 mesh('curved rib shell%d'%i,v,[(r*25+j,r*25+j+1,(r+1)*25+j+1,(r+1)*25+j) for r in range(2) for j in range(24)],clay,[{'spine':1} for _ in v],1,.004)
for side,sign in [('l',-1),('r',1)]:
 for part,radius in [('upper',.063),('lower',.048),('thigh',.076),('calf',.049)]:
  h,t=map(Vector,B[part+'_'+side]);direction=t-h;u=direction.cross(Vector((0,1,0))).normalized();v=direction.normalized().cross(u);verts=[]
  for k,rr in [(0,.8),(.15,1),(.75,.8),(1,.66)]:
   for j in range(16): verts.append(h+direction*k+radius*rr*(u*math.cos(j*math.tau/16)+v*math.sin(j*math.tau/16)))
  faces=[(i*16+j,i*16+(j+1)%16,(i+1)*16+(j+1)%16,(i+1)*16+j) for i in range(3) for j in range(16)]
  mesh(part+' '+side,verts,faces,clay,[{part+'_'+side:1} for _ in verts],1,.003)
 ellipsoid('glove '+side,B['hand_'+side][0],(.045,.035,.085),'hand_'+side,cloth)
 v=[(sign*.13+x,y,z) for z in [.0,.09,.17] for x,y in [(-.06,-.20),(.06,-.20),(.055,.06),(-.055,.06)]];mesh('boot '+side,v,[(0,3,2,1),(8,9,10,11)]+[(r*4+j,r*4+(j+1)%4,(r+1)*4+(j+1)%4,(r+1)*4+j) for r in range(2) for j in range(4)],cloth,[{'foot_'+side:1}]*12,1)
 ellipsoid('shoulder cap '+side,(sign*.235,.0,1.50),(.082,.10,.065),'upper_'+side)
# Mask is actual tapered shell with eye recess geometry and narrow crown.
loft('head under mask',[(1.60,.058,.06,0),(1.7,.075,.073,0),(1.83,.073,.069,0),(1.89,.04,.04,0)],'head',dark)
v=[]
for z,w,depth in [(1.62,.035,-.078),(1.68,.065,-.094),(1.77,.076,-.09),(1.85,.061,-.062)]:
 for j in range(9):
  x=(j/8*2-1)*w;v.append((x,depth+.048*(abs(x)/w)**1.1-(.035 if z==1.77 else .010)*max(0,1-abs(x)/(w*.28)),z))
mesh('ivory death mask',v,[(i*9+j,i*9+j+1,(i+1)*9+j+1,(i+1)*9+j) for i in range(3) for j in range(8)],ivory,[{'head':1} for _ in v],1,.004)
for x in [-.032,.032]:ellipsoid('recessed eye', (x,-.095,1.778),(.021,.008,.009),'head',dark)
loft('seated crown circlet',[(1.86,.072,.069,0),(1.88,.071,.068,0)],'head')
for j in range(7):
 t=j*math.tau/7;x=.071*math.cos(t);y=.068*math.sin(t)
 mesh('narrow crown point%d'%j,[(x-.009,y,1.875),(x+.009,y,1.875),(x,y,1.98 if j%2==0 else 1.94)],[(0,1,2)],clay,[{'head':1}]*3,0,.003)
# Open-front hood shell wraps temples, skull and nape, genuine rear surface.
v=[]
for z,rx,ry,cy in [(1.53,.115,.10,.025),(1.64,.105,.095,.018),(1.80,.094,.087,.012),(1.90,.080,.074,.007),(1.925,.035,.037,0)]:
 for j in range(25):
  t=-.30+j/24*(math.pi+.60);v.append((rx*math.cos(t),cy+ry*math.sin(t),z))
mesh('hood temples nape and crown seam',v,[(r*25+j,r*25+j+1,(r+1)*25+j+1,(r+1)*25+j) for r in range(4) for j in range(24)],cloth,[{'head':1} for _ in v],1,.005)
# Connected anatomical underbody: union only the hidden tissue, not armor or garment.
body=[]
for side,sign in [('l',-1),('r',1)]:
 for bone,sc in [('upper',(.068,.065,.075)),('lower',(.05,.05,.055)),('thigh',(.085,.08,.09)),('calf',(.055,.055,.06))]:
  body.append(ellipsoid('joint tissue '+bone+side,B[bone+'_'+side][0],sc,None,cloth))
body.append(ellipsoid('pelvis tissue',(0,0,1.02),(.155,.10,.12),None,cloth))
for o in list(objects):
 if o.name=='continuous tapered torso vest' or any(o.name==p+' '+side for p in ['upper','lower','thigh','calf'] for side in ['l','r']):
  duplicate=o.copy();duplicate.data=o.data.copy();s.collection.objects.link(duplicate);duplicate.modifiers.clear();body.append(duplicate)
# Join + voxel union gives one connected deforming base; keep metal shells above it.
bpy.ops.object.select_all(action='DESELECT')
for o in body:o.select_set(True)
bpy.context.view_layer.objects.active=body[0];bpy.ops.object.join();o=bpy.context.object;o.name='connected weighted anatomical underbody';o.modifiers.clear();o.vertex_groups.clear()
mod=o.modifiers.new('union anatomical bridges','REMESH');mod.mode='VOXEL';mod.voxel_size=.012;bpy.ops.object.modifier_apply(modifier=mod.name)
for poly in o.data.polygons:poly.use_smooth=True
bone_names=['root','spine']+[p+'_'+side for side in ['l','r'] for p in ['upper','lower','thigh','calf']]
def distseg(v,h,t):
 h=Vector(h);t=Vector(t);d=t-h;u=max(0,min(1,(v-h).dot(d)/d.length_squared));return (v-h-u*d).length
for vert in o.data.vertices:
 allowed=([n for n in bone_names if n.endswith('_l') and n.startswith(('upper','lower'))] if vert.co.x<-.27 else [n for n in bone_names if n.endswith('_r') and n.startswith(('upper','lower'))] if vert.co.x>.27 else [n for n in bone_names if not n.startswith(('upper','lower'))]);candidates=sorted((distseg(vert.co,*B[n]),n) for n in allowed)[:2];vals=[1/max(.012,d)**4 for d,n in candidates];total=sum(vals)
 for (d,n),w in zip(candidates,vals):
  g=o.vertex_groups.get(n) or o.vertex_groups.new(name=n);g.add([vert.index],w/total,'REPLACE')
mod=o.modifiers.new('Actual connected weighted skin','ARMATURE');mod.object=rig;objects.append(o)
for old in bpy.data.objects:
 if any(old.name==p+' '+side for p in ['upper','lower','thigh','calf'] for side in ['l','r']):old.hide_render=True
# Separate long weighted cloth panels: top follows spine, lower lengths independent controls.
for name,x,y,width in [('rear_l',-.16,.145,.33),('rear_r',.16,.145,.33),('front_l',-.20,-.14,.24),('front_r',.20,-.14,.24)]:
 v=[];weights=[]
 for i in range(15):
  t=i/14;z=1.55-1.40*t
  for j in range(9):
   u=j/8;xx=x+(u-.5)*width*(.62+.38*t)+(.035 if x>0 else -.035)*math.sin(t*math.pi);yy=y+(1 if 'rear' in name else -1)*(.045*math.sin(t*math.pi)+.035*math.cos((u-.17*t)*math.tau)*math.sin(t*math.pi))
   v.append((xx,yy,z+.055*u*t));w=max(0,1-t*3);weights.append({'spine':w,name:1-w})
 mesh('sewn long mantle '+name,v,[(i*9+j,i*9+j+1,(i+1)*9+j+1,(i+1)*9+j) for i in range(14) for j in range(8)],cloth,weights,1,.004)
# Yoke fits upper back, not a horizontal floating board.
loft('shoulder supported yoke',[(1.43,.265,.15,.018),(1.50,.245,.13,.015),(1.56,.17,.10,.012),(1.59,.09,.08,0)],'spine',cloth)
# Forearm mechanism and sword true volume, sockets weighted to respective bones.
ellipsoid('left reel housing',(-.40,.035,1.08),(.055,.047,.095),'lower_l')
ellipsoid('left fixed guide',(-.43,-.045,1.0),(.018,.025,.028),'lower_l',dark)
# blade oriented down in idle; sword rotation follows right hand.
verts=[(.4+x,-.055+y,z) for z,w in [(.91,.028),(.12,.022),(.04,0)] for x,y in [(-w,0),(0,-.006),(w,0),(0,.006)]]
mesh('straight pointed sword',verts,[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j) for i in range(2) for j in range(4)],clay,[{'hand_r':1}]*len(verts))
ellipsoid('sword grip',(.40,-.055,.965),(.018,.018,.065),'hand_r',cloth);ellipsoid('sword guard',(.40,-.055,.902),(.085,.013,.014),'hand_r')
# Three separate volumetric skull cores, no fire hiding silhouette.
for i,(x,y,z) in enumerate([(-.35,.18,1.92),(.32,.22,2.04),(.0,.28,2.17)]):
 ellipsoid('Witness skull %d'%i,(x,y,z),(.060,.052,.071),None,ivory)
 for dx in [-.023,.023]:ellipsoid('Witness socket %d'%i,(x+dx,y-.046,z+.008),(.017,.009,.018),None,dark)
 ellipsoid('Witness jaw %d'%i,(x,y-.01,z-.055),(.042,.039,.025),None,ivory)
# Pose snapshots stored as keyed bone transforms; no combat frame timing claimed.
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
poses=['idle','anticipation','fullcast','reel','release','thrust','miss'];frames={n:1+i*20 for i,n in enumerate(poses)}
for pose in poses:
 s.frame_set(frames[pose]);bpy.context.view_layer.update()
 anchors={n:(Vector(h),Vector(t)) for n,(h,t) in B.items()}
 shift=Vector((0,0,0));twist=0
 if pose=='anticipation':shift=Vector((.025,.04,-.07));twist=-.40
 if pose=='fullcast':shift=Vector((-.02,-.07,-.06));twist=.25
 if pose=='reel':shift=Vector((0,.09,-.15));twist=-.18
 if pose=='release':shift=Vector((.03,.035,-.07));twist=-.3
 if pose=='thrust':shift=Vector((.02,-.13,-.15));twist=.38
 if pose=='miss':shift=Vector((-.06,-.02,-.12));twist=.55
 rot=Matrix.Rotation(twist,3,'Z')
 for n,(h,t) in list(anchors.items()):
  if n!='root':anchors[n]=(rot@h+shift,rot@t+shift)
 anchors['root']=(Vector(B['root'][0])+shift,Vector(B['root'][1])+shift)
 # explicit anatomical arm chains, left cast and right independent thrust
 l={'idle':(-.40,-.025,.98),'anticipation':(-.37,.21,1.42),'fullcast':(-.24,-.58,1.49),'reel':(-.30,-.18,1.23),'release':(-.39,-.22,1.16),'thrust':(-.38,-.10,1.23),'miss':(-.55,-.25,1.05)}[pose]
 r={'idle':(.40,-.025,.98),'anticipation':(.33,.08,1.10),'fullcast':(.33,.05,1.12),'reel':(.34,.12,1.35),'release':(.34,.20,1.44),'thrust':(.18,-.61,1.45),'miss':(.30,.12,1.22)}[pose]
 for side,wr in [('l',l),('r',r)]:
  sh=anchors['upper_'+side][0];w=Vector(wr);d=w-sh;L1=(Vector(B['upper_'+side][1])-Vector(B['upper_'+side][0])).length;L2=(Vector(B['lower_'+side][1])-Vector(B['lower_'+side][0])).length;length=min(d.length,L1+L2-.005);direction=d.normalized();w=sh+direction*length;along=(L1*L1-L2*L2+length*length)/(2*length);pole=Vector(((-1 if side=='l' else 1),.7,0));pole=(pole-direction*pole.dot(direction)).normalized();e=sh+direction*along+pole*math.sqrt(max(0,L1*L1-along*along));anchors['upper_'+side]=(sh,e);anchors['lower_'+side]=(e,w)
  handdir=Vector((0,-.12,0)) if pose in ['fullcast','thrust'] else Vector((0,-.015,-.12));anchors['hand_'+side]=(w,w+handdir)
 for side,sign in [('l',-1),('r',1)]:
  hip=rot@Vector(B['thigh_'+side][0])+shift;fy=0
  if pose!='idle':fy=(-.24 if side=='l' else .17)
  if pose=='thrust':fy=(-.38 if side=='l' else .23)
  ankle=Vector((sign*(.13 if pose=='idle' else .19),fy,.12));k=hip.lerp(ankle,.53)+Vector((0,-.06,0));anchors['thigh_'+side]=(hip,k);anchors['calf_'+side]=(k,ankle);anchors['foot_'+side]=(ankle,ankle+Vector((0,-.18,-.06)))
 for n in ['rear_l','rear_r','front_l','front_r']:
  h,t=anchors[n];sgn=-1 if n.endswith('l') else 1;t.x+=sgn*(.07 if pose!='idle' else 0);t.y+=(.08 if n.startswith('rear') else -.13) if pose!='idle' else 0;anchors[n]=(h,t)
 for n,(h,t) in anchors.items():
  rest=a.bones[n];q=(rest.tail_local-rest.head_local).rotation_difference(t-h);m=Matrix.Translation(h)@q.to_matrix().to_4x4()@rest.matrix_local.to_3x3().to_4x4()@Matrix.Diagonal((1,(t-h).length/(rest.tail_local-rest.head_local).length,1,1));pb=rig.pose.bones[n];pb.matrix=m;bpy.context.view_layer.update()
  pb.keyframe_insert('location',frame=frames[pose]);pb.keyframe_insert('rotation_quaternion',frame=frames[pose]);pb.keyframe_insert('scale',frame=frames[pose])
# Visual-only chain paths, keyed visibility for each declared snapshot; no authority/physics.
for pose in poses:
 s.frame_set(frames[pose]);bpy.context.view_layer.update();pb=rig.pose.bones['lower_l'];start=pb.matrix@Vector((-.025,pb.bone.length*.94,-.04))
 reach={'idle':.18,'anticipation':.28,'fullcast':.85,'reel':.65,'release':.35,'thrust':.25,'miss':.65}[pose];end=start+Vector((-.08,-reach,-.10 if pose!='miss' else -.35))
 cu=bpy.data.curves.new('visual chain '+pose,'CURVE');cu.dimensions='3D';cu.bevel_depth=.007;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(12)
 for i,pt in enumerate(sp.points):
  t=i/12;v=start.lerp(end,t);v.z-=((.16 if pose in ['miss','release','idle'] else .025)*math.sin(math.pi*t));pt.co=(*v,1)
 ob=bpy.data.objects.new('chain path '+pose,cu);s.collection.objects.link(ob);cu.materials.append(clay)
 hcu=bpy.data.curves.new('hook '+pose,'CURVE');hcu.dimensions='3D';hcu.bevel_depth=.012;hcu.bevel_resolution=2;sp=hcu.splines.new('POLY');sp.points.add(8)
 for i,pt in enumerate(sp.points):
  t=i/8*math.pi*1.5;v=end+Vector((.045*math.sin(t),-.045*(1-math.cos(t)),0));pt.co=(*v,1)
 hook=bpy.data.objects.new('terminal hook '+pose,hcu);s.collection.objects.link(hook);hcu.materials.append(clay)
 for obj in [ob,hook]:
  for name in poses:
   obj.hide_render=name!=pose;obj.keyframe_insert('hide_render',frame=frames[name])
s.frame_start=1;s.frame_end=121;s.frame_set(1)
# Coordinate correction: authored l negativeX -> anatomical left positive worldX.
# Reflect complete character via parent, preserving deformation and hook/weapon pairing.
mirror=bpy.data.objects.new('anatomical handedness coordinate root',None);s.collection.objects.link(mirror)
for ob in list(s.objects):
 if ob!=mirror:ob.parent=mirror
mirror.scale.x=-1
# Presentation fixed scale, orthographic diagnostic cameras.
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='studio ground';floor.data.materials.append(mat('ground',(.12,.13,.14)))
for loc,power,size in [((3,-4,5),650,4),((-3,-1,3),400,3),((1,3,4),650,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=2.65
scene=D/('regent-attempt-%02d.blend'%attempt);bpy.ops.wm.save_as_mainfile(filepath=str(scene))
views=[('idle','front'),('idle','side'),('idle','back'),('anticipation','threequarter'),('fullcast','threequarter'),('reel','threequarter'),('release','threequarter'),('thrust','threequarter'),('miss','threequarter')]
if len(args)>1:views=[tuple(v.split(':')) for v in args[1:]]
for pose,view in views:
 s.frame_set(frames[pose]);loc={'front':(0,-5,1.3),'side':(5,0,1.3),'back':(0,5,1.3),'threequarter':(3,-5,2.5)}[view];cam.location=loc;cam.rotation_euler=(Vector((0,0,1.12))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(pose+'-'+view+'.png'));bpy.ops.render.render(write_still=True)
report={'attempt':attempt,'scene':str(scene),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'bones':len(a.bones),'weighted_objects':sum(any(m.type=='ARMATURE' for m in o.modifiers) for o in s.objects),'pose_frames':frames,'rendered_views':views,'limitations':['authored pose study, not engine animation','separate weighted anatomical shells, not production unified topology','no cloth physics or runtime collision validation','skull cores only, no flame']};(O/'manifest.json').write_text(json.dumps(report,indent=2))

bpy.ops.wm.open_mainfile(filepath=str(scene))
rig=bpy.data.objects['Regent weighted clay rig'];audit={'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'weights':{},'poses':{},'scope':'control mesh weight sums/components and evaluated foot bounds only; not global collision'}
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or not any(m.type=='ARMATURE' for m in ob.modifiers):continue
 sums=[sum(g.weight for g in v.groups) for v in ob.data.vertices];adj=[[] for v in ob.data.vertices]
 for e in ob.data.edges:adj[e.vertices[0]].append(e.vertices[1]);adj[e.vertices[1]].append(e.vertices[0])
 unseen=set(range(len(adj)));components=0
 while unseen:
  components+=1;stack=[unseen.pop()]
  while stack:
   for j in adj[stack.pop()]:
    if j in unseen:unseen.remove(j);stack.append(j)
 audit['weights'][ob.name]={'vertices':len(sums),'unweighted':sum(x<.999 for x in sums),'max_sum_error':max([abs(x-1) for x in sums],default=0),'components':components}
for name,frame in frames.items():
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();bounds={}
 for side in ['l','r']:
  ob=bpy.data.objects['boot '+side];ev=ob.evaluated_get(dg);bounds[side]=min((ev.matrix_world@v.co).z for v in ev.data.vertices)
 audit['poses'][name]={'frame':frame,'foot_min_z_m':bounds,'bone_matrices':{b.name:[list(row) for row in b.matrix] for b in rig.pose.bones}}
(O/'reload-audit.json').write_text(json.dumps(audit,indent=2))
