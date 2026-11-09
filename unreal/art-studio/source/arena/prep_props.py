"""Convert the CC0 Poly Haven glTF props into game-ready FBX pieces for Unreal.

Run with the project-local Blender:
  unreal/art-studio/tools/Blender.app/Contents/MacOS/Blender -b --python \
      unreal/art-studio/source/arena/prep_props.py -- artifacts/art/arena-dungeon-2026-11-09/props
Per piece: join its parts, apply transforms, pivot at base centre, optional decimation, then
<props>/fbx/<piece>.fbx. Writes <props>/fbx/pieces.json (size, triangles, materials) and
materials.json (material -> base colour / OpenGL normal / ARM-or-roughness texture paths).
The project disables engine plugins by default, so Unreal has no glTF importer here; FBX
static-mesh import works headless.
"""
import bpy, json, os, sys

PROPS = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
OUT = os.path.join(PROPS, 'fbx')
os.makedirs(OUT, exist_ok=True)

# piece -> (asset, object names to join, target triangles or None)
PIECES = {
    'SM_Statue': ('gothic_statue', ['gothic_statue'], None),
    'SM_CastleDoor': ('large_castle_door', ['large_castle_door_frame', 'large_castle_door_left', 'large_castle_door_right'], None),
    'SM_IronGate': ('large_iron_gate', ['large_iron_gate', 'large_iron_gate_left_door', 'large_iron_gate_right_door', 'large_iron_gate_bolt'], 20000),
    'SM_KiteShield': ('kite_shield', ['kite_shield_body', 'kite_shield_metal_trim', 'kite_shield_clamps_and_bolts'], None),
    'SM_Mace': ('ornate_medieval_mace', ['ornate_medieval_mace'], 6000),
    'SM_WarHammer': ('ornate_war_hammer', ['ornate_war_hammer'], None),
    'SM_Estoc': ('antique_estoc', ['antique_estoc'], None),
    'SM_CandleSmall': ('brass_candleholders', ['brass_candleholder_01'], None),
    'SM_CandleTriple': ('brass_candleholders', ['brass_candleholder_02'], None),
    'SM_Candelabra': ('brass_candleholders', ['brass_candleholder_03'], 12000),
}
for i in range(1, 7):
    PIECES[f'SM_Rock0{i}'] = ('rock_moss_set_01', [f'rock_moss_set_01_rock0{i}'], 4000)

def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)

def texture_paths(mat):
    found = {}
    if not mat or not mat.use_nodes:
        return found
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image:
            path = os.path.abspath(bpy.path.abspath(node.image.filepath, library=node.image.library))
            name = os.path.basename(path)
            for key, tag in (('diff', '_diff_'), ('nor', '_nor_gl_'), ('arm', '_arm_'), ('rough', '_rough_')):
                if tag in name:
                    found[key] = path
    return found

pieces, materials, loaded = {}, {}, None
for piece, (asset, names, target) in PIECES.items():
    if loaded != asset:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        gltf = [f for f in os.listdir(os.path.join(PROPS, asset)) if f.endswith('.gltf')][0]
        bpy.ops.import_scene.gltf(filepath=os.path.join(PROPS, asset, gltf))
        loaded = asset
        for o in bpy.context.scene.objects:
            for m in getattr(o.data, 'materials', []) or []:
                if m and m.name not in materials:
                    materials[m.name] = texture_paths(m)
    # Duplicate the parts so later pieces from the same asset keep the originals.
    bpy.ops.object.select_all(action='DESELECT')
    parts = []
    for n in names:
        src = bpy.data.objects[n]
        dup = src.copy(); dup.data = src.data.copy(); dup.parent = None
        dup.matrix_world = src.matrix_world.copy()
        bpy.context.scene.collection.objects.link(dup)
        parts.append(dup)
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    if len(parts) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    before = tris(obj)
    if target and before > target:
        mod = obj.modifiers.new('decimate', 'DECIMATE'); mod.ratio = target / before
        bpy.ops.object.modifier_apply(modifier=mod.name)
    # Pivot at the base centre so placement in Unreal is "stand it on the floor here".
    xs = [v.co.x for v in obj.data.vertices]; ys = [v.co.y for v in obj.data.vertices]; zs = [v.co.z for v in obj.data.vertices]
    base = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs))
    for v in obj.data.vertices:
        v.co.x -= base[0]; v.co.y -= base[1]; v.co.z -= base[2]
    obj.location = (0, 0, 0); obj.name = piece
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, piece + '.fbx'), use_selection=True,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
                             mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False,
                             path_mode='STRIP', embed_textures=False)
    pieces[piece] = {'asset': asset, 'size_m': [round(v, 3) for v in obj.dimensions],
                     'triangles_source': before, 'triangles': tris(obj),
                     'materials': [m.name for m in obj.data.materials if m]}
    bpy.data.objects.remove(obj)

json.dump(pieces, open(os.path.join(OUT, 'pieces.json'), 'w'), indent=1)
json.dump(materials, open(os.path.join(OUT, 'materials.json'), 'w'), indent=1)
print('BOSSLAB props prepared', len(pieces))
