import {Combat} from '../game/core/simulation.js';
import {ScriptedPlayer,SCENARIOS} from '../game/ai/scenarios.js';
import {ACTIONS,RULES,VERSION} from '../game/core/config.js';
export const ENV_VERSION='warden-rl-env-1';
export class Environment {
  reset({seed=1,scenario='early',maxTicks=7200,controller='ppo-smoke'}={}){
    this.world=new Combat({seed,controller,external:controller==='ppo-smoke'});this.bot=new ScriptedPlayer({...SCENARIOS[scenario],offset:seed%3-1});this.maxTicks=maxTicks;this.truncated=false;return this.result(0);
  }
  result(reward){const w=this.world,o=w.observation(),s=w.model.summarize(),legal=w.legal(),dx=(o.player.x-o.boss.x)/570,dy=(o.player.y-o.boss.y)/570;
    return {observation:[dx,dy,o.boss.x/285,o.boss.y/285,Math.cos(o.boss.facing),Math.sin(o.boss.facing),o.boss.hp/RULES.bossHP,Math.min(o.tick/7200,1),...Object.values(s.recent),...Object.values(s.directions),Math.min(s.effective/6,1),s.sufficient?1:0],mask:[...ACTIONS.map(a=>legal.includes(a)),legal.length===0],reward,terminated:!!w.outcome,truncated:this.truncated,report:w.outcome||this.truncated?w.report():null,version:ENV_VERSION,core:VERSION};
  }
  step(index){const w=this.world;if(w.outcome||this.truncated)throw Error('Reset required');const before={...w.metrics},mask=this.result(0).mask;if(!Number.isInteger(index)||!mask[index])throw Error('Masked action rejected');
    if(index<6&&w.external)w.propose(ACTIONS[index]);for(let n=0;n<12&&!w.outcome&&w.tick<this.maxTicks;n++)w.step(this.bot.input(w));
    this.truncated=!w.outcome&&w.tick>=this.maxTicks;let reward=(w.metrics.damageToPlayer-before.damageToPlayer)/120-(w.metrics.damageToBoss-before.damageToBoss)/420;
    if(w.outcome)reward+=w.outcome==='defeat'?1:-1;return this.result(reward);
  }
}
