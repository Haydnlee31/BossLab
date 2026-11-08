"""Create original compact BossLab surface assets with installed editor APIs."""
import json
from pathlib import Path
import unreal
directory = '/Game/BossLab/Materials'
tools = unreal.AssetToolsHelpers.get_asset_tools()
edit = unreal.MaterialEditingLibrary
name = directory + '/M_WardenSurface'
material = unreal.load_asset(name) if unreal.EditorAssetLibrary.does_asset_exist(name) else None
if not material:
    material = tools.create_asset('M_WardenSurface', directory, unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property('two_sided', True)
    for parameter, default, property_name, vector in [
        ('Color', unreal.LinearColor(.12,.14,.17,1), unreal.MaterialProperty.MP_BASE_COLOR, True),
        ('Glow', unreal.LinearColor(0,0,0,1), unreal.MaterialProperty.MP_EMISSIVE_COLOR, True),
        ('Roughness', .7, unreal.MaterialProperty.MP_ROUGHNESS, False),
        ('Metallic', .3, unreal.MaterialProperty.MP_METALLIC, False),
    ]:
        expression = edit.create_material_expression(material, unreal.MaterialExpressionVectorParameter if vector else unreal.MaterialExpressionScalarParameter)
        expression.set_editor_property('parameter_name', parameter)
        expression.set_editor_property('default_value', default)
        assert edit.connect_material_property(expression, '', property_name)
    edit.set_base_material_usage(material, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
    edit.set_base_material_usage(material, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
    errors = edit.recompile_material(material)
    assert not errors, str(errors)
    assert unreal.EditorAssetLibrary.save_loaded_asset(material)
palette = {
    'Stone': ((.075,.09,.105), .93, .05, (0,0,0)),
    'DarkStone': ((.022,.03,.04), .88, .05, (0,0,0)),
    'Iron': ((.13,.16,.19), .42, .8, (0,0,0)),
    'BlackIron': ((.035,.045,.055), .5, .75, (0,0,0)),
    'Bronze': ((.31,.19,.065), .38, .8, (0,0,0)),
    'Cloth': ((.025,.105,.12), .96, 0, (0,0,0)),
    'Amber': ((.6,.23,.035), .4, .4, (2.2,.5,.045)),
    'Jade': ((.08,.34,.3), .4, .3, (.1,.7,.52)),
}
saved = []
for short, (color, roughness, metallic, glow) in palette.items():
    asset_name = 'MI_' + short
    path = directory + '/' + asset_name
    instance = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else tools.create_asset(asset_name, directory, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    edit.set_material_instance_parent(instance, material)
    edit.set_material_instance_vector_parameter_value(instance, 'Color', unreal.LinearColor(*color, 1))
    edit.set_material_instance_vector_parameter_value(instance, 'Glow', unreal.LinearColor(*glow, 1))
    edit.set_material_instance_scalar_parameter_value(instance, 'Roughness', roughness)
    edit.set_material_instance_scalar_parameter_value(instance, 'Metallic', metallic)
    actual = edit.get_material_instance_vector_parameter_value(instance, 'Color')
    assert abs(actual.r-color[0]) < .0001 and abs(actual.g-color[1]) < .0001
    assert abs(edit.get_material_instance_scalar_parameter_value(instance, 'Roughness')-roughness) < .0001
    assert unreal.EditorAssetLibrary.save_loaded_asset(instance)
    saved.append(path)
root = Path(unreal.Paths.project_dir()).resolve().parents[1]
(root / 'artifacts/unreal/surface-assets.json').write_text(json.dumps({'parent': name, 'saved': saved, 'palette': palette}, indent=2))
unreal.log('BossLab original surface assets saved')

for source in sorted((Path(unreal.Paths.project_dir()) / 'SourceAudio').glob('*.wav')):
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', str(source))
    task.set_editor_property('destination_path', '/Game/BossLab/Audio')
    task.set_editor_property('automated', True)
    task.set_editor_property('save', True)
    task.set_editor_property('replace_existing', True)
    tools.import_asset_tasks([task])
    assert task.get_editor_property('imported_object_paths'), str(source)
