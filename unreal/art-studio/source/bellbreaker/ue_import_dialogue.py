"""Import the three spoken encounter lines into their own Unreal sound bank."""
from pathlib import Path
import wave

import unreal

source = Path(__file__).resolve().parents[4] / "artifacts/bellbreaker-fury"
destination = "/Game/BossLab/Bellbreaker/Dialogue"
library = unreal.EditorAssetLibrary
library.make_directory(destination)
for cue in ("Challenge", "PhaseBreak", "Defeat"):
    path = source / (cue + ".wav")
    assert path.is_file(), path
    name = "S_BB_" + cue
    task = unreal.AssetImportTask()
    task.filename = str(path)
    task.destination_path = destination
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    assert task.imported_object_paths, cue
    sound = library.load_asset(destination + "/" + name)
    with wave.open(str(path)) as take:
        expected = take.getnframes() / take.getframerate()
    assert sound and abs(sound.get_editor_property("duration") - expected) < 0.02, cue
    sound.set_editor_property("looping", False)
    assert library.save_loaded_asset(sound, False), cue
unreal.log("BOSSLAB imported spoken forge lines 3/3")
