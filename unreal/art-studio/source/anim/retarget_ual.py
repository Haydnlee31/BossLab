"""Retarget Quaternius Universal Animation Library clips (CC0) onto the UE5 mannequin.

Run: unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
     unreal/art-studio/source/anim/retarget_ual.py -- <manny.fbx> <out_dir> <ual.glb> <Clip,Clip,...> [<ual2.glb> <Clip,...>]
The UAL rig uses UE4-mannequin-style names (pelvis, spine_01-03, neck_01, Head, clavicle..,
fingers, thigh/calf/foot/ball). For each frame, every mapped bone takes the source bone's
world-space rotation change from its rest pose:  R_t = R_s * inv(R_s_rest) * R_t_rest.
Spine: source 01/02/03 -> Manny 01/03/05 (02 and 04 ride rigidly between); Head -> head;
unmapped Manny bones keep their rest pose relative to the parent. The pelvis moves by the
source pelvis offset scaled by the pelvis-height ratio. Clips are the in-place (no root
motion) versions; the game moves the capsule. Writes UAL_Anims.fbx (one take per clip,
24 fps) for ue_import_ual.py and a pose preview sheet (contact sheet frames per clip).
"""
import bpy, json, math, os, sys
from mathutils import Matrix, Quaternion, Vector

args = sys.argv[sys.argv.index('--') + 1:]
MANNY, OUT = os.path.abspath(args[0]), os.path.abspath(args[1])
SOURCES = [(os.path.abspath(args[i]), args[i + 1].split(',')) for i in range(2, len(args), 2)]
os.makedirs(OUT, exist_ok=True)
MAP = {'pelvis': 'pelvis', 'spine_01': 'spine_01', 'spine_02': 'spine_03', 'spine_03': 'spine_05',
       'neck_01': 'neck_01', 'Head': 'head'}
for side in 'lr':
    for b in ('clavicle', 'upperarm', 'lowerarm', 'hand', 'thigh', 'calf', 'foot', 'ball'):
        MAP[f'{b}_{side}'] = f'{b}_{side}'
    for f in ('index', 'middle', 'pinky', 'ring', 'thumb'):
        for k in (1, 2, 3):
            MAP[f'{f}_0{k}_{side}'] = f'{f}_0{k}_{side}'

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
bpy.ops.import_scene.fbx(filepath=MANNY, use_anim=False, automatic_bone_orientation=False, ignore_leaf_bones=False)
T = next(o for o in scene.objects if o.type == 'ARMATURE')
world = T.matrix_world.copy(); T.parent = None; T.matrix_world = world
for o in [o for o in scene.objects if o.type == 'MESH']:
    w = o.matrix_world.copy(); o.parent = None; o.matrix_world = w
for o in [o for o in scene.objects if o.type == 'EMPTY']:
    bpy.data.objects.remove(o, do_unlink=True)
# The mannequin FBX's top node IS the 'root' bone (Blender turns it into the armature object):
# keep that name and key the object in every take, or Unreal reports no root track.
T.name = 'root'
TQ = T.matrix_world.to_quaternion()
t_rest = {b.name: (TQ @ b.matrix_local.to_quaternion()) for b in T.data.bones}
order = []
def walk(b):
    order.append(b)
    for c in b.children: walk(c)
for b in T.data.bones:
    if b.parent is None: walk(b)
inverse = {v: k for k, v in MAP.items()}
report = {'clips': {}}
targets = []

for path, clips in SOURCES:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    S = next(o for o in bpy.data.objects if o.type == 'ARMATURE' and o not in before)
    for o in [o for o in bpy.data.objects if o not in before and o.type == 'MESH']:
        bpy.data.objects.remove(o, do_unlink=True)
    SQ = S.matrix_world.to_quaternion()
    s_rest = {b.name: (SQ @ b.matrix_local.to_quaternion()) for b in S.data.bones}
    s_pel0 = S.matrix_world @ S.data.bones['pelvis'].head_local
    t_pel0 = T.matrix_world @ T.data.bones['pelvis'].head_local
    ratio = t_pel0.z / max(1e-6, s_pel0.z)
    pel_basis = (T.matrix_world.to_3x3() @ T.data.bones['pelvis'].matrix_local.to_3x3()).inverted()
    S.animation_data_create()
    for name in clips:
        src = bpy.data.actions.get(name)
        if src is None:
            report['clips'][name] = 'missing'; continue
        S.animation_data.action = src
        f0, f1 = int(src.frame_range[0]), int(src.frame_range[1])
        act = bpy.data.actions.new('UAL_' + name)
        T.animation_data_create(); T.animation_data.action = act
        for f in range(f0, f1 + 1):
            scene.frame_set(f)
            pose_world = {}
            for b in order:
                pb = T.pose.bones[b.name]
                parent_world = pose_world[b.parent.name] if b.parent else TQ
                rest_rel = (t_rest[b.parent.name].inverted() @ t_rest[b.name]) if b.parent else (TQ.inverted() @ t_rest[b.name])
                base = parent_world @ rest_rel
                src_name = inverse.get(b.name)
                if src_name and src_name in S.pose.bones:
                    rs = SQ @ S.pose.bones[src_name].matrix.to_quaternion()
                    want = rs @ s_rest[src_name].inverted() @ t_rest[b.name]
                    q = base.inverted() @ want
                else:
                    q = Quaternion()
                q.normalize()
                pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = q
                pb.keyframe_insert('rotation_quaternion', frame=f - f0)
                pose_world[b.name] = base @ q
            # Pelvis translation: source offset from rest, scaled to Manny.
            sp = S.matrix_world @ S.pose.bones['pelvis'].head
            d = (sp - s_pel0) * ratio
            pbp = T.pose.bones['pelvis']
            pbp.location = pel_basis @ d
            pbp.keyframe_insert('location', frame=f - f0)
        for fr in (0, f1 - f0):
            T.keyframe_insert('location', frame=fr); T.keyframe_insert('rotation_euler', frame=fr); T.keyframe_insert('scale', frame=fr)
        report['clips'][name] = {'frames': f1 - f0 + 1, 'ratio': round(ratio, 4)}
        act.use_fake_user = True
        targets.append(act)
    bpy.data.objects.remove(S, do_unlink=True)

# Export every retargeted take with the armature only (Unreal imports onto SK_Mannequin).
scene.render.fps = 24
for o in scene.objects: o.select_set(False)
T.select_set(True); bpy.context.view_layer.objects.active = T
for a in list(bpy.data.actions):
    if not a.name.startswith('UAL_'): bpy.data.actions.remove(a)
T.animation_data.action = None
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, 'UAL_Anims.fbx'), use_selection=True, add_leaf_bones=False,
                         bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
                         bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
                         object_types={'ARMATURE'}, use_armature_deform_only=False,
                         primary_bone_axis='Y', secondary_bone_axis='X', axis_forward='-Z', axis_up='Y')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'ual-retarget.blend'))
json.dump(report, open(os.path.join(OUT, 'retarget.json'), 'w'), indent=1)
print('BOSSLAB ual retarget', json.dumps(report['clips']))
