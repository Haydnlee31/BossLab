"""V8 regional fit study; loads immutable V7, changes silhouette only.
No whole-character scale, camera/light/material edits, rig or AI claims.
"""
from pathlib import Path
previous=Path(__file__).with_name('last_vigil_v7.py')
exec(compile(previous.read_text().split("\nif mode in ['draft','support']:")[0],str(previous),'exec'))
D=R/'unreal/art-studio/revision-v8-2026-11-07';E=R/'artifacts/art/last-vigil-v8'
D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
V7=R/'unreal/art-studio/revision-v7-2026-11-07/last-vigil-v7.blend'

def smooth(a,b,v):
 t=max(0,min(1,(v-a)/(b-a)));return t*t*(3-2*t)

def fit(p,name):
 x,y,z=p; ax=abs(x);sg=1 if x>=0 else -1
 if any(t in name.lower() for t in ['leather boot','sabaton']):
  w=smooth(.03,.07,z)*(1-smooth(.11,.15,z));return Vector((sg*.132+(x-sg*.132)*.91,y,z-(z-.03)*.07*w))
 # Skull and every attached visor/brow/backing fitted together, preserving height.
 if z>=1.66:
  w=smooth(1.66,1.70,z);return Vector((x*(1-.04*w),.02+(y-.02)*(1-.05*w),z))
 if any(t in name.lower() for t in ['surcoat','tasset','garment stitched binding','uneven sewn hem']):
  w=1-smooth(.65,1.03,z);return Vector((x*(1-.16*w),y,z+.03*w))
 # Cape gets torso attachment adjustment only; keep broad hanging cloth silhouette.
 cape='cape' in name.lower()
 if cape:
  w=smooth(1.15,1.55,z);return Vector((x*(1-.07*w),.02+(y-.02)*(1-.07*w),z))
 # Lean torso envelope: chest depth reduction > waist, supported neck unchanged.
 chest=smooth(1.10,1.30,z)*(1-smooth(1.53,1.65,z))
 waist=smooth(.96,1.10,z)*(1-smooth(1.20,1.35,z))
 torso_x=x*(1-.07*chest-.11*waist)
 torso_y=.015+(y-.015)*(1-.12*chest-.14*waist)
 # Arm centreline follows old relaxed A pose; reduce thickness without shortening limbs.
 arm=smooth(.22,.285,ax)*smooth(.78,.91,z)*(1-smooth(1.56,1.66,z))
 centre=.394 if z<.96 else .387-(z-.96)*.16 if z<1.22 else .334-(z-1.22)*.25
 centre=max(.25,centre)
 upper=smooth(1.12,1.28,z)
 hand=1-smooth(.94,1.01,z)
 radial=.15*(1-smooth(.98,1.15,z))+.05*smooth(.98,1.15,z)
 radial=radial*(1-upper)+.22*upper
 if 'couter fan' not in name.lower():radial+=.09*max(0,1-abs(z-1.19)/.085)
 radial+=.06*(1-smooth(1.02,1.10,z))
 radius_scale=1-radial*(1-hand)
 inward=0 # Preserve joint centre spacing; only radial armor/garment bulk changes.
 arm_x=sg*(centre-inward+(ax-centre)*radius_scale)
 arm_y=.015+(y-.015)*(1-radial*(1-hand))
 nx=torso_x*(1-arm)+arm_x*arm;ny=torso_y*(1-arm)+arm_y*arm
 # Shoulder wing beyond supported arm mass folds inward with its attached mantle.
 shoulder=smooth(1.36,1.48,z)*(1-smooth(1.57,1.66,z))
 outer=max(0,abs(nx)-.20);nx-=sg*outer*.26*shoulder
 if any(t in name.lower() for t in ['sloping forged shoulder','turned shoulder']):
  lower=max(0,1.54-z);nx-=sg*lower*.065;z+=lower*.035
 return Vector((nx,ny,z))

def dimensions():
 dg=bpy.context.evaluated_depsgraph_get();regions={k:[] for k in ['chest','waist_fauld','shoulders','upper_arms']}
 for ob in S.objects:
  if ob.type!='MESH' or ob.hide_render or ob.parent!=bpy.data.objects['CHARACTER | shoulder-turn study']:continue
  if any(t in ob.name.lower() for t in ['cape','mantle','yoke']):continue
  ev=ob.evaluated_get(dg);me=ev.to_mesh()
  for v in me.vertices:
   p=ev.matrix_world@v.co;x,y,z=p
   for k,lo,hi,terms in [('chest',1.30,1.48,['breastplate','cuirass','gate']),('waist_fauld',1.07,1.20,['fauld']),('shoulders',1.43,1.57,['sloping forged shoulder','turned shoulder']),('upper_arms',1.25,1.38,['rerebrace'])]:
    if lo<=z<=hi and any(t in ob.name.lower() for t in terms):regions[k].append(tuple(p))
  ev.to_mesh_clear()
 return {k:{'samples':len(v),'width_m':max(p[0] for p in v)-min(p[0] for p in v),'depth_m':max(p[1] for p in v)-min(p[1] for p in v)} for k,v in regions.items() if v}

def protected_state():
 import hashlib
 cams={}
 for view in ['hero','front','back','side','head','headside']:
  camera(view);bpy.context.view_layer.update();cams[view]={'matrix_world':[list(row) for row in S.camera.matrix_world],'lens':S.camera.data.lens}
 sword=bpy.data.objects['OATHWAKE | display assembly'];h=hashlib.sha256()
 for ob in sorted(sword.children,key=lambda o:o.name):
  h.update(ob.name.encode());h.update(str([list(row) for row in ob.matrix_world]).encode())
  if ob.type=='MESH':
   for v in ob.data.vertices:h.update(str(tuple(v.co)).encode())
 return {'cameras':cams,'sword_sha256':h.hexdigest(),'root_scale':list(bpy.data.objects['CHARACTER | shoulder-turn study'].scale)}

def regional_fit():
 global S
 bpy.ops.wm.open_mainfile(filepath=str(V7));S=bpy.context.scene;setdevice()
 root=bpy.data.objects['CHARACTER | shoulder-turn study'];records=[];before_dimensions=dimensions();protected_before=protected_state()
 for ob in list(S.objects):
  if ob.parent!=root or ob.type not in ['MESH','CURVE']:continue
  if ob.hide_render or ob.name.startswith('COLLIDER'):continue
  world=ob.matrix_world.copy();inv=world.inverted();coords=[]
  if ob.type=='MESH':coords=[v.co for v in ob.data.vertices]
  else:
   for sp in ob.data.splines:
    coords.extend([p.co for p in sp.points])
    for p in sp.bezier_points:coords.extend([p.co,p.handle_left,p.handle_right])
  maxmove=0
  for p in coords:
   old=world@Vector(p[:3]);new=fit(old,ob.name);local=inv@new;maxmove=max(maxmove,(new-old).length)
   p[0]=local.x;p[1]=local.y;p[2]=local.z
  records.append({'object':ob.name,'control_points':len(coords),'max_displacement_m':maxmove})
 S['v8_scope']='Regional lean silhouette study, original limb lengths/height/cameras/sword/materials preserved. Static fit only.'
 (E/'regional-fit.json').write_text(json.dumps({'source_scene':str(V7.relative_to(R)),'scope':S['v8_scope'],'objects':records,'protected_before':protected_before,'protected_after':protected_state(),'before_regions':before_dimensions,'after_regions':dimensions(),'measurement_scope':'Evaluated mesh samples in identical named armor groups and world-height bands; total bilateral arm span is not limb diameter. Same object membership before/after.'},indent=2)+'\n')
 camera('hero');bpy.ops.wm.save_as_mainfile(filepath=str(D/'last-vigil-v8.blend'))

def audit_protected_reload():
 global S
 bpy.ops.wm.open_mainfile(filepath=str(V7));S=bpy.context.scene;before=protected_state()
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v8.blend'));S=bpy.context.scene;after=protected_state()
 result={'scope':'Fresh saved-scene V7/V8 comparison after explicit dependency-graph camera update; no scene saves','before':before,'after':after,'equal':before==after,'distinct_camera_views':len({str(v['matrix_world']) for v in after['cameras'].values()})}
 (E/'protected-state-reload.json').write_text(json.dumps(result,indent=2)+'\n')
 p=E/'regional-fit.json';old=json.loads(p.read_text());old['protected_before']=before;old['protected_after']=after;old['camera_readback_correction']='Explicit view_layer.update and fresh V7/V8 reload; initial stale matrix readback preserved separately.';p.write_text(json.dumps(old,indent=2)+'\n')
 assert result['equal'] and result['distinct_camera_views']==6

def audit_v8():
 # Six slot test origins must follow the identical helmet fit.
 slots=[]
 for sg in [-1,1]:
  for j in range(3):
   p=fit(Vector((sg*(.031+j*.013),-.25,1.678+j*.004)),'helmet')
   hit,loc,n,index,ob,mat=S.ray_cast(bpy.context.evaluated_depsgraph_get(),p,Vector((0,1,0)),distance=1)
   slots.append({'origin':list(p),'first_hit':ob.name if hit else None,'backing':bool(hit and ob.name=='V7 | recessed breathing slot backing')})
 (E/'v8-slot-audit.json').write_text(json.dumps({'slots':slots,'all_reach_backing':all(s['backing'] for s in slots),'scope':'Point rays only, not manifold or motion certification'},indent=2)+'\n')
 asset_audit();audit_static_clearance();audit_focal();audit_v6_panels()

if mode=='baseline':
 E=E/'baseline-v7';E.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(V7));S=bpy.context.scene;setdevice()
elif mode=='draft':regional_fit()
else:
 bpy.ops.wm.open_mainfile(filepath=str(D/'last-vigil-v8.blend'));S=bpy.context.scene;setdevice()
if mode in ['draft','probe','render','baseline']:
 S.render.resolution_x=1400 if mode=='render' else 720;S.render.resolution_y=1800 if mode=='render' else 920;S.cycles.samples=48 if mode=='render' else 16
 for v in args[1:] or ['hero','front','side','clay_hero']:render(v)
if mode=='audit':audit_protected_reload()
if mode!='baseline':audit_v8()
