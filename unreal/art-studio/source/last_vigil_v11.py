"""Bounded V11 projection study. Baked concept image on actual coarse shells; NOT PBR."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];D=R/'unreal/art-studio/revision-v11-2026-11-07';E=R/'artifacts/art/last-vigil-v11';D.mkdir(exist_ok=True);E.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:];mode=args[0] if args else 'draft';ATTEMPT=3
SOURCE=R/'artifacts/art/last-vigil-concept-2026-11-07/concept-target-not-built.png'
S=bpy.context.scene

def material(name,color,metal=0,rough=.6):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough;return m

def point(px,py,depth):return ((px-473)/500,depth,(650-py)/500)

def mesh(name,vs,fs,projected_flags):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();import bmesh;bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(PROJECT);me.materials.append(FALLBACK)
 uv=me.uv_layers.new(name='V11 reference orthographic projection')
 for face,flag in zip(me.polygons,projected_flags):
  face.material_index=0 if flag else 1;face.use_smooth=True
  for li in face.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((p.x*500+473)/WIDTH,1-(650-p.z*500)/HEIGHT)
 ob['detail_scope']='Only coarse shell/overlap is geometry. Rivets, grooves, fur strands, wear and lighting are projected pixels.'
 return ob

def shell(name,outline,edge_depth,bulge=.02,thickness=.008):
 # Convex bounded shell, not a planar billboard: interior ring and centre provide actual depth.
 cx=sum(p[0] for p in outline)/len(outline);cy=sum(p[1] for p in outline)/len(outline);N=len(outline);vs=[]
 for shrink,depth in [(1,edge_depth),(.64,edge_depth-bulge*.85)]:
  for x,y in outline:
   px=cx+(x-cx)*shrink;py=cy+(y-cy)*shrink
   if 'shoulder' in name or 'collar' in name:
    inner=min(p[0] for p in outline) if cx>473 else max(p[0] for p in outline);outer=max(p[0] for p in outline) if cx>473 else min(p[0] for p in outline);t=(px-inner)/(outer-inner);depth=-.16+.24*max(0,t)**1.5-bulge*(1-shrink)
   vs.append(point(px,py,depth))
 centerdepth=(-.16+.24*.5**1.5-bulge) if ('shoulder' in name or 'collar' in name) else edge_depth-bulge;vs.append(point(cx,cy,centerdepth));centre=len(vs)-1
 for k,(x,y) in enumerate(outline):vs.append((vs[k][0],vs[k][1]+thickness,vs[k][2]))
 fs=[];flags=[]
 for k in range(N):
  j=(k+1)%N;fs.extend([(k,j,N+j,N+k),(N+k,N+j,centre),(k,centre+1+k,centre+1+j,j)]);flags.extend([True,True,False])
 fs.append(tuple(reversed([centre+1+k for k in range(N)])));flags.append(False)
 return mesh(name,vs,fs,flags)

def build():
 global S,PROJECT,FALLBACK,WIDTH,HEIGHT
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);S=bpy.context.scene
 S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=24;S.cycles.use_denoising=True;S.render.resolution_x=960;S.render.resolution_y=960;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='Standard';S.view_settings.look='None';S.view_settings.exposure=0;S.view_settings.gamma=1
 image=bpy.data.images.load(str(SOURCE));image.name='V11 approved generated concept - baked lighting NOT PBR';image.use_fake_user=True;image.pack();WIDTH,HEIGHT=image.size
 PROJECT=bpy.data.materials.new('V11 IMAGE PROJECTION baked light NOT PBR');PROJECT.use_nodes=True;n=PROJECT.node_tree.nodes;n.clear();l=PROJECT.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map='V11 reference orthographic projection';tx=n.new('ShaderNodeTexImage');tx.image=image;tx.extension='CLIP';em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1;out=n.new('ShaderNodeOutputMaterial');l.new(uv.outputs['UV'],tx.inputs['Vector']);l.new(tx.outputs['Color'],em.inputs['Color']);l.new(em.outputs[0],out.inputs['Surface'])
 FALLBACK=material('V11 neutral unseen sides - no invented source detail',(.012,.015,.019),0,.85)
 rows=[(437,[386,419,457,499,548],[-.08,-.16,-.20,-.16,-.07]),(481,[383,414,455,501,556],[-.06,-.16,-.215,-.16,-.05]),(540,[391,418,455,496,549],[-.045,-.145,-.195,-.14,-.04]),(600,[399,421,456,492,535],[-.025,-.12,-.165,-.12,-.02]),(615,[397,421,456,492,536],[-.02,-.115,-.155,-.11,-.015])]
 vs=[]
 for y,xs,ds in rows:
  vs.extend(point(x,y,d) for x,d in zip(xs,ds));vs.extend(point(x,y,.08) for x in reversed(xs))
 fs=[];flags=[]
 for row in range(len(rows)-1):
  for j in range(10):fs.append((row*10+j,row*10+(j+1)%10,(row+1)*10+(j+1)%10,(row+1)*10+j));flags.append(j<4)
 fs.extend([tuple(reversed(range(10))),tuple(40+i for i in range(10))]);flags.extend([False,False]);mesh('V11 | real depth breastplate and side returns',vs,fs,flags)
 left=[[(316,434),(350,410),(398,429),(399,462),(359,470),(308,451)],[(308,450),(352,445),(395,458),(384,479),(345,489),(304,471)],[(304,476),(345,469),(383,479),(374,502),(338,512),(301,495)],[(301,502),(339,496),(373,506),(366,529),(329,536),(298,520)],[(298,527),(332,521),(367,533),(361,552),(320,559),(295,546)]]
 right=[[(544,435),(587,430),(629,448),(648,492),(607,494),(552,477)],[(553,477),(607,483),(644,498),(652,521),(611,516),(563,501)],[(563,502),(611,511),(651,524),(655,546),(615,540),(572,524)],[(572,527),(615,535),(654,550),(650,566),(612,561),(580,547)]]
 for sg,plates in [('left',left),('right',right)]:
  for i,outline in enumerate(plates):shell('V11 | '+sg+' shoulder physical plate '+str(i),outline,-.105+i*.009,.025,.012)
 shell('V11 | left collar coarse fur mass',[(340,410),(345,396),(381,383),(410,388),(431,407),(438,431),(411,447),(385,434),(357,430)],-.15,.024,.035)
 shell('V11 | right collar coarse fur mass',[(507,382),(524,363),(545,367),(557,387),(584,391),(611,412),(637,429),(648,462),(626,456),(601,445),(570,455),(547,443),(520,439)],-.16,.032,.04)
 # Integrated hollow gorget; front source-projected, back/inside neutral and explicit.
 vs=[];fs=[];flags=[];N=64
 for radius_x,radius_y,z in [(.100,.100,.431),(.098,.095,.488),(.092,.089,.540),(.087,.084,.540),(.093,.090,.488),(.095,.095,.431)]:
  for k in range(N):
   a=2*math.pi*k/N;vs.append((.012+radius_x*math.sin(a),-.020-radius_y*math.cos(a),z))
 for j in range(6):
  for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,((j+1)%6)*N+(k+1)%N,((j+1)%6)*N+k));flags.append(j<2 and math.cos(2*math.pi*(k+.5)/N)>0)
 mesh('V11 | integrated hollow gorget',vs,fs,flags)
 # Coherent neutral upper-arm roots join torso under the projected plate shells.
 for sign in [-1,1]:
  vs=[];fs=[];N=40
  for cx,cy,z,rx,ry in [(.185,.005,.430,.075,.09),(.245,.010,.390,.087,.10),(.283,.015,.320,.079,.095),(.300,.020,.240,.062,.080),(.300,.022,.185,.052,.070)]:
   for k in range(N):
    a=2*math.pi*k/N;vs.append((sign*(cx+rx*math.cos(a)),cy+ry*math.sin(a),z))
  for j in range(4):
   for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
  fs.extend([tuple(reversed(range(N))),tuple(4*N+k for k in range(N))]);mesh('V11 | neutral connected arm root '+str(sign),vs,fs,[False]*len(fs))
 world=bpy.data.worlds.new('V11 neutral studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.018,.021,.025,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;S.world=world
 for name,loc,power,size in [('key',(-1,-2,2),300,2),('rim',(1,1,1.5),400,2)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='V11 '+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.35))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();S.camera=bpy.context.object;S.camera.name='V11 study camera';S.camera.data.type='ORTHO';S.camera.data.ortho_scale=.82
 bpy.ops.object.text_add();label=bpy.context.object;label.name='V11 image evidence label';label.data.align_x='CENTER';label.data.size=.012;label.data.body='IMAGE-PROJECTED STUDY / BAKED LIGHT / NOT PBR'
 lm=bpy.data.materials.new('V11 evidence label emission');lm.use_nodes=True;ln=lm.node_tree.nodes;ln.clear();le=ln.new('ShaderNodeEmission');le.inputs[0].default_value=(.75,.78,.82,1);lo=ln.new('ShaderNodeOutputMaterial');lm.node_tree.links.new(le.outputs[0],lo.inputs[0]);label.data.materials.append(lm)
 camera('reference');bpy.ops.wm.save_as_mainfile(filepath=str(D/'v11-attempt-03.blend'))
 (E/'attempt-03-construction.json').write_text(json.dumps({'attempt':ATTEMPT,'maximum_attempts':3,'source_image':str(SOURCE.relative_to(R)),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_size':[WIDTH,HEIGHT],'projection':'Orthographic +Y; x=(pixel_x-473)/500; z=(650-pixel_y)/500. Image projected only onto authored front shell faces.','world_units':'meters, approximate study scale, not calibrated photogrammetry','chest_rows_pixels_and_depth_m':rows,'left_shoulder_outlines':left,'right_shoulder_outlines':right,'material':'Pure emission baked-image projection. No inferred PBR, no relighting/detail claim. Unseen sides/back neutral.','physics':False,'limitations':'Only chest/plate/collar mass and overlaps are geometry; engraving, rivets, fur strands and scratches are image detail.'},indent=2)+'\n')

def camera(view):
 target=Vector((0,0,.34));pos={'reference':(0,-3,.34),'three-quarter':(1.8,-2.4,.55),'side':(3,0,.40)}[view];S.camera.location=pos;S.camera.rotation_euler=(target-Vector(pos)).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
 label=bpy.data.objects['V11 image evidence label'];q=S.camera.rotation_euler.to_quaternion();label.location=S.camera.location+q@Vector((0,-.385,-2));label.rotation_euler=S.camera.rotation_euler

def render(view):
 clay=view.startswith('clay-');diagnostic=view.startswith('uv-');cam=view[5:] if clay else view[3:] if diagnostic else view;camera(cam);label=bpy.data.objects['V11 image evidence label'];label.data.body=('CLAY: ACTUAL COARSE GEOMETRY / NO PROJECTED DETAIL' if clay else 'UV DIAGNOSTIC: ORTHOGRAPHIC SOURCE COORDINATES' if diagnostic else 'IMAGE-PROJECTED STUDY / BAKED LIGHT / NOT PBR');restores=[]
 if clay or diagnostic:
  ma=material('V11 clay diagnostic',(.24,.26,.28),0,.8)
  if diagnostic:
   n=ma.node_tree.nodes;n.clear();l=ma.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map='V11 reference orthographic projection';tx=n.new('ShaderNodeTexChecker');tx.inputs['Scale'].default_value=35;tx.inputs['Color1'].default_value=(.06,.25,.7,1);tx.inputs['Color2'].default_value=(.85,.85,.75,1);em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(uv.outputs[0],tx.inputs['Vector']);l.new(tx.outputs['Color'],em.inputs[0]);l.new(em.outputs[0],out.inputs[0])
  for ob in S.objects:
   if ob.type=='MESH':
    for slot in ob.material_slots:restores.append((slot,slot.material));slot.material=ma
 S.render.filepath=str(E/('attempt-03-'+view+'.png'));bpy.ops.render.render(write_still=True)
 for slot,ma in restores:slot.material=ma

if mode=='draft':build()
else:bpy.ops.wm.open_mainfile(filepath=str(D/'v11-attempt-03.blend'));S=bpy.context.scene
if mode=='audit':
 meshes=[]
 for ob in S.objects:
  if ob.type!='MESH':continue
  ob.data.calc_loop_triangles();points=[ob.matrix_world@v.co for v in ob.data.vertices];uv=ob.data.uv_layers.active
  meshes.append({'name':ob.name,'vertices':len(points),'triangles':len(ob.data.loop_triangles),'bounds_min':[min(p[k] for p in points) for k in range(3)],'bounds_max':[max(p[k] for p in points) for k in range(3)],'finite_geometry':all(math.isfinite(c) for p in points for c in p),'finite_uv':all(math.isfinite(c) for v in uv.data for c in v.uv),'projected_faces':sum(p.material_index==0 for p in ob.data.polygons),'neutral_faces':sum(p.material_index==1 for p in ob.data.polygons)})
 images=[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size),'packed_sha256':hashlib.sha256(im.packed_file.data).hexdigest() if im.packed_file else None} for im in bpy.data.images]
 report={'attempt':ATTEMPT,'maximum_attempts':3,'meshes':meshes,'packed_images':images,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==json.loads((E/'attempt-01-construction.json').read_text())['source_sha256'],'projection_material':'Emission baked image; explicitly not PBR/relightable','actual_geometry_scope':'Coarse bust volume, shoulder layers, collar masses, hollow gorget and neutral support only','physics':'Off; no simulation or contact certification','no_billboard_geometry_claim':'Depth bounds recorded per piece; side/clay renders expose actual shape and projection limits'}
 (E/'attempt-03-reload-audit.json').write_text(json.dumps(report,indent=2)+'\n');assert all(m['finite_geometry'] and m['finite_uv'] for m in meshes) and report['source_unchanged'] and any(im['packed_sha256']==report['source_sha256'] for im in images)
else:
 for view in args[1:] or ['reference','three-quarter','side','clay-reference','clay-side','uv-reference']:render(view)
