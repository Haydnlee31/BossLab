"""Import only the original menu score and UI cues; never touch combat sounds.
Run via the project's guarded Unreal python launcher after make_interface_audio.py.
"""
from pathlib import Path
import json
import unreal

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'artifacts/audio-interface-2026-11-14/out'
DEST = '/Game/BossLab/InterfaceAudio'
NAMES = ('MenuMusic_0', 'UIConfirm_0', 'UIAdjust_0')
for name in NAMES:
    if not (SRC / f'{name}.wav').is_file():
        raise RuntimeError(f'Missing interface audio input: {name}')
tasks = []
for name in NAMES:
    task = unreal.AssetImportTask()
    task.filename = str(SRC / f'{name}.wav')
    task.destination_path = DEST
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = False
    tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
# UISound is a SoundClass/AudioComponent flag in UE 5.8, not a SoundWave property.
ui_class = unreal.load_asset(f'{DEST}/SC_Interface')
if ui_class is None:
    ui_class = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        'SC_Interface', DEST, unreal.SoundClass, unreal.SoundClassFactory())
if ui_class is None:
    raise RuntimeError('Could not create interface sound class')
properties = ui_class.get_editor_property('properties')
properties.set_editor_property('is_ui_sound', True)
properties.set_editor_property('reverb', False)
properties.set_editor_property('default2d_reverb_send_amount', 0.0)
ui_class.set_editor_property('properties', properties)
unreal.EditorAssetLibrary.save_loaded_asset(ui_class, only_if_is_dirty=False)
records = []
for name in NAMES:
    sound = unreal.load_asset(f'{DEST}/{name}')
    if not isinstance(sound, unreal.SoundWave):
        raise RuntimeError(f'Interface SoundWave import failed: {name}')
    music = name == 'MenuMusic_0'
    sound.set_editor_property('looping', music)
    sound.set_editor_property('sound_class_object', ui_class)
    if music:
        sound.set_editor_property('virtualization_mode', unreal.VirtualizationMode.PLAY_WHEN_SILENT)
    if not unreal.EditorAssetLibrary.save_loaded_asset(sound, only_if_is_dirty=False):
        raise RuntimeError(f'Interface sound save failed: {name}')
    records.append({'asset': f'{DEST}/{name}', 'looping': bool(sound.get_editor_property('looping')),
                    'is_ui_sound': bool(ui_class.get_editor_property('properties').get_editor_property('is_ui_sound'))})
report = {'imported': records, 'scope': 'Only /Game/BossLab/InterfaceAudio; no directory deletion or combat asset changes.'}
(ROOT / 'artifacts/audio-interface-2026-11-14/import-report.json').write_text(json.dumps(report, indent=2) + '\n')
unreal.log('BOSSLAB interface audio import ' + json.dumps(report))
