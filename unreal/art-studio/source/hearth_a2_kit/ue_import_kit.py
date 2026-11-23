"""Import the Hearth A2 concept-detail kit (build_kit.py) and its materials, 2026-11-17.

Run in the editor: ./scripts/bosslab-unreal editor unreal/art-studio/source/hearth_a2_kit/ue_import_kit.py
(the script quits the editor; the launcher's exit 1 is expected). Writes /Game/BossLab/HearthA2/Kit
(local). Material slots named after existing A2 materials are bound to them; new ones:
- M_Kit_Banner: two-sided masked cloth from T_Kit_Banner (FLUX artwork, aged/tattered in PIL).
- M_A2_Steam: translucent unlit rising vapour for the quench cistern (WardenSmeltery.cpp places it).
Also darkens the stepped furnace's own materials (extra soot; the board's hood is dark, A2's was pale);
backups of those .uasset files go to material-backup/ first.
"""
import json, os, shutil
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[4]
ART = ROOT / 'artifacts/art/hearth-a2-dressing-2026-11-17'
KIT = ART / 'kit'
CONTENT = ROOT / 'unreal/BossLabWarden/Content/BossLab/HearthA2'
D = '/Game/BossLab/HearthA2/'
DEST = D + 'Kit'
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
MP = unreal.MaterialProperty
if eal.does_directory_exist(DEST):
    eal.delete_directory(DEST)

def task(filename, name, options=None):
    t = unreal.AssetImportTask()
    t.filename = str(filename); t.destination_path = DEST; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = False
    if options: t.options = options
    tools.import_asset_tasks([t])
    return unreal.load_asset(f'{DEST}/{name}')

def custom(m, code, inputs, out, x=-400, y=0):
    n = mel.create_material_expression(m, unreal.MaterialExpressionCustom, x, y)
    pins = []
    for k in inputs:
        p = unreal.CustomInput(); p.set_editor_property('input_name', k); pins.append(p)
    n.set_editor_property('inputs', pins); n.set_editor_property('code', code); n.set_editor_property('output_type', out)
    return n

F3, F1 = unreal.CustomMaterialOutputType.CMOT_FLOAT3, unreal.CustomMaterialOutputType.CMOT_FLOAT1

# Banner cloth.
tex = task(KIT / 'T_Kit_Banner.png', 'T_Kit_Banner')
banner = tools.create_asset('M_Kit_Banner', DEST, unreal.Material, unreal.MaterialFactoryNew())
banner.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED); banner.set_editor_property('two_sided', True)
s = mel.create_material_expression(banner, unreal.MaterialExpressionTextureSample, -600, 0); s.set_editor_property('texture', tex)
mel.connect_material_property(s, 'RGB', MP.MP_BASE_COLOR); mel.connect_material_property(s, 'A', MP.MP_OPACITY_MASK)
r = mel.create_material_expression(banner, unreal.MaterialExpressionConstant, -300, 300); r.set_editor_property('r', .92)
mel.connect_material_property(r, '', MP.MP_ROUGHNESS)
mel.recompile_material(banner)

# Quench steam.
steam = tools.create_asset('M_A2_Steam', DEST, unreal.Material, unreal.MaterialFactoryNew())
steam.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
steam.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
steam.set_editor_property('two_sided', True)
pos = mel.create_material_expression(steam, unreal.MaterialExpressionWorldPosition, -900, 0)
tm = mel.create_material_expression(steam, unreal.MaterialExpressionTime, -900, 150)
uv = mel.create_material_expression(steam, unreal.MaterialExpressionTextureCoordinate, -900, 300)
N = ('(lerp(lerp(frac(sin(dot(floor({e}),float2(127.1,311.7)))*43758.5453),frac(sin(dot(floor({e})+float2(1,0),float2(127.1,311.7)))*43758.5453),smoothstep(0,1,frac({e}).x)),'
     'lerp(frac(sin(dot(floor({e})+float2(0,1),float2(127.1,311.7)))*43758.5453),frac(sin(dot(floor({e})+float2(1,1),float2(127.1,311.7)))*43758.5453),smoothstep(0,1,frac({e}).x)),smoothstep(0,1,frac({e}).y)))')
q1 = 'float2(P.x*.013+P.y*.009+sin(P.z*.02+T*.7)*.4,P.z*.011-T*.55)'
q2 = 'float2(P.y*.031-P.x*.017,P.z*.027-T*1.1)'
code = ('float n=' + N.format(e=q1) + '*.65+' + N.format(e=q2) + '*.35;'
        'float edge=smoothstep(0,.25,UV.x)*smoothstep(1,.75,UV.x);'
        'float rise=smoothstep(1,.82,UV.y)*smoothstep(0,.85,UV.y);'
        'return (.3+.7*saturate((n-.2)*1.6))*edge*rise*.9;')
op = custom(steam, code, ['P', 'T', 'UV'], F1)
for node, pin in ((pos, 'P'), (tm, 'T'), (uv, 'UV')):
    mel.connect_material_expressions(node, '', op, pin)
fade = mel.create_material_expression(steam, unreal.MaterialExpressionDepthFade, -150, 0)
fade.set_editor_property('fade_distance_default', 25.0)
mel.connect_material_expressions(op, '', fade, 'Opacity'); mel.connect_material_property(fade, '', MP.MP_OPACITY)
col = mel.create_material_expression(steam, unreal.MaterialExpressionConstant3Vector, -300, 300)
col.set_editor_property('constant', unreal.LinearColor(1.5, 1.52, 1.6, 1)); mel.connect_material_property(col, '', MP.MP_EMISSIVE_COLOR)
mel.recompile_material(steam)

# Meshes.
report = {}
for name in ['SM_Kit_Floor', 'SM_Kit_Chains', 'SM_Kit_Timber', 'SM_Kit_Banners']:
    ui = unreal.FbxImportUI()
    ui.import_mesh = True; ui.import_as_skeletal = False; ui.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    ui.import_materials = False; ui.import_textures = False; ui.import_animations = False
    sm = ui.static_mesh_import_data
    sm.set_editor_property('combine_meshes', True); sm.set_editor_property('import_uniform_scale', 100.0)
    sm.set_editor_property('auto_generate_collision', False); sm.set_editor_property('generate_lightmap_u_vs', False)
    sm.set_editor_property('normal_import_method', unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    mesh = task(KIT / (name + '.fbx'), name, ui)
    if mesh is None:
        report[name] = 'missing'; continue
    slots, bound = [], []
    for slot in mesh.get_editor_property('static_materials'):
        sname = str(slot.get_editor_property('material_slot_name'))
        m = unreal.load_asset(D + sname) or unreal.load_asset(f'{DEST}/{sname}')
        if m: slot.set_editor_property('material_interface', m); bound.append(sname)
        slots.append(slot)
    mesh.set_editor_property('static_materials', slots)
    box = mesh.get_bounding_box()
    report[name] = {'triangles': mesh.get_num_triangles(0), 'bound': bound,
                    'bounds_cm': [[round(box.min.x), round(box.min.y), round(box.min.z)], [round(box.max.x), round(box.max.y), round(box.max.z)]]}

# Darker, sootier furnace: extra multiplier in its graded materials (ue_concept_grade.py nodes).
backup = ART / 'material-backup'; backup.mkdir(exist_ok=True)
furnace = unreal.load_asset(D + 'SM_A2_generated_SteppedFurnace')
darkened = []
for slot in furnace.get_editor_property('static_materials'):
    m = slot.get_editor_property('material_interface')
    if not isinstance(m, unreal.Material): continue
    node = mel.get_material_property_input_node(m, MP.MP_BASE_COLOR)
    if node and 'BOSSLAB_GRADE' in (node.get_editor_property('desc') or ''):
        code = node.get_editor_property('code')
        if 'FURNACE_SOOT' not in code:
            src = CONTENT / (m.get_name() + '.uasset')
            if src.exists() and not (backup / (src.stem + '-furnace.uasset')).exists():
                shutil.copy2(src, backup / (src.stem + '-furnace.uasset'))
            code = code.replace('return c*(1-soot)*K;', '/*FURNACE_SOOT*/float lip=saturate(1-abs(P.z-120)/90);return c*(1-soot)*K*lerp(.42,.75,lip);')
            node.set_editor_property('code', code); mel.recompile_material(m); eal.save_loaded_asset(m)
        darkened.append(m.get_name())
report['furnace_darkened'] = darkened
eal.save_directory(DEST, only_if_is_dirty=False, recursive=True)
(ART / 'kit-import-report.json').write_text(json.dumps(report, indent=1))
unreal.log('BOSSLAB kit import ' + json.dumps(report))
unreal.SystemLibrary.quit_editor()
