from pathlib import Path
import unreal
p=Path(__file__).resolve().parents[4]/'artifacts/unreal/bellbreaker-weight/anvil-measure.wav'
assert p.is_file()
t=unreal.AssetImportTask(); t.filename=str(p); t.destination_path='/Game/BossLab/Bellbreaker/Score'; t.destination_name='S_BB_AnvilMeasure';t.automated=True;t.replace_existing=True;t.save=False
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
a=unreal.load_asset('/Game/BossLab/Bellbreaker/Score/S_BB_AnvilMeasure')
assert a and abs(a.duration-36)<.05
a.set_editor_property('looping',True)
assert unreal.EditorAssetLibrary.save_loaded_asset(a,False)
unreal.log('BOSSLAB forge score imported 36-second loop')
