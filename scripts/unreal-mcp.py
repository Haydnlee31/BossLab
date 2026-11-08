#!/usr/bin/env python3
"""Small stdlib client for Epic's native MCP server; does not start a service."""
import json
from pathlib import Path
import sys
import urllib.request
import urllib.error

ENDPOINT = 'http://127.0.0.1:8000/mcp'
class Client:
    def __init__(self):
        self.session = None
        self.sequence = 0
        self.protocol = '2025-11-25'
    def request(self, method, params=None, notification=False):
        self.sequence += 1
        body = {'jsonrpc': '2.0', 'method': method, 'params': params or {}}
        if not notification:
            body['id'] = self.sequence
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
                   'MCP-Protocol-Version': self.protocol}
        if self.session:
            headers['Mcp-Session-Id'] = self.session
        request = urllib.request.Request(ENDPOINT, json.dumps(body).encode(), headers)
        with urllib.request.urlopen(request, timeout=55) as response:
            self.session = response.headers.get('Mcp-Session-Id', self.session)
            raw = response.read().decode()
        if not raw.strip():
            return None
        if raw.lstrip().startswith('{'):
            result = json.loads(raw)
        else:
            messages = [json.loads(line[5:].strip()) for line in raw.splitlines() if line.startswith('data:')]
            result = next((item for item in messages if item.get('id') == body.get('id')), messages[-1])
        if 'error' in result:
            raise RuntimeError(json.dumps(result['error']))
        return result.get('result', result)
    def connect(self):
        result = self.request('initialize', {'protocolVersion':self.protocol, 'capabilities':{},
                           'clientInfo':{'name':'bosslab-local-development','version':'0.1'}})
        self.protocol = result['protocolVersion']
        self.request('notifications/initialized', notification=True)
        return result

def main():
    client = Client()
    info = client.connect()
    if len(sys.argv) == 1:
        output = {'initialize': info, 'tools': client.request('tools/list')}
    else:
        output = client.request('tools/call', {'name':sys.argv[1],
                 'arguments': json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}})
    print(json.dumps(output, indent=2))
    if isinstance(output, dict) and output.get('isError'):
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, urllib.error.URLError) as error:
        print(json.dumps({'connected': False, 'error': str(error)}), file=sys.stderr)
        sys.exit(1)
