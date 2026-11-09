"""Prepare the Funeral Regent greybox props as FBX for Unreal.

Run with the project-local Blender:
  unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
      unreal/art-studio/source/regent/prep_regent_props.py -- artifacts/art/regent-moveset-2026-11-09/props
Writes <props>/fbx/:
  SM_RegentCenser.fbx  CC0 Poly Haven brass_diya_lantern body + hanging ring (its chain dropped);
                       pivot at the top of the ring, hanging down -Z.
  SM_RegentLink.fbx    one oval chain link (the lantern's own chain is flat 0.4 mm rings, too thin
                       at boss scale); pivot at its centre, long axis Z.
  SM_RegentSkull.fbx   interim witness skull built here (blended volumes, voxel remesh, carved
                       sockets/nose/mouth, tooth row); faces +X. Stand-in until a generated skull
                       replaces it; not a reference-quality sculpt.
and pieces.json (sizes/triangles/materials). Blender units are metres; import at 100x.
"""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector

PROPS = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
OUT = os.path.join(PROPS, 'fbx')
os.makedirs(OUT, exist_ok=True)
pieces = {}

def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)

def only(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o

def pivot(o, point):
    for v in o.data.vertices: v.co -= point
    o.location = (0, 0, 0)

def export(o, name):
    only(o); o.name = name
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + '.fbx'), use_selection=True,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='STRIP', embed_textures=False)
    pieces[name] = {'size_m': [round(v, 4) for v in o.dimensions], 'triangles': tris(o),
                    'materials': [m.name for m in o.data.materials if m]}

# --- Censer and chain link from the CC0 lantern -------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(PROPS, 'brass_diya_lantern', 'brass_diya_lantern_1k.gltf'))
objs = {o.name: o for o in bpy.context.scene.objects if o.type == 'MESH'}
for o in objs.values():
    o.parent = None
only(objs['brass_diya_lantern_chain']); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
chain = objs['brass_diya_lantern_chain']
bpy.data.objects.remove(chain)
bpy.ops.mesh.primitive_torus_add(major_radius=.01, minor_radius=.0026, major_segments=20, minor_segments=8, rotation=(math.pi / 2, 0, 0))
link = bpy.context.active_object; link.scale = (1, 1.55, 1)  # local Y is world Z after the 90° turn
bpy.ops.object.transform_apply(rotation=True, scale=True)
link.data.materials.append(bpy.data.materials.new('regent_iron'))
bpy.ops.object.shade_smooth()
export(link, 'SM_RegentLink')
bpy.data.objects.remove(link)

body, ring = objs['brass_diya_lantern'], objs['brass_diya_lantern_connection']
for o in (body, ring): o.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
censer = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
vs = [v.co for v in censer.data.vertices]
top = Vector(((min(v.x for v in vs) + max(v.x for v in vs)) / 2, (min(v.y for v in vs) + max(v.y for v in vs)) / 2, max(v.z for v in vs)))
pivot(censer, top)
export(censer, 'SM_RegentCenser')

# --- Interim witness skull -----------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
def blob(loc, radius, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=48, ring_count=24)
    o = bpy.context.active_object; o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return o
# Human proportions: a rounded cranium with a tapered face block in front of its lower
# half; sockets, nose and mouth are carved into that block's front plane (x ~ 0.105 m).
parts = [blob((-.014, 0, .026), .079, (1.12, .86, .88))]
bpy.ops.mesh.primitive_cube_add(size=1, location=(.055, 0, -.035))
face = bpy.context.active_object; face.scale = (.1, .125, .12)
bpy.ops.object.transform_apply(scale=True)
for v in face.data.vertices:
    if v.co.z < 0: v.co.y *= .72          # jaw narrower than the cheeks
    if v.co.x < 0: v.co.y *= 1.1
sub = face.modifiers.new('round', 'SUBSURF'); sub.levels = 3
only(face); bpy.ops.object.modifier_apply(modifier=sub.name)
parts.append(face)
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
skull = bpy.context.active_object
m = skull.modifiers.new('remesh', 'REMESH'); m.mode = 'VOXEL'; m.voxel_size = .003
bpy.ops.object.modifier_apply(modifier=m.name)
m = skull.modifiers.new('smooth', 'SMOOTH'); m.factor = .5; m.iterations = 4
bpy.ops.object.modifier_apply(modifier=m.name)

def carve(cutter):
    mod = skull.modifiers.new('carve', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cutter; mod.solver = 'EXACT'
    only(skull); bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter)
front = max(v.co.x for v in skull.data.vertices if abs(v.co.y) < .01 and -.03 < v.co.z < -.01)
print('BOSSLAB skull front', front)
for side in (1, -1):
    carve(blob((front - .006, side * .031, -.02), .025, (1.2, 1.0, .9)))   # eye sockets
    carve(blob((.015, side * .082, -.03), .03, (1.5, .5, 1.0)))            # temporal hollows
bpy.ops.mesh.primitive_cone_add(radius1=.014, depth=.04, vertices=3, location=(front - .004, 0, -.046), rotation=(0, math.pi / 2, 0))
cone = bpy.context.active_object; cone.rotation_euler = (math.pi / 2, math.pi / 2, 0)
carve(cone)                                                               # nasal cavity
bpy.ops.mesh.primitive_cube_add(size=1, location=(front, 0, -.068)); bpy.context.active_object.scale = (.03, .07, .004)
bpy.ops.object.transform_apply(scale=True)
carve(bpy.context.active_object)                                          # mouth line
teeth = []
for z in (-.0625, -.0735):
    for i in range(10):
        a = math.radians(-40 + i * 80 / 9)
        r = front - .062
        bpy.ops.mesh.primitive_cube_add(size=1, location=(.06 + math.cos(a) * r - .002, math.sin(a) * r, z))
        t = bpy.context.active_object; t.scale = (.006, .0062, .0095); t.rotation_euler = (0, 0, a)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bv = t.modifiers.new('bevel', 'BEVEL'); bv.width = .0018; bv.segments = 2
        only(t); bpy.ops.object.modifier_apply(modifier=bv.name)
        teeth.append(t)
for t in teeth: t.select_set(True)
skull.select_set(True); bpy.context.view_layer.objects.active = skull
bpy.ops.object.join()
skull = bpy.context.active_object
m = skull.modifiers.new('decimate', 'DECIMATE'); m.ratio = min(1.0, 7000 / max(1, tris(skull)))
bpy.ops.object.modifier_apply(modifier=m.name)
bpy.ops.object.shade_smooth()
mat = bpy.data.materials.new('regent_bone'); skull.data.materials.append(mat)
vs = [v.co for v in skull.data.vertices]
pivot(skull, Vector(((min(v.x for v in vs) + max(v.x for v in vs)) / 2, 0, (min(v.z for v in vs) + max(v.z for v in vs)) / 2)))
export(skull, 'SM_RegentSkull')
# Preview render of the skull for inspection (Workbench, fast, no GPU).
bpy.ops.object.camera_add(location=(.4, -.24, .03)); cam = bpy.context.active_object
direction = Vector((0, 0, 0)) - cam.location; cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
bpy.context.scene.render.resolution_x = bpy.context.scene.render.resolution_y = 512
bpy.context.scene.render.filepath = os.path.join(OUT, 'skull-preview.png')
bpy.ops.render.render(write_still=True)
cam.location = (.45, 0, -.01); cam.rotation_euler = (Vector((0, 0, -.02)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.render.filepath = os.path.join(OUT, 'skull-preview-front.png')
bpy.ops.render.render(write_still=True)

json.dump(pieces, open(os.path.join(OUT, 'pieces.json'), 'w'), indent=1)
print('BOSSLAB regent props', json.dumps(pieces))
