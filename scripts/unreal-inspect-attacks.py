"""Sample installed attack assets using Unreal's actual pose evaluator."""
import json
from pathlib import Path
import unreal
root = Path(unreal.Paths.project_dir()).resolve().parents[1]
report = {}
for name in ['MM_Attack_01', 'MM_Attack_02', 'MM_Attack_03', 'MM_ChargedAttack']:
    asset = unreal.load_asset('/Game/Characters/Mannequins/Anims/Unarmed/Attack/' + name)
    duration = asset.get_editor_property('sequence_length')
    samples = []
    for i in range(21):
        t = duration * i / 20
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(asset, t, unreal.AnimPoseEvaluationOptions())
        bones = {}
        for bone in ['root', 'hand_r', 'hand_l', 'foot_r', 'foot_l']:
            transform = unreal.AnimPoseExtensions.get_bone_pose(pose, bone, unreal.AnimPoseSpaces.WORLD)
            p = transform.translation
            bones[bone] = [p.x, p.y, p.z]
        samples.append({'seconds': t, 'bones': bones})
    report[name] = {'duration': duration, 'samples': samples}
(root / 'artifacts/unreal/attack-animation-samples.json').write_text(json.dumps(report, indent=2))
unreal.log('BossLab attack pose audit saved')
