"""Uniformly fit original generated props on derived copies; no source mutation."""
import bpy,bmesh,math,json,hashlib
from mathutils import Vector,Matrix

def load_assets(root,evidence,config,groups):
 report=[]
 for key,entry in config.items():
  path=root/entry['path']
  if not path.is_file():
   report.append({'asset':key,'status':'not generated yet','source':entry['path']});continue
  if 'rotate_source_z_deg' not in entry:
   report.append({'asset':key,'status':'awaiting actual orientation probe','source':entry['path']});continue
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));bpy.context.view_layer.update();new=set(bpy.data.objects)-before;obs=[o for o in new if o.type=='MESH'];rotation=Matrix.Rotation(math.radians(entry['rotate_source_z_deg']),4,'Z')
  coords={o:[rotation@o.matrix_world@v.co for v in o.data.vertices] for o in obs};vs=[v for points in coords.values() for v in points];lo=Vector([min(p[i] for p in vs) for i in range(3)]);hi=Vector([max(p[i] for p in vs) for i in range(3)]);size=hi-lo;centre=(lo+hi)/2;scale=min(entry['bounds_m'][i]/size[i] for i in range(3));total=0
  for o in obs:o.data.calc_loop_triangles();total+=len(o.data.loop_triangles)
  removed=0;tris=0;points=[]
  for o in obs:
   o.parent=None;o.matrix_world=Matrix.Identity(4)
   for v,p in zip(o.data.vertices,coords[o]):v.co=(p-Vector((centre.x,centre.y,lo.z)))*scale
   o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops));o.data.update()
   bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('derived detail budget','DECIMATE');mod.ratio=min(1,entry['triangles']/total);bpy.ops.object.modifier_apply(modifier=mod.name)
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<=1e-12];removed+=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free();o.data.update();o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
   o.name='A2_'+key;o.location=entry['position_m'];o.rotation_euler.z=math.radians(entry.get('yaw_deg',0));groups.setdefault('generated_'+key,[]).append(o)
   for mat in o.data.materials:
    if mat and mat.use_nodes:
     if entry.get('amber_emission') and not mat.get('hearth_a2_amber_panel_emission'):
      nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');base=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].is_linked else None
      if base:
       sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(base,sep.inputs[0])
       def mn(op,a,b):
        n=nt.nodes.new('ShaderNodeMath');n.operation=op
        for i,v in enumerate([a,b]):
         if isinstance(v,(int,float)):n.inputs[i].default_value=v
         else:nt.links.new(v,n.inputs[i])
        return n.outputs[0]
       amber=mn('MULTIPLY',mn('GREATER_THAN',sep.outputs['Red'],mn('MULTIPLY',sep.outputs['Blue'],1.5)),mn('GREATER_THAN',sep.outputs['Red'],.055))
       nt.links.new(base,bs.inputs['Emission Color']);nt.links.new(mn('MULTIPLY',amber,3.0),bs.inputs['Emission Strength']);mat['hearth_a2_amber_panel_emission']=3.0
     for n in mat.node_tree.nodes:
      if n.type=='TEX_IMAGE' and n.image:n.image.pack()
  for o in new:
   if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
  bpy.context.view_layer.update()
  for o in obs:points.extend(o.matrix_world@v.co for v in o.data.vertices)
  bounds=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]]
  report.append({'asset':key,'status':'actual derived mesh','source':entry['path'],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_triangles':total,'derived_triangles':tris,'removed_faces_area_le_1e_12':removed,'uniform_fit':scale,'bounds_m':bounds,'normal_policy':'recomputed from geometry after normalization, original smooth flags retained'})
 (evidence/'asset-fit.json').write_text(json.dumps(report,indent=2));return report
