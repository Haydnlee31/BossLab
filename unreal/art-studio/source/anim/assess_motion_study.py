"""Read retargeted .blend, report actual sampled joints. No render or mesh edits.
Blender -b --python assess_motion_study.py -- study.blend assessment.json
Feet are bone endpoints, not sole contact; metrics are diagnostic, never a quality pass.
"""
import bpy, sys, json, math
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=str(Path(args[0]).resolve()))
s=bpy.context.scene
a=next(o for o in s.objects if o.type=='ARMATURE')
names=['pelvis','spine_03','head','upperarm_l','lowerarm_l','hand_l','upperarm_r','lowerarm_r','hand_r','thigh_l','calf_l','foot_l','ball_l','thigh_r','calf_r','foot_r','ball_r']
out={'source':str(Path(args[0]).resolve()),'units':'Blender world units; expected metres; verify target scale','limits':'bone endpoint metrics, not mesh/weapon collision, grip or grounded sole proof','takes':{}}
for action in list(bpy.data.actions):
 if not action.name.startswith('HY_'):continue
 a.animation_data.action=action
 if hasattr(action,'slots') and len(action.slots):a.animation_data.action_slot=action.slots[0]
 lo,hi=map(int,action.frame_range); frames=[]
 for f in range(lo,hi+1):
  s.frame_set(f); bpy.context.view_layer.update()
  j={n:list(a.matrix_world @ a.pose.bones[n].head) for n in names if n in a.pose.bones}
  frames.append({'frame':f,'joints':j})
 footlow=min(min(fr['joints'][n][2] for n in ['ball_l','ball_r']) for fr in frames)
 air=[min(fr['joints']['ball_l'][2],fr['joints']['ball_r'][2])-footlow for fr in frames]
 handsep=[math.dist(fr['joints']['hand_l'],fr['joints']['hand_r']) for fr in frames]
 out['takes'][action.name]={'fps':s.render.fps/s.render.fps_base,'frame_count':len(frames),'toe_endpoint_baseline':footlow,'both_toes_above_baseline_max':max(air),'frames_both_toes_over_5cm':sum(v>.05 for v in air),'wrist_separation_min':min(handsep),'wrist_separation_max':max(handsep),'frames':frames}
Path(args[1]).write_text(json.dumps(out,indent=1))
print('BOSSLAB study assessment',json.dumps({k:{n:v for n,v in d.items() if n!='frames'} for k,d in out['takes'].items()}))
