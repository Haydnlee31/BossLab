"""Hearth A2 concept-detail kit (2026-11-17): procedural flagstone floor, hanging chains, timber
gallery frames and banners, laid out on the measured A2 plan.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/hearth_a2_kit/build_kit.py -- <out_dir>
Writes SM_Kit_Floor/Chains/Timber/Banners.fbx and kit.json (lantern placements) into out_dir.

Authoring is in Unreal centimetres; B() converts once to Blender metres (Unreal y = -Blender y,
the convention prep_arena_gen.py/FBX import uses, verified on SM_A2_hotmetal's bounds). Material
slot names are the Unreal material names; ue_import_kit.py binds them. Deterministic (seeded).

Plan (Unreal cm): side walls' inner faces x = +-1080, entry wall y = -1370, rear wall y ~ 1200
with the furnace (x 21..820) and bellows (x -500..-160) alcoves, window bay diagonal in the
right-rear corner. The walkable field is x +-800, y +-900; everything here is NoCollision art.
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Matrix, Vector

OUT = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
rng = random.Random(1117)

def B(x, y, z):
    return Vector((x / 100, -y / 100, z / 100))

MATS = {}
def mat(name):
    if name not in MATS:
        MATS[name] = bpy.data.materials.new(name)
    return MATS[name]

def new_object(name, bm, slots):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for s in slots:
        me.materials.append(mat(s))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob

def export(ob, name):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + '.fbx'), use_selection=True, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_UNITS', mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='STRIP')
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    return tris

report = {}

# ---------------------------------------------------------------- floor
FLOOR_SLOTS = [f'M_A2_worn_floor_stone_{i}' for i in range(6)] + ['M_A2_deep_charcoal_mortar']
bm = bmesh.new()
uv = bm.loops.layers.uv.new('UVMap')

def skip(x, y):
    if y < -1395: return True
    if x > 1105 and y < 1150: return True
    if x < -1105 and y < 600: return True
    return False

def slab(poly, matid):
    """poly: plan corners (Unreal cm, CCW seen from above). Builds a closed bevelled stone."""
    n = len(poly)
    cx = sum(p[0] for p in poly) / n; cy = sum(p[1] for p in poly) / n
    top = rng.uniform(-.45, .25)
    tx, ty = rng.uniform(-.004, .004), rng.uniform(-.004, .004)   # tilt (cm per cm)
    bevel = rng.uniform(1.0, 1.8)
    wear = rng.uniform(.1, .45)
    def h(x, y): return top + (x - cx) * tx + (y - cy) * ty
    inner = []
    for (x, y) in poly:
        dx, dy = cx - x, cy - y; L = math.hypot(dx, dy) or 1
        inner.append((x + dx / L * bevel, y + dy / L * bevel))
    vt = [bm.verts.new(B(x, y, h(x, y))) for (x, y) in inner]
    vr = [bm.verts.new(B(x, y, h(x, y) - .9)) for (x, y) in poly]
    vb = [bm.verts.new(B(x, y, -3)) for (x, y) in poly]
    vc = bm.verts.new(B(cx, cy, h(cx, cy) - wear))
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((vc, vt[i], vt[j])))
        faces.append(bm.faces.new((vt[i], vr[i], vr[j], vt[j])))
        faces.append(bm.faces.new((vr[i], vb[i], vb[j], vr[j])))
    # (no bottom: never seen, the mortar bed sits under every gap)
    ou, ov, rot = rng.random(), rng.random(), rng.randint(0, 3)
    for f in faces:
        f.material_index = matid
        for loop in f.loops:
            p = loop.vert.co
            u, v = p.x * 100 / 160, p.y * 100 / 160
            for _ in range(rot): u, v = -v, u
            loop[uv].uv = (u + ou, v + ov)
    return faces

X0, X1, Y0, Y1 = -1520, 1250, -1400, 2040
gap = 1.5
y = Y0
slabs = 0
while y < Y1:
    row = rng.uniform(32, 54)
    x = X0 + rng.uniform(-40, 0)
    wav = rng.uniform(-3, 3)
    while x < X1:
        L = rng.uniform(42, 98)
        if rng.random() < .08: L *= 1.6
        x0, x1 = x + gap / 2, x + L - gap / 2
        ya, yb = y + gap / 2 + wav, y + row - gap / 2 + wav
        cx, cy = (x0 + x1) / 2, (ya + yb) / 2
        if not skip(cx, cy):
            j = lambda: rng.uniform(-2.2, 2.2)
            quad = [(x0 + j(), ya + j()), (x1 + j(), ya + j()), (x1 + j(), yb + j()), (x0 + j(), yb + j())]
            m = rng.randrange(6)
            if rng.random() < .07:   # a cracked stone: two pieces with a jagged gap
                t1, t2 = rng.uniform(.3, .7), rng.uniform(.3, .7)
                a = (quad[0][0] + (quad[1][0] - quad[0][0]) * t1, quad[0][1] + (quad[1][1] - quad[0][1]) * t1)
                b = (quad[3][0] + (quad[2][0] - quad[3][0]) * t2, quad[3][1] + (quad[2][1] - quad[3][1]) * t2)
                slab([quad[0], (a[0] - .8, a[1]), (b[0] - .8, b[1]), quad[3]], m)
                slab([(a[0] + .8, a[1]), quad[1], quad[2], (b[0] + .8, b[1])], m)
                slabs += 2
            elif rng.random() < .18:  # a chipped corner
                k = rng.randrange(4); p, q, r = quad[k - 1], quad[k], quad[(k + 1) % 4]
                c1 = (q[0] + (p[0] - q[0]) * .18, q[1] + (p[1] - q[1]) * .18)
                c2 = (q[0] + (r[0] - q[0]) * .18, q[1] + (r[1] - q[1]) * .18)
                slab(quad[:k] + [c1, c2] + quad[k + 1:], m); slabs += 1
            else:
                slab(quad, m); slabs += 1
        x += L
    y += row
# Mortar bed under the gaps.
bed = [bm.verts.new(B(x, y, -1.6)) for (x, y) in ((X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1))]
f = bm.faces.new(bed); f.material_index = 6
for loop in f.loops:
    loop[uv].uv = (loop.vert.co.x / 2, loop.vert.co.y / 2)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
for f in bm.faces:
    if f.normal.z < -.5 and f.material_index == 6: f.normal_flip()
ob = new_object('SM_Kit_Floor', bm, FLOOR_SLOTS)
report['SM_Kit_Floor'] = {'stones': slabs, 'triangles': export(ob, 'SM_Kit_Floor')}

# ---------------------------------------------------------------- chains
bm = bmesh.new()
def torus(center, axis_rot, R, r, seg=6, ring=4):
    """A link: torus in its local XZ plane, rotated by axis_rot (Matrix) and moved to center (Blender m)."""
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for k in range(ring):
            b = 2 * math.pi * k / ring
            p = Vector(((R + r * math.cos(b)) * math.cos(a), r * math.sin(b), (R + r * math.cos(b)) * math.sin(a) * 1.5))
            row.append(bm.verts.new(center + axis_rot @ p))
        verts.append(row)
    for i in range(seg):
        for k in range(ring):
            bm.faces.new((verts[i][k], verts[(i + 1) % seg][k], verts[(i + 1) % seg][(k + 1) % ring], verts[i][(k + 1) % ring]))

lanterns = []
CHAINS = [  # x, y, top z, bottom z, end
    (930, -120, 1150, 520, 'lantern'), (930, 780, 1150, 600, 'hook'), (-930, -320, 1150, 500, 'lantern'),
    (-930, 300, 1150, 620, 'hook'), (320, 520, 1180, 640, 'hook'), (-260, -260, 1180, 660, 'ring'),
    (560, -250, 1180, 430, 'hook'), (40, 980, 1150, 560, 'lantern'), (-600, 760, 1150, 600, 'ring'),
    (700, -1150, 1150, 560, 'hook'), (-700, -1150, 1150, 520, 'lantern')]
# Each chain starts at the vault's underside (measured from the A2 vault mesh, chain_ceiling.json)
# and hangs from a riveted iron anchor plate with an eye bolt; plate/eye are added below.
ceil = json.load(open(os.path.join(OUT, 'chain_ceiling.json'))) if os.path.exists(os.path.join(OUT, 'chain_ceiling.json')) else {}
anchors = []
for (x, y, zt, zb, end) in CHAINS:
    zt = ceil.get(f'{x},{y}') or zt
    zb = min(zb, zt - 110)   # at least ~1 m of chain under a low vault
    anchors.append((x, y, zt))
    z = zt - 10; k = 0; tw = rng.uniform(0, math.pi)
    while z > zb:
        rot = Matrix.Rotation(tw + (math.pi / 2 if k % 2 else 0), 3, 'Z')
        torus(B(x, y, z), rot, .03, .009)
        z -= 7.2; k += 1
    if end == 'hook':
        rot = Matrix.Rotation(tw, 3, 'Z')
        for s in range(5):   # a heavy J hook from short curved segments
            a = math.pi * (1.1 + s * .22)
            torus(B(x, y, z - 9) + rot @ Vector((math.cos(a) * .09, 0, math.sin(a) * .09)), rot @ Matrix.Rotation(a, 3, 'Y'), .035, .016)
    elif end == 'ring':
        torus(B(x, y, z - 16), Matrix.Rotation(tw, 3, 'Z'), .11, .018, seg=12)
    else:
        lanterns.append([x, y, z - 4])
for f in bm.faces: f.smooth = True
for (x, y, zt) in anchors:
    plate = bmesh.ops.create_cube(bm, size=1.0)['verts']
    bmesh.ops.transform(bm, matrix=Matrix.Translation(B(x, y, zt - 2)) @ Matrix.Diagonal((.26, .26, .04, 1)), verts=plate)
    for dx, dy in ((-9, -9), (9, -9), (-9, 9), (9, 9)):          # rivet heads
        r = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.transform(bm, matrix=Matrix.Translation(B(x + dx, y + dy, zt - 4.5)) @ Matrix.Diagonal((.03, .03, .015, 1)), verts=r)
    torus(B(x, y, zt - 8), Matrix.Identity(3), .035, .012, seg=8)  # eye bolt
ob = new_object('SM_Kit_Chains', bm, ['M_A2_forged_iron'])
report['SM_Kit_Chains'] = {'chains': len(CHAINS), 'triangles': export(ob, 'SM_Kit_Chains')}

# ---------------------------------------------------------------- timber gallery frames
bm = bmesh.new()
uvt = bm.loops.layers.uv.new('UVMap')
def box(c, size, matid, yaw=0.0, tilt=None):
    """Axis box centred at c (Unreal cm), size (cm); yaw (deg, Unreal) about Z; optional tilt Matrix."""
    res = bmesh.ops.create_cube(bm, size=1.0)
    vs = res['verts']
    M = Matrix.Diagonal((size[0] / 100, size[1] / 100, size[2] / 100, 1))
    R = Matrix.Rotation(math.radians(-yaw), 4, 'Z')
    if tilt is not None: R = R @ tilt
    bmesh.ops.transform(bm, matrix=Matrix.Translation(B(*c)) @ R @ M, verts=vs)
    faces = list({f for v in vs for f in v.link_faces})
    for f in faces:
        f.material_index = matid
        n = f.normal
        for loop in f.loops:
            p = loop.vert.co
            loop[uvt].uv = ((p.x + p.y) * .6, p.z * .6) if abs(n.z) < .7 else (p.x * .6, p.y * .6)
    return faces

def post(x, y, h=640):
    box((x, y, 14), (54, 54, 28), 2)                               # stone plinth
    box((x, y, 28 + h / 2), (34, 34, h), 0)                        # oak post
    for zb in (70, h * .55, h - 30):
        box((x, y, 28 + zb), (37, 37, 9), 1)                       # iron bands
    box((x, y, 28 + h + 10), (44, 44, 20), 0)                      # cap block

def beam(x, y0, y1, z):
    box((x, (y0 + y1) / 2, z), (32, abs(y1 - y0), 36), 0)
    n = int(abs(y1 - y0) // 150)
    for i in range(n + 1):                                         # iron straps along the beam
        box((x, y0 + (y1 - y0) * i / max(1, n), z), (35, 6, 39), 1)

def brace(x, y, z0, dy, run=95):
    a = math.atan2(run, run)
    L = math.hypot(run, run)
    tilt = Matrix.Rotation(a * dy, 4, 'X')   # leans from the post up toward the beam (Unreal +y = Blender -y)
    box((x, y + dy * run / 2, z0 + run / 2), (22, 22, L), 0, tilt=tilt)

for side, ys in ((1, (-1250, -470, 330, 1060)), (-1, (-1250, -650, 110))):
    x = 958 * side
    for y in ys:
        post(x, y)
        for dy in (-1, 1):
            if (dy < 0 and y == ys[0]) or (dy > 0 and y == ys[-1]): continue
            brace(x, y, 28 + 640 - 120, dy)
    beam(x, ys[0] - 60, ys[-1] + 60, 28 + 640 + 38)
# A heavy tie beam across the entry bay, high, with a hanging hoist block.
box((0, -1150, 690), (2160, 36, 40), 0)
for xx in (-700, -300, 300, 700): box((xx, -1150, 690), (8, 39, 43), 1)
ob = new_object('SM_Kit_Timber', bm, ['M_A2_aged_oak', 'M_A2_forged_iron', 'M_A2_cut_stone_value_2'])
report['SM_Kit_Timber'] = {'triangles': export(ob, 'SM_Kit_Timber')}

# ---------------------------------------------------------------- banners
bm = bmesh.new()
uvb = bm.loops.layers.uv.new('UVMap')
def banner(x, y, z_top, yaw, w=120, h=250):
    """Folded cloth on an iron rod; front faces along yaw (Unreal deg)."""
    nu, nv = 10, 22
    fwd = Vector((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0))
    right = Vector((-fwd.y, fwd.x, 0))
    ph = rng.uniform(0, 6.28)
    grid = []
    for j in range(nv + 1):
        v = j / nv
        row = []
        for i in range(nu + 1):
            u = i / nu
            fold = 4.5 * math.sin(u * 2 * math.pi * 2.5 + ph) * (.4 + .6 * v) + 2.5 * v * v
            sag = -3 * math.sin(u * math.pi) * (1 - v)
            p = Vector((x, y, z_top)) + right * ((u - .5) * w * (1 - .06 * v)) + fwd * fold + Vector((0, 0, -v * h + sag))
            row.append(bm.verts.new(B(p.x, p.y, p.z)))
        grid.append(row)
    for j in range(nv):
        for i in range(nu):
            f = bm.faces.new((grid[j][i], grid[j + 1][i], grid[j + 1][i + 1], grid[j][i + 1]))
            f.material_index = 0; f.smooth = True
            for loop, (uu, vv) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))):
                loop[uvb].uv = (uu / nu, 1 - vv / nv)
    # rod and finials
    rod = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.018, radius2=.018, depth=(w + 30) / 100)
    rv = rod['verts']
    bmesh.ops.transform(bm, matrix=Matrix.Translation(B(x, y, z_top + 3)) @ Matrix.Rotation(math.radians(-yaw), 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'X'), verts=rv)
    for fc in {f for v in rv for f in v.link_faces}: fc.material_index = 1; fc.smooth = True

# In front of the wall rails (the upper walls stand proud of the plan's 0.4-2.2 m slice).
for (x, y, z, yaw) in ((985, -760, 470, 180), (985, 640, 480, 180), (-985, -820, 470, 0), (-985, 430, 480, 0),
                       (-560, -1290, 470, 90), (560, -1290, 470, 90)):
    banner(x, y, z, yaw)
ob = new_object('SM_Kit_Banners', bm, ['M_Kit_Banner', 'M_A2_forged_iron'])
report['SM_Kit_Banners'] = {'triangles': export(ob, 'SM_Kit_Banners')}

json.dump({'report': report, 'lanterns_cm': lanterns}, open(os.path.join(OUT, 'kit.json'), 'w'), indent=1)
print('BOSSLAB kit', json.dumps(report))
