"""Prepare the TRELLIS-generated Regent estoc for the game.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/regent/prep_estoc_trellis.py -- <model.glb> <out_dir> [length_m] [guard_axis]
Joins the generated parts, decimates to ~16k triangles (smooth shaded), finds the blade's long axis and
stands it on +Z with the pommel at the origin (the same convention as the interim CC0
SM_Estoc: pommel at origin, point up), scales the overall length to length_m (default
1.49 m, the interim estoc's length), turns the crossguard onto guard_axis (X or Y, default
X, as SM_Estoc's 37 cm guard) and reports the guard height so the game can seat the grip in the hand. The pommel end is
the end nearer the widest slice (the crossguard). Saves textures as real PNGs (Unreal rejects
the glTF's embedded WebP), exports SM_RegentEstocGen.fbx and renders previews.
"""
import bpy, json, math, os, sys
from mathutils import Matrix, Vector

args = sys.argv[sys.argv.index('--') + 1:]
GLB, OUT = os.path.abspath(args[0]), os.path.abspath(args[1])
LENGTH = float(args[2]) if len(args) > 2 else 1.49
GUARD_AXIS = (args[3] if len(args) > 3 else 'X').upper()
TARGET = 16000
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects: o.select_set(False)
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
sword = bpy.context.active_object
for o in list(bpy.context.scene.objects):
    if o != sword and o.type != 'MESH': bpy.data.objects.remove(o)
sword.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
before = sum(len(p.vertices) - 2 for p in sword.data.polygons)
m = sword.modifiers.new('decimate', 'DECIMATE'); m.ratio = min(1.0, TARGET / max(1, before))
bpy.ops.object.modifier_apply(modifier=m.name)
for p in sword.data.polygons: p.use_smooth = True

# Principal axes: the long axis is the blade; of the two others, the wider spread is the guard.
vs = [v.co.copy() for v in sword.data.vertices]
c = sum(vs, Vector()) / len(vs)
cov = [[sum((v[i] - c[i]) * (v[j] - c[j]) for v in vs) / len(vs) for j in range(3)] for i in range(3)]
def power(M, x, n=60):
    for _ in range(n):
        y = Vector([sum(M[i][j] * x[j] for j in range(3)) for i in range(3)])
        x = y.normalized()
    return x
long_axis = power(cov, Vector((.3, .5, .8)))
lam = long_axis.dot(Vector([sum(cov[i][j] * long_axis[j] for j in range(3)) for i in range(3)]))
deflated = [[cov[i][j] - lam * long_axis[i] * long_axis[j] for j in range(3)] for i in range(3)]
wide_axis = power(deflated, Vector((.7, -.2, .4)))
wide_axis = (wide_axis - long_axis * wide_axis.dot(long_axis)).normalized()
proj = [(v - c).dot(long_axis) for v in vs]
lo, hi = min(proj), max(proj)
# Widest slice (crossguard) along the long axis decides which end is the pommel.
BINS = 60
width = [0.0] * BINS
for v, p in zip(vs, proj):
    b = min(BINS - 1, int((p - lo) / (hi - lo) * BINS))
    width[b] = max(width[b], abs((v - c).dot(wide_axis)))
guard_bin = max(range(BINS), key=lambda b: width[b])
if guard_bin > BINS / 2:   # guard nearer the high end: flip so the pommel is the low end
    long_axis = -long_axis; proj = [-p for p in proj]; lo, hi = -hi, -lo; guard_bin = BINS - 1 - guard_bin
side = long_axis.cross(wide_axis).normalized()
# Rotation taking (wide, side, long) -> (guard axis, other, +Z).
target_wide = Vector((0, 1, 0)) if GUARD_AXIS == 'Y' else Vector((1, 0, 0))
target_side = Vector((0, 0, 1)).cross(target_wide)  # keeps the frame right-handed (no mirroring)
R = Matrix((target_wide, target_side, Vector((0, 0, 1)))).transposed() @ Matrix((wide_axis, side, long_axis))
scale = LENGTH / (hi - lo)
base = c + long_axis * lo
for v in sword.data.vertices: v.co = (R @ (v.co - base)) * scale
guard_m = (guard_bin + .5) / BINS * LENGTH
sword.name = 'SM_RegentEstocGen'
textures = []
for slot in sword.data.materials:
    if slot and slot.use_nodes:
        for n in slot.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                path = os.path.join(OUT, f'T_RegentEstocGen_{len(textures)}.png')
                src = n.image; w, h = src.size
                png = bpy.data.images.new(f'png_{len(textures)}', w, h, alpha=True)
                png.colorspace_settings.name = src.colorspace_settings.name
                png.pixels = src.pixels[:]
                png.filepath_raw = path; png.file_format = 'PNG'; png.save()
                textures.append({'material': slot.name, 'node': n.label or n.name, 'path': path})
bpy.ops.object.select_all(action='DESELECT'); sword.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, 'SM_RegentEstocGen.fbx'), use_selection=True, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='OFF', add_leaf_bones=False, path_mode='STRIP')
after = sum(len(p.vertices) - 2 for p in sword.data.polygons)
vs = [v.co for v in sword.data.vertices]
size = [round(max(v[i] for v in vs) - min(v[i] for v in vs), 4) for i in range(3)]
bpy.ops.object.light_add(type='SUN', location=(1, -1, 2)); bpy.context.active_object.data.energy = 4
world = bpy.data.worlds.new('w'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (.3, .3, .32, 1)
bpy.context.scene.world = world
bpy.ops.object.camera_add(); cam = bpy.context.active_object; bpy.context.scene.camera = cam
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x = 320; sc.render.resolution_y = 960
mid = Vector((0, 0, LENGTH / 2))
for name, d in (('front', Vector((2.4, 0, 0))), ('edge', Vector((0, 2.4, 0))), ('hilt', Vector((.35, -.35, .1)))):
    at = Vector((0, 0, guard_m)) if name == 'hilt' else mid
    cam.location = at + d; cam.rotation_euler = (at - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 50
    sc.render.filepath = os.path.join(OUT, f'estoc-gen-{name}.png'); bpy.ops.render.render(write_still=True)
json.dump({'triangles_source': before, 'triangles': after, 'length_m': LENGTH, 'guard_m': round(guard_m, 4),
           'guard_axis': GUARD_AXIS, 'size_m': size, 'textures': textures},
          open(os.path.join(OUT, 'estoc-gen.json'), 'w'), indent=1)
print('BOSSLAB estoc gen', before, after, size, 'guard', round(guard_m, 3))
