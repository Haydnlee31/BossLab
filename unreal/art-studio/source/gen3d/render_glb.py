"""Render turntable review stills of a generated GLB.

blender -b -P render_glb.py -- <model.glb> <out_dir> [size]
Writes front/threequarter/side/back PNGs, a mesh summary JSON, and a
contact sheet input list. The model is scaled to 1.8 m tall, feet on Z=0.
"""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
glb, out = Path(argv[0]), Path(argv[1])
size = int(argv[2]) if len(argv) > 2 else 900
out.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']

def bounds():
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

roots = [o for o in bpy.context.scene.objects if o.parent is None]
lo, hi = bounds()
scale = 1.8 / (hi.z - lo.z)
for r in roots:
    r.scale *= scale
bpy.context.view_layer.update()
lo, hi = bounds()
center = (lo + hi) / 2
for r in roots:
    r.location -= Vector((center.x, center.y, lo.z))
bpy.context.view_layer.update()
lo, hi = bounds()

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = int(size * 0.75)
scene.render.resolution_y = size
scene.render.film_transparent = False
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - Medium High Contrast'
world = bpy.data.worlds.new('w'); scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.13, 0.13, 0.14, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.2

def light(name, rot, energy, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'SUN'); d.energy = energy; d.color = color
    o = bpy.data.objects.new(name, d); o.rotation_euler = [math.radians(a) for a in rot]
    scene.collection.objects.link(o)
light('key', (50, 0, -35), 6.0, (1, 0.96, 0.9))
light('fill', (60, 0, 140), 2.0, (0.8, 0.85, 1))
light('rim', (70, 0, 180), 2.0)

bpy.ops.mesh.primitive_cylinder_add(radius=1.4, depth=0.05, location=(0, 0, -0.025))
floor = bpy.context.object
m = bpy.data.materials.new('floor'); m.use_nodes = True
m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1)
floor.data.materials.append(m)

cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.lens = 70
scene.collection.objects.link(cam); scene.camera = cam
target = Vector((0, 0, (hi.z - lo.z) * 0.5))
dist = 4.4
views = {'front': -90, 'threequarter': -55, 'side': 0, 'back': 90}
for name, az in views.items():
    a = math.radians(az)
    cam.location = target + Vector((math.cos(a) * dist, math.sin(a) * dist, 0.3))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = str(out / f'{name}.png')
    bpy.ops.render.render(write_still=True)

tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
imgs = [{'name': i.name, 'size': list(i.size)} for i in bpy.data.images if i.size[0]]
json.dump({'glb': str(glb), 'objects': len(meshes), 'triangles': tris,
           'vertices': sum(len(o.data.vertices) for o in meshes), 'images': imgs,
           'materials': [s.material.name for o in meshes for s in o.material_slots if s.material],
           'height_m_after_normalize': round(hi.z - lo.z, 4)},
          open(out / 'mesh-summary.json', 'w'), indent=1)
