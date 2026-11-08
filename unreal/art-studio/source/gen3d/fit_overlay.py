"""Orthographic front/side overlay of a rigged fit (or a raw fit config) for joint alignment.

blender -b -P fit_overlay.py -- <file.blend | fit.json> <out_prefix>
With a .blend (output of rig_fit.py) the skinned mesh is rendered in rest pose and
its armature joints are drawn on top. With a fit.json, the raw GLB is placed using
the same scale/offset rules and the unmodified mannequin joints are drawn, which is
how the pose rotations are chosen.
"""
import bpy, json, math, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
src, prefix = argv[0], argv[1]
if src.endswith('.blend'):
    bpy.ops.wm.open_mainfile(filepath=src)
    arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for o in meshes:
        for m in o.modifiers:
            if m.type == 'ARMATURE':
                m.show_render = False
else:
    cfg = json.load(open(src))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=cfg['manny_fbx'], use_anim=False, automatic_bone_orientation=False)
    arm = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    manny = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    pts = [o.matrix_world @ Vector(c) for o in manny for c in o.bound_box]
    m_lo = Vector([min(p[i] for p in pts) for i in range(3)]); m_hi = Vector([max(p[i] for p in pts) for i in range(3)])
    for o in manny:
        bpy.data.objects.remove(o, do_unlink=True)
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=cfg['glb'])
    meshes = [o for o in bpy.context.scene.objects if o not in before and o.type == 'MESH']
    for o in meshes:
        o.rotation_euler.z += math.radians(cfg.get('yaw_deg', 0))
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    s = (m_hi.z - m_lo.z) / (hi.z - lo.z) * cfg.get('height_scale', 1.0)
    root = next(o for o in bpy.context.scene.objects if o not in before and o.parent is None)
    root.scale *= s
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    root.location += Vector(((m_lo.x + m_hi.x) / 2 - (lo.x + hi.x) / 2, (m_lo.y + m_hi.y) / 2 - (lo.y + hi.y) / 2,
                             m_lo.z - lo.z)) + Vector(cfg.get('offset', (0, 0, 0)))
    bpy.context.view_layer.update()
    if cfg.get('pose'):
        from mathutils import Matrix
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')
        for name, axis, deg in cfg['pose']:
            pb = arm.pose.bones[name]
            bpy.context.view_layer.update()
            head = pb.matrix.to_translation()
            pb.matrix = (Matrix.Translation(head) @ Matrix.Rotation(math.radians(deg), 4, Vector(axis))
                         @ Matrix.Translation(-head)) @ pb.matrix
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.update()

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
W, H, ORTHO = 800, 1000, 2.0
scene.render.resolution_x, scene.render.resolution_y = W, H
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.5, 0.5, 0.5, 1)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
cam.data.type = 'ORTHO'; cam.data.ortho_scale = ORTHO * H / W if H > W else ORTHO
scene.collection.objects.link(cam); scene.camera = cam
half_h = cam.data.ortho_scale / 2
half_w = half_h * W / H
CZ = 0.9
joints = ['pelvis', 'spine_03', 'neck_01', 'head', 'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l', 'upperarm_r',
          'lowerarm_r', 'hand_r', 'thigh_l', 'calf_l', 'foot_l', 'ball_l', 'thigh_r', 'calf_r', 'foot_r', 'ball_r']
pos = {}
for n in joints:
    pb = arm.pose.bones[n]
    pos[n] = arm.matrix_world @ pb.head
out = {}
for view, loc, rot, axis in [('front', (0, -6, CZ), (math.pi / 2, 0, 0), 0), ('side', (6, 0, CZ), (math.pi / 2, 0, math.pi / 2), 1)]:
    cam.location = loc; cam.rotation_euler = rot
    scene.render.filepath = f'{prefix}-{view}.png'
    bpy.ops.render.render(write_still=True)
    pix = {}
    for n, p in pos.items():
        h = p[axis]
        pix[n] = [round((h + half_w) / (2 * half_w) * W), round((half_h - (p.z - CZ)) / (2 * half_h) * H)]
    out[view] = pix
json.dump(out, open(f'{prefix}-joints.json', 'w'), indent=1)
