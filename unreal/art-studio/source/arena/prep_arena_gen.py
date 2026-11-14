"""Prepare a TRELLIS-generated arena prop for the dungeon hall.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/arena/prep_arena_gen.py -- <model.glb> <out_dir> <Name> <height_m> <triangles> [yaw_deg]
Joins the parts, decimates to <triangles> (smooth shaded), turns the prop yaw_deg about Z (the
generator keeps the input's three-quarter view, so the front is corrected per prop), puts the
pivot at the base centre (front toward -Y in Blender, +Y in Unreal, like the Poly Haven props),
scales it to height_m, saves textures as real PNGs, exports SM_<Name>Gen.fbx and renders a
top and a front preview.
"""
import bpy, json, math, os, sys
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index('--') + 1:]
GLB, OUT, NAME = os.path.abspath(args[0]), os.path.abspath(args[1]), args[2]
HEIGHT, TRIS = float(args[3]), int(args[4])
YAW = float(args[5]) if len(args) > 5 else 0.0
STEM = f'{NAME}Gen'
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
for p in prop.data.polygons: p.use_smooth = True
R = Matrix.Rotation(math.radians(YAW), 3, 'Z')
for v in prop.data.vertices: v.co = R @ v.co
vs = [v.co for v in prop.data.vertices]
lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
base = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
scale = HEIGHT / (hi.z - lo.z)
for v in prop.data.vertices: v.co = (v.co - base) * scale
prop.name = f'SM_{STEM}'
textures = []
for slot in prop.data.materials:
    if slot and slot.use_nodes:
        for n in slot.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                path = os.path.join(OUT, f'T_{STEM}_{len(textures)}.png')
                src = n.image; w, h = src.size
                png = bpy.data.images.new(f'png_{len(textures)}', w, h, alpha=True)
                png.colorspace_settings.name = src.colorspace_settings.name
                png.pixels = src.pixels[:]
                png.filepath_raw = path; png.file_format = 'PNG'; png.save()
                textures.append({'material': slot.name, 'node': n.label or n.name, 'path': path})
bpy.ops.object.select_all(action='DESELECT'); prop.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, f'SM_{STEM}.fbx'), use_selection=True, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='OFF', add_leaf_bones=False, path_mode='STRIP')
after = sum(len(p.vertices) - 2 for p in prop.data.polygons)
size = [round((hi[i] - lo[i]) * scale, 3) for i in range(3)]
bpy.ops.object.light_add(type='SUN', location=(1, -1, 2)); bpy.context.active_object.data.energy = 4
world = bpy.data.worlds.new('w'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (.3, .3, .32, 1)
bpy.context.scene.world = world
bpy.ops.object.camera_add(); cam = bpy.context.active_object; bpy.context.scene.camera = cam
cam.data.type = 'ORTHO'; cam.data.ortho_scale = max(size) * 1.25
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x = 384; sc.render.resolution_y = 384
mid = Vector((0, 0, HEIGHT / 2))
# Front view looks from -Y (the prop's intended front) toward +Y.
for name, loc in (('front', mid + Vector((0, -10, 0))), ('top', Vector((0, 0, HEIGHT + 10)))):
    cam.location = loc; cam.rotation_euler = ((Vector((0, 0, 0)) if name == 'top' else mid) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(OUT, f'{STEM}-{name}.png'); bpy.ops.render.render(write_still=True)
json.dump({'name': NAME, 'triangles_source': before, 'triangles': after, 'height_m': HEIGHT, 'yaw_deg': YAW,
           'size_m': size, 'textures': textures}, open(os.path.join(OUT, f'{STEM}.json'), 'w'), indent=1)
print('BOSSLAB arena gen', NAME, before, after, size)
