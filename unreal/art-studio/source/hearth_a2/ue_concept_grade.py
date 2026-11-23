"""Hearth A2 concept pass (2026-11-17): soot, grime and damp toward the approved concept board.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/hearth_a2/ue_concept_grade.py
(the script quits the editor; the launcher's exit 1 is expected). A2 materials only, no geometry.
Each touched material's .uasset is backed up once to
artifacts/art/hearth-a2-dressing-2026-11-17/material-backup/ (copy back to restore). Idempotent:
a material already wrapped (its base colour comes from a node described 'BOSSLAB_GRADE') is skipped.

What it adds (world-space, so it reads across module seams):
- walls/vault/generated props: soot that deepens with height and around the furnace mouth, slight
  desaturation; the concept's stone is dark and smoke-stained, the imported stone was clean beige.
- floor: darker, cooler stone with blotchy grime and damp patches (lower roughness, darker colour) so
  the furnace and lanterns leave highlights on it, as the concept's wet flags do.
- oak: darkened (the board's charred timber).
Emissive, water, window and molten materials are not touched.
"""
import json, shutil
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[4]
CONTENT = ROOT / 'unreal/BossLabWarden/Content/BossLab/HearthA2'
BACKUP = ROOT / 'artifacts/art/hearth-a2-dressing-2026-11-17/material-backup'
BACKUP.mkdir(parents=True, exist_ok=True)
D = '/Game/BossLab/HearthA2/'
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
MP = unreal.MaterialProperty

# Custom nodes cannot declare functions; inline value noise as a macro-free block instead.
def noise(expr):
    return ('(lerp(lerp(frac(sin(dot(floor({e}),float2(127.1,311.7)))*43758.5453),frac(sin(dot(floor({e})+float2(1,0),float2(127.1,311.7)))*43758.5453),smoothstep(0,1,frac({e}).x)),'
            'lerp(frac(sin(dot(floor({e})+float2(0,1),float2(127.1,311.7)))*43758.5453),frac(sin(dot(floor({e})+float2(1,1),float2(127.1,311.7)))*43758.5453),smoothstep(0,1,frac({e}).x)),smoothstep(0,1,frac({e}).y)))').format(e=expr)

FURNACE = 'float2(420,950)'
WALL = ('float soot=saturate((P.z-120)/700)*.55+saturate(1-length(P.xy-' + FURNACE + ')/650)*.35;'
        'float g=' + noise('P.xz*.006+P.yz*.004') + ';'
        'soot=saturate(soot*(.7+.6*g)+.12);'
        'float3 grey=dot(C,float3(.3,.59,.11));'
        'float3 c=lerp(C,grey,.25)*float3(.86,.82,.8);'
        'return c*(1-soot)*K;')
FLOOR = ('float g=' + noise('P.xy*.004') + '*.6+' + noise('P.xy*.017') + '*.4;'
         'float damp=saturate((' + noise('P.xy*.0025+float2(7,3)') + '-.5)*3.5);'
         'float3 grey=dot(C,float3(.3,.59,.11));'
         'float3 c=lerp(C,grey,.35)*float3(.62,.6,.6);'
         'c*=lerp(.75,1.05,g);c*=1-.35*damp;'
         'c*=1-.3*saturate(1-length(P.xy-' + FURNACE + ')/700);'
         'return c;')
FLOOR_ROUGH = ('float damp=saturate((' + noise('P.xy*.0025+float2(7,3)') + '-.5)*3.5);'
               'return lerp(min(R,.78),.22,damp);')

def described(node):
    try:
        return 'BOSSLAB_GRADE' in (node.get_editor_property('desc') or '')
    except Exception:
        return False

def wrap(mat, prop, code, extra_inputs, k=None):
    """Insert a custom node between whatever feeds `prop` and the property."""
    src = mel.get_material_property_input_node(mat, prop)
    if src is None:
        return 'no input'
    if described(src):
        return 'already'
    try:
        out = mel.get_material_property_input_node_output_name(mat, prop)
    except Exception:
        out = ''
    node = mel.create_material_expression(mat, unreal.MaterialExpressionCustom, -200, 0)
    node.set_editor_property('desc', 'BOSSLAB_GRADE')
    pins = []
    for name in ['C' if prop == MP.MP_BASE_COLOR else 'R'] + extra_inputs:
        p = unreal.CustomInput(); p.set_editor_property('input_name', name); pins.append(p)
    node.set_editor_property('inputs', pins)
    node.set_editor_property('code', code)
    node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3 if prop == MP.MP_BASE_COLOR else unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    mel.connect_material_expressions(src, out, node, 'C' if prop == MP.MP_BASE_COLOR else 'R')
    if 'P' in extra_inputs:
        pos = mel.create_material_expression(mat, unreal.MaterialExpressionWorldPosition, -500, 0)
        mel.connect_material_expressions(pos, '', node, 'P')
    if 'K' in extra_inputs:
        kk = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -500, 100)
        kk.set_editor_property('r', k)
        mel.connect_material_expressions(kk, '', node, 'K')
    mel.connect_material_property(node, '', prop)
    return 'wrapped'

groups = {
    'floor': [f'M_A2_worn_floor_stone_{i}' for i in range(6)],
    'wall': ['M_A2_weathered_masonry_0', 'M_A2_weathered_masonry_1', 'M_A2_deep_charcoal_mortar'] + [f'M_A2_cut_stone_value_{i}' for i in range(5)],
    'prop': ['M_A2_Material_0'] + [f'M_A2_Material_0_{i:03d}' for i in range(1, 10)] + ['M_A2_forged_iron', 'M_A2_faded_oxblood', 'M_A2_rough_hemp_rope'],
    'oak': ['M_A2_aged_oak', 'M_A2_exposed_cut_oak_end'],
}
report = {}
for group, names in groups.items():
    for name in names:
        mat = unreal.load_asset(D + name)
        if not isinstance(mat, unreal.Material):
            report[name] = 'missing'; continue
        src = CONTENT / (name + '.uasset')
        if src.exists() and not (BACKUP / src.name).exists():
            shutil.copy2(src, BACKUP / src.name)
        if group == 'floor':
            r = [wrap(mat, MP.MP_BASE_COLOR, FLOOR, ['P']), wrap(mat, MP.MP_ROUGHNESS, FLOOR_ROUGH, ['P'])]
        elif group == 'wall':
            r = [wrap(mat, MP.MP_BASE_COLOR, WALL, ['P', 'K'], 1.0)]
        elif group == 'prop':
            r = [wrap(mat, MP.MP_BASE_COLOR, WALL, ['P', 'K'], .9)]
        else:
            r = [wrap(mat, MP.MP_BASE_COLOR, WALL, ['P', 'K'], .7)]
        mel.recompile_material(mat)
        eal.save_loaded_asset(mat)
        report[name] = r
out = ROOT / 'artifacts/art/hearth-a2-dressing-2026-11-17/concept-grade-report.json'
out.write_text(json.dumps(report, indent=1))
unreal.log('BOSSLAB concept grade ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
