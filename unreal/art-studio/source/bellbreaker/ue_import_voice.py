"""Non-destructive import of original forge-only vocal gestures and furnace bed."""
from pathlib import Path
import unreal
src=Path(__file__).resolve().parents[4]/'artifacts/bellbreaker-voice'
names=('HeaveA','HeaveB','ReleaseA','ReleaseB','BreakRoar','DeathBreath','forge_breath_v0')
dst='/Game/BossLab/Bellbreaker/Voice'
for n in names: assert (src/(n+'.wav')).is_file(),n
tools=unreal.AssetToolsHelpers.get_asset_tools();unreal.EditorAssetLibrary.make_directory(dst)
for n in names:
 task=unreal.AssetImportTask(); task.filename=str(src/(n+'.wav'));task.destination_path=dst;task.destination_name='S_BB_'+n
 task.replace_existing=True;task.automated=True;task.save=False
 tools.import_asset_tasks([task]);a=unreal.load_asset(dst+'/S_BB_'+n)
 assert a and a.get_editor_property('duration')>.2,n
 a.set_editor_property('looping',n=='forge_breath_v0')
 if n=='forge_breath_v0': a.set_editor_property('virtualization_mode',unreal.VirtualizationMode.PLAY_WHEN_SILENT)
 assert unreal.EditorAssetLibrary.save_loaded_asset(a,False),n
unreal.log('BOSSLAB FORGE VOICE imported 7/7')
