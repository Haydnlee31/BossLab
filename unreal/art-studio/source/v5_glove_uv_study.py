"""Isolated original glove seam/unwrap study. No full groom, no engine changes."""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
import numpy as np
R=Path(__file__).resolve().parents[3];D=R/'unreal/art-studio/revision-v5-2026-11-07';E=R/'artifacts/art/last-vigil-v5/glove-uv';E.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
source=D/'last-vigil-v5.blend'
with bpy.data.libraries.load(str(source),link=False) as (a,b):b.objects=[n for n in a.objects if 'unified leather palm' in n]
objects=[]
for ob in b.objects:
 if ob:
  bpy.context.collection.objects.link(ob);ob.parent=None;objects.append(ob)
assert len(objects)==2
methods=[x.identifier for x in bpy.ops.uv.unwrap.get_rna_type().properties['method'].enum_items];print('UNWRAP_METHODS',methods)
report={'unwrap_method':'MINIMUM_STRETCH','available_unwrap_methods':methods,'scope':'Isolated seam-cut unwrap of static glove bases, not final anatomy/rig/production atlas acceptance','source':str(source.relative_to(R)),'objects':[]}
def overlap_faces(me,uv,N=1024):
 owner=np.full((N,N),-1,dtype=np.int32);bad=set();count=0;me.calc_loop_triangles()
 for tri in me.loop_triangles:
  pts=np.array([uv.data[i].uv[:] for i in tri.loops],dtype=float);a,b,c=pts;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-12:bad.add(tri.polygon_index);continue
  lo=np.maximum(0,np.floor(pts.min(axis=0)*N).astype(int));hi=np.minimum(N-1,np.ceil(pts.max(axis=0)*N).astype(int))
  if any(hi<lo):continue
  xx,yy=np.meshgrid((np.arange(lo[0],hi[0]+1)+.5)/N,(np.arange(lo[1],hi[1]+1)+.5)/N);aa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;bb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;mask=(aa>1e-7)&(bb>1e-7)&(aa+bb<1-1e-7)
  tile=owner[lo[1]:hi[1]+1,lo[0]:hi[0]+1];conflict=mask&(tile>=0)&(tile!=tri.polygon_index)
  if conflict.any():bad.add(tri.polygon_index);bad.update(int(x) for x in tile[conflict]);count+=int(conflict.sum())
  tile[mask]=tri.polygon_index
 return bad,count

for ob in objects:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 # Evaluate existing smoothing before seam decisions; geometry still the same static authored glove form.
 for mod in list(ob.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 me=ob.data;me.update();bm=bmesh.new();bm.from_mesh(me);bm.normal_update()
 # Two coherent glove halves include their curved finger sides; no projected side collapse.
 groups={}
 for face in bm.faces:
  c=face.calc_center_median();mid=-.012+max(0,.899-c.z)*.55
  if abs(c.x-(.394 if c.x>0 else -.394))>.040:mid=.010
  groups[face]=0 if (face.normal.y>.04 or abs(face.normal.y)<=.04 and c.y>mid) else 1
 # Smooth ambiguous side labels by adjacency, then merge tiny isolated regions.
 for iteration in range(5):
  new=dict(groups)
  for face in bm.faces:
   if abs(face.normal.y)>.30:continue
   neighbors=[other for edge in face.edges for other in edge.link_faces if other!=face]
   if neighbors:
    votes=sum(groups[n] for n in neighbors);new[face]=1 if votes>len(neighbors)/2 else 0 if votes<len(neighbors)/2 else groups[face]
  groups=new
 for iteration in range(3):
  unseen=set(bm.faces);changed=False
  while unseen:
   start=unseen.pop();label=groups[start];region=[start];stack=[start];boundary=[]
   while stack:
    face=stack.pop()
    for edge in face.edges:
     for other in edge.link_faces:
      if groups[other]==label and other in unseen:unseen.remove(other);region.append(other);stack.append(other)
      elif groups[other]!=label:boundary.append(groups[other])
   if len(region)<160 and boundary:
    label=1 if sum(boundary)>len(boundary)/2 else 0
    for face in region:groups[face]=label
    changed=True
  if not changed:break
 # Anatomical root and longitudinal cuts create two coherent charts per digit, not one spiral chart.
 sg=1 if 'R unified' in ob.name else -1;cx=sg*.394
 for face in bm.faces:
  p=face.calc_center_median();localx=(p.x-cx)*sg;side=0 if face.normal.y>=0 else 1
  if p.z>.973:groups[face]=40
  elif localx<-.035 and p.z<.938:
   groups[face]=20+side
   if p.z<.895:groups[face]=35
  elif p.z<.899:
   f=min(range(4),key=lambda k:abs(localx-[-.027,-.009,.010,.027][k]));groups[face]=10+2*f+side
   ratio=[.87,1,.94,.74][f];rootz=[.899,.895,.898,.906][f]+.003;length=.078*ratio;end=rootz-sum(length*w*math.cos(math.radians(a+f*2)) for w,a in zip([.45,.32,.23],[14,37,50]))
   if p.z<end+.007:groups[face]=30+f
 # Remove disconnected one-face label fragments introduced at digit seams; keep continuous anatomical charts.
 for iteration in range(4):
  unseen=set(bm.faces);changes=0
  while unseen:
   seed=unseen.pop();label=groups[seed];region=[seed];stack=[seed];boundary=[]
   while stack:
    face=stack.pop()
    for edge in face.edges:
     for other in edge.link_faces:
      if groups[other]==label and other in unseen:unseen.remove(other);region.append(other);stack.append(other)
      elif groups[other]!=label:boundary.append(groups[other])
   if len(region)<64 and boundary:
    dominant=max(set(boundary),key=boundary.count)
    for face in region:groups[face]=dominant
    changes+=1
  if not changes:break
 for edge in bm.edges:edge.seam=len(edge.link_faces)==2 and groups[edge.link_faces[0]]!=groups[edge.link_faces[1]]
 bm.to_mesh(me);bm.free()
 uv=me.uv_layers.new(name='V5 seam islands');me.uv_layers.active_index=len(me.uv_layers)-1;uv.active_render=True
 for old in me.uv_layers:
  if old!=uv:old.active_render=False
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.unwrap(method='MINIMUM_STRETCH',margin=.003);bpy.ops.uv.average_islands_scale();bpy.ops.uv.pack_islands(rotate=True,margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
 repair_history=[] # No per-face overlap surgery; preserve coherent charts.
 me.calc_loop_triangles();uv=me.uv_layers['V5 seam islands'];N=1024;hits=np.zeros((N,N),dtype=np.uint16);wire=np.zeros((N,N,4),dtype=np.float32);wire[:,:,3]=1;wire[:,:,:3]=.02
 areas=[];invalid=0
 for tri in me.loop_triangles:
  pts=np.array([uv.data[i].uv[:] for i in tri.loops],dtype=float);a,b,c=pts;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);areas.append(abs(den)*.5)
  if abs(den)<1e-12:invalid+=1;continue
  lo=np.maximum(0,np.floor(pts.min(axis=0)*N).astype(int));hi=np.minimum(N-1,np.ceil(pts.max(axis=0)*N).astype(int))
  if any(hi<lo):continue
  xx,yy=np.meshgrid((np.arange(lo[0],hi[0]+1)+.5)/N,(np.arange(lo[1],hi[1]+1)+.5)/N)
  aa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;bb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;mask=(aa>1e-7)&(bb>1e-7)&(aa+bb<1-1e-7)
  hits[lo[1]:hi[1]+1,lo[0]:hi[0]+1]+=mask.astype(np.uint16)
 # UV islands via seam-free face adjacency, independently recorded.
 bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();unseen=set(bm.faces);sizes=[]
 while unseen:
  stack=[unseen.pop()];count=0
  while stack:
   f=stack.pop();count+=1
   for e in f.edges:
    if not e.seam:
     for other in e.link_faces:
      if other in unseen:unseen.remove(other);stack.append(other)
  sizes.append(count)
 bm.free()
 for face in me.polygons:
  color=(.25,.7,.4) if face.normal.y>.42 else (.25,.5,.9) if face.normal.y<-.42 else (.85,.55,.2)
  vals=[uv.data[i].uv[:] for i in face.loop_indices]
  for a,b in zip(vals,vals[1:]+vals[:1]):
   a=np.array(a);b=np.array(b);line=np.linspace(a,b,max(2,int(np.linalg.norm(b-a)*N)));x=np.clip((line[:,0]*(N-1)).astype(int),0,N-1);y=np.clip((line[:,1]*(N-1)).astype(int),0,N-1);wire[y,x,:3]=color
 label='left' if 'L unified' in ob.name else 'right';img=bpy.data.images.new('V5 '+label+' UV islands',width=N,height=N,alpha=True);img.pixels.foreach_set(wire.reshape(-1));img.filepath_raw=str(E/(label+'-islands.png'));img.file_format='PNG';img.save();img.use_fake_user=True;img.pack()
 report['objects'].append({'name':ob.name,'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'overlap_repair_history':repair_history,'seam_edges':sum(e.use_seam for e in me.edges),'islands':len(sizes),'island_face_counts':sorted(sizes,reverse=True),'degenerate_uv_double_area_below_1e12':invalid,'minimum_uv_triangle_area':min(areas),'sum_uv_triangle_area':sum(areas),'occupied_1024_pixels':int((hits>0).sum()),'overlap_1024_pixels':int((hits>1).sum()),'overlap_scope':'Strict interior raster samples at1024, not proof of zero subpixel overlap; adjacent boundary samples excluded','finite_uv':all(math.isfinite(x) for p in uv.data for x in p.uv)})
 # Real checker shader explicitly uses new seam islands.
 mat=bpy.data.materials.new('V5 '+label+' seam checker');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8;tex=n.new('ShaderNodeTexChecker');tex.inputs['Scale'].default_value=24;tex.inputs['Color1'].default_value=(.04,.06,.08,1);tex.inputs['Color2'].default_value=(.65,.65,.62,1);coord=n.new('ShaderNodeUVMap');coord.uv_map='V5 seam islands';l.new(coord.outputs['UV'],tex.inputs['Vector']);l.new(tex.outputs['Color'],bs.inputs['Base Color']);me.materials.clear();me.materials.append(mat)
(E/'seam-unwrap-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('UV_STUDY',json.dumps(report))
S=bpy.context.scene;S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=16;S.cycles.use_denoising=True;S.render.resolution_x=640;S.render.resolution_y=800;S.render.resolution_percentage=100;S.world.color=(.15,.15,.15)
for name,pos,energy,size in [('key',(.5,1.1,1.6),110,1),('fill',(-.5,-.8,1.2),80,1)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector((.394,0,.91))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;S.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=.235
for ob in objects:ob.hide_render='L unified' in ob.name
for name,pos in [('palm-checker',(.64,1.0,1.0)),('dorsal-checker',(.64,-1.0,1.0)),('side-checker',(1.4,.1,1.0))]:
 cam.location=pos;cam.rotation_euler=(Vector((.394,.005,.905))-cam.location).to_track_quat('-Z','Y').to_euler();S.render.filepath=str(E/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(D/'v5-glove-seam-study.blend'))
