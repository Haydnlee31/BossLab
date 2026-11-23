"""Retarget mannequin clips onto the Bellbreaker's custom-proportion skeleton, 2026-11-18.

Run in the editor AFTER ue_import_bellbreaker_rig.py (which recreates the skeleton, so re-run this too):
./scripts/bosslab-unreal editor unreal/art-studio/source/bellbreaker/ue_retarget_bellbreaker.py
Writes /Game/BossLab/Bellbreaker/Anim (local):
- IK_Manny (source rig on SKM_Manny_Simple) and IK_Bellbreaker (target), both from Unreal's
  auto-generated retarget definition (same mannequin bone names, longer boss arms);
- RTG_MannyToBellbreaker (default op stack: pelvis, FK chains; chains auto-mapped by name);
- retargeted copies of CLIPS (prefix BB_) on SKM_BellbreakerRig_Skeleton.
Also imports the 2026-11-18 HY-Motion hammer batch (artifacts/art/hy-motion-2026-11-18/HY_Anims.fbx,
retarget_motion.py output on SK_Mannequin; Tencent Hunyuan licence, local) to /Game/BossLab/Bellbreaker/HYSource
and retargets those too. Presentation/preview only: no moves, AI or gameplay. Report -> artifacts/art/bellbreaker-boss-2026-11-18/retarget-report.json.
"""
import json, os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
OUT = os.path.join(ROOT, 'artifacts/art/bellbreaker-boss-2026-11-18')
os.makedirs(OUT, exist_ok=True)
DEST = '/Game/BossLab/Bellbreaker/Anim'
SOURCE_MESH = '/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple'
TARGET_MESH = '/Game/BossLab/Bellbreaker/Rig/SKM_BellbreakerRig'
CLIPS = [
    '/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle',
    '/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd',
    '/Game/BossLab/Anim/UAL/UAL_Anims_root_UAL_Idle_Loop',
    '/Game/BossLab/Anim/UAL/UAL_Anims_root_UAL_Walk_Loop',
    '/Game/BossLab/Anim/UAL/UAL_Anims_root_UAL_Sword_Idle',
    '/Game/BossLab/Anim/UAL/UAL_Anims_root_UAL_Sword_Heavy_Combo',
    '/Game/BossLab/Anim/UAL/UAL_Anims_root_UAL_Sword_Attack',
    '/Game/BossLab/Anim/UAL/UAL_Anims_root_UAL_Hit_Knockback',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_cut_heavy_s0',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_stalk_s0',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_strafe_s0',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_stagger_s0',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_hit_heavy_s0',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_death_s0',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_jump_attack_s0',
    '/Game/BossLab/Anim/HY/HY_Anims_root_HY_cast_s0',
]
HAMMER_FBX = os.path.join(ROOT, 'artifacts/art/hy-motion-2026-11-18/HY_Anims.fbx')
HAMMER_SRC = '/Game/BossLab/Bellbreaker/HYSource'
tools = unreal.AssetToolsHelpers.get_asset_tools()
eal = unreal.EditorAssetLibrary
report = {'steps': []}

def note(k, v):
    report['steps'].append([k, v]); unreal.log(f'BOSSLAB retarget {k}: {v}')

def methods(obj):
    return [m for m in dir(obj) if not m.startswith('_')]

def call(obj, names, *args):
    """First method in `names` that exists; returns (name, result)."""
    for n in names:
        if hasattr(obj, n):
            return n, getattr(obj, n)(*args)
    raise AttributeError(f'none of {names} on {type(obj).__name__}: {methods(obj)}')

try:
    if eal.does_directory_exist(DEST):
        eal.delete_directory(DEST)
    if os.path.exists(HAMMER_FBX):
        if eal.does_directory_exist(HAMMER_SRC):
            eal.delete_directory(HAMMER_SRC)
        ui = unreal.FbxImportUI()
        ui.import_mesh = False; ui.import_as_skeletal = True; ui.import_animations = True
        ui.import_materials = False; ui.import_textures = False
        ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_ANIMATION
        ui.skeleton = unreal.load_asset('/Game/Characters/Mannequins/Meshes/SK_Mannequin')
        ad = ui.anim_sequence_import_data
        ad.set_editor_property('animation_length', unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        ad.set_editor_property('import_bone_tracks', True)
        ad.set_editor_property('remove_redundant_keys', False)
        t = unreal.AssetImportTask()
        t.filename = HAMMER_FBX; t.destination_path = HAMMER_SRC; t.automated = True; t.replace_existing = True; t.save = True; t.options = ui
        tools.import_asset_tasks([t])
        hy = sorted(str(a) .split('.')[0] for a in eal.list_assets(HAMMER_SRC, recursive=False))
        hy = [a for a in hy if isinstance(unreal.load_asset(a), unreal.AnimSequence)]
        eal.save_directory(HAMMER_SRC, only_if_is_dirty=False, recursive=True)   # sources (the player stun clips are used directly)
        CLIPS.extend(hy)
        note('hammer_import', hy)
    src_mesh = unreal.load_asset(SOURCE_MESH); tgt_mesh = unreal.load_asset(TARGET_MESH)
    assert src_mesh and tgt_mesh, 'meshes missing'

    def make_rig(name, mesh):
        rig = tools.create_asset(name, DEST, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
        c = unreal.IKRigController.get_controller(rig)
        c.set_skeletal_mesh(mesh)
        n, r = call(c, ['apply_auto_generated_retarget_definition', 'apply_auto_generated_retarget_definition_to_rig'])
        chains = []
        try:
            chains = [str(ch.get_editor_property('chain_name')) for ch in c.get_retarget_chains()]
        except Exception as e:
            chains = ['?', str(e)]
        try:
            root = str(c.get_retarget_root())
        except Exception:
            root = '?'
        note(name, {'auto': n, 'result': str(r), 'root': root, 'chains': chains})
        return rig

    src_rig = make_rig('IK_Manny', src_mesh)
    tgt_rig = make_rig('IK_Bellbreaker', tgt_mesh)

    rtg = tools.create_asset('RTG_MannyToBellbreaker', DEST, unreal.IKRetargeter, unreal.IKRetargetFactory())
    rc = unreal.IKRetargeterController.get_controller(rtg)
    S, T = unreal.RetargetSourceOrTarget.SOURCE, unreal.RetargetSourceOrTarget.TARGET
    rc.set_ik_rig(S, src_rig); rc.set_ik_rig(T, tgt_rig)
    try:
        rc.set_preview_mesh(S, src_mesh); rc.set_preview_mesh(T, tgt_mesh)
    except Exception as e:
        note('preview_mesh', str(e))
    if hasattr(rc, 'add_default_ops'):
        rc.add_default_ops()
        if hasattr(rc, 'assign_ik_rig_to_all_ops'):
            rc.assign_ik_rig_to_all_ops(S, src_rig); rc.assign_ik_rig_to_all_ops(T, tgt_rig)
        try:
            note('ops', [str(rc.get_op_name(i)) for i in range(rc.get_num_retarget_ops())])
        except Exception as e:
            note('ops', 'listed? ' + str(e))
    try:
        rc.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
        note('auto_map', 'exact')
    except Exception as e:
        note('auto_map', 'failed: ' + str(e))
    eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)

    clips = [unreal.EditorAssetLibrary.find_asset_data(p) for p in CLIPS if eal.does_asset_exist(p)]
    note('clips_found', len(clips))
    B = unreal.IKRetargetBatchOperation
    try:
        res = B.duplicate_and_retarget(clips, src_mesh, tgt_mesh, rtg, '', '', 'BB_', '', True, True, True)
    except TypeError:
        res = B.duplicate_and_retarget(clips, src_mesh, tgt_mesh, rtg, '', '', 'BB_', '')
    made = [str(a.get_editor_property('package_name')) for a in res] if res else []
    # Batch duplicates land next to the source by default; move them under DEST.
    moved = []
    for p in made:
        name = p.rsplit('/', 1)[1]
        if not p.startswith(DEST):
            dst = f'{DEST}/{name}'
            if eal.rename_asset(p, dst):
                p = dst
        a = unreal.load_asset(p)
        if isinstance(a, unreal.AnimSequence):
            moved.append({'asset': p, 'skeleton': a.get_editor_property('skeleton').get_name(),
                          'seconds': round(a.get_play_length(), 2)})
    note('retargeted', moved)
    eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
    report['ok'] = len(moved) > 0
except Exception as e:
    import traceback
    report['ok'] = False; report['error'] = traceback.format_exc()
    unreal.log_error('BOSSLAB retarget failed ' + str(e))
json.dump(report, open(os.path.join(OUT, 'retarget-report.json'), 'w'), indent=1)
unreal.log('BOSSLAB retarget done ' + json.dumps({'ok': report.get('ok')}))
unreal.SystemLibrary.quit_editor()
