#!/usr/bin/env python3
"""Check an actual Unreal four-attack capture made with BOSSLAB_BELL_AUDIT=1."""
import argparse
import json
import re
from pathlib import Path
from statistics import median

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("log", type=Path)
options = parser.parse_args()
log = options.log.read_text()
rows = [dict((key, float(value)) for key, value in re.findall(r"(\w+)=(-?[\d.]+)", line))
        for line in log.splitlines() if "BOSSLAB bellmesh move=" in line]
soles = [min(float(left), float(right)) for left, right in
         re.findall(r"BOSSLAB sole .*? left=([-\d.]+) right=([-\d.]+)", log)]
errors = [float(v) for v in re.findall(r"BOSSLAB bell path move \d+ age [\d.]+ error ([\d.]+)", log)]
complete = set(re.findall(r"BELLBREAKER study after ([^:]+):", log))
both = sum(r["left"] > 0 and r["right"] > 0 for r in rows)
checks = {
    "four_attacks_reviewed": complete == {"HAMMER FALL", "FORGE SWEEP", "BELL QUAKE", "THE BELL BREAKS"},
    "rendered_mesh_measured": len(rows) >= 600 and len(soles) == len(rows),
    "active_melee_agrees_with_visible_bell": bool(errors) and max(errors) <= .1,
    "both_hands_on_haft": bool(rows) and both == len(rows),
    "head_and_legs_clear": bool(rows) and all(r["head"] == r["leg"] == 0 for r in rows),
    "support_boot_near_floor": bool(soles) and max(abs(height) for height in soles) < 2,
}
print(json.dumps({
    "checks": checks, "poses": len(rows), "two_hands_touching": both,
    "lower_boot_world_z_cm": [min(soles), median(soles), max(soles)] if soles else [],
    "crossing_poses": {key: sum(row[key] > 0 for row in rows)
                      for key in ("head", "torso", "leg", "upper", "forearm")},
}, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
