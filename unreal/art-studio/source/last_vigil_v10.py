"""V10 authored padded mantle study. Frozen V9 armor input; no failed cloth simulation."""
from pathlib import Path
previous=Path(__file__).with_name('last_vigil_v9_armor.py')
exec(compile(previous.read_text().split("\nif mode=='draft':")[0],str(previous),'exec'))
D=R/'unreal/art-studio/revision-v10-2026-11-07';E=R/'artifacts/art/last-vigil-v10';D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
INPUT=R/'unreal/art-studio/revision-v9-armor-2026-11-07/last-vigil-v9-armor.blend'

def build_v10():
 global S
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));S=bpy.context.scene;setdevice();root=bpy.data.objects['CHARACTER | shoulder-turn study'];removed=[];oldpoints=[]
 for ob in list(S.objects):
  if ('V6 |' in ob.name and 'fibers' in ob.name) or ob.name in ['V5 | sewn horseshoe wool yoke','V5 | authored mantle control cage','V5 | bound yoke opening','V5 | bound yoke hem','V2 | gate clasp','V2 | cape leather tether']:
   if ob.type=='MESH':oldpoints.extend([ob.matrix_world@v.co for v in ob.data.vertices])
   removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 inner=[(.055,-.110,1.600),(.090,-.020,1.645),(.095,.035,1.645),(.060,.085,1.640),(0,.090,1.640),(-.060,.085,1.640),(-.095,.025,1.645),(-.080,-.045,1.640),(-.050,-.110,1.605),(.015,-.125,1.595)]
 outer=[(.130,-.110,1.525),(.220,-.035,1.540),(.225,.065,1.535),(.150,.155,1.535),(0,.180,1.545),(-.170,.150,1.540),(-.230,.045,1.540),(-.180,-.090,1.535),(-.110,-.135,1.535),(.040,-.135,1.545)]
 profile=[(float(u),float(.038*sin(pi*u)**.75-.005*math.exp(-((u-.32)/.045)**2)-.004*math.exp(-((u-.68)/.04)**2))) for u in np.linspace(0,1,25)]
 vs=[];fs=[];rows=55;cols=len(profile)
 for layer in [0,1]:
  for i in range(rows):
   t=i/(rows-1);a=Vector(v5_curve(inner,t));b=Vector(v5_curve(outer,t));end=min(1,.35+min(t,1-t)*10)
   for u,h in profile:
    # Rounded compressed tongues and stuffed underside, no planar brim.
    tt=t+(max(0,1-t*16)-max(0,1-(1-t)*16))*.025*(2*u-1)**2
    a=Vector(v5_curve(inner,tt));b=Vector(v5_curve(outer,tt));b.x*=.74;p=a.lerp(b,u)
    sag=.009*sin(pi*u)*sin(pi*t*1.3)**2
    p.z+=(h*end-sag if layer==0 else h*.35*end-.008-sag)
    vs.append(tuple(p))
 count=rows*cols
 for i in range(rows-1):
  for j in range(cols-1):
   a=i*cols+j;fs.append((a,a+1,a+cols+1,a+cols));a+=count;fs.append((a+cols,a+cols+1,a+1,a))
 for i in range(rows-1):
  for j in [0,cols-1]:
   a=i*cols+j;b=a+cols;fs.append((a,b,b+count,a+count))
 for i in [0,rows-1]:
  for j in range(cols-1):
   a=i*cols+j;fs.append((a,a+count,a+count+1,a+1))
 ma=mat_simple('V10 | charcoal quilted wool',(.018,.014,.012),0,.88)
 v5_wool(ma, (.014,.011,.009))
 ob=mesh('V10 | mantle padded sewn collar',vs,fs,ma);ob.parent=root
 mod=ob.modifiers.new('Sewn padded surface subdivision','SUBSURF');mod.levels=2;mod.render_levels=2
 for p in ob.data.polygons:p.use_smooth=True
 # Short rim-only groom; roots on outer sewn surface, no all-over carpet.
 import random
 rng=random.Random(1010)
 for shade in range(3):
  hm=mat_simple('V10 | mantle rim fiber '+str(shade),[(.025,.020,.016),(.042,.034,.026),(.016,.013,.011)][shade],0,.88)
  cu=bpy.data.curves.new('V10 rim groom','CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=.00032;cu.bevel_resolution=0;cu.use_fill_caps=True
  for strand in range(650):
   t=rng.uniform(.02,.98);u=rng.uniform(.89,.99);a=Vector(v5_curve(inner,t));b=Vector(v5_curve(outer,t));b.x*=.74;p=a.lerp(b,u);p.z+=.038*sin(pi*u)**.75+.001
   direction=(b-a).normalized();tangent=(Vector(v5_curve(outer,min(1,t+.003)))-Vector(v5_curve(outer,max(0,t-.003)))).normalized()
   length=.016+.021*(.5+.5*sin(t*47))+.006*rng.random();length*=rng.uniform(.72,1.08)*(.55+.45*min(1,t*6,(1-t)*6))
   drift=direction*.50+tangent*(.55*sin(t*47));sp=cu.splines.new('NURBS');sp.points.add(7);sp.order_u=3;sp.use_endpoint_u=True
   for k,pt in enumerate(sp.points):
    w=k/7;normal=Vector((direction.x*.6,direction.y*.6,1)).normalized();q=p+drift*length*w+normal*(.009*sin(pi*w))-Vector((0,0,length*.60*w*w));pt.co=(*q,1);pt.radius=max(.08,1-w*.92)
  hair=bpy.data.objects.new('V10 | mantle short irregular rim '+str(shade),cu);bpy.context.collection.objects.link(hair);cu.materials.append(hm);hair.parent=root
 leather=mat_simple('V10 | collar retention leather',(.015,.009,.006),0,.75)
 strapvs=[]
 for k in range(17):
  t=k/16;p=Vector(v5_curve([(-.060,-.128,1.606),(-.020,-.151,1.586),(.050,-.151,1.579),(.095,-.118,1.597)],t));strapvs.extend([tuple(p+Vector((0,0,-.006))),tuple(p+Vector((0,0,.006)))])
 strap=plate_patch('V10 | mantle curved retention strap',strapvs,[(2*k,2*k+1,2*k+3,2*k+2) for k in range(16)],leather,.002);strap.parent=root
 clasp=curve('V10 | mantle single clasp',[(-.004,-.156,1.573),(-.004,-.156,1.593),(.015,-.156,1.591),(.015,-.156,1.571),(-.004,-.156,1.573)],.0018,leather);clasp.parent=root
 bpy.context.view_layer.update()
 from mathutils.bvhtree import BVHTree
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();tree=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[tuple(p.vertices) for p in me.polygons],all_triangles=False);ev.to_mesh_clear()
 for vert in strap.data.vertices:
  row=vert.index//2;distance=min(row,16-row);w=max(0,min(1,(6-distance)/4));w=w*w*(3-2*w)
  if w:
   hit,normal,face,d=tree.find_nearest(vert.co);direction=(vert.co-hit).normalized() if d>.0001 else normal
   vert.co=vert.co.lerp(hit+direction*.0015,w)
 (E/'collar-construction.json').write_text(json.dumps({'method':'Closed authored control mesh, not cloth simulation. One soft convex stuffed volume with two shallow compressed seam valleys and asymmetric split front. Bare geometry probe before groom.','input':str(INPUT.relative_to(R)),'removed_objects':removed,'control_vertices':len(vs),'control_faces':len(fs),'old_removed_geometry_x_span_m':max(p.x for p in oldpoints)-min(p.x for p in oldpoints) if oldpoints else None,'new_control_x_span_m':max(p[0] for p in vs)-min(p[0] for p in vs),'inner_landmarks':inner,'outer_landmarks':outer,'profile_u_height':profile},indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v10.blend'))

def crafted_sample():
 N=1024;vv,uu=np.mgrid[0:N,0:N]/(N-1);folder=D/'textures';folder.mkdir(exist_ok=True);records=[]
 def make_image(name,data):
  if data.ndim==2:data=np.stack([data,data,data],axis=2)
  im=bpy.data.images.new(name,width=N,height=N,alpha=True);im.use_fake_user=True;im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(np.concatenate([data,np.ones((N,N,1))],axis=2).astype(np.float32).ravel());im.filepath_raw=str(folder/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im
 for family in ['visor','shoulder','crown','articulated']:
  if family=='visor':
   top=.83+.025*np.sin(uu*13)+.012*np.sin(uu*37)
   oxide=1/(1+np.exp(np.clip((top-vv)/.018,-40,40)))
   oxide=np.maximum(oxide,.9*np.exp(-((uu-.12)/.055)**4-((vv-.62)/.24)**4))
   oxide=np.maximum(oxide,.8*np.exp(-((uu-.86)/.055)**4-((vv-.68)/.19)**4))
   oxide=np.maximum(oxide,.92*np.exp(-((np.minimum(uu,1-uu)-.052-.022*(vv-.29))/.045)**2-((vv-.29)/.20)**2))
   polish=.65*np.exp(-((np.minimum(uu,1-uu)-.065)/.05)**4-((vv-.27)/.19)**4)
  elif family=='shoulder':
   boundary=.76+.035*np.sin(uu*12)+.015*np.sin(uu*31)
   oxide=1/(1+np.exp(np.clip((boundary-vv)/.022,-40,40)))
   oxide=np.maximum(oxide,.85*np.exp(-((uu-.14)/.095)**4-((vv-.48)/.32)**4))
   edge=.27+.06*np.sin(uu*7)+.018*np.sin(uu*29)
   oxide=np.maximum(oxide,.94/(1+np.exp(np.clip((vv-edge)/.018,-40,40))))
   polish=.8*np.exp(-((vv-.16-.07*uu)/.11)**4-((uu-.62)/.34)**4)
  elif family=='crown':
   front=np.exp(-(np.minimum(uu,1-uu)/.23)**4);boundary=.15+.022*np.sin(uu*17)
   oxide=.88/(1+np.exp(np.clip((vv-boundary)/.025,-40,40)))*front
   polish=.55*np.exp(-(np.minimum(uu,1-uu)/.027)**4-((vv-.52)/.41)**4)
  else:
   boundary=.13+.035*np.sin(uu*15)
   oxide=.82/(1+np.exp(np.clip((vv-boundary)/.022,-40,40)))+.72/(1+np.exp(np.clip((.87-vv)/.022,-40,40)))
   polish=.45*np.exp(-((np.minimum(uu,1-uu)-.12)/.07)**4-((vv-.53)/.31)**4)
  polish*=1-oxide;oxide=np.clip(oxide,0,1)
  color=np.zeros((N,N,3))+[.018,.020,.023]
  color=color*(1-oxide[:,:,None])+np.array([.0015,.0012,.0010])*oxide[:,:,None]
  color=color*(1-polish[:,:,None])+np.array([.080,.085,.090])*polish[:,:,None]
  rough=.61+.19*oxide-.27*polish;metal=.95-.92*oxide
  mask=make_image('V10-'+family+'-construction-mask',np.stack([polish,oxide,np.zeros_like(uu)],axis=2))
  col=make_image('V10-'+family+'-color',color);properties=make_image('V10-'+family+'-roughness-metallic',np.stack([rough,metal,np.zeros_like(uu)],axis=2))
  ma=mat_simple('V10 | worked '+family,(.052,.057,.060),.95,.49);n=ma.node_tree.nodes;l=ma.node_tree.links;bs=n.get('Principled BSDF');uv=n.new('ShaderNodeUVMap');uv.uv_map='V10 cylindrical plate UV' if family=='articulated' else 'V7 forged UV';bs.inputs['Specular IOR Level'].default_value=.22
  tx=n.new('ShaderNodeTexImage');tx.image=col;l.new(uv.outputs[0],tx.inputs['Vector']);l.new(tx.outputs['Color'],bs.inputs['Base Color'])
  tx=n.new('ShaderNodeTexImage');tx.image=properties;l.new(uv.outputs[0],tx.inputs['Vector']);sep=n.new('ShaderNodeSeparateColor');l.new(tx.outputs['Color'],sep.inputs[0]);l.new(sep.outputs[0],bs.inputs['Roughness']);l.new(sep.outputs[1],bs.inputs['Metallic'])
  # Local intermediate-scale worked relief, masked to construction zones.
  coord=n.new('ShaderNodeTexCoord');grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=210;grain.inputs['Detail'].default_value=2;grain.inputs['Roughness'].default_value=.65;stretch=n.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(.65,2.5,1);l.new(coord.outputs['Object'],stretch.inputs[0]);l.new(stretch.outputs[0],grain.inputs['Vector'])
  mt=n.new('ShaderNodeTexImage');mt.image=mask;l.new(uv.outputs[0],mt.inputs['Vector']);ms=n.new('ShaderNodeSeparateColor');l.new(mt.outputs['Color'],ms.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(grain.outputs['Fac'],mul.inputs[0]);l.new(ms.outputs[1],mul.inputs[1]);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=.0004;l.new(mul.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
  targets=[]
  for ob in S.objects:
   if ob.type!='MESH':continue
   articulated=family=='articulated' and (ob.name.startswith('Sliding fauld lame') or 'tapered vambrace' in ob.name or 'flared gauntlet cuff' in ob.name)
   if articulated:
    me=ob.data;uvlayer=me.uv_layers.get('V10 cylindrical plate UV') or me.uv_layers.new(name='V10 cylindrical plate UV');points=[v.co for v in me.vertices];cx=sum(p.x for p in points)/len(points);cy=sum(p.y for p in points)/len(points);lo=min(p.z for p in points);hi=max(p.z for p in points)
    for face in me.polygons:
     values=[]
     for li in face.loop_indices:
      p=me.vertices[me.loops[li].vertex_index].co;values.append(((math.atan2(p.x-cx,-(p.y-cy))/(2*pi))%1,(p.z-lo)/max(.001,hi-lo)))
     wrap=max(a for a,b in values)-min(a for a,b in values)>.5
     for li,(a,b) in zip(face.loop_indices,values):uvlayer.data[li].uv=(a+1 if wrap and a<.5 else a,b)
    ob.data.materials.clear();ob.data.materials.append(ma);targets.append(ob.name)
   if any(m and m.name=='V7 forged '+family for m in ob.data.materials):
    for slot in ob.material_slots:
     if slot.material and slot.material.name=='V7 forged '+family:slot.material=ma
    targets.append(ob.name)
  records.append({'family':family,'objects':targets,'UV':'V10 cylindrical plate UV (new cylindrical sample)' if family=='articulated' else 'V7 forged UV inherited sample projection, not new unwrap','oxide_mask_gt_half_fraction':float(np.mean(oxide>.5)),'roughness_range':[float(rough.min()),float(rough.max())],'metallic_range':[float(metal.min()),float(metal.max())],'change':'Actual oxide regions reduce metallic response as well as raise roughness/darken albedo. Metal fields retain .95 metallic. No imported maps.'})
 (E/'crafted-sample.json').write_text(json.dumps(records,indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v10.blend'))

def static_garment():
 root=bpy.data.objects['CHARACTER | shoulder-turn study'];removed=[];records=[]
 for ob in list(S.objects):
  if ob.name.startswith(('V2 | garment stitched binding','V5 | surcoat sewn side seam','V2 | uneven sewn hem')):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 for sg in [-1,1]:
  old=bpy.data.objects['V2 | sewn overlapping surcoat '+str(sg)];ma=old.data.materials[0];removed.append(old.name);bpy.data.objects.remove(old,do_unlink=True)
  # Five support regions plus two close belt-tuck support rows; two unequal diagonal load folds.
  heights=[1.065,1.043,1.025,.885,.78,.665,.575 if sg<0 else .595]
  widths=[.150,.150,.180,.174,.171,.159,.150]
  depths=[[-.11,-.10,-.09,-.08,-.07],[-.11,-.10,-.09,-.08,-.07],[-.147,-.155,-.15,-.157,-.145],[-.165,-.174,-.167,-.180,-.165],[-.149,-.188,-.153,-.193,-.150],[-.128,-.173,-.139,-.177,-.130],[-.128,-.160,-.129,-.166,-.125]]
  def panel(u,v):
   rows=[]
   for j in range(7):
    t=j/6;points=[]
    for k in range(5):
     q=[[0,.25,.56,.82,1],[0,.25,.56,.82,1],[0,.25,.56,.82,1],[0,.23,.54,.80,1],[0,.20,.50,.75,1],[0,.17,.46,.69,1],[0,.15,.42,.64,1]][j][k];x=sg*(.012+widths[j]*q)
     z=heights[j]+.035*q*q*t**3
     y=(-.115*sqrt(max(.01,1-(x/.175)**2))+.005) if j<2 else depths[j][k]+(.003 if j in [2,3] else 0)
     points.append((x,y,z))
    rows.append(v5_curve(points,u))
   return v5_curve(rows,v)
  nx,ny=36,48;vs=[panel(i/nx,j/ny) for j in range(ny+1) for i in range(nx+1)];fs=[]
  for j in range(ny):
   for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
  ob=mesh('V10 | authored static split surcoat '+str(sg),vs,fs,ma);ob.parent=root;solid(ob,.0025);sub(ob,1)
  thread=mat_simple('V10 | worn cloth binding '+str(sg),(.012,.009,.007),0,.92)
  for u in [.018,.982]:
   edge=curve('V10 | surcoat fitted side binding',[panel(u,v)+Vector((0,-.0015,0)) for v in np.linspace(0,1,100)],.0008,thread);edge.parent=root
  hem=curve('V10 | surcoat curved hem',[panel(u,.985)+Vector((0,-.0015,0)) for u in np.linspace(0,1,100)],.001,thread);hem.parent=root
  records.append({'object':ob.name,'row_heights':heights,'widths':widths,'depth_landmarks':depths,'source_control_vertices':len(vs),'method':'Authored static pattern/support cage, not physics or simulation','outer_hem_raise_m':.035})
 (E/'static-garment-construction.json').write_text(json.dumps({'removed':removed,'panels':records,'rigid_tassets':'Unchanged original V9-armor geometry; no failed V9 solver imported','limits':'Static fit only, visual and scoped clearance checks required'},indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v10.blend'))

def audit_v10():
 global S
 import hashlib,struct
 from mathutils.bvhtree import BVHTree
 def states():
  out={}
  for ob in S.objects:
   if ob.type not in ['MESH','CURVE'] or ob.hide_render:continue
   h=hashlib.sha256();h.update(str([list(r) for r in ob.matrix_world]).encode())
   if ob.type=='MESH':
    for v in ob.data.vertices:h.update(struct.pack('<3f',*v.co))
    for face in ob.data.polygons:h.update(str(tuple(face.vertices)).encode())
   else:
    for sp in ob.data.splines:
     for p in sp.points:h.update(struct.pack('<4f',*p.co))
     for p in sp.bezier_points:h.update(struct.pack('<3f',*p.co))
   out[ob.name]=h.hexdigest()
  return out
 def evaluated_bounds(name):
  ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return {'min':[min(p[k] for p in pts) for k in range(3)],'max':[max(p[k] for p in pts) for k in range(3)],'span':[max(p[k] for p in pts)-min(p[k] for p in pts) for k in range(3)]}
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));S=bpy.context.scene;before=states();protected_before=protected_state();old_collar_bounds=evaluated_bounds('V5 | sewn horseshoe wool yoke')
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v10.blend'));S=bpy.context.scene;after=states();protected_after=protected_state()
 removed=json.loads((E/'collar-construction.json').read_text())['removed_objects']+json.loads((E/'static-garment-construction.json').read_text())['removed']
 changed=[n for n in before if n in after and before[n]!=after[n]];missing=[n for n in before if n not in after and n not in removed]
 def tree_for(test):
  vs=[];fs=[]
  for ob in S.objects:
   if ob.type!='MESH' or ob.hide_render or not test(ob.name):continue
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();off=len(vs);vs.extend([ev.matrix_world@v.co for v in me.vertices]);fs.extend([tuple(off+i for i in p.vertices) for p in me.polygons]);ev.to_mesh_clear()
  return BVHTree.FromPolygons(vs,fs,all_triangles=False)
 collar_tree=tree_for(lambda n:n=='V10 | mantle padded sewn collar');strap=bpy.data.objects['V10 | mantle curved retention strap'];ends=[]
 for idx in [0,1,len(strap.data.vertices)-2,len(strap.data.vertices)-1]:
  p=strap.matrix_world@strap.data.vertices[idx].co;hit,n,face,dist=collar_tree.find_nearest(p);ends.append({'endpoint_vertex':idx,'nearest_collar_distance_m':dist})
 collar_metrics={'old_evaluated_support_bounds':old_collar_bounds,'new_evaluated_support_bounds':evaluated_bounds('V10 | mantle padded sewn collar'),'retention_end_nearest_samples':ends,'scope':'Same evaluated support-only bounds, excluding groom; strap four control-end vertex nearest distances only, not full contact or motion validation.'}
 body=tree_for(lambda n: 'cuisse' in n.lower() or 'Riveted mail skirt' in n or 'knee' in n.lower())
 plates=tree_for(lambda n:'shaped suspended tasset' in n)
 cloth_report=[]
 for ob in S.objects:
  if not ob.name.startswith('V10 | authored static split surcoat'):continue
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bodyds=[];plateds=[]
  for v in me.vertices:
   p=ev.matrix_world@v.co;hit,normal,idx,d=body.ray_cast(Vector((p.x,-1,p.z)),Vector((0,1,0)),2)
   if hit is not None:bodyds.append(hit.y-p.y)
   hit,normal,idx,d=plates.ray_cast(Vector((p.x,1,p.z)),Vector((0,-1,0)),2)
   if hit is not None:plateds.append(p.y-hit.y)
  ev.to_mesh_clear();cloth_report.append({'object':ob.name,'body_front_envelope_samples':len(bodyds),'min_body_front_clearance_m':min(bodyds) if bodyds else None,'body_samples_below_3mm':sum(d<.003 for d in bodyds),'tasset_back_envelope_samples':len(plateds),'min_tasset_back_clearance_m':min(plateds) if plateds else None,'tasset_samples_below_3mm':sum(d<.003 for d in plateds)})
 images=[]
 for im in bpy.data.images:
  if not im.name.startswith('V10-'):continue
  pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels);pixels=pixels.reshape(-1,4)
  images.append({'name':im.name,'size':list(im.size),'packed':bool(im.packed_file),'color_space':im.colorspace_settings.name,'channel_min':pixels.min(axis=0).tolist(),'channel_max':pixels.max(axis=0).tolist()})
 shader=[]
 for ma in bpy.data.materials:
  if ma.name.startswith('V10 | worked '):
   bs=ma.node_tree.nodes.get('Principled BSDF');shader.append({'material':ma.name,'links':{key:[li.from_node.name+':'+li.from_socket.name for li in bs.inputs[key].links] for key in ['Base Color','Metallic','Roughness','Normal']}})
 uv_integrity=[]
 for ob in S.objects:
  if ob.type!='MESH' or not ob.data.uv_layers.get('V10 cylindrical plate UV'):continue
  me=ob.data;uv=me.uv_layers['V10 cylindrical plate UV'];me.calc_loop_triangles();areas=[]
  for tri in me.loop_triangles:
   a,b,c=[uv.data[i].uv for i in tri.loops];areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5)
  uv_integrity.append({'object':ob.name,'triangles':len(areas),'uv_area_below_1e_minus_12':sum(a<1e-12 for a in areas),'finite':all(math.isfinite(a) for a in areas),'scope':'Raw cylindrical sample projection, including any cap degeneracy; not an atlas or overlap certificate'})
 result={'input_scene':str(INPUT.relative_to(R)),'retained_visible_geometry_objects':len(set(before)&set(after)),'unexpected_changed_retained_geometry':changed,'unexpected_missing_originals':missing,'explicit_removed':removed,'new_objects':sorted(set(after)-set(before)),'protected_match':protected_before==protected_after,'protected_before':protected_before,'protected_after':protected_after,'static_garment_ray_envelopes':cloth_report,'collar_metrics':collar_metrics,'scope':'Static vertex +Y body/front and -Y tasset/back envelopes; not triangle intersection, manifold, motion, or cloth physics certification. Geometry hashes omit material/UV to permit explicitly declared finish changes.','packed_v10_images':images,'new_uv_integrity':uv_integrity,'shader_connections':shader,'no_failed_solver_objects':not any(o.name.startswith(('V9 | actual cloth','V9 | settled static cloth')) for o in S.objects)}
 (E/'v10-reload-audit.json').write_text(json.dumps(result,indent=2)+'\n')
 assert not changed and not missing and result['protected_match'] and result['no_failed_solver_objects']

prior_render=render
def render(view):
 restores=[]
 if view.startswith('mask_'):
  for ob in S.objects:
   if ob.type!='MESH':continue
   for slot in ob.material_slots:
    old=slot.material
    if not old or not old.name.startswith('V10 | worked '):continue
    family=old.name.split('V10 | worked ')[1];ma=bpy.data.materials.get('V10 diagnostic '+family)
    if ma is None:
     ma=bpy.data.materials.new('V10 diagnostic '+family);ma.use_nodes=True;n=ma.node_tree.nodes;n.clear();l=ma.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map='V10 cylindrical plate UV' if family=='articulated' else 'V7 forged UV';tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images.get('V10-'+family+'-construction-mask') or bpy.data.images.load(str(D/'textures'/('V10-'+family+'-construction-mask.png')));em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(uv.outputs[0],tx.inputs[0]);l.new(tx.outputs['Color'],em.inputs[0]);l.new(em.outputs[0],out.inputs[0])
    restores.append((slot,old));slot.material=ma
 prior_render(view)
 for slot,ma in restores:slot.material=ma

if mode=='draft':
 build_v10();crafted_sample();static_garment()
else:
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v10.blend'));S=bpy.context.scene;setdevice()
if mode=='diagnostic':
 records=[]
 for ma in bpy.data.materials:
  if not ma.name.startswith('V10 | worked '):continue
  bs=ma.node_tree.nodes.get('Principled BSDF');record={'material':ma.name,'inputs':{},'maps':[]}
  for socket in ['Base Color','Metallic','Roughness']:
   record['inputs'][socket]=[{'node':li.from_node.name,'socket':li.from_socket.name} for li in bs.inputs[socket].links]
  for n in ma.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:
    im=n.image;pix=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pix);pix=pix.reshape(-1,4);record['maps'].append({'name':im.name,'color_space':im.colorspace_settings.name,'channel_min':pix.min(axis=0).tolist(),'channel_max':pix.max(axis=0).tolist(),'sample_10percent':pix[int(len(pix)*.1)].tolist()})
  records.append(record)
  for socket in ['Base Color','Metallic','Roughness']:
   for link in list(bs.inputs[socket].links):ma.node_tree.links.remove(link)
  bs.inputs['Base Color'].default_value=(.014,.012,.010,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.85
 (E/'shader-readback.json').write_text(json.dumps(records,indent=2)+'\n')
 S.render.resolution_x=720;S.render.resolution_y=920;S.cycles.samples=16;render('shoulder');(E/'shoulder.png').rename(E/'diagnostic-constant-oxide.png')
if mode=='surface':crafted_sample()
if mode in ['draft','probe','render','surface']:
 S.render.resolution_x=1400 if mode=='render' else 720;S.render.resolution_y=1800 if mode=='render' else 920;S.cycles.samples=48 if mode=='render' else 16
 for view in args[1:] or ['clay_shoulder','clay_headside','hero']:render(view)
if mode=='audit':audit_v10()
asset_audit();audit_static_clearance()
