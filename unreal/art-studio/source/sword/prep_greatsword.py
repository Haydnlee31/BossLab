"""Model the player's enchanted greatsword from the approved concept
(artifacts/art/claude-revamp-2026-11-09/inputs/greatsword-input.png) in project-local Blender.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/sword/prep_greatsword.py -- artifacts/art/overnight-2026-11-10/sword
Frame matches the game's sword root (WardenSword.cpp): the right-hand grip point is the
origin, the blade runs up +Z, guard at 8 cm, point at 148 cm (the engine's reach), the
two-handed grip down to -30 cm. Blender metres; Unreal imports at 100x.
Parts and material slots: sword_steel (blade), sword_iron (guard, ring, langet),
sword_leather (grip + spiral wrap), sword_bronze (ferrules, pommel), sword_rune (six
glyphs inlaid in the fuller - the enchanted glow). Writes SM_Greatsword.fbx, a preview
render and pieces.json.
"""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector

OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
CM = .01
mats = {}
def mat(name, colour, metal, rough, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*colour, 1); b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 6
    mats[name] = m
    return m
mat('sword_steel', (.16, .16, .17), .9, .42)
mat('sword_iron', (.09, .09, .1), .85, .5)
mat('sword_leather', (.13, .055, .03), 0, .72)
mat('sword_bronze', (.42, .3, .14), .95, .38)
mat('sword_rune', (1, .55, .15), 0, .4, emit=(1, .5, .12))

def finish(obj, material):
    obj.data.materials.append(mats[material])
    return obj

# --- Blade: flattened diamond section with a fuller, tapering to a point -------------
def blade():
    bm = bmesh.new()
    rings = []
    base, length = 9.5, 138.5          # cm, from just above the guard to the point
    steps = 60
    for i in range(steps + 1):
        u = i / steps
        z = base + length * u
        # Width: 7 cm at the base, a gentle taper to 4.4 cm, then the point (last 16%).
        w = 7.0 - 2.6 * u
        if u > .84: w *= max(.02, (1 - u) / .16) ** .85
        t = .95 * (w / 7.0) ** .6 + .05     # thickness, cm
        f = min(1.9, w * .32)               # fuller width
        d = .28 * (1 - min(1, max(0, (u - .68) / .08)))   # fuller depth, fades by 76%
        ring = []
        for side in (1, -1):                # front (+y) then back (-y)
            pts = [(-w / 2, 0), (-f / 2, t / 2), (-f * .3, t / 2 - d), (f * .3, t / 2 - d), (f / 2, t / 2), (w / 2, 0)]
            if side < 0: pts = [(x, -y) for x, y in reversed(pts)]
            for x, y in (pts[1:-1] if side > 0 else pts[1:-1]):
                ring.append(bm.verts.new((x * CM, y * CM, z * CM)))
            if side > 0: ring.insert(0, bm.verts.new((-w / 2 * CM, 0, z * CM))); ring.append(bm.verts.new((w / 2 * CM, 0, z * CM)))
        rings.append(ring)
    for a, b in zip(rings, rings[1:]):
        n = len(a)
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    tip = bm.verts.new((0, 0, (base + length + .3) * CM))
    last = rings[-1]
    for k in range(len(last)): bm.faces.new((last[k], last[(k + 1) % len(last)], tip))
    me = bpy.data.meshes.new('blade'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('blade', me); bpy.context.scene.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = False
    return finish(o, 'sword_steel')

def tube(name, points, radius, material, closed=False):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(points) - 1)
    for p, c in zip(sp.points, points): p.co = (*c, 1)
    sp.use_cyclic_u = closed
    cu.bevel_depth = radius; cu.bevel_resolution = 3; cu.use_fill_caps = True
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.convert(target='MESH'); o.select_set(False)
    return finish(bpy.context.view_layer.objects.active, material)

def prim(op, name, material, **kw):
    getattr(bpy.ops.mesh, op)(**kw)
    o = bpy.context.active_object; o.name = name
    bpy.ops.object.shade_smooth()
    return finish(o, material)

parts = [blade()]
# Guard: a crossbar whose quillons curve toward the grip, ball finials, a centre langet
# pointing up the blade, and the half-ring around the grip seen in the concept.
quillon = [((x * 17) * CM, 0, (8 - 4.5 * (abs(x) ** 2.4)) * CM) for x in [i / 16 - 1 for i in range(33)]]
parts.append(tube('guard', quillon, 1.05 * CM, 'sword_iron'))
for s in (1, -1):
    parts.append(prim('primitive_uv_sphere_add', 'finial', 'sword_iron', radius=1.5 * CM, location=(s * 17 * CM, 0, 3.6 * CM), segments=16, ring_count=10))
ring = [(math.cos(a) * 5.2 * CM, 0, (8 + math.sin(a) * 5.2) * CM) for a in [math.pi * i / 24 for i in range(25)]]
parts.append(tube('ring', ring, .42 * CM, 'sword_iron'))
bm = bmesh.new()
for v in [(0, .9, 8), (2.1, 0, 9.4), (0, -.9, 8), (-2.1, 0, 9.4), (0, 0, 15.5), (0, 0, 7)]:
    bm.verts.new((v[0] * CM, v[1] * CM, v[2] * CM))
bm.verts.ensure_lookup_table(); V = bm.verts
for f in [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (1, 0, 5), (2, 1, 5), (3, 2, 5), (0, 3, 5)]: bm.faces.new([V[i] for i in f])
me = bpy.data.meshes.new('langet'); bm.to_mesh(me); bm.free()
lo = bpy.data.objects.new('langet', me); bpy.context.scene.collection.objects.link(lo); parts.append(finish(lo, 'sword_iron'))
# Grip: leather core with a raised spiral wrap, bronze ferrules, a faceted bronze pommel.
parts.append(prim('primitive_cylinder_add', 'grip', 'sword_leather', radius=1.55 * CM, depth=36 * CM, location=(0, 0, -12 * CM), vertices=16))
helix = [(math.cos(a) * 1.65 * CM, math.sin(a) * 1.65 * CM, (-29.5 + 35 * a / (2 * math.pi * 9)) * CM) for a in [2 * math.pi * 9 * i / 360 for i in range(361)]]
parts.append(tube('wrap', helix, .32 * CM, 'sword_leather'))
for z in (5.5, -30):
    parts.append(prim('primitive_cylinder_add', 'ferrule', 'sword_bronze', radius=1.95 * CM, depth=1.6 * CM, location=(0, 0, z * CM), vertices=16))
parts.append(prim('primitive_cylinder_add', 'pommel', 'sword_bronze', radius=2.7 * CM, depth=4.2 * CM, location=(0, 0, -33.6 * CM), vertices=8))
parts.append(prim('primitive_cone_add', 'pommelcap', 'sword_bronze', radius1=2.7 * CM, radius2=.8 * CM, depth=2.2 * CM, location=(0, 0, -36.8 * CM), rotation=(math.pi, 0, 0), vertices=8))
# Runes: six small bracket glyphs inlaid on both faces of the fuller, slightly proud so
# they catch the eye; they glow (the enchantment).
for k in range(6):
    z = 40 + k * 10.5
    for side in (1, -1):
        y = side * (.26 * .5 + .06) * CM
        for dz, sx, sz in ((0, .55, 2.6), (1.25, 1.1, .32), (-1.25, 1.1, .32)):
            parts.append(prim('primitive_cube_add', 'rune', 'sword_rune', size=1, location=(0, y, (z + dz) * CM), scale=(sx * CM, .12 * CM, sz * CM)))

for p in parts: p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
sword = bpy.context.active_object; sword.name = 'SM_Greatsword'
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, 'SM_Greatsword.fbx'), use_selection=True, apply_unit_scale=True,
                         apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE', add_leaf_bones=False)
tris = sum(len(p.vertices) - 2 for p in sword.data.polygons)
dims = [round(v * 100, 1) for v in sword.dimensions]
# Preview: lying diagonally, lit, Eevee.
sword.rotation_euler = (0, math.radians(-90), math.radians(20))
bpy.ops.object.camera_add(location=(.2, -1.9, .35)); cam = bpy.context.active_object
cam.rotation_euler = (Vector((.2, 0, .1)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = 50
bpy.context.scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=(.6, -1, 1.2)); bpy.context.active_object.data.energy = 300
bpy.ops.object.light_add(type='AREA', location=(-1, -.4, .3)); bpy.context.active_object.data.energy = 120
world = bpy.data.worlds.new('w'); world.use_nodes = True; world.node_tree.nodes['Background'].inputs[0].default_value = (.02, .02, .025, 1)
bpy.context.scene.world = world
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 1400, 600
sc.render.filepath = os.path.join(OUT, 'greatsword-preview.png')
bpy.ops.render.render(write_still=True)
json.dump({'triangles': tris, 'size_cm': dims, 'materials': [m.name for m in sword.data.materials]}, open(os.path.join(OUT, 'pieces.json'), 'w'), indent=1)
print('BOSSLAB greatsword', tris, dims)
