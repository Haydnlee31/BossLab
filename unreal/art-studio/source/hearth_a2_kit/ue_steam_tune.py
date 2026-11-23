"""Re-applies the current M_A2_Steam opacity/colour from ue_import_kit.py without re-importing the kit."""
import re, unreal
from pathlib import Path
src = (Path(__file__).parent / 'ue_import_kit.py').read_text()
code_ret = re.search(r"'(return \(\.18.*?;)'", src).group(1)
mel = unreal.MaterialEditingLibrary
m = unreal.load_asset('/Game/BossLab/HearthA2/Kit/M_A2_Steam')
done = []
fade = mel.get_material_property_input_node(m, unreal.MaterialProperty.MP_OPACITY)
custom = mel.get_inputs_for_material_expression(m, fade)[0] if fade else None
if custom:
    c = custom.get_editor_property('code'); c = re.sub(r'return .*;$', code_ret, c); custom.set_editor_property('code', c); done.append('opacity')
col = mel.get_material_property_input_node(m, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
if col: col.set_editor_property('constant', unreal.LinearColor(1.1, 1.12, 1.18, 1)); done.append('colour')
mel.recompile_material(m); unreal.EditorAssetLibrary.save_loaded_asset(m)
unreal.log('BOSSLAB steam tuned ' + ','.join(done))
unreal.SystemLibrary.quit_editor()
