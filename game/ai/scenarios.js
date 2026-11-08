import {ATTACKS} from '../core/config.js';
import {angle,distance} from '../core/math.js';
export const SCENARIOS=Object.freeze({early:{timing:'early',switchTick:900},late:{timing:'late',switchTick:900},switch:{timing:'switch',switchTick:900}});
export class ScriptedPlayer {
  constructor({timing='switch',switchTick=2400,offset=0,lateral=.18}={}){this.config={timing,switchTick,offset,lateral};this.responded=new Set();this.punished=new Set();}
  stage(tick){return this.config.timing==='switch'?(tick<this.config.switchTick?'early':'late'):this.config.timing;}
  input(world,elapsed=world.tick){
    const p=world.player,b=world.boss,d=distance(p,b),a=angle(p,b),stage=this.stage(elapsed),attack=ATTACKS[b.action];
    const v={x:0,y:0,aim:a};
    if(p.hp<65&&p.heals&&d>180){v.heal=true;return v;}
    if(b.state==='attack'&&attack){
      const when=(stage==='early'?8:attack.windup-7)+this.config.offset;
      if(!this.responded.has(b.instance)&&b.age>=when&&b.age<attack.windup&&p.state==='ready'&&p.stamina>=26){
        this.responded.add(b.instance);v.dodge=true;v.x=Math.cos(a+this.config.lateral);v.y=Math.sin(a+this.config.lateral);return v;
      }
      if(world.phase()==='recovery'&&b.age===attack.windup+attack.active&&p.hp<85&&p.heals){v.heal=true;return v;}
      if(world.phase()==='recovery'&&d<100&&p.state==='ready'&&p.stamina>48&&!this.punished.has(b.instance)){this.punished.add(b.instance);v.attack=true;return v;}
    }
    if(d>78){v.x=Math.cos(a);v.y=Math.sin(a);}else if(d<57){v.x=-Math.cos(a)*.35;v.y=-Math.sin(a)*.35;}
    return v;
  }
}
export function runEncounter(Combat,{seed,controller,scenario='early',offset=0,maxTicks=7200}={}){
  const world=new Combat({seed,controller,encounterId:`${controller}-${scenario}-${seed}`}),player=new ScriptedPlayer({...SCENARIOS[scenario],offset});
  while(!world.outcome&&world.tick<maxTicks)world.step(player.input(world));
  if(!world.outcome)world.finish('timeout');return world;
}
