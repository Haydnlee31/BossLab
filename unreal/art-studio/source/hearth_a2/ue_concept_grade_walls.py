"""Hearth A2 concept pass, wall darkening step (2026-11-17): deepen the soot in the walls'
BOSSLAB_GRADE nodes (ue_concept_grade.py); the masonry still read light beige under the lanterns.
Run in the editor after ue_concept_grade.py. Edits node code only; backups from the first script apply."""
import unreal
mel = unreal.MaterialEditingLibrary
D = '/Game/BossLab/HearthA2/'
names = ['M_A2_weathered_masonry_0', 'M_A2_weathered_masonry_1', 'M_A2_deep_charcoal_mortar'] + [f'M_A2_cut_stone_value_{i}' for i in range(5)]
for name in names:
    m = unreal.load_asset(D + name)
    node = mel.get_material_property_input_node(m, unreal.MaterialProperty.MP_BASE_COLOR)
    if node and 'BOSSLAB_GRADE' in (node.get_editor_property('desc') or ''):
        code = node.get_editor_property('code')
        code = code.replace('float3(.86,.82,.8)', 'float3(.66,.62,.6)').replace('+.12);', '+.2);')
        node.set_editor_property('code', code)
        mel.recompile_material(m); unreal.EditorAssetLibrary.save_loaded_asset(m)
unreal.log('BOSSLAB walls darkened')
unreal.SystemLibrary.quit_editor()
