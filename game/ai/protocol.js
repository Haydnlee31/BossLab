import {freeze} from '../core/math.js';
export const PROTOCOL='bosslab-decision-1';
export function validatePlan(plan,{tick,evidence,neutral}){
  if(!neutral||!plan||!['pressure','space','observe'].includes(plan.tactic)||!Number.isInteger(plan.expires)||plan.expires<=tick||plan.expires>tick+600||!Array.isArray(plan.evidence)||!plan.evidence.every(id=>evidence.includes(id)))return null;
  return freeze({tactic:plan.tactic,expires:plan.expires,evidence:[...plan.evidence]});
}
// Transport is explicitly injected. Default is unavailable; this never calls a network service.
export class DecisionBridge {
  constructor(transport=null,{timeoutMs=80,now=()=>performance.now()}={}){this.transport=transport;this.timeoutMs=timeoutMs;this.now=now;this.pending=null;this.generation=0;}
  reset(){this.generation++;this.pending=null;}
  async request({encounterId,window,observation,summary,legal,policyId,plan=null},current){
    if(!this.transport)return {ok:false,reason:'model-unavailable'};
    if(this.pending)return {ok:false,reason:'in-flight'};
    const generation=this.generation,start=this.now(),request=freeze({version:PROTOCOL,encounterId,window,observationTick:observation.tick,observation,summary,legal:[...legal],policyId,plan,deadlineMs:start+this.timeoutMs});
    const token={};this.pending=token;let timer;
    try{const reply=await Promise.race([Promise.resolve().then(()=>this.transport(request)),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('timeout')),this.timeoutMs);})]);
      if(generation!==this.generation||current().encounterId!==encounterId||current().window!==window)return {ok:false,reason:'stale'};
      if(this.now()>request.deadlineMs)return {ok:false,reason:'timeout'};
      const r=typeof reply==='string'?JSON.parse(reply):reply;
      if(!r||r.version!==PROTOCOL||r.encounterId!==encounterId||r.window!==window||r.policyId!==policyId||!legal.includes(r.action)||typeof r.modelId!=='string'||!r.modelId.length)return {ok:false,reason:'invalid-response'};
      if(r.scores&&(!Object.keys(r.scores).length||!Object.entries(r.scores).every(([k,v])=>legal.includes(k)&&Number.isFinite(v)&&v>=0&&v<=1)))return {ok:false,reason:'invalid-scores'};
      return {ok:true,action:r.action,modelId:r.modelId,policyId:r.policyId,latencyMs:this.now()-start,scores:r.scores||null};
    }catch(e){return {ok:false,reason:e.message==='timeout'?'timeout':'malformed-or-disconnected'};}
    finally{clearTimeout(timer);if(this.pending===token)this.pending=null;}
  }
}
