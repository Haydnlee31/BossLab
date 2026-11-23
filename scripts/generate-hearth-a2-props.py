"""Finite, sequential official HF Space requests; credential stays in process memory.

Run with project .venv-gen3d Python in a terminal. No paid inference endpoints.
Original inputs must already exist. Outputs are local, not automatic publications.
"""
from pathlib import Path
import getpass, hashlib, json, os, shutil, signal, subprocess, time, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/art/hearth-a2-2026-11-16'
os.environ['GRADIO_TEMP_DIR'] = str(OUT / 'tmp')
SPACE = 'microsoft/TRELLIS.2'

def guard():
    free = shutil.disk_usage(ROOT).free
    used = int(subprocess.check_output(['du', '-sk', str(ROOT / 'unreal')]).split()[0]) * 1024
    if free < 24 * 1024**3 or used >= 10_000_000_000:
        raise RuntimeError('Project storage guard: less than24GiB free or Unreal allocation reached10GB')
    return {'free_bytes': free, 'unreal_allocated_bytes': used}

def path_of(value):
    if isinstance(value, dict):
        return value.get('path') or value.get('value')
    return value

def expired(*_):
    raise TimeoutError('Finite generation deadline reached; no automatic retry')

def main():
    from gradio_client import Client, handle_file
    guard()
    token = os.environ.get('HF_TOKEN') or getpass.getpass('HF token (hidden; memory only): ')
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(2400)
    results = []
    for name, seed in [('stepped-furnace', 281), ('oak-bellows', 282), ('anvil-workstation', 283), ('stock-workbay', 284), ('forge-lantern', 285), ('gothic-window', 286)]:
        if sys.argv[1:] and name not in sys.argv[1:]:
            continue
        dest = OUT / 'generated' / name
        dest.mkdir(parents=True, exist_ok=True)
        if (dest / 'model.glb').exists():
            print(name + ': existing model preserved', flush=True)
            continue
        record = {'space': SPACE, 'asset': name, 'seed': seed, 'resolution': '1024',
                  'decimation_target': 220000, 'texture_size': 2048,
                  'status': 'started', 'storage_before': guard()}
        start = time.monotonic()
        try:
            print(name + ': connecting to official Space', flush=True)
            c = Client(SPACE, token=token, verbose=False, httpx_kwargs={'timeout': 180}, analytics_enabled=False)
            c.predict(api_name='/start_session')
            src = OUT / 'inputs' / (name + '.png')
            record['input_sha256'] = hashlib.sha256(src.read_bytes()).hexdigest()
            pre = path_of(c.predict(input=handle_file(str(src)), api_name='/preprocess_image'))
            shutil.copyfile(pre, dest / 'preprocessed.png')
            print(name + ': preprocessing complete; requesting mesh', flush=True)
            c.predict(image=handle_file(pre), seed=seed, resolution='1024', api_name='/image_to_3d')
            print(name + ': extracting GLB', flush=True)
            try:
                glb, _ = c.predict(decimation_target=220000, texture_size=2048, api_name='/extract_glb')
            except Exception as extract_error:
                record['first_extract_error'] = str(extract_error).replace(token, '[REDACTED]')[:500]
                if 'timed out' not in str(extract_error).lower():
                    raise
                print(name + ': bounded export retry in same session; no new shape generation', flush=True)
                glb, _ = c.predict(decimation_target=220000, texture_size=2048, api_name='/extract_glb')
            guard()
            src_glb = Path(path_of(glb))
            if src_glb.stat().st_size > 150_000_000:
                raise RuntimeError('Generated mesh exceeds150MB asset cap')
            shutil.copyfile(src_glb, dest / 'model.glb')
            record.update(status='completed', bytes=(dest / 'model.glb').stat().st_size,
                          sha256=hashlib.sha256((dest / 'model.glb').read_bytes()).hexdigest())
            print(name + ': completed (' + str(record['bytes']) + ' bytes)', flush=True)
        except Exception as exc:
            message = str(exc).replace(token, '[REDACTED]') if token else str(exc)
            record.update(status='failed', error=message[:2000])
            print(name + ': ' + message[:500], flush=True)
        finally:
            record['seconds'] = round(time.monotonic() - start, 2)
            (dest / 'run.json').write_text(json.dumps(record, indent=2) + '\n')
            results.append(record)
        if record['status'] == 'failed' and any(word in record.get('error', '').lower() for word in ('quota', 'gpu duration', 'exceeded')):
            break
    signal.alarm(0)
    (OUT / ('generation-summary-' + '-'.join(sys.argv[1:]) + '.json' if sys.argv[1:] else 'generation-summary.json')).write_text(json.dumps(results, indent=2) + '\n')
    token = None
    if any(r['status'] != 'completed' for r in results):
        raise SystemExit(1)

if __name__ == '__main__':
    main()
