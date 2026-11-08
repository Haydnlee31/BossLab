import {distance,freeze} from '../core/math.js';
export const CONTROLLERS = Object.freeze({static:'Static baseline',adaptive:'Adaptive utility — statistical opponent model'});
export function decide(observation,summary,plan,legal,random,mode='adaptive'){
  const d=distance(observation.boss,observation.player),base={cut:d<112?1.2:.08,overhead:d<145?1:.1,thrust:d>90&&d<215?1.3:.4,approach:d>150?2.8:.08,reposition:.10,wait:.06};
  const contributions={cut:0,overhead:0,thrust:0,approach:0,reposition:0,wait:0};
  if(mode==='adaptive'&&summary.sufficient){
    const p=summary.recent,scale=Math.min(1,summary.effective/5),o=summary.families?.overhead?.n>=6?summary.families.overhead.recent:p,c=summary.families?.cut?.n>=6?summary.families.cut.recent:p;
    contributions.overhead=scale*Math.max(-.65,Math.min(2.4,3.4*(o.early-o.late)));
    contributions.cut=scale*Math.max(-.5,Math.min(1.2,1.5*(c.late-c.early)));
    if(summary.directionN>=6)contributions.thrust=.6*(summary.directions.outward-summary.directions.lateral);
  }
  const scores=Object.fromEntries(legal.map(k=>[k,Math.max(.025,base[k]+contributions[k])])),total=Object.values(scores).reduce((a,b)=>a+b,0),probabilities=Object.fromEntries(Object.entries(scores).map(([k,v])=>[k,v/total]));
  let r=random(),action=legal.at(-1);for(const k of legal){r-=probabilities[k];if(r<=0){action=k;break;}}
  return freeze({action,controller:mode,version:`${mode}-1`,scores,contributions,probabilities,reason:mode==='adaptive'&&summary.sufficient?'observed-response-utility':'spacing-only',evidence:mode==='adaptive'?summary.evidence:[],planVersion:null});
}
