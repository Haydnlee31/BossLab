"""Retarget HY-Motion (SMPL-style 52-bone FBX) clips onto the UE5 mannequin.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/anim/retarget_motion.py -- <manny.fbx> <out.fbx> <clip.fbx> [<clip.fbx> ...]
Each clip becomes one take named after its file stem (HY_<stem>).
- Rest alignment: HY rests in a T-pose, Manny in an A-pose, so each mapped Manny bone's rest is
  first turned (world space) so its direction to the next mapped joint matches the source's;
  then every frame:  R_t = R_s * inv(R_s_rest) * (C * R_t_rest).
- Spine Spine1/2/3 -> spine_01/03/05; Neck -> neck_01; Collar/Shoulder/Elbow/Wrist -> clavicle/
  upperarm/lowerarm/hand; Hip/Knee/Ankle/Foot -> thigh/calf/foot/ball; fingers 1-3 -> 01-03.
- In place: the pelvis keeps its height and its sway, but the straight-line horizontal drift
  between the first and last frame is removed (the game moves the capsule itself).
The armature object is named 'root' and keyed in each take (Unreal needs the root track).
"""
import bpy, json, math, os, sys
from mathutils import Quaternion, Vector

args = sys.argv[sys.argv.index('--') + 1:]
MANNY, OUT, CLIPS = os.path.abspath(args[0]), os.path.abspath(args[1]), [os.path.abspath(a) for a in args[2:]]
MAP = {'Pelvis': 'pelvis', 'Spine1': 'spine_01', 'Spine2': 'spine_03', 'Spine3': 'spine_05', 'Neck': 'neck_01', 'Head': 'head'}
for S, s in (('L', 'l'), ('R', 'r')):
    MAP.update({f'{S}_Collar': f'clavicle_{s}', f'{S}_Shoulder': f'upperarm_{s}', f'{S}_Elbow': f'lowerarm_{s}', f'{S}_Wrist': f'hand_{s}',
                f'{S}_Hip': f'thigh_{s}', f'{S}_Knee': f'calf_{s}', f'{S}_Ankle': f'foot_{s}', f'{S}_Foot': f'ball_{s}'})
    for f in ('Index', 'Middle', 'Pinky', 'Ring', 'Thumb'):
        for k in (1, 2, 3):
            MAP[f'{S}_{f}{k}'] = f'{f.lower()}_0{k}_{s}'
# The joint each bone points at (for rest alignment): source -> target pairs.
CHAIN = {'Spine1': 'Spine2', 'Spine2': 'Spine3', 'Spine3': 'Neck', 'Neck': 'Head'}
for S in 'LR':
    CHAIN.update({f'{S}_Collar': f'{S}_Shoulder', f'{S}_Shoulder': f'{S}_Elbow', f'{S}_Elbow': f'{S}_Wrist', f'{S}_Wrist': f'{S}_Middle1',
                  f'{S}_Hip': f'{S}_Knee', f'{S}_Knee': f'{S}_Ankle', f'{S}_Ankle': f'{S}_Foot'})
    for f in ('Index', 'Middle', 'Pinky', 'Ring', 'Thumb'):
        CHAIN[f'{S}_{f}1'] = f'{S}_{f}2'; CHAIN[f'{S}_{f}2'] = f'{S}_{f}3'

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.fbx(filepath=MANNY, use_anim=False, automatic_bone_orientation=False, ignore_leaf_bones=False)
T = next(o for o in scene.objects if o.type == 'ARMATURE')
w = T.matrix_world.copy(); T.parent = None; T.matrix_world = w
for o in [o for o in scene.objects if o.type != 'ARMATURE']:
    bpy.data.objects.remove(o, do_unlink=True)
T.name = 'root'
TQ = T.matrix_world.to_quaternion()
t_rest = {b.name: TQ @ b.matrix_local.to_quaternion() for b in T.data.bones}
t_head = {b.name: T.matrix_world @ b.head_local for b in T.data.bones}
order = []
def walk(b):
    order.append(b)
    for c in b.children: walk(c)
for b in T.data.bones:
    if b.parent is None: walk(b)
inverse = {v: k for k, v in MAP.items()}
report, takes = {}, []

for path in CLIPS:
    before = set(bpy.data.objects); acts_before = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False, ignore_leaf_bones=False)
    S = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o not in before)
    src = next(a for a in bpy.data.actions if a not in acts_before)
    for o in [o for o in bpy.data.objects if o not in before and o is not S]:
        bpy.data.objects.remove(o, do_unlink=True)
    SQ = S.matrix_world.to_quaternion()
    s_rest = {b.name: SQ @ b.matrix_local.to_quaternion() for b in S.data.bones}
    s_head = {b.name: S.matrix_world @ b.head_local for b in S.data.bones}
    # Rest alignment per mapped target bone.
    corr = {}
    for sb, nxt in CHAIN.items():
        if sb in s_head and nxt in s_head and sb in MAP and nxt in MAP:
            ds = (s_head[nxt] - s_head[sb]).normalized(); dt = (t_head[MAP[nxt]] - t_head[MAP[sb]]).normalized()
            corr[MAP[sb]] = dt.rotation_difference(ds)
    pel_basis = (T.matrix_world.to_3x3() @ T.data.bones['pelvis'].matrix_local.to_3x3()).inverted()
    S.animation_data_create(); S.animation_data.action = src
    f0, f1 = int(src.frame_range[0]), int(src.frame_range[1])
    W = lambda n: S.matrix_world @ S.pose.bones[n].head
    # Facing: HY clips start at arbitrary yaws; turn each so it starts facing -Y (Manny's
    # front in Blender), from the hip line on the first frame.
    scene.frame_set(f0)
    hips = W('R_Hip') - W('L_Hip'); fwd = Vector((0, 0, 1)).cross(Vector((hips.x, hips.y, 0))).normalized()
    Y = fwd.to_track_quat('-Y', 'Z').inverted() if fwd.length > .5 else Quaternion()
    Y = Quaternion((0, 0, 1), Y.to_euler().z)   # yaw only
    # Standing hip height: rest leg length (hip to toe joint) plus the planted toe-joint height.
    planted = min(min(W('L_Foot').z, W('R_Foot').z) for _ in [0] for fr in [f0] )
    for fr in range(f0, f1 + 1, 2):
        scene.frame_set(fr); planted = min(planted, W('L_Foot').z, W('R_Foot').z)
    s_stand = (s_head['Pelvis'].z - min(s_head['L_Foot'].z, s_head['R_Foot'].z)) + planted
    t_stand = t_head['pelvis'].z
    ratio = t_stand / max(1e-6, s_stand)
    # Travel to remove: the pelvis path smoothed over +-7 frames (~0.5 s); what stays is the
    # sway and weight shift around it (a straight line left curved travel, e.g. pivots, in).
    track = []
    for fr in range(f0, f1 + 1):
        scene.frame_set(fr); track.append(Y @ W('Pelvis'))
    def smooth(i, k=7):
        lo, hi = max(0, i - k), min(len(track) - 1, i + k)
        return sum((track[j] for j in range(lo, hi + 1)), Vector()) / (hi - lo + 1)
    p_first, p_last = track[0], track[-1]
    name = 'HY_' + os.path.splitext(os.path.basename(path))[0]
    act = bpy.data.actions.new(name); T.animation_data_create(); T.animation_data.action = act
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        pose_world = {}
        for b in order:
            pb = T.pose.bones[b.name]
            parent_world = pose_world[b.parent.name] if b.parent else TQ
            rest_rel = (t_rest[b.parent.name].inverted() @ t_rest[b.name]) if b.parent else (TQ.inverted() @ t_rest[b.name])
            base = parent_world @ rest_rel
            sname = inverse.get(b.name)
            if sname and sname in S.pose.bones:
                rs = Y @ SQ @ S.pose.bones[sname].matrix.to_quaternion()
                want = rs @ s_rest[sname].inverted() @ corr.get(b.name, Quaternion()) @ t_rest[b.name]
                q = base.inverted() @ want
            else:
                q = Quaternion()
            q.normalize()
            pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = q
            pb.keyframe_insert('rotation_quaternion', frame=f - f0)
            pose_world[b.name] = base @ q
        u = (f - f0) / max(1, f1 - f0)
        sp = Y @ W('Pelvis')
        drift = smooth(f - f0)
        d = Vector(((sp.x - drift.x) * ratio, (sp.y - drift.y) * ratio, (sp.z - s_stand) * ratio))
        pbp = T.pose.bones['pelvis']; pbp.location = pel_basis @ d
        pbp.keyframe_insert('location', frame=f - f0)
    wrists = []
    for fr in range(f0, f1 + 1):
        scene.frame_set(fr); wrists.append((W('L_Wrist') + W('R_Wrist')) * .5 - W('Pelvis'))
    speeds = [(wrists[i] - wrists[i - 1]).length for i in range(1, len(wrists))]
    peak = max(range(len(speeds)), key=lambda i: speeds[i]) + 1 if speeds else 0
    for fr in (0, f1 - f0):
        T.keyframe_insert('location', frame=fr); T.keyframe_insert('rotation_euler', frame=fr); T.keyframe_insert('scale', frame=fr)
    act.use_fake_user = True; takes.append(act)
    report[name] = {'frames': f1 - f0 + 1, 'fps': scene.render.fps, 'ratio': round(ratio, 4), 'yaw_fix_deg': round(math.degrees(Y.to_euler().z), 1),
                    'drift_removed_m': round((p_last - p_first).length, 3), 'peak_hand_speed_frame': peak,
                    'peak_hand_speed_s': round(peak / scene.render.fps, 3)}
    bpy.data.objects.remove(S, do_unlink=True)
    for a in list(bpy.data.actions):
        if a not in takes: bpy.data.actions.remove(a)

for o in scene.objects: o.select_set(False)
T.select_set(True); bpy.context.view_layer.objects.active = T; T.animation_data.action = None
bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                         bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
                         object_types={'ARMATURE'}, use_armature_deform_only=False,
                         primary_bone_axis='Y', secondary_bone_axis='X', axis_forward='-Z', axis_up='Y')
bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(OUT)[0] + '.blend')
json.dump(report, open(os.path.splitext(OUT)[0] + '.json', 'w'), indent=1)
print('BOSSLAB hy retarget', json.dumps(report))
