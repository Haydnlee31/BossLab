"""Generate Bellbreaker's alternate performance as a single cast-and-directed take."""
from pathlib import Path
import shutil
from gradio_client import Client

OUT = Path(__file__).resolve().parents[4] / 'artifacts/bellbreaker-fury'
LINES = ("You came for my bell? LIFT IT!", "You CRACKED her! She was ALL I HAD!", "Ring on.")
DIRECTION = (
    "Perform a dramatic VIDEO GAME BOSS confrontation in English. One battle-scarred male "
    "blacksmith in his fifties with a massive barrel chest, a booming weathered low baritone, "
    "gritty voiced consonants and fierce physical projection. Dry studio recording. "
    "His bell is the last thing his lost apprentice made with him. In the FIRST speech he "
    "challenges an intruder with blazing contempt, then bellows LIFT IT across a roaring forge. "
    "Long beat. In the SECOND speech, seeing the bell crack stuns him. CRACKED bursts out in shock. "
    "His grief surges into a full-throated furious SHOUT on ALL I HAD, leaning hard on HAD. "
    "Long beat. In the LAST two words the dying smith talks to his bell, a short fierce command, "
    "quiet but still strong. Different volume levels, real breaths at the beats. Keep the same "
    "male British voice throughout. Speak only the script, clear words, no nonverbal roars."
)

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True, parents=True)
    output = OUT / 'performance.wav'
    if output.exists():
        raise SystemExit('Selected performance already exists.')
    c = Client('Qwen/Qwen3-TTS', token=False, verbose=False)
    source, status = c.predict(text='\n\n'.join(LINES), language='English',
                               voice_description=DIRECTION, api_name='/generate_voice_design')
    if not source:
        raise RuntimeError(status)
    shutil.copyfile(source, output)
    print(status)
