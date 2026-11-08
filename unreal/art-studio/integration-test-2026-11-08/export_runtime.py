"""Actual V13 evaluated-mesh rigid attachment trial. Never saves the frozen scene."""
import bpy,math,json,hashlib,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];E=R/'artifacts/art/v13-unreal-test-2026-11-08';OUT=R/'unreal/BossLabWarden/Content/BossLab/V13';OUT.mkdir(parents=True,exist_ok=True);E.mkdir(exist_ok=True)
SCENE=R/'unreal/art-studio/revision-v13-2026-11-07/last-vigil-v13-context.blend';expected='2457b527d43ceea7bf94f16d3fb15fcda230a302253956c36d9c2cbd4ed00839';assert hashlib.sha256(SCENE.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(SCENE));S=bpy.context.scene;bpy.context.view_layer.update()
palette=[('steel',[.16,.18,.20],.46,.9),('aged_bronze',[.16,.09,.025],.53,.8),('oxblood_cloth',[.08,.012,.018],.9,0),('oiled_leather',[.025,.014,.008],.72,0),('charcoal_wool',[.014,.015,.017],.94,0),('fur',[.025,.022,.018],.92,0),('mail',[.08,.09,.10],.57,.85),('polished_edge',[.30,.32,.34],.32,.95)]
materials=[dict(name=n,color=c,roughness=r,metallic=m) for n,c,r,m in palette]
def matid(ob,ma):
 n=((ma.name if ma else '')+' '+ob.name).lower()
 # The main wool material name includes its gold graphic; it is still cloth.
 if 'cape' in ob.name.lower():return 2
 if any(k in n for k in ['bronze','gold','brass','oath mark','brazed','reliquary frame','seated peened stud']):return 1
 if 'cape' in ob.name.lower():return 2
 if 'mail' in n:return 6
 if 'fur' in n or 'hair' in n:return 5
 if any(k in n for k in ['wool','surcoat','padded','darkness','joint padding','collar']):return 4
 if any(k in n for k in ['leather','hide','pouch','binding','strap']):return 3
 if any(k in n for k in ['silver','cutting bevel','polish']):return 7
 return 0
# Blender landmarks are authored source joints, not claimed skeleton skinning.
anchors={'head':((0,0,1.64),(0,0,1),None),'spine_05':((0,0,1.42),(0,0,1),None),'spine_01':((0,0,1.14),(0,0,1),None),'pelvis':((0,0,1.055),(0,0,1),None)}
for sign,label in [(-1,'l'),(1,'r')]:
 shoulder=Vector((sign*.245,0,1.49));elbow=Vector((sign*.351,0,1.187));wrist=Vector((sign*.394,0,.977));hip=Vector((sign*.11,0,1.02));knee=Vector((sign*.118,0,.559));ankle=Vector((sign*.12,0,.14))
 for bone,origin,end,child in [('upperarm',shoulder,elbow,'lowerarm'),('lowerarm',elbow,wrist,'hand'),('hand',wrist,wrist+Vector((-sign*.010,-.005,-.082)),'middle_01'),('thigh',hip,knee,'calf'),('calf',knee,ankle,'foot'),('foot',ankle,ankle+Vector((0,-.12,-.085)),'ball')]:anchors[bone+'_'+label]=(tuple(origin),tuple(end-origin),child+'_'+label if child else None)
anchors['sword']=((0,0,0),(0,0,1),None);anchors['cape']=anchors['spine_05']
def convert(p):return Vector((-100*p.y,100*p.x,100*p.z))
def group(ob,center):
 n=ob.name.lower();par=ob
 if 'cape' in n:return 'cape'
 while par:
  if 'oathwake' in par.name.lower():return 'sword'
  par=par.parent
 if any(k in n for k in ['oathwake','oath mark','pommel','ricasso','quillon','guard worn','reliquary halo']):return 'sword'
 side='l' if center.x<0 else 'r'
 if any(k in n for k in ['skull','crown','visor','occiput','brow','eye darkness','breathing slot']):return 'head'
 if any(k in n for k in ['gorget','collar','mantle','cape','cuirass','reliquary','doublet','neck seal']):return 'spine_05'
 if any(k in n for k in ['metacarpal','finger','thumb','palm','gauntlet']):return 'hand_'+side
 if any(k in n for k in ['vambrace','couter']):return 'lowerarm_'+side
 if any(k in n for k in ['shoulder cup','overlapping lame','rerebrace','arming sleeve']):return 'upperarm_'+side
 if any(k in n for k in ['sabaton','boot']):return 'foot_'+side
 if any(k in n for k in ['greave','poleyn']):return 'calf_'+side
 if any(k in n for k in ['cuisse','chausses','mail skirt','surcoat','tasset']):return 'thigh_'+side
 if 'fauld' in n:return 'spine_01'
 if any(k in n for k in ['belt','buckle','pouch','memorial','tag']):
  if center.z<.55:return 'calf_'+side
  if center.z>1.2 and abs(center.x)>.23:return 'upperarm_'+side
  return 'pelvis'
 if abs(center.x)>.25:
  if center.z<1.0:return 'hand_'+side
  if center.z<1.24:return 'lowerarm_'+side
  if center.z<1.55:return 'upperarm_'+side
 if center.z<.3:return 'foot_'+side
 if center.z<.6:return 'calf_'+side
 if center.z<1.05:return 'thigh_'+side
 return 'spine_05' if center.z>1.2 else 'pelvis'
def target(ob,n):
 s=ob.name.lower()
 if 'unified leather palm' in s:return min(n,2500)
 if 'mail skirt' in s:return min(n,2500)
 if 'overlapping cut leather ribbon' in s:return min(n,1800)
 if 'tailored static cape' in s:return min(n,3500)
 if 'surcoat' in s:return min(n,1800)
 if 'cuirass' in s:return min(n,2500)
 if any(k in s for k in ['skull','visor']):return min(n,1600)
 if any(k in s for k in ['shoulder cup','overlapping lame','gorget']):return min(n,1000)
 if 'collar' in s:return min(n,1200)
 if ob.type=='CURVE':return min(n,48 if 'stitch' in s else 150)
 return min(n,800)
parts={};report=[];excluded=[];total_before=0
originals=list(S.objects)
for ob in originals:
 if ob.type not in ['MESH','CURVE'] or ob.hide_render or ob.name.startswith(('STUDIO','COLLIDER')):continue
 if not ob.parent:excluded.append({'object':ob.name,'reason':'not character/sword parented'});continue
 source=ob;tempcurve=None;groom='grouped curved fur rim' in ob.name
 if groom:
  tempcurve=ob.copy();tempcurve.data=ob.data.copy();bpy.context.collection.objects.link(tempcurve)
  for i in range(len(tempcurve.data.splines)-1,-1,-1):
   if i%18:tempcurve.data.splines.remove(tempcurve.data.splines[i])
  tempcurve.data.resolution_u=2;tempcurve.data.bevel_resolution=0;source=tempcurve
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=source.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);me.calc_loop_triangles();before=len(me.loop_triangles);total_before+=before
 if not before:
  bpy.data.meshes.remove(me);continue
 work=bpy.data.objects.new('EXPORT_TEMP',me);bpy.context.collection.objects.link(work)
 work.matrix_world=ob.matrix_world.copy();bpy.context.view_layer.objects.active=work
 cap=min(before,800) if groom else max(8,int(target(ob,before)*.65))
 if before>cap:
  dec=work.modifiers.new('Testing derived decimation','DECIMATE');dec.ratio=cap/before;dec.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=dec.name)
 me=work.data;me.calc_loop_triangles();points=[work.matrix_world@v.co for v in me.vertices];center=sum(points,Vector())/len(points);bone=group(ob,center)
 if bone not in parts:
  origin,axis,child=anchors[bone];parts[bone]={'name':'V13_'+bone,'bone':'spine_05' if bone=='cape' else bone,'source_origin':list(convert(Vector(origin))) if bone!='sword' else [0,0,0],'source_axis':list(convert(Vector(axis))) if child else [0,0,1],'scale_length':bone.startswith(('upperarm','lowerarm','thigh','calf')),'vertices':[],'normals':[],'uvs':[],'triangles':[]}
  if child:parts[bone]['target_child']=child
 part=parts[bone];mapping={};uv=me.uv_layers.active.data if me.uv_layers.active else None;normalmat=work.matrix_world.to_3x3().inverted().transposed();dropped=0
 for tri in me.loop_triangles:
  p=[points[i] for i in tri.vertices]
  if (p[1]-p[0]).cross(p[2]-p[0]).length<1e-12:dropped+=1;continue
  ids=[]
  for vi,li in zip(tri.vertices,tri.loops):
   q=points[vi];normal=(normalmat@me.vertices[vi].normal).normalized();coord=convert(q)
   if bone=='sword':scale=134/127;coord=Vector((-(q.y+.01)*100*scale,(q.x-.71)*100*scale,14+(1.37-q.z)*100*scale));normal=Vector((-normal.y,normal.x,-normal.z)); # Reflection changes winding below.
   else:normal=Vector((-normal.y,normal.x,normal.z))
   tx=list(uv[li].uv) if uv else [coord.y*.02,coord.z*.02];key=tuple(round(v,6) for v in (*coord,*normal,*tx))
   if key not in mapping:
    mapping[key]=len(part['vertices']);part['vertices'].append([round(v,6) for v in coord]);part['normals'].append([round(v,6) for v in normal]);part['uvs'].append([round(v,6) for v in tx])
   ids.append(mapping[key])
  ma=ob.data.materials[min(tri.material_index,len(ob.data.materials)-1)] if len(ob.data.materials) else None
  if bone=='sword':ids[1],ids[2]=ids[2],ids[1]
  part['triangles'].append(ids+[matid(ob,ma)])
 report.append({'object':ob.name,'bone':bone,'evaluated_triangles_after_groom_sampling':before,'exported_triangles':len(me.loop_triangles)-dropped,'degenerate_triangles_omitted':dropped,'groom_original_splines':len(ob.data.splines) if groom else None,'groom_stride':18 if groom else None})
 bpy.data.objects.remove(work,do_unlink=True);bpy.data.meshes.remove(me)
 if tempcurve:
  data=tempcurve.data;bpy.data.objects.remove(tempcurve,do_unlink=True);bpy.data.curves.remove(data)
 print('EXPORTED',ob.name,report[-1]['exported_triangles'],flush=True)
result={'schema':1,'source_scene_sha256':expected,'materials':materials,'parts':list(parts.values())};triangles=sum(len(p['triangles']) for p in result['parts']);assert triangles<=120000,triangles
for p in result['parts']:
 assert len(p['vertices'])==len(p['normals'])==len(p['uvs']) and all(math.isfinite(x) for v in p['vertices'] for x in v)
file=OUT/'v13-runtime.json';file.write_text(json.dumps(result,separators=(',',':'))+'\n')
audit={'source_scene':str(SCENE.relative_to(R)),'source_scene_sha256':expected,'source_unchanged':hashlib.sha256(SCENE.read_bytes()).hexdigest()==expected,'runtime_file':str(file.relative_to(R)),'runtime_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'parts':len(parts),'triangles':triangles,'vertices':sum(len(p['vertices']) for p in result['parts']),'bytes':file.stat().st_size,'objects':report,'excluded':excluded,'axis':'game authoredcm=(-100*BlenderY,100*BlenderX,100*BlenderZ); rigid source anchors recorded','sword':'Uniform1.0551181102 scale: studio blade z1.37→.10 maps gameZ14→148cm; winding reversed for reflected Z. Blade silhouette actualderivedmesh, not collisionauthority.','material_limits':'Simplified8material palette only; inherited UVs included but no texture/shader transfer or productionUV claim. Cape graphic is not transferred by this palette.','rig_limits':'Rigid bone attachment testing only, no skinning, runtime cape/groom physics or production optimization. Original curved fur sampled every18th spline.','evaluated_triangles_scope':'Count before decimation but AFTER fur spline sampling, not full studio evaluated count.'}
(E/'export-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items() if k not in ['objects','excluded']},indent=2))
