"""Generate a single continuous performance so all three cues share one voice.

Run from the project root with .venv-gen3d/bin/python. Only the original script and
performance direction are sent to the public Hugging Face Space.
"""
import shutil
from pathlib import Path
from gradio_client import Client

OUT = Path(__file__).resolve().parents[4] / 'artifacts/bellbreaker-dialogue'
SPACE = 'Qwen/Qwen3-TTS'
LINES = ("I've buried better steel than that.", "Hear that crack? She'll ring once more.", "Good steel.")
DIRECTION = ("Adult male master blacksmith, about fifty, natural English speaking voice. "
             "Deep resonant chest register, warm worn baritone, rough edges on the consonants. "
             "A man used to being heard over a forge, conversational and close. "
             "First line quietly sizes up a challenger, dry and certain. Long silence. "
             "Second line to his cracking bell, with fierce fond pride. Long silence. "
             "Final two words almost under his breath in sincere admiration. "
             "Clear diction. No grunting, music, effects or narration.")

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True, parents=True)
    output = OUT / 'performance.wav'
    if output.exists():
        raise SystemExit(f"Selected performance already exists at {output}. Choose a new output directory for another take.")
    client = Client(SPACE, token=False, verbose=False)
    source, status = client.predict(text='\n\n'.join(LINES), language='English',
                                    voice_description=DIRECTION, api_name='/generate_voice_design')
    if not source:
        raise RuntimeError(status)
    shutil.copyfile(source, output)
    print(status)
