export const VERSION = 'warden-core-1.0.0';
export const RULES = Object.freeze({ hz:60, delay:12, radius:285, playerHP:120, bossHP:420, playerRadius:12, bossRadius:22, speed:2.65, bossSpeed:1.5, dodgeCost:26, dodgeDuration:26, dashDuration:14, dashSpeed:5.1, invulStart:2, invulEnd:16, attackCost:18, healDuration:72, healAmount:45 });
export const ATTACKS = Object.freeze(Object.fromEntries(Object.entries({
  cut: { name:'Quick cut', windup:22, active:5, recovery:28, lock:13, turn:0.08, range:104, arc:1.13, width:0, damage:16, cooldown:80, movement:0, geometry:'sector' },
  overhead: { name:'Delayed overhead', windup:50, active:6, recovery:40, lock:30, turn:0.065, range:140, arc:0.34, width:0, damage:24, cooldown:110, movement:0, geometry:'sector' },
  thrust: { name:'Advancing thrust', windup:32, active:7, recovery:36, lock:20, turn:0.07, range:172, arc:0, width:21, damage:20, cooldown:100, movement:2.6, geometry:'capsule' }
}).map(([id,a])=>[id,Object.freeze({...a,id,cancel:false,followups:Object.freeze(['ready'])})])));
export const ACTIONS = Object.freeze(['cut','overhead','thrust','approach','reposition','wait']);
export const PLAYER_ATTACK = Object.freeze({windup:10,active:4,recovery:19,range:83,arc:1.05,damage:30});
