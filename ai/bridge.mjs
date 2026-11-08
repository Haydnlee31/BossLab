import readline from 'node:readline';
import {Environment} from './environment.mjs';
const env=new Environment();
for await(const line of readline.createInterface({input:process.stdin})){try{const req=JSON.parse(line);const result=req.op==='reset'?env.reset(req.config):req.op==='step'?env.step(req.action):(()=>{throw Error('Unknown operation');})();console.log(JSON.stringify(result));}catch(e){console.log(JSON.stringify({error:e.message}));}}
