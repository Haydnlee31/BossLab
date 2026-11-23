"""Build the forge boot contact material. Run with the project-local Unreal python launcher."""
import unreal

folder = '/Game/BossLab/Bellbreaker/FX'
name = 'M_BB_SoleShade'
library = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
library.make_directory(folder)
material = unreal.load_asset(folder+'/'+name) if library.does_asset_exist(folder+'/'+name) else None
if not material:
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
mel.delete_all_material_expressions(material)
material.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
material.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
uv = mel.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -500, 0)
amount = mel.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -500, 180)
amount.set_editor_property('parameter_name', 'Contact')
amount.set_editor_property('default_value', .48)
falloff = mel.create_material_expression(material, unreal.MaterialExpressionCustom, -240, 0)
inputs = []
for pin_name in ['UV','Amount']:
    pin = unreal.CustomInput()
    pin.set_editor_property('input_name', pin_name)
    inputs.append(pin)
falloff.set_editor_property('inputs', inputs)
falloff.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT1)
falloff.set_editor_property('code', 'float r=length(2.0*UV-1.0); return Amount*(1.-smoothstep(.12,.98,r));')
assert mel.connect_material_expressions(uv, '', falloff, 'UV')
assert mel.connect_material_expressions(amount, '', falloff, 'Amount')
assert mel.connect_material_property(falloff, '', unreal.MaterialProperty.MP_OPACITY)
mel.recompile_material(material)
assert library.save_loaded_asset(material, only_if_is_dirty=False)
unreal.log('BOSSLAB boot contact material saved')
