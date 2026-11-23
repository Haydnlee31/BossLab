#!/usr/bin/env python3
"""Summarize support-foot heights in an Unreal Bellbreaker pursuit/footwork study."""
import json
import re
import statistics
import sys
from pathlib import Path


def fields(line):
    return dict(re.findall(r'(\w+)=([-\d.]+)', line))


def sample_heights(log):
    phases = [fields(row) for row in log if 'BOSSLAB gait phase=' in row]
    boots = [fields(row) for row in log if 'BOSSLAB sole move=' in row]
    if len(boots) != len(phases) or not boots:
        raise ValueError('Expected one skinned boot sample for each gait sample')
    single, grounded, active = [], [], []
    for index,(phase,boot) in enumerate(zip(phases,boots)):
        if phase['active'] != '1' or float(phase['enter']) < .99:
            continue
        left, right = float(boot['left']), float(boot['right'])
        grounded.append(min(left,right))
        active.append(index)
        supports = (phase['support_l']=='1',phase['support_r']=='1')
        if sum(supports)==1:
            single.append(left if supports[0] else right)
    if not single:
        raise ValueError('No established single-support samples')
    def distribution(data):
        return {'median':round(statistics.median(data),2),
                'p95':round(statistics.quantiles(data,n=100,method='inclusive')[94],2),
                'max':round(max(data),2)}
    return {'established_gait_samples':len(active),'single_support_samples':len(single),
            'lowest_visible_tread_cm':distribution(grounded),
            'support_boot_lowest_visible_tread_cm':distribution(single),
            'support_boot_over_5cm':sum(v>5 for v in single),
            'both_boots_over_5cm':sum(v>5 for v in grounded),
            'scope':'Skinned boot vertices in the lowest 8 cm of the bind mesh, settled gait only, 30 Hz. The other boot may be in swing.'}


if __name__=='__main__':
    print(json.dumps(sample_heights(Path(sys.argv[1]).read_text().splitlines()),indent=2))
