import {RULES,ATTACKS,PLAYER_ATTACK,VERSION,ACTIONS} from './config.js';
import {rng,distance,angle,clamp,turn,hitGeometry,freeze} from './math.js';
import {OpponentModel} from '../ai/opponent.js';
import {decide,CONTROLLERS} from '../ai/policy.js';
let sequence=0;
export class Combat {
  constructor({seed=1,controller='adaptive',delay=RULES.delay,encounterId,external=false}={}){
    if(!CONTROLLERS[controller]&&!external)throw Error('Unavailable controller');
    this.config=freeze({seed,controller,delay,version:VERSION});this.id=encounterId||`encounter-${++sequence}`;this.random=rng(seed);this.external=external;
    this.tick=0;this.outcome=null;this.player={x:0,y:130,facing:-Math.PI/2,radius:RULES.playerRadius,hp:RULES.playerHP,stamina:100,heals:3,state:'ready',age:0};
    this.boss={x:0,y:-60,facing:Math.PI/2,radius:RULES.bossRadius,hp:RULES.bossHP,state:'ready',age:0};
    this.model=new OpponentModel();this.events=[];this.pending=[];this.snapshots=[];this.opportunities=[];this.cooldowns={cut:0,overhead:0,thrust:0};this.attackSerial=0;this.window=0;this.waits=0;this.nextDecision=30;this.lastDecision=null;this.metrics={damageToPlayer:0,damageToBoss:0,attacks:{cut:0,overhead:0,thrust:0},fallbacks:0,decisionMs:[]};
    this.visible=freeze(this.snapshot());this.emit('start',{config:this.config});
  }
  emit(type,data={}){const e=freeze({type,tick:this.tick,encounterId:this.id,...data});this.events.push(e);return e;}
  snapshot(){return {version:'observation-1',tick:this.tick,boss:{x:this.boss.x,y:this.boss.y,facing:this.boss.facing,state:this.boss.state,hp:this.boss.hp},player:{x:this.player.x,y:this.player.y,facing:this.player.facing,state:this.player.state},arena:{radius:RULES.radius}};}
  observation(){return freeze({...this.visible,boss:{x:this.boss.x,y:this.boss.y,facing:this.boss.facing,state:this.boss.state,hp:this.boss.hp},encounterId:this.id,window:this.window});}
  legal(){if(this.outcome||this.boss.state!=='ready'||this.tick<this.nextDecision)return [];return ACTIONS.filter(a=>!ATTACKS[a]||(this.cooldowns[a]<=this.tick)).filter(a=>a!=='wait'||this.waits<2);}
  propose(action,{encounterId=this.id,window=this.window}={}){
    if(encounterId!==this.id||window!==this.window||!this.legal().includes(action)){this.emit('rejected',{action,window,reason:'stale-or-illegal'});return false;}
    this.window++;this.waits=action==='wait'?this.waits+1:0;
    this.emit('accepted',{action,window:window,controller:this.config.controller});
    if(ATTACKS[action]){const a=ATTACKS[action],b=this.boss;b.state='attack';b.age=0;b.action=action;b.hit=false;b.facing=angle(b,this.visible.player);b.instance=`${this.id}:${++this.attackSerial}`;this.cooldowns[action]=this.tick+a.cooldown;this.metrics.attacks[action]++;
      this.opportunities.push({instance:b.instance,family:action,start:this.tick,end:this.tick+a.windup+a.active-1,spacing:distance(b,this.visible.player),response:null,outcome:'miss'});this.emit('cue',{instance:b.instance,action,availableTick:this.tick});
    }else{this.boss.state=action;this.boss.age=0;this.nextDecision=this.tick+(action==='wait'?16:20);}
    return true;
  }
  phase(){const b=this.boss,a=ATTACKS[b.action];if(b.state!=='attack')return b.state;if(b.age<a.lock)return 'windup';if(b.age<a.windup)return 'aim-locked';if(b.age<a.windup+a.active)return 'active';return 'recovery';}
  invulnerable(){const p=this.player;return p.state==='dodge'&&p.age>=RULES.invulStart&&p.age<RULES.invulEnd;}
  move(actor,dx,dy){actor.x+=dx;actor.y+=dy;const d=Math.hypot(actor.x,actor.y),limit=RULES.radius-actor.radius;if(d>limit){actor.x*=limit/d;actor.y*=limit/d;}}
  playerInput(input){const p=this.player;if(p.state!=='ready')return;
    if(Number.isFinite(input.aim))p.facing=input.aim;
    let dx=Number(input.x)||0,dy=Number(input.y)||0;const n=Math.hypot(dx,dy);if(n>1){dx/=n;dy/=n;}
    if(input.dodge&&p.stamina>=RULES.dodgeCost){p.stamina-=RULES.dodgeCost;p.state='dodge';p.age=0;p.dx=n?dx:Math.cos(p.facing);p.dy=n?dy:Math.sin(p.facing);
      const rel=angle(this.boss,p),dot=p.dx*Math.cos(rel)+p.dy*Math.sin(rel),direction=dot>.55?'outward':dot<-.55?'inward':'lateral';
      const e=this.emit('dodge',{direction,availableTick:this.tick+this.config.delay});this.pending.push(e);
    }else if(input.attack&&p.stamina>=RULES.attackCost){p.stamina-=RULES.attackCost;p.state='attack';p.age=0;p.hit=false;this.emit('player-attack');}
    else if(input.heal&&p.heals>0&&p.hp<RULES.playerHP){p.heals--;p.state='heal';p.age=0;this.emit('heal-start');}
    else this.move(p,dx*RULES.speed,dy*RULES.speed);
  }
  deliver(){
    while(this.snapshots.length&&this.snapshots[0].tick+this.config.delay<=this.tick)this.visible=freeze(this.snapshots.shift());
    while(this.pending.length&&this.pending[0].availableTick<=this.tick){const e=this.pending.shift();this.emit('observed',{sourceType:e.type,sourceTick:e.tick,availableTick:e.availableTick});
      const o=this.opportunities.find(o=>!o.closed&&!o.response&&e.tick>=o.start&&e.tick<=o.end);
      if(o)o.response={response:e.tick-o.start<ATTACKS[o.family].windup*.55?'early':'late',direction:e.direction,responseTick:e.tick};
    }
    for(const o of this.opportunities){if(!o.closed&&this.tick>=o.end+this.config.delay){o.closed=true;const s={instance:o.instance,family:o.family,spacing:o.spacing,outcome:o.outcome,...(o.response||{response:'none'}),observedTick:this.tick};this.model.add(s);this.emit('sample',s);}}
  }
  damage(target,amount,source,instance){if(target.hp<=0)return;const before=target.hp;target.hp=clamp(target.hp-amount,0,target===this.player?RULES.playerHP:RULES.bossHP);this.metrics[target===this.player?'damageToPlayer':'damageToBoss']+=before-target.hp;this.emit('hit',{target:target===this.player?'player':'boss',damage:before-target.hp,source,instance});}
  step(input={}){
    if(this.outcome)return;this.tick++;this.deliver();this.playerInput(input);
    const p=this.player,b=this.boss;
    if(!this.external&&b.state==='ready'&&this.tick>=this.nextDecision){const ob=this.observation(),summary=this.model.summarize(),start=performance.now(),d=decide(ob,summary,null,this.legal(),this.random,this.config.controller);const ms=performance.now()-start;this.metrics.decisionMs.push(ms);this.lastDecision={...d,observationTick:ob.tick,window:this.window,latencyMs:ms};this.emit('decision',{...this.lastDecision,inputVersion:ob.version,summary});this.propose(d.action);}
    if(p.state==='dodge'&&p.age<RULES.dashDuration)this.move(p,p.dx*RULES.dashSpeed,p.dy*RULES.dashSpeed);
    if(b.state==='approach'||b.state==='reposition'){const a=angle(b,this.visible.player)+(b.state==='reposition'?Math.PI/2:0);b.facing=turn(b.facing,a,.07);if(distance(b,this.visible.player)>60||b.state==='reposition')this.move(b,Math.cos(a)*RULES.bossSpeed,Math.sin(a)*RULES.bossSpeed);if(this.tick>=this.nextDecision)b.state='ready';}
    if(b.state==='wait'&&this.tick>=this.nextDecision)b.state='ready';
    if(b.state==='attack'){const a=ATTACKS[b.action];if(b.age<a.lock)b.facing=turn(b.facing,angle(b,this.visible.player),a.turn);if(this.phase()==='active'){
      if(a.movement)this.move(b,Math.cos(b.facing)*a.movement,Math.sin(b.facing)*a.movement);
      if(!b.hit&&hitGeometry(b,p,a)&&!this.invulnerable()){b.hit=true;this.damage(p,a.damage,b.action,b.instance);const o=this.opportunities.find(o=>o.instance===b.instance);if(o)o.outcome='hit';}
    }}
    // Boss resolves first on a simultaneous tick. A lethal strike prevents retaliation.
    if(p.hp>0&&p.state==='attack'&&p.age>=PLAYER_ATTACK.windup&&p.age<PLAYER_ATTACK.windup+PLAYER_ATTACK.active&&!p.hit&&hitGeometry(p,b,PLAYER_ATTACK)){p.hit=true;this.damage(b,PLAYER_ATTACK.damage,'player');}
    const sep=distance(p,b),minimum=p.radius+b.radius;if(sep<minimum){const a=sep===0?0:angle(b,p);this.move(p,Math.cos(a)*(minimum-sep),Math.sin(a)*(minimum-sep));}
    p.age++;b.age++;
    if(p.state==='dodge'&&p.age>=RULES.dodgeDuration||p.state==='attack'&&p.age>=PLAYER_ATTACK.windup+PLAYER_ATTACK.active+PLAYER_ATTACK.recovery)p.state='ready';
    if(p.hp>0&&p.state==='heal'&&p.age>=RULES.healDuration){p.hp=clamp(p.hp+RULES.healAmount,0,RULES.playerHP);p.state='ready';this.emit('heal-complete');}
    if(p.state==='ready')p.stamina=clamp(p.stamina+.65,0,100);
    if(b.state==='attack'){const a=ATTACKS[b.action];if(b.age>=a.windup+a.active+a.recovery){b.state='ready';this.nextDecision=this.tick+8;}}
    this.snapshots.push(this.snapshot());if(this.tick%120===0)this.emit('snapshot',{state:this.snapshot(),playerHP:p.hp});
    if(p.hp<=0||b.hp<=0)this.finish(p.hp<=0?'defeat':'victory');
  }
  finish(outcome){if(this.outcome)return;this.outcome=outcome;for(const o of this.opportunities){if(!o.closed){o.closed=true;const s={instance:o.instance,family:o.family,response:'unknown',observedTick:this.tick};this.model.add(s);this.emit('censored',s);}}this.emit('end',{outcome});}
  inspector(){return {controller:CONTROLLERS[this.config.controller]||this.config.controller,controllerVersion:`${this.config.controller}-1`,observation:this.observation(),delay:this.config.delay,summary:this.model.summarize(),decision:this.lastDecision,phase:this.phase(),models:{ppo:'Headless PPO smoke checkpoint; browser inference unavailable',laya:'Not connected',jev:'Not connected',clm:'Not connected',strategist:'Disabled'},weights:'Utility coefficients frozen; statistical counts update per exchange',fallbacks:this.metrics.fallbacks};}
  report(){const times=this.metrics.decisionMs;return {version:VERSION,config:this.config,encounterId:this.id,ticks:this.tick,outcome:this.outcome||'in-progress',playerHP:this.player.hp,bossHP:this.boss.hp,metrics:{...this.metrics,decisionMs:undefined,decisions:times.length,meanDecisionMs:times.length?times.reduce((a,b)=>a+b,0)/times.length:0,maxDecisionMs:times.length?Math.max(...times):0},summary:this.model.summarize()};}
}
