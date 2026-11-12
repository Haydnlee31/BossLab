"""Prepare the TRELLIS-generated soul-fire censer for the game.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/regent/prep_censer_trellis.py -- <model.glb> <out_dir> [height_m]
Joins the generated parts, decimates to ~14k triangles, puts the pivot at the top centre
(the hanging point, like SM_RegentCenser, hanging down -Z), scales the height to height_m
(default 0.24 m; the game scales the censer x2.4), saves the textures as real PNGs and
exports SM_RegentCenserGen.fbx. Renders side and three-quarter previews.
"""
import bpy, json, os, sys
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
GLB, OUT = os.path.abspath(args[0]), os.path.abspath(args[1])
HEIGHT = float(args[2]) if len(args) > 2 else .24
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects: o.select_set(False)
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
censer = bpy.context.active_object
for o in list(bpy.context.scene.objects):
    if o != censer and o.type != 'MESH': bpy.data.objects.remove(o)
censer.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
before = sum(len(p.vertices) - 2 for p in censer.data.polygons)
m = censer.modifiers.new('decimate', 'DECIMATE'); m.ratio = min(1.0, 14000 / max(1, before))
bpy.ops.object.modifier_apply(modifier=m.name)
vs = [v.co for v in censer.data.vertices]
lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
top = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z))
scale = HEIGHT / (hi.z - lo.z)
for v in censer.data.vertices: v.co = (v.co - top) * scale
censer.name = 'SM_RegentCenserGen'
textures = []
for slot in censer.data.materials:
    if slot and slot.use_nodes:
        for n in slot.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                # image.save() would keep the glTF's embedded WebP, which Unreal rejects.
                path = os.path.join(OUT, f'T_RegentCenserGen_{len(textures)}.png')
                src = n.image; w, h = src.size
                png = bpy.data.images.new(f'png_{len(textures)}', w, h, alpha=True)
                png.colorspace_settings.name = src.colorspace_settings.name
                png.pixels = src.pixels[:]
                png.filepath_raw = path; png.file_format = 'PNG'; png.save()
                textures.append({'material': slot.name, 'node': n.label or n.name, 'path': path})
bpy.ops.object.select_all(action='DESELECT'); censer.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, 'SM_RegentCenserGen.fbx'), use_selection=True, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='STRIP')
after = sum(len(p.vertices) - 2 for p in censer.data.polygons)
size = [round((hi[i] - lo[i]) * scale, 4) for i in range(3)]
bpy.ops.object.light_add(type='SUN', location=(1, -1, 2)); bpy.context.active_object.data.energy = 4
world = bpy.data.worlds.new('w'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (.3, .3, .32, 1)
bpy.context.scene.world = world
bpy.ops.object.camera_add(); cam = bpy.context.active_object; bpy.context.scene.camera = cam
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x = 384; sc.render.resolution_y = 512
mid = Vector((0, 0, -HEIGHT / 2))
for name, d in (('side', Vector((.75, 0, 0))), ('three-quarter', Vector((.5, -.5, .18)))):
    cam.location = mid + d; cam.rotation_euler = (mid - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(OUT, f'censer-gen-{name}.png'); bpy.ops.render.render(write_still=True)
json.dump({'triangles_source': before, 'triangles': after, 'height_m': HEIGHT, 'size_m': size, 'textures': textures},
          open(os.path.join(OUT, 'censer-gen.json'), 'w'), indent=1)
print('BOSSLAB censer gen', before, after, size)
