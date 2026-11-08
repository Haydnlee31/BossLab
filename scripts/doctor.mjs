import {existsSync} from 'node:fs';
import {VERSION} from '../game/core/config.js';
console.log(JSON.stringify({engine:VERSION,node:process.version,platform:process.platform,arch:process.arch,core:existsSync(new URL('../game/core/simulation.js',import.meta.url)),dependencies:'None for play/test/evaluate',models:'Not connected'},null,2));
if(Number(process.versions.node.split('.')[0])<22){console.error('Install Node.js 22 or newer.');process.exit(1);}
