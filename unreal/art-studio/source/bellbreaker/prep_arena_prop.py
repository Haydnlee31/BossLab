"""Prepare a TRELLIS-generated forge arena prop for the Bellbreaker fight (2026-11-23 readiness pass).

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/bellbreaker/prep_arena_prop.py -- <model.glb> <out_dir> <name> <height_m> [triangles]
Joins the generated parts, decimates to `triangles` (default 12000: the raw output is ~300k, too heavy for
set dressing), puts the pivot at the bottom centre (stands on the floor), scales the height, saves the
textures as real PNGs (Unreal rejects the glTF's embedded WebP), exports <name>.fbx and a preview.
"""
import bpy, json, os, sys
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
GLB, OUT, NAME, HEIGHT = os.path.abspath(args[0]), os.path.abspath(args[1]), args[2], float(args[3])
TRIS = int(args[4]) if len(args) > 4 else 12000
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects: o.select_set(False)
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
prop = bpy.context.active_object
for o in list(bpy.context.scene.objects):
    if o != prop and o.type != 'MESH': bpy.data.objects.remove(o)
prop.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
before = sum(len(p.vertices) - 2 for p in prop.data.polygons)
m = prop.modifiers.new('decimate', 'DECIMATE'); m.ratio = min(1.0, TRIS / max(1, before))
bpy.ops.object.modifier_apply(modifier=m.name)
vs = [v.co for v in prop.data.vertices]
lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
base = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
scale = HEIGHT / (hi.z - lo.z)
for v in prop.data.vertices: v.co = (v.co - base) * scale
prop.name = NAME
textures = []
for slot in prop.data.materials:
    if slot and slot.use_nodes:
        for n in slot.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                path = os.path.join(OUT, f'T_{NAME[3:]}_{len(textures)}.png')
                src = n.image; w, h = src.size
                png = bpy.data.images.new(f'png_{len(textures)}', w, h, alpha=True)
                png.colorspace_settings.name = src.colorspace_settings.name
                png.pixels = src.pixels[:]
                png.filepath_raw = path; png.file_format = 'PNG'; png.save()
                textures.append({'material': slot.name, 'node': n.label or n.name, 'path': path})
bpy.ops.object.select_all(action='DESELECT'); prop.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, NAME + '.fbx'), use_selection=True, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='STRIP')
after = sum(len(p.vertices) - 2 for p in prop.data.polygons)
size = [round((hi[i] - lo[i]) * scale, 3) for i in range(3)]
bpy.ops.object.light_add(type='SUN', location=(1, -1, 2)); bpy.context.active_object.data.energy = 4
world = bpy.data.worlds.new('w'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (.3, .3, .32, 1)
bpy.context.scene.world = world
bpy.ops.object.camera_add(); cam = bpy.context.active_object; bpy.context.scene.camera = cam
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x = 512; sc.render.resolution_y = 512
mid = Vector((0, 0, HEIGHT / 2)); r = max(size) * 1.6
cam.location = mid + Vector((r * .7, -r * .7, r * .35)); cam.rotation_euler = (mid - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.filepath = os.path.join(OUT, NAME + '-preview.png'); bpy.ops.render.render(write_still=True)
json.dump({'source': GLB, 'triangles_source': before, 'triangles': after, 'height_m': HEIGHT, 'size_m': size, 'textures': textures},
          open(os.path.join(OUT, NAME + '.json'), 'w'), indent=1)
print('BOSSLAB arena prop', NAME, before, after, size)
