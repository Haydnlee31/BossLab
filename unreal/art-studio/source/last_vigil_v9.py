"""V9: actual bounded cloth drape authoring experiment, immutable V8 input."""
from pathlib import Path
previous=Path(__file__).with_name('last_vigil_v8.py')
exec(compile(previous.read_text().split("\nif mode=='baseline':")[0],str(previous),'exec'))
D=R/'unreal/art-studio/revision-v9-2026-11-07';E=R/'artifacts/art/last-vigil-v9';D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
V8=R/'unreal/art-studio/revision-v8-2026-11-07/last-vigil-v8.blend'

def evaluated_coords(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return pts

def fit_mail_layer():
 from mathutils.bvhtree import BVHTree
 import bmesh
 verts=[];faces=[]
 for body in S.objects:
  if body.type!='MESH' or not any(t in body.name.lower() for t in ['padded chausses',' | cuisse']):continue
  ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();offset=len(verts);verts.extend([ev.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(offset+i for i in f.vertices) for f in me.polygons]);ev.to_mesh_clear()
 tree=BVHTree.FromPolygons(verts,faces,all_triangles=False);report=[]
 for ob in list(S.objects):
  if not ob.name.startswith('Riveted mail skirt'):continue
  world=ob.matrix_world.copy();inv=world.inverted();hitcount=0;moved=[]
  for first in range(0,len(ob.data.vertices),48):
   group=list(ob.data.vertices)[first:first+48];centre=sum((world@v.co for v in group),Vector())/len(group);sg=1 if centre.x>0 else -1
   x=sg*(.016+(abs(centre.x)-.016)*.86)
   hit,n,idx,d=tree.ray_cast(Vector((x,-1,centre.z)),Vector((0,1,0)),2)
   if hit is None:
    x=sg*min(abs(x),.185);hit,n,idx,d=tree.ray_cast(Vector((x,-1,centre.z)),Vector((0,1,0)),2)
   if hit is None:continue
   target=Vector((x,hit.y-.008,centre.z));delta=target-centre;hitcount+=1;moved.append(delta.length)
   for v in group:v.co=inv@(world@v.co+delta)
  # Closed convex coverage of the actually fitted mail vertices, not a renamed thigh sphere.
  points=[world@v.co for v in ob.data.vertices];bm=bmesh.new()
  for p in points:bm.verts.new(p)
  bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
  loose=[v for v in bm.verts if not v.link_faces]
  if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  closed=all(len(e.link_faces)==2 for e in bm.edges);me=bpy.data.meshes.new('Measured fitted mail convex envelope');bm.to_mesh(me);bm.free()
  proxy=bpy.data.objects.new('V9 collision | fitted mail envelope '+ob.name,me);bpy.context.collection.objects.link(proxy);proxy.hide_render=True;proxy.display_type='WIRE';collision(proxy);proxy.collision.thickness_outer=.002;proxy.collision.thickness_inner=.001;proxy.collision.cloth_friction=4
  report.append({'mail_object':ob.name,'rings':len(ob.data.vertices)//48,'fitted_rings':hitcount,'max_ring_translation_m':max(moved) if moved else 0,'proxy_object':proxy.name,'proxy_closed_two_faces_per_edge':closed,'proxy_vertices':len(me.vertices),'proxy_faces':len(me.polygons),'scope':'Each ring translated intact to8mm ahead of actual padded thigh/cuisse front envelope; closed convex hull covers fitted mail geometry.'})
 (E/'mail-layer-fit.json').write_text(json.dumps(report,indent=2)+'\n')

def setup_cloth():
 global S
 bpy.ops.wm.open_mainfile(filepath=str(V8));S=bpy.context.scene;setdevice();S.frame_set(1)
 root=bpy.data.objects['CHARACTER | shoulder-turn study']
 for ob in S.objects:
  for mod in list(ob.modifiers):
   if mod.type in ['COLLISION','CLOTH']:ob.modifiers.remove(mod)
  if any(t in ob.name.lower() for t in ['sewn overlapping surcoat','garment stitched binding','surcoat sewn side seam','uneven sewn hem']):ob.hide_render=True;ob.hide_set(True)
 fit_mail_layer()
 proxies=[]
 for label in ['L','R']:
  for suffix in [' | cuisse',' | pointed poleyn']:
   source=bpy.data.objects.get(label+suffix)
   if source is None:continue
   points=evaluated_coords(source);lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
   centre=(lo+hi)/2;rad=(hi-lo)/2+Vector((.003,.003,.003))
   # Upper thigh coverage extends to belt, measured transverse armor bounds retained.
   if suffix.endswith('cuisse'):centre.z=.825;rad.z=.222
   proxy=sphere('V9 collision | '+label+suffix,centre,rad,bpy.data.materials['V2 | light absorbing recess'],24,16);proxy.hide_render=True;proxy.display_type='WIRE';collision(proxy)
   proxy.collision.thickness_outer=.003;proxy.collision.thickness_inner=.001;proxy.collision.cloth_friction=8
   proxies.append({'object':proxy.name,'source':source.name,'source_bounds':[list(lo),list(hi)],'centre':list(centre),'radius':list(rad),'scope':'Measured transverse rigid armor bounds; thigh z extended to waistband. Ellipsoid approximation, not exact full-body collision.'})
 # Closed measured stack envelopes replace thin overlapping collision surfaces only.
 import bmesh
 plate_proxy_report=[]
 for sg in [-1,1]:
  sources=[];points=[]
  for plate in S.objects:
   if not plate.name.startswith('V2 | shaped suspended tasset'):continue
   pts=evaluated_coords(plate)
   if (sum(p.x for p in pts)/len(pts)>0)!=(sg>0):continue
   sources.append(plate.name);points.extend(pts)
  bm=bmesh.new()
  for p in points:bm.verts.new(p)
  bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
  loose=[v for v in bm.verts if not v.link_faces]
  if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  closed=all(len(e.link_faces)==2 for e in bm.edges);volume=bm.calc_volume();me=bpy.data.meshes.new('Closed measured tasset stack coverage');bm.to_mesh(me);bm.free()
  proxy=bpy.data.objects.new('V9 collision | closed tasset stack '+str(sg),me);bpy.context.collection.objects.link(proxy);proxy.hide_render=True;proxy.display_type='WIRE';collision(proxy);proxy.collision.thickness_outer=.002;proxy.collision.thickness_inner=.001;proxy.collision.cloth_friction=6
  plate_proxy_report.append({'object':proxy.name,'sources':sources,'closed_two_faces_per_edge':closed,'volume_m3':volume,'vertices':len(me.vertices),'faces':len(me.polygons),'scope':'Convex hull of actual evaluated rigid stack; fills gaps between lames for solver only, visible armor unchanged.'})
 (E/'tasset-proxy-audit.json').write_text(json.dumps(plate_proxy_report,indent=2)+'\n')
 nx,ny=20,44;verts=[];faces=[];pins=[];uvcoords=[]
 for sg in [-1,1]:
  offset=len(verts);length=.43 if sg<0 else .41
  for j in range(ny+1):
   v=j/ny;width=.194-.049*smooth(.25,1,v)
   for i in range(nx+1):
    u=i/nx;x=sg*(.014+width*u);y=-.135-.055*v;z=1.03-length*v+.035*u*u*v*v
    verts.append((x,y,z));uvcoords.append((u,v))
    if j==0:pins.append(offset+i)
  for j in range(ny):
   for i in range(nx):
    k=offset+j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1) if sg>0 else (k+nx+1,k+nx+2,k+1,k))
 ob=mesh('V9 | actual cloth split front panels',verts,faces,bpy.data.materials['V2 | heavy charcoal surcoat']);ob.parent=root
 uv=ob.data.uv_layers.new(name='V9 cut pattern grain')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:uv.data[li].uv=uvcoords[ob.data.loops[li].vertex_index]
 vg=ob.vertex_groups.new(name='Belt seam pins');vg.add(pins,1,'REPLACE')
 ob.shape_key_add(name='Cut pattern');gather=ob.shape_key_add(name='Thirteen percent belt gathering')
 for idx in pins:
  p=gather.data[idx].co;sg=1 if p.x>0 else -1;u=(abs(p.x)-.014)/.194;p.x=sg*(.014+(abs(p.x)-.014)*(.16926/.194))
 gather.value=0;gather.keyframe_insert('value',frame=1);gather.value=1;gather.keyframe_insert('value',frame=16)
 cloth=ob.modifiers.new('V9 real gravity cloth solve','CLOTH');c=cloth.settings;c.quality=8;c.mass=.35;c.air_damping=3;c.tension_stiffness=35;c.compression_stiffness=35;c.shear_stiffness=15;c.bending_stiffness=.35;c.tension_damping=6;c.compression_damping=6;c.shear_damping=5;c.bending_damping=3;c.vertex_group_mass=vg.name;c.pin_stiffness=1
 cc=cloth.collision_settings;cc.use_collision=True;cc.collision_quality=5;cc.distance_min=.003;cc.use_self_collision=True;cc.self_distance_min=.003;cc.self_friction=5
 pc=cloth.point_cache;pc.frame_start=1;pc.frame_end=200;pc.use_disk_cache=True
 S.frame_start=1;S.frame_end=200;S.render.fps=30;S.gravity=(0,0,-9.81)
 report={'scope':'Actual Blender cloth authoring settle, not locomotion/combat or runtime cloth','vertices':len(verts),'quad_faces':len(faces),'panels':2,'grid_per_panel':[nx+1,ny+1],'pin_vertices':len(pins),'pin_scope':'Top row only;12.75% gather with previously stable straight attachment drivenframes1–16; virtual under-belt supports','frames':[1,200],'fps':30,'gravity':list(S.gravity),'mass_setting':c.mass,'quality':c.quality,'stiffness':{'tension':35,'compression':35,'shear':15,'bending':.35},'collision_distance_m':.003,'self_collision':True,'proxies':proxies,'rigid_tasset_visual_pieces':6,'closed_stack_collision_proxies':2,'diagnostic_change':'Tailored194→145mm outer taper below tassets; outer hem corner35mm higher, opposite panel20mm shorter; same stable mail and rigid collider setup','limits':'No full-body collider, no wind, no combat/root motion, no physical fabric calibration.'}
 (E/'solver-setup.json').write_text(json.dumps(report,indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v9-solver.blend'))
 return ob,cloth

def setup_preflight(ob,phase='before bake'):
 from mathutils.bvhtree import BVHTree
 bpy.context.view_layer.update();vg=ob.vertex_groups['Belt seam pins'];pinidx=[v.index for v in ob.data.vertices if any(g.group==vg.index and g.weight>.99 for g in v.groups)];goal=ob.data.shape_keys.key_blocks[-1]
 initial=[ob.matrix_world@v.co for v in ob.data.vertices];targets=[ob.matrix_world@goal.data[i].co for i in pinidx];results=[]
 for proxy in S.objects:
  if not proxy.name.startswith('V9 collision |'):continue
  ev=proxy.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons],all_triangles=False);ev.to_mesh_clear()
  def gaps(points):
   out=[]
   for p in points:
    hit,n,idx,dist=tree.find_nearest(p)
    if hit is not None:out.append(dist if (p-hit).dot(n)>=0 else -dist)
   return out
  a=gaps(initial);b=gaps(targets);contact=.003+proxy.collision.thickness_outer
  results.append({'proxy':proxy.name,'initial_min_signed_m':min(a),'initial_inside_beyond_1mm':sum(x<-.001 for x in a),'pin_target_min_signed_m':min(b),'combined_contact_envelope_m':contact,'pin_target_shortfall_beyond_1mm':sum(x<contact-.001 for x in b)})
 passed=all(r['initial_inside_beyond_1mm']==0 and r['pin_target_shortfall_beyond_1mm']==0 for r in results)
 report={'phase':phase,'scope':'Initial pattern and final pin targets versus closed proxy surfaces; rigid tasset ray-gap check is separate','criteria':'No initial proxy penetration beyond1mm; constrained pin goals must clear combined contact envelope within1mm tolerance','results':results,'passes':passed}
 (E/'setup-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
 if phase=='before bake':assert passed,'Cloth setup preflight failed; no bake permitted'
 return report

def run_study():
 ob,cloth=setup_cloth();setup_preflight(ob);bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 with bpy.context.temp_override(point_cache=cloth.point_cache,active_object=ob,object=ob):bpy.ops.ptcache.bake(bake=True)
 rest=[Vector(v.co) for v in ob.data.vertices];edges=[tuple(e.vertices) for e in ob.data.edges];samples=[];previous=None;settled=None;frame90=None
 for frame in range(1,201):
  S.frame_set(frame);points=evaluated_coords(ob);lengths=[(points[a]-points[b]).length/max(1e-9,(rest[a]-rest[b]).length) for a,b in edges]
  samples.append({'frame':frame,'max_edge_stretch':max(lengths),'min_edge_ratio':min(lengths),'max_step_m':max((a-b).length for a,b in zip(points,previous)) if previous else 0,'min_z':min(p.z for p in points),'finite':all(np.isfinite(x) for p in points for x in p)})
  previous=points
  if frame==190:frame90=[p.copy() for p in points]
  if frame in [200]:
   Eframe=E/('frame-'+str(frame).zfill(3));Eframe.mkdir(exist_ok=True)
   for view in ['clay_front','clay_side']:
    S.render.resolution_x=720;S.render.resolution_y=920;S.cycles.samples=12
    render(view);os.replace(E/(view+'.png'),Eframe/(view+'.png'))
 settled=points
 (E/'solver-audit.json').write_text(json.dumps({'baked':cloth.point_cache.is_baked,'samples':samples,'max_edge_stretch':max(s['max_edge_stretch'] for s in samples),'max_step_last10_m':max(s['max_step_m'] for s in samples[-10:]),'all_finite':all(s['finite'] for s in samples),'max_frame190_to200_drift_m':max((a-b).length for a,b in zip(points,frame90)),'limits':'Strain and convergence only; contact clearance not yet certified'},indent=2)+'\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v9-solver.blend'))
 # Save a separate settled static candidate; no simulation-ready claim for this baked mesh.
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=bpy.data.meshes.new_from_object(ev);candidate=bpy.data.objects.new('V9 | settled static cloth candidate',me);bpy.context.collection.objects.link(candidate);candidate.parent=ob.parent
 ob.hide_render=True;ob.hide_set(True);solid(candidate,.0025);sub(candidate,1)
 S['v9_scope']='Static candidate extracted from actual200-frame cloth settle; not approved, not runtime cloth.'
 bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v9.blend'))
 engineering=all(s['finite'] for s in samples) and max(s['max_edge_stretch'] for s in samples)<=1.10 and max(s['max_step_m'] for s in samples[-10:])<=.001
 if engineering:
  for v in ['hero','front','side','garment']:render(v)
 else:print('REJECTED: numerical cloth gates failed; no final material suite')
 asset_audit()

def contact_audit():
 from mathutils.bvhtree import BVHTree
 def tree(ob):
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();t=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons],all_triangles=False);ev.to_mesh_clear();return t
 cloth=bpy.data.objects['V9 | settled static cloth candidate'];points=[cloth.matrix_world@v.co for v in cloth.data.vertices]
 proxy_results=[]
 for ob in S.objects:
  if not ob.name.startswith('V9 collision |'):continue
  t=tree(ob);ds=[]
  for p in points:
   hit,n,idx,dist=t.find_nearest(p)
   if hit is not None:ds.append(dist if (p-hit).dot(n)>=0 else -dist)
  proxy_results.append({'object':ob.name,'min_signed_clearance_m':min(ds),'samples_inside_beyond_1mm':sum(d<-.001 for d in ds)})
 plates=[tree(ob) for ob in S.objects if ob.name.startswith('V2 | shaped suspended tasset')];gaps=[]
 for p in points:
  hits=[]
  for t in plates:
   hit,n,idx,d=t.ray_cast(Vector((p.x,2,p.z)),Vector((0,-1,0)),4)
   if hit is not None:hits.append(hit.y)
  if hits:gaps.append(p.y-max(hits))
 solver=bpy.data.objects['V9 | actual cloth split front panels'];pinerr=[];endpoint=[];initial_gaps=[]
 for v in solver.data.vertices:
  p=solver.matrix_world@v.co;hits=[]
  for t in plates:
   hit,n,idx,d=t.ray_cast(Vector((p.x,2,p.z)),Vector((0,-1,0)),4)
   if hit is not None:hits.append(hit.y)
  if hits:initial_gaps.append(p.y-max(hits))
 for i,p in enumerate(points):
  v=solver.data.vertices[i];target=Vector(v.co)
  if i%945<21:
   sg=1 if target.x>0 else -1;u=(abs(target.x)-.014)/.194;target.x=sg*(.014+(abs(target.x)-.014)*(.16926/.194));pinerr.append((p-(solver.matrix_world@target)).length)
  endpoint.append((p-(solver.matrix_world@v.co)).length)
 a=json.loads((E/'solver-audit.json').read_text());gates={'finite':a['all_finite'],'strain_le_1_10':a['max_edge_stretch']<=1.10,'last10_step_le_1mm':a['max_step_last10_m']<=.001,'pin_error_le_1mm':max(pinerr)<=.001,'body_proxy_tolerance':all(r['min_signed_clearance_m']>=-.001 for r in proxy_results),'tasset_back_gap_ge_1_5mm':bool(gaps) and min(gaps)>=.0015}
 report={'scope':'Mid-surface vertices versus approximate closed body proxies and ray-hit tasset back surfaces; not arbitrary cloth/armor triangle intersection or motion proof','thresholds_declared_before_result':{'max_edge_stretch':1.10,'last10_max_vertex_step_m':.001,'pin_error_m':.001,'proxy_signed_tolerance_m':-.001,'tasset_back_gap_m':.0015},'proxy_results':proxy_results,'initial_tasset_ray_hits':len(initial_gaps),'initial_min_tasset_back_gap_m':min(initial_gaps) if initial_gaps else None,'initial_tasset_gap_fail_samples':sum(g<.0015 for g in initial_gaps),'tasset_ray_hit_samples':len(gaps),'min_tasset_back_gap_m':min(gaps) if gaps else None,'tasset_gap_fail_samples':sum(g<.0015 for g in gaps),'max_pin_target_error_m':max(pinerr),'max_total_frame1_to200_deformation_m':max(endpoint),'gates':gates,'all_engineering_gates':all(gates.values())}
 (E/'contact-stability-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('CONTACT',json.dumps(report))

def export_handoff():
 global S
 out=D/'neutral-handoff';out.mkdir(exist_ok=True)
 def objfile(path,objects,evaluated=True):
  lines=['# BossLab V9 diagnostic geometry; meters; X right, -Y front, Z up.'];base=1;counts=[]
  for ob in objects:
   ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else ob;me=ev.to_mesh() if evaluated else ob.data
   lines.append('o '+ob.name.replace(' ','_').replace('|','_'))
   for v in me.vertices:
    p=ob.matrix_world@v.co;lines.append('v %.9f %.9f %.9f'%tuple(p))
   for f in me.polygons:lines.append('f '+' '.join(str(base+i) for i in f.vertices))
   counts.append({'object':ob.name,'vertices':len(me.vertices),'faces':len(me.polygons)});base+=len(me.vertices)
   if evaluated:ev.to_mesh_clear()
  path.write_text('\n'.join(lines)+'\n');return counts
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v9.blend'));S=bpy.context.scene
 cloth=bpy.data.objects['V9 | actual cloth split front panels'];vg=cloth.vertex_groups['Belt seam pins'];goal=cloth.data.shape_keys.key_blocks[-1]
 manifest={'scope':'Neutral local DCC handoff, not accepted cloth or production sewing patterns','units':'meters','axes':{'right':'+X','front':'-Y','up':'+Z'},'cut_panels':objfile(out/'tailored-rest-panels.obj',[cloth],False),'collision_proxies':objfile(out/'measured-collision-proxies.obj',[o for o in S.objects if o.name.startswith('V9 collision |')]),'rigid_tassets':objfile(out/'rigid-tassets.obj',[o for o in S.objects if o.name.startswith('V2 | shaped suspended tasset')])}
 pins=[]
 for v in cloth.data.vertices:
  if any(g.group==vg.index and g.weight>.99 for g in v.groups):pins.append({'zero_based_vertex_index':v.index,'rest_world':list(cloth.matrix_world@v.co),'target_world':list(cloth.matrix_world@goal.data[v.index].co)})
 (out/'attachments.json').write_text(json.dumps({'scope':'Virtual top-row supports; not exported constraints or a physical sewn belt','grid_per_panel':[21,45],'panel_count':2,'pins':pins},indent=2)+'\n')
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v9-best-stable-partial.blend'));S=bpy.context.scene
 manifest['best_stable_partial']=objfile(out/'best-stable-partial-not-approved.obj',[bpy.data.objects['V9 | settled static cloth candidate']])
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (out/'README.md').write_text('# BossLab V9 neutral DCC handoff\n\nAll OBJ coordinates are meters, +X right, -Y forward, +Z up. No rescaling or external uploads were performed. Import at 1 unit = 1 meter.\n\n`tailored-rest-panels.obj` contains the actual two disconnected solver rest-position panels (21x45 grid each), not the failed evaluated drape. Their initial pose has a shallow forward tilt; this is not a certified flat production cutting template. `attachments.json` gives zero-based vertex indices and world-space pin targets.\n\n`measured-collision-proxies.obj` contains two thigh approximations, two closed fitted-mail envelopes and two closed measured tasset-stack envelopes. `rigid-tassets.obj` contains the six unchanged visible armor plates for exact fit comparison. Collision thickness must be configured in the destination DCC; it is not embedded in OBJ. Use source solver-setup.json for trial settings, not calibrated fabric values.\n\n`best-stable-partial-not-approved.obj` is the earlier100-frame static extracted cloth. It passed local strain/step/contact checks but remains visually ribbon-like and was NOT accepted as finished art. The later tailored200-frame solve FAILED (1.7598x maximum stretch,12.4mm final per-frame motion); no accepted tailored drape is included.\n\nThe working character remains frozen V8. No garment was integrated into Unreal, no runtime cloth or combat behavior was tested. Materials, skinning, UV guarantees and application-specific constraint setup are not provided by these neutral files. Next DCC work: inspect rest pattern and attachment clearance, correct contact/stability, then author convincing tailored drape and verify all layers before seams/detail.\n')
 print('HANDOFF',json.dumps(manifest))

if mode=='handoff':export_handoff()
elif mode=='study':run_study()
elif mode in ['probe','render','audit']:
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v9.blend'));S=bpy.context.scene;setdevice();S.render.resolution_x=1400 if mode=='render' else 720;S.render.resolution_y=1800 if mode=='render' else 920;S.cycles.samples=48 if mode=='render' else 16
 if mode!='audit':
  for view in args[1:] or ['hero','front','side']:render(view)
 asset_audit();audit_static_clearance();contact_audit();setup_preflight(bpy.data.objects['V9 | actual cloth split front panels'],'postsolve retrospective setup verification')
