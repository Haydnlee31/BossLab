"""Derived Hearth A2 export; canonical author scene unchanged, explicit UE X reflection."""
import bpy,bmesh,json,math,hashlib,re,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/hearth-a2-2026-11-16';P=E/'export';T=P/'textures';T.mkdir(parents=True,exist_ok=True)
scene=R/'unreal/art-studio/hearth-a2-2026-11-16/final.blend';sourcehash=hashlib.sha256(scene.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(scene));S=bpy.context.scene
# Identify the bright window-side pixels in the actual saved entry camera.
ray_receipt=[];camera=S.camera;frame=camera.data.view_frame(scene=S);xmin=min(v.x for v in frame);xmax=max(v.x for v in frame);ymin=min(v.y for v in frame);ymax=max(v.y for v in frame);zz=frame[0].z
for px,py in [(1167,180),(1172,202),(1204,154),(1180,220),(1420,180),(1420,220),(1380,190),(1435,170)]:
 direction=camera.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*px/1536,ymax-(ymax-ymin)*py/630,zz));hit,loc,norm,index,ob,mat=S.ray_cast(bpy.context.evaluated_depsgraph_get(),camera.location,direction.normalized())
 ray_receipt.append({'entry_pixel':[px,py],'hit':hit,'object':ob.name if ob else None,'world_m':list(loc) if hit else None})
closure_rays=[]
for origin,direction in [((12,5.6,7),(0,0,1)),((0,-10,10),(0,-1,0))]:
 hit,loc,norm,index,ob,mat=S.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector(origin),Vector(direction));closure_rays.append({'origin_m':origin,'hit':hit,'object':ob.name if ob else None,'location_m':list(loc) if hit else None})
assert all(v['hit'] for v in closure_rays)
materials={};pieces={};instances=[];groups={}
def find_image(sock,seen=None):
 seen=set() if seen is None else seen
 for link in sock.links:
  n=link.from_node
  if n.as_pointer() in seen:continue
  seen.add(n.as_pointer())
  if n.type=='TEX_IMAGE':return n.image
  for inp in n.inputs:
   v=find_image(inp,seen)
   if v:return v
 return None
for o in list(S.objects):
 if o.type=='MESH' and o.get('hearth_a2_group') and o['hearth_a2_group']!='diagnostics':groups.setdefault(o['hearth_a2_group'],[]).append(o)
for m in set(m for obs in groups.values() for o in obs for m in o.data.materials if m):
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
 if not bs:raise RuntimeError('Unsupported material '+m.name)
 old=m.name;m.name='M_A2_'+re.sub('[^A-Za-z0-9_]','_',old)
 info={'author_name':old,'color':list(bs.inputs['Base Color'].default_value)[:3],'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'kind':'pbr','arm_occlusion':False}
 for channel,socket in [('diff','Base Color'),('arm','Roughness'),('normal_gl','Normal')]:
  im=find_image(bs.inputs[socket])
  if im:
   path=T/(m.name+'_'+channel+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();info[channel]=str(path.relative_to(R))
 if 'hearth_a2_color_multiplier' in m:info['color_multiplier']=list(m['hearth_a2_color_multiplier'])
 if 'hearth_a2_floor_tint' in m:
  info.update(kind='floor_a2',color_multiplier=list(m['hearth_a2_floor_tint']),roughness=float(m['hearth_a2_floor_dry_roughness']));info.pop('arm',None)
 if m.get('hearth_a2_amber_panel_emission'):info.update(kind='amber_panel',emission_strength=float(m['hearth_a2_amber_panel_emission']))
 if old=='aged oak':info.update(kind='wood',procedural_conversion_limit='Blender generated-coordinate noise translated to UV directional grain; same palette/roughness, not pixel-identical noise')
 if 'quench water' in old:info['kind']='water'
 if 'daylit exterior' in old:info['kind']='window'
 if 'molten' in old.lower() or 'heat' in old.lower():info['kind']='molten'
 if not bs.inputs['Emission Strength'].is_linked and bs.inputs['Emission Strength'].default_value>0:info['emission']=[v*bs.inputs['Emission Strength'].default_value for v in list(bs.inputs['Emission Color'].default_value)[:3]]
 materials[m.name]=info
for group,obs in groups.items():
 name='SM_A2_'+re.sub('[^A-Za-z0-9_]','_',group)
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<=1e-12];removed=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update();o.data.calc_loop_triangles()
 pts=[v.co for v in o.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 info={'triangles':len(o.data.loop_triangles),'removed_tiny_faces':removed,'bounds_m':[lo,hi],'author_bounds_m':[lo,hi],'ue_expected_bounds_m':[[-hi[0],lo[1],lo[2]],[-lo[0],hi[1],hi[2]]],'size_m':[hi[i]-lo[i] for i in range(3)],'materials':[m.name for m in o.data.materials],'finite':all(math.isfinite(x) for p in pts for x in p),'uv_layers':[u.name for u in o.data.uv_layers]}
 assert info['finite'] and info['uv_layers'];pieces[name]=info
 o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops));o.data.update();rot=Matrix.Diagonal((-1,-1,1));normals=[(rot@n.vector).normalized() for n in o.data.corner_normals]
 for v in o.data.vertices:v.co=rot@v.co
 o.data.update();o.data.normals_split_custom_set(normals)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(P/(name+'.fbx')),use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='STRIP',embed_textures=False)
 info['fbx_sha256']=hashlib.sha256((P/(name+'.fbx')).read_bytes()).hexdigest();instances.append({'asset':'/Game/BossLab/HearthA2/'+name,'location_cm':[0,0,0],'rotation_deg':[0,0,0],'scale':[1,1,1]})
def ue(p):return [-100*p[0],100*p[1],100*p[2]]
def point(name,p,color,lm,r):return {'fixture_id':name,'type':'point','casts_shadows':False,'location_cm':ue(p),'color_rgb':color,'intensity_lumens':lm,'attenuation_radius_cm':r}
lights=[point('furnace-mouths',[-4.2,10.5,1.6],[1,.43,.12],1800,1250),point('bellows-lantern',[3.3,10.7,2.65],[1,.67,.38],850,850),point('anvil-lantern',[-6.7,-2.5,2.9],[1,.67,.38],900,950),point('stock-lantern',[6.2,.5,3],[1,.67,.38],1000,1000)]
lights.append({'fixture_id':'gothic-window','type':'spot','casts_shadows':True,'location_cm':ue([10.7,7.5,6]),'target_cm':ue([0,1,0]),'color_rgb':[.63,.78,1],'intensity_lumens':14000,'attenuation_radius_cm':3000,'inner_angle_deg':18,'outer_angle_deg':33})
colliders=[]
for key in ['generated_AnvilWorkstation','generated_StockWorkbay','generated_OreStorage']:
 info=pieces['SM_A2_'+key];lo,hi=info['author_bounds_m'];colliders.append({'cluster_id':key,'location_cm':ue([(lo[i]+hi[i])/2 for i in range(3)]),'extent_cm':[(hi[i]-lo[i])*50+5 for i in range(3)],'yaw_deg':0})
camera=[{'location_cm':ue(p),'extent_cm':e} for p,e in [((-12.4,2,4),[30,1800,500]),((13.5,2,4),[30,1800,500]),((0,-14,4),[1500,30,500]),((0,19.7,4),[1500,30,500])]]
route=[ue(p) for p in [(-2,-1,.95),(-2,5,.95),(3,5,.95),(3,-3,.95),(-2,-5,.95),(-4,-4,.95)]]
layout={'schema_version':2,'scene_id':'hearth-a2','coordinate_space':'unreal_cm','walkable_cm':[1600,1800],'spawn_cm':[400,-400,95],'entry_target_cm':[0,500,95],'entry_pitch_deg':-12,'instances':instances,'lights':lights,'camera_boundary_mode':'outer_proxies','camera_collision':camera,'prop_collision':colliders,'study_waypoints_cm':route,'hearth_effect_anchors_cm':[ue([-5.45,11.7,.9]),ue([-2.95,11.7,.9])],'emission_scope':'Molten channel geometry and amber lantern color mask are emissive; furnace stone is ordinary textured PBR, mouth lights are separate; no whole-mesh glow','coordinate_map':'author(x,y,z) -> Unreal(-100x,100y,100z); FBX disposable vertices rotate XY180 to compensate importer Y reflection'}
for name,value in [('pieces',pieces),('materials',materials),('layout',layout)]: (P/(name+'.json')).write_text(json.dumps(value,indent=2))
assert hashlib.sha256(scene.read_bytes()).hexdigest()==sourcehash
(E/'export-readback.json').write_text(json.dumps({'source_scene':str(scene.relative_to(R)),'source_scene_sha256':sourcehash,'source_unchanged':True,'window_bright_pixel_rays':ray_receipt,'specific_closure_rays':closure_rays,'groups':len(pieces),'triangles':sum(p['triangles'] for p in pieces.values()),'material_count':len(materials),'normal_policy':'recompute retained geometry smoothing then rotate corner normals XY; determinant +1, no reversed winding','limits':'static mesh/UV presence and finite checks, not manifold/global collision; PNG signature normalization must follow','images':[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in bpy.data.images if im.type=='IMAGE']},indent=2));print('A2 EXPORT DONE',len(pieces),len(materials))
