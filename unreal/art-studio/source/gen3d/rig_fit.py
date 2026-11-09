"""Fit a generated character GLB to the Unreal mannequin skeleton and skin it.

blender -b -P rig_fit.py -- <fit.json>

fit.json keys:
  glb, manny_fbx, out_fbx, out_blend, review_dir
  height_scale     multiply after matching the mesh height to the mannequin
  offset           [x, y, z] metres, applied after scaling
  yaw_deg          rotation of the mesh about Z to face the mannequin's front
  pose             [[bone, [ax, ay, az], degrees], ...] world-axis rotations about
                   each bone's head, applied in order (parents first) before the pose
                   becomes the new rest pose; used to bring the arms inside the
                   generated limbs. Only rotations change, so every bone's local
                   translation stays identical to the mannequin and the game's
                   index-copied poses remain valid.
  target_tris      decimation target for the runtime mesh
  voxel            voxel size (m) of the watertight weighting proxy
  cut_islands      optional [[min xyz], [max xyz]] boxes: welded islands whose
                   bounds lie fully inside are removed (e.g. a loose crossguard)
  cut_segments     optional [[a xyz], [b xyz], radius]: vertices within radius of
                   the segment are removed (e.g. a blade fused to the robe)
  Cut coordinates are in mannequin space before `offset` is applied.
  chains           optional swing chains for capes/robes, simulated in game:
                   [{"group": "back"|"front", "columns": [x...], "levels": [z...],
                     "x_extent": w, "layer": t, "margin": m}]. Each column becomes a
                   parentless chain of bones (cape_<group><c>_<k>, plus an unweighted
                   _end bone) placed on the cloth surface at those heights. Cloth is
                   the outermost layer (within t) on that side, |x| < w, at least m
                   off the mannequin's body surface. Chains are appended after every mannequin bone so
                   the mannequin's indices are unchanged.
  cutout_alpha     faces whose base-colour alpha drops below this anywhere get the
                   masked "Cloth" slot; everything else is opaque "Solid" (default .98)

Weights are distance-to-bone (see below); cloth regions blend onto the swing chains.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector, Euler

cfg = json.load(open(sys.argv[sys.argv.index('--') + 1]))
report = {'config': cfg}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def select_only(*objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

def apply_pose(arm, pose):
    from mathutils import Matrix
    for name, axis, deg in pose:
        pb = arm.pose.bones[name]
        bpy.context.view_layer.update()
        head = pb.matrix.to_translation()
        rot = Matrix.Translation(head) @ Matrix.Rotation(math.radians(deg), 4, Vector(axis)) @ Matrix.Translation(-head)
        pb.matrix = rot @ pb.matrix
    bpy.context.view_layer.update()

def world_bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (Vector([min(p[i] for p in pts) for i in range(3)]),
            Vector([max(p[i] for p in pts) for i in range(3)]))

# Mannequin: armature plus its mesh (mesh only used for height reference).
bpy.ops.import_scene.fbx(filepath=cfg['manny_fbx'], use_anim=False, automatic_bone_orientation=False,
                         ignore_leaf_bones=False)
arm = next(o for o in scene.objects if o.type == 'ARMATURE')
# The FBX puts the armature under a 0.01-scale null (Unreal centimetres). Detach it,
# keeping its world transform, so the armature object itself carries that scale.
world = arm.matrix_world.copy(); arm.parent = None; arm.matrix_world = world
manny_meshes = [o for o in scene.objects if o.type == 'MESH']
for o in manny_meshes:
    w = o.matrix_world.copy(); o.parent = None; o.matrix_world = w
for o in [o for o in scene.objects if o.type == 'EMPTY']:
    bpy.data.objects.remove(o, do_unlink=True)
m_lo, m_hi = world_bounds(manny_meshes)
report['manny_bounds'] = [list(m_lo), list(m_hi)]
report['bones'] = [b.name for b in arm.data.bones]

# Generated character.
before = set(scene.objects)
bpy.ops.import_scene.gltf(filepath=cfg['glb'])
gen_objs = [o for o in scene.objects if o not in before]
mesh = next(o for o in gen_objs if o.type == 'MESH')
for o in gen_objs:
    if o is not mesh and o.type != 'MESH':
        mesh.matrix_world = mesh.matrix_world.copy()
select_only(mesh)
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in gen_objs:
    if o is not mesh:
        bpy.data.objects.remove(o, do_unlink=True)

# Weld UV-seam splits so islands are geometric.
bm = bmesh.new(); bm.from_mesh(mesh.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)

def islands(bm):
    bm.verts.ensure_lookup_table()
    seen, out = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, comp = [v], []
        seen.add(v.index)
        while stack:
            x = stack.pop(); comp.append(x)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen:
                    seen.add(y.index); stack.append(y)
        out.append(comp)
    return out

# Orient and scale; cuts are expressed with the mesh centred on X/Y, feet at Z=0.
yaw = math.radians(cfg.get('yaw_deg', 0))
bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Euler((0, 0, yaw)).to_matrix())
zs = [v.co.z for v in bm.verts]
scale = (m_hi.z - m_lo.z) / (max(zs) - min(zs)) * cfg.get('height_scale', 1.0)
bmesh.ops.scale(bm, vec=(scale, scale, scale), verts=bm.verts)
xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, m_lo.z - min(zs))))

removed = 0
for lo, hi in cfg.get('cut_islands', []):
    for comp in islands(bm):
        if all(lo[i] <= v.co[i] <= hi[i] for v in comp for i in range(3)):
            removed += len(comp)
            bmesh.ops.delete(bm, geom=comp, context='VERTS')
for a, b, radius in cfg.get('cut_segments', []):
    a, b = Vector(a), Vector(b)
    ab = b - a
    doomed = [v for v in bm.verts
              if (v.co - (a + ab * max(0.0, min(1.0, (v.co - a).dot(ab) / ab.length_squared)))).length < radius]
    removed += len(doomed)
    bmesh.ops.delete(bm, geom=doomed, context='VERTS')
report['cut_vertices'] = removed
bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(((m_lo.x + m_hi.x) / 2, (m_lo.y + m_hi.y) / 2, 0))
                    + Vector(cfg.get('offset', (0, 0, 0))))
bm.to_mesh(mesh.data); bm.free()
mesh.data.update()
mesh.name = 'Body'

# Runtime decimation (UVs preserved by collapse).
tris = sum(len(p.vertices) - 2 for p in mesh.data.polygons)
target = cfg.get('target_tris', 100000)
if tris > target:
    d = mesh.modifiers.new('decimate', 'DECIMATE'); d.ratio = target / tris; d.use_collapse_triangulate = True
    select_only(mesh); bpy.ops.object.modifier_apply(modifier=d.name)
report['triangles_source'] = tris
report['triangles_runtime'] = sum(len(p.vertices) - 2 for p in mesh.data.polygons)

# Mannequin body surface (front-most / back-most y per 2 cm height band) for
# telling loose cloth apart from armour that sits on the body.
import numpy as np
MV = np.array([tuple(o.matrix_world @ v.co) for o in manny_meshes for v in o.data.vertices])
MV = MV[np.abs(MV[:, 0]) < .22]
BANDS = np.arange(0, 1.9, .02)
def band_profile(fn, fill):
    out = np.array([fn(MV[np.abs(MV[:, 2] - z) < .02, 1]) if (np.abs(MV[:, 2] - z) < .02).any() else fill for z in BANDS])
    return np.array([fn(out[max(0, i - 2):i + 3]) for i in range(len(out))])
BACK = band_profile(np.max, 0.0)
FRONT = band_profile(np.min, 0.0)
def surface(group, z):
    return np.interp(z, BANDS, BACK if group == 'back' else FRONT)

# Re-rest the mannequin skeleton: rotations only.
for o in manny_meshes:
    bpy.data.objects.remove(o, do_unlink=True)
select_only(arm)
bpy.ops.object.mode_set(mode='POSE')
apply_pose(arm, cfg.get('pose', []))
bpy.ops.pose.armature_apply(selected=False)
bpy.ops.object.mode_set(mode='OBJECT')

V = np.array([tuple(mesh.matrix_world @ v.co) for v in mesh.data.vertices])
smooth01 = lambda x: np.clip(x, 0, 1) ** 2 * (3 - 2 * np.clip(x, 0, 1))
def cloth_share_of(spec):
    # Loose cloth = the outermost layer on the group's side (within `layer` of the
    # back-most/front-most surface in its 3 cm x/z cell), inside the chain group's
    # width and at least `margin` off the mannequin's body surface.
    g = spec['group']; side = 1 if g == 'back' else -1
    sy = V[:, 1] * side
    cell = np.floor(V[:, 0] / .03).astype(int) * 1000 + np.floor(V[:, 2] / .03).astype(int)
    order = np.argsort(cell); uniq, start = np.unique(cell[order], return_index=True)
    outer = np.maximum.reduceat(sy[order], start)
    depth = np.empty(len(V)); depth[order] = np.repeat(outer, np.diff(np.append(start, len(V)))) - sy[order]
    layer = spec.get('layer', .03)
    off_body = sy - surface(g, V[:, 2]) * side - spec.get('margin', 0.0)
    return (smooth01((layer + .01 - depth) / .02) * smooth01(off_body / .03)
            * smooth01((spec.get('x_extent', .3) - np.abs(V[:, 0])) / .04))
chains = []  # (group, [bone names], [points])
for spec in cfg.get('chains', []):
    g = spec['group']
    loose = cloth_share_of(spec) > .5
    for c, x in enumerate(spec['columns']):
        pts = []
        for z in spec['levels']:
            near = loose & (np.abs(V[:, 0] - x) < .05) & (np.abs(V[:, 2] - z) < .04)
            if near.sum() < 5:
                if pts:
                    break
                continue  # cloth starts lower than this level
            # sit the bone just inside the cloth's outer face
            y = np.percentile(V[near, 1], 70 if g == 'back' else 30)
            pts.append((x, float(y), z))
        if len(pts) >= 3:
            chains.append((g, [f'cape_{g}{c}_{k}' for k in range(len(pts) - 1)] + [f'cape_{g}{c}_end'], pts))
if chains:
    select_only(arm)
    bpy.ops.object.mode_set(mode='EDIT')
    inv = arm.matrix_world.inverted()
    for g, names_, pts in chains:
        parent = None
        for k, name in enumerate(names_):
            eb = arm.data.edit_bones.new(name)
            a = Vector(pts[k]); b = Vector(pts[k + 1]) if k + 1 < len(pts) else a + (a - Vector(pts[k - 1])) * .3
            eb.head = inv @ a; eb.tail = inv @ b
            eb.parent = parent; eb.use_connect = False; eb.use_deform = not name.endswith('_end')
            parent = eb
    bpy.ops.object.mode_set(mode='OBJECT')
report['chains'] = [{'group': g, 'bones': n, 'points': p} for g, n, p in chains]
report['bone_heads'] = {b.name: list(arm.matrix_world @ b.head_local) for b in arm.data.bones}

# Distance-to-bone skin weights. Each deforming body bone is a segment from its
# head to its main child (leaves extend along their parent). A vertex's weight for
# a bone falls off with distance scaled by that bone's typical limb radius, then
# the weights are smoothed over the mesh and limited to four influences.
RADIUS = {'pelvis': .16, 'spine': .16, 'neck': .07, 'head': .12, 'clavicle': .08, 'upperarm': .07,
          'lowerarm': .06, 'hand': .05, 'thigh': .10, 'calf': .07, 'foot': .06, 'ball': .05}
CHILD = {'pelvis': 'spine_01', 'spine_05': 'neck_01', 'hand_l': 'middle_metacarpal_l', 'hand_r': 'middle_metacarpal_r'}
bones = {b.name: b for b in arm.data.bones}
skip = ('ik_', 'interaction', 'center_of_mass', 'root', 'cape_')
body = [b for b in arm.data.bones if b.use_deform and 'twist' not in b.name and not b.name.startswith(skip)]
def head(b):
    return np.array(arm.matrix_world @ b.head_local)
segs, rads, names = [], [], []
for b in body:
    kids = [c for c in b.children if c in body]
    child = bones.get(CHILD.get(b.name, '')) or (max(kids, key=lambda c: len(c.children_recursive)) if kids else None)
    a = head(b)
    if child is not None:
        e = head(child)
    elif b.name == 'head':
        e = a + np.array([0, 0, .2])
    else:
        d = a - head(b.parent); e = a + d * 0.7
    key = next((k for k in RADIUS if b.name.startswith(k)), None)
    r = RADIUS[key] if key else .02  # fingers
    segs.append((a, e)); rads.append(r); names.append(b.name)
A = np.array([s[0] for s in segs]); E = np.array([s[1] for s in segs]); R = np.array(rads)
AB = E - A
t = np.clip(np.einsum('vbk,bk->vb', V[:, None, :] - A[None], AB) / np.maximum((AB * AB).sum(1), 1e-9), 0, 1)
D = np.linalg.norm(V[:, None, :] - (A[None] + t[..., None] * AB[None]), axis=2) / R[None]
W = 1.0 / np.maximum(D, 0.05) ** 6 + 1e-12
# Limb bones own the armour around the limb but not cloth hanging behind it. The
# reach is generous (bulky plate sits 10-15 cm from the bone), but arm bones ignore
# anything more than 9 cm behind the arm (the cape) and leg bones ignore anything
# more than 15 cm in front of or behind the leg (cape behind, stoles in front), so
# loose cloth falls back to the spine and pelvis and clips rather than tearing.
CORE = {'thigh': .17, 'calf': .14, 'foot': .13, 'ball': .12, 'upperarm': .15, 'lowerarm': .13, 'hand': .12}
dist = D * R[None]
dy = V[:, None, 1] - (A[None, :, 1] + t * AB[None, :, 1])
for bi, name in enumerate(names):
    key = next((k for k in CORE if name.startswith(k)), None)
    leg = key in ('thigh', 'calf', 'foot', 'ball')
    is_arm = not leg and (key is not None or (name.endswith(('_l', '_r')) and not name.startswith('clavicle')))
    if not (leg or is_arm):
        continue
    W[:, bi] *= np.exp(-(np.maximum(0, dist[:, bi] - CORE.get(key, .06)) / cfg.get('fade', .05)) ** 2)
    W[(np.abs(dy[:, bi]) if leg else dy[:, bi]) > (cfg.get('leg_depth', .15) if leg else cfg.get('arm_behind', .09)), bi] = 0
W /= W.sum(1, keepdims=True)
# Loose cloth blends from the body bones onto the nearest swing chain: fully free a
# few centimetres beyond the body surface, pinned near the top of the chain.
cloth_share = np.zeros(len(V))
for g in sorted({c[0] for c in chains}):
    spec = next(s_ for s_ in cfg['chains'] if s_['group'] == g)
    gc = [c for c in chains if c[0] == g]
    top_z = max(c[2][0][2] for c in gc)
    f = cloth_share_of(spec) * smooth01((top_z - V[:, 2]) / .15)
    segs_g, names_g = [], []
    for _, bn, pts in gc:
        for k in range(len(pts) - 1):
            segs_g.append((np.array(pts[k]), np.array(pts[k + 1]))); names_g.append(bn[k])
    a_ = np.array([q[0] for q in segs_g]); ab_ = np.array([q[1] for q in segs_g]) - a_
    t_ = np.clip(np.einsum('vbk,bk->vb', V[:, None, :] - a_[None], ab_) / (ab_ * ab_).sum(1), 0, 1)
    d_ = np.linalg.norm(V[:, None, :] - (a_[None] + t_[..., None] * ab_[None]), axis=2)
    wc = 1.0 / np.maximum(d_, .02) ** 4; wc /= wc.sum(1, keepdims=True)
    f = np.minimum(f, 1 - cloth_share); cloth_share += f
    W = np.concatenate([W, wc * f[:, None]], axis=1); names += names_g
    W[:, :len(segs)] *= (1 - f)[:, None]
report['cloth_vertices'] = int((cloth_share > .5).sum())
top = np.argsort(-W, axis=1)[:, :4]
groups = {n: mesh.vertex_groups.new(name=n) for n in names}
for b in arm.data.bones:
    if b.name not in groups:
        mesh.vertex_groups.new(name=b.name)
rows = np.arange(len(V))[:, None]
Wt = W[rows, top]; Wt /= Wt.sum(1, keepdims=True)
for bi, name in enumerate(names):
    sel = np.nonzero((top == bi).any(1))[0]
    g = groups[name]
    for vi in sel:
        g.add([int(vi)], float(Wt[vi][list(top[vi]).index(bi)]), 'REPLACE')
select_only(mesh)
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=cfg.get('smooth', 3))
bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
bpy.ops.object.vertex_group_normalize_all(lock_active=False)
bpy.ops.object.mode_set(mode='OBJECT')
report['weighted_bones'] = names
report['mesh_unweighted'] = sum(1 for v in mesh.data.vertices if not v.groups)

mesh.parent = arm
mesh.matrix_parent_inverse = arm.matrix_world.inverted()
mod = mesh.modifiers.new('Armature', 'ARMATURE'); mod.object = arm

# Opaque/cutout split: only faces that actually use the base-colour alpha (torn
# cloth edges) keep the masked material; armour renders opaque.
mat = mesh.active_material
img = next(n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image
           and n.outputs['Color'].links and n.outputs['Color'].links[0].to_node.type == 'BSDF_PRINCIPLED')
w_, h_ = img.size
alpha = np.array(img.pixels[:], dtype=np.float32).reshape(h_, w_, 4)[..., 3]
uv = np.zeros(len(mesh.data.loops) * 2); mesh.data.uv_layers.active.data.foreach_get('uv', uv); uv = uv.reshape(-1, 2)
px = np.clip((uv[:, 0] % 1) * w_, 0, w_ - 1).astype(int); py = np.clip((uv[:, 1] % 1) * h_, 0, h_ - 1).astype(int)
loop_alpha = alpha[py, px]
limit = cfg.get('cutout_alpha', .98)
solid = mat; solid.name = 'Solid'
cloth = solid.copy(); cloth.name = 'Cloth'
mesh.data.materials.clear(); mesh.data.materials.append(solid); mesh.data.materials.append(cloth)
cut = [min(loop_alpha[p.loop_start:p.loop_start + p.loop_total]) < limit for p in mesh.data.polygons]
mesh.data.polygons.foreach_set('material_index', np.array(cut, dtype=np.int32))
report['cutout_faces'] = int(sum(cut)); report['faces'] = len(cut)

# Name the generated textures by role (the glTF importer calls them Image_0/1).
for node in solid.node_tree.nodes:
    if node.type == 'TEX_IMAGE' and node.image:
        out = node.outputs['Color'].links[0].to_node if node.outputs['Color'].links else None
        node.image.name = 'BaseColor' if out is not None and out.type == 'BSDF_PRINCIPLED' else 'MetalRough'

Path(cfg['out_fbx']).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=cfg['out_blend'])
select_only(mesh, arm)
bpy.ops.export_scene.fbx(filepath=cfg['out_fbx'], use_selection=True, add_leaf_bones=False,
                         bake_anim=False, mesh_smooth_type='FACE', use_armature_deform_only=False,
                         primary_bone_axis='Y', secondary_bone_axis='X', axis_forward='-Z', axis_up='Y',
                         path_mode='STRIP', embed_textures=False)
tex_dir = Path(cfg['out_fbx']).parent
for img in bpy.data.images:
    if img.size[0] and img.name in ('BaseColor', 'MetalRough'):
        img.filepath_raw = str(tex_dir / f"{Path(cfg['out_fbx']).stem}_{img.name}.png")
        img.file_format = 'PNG'; img.save()
json.dump(report, open(Path(cfg['out_fbx']).with_suffix('.json'), 'w'), indent=1, default=list)
print('RIGFIT done', report['triangles_runtime'], 'unweighted', report['mesh_unweighted'])
