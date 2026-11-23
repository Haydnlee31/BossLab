"""Fit study through existing distance-weight pipeline, then restore EXACT source rest.
Uses a temporary fitted binding pose only; original skeleton data/order is reinstated.
Run Blender -b -P this.py -- fit.json. Does not import into Unreal.
"""
from pathlib import Path
source=Path(__file__).resolve().parents[1]/'gen3d/rig_fit.py'
s=source.read_text()
marker='# Re-rest the mannequin skeleton: rotations only.'
assert s.count(marker)==1
s=s.replace(marker,'''# Preserve original runtime skeleton before temporary binding pose.
weathered_original_data = arm.data.copy()
weathered_original_rest = {b.name: b.matrix_local.copy() for b in arm.data.bones}
weathered_original_order = [b.name for b in arm.data.bones]
'''+marker)
marker="Path(cfg['out_fbx']).parent.mkdir(parents=True, exist_ok=True)"
assert s.count(marker)==1
s=s.replace(marker,'''# Bake the generated surface back from fitted bind pose to unchanged runtime rest.
from mathutils import Matrix
assert not cfg.get('joint_offsets') and not cfg.get('bone_scale') and not cfg.get('chains'), 'Exact source skeleton only'
for b in arm.data.bones:
    arm.pose.bones[b.name].matrix = weathered_original_rest[b.name]
    bpy.context.view_layer.update()
select_only(mesh)
for modifier in list(mesh.modifiers):
    if modifier.type == 'ARMATURE': bpy.ops.object.modifier_apply(modifier=modifier.name)
arm.data = weathered_original_data
for pb in arm.pose.bones: pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
mesh.modifiers.new('RuntimeSkeleton', 'ARMATURE').object = arm
assert [b.name for b in arm.data.bones] == weathered_original_order
err=max(max(abs(b.matrix_local[i][j]-weathered_original_rest[b.name][i][j]) for i in range(4) for j in range(4)) for b in arm.data.bones)
assert err < 1e-7
report['original_runtime_rest_max_error'] = err
report['original_runtime_bone_order_preserved'] = True
report['binding_pose_only'] = cfg.get('pose', [])
'''+marker)
s=s.replace("apply_pose(arm, cfg.get('pose', []))", """apply_pose(arm, cfg.get('pose', []))
# Explicit generated-surface joint landmarks in world metres.
from mathutils import Matrix
for side, sign in [('l',1),('r',-1)]:
    def world(n): return arm.matrix_world @ arm.pose.bones[n].head
    def pointbone(name, child, direction):
        pb=arm.pose.bones[name]
        current=(world(child)-world(name)).normalized()
        desired=Vector(direction).normalized()
        rot=current.rotation_difference(desired).to_matrix().to_4x4()
        headw=world(name)
        transform=Matrix.Translation(headw)@rot@Matrix.Translation(-headw)
        pb.matrix=arm.matrix_world.inverted()@transform@arm.matrix_world@pb.matrix
        bpy.context.view_layer.update()
    elbow=Vector((sign*.48, .005, 1.29))
    pointbone('upperarm_'+side,'lowerarm_'+side,elbow-world('upperarm_'+side))
    wrist=Vector((sign*.75,-.135,1.28))
    pointbone('lowerarm_'+side,'hand_'+side,wrist-world('lowerarm_'+side))
    pointbone('hand_'+side,'middle_01_'+side,(sign,0,0))
    # Twist hand about its forward axis so the open thumb sits above the fingers.
    h='hand_'+side; axis=Vector((sign,0,0)); v=world('thumb_01_'+side)-world(h)
    v=(v-axis*v.dot(axis)).normalized(); desired=Vector((0,0,1))
    angle=math.atan2(axis.dot(v.cross(desired)),v.dot(desired))
    headw=world(h);rot=Matrix.Rotation(angle,4,axis)
    arm.pose.bones[h].matrix=arm.matrix_world.inverted()@Matrix.Translation(headw)@rot@Matrix.Translation(-headw)@arm.matrix_world@arm.pose.bones[h].matrix
    bpy.context.view_layer.update()
    for finger,spread in [('index',.12),('middle',0),('ring',-.07),('pinky',-.15),('thumb',.9)]:
        for k in [1,2]:
            pointbone(f'{finger}_0{k}_{side}',f'{finger}_0{k+1}_{side}',(sign,0,spread))
""")
exec(compile(s,str(source),'exec'))
