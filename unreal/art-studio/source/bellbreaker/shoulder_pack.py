from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[4];O=R/'artifacts/art/bellbreaker-shoulder-2026-11-20';f=O/'ForgeShoulder.blend';bpy.ops.wm.open_mainfile(filepath=str(f))
p=R/'artifacts/art/bellbreaker-boss-2026-11-18/rig-v3/out/SKM_BellbreakerRig_BaseColor.png'
im=bpy.data.images.get('BaseColor');im.filepath=str(p);im.reload();im.pack();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(f));bpy.ops.wm.open_mainfile(filepath=str(f));a=json.loads((O/'blender-readback.json').read_text());a['scene_sha256']=hashlib.sha256(f.read_bytes()).hexdigest();a['images']=[{'name':i.name,'packed':bool(i.packed_file),'filepath':i.filepath} for i in bpy.data.images];a['basecolor_restored_from_original']=str(p.relative_to(R));(O/'blender-readback.json').write_text(json.dumps(a,indent=2))
