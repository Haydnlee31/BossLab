#!/usr/bin/env python3
"""Detect gross wrist reversals in an instrumented 30 fps Unreal four-attack capture.

Usage: python3 scripts/review-bellbreaker-grip.py capture.log
BOSSLAB_BELL_AUDIT=1 supplies per-rendered-frame shaft transforms and knuckle axes.
"""
import json
import math
import re
import sys
from pathlib import Path


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def unit(v):
    length = math.sqrt(dot(v, v))
    if not .98 < length < 1.02:
        raise ValueError(f'Missing or invalid unit axis {v}')
    return tuple(x/length for x in v)


def in_weapon_space(v, q):
    # Inverse unit-quaternion rotation, from mesh component space into haft space.
    xyz = tuple(-x for x in q[:3])
    t = tuple(2*x for x in cross(xyz, v))
    return unit(tuple(a+q[3]*b+c for a, b, c in zip(v, t, cross(xyz, t))))


def degrees(a, b):
    return math.degrees(math.acos(max(-1, min(1, dot(a, b)))))


def vector(fields, key):
    return unit(tuple(map(float, fields[key].split(','))))


def review(path, combat=False):
    # Unreal stamps each line when it flushes. A late skin-probe line can
    # acquire the following frame's prefix. Group by ordered pose emission
    # (right hand, left hand, weapon) and check the move/age independently.
    frames = {}
    coverage = []
    pair = {}
    log=path.read_text()
    if combat and 'BOSSLAB footwork frame=' not in log:
        raise ValueError('Expected a player-camera combat route')
    for line in log.splitlines():
        if 'BOSSLAB grip coverage ' in line:
            coverage.append(dict(re.findall(r'(\w+)=([-\d]+)',line)))
        if 'BOSSLAB anatomy ' not in line and 'BOSSLAB bellmesh move=' not in line:
            continue
        fields = dict(re.findall(r'(\w+)=([\w.,-]+)', line))
        key = fields.get('side', 'weapon')
        if key in pair or (key == 'weapon' and pair.keys() != {'L','R'}):
            raise ValueError('Missing or duplicate records inside a single pose')
        pair[key] = fields
        if key == 'weapon':
            for side in ('L','R'):
                if fields['move'] != pair[side]['move'] or abs(float(fields['age'])-float(pair[side]['age']))>1.01:
                    raise ValueError('Hand and weapon timestamps disagree')
            frames[len(frames)+1] = pair
            pair = {}
    expected_count=542 if combat else 662
    if pair or len(frames) != expected_count:
        raise ValueError(f'Expected {expected_count} complete poses including warmup and exit')
    moves={int(row['weapon']['move']) for row in frames.values()}
    if not {-1,20,21,22}.issubset(moves) or (not combat and 23 not in moves):
        raise ValueError(f'Missing expected attacks and carry. Observed indices {moves}')
    result = {}
    for side in ('L','R'):
        last = None
        steps = []
        joint_peaks = {key:(0.,0) for key in ('hand','elbow','shoulder')}
        prior_joints = None
        wrist_angles = []
        grip_alignment = []
        for frame, pair in frames.items():
            q = vector(pair['weapon'], 'quat')
            basis = [in_weapon_space(vector(pair[side], key), q) for key in ('normal','span')]
            joints={key:vector(pair[side],key) for key in joint_peaks}
            if prior_joints:
                for key,current in joints.items():
                    change=2*math.degrees(math.acos(min(1.,abs(dot(prior_joints[key],current)))))
                    joint_peaks[key]=max(joint_peaks[key],(change,frame))
            prior_joints=joints
            wrist = joints['hand']
            wrist_angles.append(2*math.degrees(math.acos(min(1,abs(wrist[3])))))
            signed = dot(vector(pair[side], 'span'), vector(pair[side], 'shaft'))
            grip_alignment.append(signed if side == 'L' else -signed)
            if last is not None:
                prior_frame, prev = last
                if frame != prior_frame+1:
                    raise ValueError(f'Missing or out-of-order samples at {frame}')
                step = max(degrees(p, v) for p, v in zip(prev, basis))
                steps.append((step, frame, int(pair[side]['move']), float(pair[side]['age'])))
            last = frame, basis
        peak, frame, move, age = max(steps)
        result[side] = dict(poses=len(frames), peak_relative_frame_change_deg=round(peak,2),
                            frame=frame, move=move, action_age=age,
                            quarter_turns=sum(step>=90 for step,*_ in steps),
                            peak_joint_step={key:{'degrees':round(v,2),'pose':f} for key,(v,f) in joint_peaks.items()},
                            peak_wrist_from_rest_deg=round(max(wrist_angles),2),
                            reversed_grip_samples=sum(d<0 for d in grip_alignment))
        if coverage:
            if len(coverage)!=len(frames):
                raise ValueError('Incomplete handle-surface evidence')
            suffix=side.lower()
            digits=[int(row['digits_'+suffix]) for row in coverage]
            sectors=[bin(int(row['sectors_'+suffix])).count('1') for row in coverage]
            result[side]['actual_handle_surface']={
                'thumb_and_finger_contact_poses':sum(bool(d&1 and d&30) for d in digits),
                'three_or_more_fingers_contact_poses':sum(bin(d&30).count('1')>=3 for d in digits),
                'min_contacted_octants':min(sectors),
                'poses_with_contacts_in_four_or_more_octants':sum(n>=4 for n in sectors)}
    return result


if __name__ == '__main__':
    report = review(Path(sys.argv[1]),combat='--combat' in sys.argv[2:])
    print(json.dumps(report, indent=2))
    # Gross one-frame flips, forced backwards grip or extreme wrist rotation
    # relative to this specific fitted neutral wrist.
    # Passing this narrow regression check still requires review at playback speed.
    sys.exit(int(any(side['quarter_turns'] or side['reversed_grip_samples'] or
                     side['peak_wrist_from_rest_deg']>=90 or
                     any(v['degrees']>=60 for v in side['peak_joint_step'].values()) for side in report.values())))
