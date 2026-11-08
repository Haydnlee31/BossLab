#!/usr/bin/env python3
"""Bounded, sequential read/write/reload proof using Epic's native toolsets."""
import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
Client = runpy.run_path(str(ROOT / 'scripts/unreal-mcp.py'))['Client']
client = Client()
report = {'connection': client.connect(), 'steps': [], 'passed': False}
scene = 'editor_toolset.toolsets.scene.SceneTools'
actor = 'editor_toolset.toolsets.actor.ActorTools'
asset = 'editor_toolset.toolsets.asset.AssetTools'
automation = 'AutomationTestToolset.AutomationTestToolset'

def call(toolset, tool, **arguments):
    result = client.request('tools/call', {'name': 'call_tool', 'arguments': {
        'toolset_name': toolset, 'tool_name': tool, 'arguments': arguments}})
    report['steps'].append({'tool': toolset + '.' + tool, 'arguments': arguments, 'result': result})
    if result.get('isError'):
        raise RuntimeError(str(result))
    value = json.loads(result['content'][0]['text']).get('returnValue')
    if value is False:
        raise RuntimeError(tool + ' returned false')
    return value

try:
    current = call(scene, 'get_current_level')
    assert current == '/Game/BossLab/Maps/MCPProof', current
    matches = call(scene, 'find_actors', name='BossLab_Disposable_MCP_Probe', tag='', collision_channels=[])
    assert not matches, 'Existing probe: inspect before rerun; never delete unrelated actors'
    probe = call(scene, 'add_to_scene_from_asset', asset_path='/Engine/BasicShapes/Cube',
                 name='BossLab_Disposable_MCP_Probe', xform={'location': {'x': 100, 'y': 200, 'z': 150}})
    position = {'x': 320, 'y': -110, 'z': 175}
    call(actor, 'set_actor_transform', actor=probe, xform={'location': position})
    assert call(actor, 'get_actor_transform', actor=probe)['location'] == position
    call(asset, 'save_assets', asset_paths=[current])
    call(scene, 'load_level', level_path='/Engine/Maps/Entry')
    call(scene, 'load_level', level_path=current)
    matches = call(scene, 'find_actors', name='BossLab_Disposable_MCP_Probe', tag='', collision_channels=[])
    assert len(matches) == 1
    assert call(actor, 'get_actor_transform', actor=matches[0])['location'] == position
    call(scene, 'remove_from_scene', actor=matches[0])
    call(asset, 'save_assets', asset_paths=[current])
    assert not call(scene, 'find_actors', name='BossLab_Disposable_MCP_Probe', tag='', collision_channels=[])
    call(automation, 'DiscoverTests', bForceRediscover=True)
    tests = json.loads(call(automation, 'RunTests', testNames=[
        'BossLab.Preflight.ActorCollisionLifecycle', 'BossLab.Preflight.EditorSubsystems']))
    report['tests'] = tests
    assert tests['passed'] == 2 and tests['failed'] == 0
    assert all(not test['warnings'] for test in tests['tests'])
    report['passed'] = True
finally:
    (ROOT / 'artifacts/unreal/mcp-proof.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({'passed': report['passed'], 'steps': len(report['steps']), 'tests': report.get('tests')}))
