import {freeze} from '../core/math.js';
const cats=['early','late','none'];
const distribution=c=>{const total=Object.values(c).reduce((a,b)=>a+b,0);return Object.fromEntries(Object.entries(c).map(([k,v])=>[k,(v+1)/(total+Object.keys(c).length)]));};
export class OpponentModel {
  constructor(){this.samples=[];this.seen=new Set();this.censored=0;}
  add(sample){if(this.seen.has(sample.instance))return false;this.seen.add(sample.instance);if(sample.response==='unknown'){this.censored++;return false;}this.samples.push(freeze({...sample}));return true;}
  summarize(context=null){
    const contextual=this.samples.filter(s=>s.family===context),use=contextual.length>=6?contextual:this.samples;
    const counts={early:0,late:0,none:0},long={early:0,late:0,none:0},dirs={inward:0,outward:0,lateral:0};
    for(const s of use){for(const k of cats){counts[k]*=.82;long[k]*=.97;}counts[s.response]++;long[s.response]++;if(s.direction){for(const k in dirs)dirs[k]*=.82;dirs[s.direction]++;}}
    const effective=Object.values(counts).reduce((a,b)=>a+b,0),n=use.length;
    const families={};for(const family of ['cut','overhead','thrust']){const samples=this.samples.filter(s=>s.family===family),c={early:0,late:0,none:0};for(const s of samples){for(const k of cats)c[k]*=.82;c[s.response]++;}families[family]={n:samples.length,recent:distribution(c),scope:samples.length>=6?family:'pooled backoff'};}
    return freeze({n,effective,sufficient:n>=6,scope:contextual.length>=6?context:'pooled (sparse-context backoff)',recent:distribution(counts),long:distribution(long),directions:distribution(dirs),directionN:use.filter(s=>s.direction).length,censored:this.censored,evidence:use.slice(-8).map(s=>s.instance),contexts:Object.fromEntries(['cut','overhead','thrust'].map(k=>[k,this.samples.filter(s=>s.family===k).length])),families});
  }
}
