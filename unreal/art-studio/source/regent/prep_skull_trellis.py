"""Prepare the TRELLIS-generated witness skull for the game.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/regent/prep_skull_trellis.py -- <model.glb> <out_dir> [yaw_degrees]
Joins the generated parts, decimates to ~9k triangles, rotates by yaw so the face looks
down +X (the game's skull facing), centres the pivot on the bounds, scales the longest
side to 22 cm, saves the base-colour texture as PNG and exports SM_RegentSkullGen.fbx.
Renders front and three-quarter previews to check the orientation.
"""
import bpy, json, math, os, sys
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
GLB, OUT = os.path.abspath(args[0]), os.path.abspath(args[1])
YAW = float(args[2]) if len(args) > 2 else 0.0
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
for o in bpy.context.scene.objects: o.select_set(False)
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1: bpy.ops.object.join()
skull = bpy.context.active_object
for o in list(bpy.context.scene.objects):
    if o != skull and o.type != 'MESH': bpy.data.objects.remove(o)
skull.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
before = sum(len(p.vertices) - 2 for p in skull.data.polygons)
m = skull.modifiers.new('decimate', 'DECIMATE'); m.ratio = min(1.0, 9000 / max(1, before))
bpy.ops.object.modifier_apply(modifier=m.name)
# The glTF importer leaves objects in quaternion mode, where rotation_euler is ignored.
skull.rotation_mode = 'XYZ'; skull.rotation_euler = (0, 0, math.radians(YAW))
bpy.ops.object.transform_apply(rotation=True)
vs = [v.co for v in skull.data.vertices]
lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
centre, size = (lo + hi) / 2, max(hi - lo)
for v in skull.data.vertices: v.co = (v.co - centre) * (.22 / size)
skull.name = 'SM_RegentSkullGen'
textures = []
for slot in skull.data.materials:
    if slot and slot.use_nodes:
        for n in slot.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                path = os.path.join(OUT, f'T_RegentSkullGen_{len(textures)}.png')
                # image.save() keeps the glTF's embedded format (WebP), which Unreal rejects;
                # copy the pixels into a fresh PNG image instead (same colour space, no transform).
                src = n.image; w, h = src.size
                png = bpy.data.images.new(f'png_{len(textures)}', w, h, alpha=True)
                png.colorspace_settings.name = src.colorspace_settings.name
                png.pixels = src.pixels[:]
                png.filepath_raw = path; png.file_format = 'PNG'; png.save()
                textures.append({'material': slot.name, 'node': n.label or n.name, 'path': path})
bpy.ops.object.select_all(action='DESELECT'); skull.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, 'SM_RegentSkullGen.fbx'), use_selection=True, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='STRIP')
after = sum(len(p.vertices) - 2 for p in skull.data.polygons)
# Previews: looking back along -X at the face, and a three-quarter view.
bpy.ops.object.light_add(type='SUN', location=(1, -1, 2)); bpy.context.active_object.data.energy = 4
world = bpy.data.worlds.new('w'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (.3, .3, .32, 1)
bpy.context.scene.world = world
bpy.ops.object.camera_add(); cam = bpy.context.active_object; bpy.context.scene.camera = cam
sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'; sc.display.shading.color_type = 'TEXTURE'
sc.render.resolution_x = sc.render.resolution_y = 512
for name, loc in (('front', (.6, 0, .02)), ('three-quarter', (.42, -.42, .1))):
    cam.location = loc; cam.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(OUT, f'skull-gen-{name}.png'); bpy.ops.render.render(write_still=True)
json.dump({'triangles_source': before, 'triangles': after, 'yaw': YAW, 'textures': textures}, open(os.path.join(OUT, 'skull-gen.json'), 'w'), indent=1)
print('BOSSLAB skull gen', before, after, textures)
