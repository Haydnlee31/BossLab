"""Deformation check: render a rigged .blend in rest pose and in a stride/raised-arm pose.

blender -b -P pose_test.py -- <rig.blend> <out_prefix>
"""
import bpy, math, sys
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.open_mainfile(filepath=argv[0])
prefix = argv[1]
scene = bpy.context.scene
arm = next(o for o in scene.objects if o.type == 'ARMATURE')

scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x, scene.render.resolution_y = 700, 900
scene.view_settings.view_transform = 'AgX'
world = bpy.data.worlds.new('w'); scene.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.13, 0.13, 0.14, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.2
for name, rot, e in [('key', (50, 0, -35), 6.0), ('fill', (60, 0, 140), 2.0), ('rim', (70, 0, 180), 2.0)]:
    d = bpy.data.lights.new(name, 'SUN'); d.energy = e
    o = bpy.data.objects.new(name, d); o.rotation_euler = [math.radians(a) for a in rot]; scene.collection.objects.link(o)
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); cam.data.lens = 60
scene.collection.objects.link(cam); scene.camera = cam

def shoot(name, az):
    target = Vector((0, 0, 0.95)); a = math.radians(az)
    cam.location = target + Vector((math.cos(a) * 4.2, math.sin(a) * 4.2, 0.4))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.filepath = f'{prefix}-{name}.png'
    bpy.ops.render.render(write_still=True)

shoot('rest', -60)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for name, axis, deg in [('thigh_l', (1, 0, 0), 35), ('calf_l', (1, 0, 0), -30), ('thigh_r', (1, 0, 0), -25),
                        ('calf_r', (1, 0, 0), -35), ('spine_03', (0, 0, 1), 15),
                        ('upperarm_r', (1, 0, 0), 80), ('lowerarm_r', (1, 0, 0), 50),
                        ('upperarm_l', (1, 0, 0), 40), ('lowerarm_l', (1, 0, 0), 60), ('head', (0, 0, 1), -15)]:
    pb = arm.pose.bones[name]
    bpy.context.view_layer.update()
    h = pb.matrix.to_translation()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, Vector(axis)) @ Matrix.Translation(-h) @ pb.matrix
bpy.ops.object.mode_set(mode='OBJECT')
shoot('pose', -60)
shoot('pose-side', 0)
