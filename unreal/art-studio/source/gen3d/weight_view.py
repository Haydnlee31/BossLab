"""Render a rigged .blend coloured by each vertex's dominant bone family.

blender -b -P weight_view.py -- <rig.blend> <out_prefix>   (writes -front/-side/-back PNGs)
magenta = cape/robe swing chains, red = arms/hands, green = legs/feet, blue = spine/neck/clavicles, yellow = pelvis, white = head.
"""
import bpy, math, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.open_mainfile(filepath=argv[0])
scene = bpy.context.scene
mesh = next(o for o in scene.objects if o.type == 'MESH')
names = {g.index: g.name for g in mesh.vertex_groups}

def family(n):
    if n.startswith('cape_'):
        return (.8, .2, 1)
    if n.startswith(('upperarm', 'lowerarm', 'hand')) or n.split('_')[0] in ('index', 'middle', 'ring', 'pinky', 'thumb'):
        return (1, .1, .1)
    if n.startswith(('thigh', 'calf', 'foot', 'ball')):
        return (.1, 1, .2)
    if n == 'pelvis':
        return (1, .9, .1)
    if n.startswith('head'):
        return (1, 1, 1)
    return (.2, .4, 1)

col = mesh.data.color_attributes.new('dominant', 'FLOAT_COLOR', 'POINT')
for v in mesh.data.vertices:
    g = max(v.groups, key=lambda g: g.weight, default=None)
    col.data[v.index].color = (*family(names[g.group]), 1) if g else (0, 0, 0, 1)
mat = bpy.data.materials.new('weights'); mat.use_nodes = True
nt = mat.node_tree; nt.nodes.clear()
attr = nt.nodes.new('ShaderNodeVertexColor'); attr.layer_name = 'dominant'
emit = nt.nodes.new('ShaderNodeEmission'); out = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(attr.outputs['Color'], emit.inputs['Color']); nt.links.new(emit.outputs[0], out.inputs[0])
mesh.data.materials.clear(); mesh.data.materials.append(mat)

scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x, scene.render.resolution_y = 500, 700
scene.view_settings.view_transform = 'Standard'
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.1
scene.collection.objects.link(cam); scene.camera = cam
for name, az in (('front', -90), ('side', 0), ('back', 90)):
    a = math.radians(az)
    cam.location = Vector((math.cos(a) * 5, math.sin(a) * 5, 0.95))
    cam.rotation_euler = (Vector((0, 0, 0.95)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = f'{argv[1]}-{name}.png'
    bpy.ops.render.render(write_still=True)
