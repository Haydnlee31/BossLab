"""Medieval smeltery modules for an opt-in UE human walkthrough. No engine edits."""
import bpy,math,json,sys,hashlib,random,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[4];E=R/'artifacts/art/bellbreaker-smeltery-2026-11-16';D=R/'unreal/art-studio/bellbreaker-smeltery-2026-11-16';OUT=E/'export';TEX=OUT/'textures'
for p in [D,OUT,TEX]:p.mkdir(parents=True,exist_ok=True)
mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'architecture'
rng=random.Random(6184)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.context.preferences.filepaths.save_version=0
S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1;S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.device='CPU';S.cycles.use_denoising=True;S.cycles.max_bounces=5;S.world.color=(.08,.09,.10)
materials={};groups={};pieces={};instances=[];source_assets=[]
def material(name,color,rough=.8,metal=0,stem=None,kind='pbr'):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 meta={'color':list(color),'roughness':rough,'metallic':metal,'kind':kind}
 if stem:
  folder=R/'artifacts/art/arena-dungeon-2026-11-09/textures'
  for suffix,key in [('diff','diff'),('arm','arm'),('nor_dx','normal_dx')]:
   p=folder/f'{stem}_{suffix}_2k.jpg'
   if not p.exists():continue
   meta[key]=str(p.relative_to(R));im=bpy.data.images.load(str(p),check_existing=True);im.pack();n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im
   if key=='diff':m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
   elif key=='arm':
    im.colorspace_settings.name='Non-Color';sep=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(n.outputs['Color'],sep.inputs['Color']);m.node_tree.links.new(sep.outputs['Green'],bs.inputs['Roughness'])
  # Blender view uses gentle actual high-frequency bump; UE uses the genuine normal map.
  noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=60;bu=m.node_tree.nodes.new('ShaderNodeBump');bu.inputs['Distance'].default_value=.015;bu.inputs['Strength'].default_value=.15;m.node_tree.links.new(noise.outputs['Fac'],bu.inputs['Height']);m.node_tree.links.new(bu.outputs['Normal'],bs.inputs['Normal'])
 if kind=='molten':bs.inputs['Base Color'].default_value=(.19,.027,.003,1);bs.inputs['Emission Color'].default_value=(1,.12,.005,1);bs.inputs['Emission Strength'].default_value=4
 materials[name]=meta;return m
stone=material('M_SmeltStone',(.16,.135,.10),stem='castle_wall_varriation');floor=material('M_SmeltFloor',(.20,.18,.15),stem='cobblestone_pavement');dark=material('M_SmeltSoot',(.045,.038,.031),.96);roof=material('M_SmeltVault',(.075,.062,.048),stem='castle_wall_slates');wood=material('M_SmeltOak',(.12,.055,.020),.86,kind='wood');iron=material('M_SmeltIron',(.055,.045,.032),.58,.72);lava=material('M_SmeltMolten',(.25,.035,.002),.8,kind='molten');slag=material('M_SmeltSlag',(.025,.022,.018),.97)
def register(o,group):groups.setdefault(group,[]).append(o);return o
def mesh(n,v,f,m,g):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.data.materials.append(m);return register(o,g)
def box(n,loc,size,m,g,bevel=0):
 sx,sy,sz=[q/2 for q in size];v=[(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
 o=mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,g);o.location=loc
 if bevel:mod=o.modifiers.new('worn stone edge','BEVEL');mod.width=bevel;mod.segments=1
 return o
def beam(n,a,b,width,depth,m,g):
 a,b=Vector(a),Vector(b);o=box(n,(a+b)/2,(width,depth,(b-a).length),m,g,.035);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def stoneblock(n,loc,size,g='SM_SmelteryMasonry'):
 o=box(n,loc,size,stone,g,.045);o.rotation_euler.z=rng.uniform(-.012,.012);return o
# Continuous exactly level walk floor, with quiet flush inset casting scars.
box('continuous walk floor',(0,0,-.22),(43,57,.44),floor,'SM_SmelteryFloor')
box('rear furnace floor recess',(0,31,-.22),(14,9,.44),floor,'SM_SmelteryFloor')
for x in [-1,1]:box('workshop floor',(x*23,0,-.22),(5,54,.44),floor,'SM_SmelteryFloor')
for side in [-1,1]:
 for y in [-13,-3,11]:
  o=box('peripheral flush scorched repair',(side*12.9,y,.001),(rng.uniform(.5,1.1),rng.uniform(1.2,2.4),.001),dark,'SM_SmelteryFloor');o.rotation_euler.z=rng.uniform(-.4,.4)
# Thick supported medieval vault and lower workshop enclosure.
def arch(n,cx,cy,half,spring,rise,depth,thick,count=30):
 for k in range(count):
  a=math.pi*k/count+.003;b=math.pi*(k+1)/count-.003
  v=[]
  for yy in [cy-depth/2,cy+depth/2]:
   for r,zr,t in [(half,rise,a),(half,rise,b),(half+thick,rise+thick,b),(half+thick,rise+thick,a)]:v.append((cx+r*math.cos(t),yy,spring+zr*math.sin(t)))
  o=mesh(n,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone,'SM_SmelteryMasonry')
  mod=o.modifiers.new('chipped voussoir edge','BEVEL');mod.width=.025;mod.segments=1
for side in [-1,1]:
 box('workshop wall mortar core',(side*24.8,0,2.8),(.8,55,5.6),dark,'SM_SmelteryMasonry')
 for row in range(8):
  y=-27.2
  while y<27:
   length=rng.uniform(1.0,1.8);stoneblock('irregular thick fieldstone',(side*24.25,y+length/2,.35+row*.7),(.7,length-.025,.68+rng.uniform(-.01,.01)));y+=length
 for y in [-24,-16,-8,0,8,16,24]:
  box('pier recessed mortar heart',(side*18.1,y,2.8),(1.35,1.45,5.6),dark,'SM_SmelteryMasonry')
  for row in range(8):stoneblock('deep full pier course',(side*18.1+rng.uniform(-.02,.02),y+rng.uniform(-.02,.02),.35+row*.70),(1.9+rng.uniform(-.04,.04),2.05+rng.uniform(-.03,.03),.685))
  stoneblock('spread pier foot',(side*18.1,y,.3),(2.3,2.4,.6));stoneblock('vault bearing capital',(side*18.1,y,5.6),(2.25,2.4,.6))
  beam('short pegged workshop brace',(side*18.3,y,4.0),(side*22,y,5.0),.35,.42,wood,'SM_SmelteryTimber')
  beam('workshop supported rafter',(side*18.3,y,5.3),(side*25,y,4.5),.33,.40,wood,'SM_SmelteryTimber')
 for i in range(20):box('aged oak workshop roof',(side*(18.5+i*.32),0,5.3-i*.04),(.30,54,.15),wood,'SM_SmelteryTimber')
 # Small workshop arches turn toward nave, mechanically supported on short masonry posts.
 for yy in [-20,-12,-4,4,12,20]:
  # build in XY then rotate whole arch set around its centre into longitudinal side opening
  before=len(groups.get('SM_SmelteryMasonry',[]));arch('workshop arched opening',0,0,2.6,2.6,2.2,.75,.5,16)
  for ob in groups['SM_SmelteryMasonry'][before:]:
   for v in ob.data.vertices:x,z=v.co.x,v.co.z;v.co=(side*23.5+v.co.y,yy+x,z)
  for dy in [-2.6,2.6]:stoneblock('workshop arch jamb',(side*23.5,yy+dy,1.3),(1.1,1.0,2.6))
for y in [-24,-16,-8,0,8,16,24]:arch('individual nave voussoir',0,y,18,5.7,11.0,1.05,.72,42)
# Continuous curved stone barrel between load-bearing ribs, no gable roof strips.
for i in range(48):
 a=math.pi*i/48;b=math.pi*(i+1)/48
 mesh('heavy curved vault soffit',[(18.8*math.cos(a),-28,5.7+11.8*math.sin(a)),(18.8*math.cos(b),-28,5.7+11.8*math.sin(b)),(18.8*math.cos(b),32,5.7+11.8*math.sin(b)),(18.8*math.cos(a),32,5.7+11.8*math.sin(a))],[(0,1,2,3)],roof,'SM_SmelteryRoof')
# Rear forge sits in a supported deep masonry alcove, not in a blank garage panel.
arch('deep furnace alcove voussoir',0,25.0,6.3,4.8,7.1,1.9,.85,28)
for side in [-1,1]:
 for row in range(7):stoneblock('furnace alcove jamb',(side*6.65,25, .35+row*.7),(1.2,2.0,.68))
# Irregular fitted masonry surrounding arched void. Back wall closes actual recess.
for y,isfront in [(25.1,True),(34.0,False),(-28.0,True)]:
 for row in range(23):
  z=.35+row*.7
  gap=(6.4 if z<4.8 else 6.4*math.sqrt(max(0,1-((z-4.8)/7.3)**2))) if isfront else 0
  if y<0:gap=4.8 if z<5.5 else 4.8*math.sqrt(max(0,1-((z-5.5)/4.2)**2))
  for side in [-1,1]:
   x=max(gap,.02)
   while x<18.8:
    width=min(rng.uniform(1.05,1.95),18.8-x)
    if width>.06:stoneblock('load-bearing end fieldstone',(side*(x+width/2),y,z),(width-.025,1.05,.68))
    x+=width
arch('entrance stone arch',0,-27.8,4.9,5.5,4.2,1.4,.65,24)
box('sealed aged timber entrance',(0,-28.3,2.6),(9.5,.45,5.2),wood,'SM_SmelteryTimber')
for z in [1,3,4.7]:box('entrance forged binding',(0,-28,z),(9.5,.14,.13),iron,'SM_SmelteryTimber')
# Low continuous curb makes engine boundary legible; no geometry enters the walk rectangle.
for side in [-1,1]:
 for y in range(-18,18):stoneblock('visible walk boundary coping',(side*14.28,y+.5,.22),(.48,.98,.44),'SM_SmelteryCoping')
 for x in range(-14,14):stoneblock('visible walk end coping',(x+.5,side*18.28,.22),(.98,.48,.44),'SM_SmelteryCoping')
# Protected narrow molten channels: low stone basins outside walk floor.
for side in [-1,1]:
 x=side*17.8
 box('contained molten run',(x,0,.3075),(.6,35,.025),lava,'SM_SmelteryMolten')
 for offset in [-.55,.55]:
  for j in range(22):stoneblock('molten channel thick coping',(x+offset,-16.7+j*1.59,.25),(.45,1.53,.5),'SM_SmelteryCoping')
 for y in [-17.4,17.4]:stoneblock('molten channel closed end',(x,y,.25),(1.55,.45,.5),'SM_SmelteryCoping')
 # short stone lids at working crossings, not accessible ramps.
 for y in [-12,0,12]:stoneblock('channel stone crossing lid',(x,y,.54),(1.6,1.5,.15),'SM_SmelteryCoping')
box('forge molten receiving basin',(0,22.2,.3075),(9,.7,.025),lava,'SM_SmelteryMolten')
for y in [21.6,22.8]:
 for x in [-4,-2,0,2,4]:stoneblock('rear casting basin curb',(x,y,.28),(1.95,.45,.56),'SM_SmelteryCoping')
# Sparse coal heaps and cooled slag piles stay off the walkable rectangle.
for side in [-1,1]:
 for y in [-20,-4,18]:
  for i in range(7):
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rng.uniform(.18,.42),location=(side*(15.2+rng.random()*.7),y+rng.uniform(-.6,.6),.17));o=bpy.context.object;o.name='cooled coal outside walking edge';o.scale.z=.55;o.data.materials.append(slag);register(o,'SM_SmelteryCoping')
# Small volumetric ember beds inside the two actual forward hearth mouths; no flame cards.
if not mode.startswith('architecture'):
 for side in [-1,1]:
  for k in range(16):
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rng.uniform(.12,.24),location=(side*1.45+rng.uniform(-.45,.45),23.65+rng.uniform(-.12,.35),1.35+rng.uniform(0,.22)));o=bpy.context.object;o.name='contained forge ember';o.scale.z=.6;o.data.materials.append(lava);register(o,'SM_SmelteryMolten')
print('Architecture meshes constructed',len(bpy.data.objects),flush=True)
# Export physical planar UVs for authored architecture.
bpy.context.view_layer.update()
for g,obs in groups.items():
 for o in obs:
  if o.type!='MESH':continue
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='physical scale UV')
  for poly in o.data.polygons:
   n=o.matrix_world.to_3x3()@poly.normal;axis=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=axis];tile=3.0 if g!='SM_SmelteryFloor' else 4.5
   for li in poly.loop_indices:
    co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/tile,co[axes[1]]/tile)
# Optional actual generated assets; no placeholder mesh masquerading as final generated art.
config=Path(__file__).with_name('assets.json');cfg=json.loads(config.read_text()) if config.exists() else {}
if mode.startswith('architecture'):cfg={}
if mode=='final':
 missing=[e['path'] for e in cfg.values() if not (R/e['path']).exists()]
 if missing:raise RuntimeError('Final assembly missing generated source meshes: '+str(missing))
def find_image(sock,seen=None):
 seen=seen or set()
 for link in sock.links:
  node=link.from_node
  if node in seen:continue
  seen.add(node)
  if node.type=='TEX_IMAGE' and node.image:return node.image
  for inp in node.inputs:
   im=find_image(inp,seen)
   if im:return im
 return None
def import_asset(key,entry):
 p=R/entry['path']
 if not p.exists():return
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));obs=[o for o in set(bpy.data.objects)-before if o.type=='MESH'];allnew=set(bpy.data.objects)-before
 rot=Matrix.Rotation(math.radians(entry.get('rotate_z_deg',0)),4,'Z');coords={o:[rot@o.matrix_world@v.co for v in o.data.vertices] for o in obs};ps=[v for a in coords.values() for v in a];lo=Vector(tuple(min(v[i] for v in ps) for i in range(3)));hi=Vector(tuple(max(v[i] for v in ps) for i in range(3)));size=hi-lo;fit=min(entry['bounds_m'][i]/max(1e-8,size[i]) for i in range(3));center=(lo+hi)/2
 total=0
 for o in obs:o.data.calc_loop_triangles();total+=len(o.data.loop_triangles)
 asset='SM_'+key
 for o in obs:
  o.data=o.data.copy();o.parent=None
  for v,co in zip(o.data.vertices,coords[o]):v.co=(co-Vector((center.x,center.y,lo.z)))*fit
  o.matrix_world.identity();o.name=asset
  mod=o.modifiers.new('derived mesh budget','DECIMATE');mod.ratio=min(1,entry.get('triangles',40000)/max(1,total));bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  # Remove confirmed area-zero faces on derived copies, preserve original HF file.
  bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if f.calc_area()<=1e-12];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free()
  for slot in o.material_slots:
   if not slot.material:continue
   m=slot.material;m.name=asset+'_'+m.name.replace('.','_');bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   if not bs:continue
   info={'color':list(bs.inputs['Base Color'].default_value)[:3],'roughness':float(bs.inputs['Roughness'].default_value),'metallic':float(bs.inputs['Metallic'].default_value),'kind':'pbr'}
   for channel,socket in [('diff','Base Color'),('arm','Roughness'),('normal_gl','Normal')]:
    im=find_image(bs.inputs[socket])
    if im:
     path=TEX/(m.name+'_'+channel+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();im.pack();info[channel]=str(path.relative_to(R))
   materials[m.name]=info
  register(o,asset)
 for o in allnew:
  if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
 source_assets.append({'key':key,'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_triangles':total,'fit_scale':fit,'fitted_size_m':list(size*fit),'placements':entry['instances']})
 for placement in entry['instances']:instances.append({'asset':'/Game/BossLab/Smeltery/'+asset,'location_cm':[v*100 for v in placement['location_m']],'rotation_deg':[0,placement.get('yaw_deg',0),0],'scale':[1,1,1]})
for key,entry in cfg.items():import_asset(key,entry)
# Export each mesh family, apply modifiers once, keep separate reusable prop pivots.
for g,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=g;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 o.data.calc_loop_triangles();points=[v.co for v in o.data.vertices];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
 pieces[g]={'triangles':len(o.data.loop_triangles),'area_le_1e_12_triangles':sum(t.area<=1e-12 for t in o.data.loop_triangles),'finite_vertices':all(all(math.isfinite(c) for c in v.co) for v in o.data.vertices),'bounds_m':[lo,hi],'size_m':[hi[i]-lo[i] for i in range(3)],'materials':[m.name for m in o.data.materials],'source':'derived generated prop' if any('/'+g==i['asset'][-len(g)-1:] for i in instances) else 'authored modular architecture'}
 bpy.ops.export_scene.fbx(filepath=str(OUT/(g+'.fbx')),use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,path_mode='STRIP',embed_textures=False)
 if not any(i['asset'].endswith('/'+g) for i in instances):instances.append({'asset':'/Game/BossLab/Smeltery/'+g,'location_cm':[0,0,0],'rotation_deg':[0,0,0],'scale':[1,1,1]})
# Place mesh instances only after local-pivot exports; source assets remain untouched.
for i in instances:
 name=i['asset'].split('/')[-1];source=bpy.data.objects.get(name)
 if not source:continue
 ob=source.copy();ob.data=source.data;S.collection.objects.link(ob);ob.name=name+'_PLACED';ob.location=Vector(i['location_cm'])/100;ob.rotation_euler.z=math.radians(i['rotation_deg'][1])
for name in pieces:bpy.data.objects[name].hide_render=True;bpy.data.objects[name].hide_set(True)
(OUT/'pieces.json').write_text(json.dumps(pieces,indent=2));(OUT/'materials.json').write_text(json.dumps(materials,indent=2));(OUT/'layout.json').write_text(json.dumps({'schema':1,'units':'cm','axis':'+X width,+Y rear forge,Zup','walkable_cm':[2800,3600],'instances':instances,'lights':[{'location_cm':[0,2000,250],'color_rgb':[1,.27,.045],'intensity_lumens':3000,'attenuation_radius_cm':2000},{'location_cm':[-1300,-200,400],'color_rgb':[1,.64,.38],'intensity_lumens':2000,'attenuation_radius_cm':1800},{'location_cm':[1300,-100,400],'color_rgb':[1,.64,.38],'intensity_lumens':2000,'attenuation_radius_cm':1800}]},indent=2));(OUT/'sources.json').write_text(json.dumps(source_assets,indent=2))
# One efficient preview, not a substitute for the real Unreal walkthrough.
def light(n,loc,power,size,col,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(n,d);S.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('forge amber bounce',(0,22,5),2500,8,(1,.40,.12),(0,0,2));light('high pale daylight',(0,-6,11),6500,14,(.72,.79,1),(0,0,0));light('entry reflected light',(0,-23,5),1800,10,(1,.76,.52),(0,10,3))
bpy.ops.object.camera_add(location=(0,-18,1.8));S.camera=bpy.context.object;S.camera.rotation_euler=(Vector((0,20,4))-S.camera.location).to_track_quat('-Z','Y').to_euler();S.camera.data.lens=26
S.render.resolution_x=1200;S.render.resolution_y=800;S.render.resolution_percentage=100
for im in bpy.data.images:
 if im.type=='IMAGE' and im.size[0]>0 and not im.packed_file:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(D/(mode+'.blend')));S.render.filepath=str(E/(mode+'-preview.png'));bpy.ops.render.render(write_still=True)
print(json.dumps({'mode':mode,'pieces':len(pieces),'instances':len(instances),'triangles_unique':sum(v['triangles'] for v in pieces.values()),'source_assets':source_assets},indent=2))
