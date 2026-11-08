import {writeFile} from 'node:fs/promises';
import {Combat} from '../game/core/simulation.js';
import {ScriptedPlayer} from '../game/ai/scenarios.js';
const bot=new ScriptedPlayer({timing:'switch',switchTick:2400});let world=new Combat({seed:7}),round=1;const rounds=[],checkpoints=[];
for(let elapsed=0;elapsed<5400;elapsed++){
  if(world.outcome){rounds.push({report:world.report(),events:world.events});const model=world.model,previous=world.id;world=new Combat({seed:7+round});world.model=model;world.emit('demo-round-reset',{previousEncounter:previous,round:++round,evidenceRetained:true,demoElapsed:elapsed});}
  world.step(bot.input(world,elapsed));
  if([1800,2399,3600,4500,5399].includes(elapsed))checkpoints.push({elapsed,round,stage:bot.stage(elapsed),summary:world.model.summarize(),lastDecision:world.lastDecision});
}
rounds.push({report:world.report(),events:world.events});await writeFile('artifacts/demo-evidence.json',JSON.stringify({durationTicks:5400,switchTick:2400,description:'90 simulation seconds, real health and visible logical round resets, evidence retained; browser adds a 2 second inter-round pause',checkpoints,rounds},null,2));console.table(checkpoints.map(c=>({seconds:c.elapsed/60,round:c.round,stage:c.stage,n:c.summary.n,early:c.summary.recent.early,late:c.summary.recent.late,overheadContribution:c.lastDecision?.contributions.overhead})));
