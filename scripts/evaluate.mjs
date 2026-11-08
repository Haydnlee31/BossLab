import {writeFile,mkdir} from 'node:fs/promises';
import {Combat} from '../game/core/simulation.js';
import {runEncounter} from '../game/ai/scenarios.js';
import {VERSION} from '../game/core/config.js';
await mkdir('artifacts',{recursive:true});
const seeds=[1001,1201,1409,1601,1801,2003],reports=[];
for(const scenario of ['early','late','switch'])for(const seed of seeds)for(const controller of ['static','adaptive']){
  const world=runEncounter(Combat,{seed,controller,scenario,offset:(seed%3)-1});
  reports.push({...world.report(),scenario,offset:(seed%3)-1});
  if(seed===1001&&scenario==='switch')await writeFile(`artifacts/${controller}-switch-events.json`,JSON.stringify({report:world.report(),events:world.events},null,2));
}
const groups=[];for(const scenario of ['early','late','switch'])for(const controller of ['static','adaptive']){const rows=reports.filter(r=>r.scenario===scenario&&r.config.controller===controller);groups.push({scenario,controller,encounters:rows.length,bossWins:rows.filter(r=>r.outcome==='defeat').length,playerWins:rows.filter(r=>r.outcome==='victory').length,timeouts:rows.filter(r=>r.outcome==='timeout').length,meanDamageToPlayer:rows.reduce((s,r)=>s+r.metrics.damageToPlayer,0)/rows.length,meanDamageToBoss:rows.reduce((s,r)=>s+r.metrics.damageToBoss,0)/rows.length});}
await writeFile('artifacts/evaluation.json',JSON.stringify({version:VERSION,generatedAt:new Date().toISOString(),seeds,split:'held-out; development 1–20 and pilot 101/203/307/409/503/607',maxTicks:7200,switchTick:900,groups,reports},null,2));
await writeFile('artifacts/evaluation.csv','scenario,controller,seed,offset,outcome,ticks,damage_to_player,damage_to_boss,cut,overhead,thrust,samples,effective,early,late,none,mean_decision_ms,fallbacks\n'+reports.map(r=>[r.scenario,r.config.controller,r.config.seed,r.offset,r.outcome,r.ticks,r.metrics.damageToPlayer,r.metrics.damageToBoss,...Object.values(r.metrics.attacks),r.summary.n,r.summary.effective,...Object.values(r.summary.recent),r.metrics.meanDecisionMs,r.metrics.fallbacks].join(',')).join('\n')+'\n');
console.table(groups);console.log('Saved artifacts/evaluation.json, evaluation.csv, and switch event logs.');
